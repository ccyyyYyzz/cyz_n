#!/usr/bin/env python3
"""Deterministic finite-window no-entry cover for the frozen index-2 source.

The certificate produced here has deliberately narrow scope.  It partitions
the registered half-open world-sheet/time window, evaluates the *closure* of
every leaf with outward-rounded Arb arithmetic, and proves that at least one
target coordinate admits no lattice image within ``r_out``.  A successful
bundle therefore records finite-window right censoring, never an all-time
no-entry statement.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from physical_arb_jets import (  # noqa: E402
    FLINT_VERSION,
    PYTHON_FLINT_VERSION,
    arb_exact_endpoints,
    evaluate_physical_jets,
)


CERTIFICATE_SCHEMA = "cyz-brief-0019-physical-no-entry-certificate-v1"
REPORT_SCHEMA = "cyz-brief-0019-physical-no-entry-report-v1"
SOLVER_REGISTRY_SCHEMA = (
    "cyz-brief-0019-physical-no-entry-solver-registry-v1"
)
PHYSICAL_PROBLEM_SEMANTIC_SHA256 = (
    "1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca"
)
SOLVER_REGISTRY_SEMANTIC_SHA256 = (
    "e0563bd70cd1d9b330d507605b34f0a7f61f8b6abba1f19c556da8462b51d541"
)

DEFAULT_PRECISION_BITS = 192
DEFAULT_MAX_NODES = 4095
DEFAULT_MAX_DEPTH = 48
DOMAIN_AXES = ("sigma1", "sigma2", "t")
TARGET_AXIS_ORDER = tuple(range(9))

SOURCE_FIXTURE = HERE / "source_state_bridge_fixture.json"
DEFAULT_CERTIFICATE = HERE / "physical_no_entry_certificate.json"
DEFAULT_REPORT = HERE / "physical_no_entry_report.json"


class NoEntryError(ValueError):
    """A finite-window cover or certificate failed a typed gate."""


def fail(gate: str, message: str) -> None:
    raise NoEntryError(f"{gate}: {message}")


def _reject_duplicate_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("strict_json", f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    fail("strict_json", f"non-finite JSON token {value!r}")


def _reject_float(value: str) -> None:
    fail("strict_json", f"ordinary JSON float {value!r} is forbidden")


def assert_float_free_json(value: Any, path: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        fail("strict_json", f"{path} contains an ordinary float")
    if type(value) is list:
        for index, item in enumerate(value):
            assert_float_free_json(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                fail("strict_json", f"{path} contains a non-string key")
            assert_float_free_json(item, f"{path}.{key}")
        return
    fail("strict_json", f"{path} contains {type(value).__name__}")


def strict_json_loads(text: str) -> Any:
    value = json.loads(
        text,
        object_pairs_hook=_reject_duplicate_pairs,
        parse_constant=_reject_nonfinite,
        parse_float=_reject_float,
    )
    assert_float_free_json(value)
    return value


def strict_json_load(path: Path) -> Any:
    try:
        return strict_json_loads(path.read_text(encoding="utf-8-sig"))
    except OSError as error:
        fail("strict_json", f"cannot read {path}: {error}")


def canonical_bytes(value: Any) -> bytes:
    assert_float_free_json(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def semantic_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def type_strict_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return (
            set(left) == set(right)
            and all(type_strict_equal(left[key], right[key]) for key in left)
        )
    if type(left) is list:
        return len(left) == len(right) and all(
            type_strict_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def pretty_json(value: Any) -> str:
    assert_float_free_json(value)
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(pretty_json(value), encoding="utf-8", newline="\n")


def _exact_keys(
    value: Any, expected: set[str], path: str, gate: str
) -> Mapping[str, Any]:
    if type(value) is not dict:
        fail(gate, f"{path} must be an object")
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        fail(gate, f"{path} is missing keys {missing}")
    if extra:
        fail(gate, f"{path} has unexpected keys {extra}")
    return value


def _integer(value: Any, path: str, gate: str) -> int:
    if type(value) is not int:
        fail(gate, f"{path} must be an integer; booleans are forbidden")
    return value


def dyadic_fraction(value: Any, path: str = "$dyadic") -> Fraction:
    item = _exact_keys(
        value, {"numerator", "exponent"}, path, "dyadic_encoding"
    )
    numerator = _integer(
        item["numerator"], f"{path}.numerator", "dyadic_encoding"
    )
    exponent = _integer(
        item["exponent"], f"{path}.exponent", "dyadic_encoding"
    )
    if exponent < 0:
        fail("dyadic_encoding", f"{path}.exponent must be nonnegative")
    if numerator == 0 and exponent != 0:
        fail("dyadic_encoding", f"{path} zero must have exponent zero")
    if numerator and exponent and numerator % 2 == 0:
        fail("dyadic_encoding", f"{path} is not reduced")
    return Fraction(numerator, 2**exponent)


def dyadic_json(value: Fraction | int) -> dict[str, int]:
    fraction = Fraction(value)
    denominator = fraction.denominator
    if denominator & (denominator - 1):
        fail("dyadic_encoding", "attempted to encode a non-dyadic rational")
    exponent = denominator.bit_length() - 1
    numerator = fraction.numerator
    while exponent and numerator % 2 == 0:
        numerator //= 2
        exponent -= 1
    if numerator == 0:
        exponent = 0
    return {"numerator": numerator, "exponent": exponent}


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _load_registered_problem() -> dict[str, Any]:
    fixture = strict_json_load(SOURCE_FIXTURE)
    if type(fixture) is not dict or "physical_problem" not in fixture:
        fail("physical_problem", "source bridge fixture lacks physical_problem")
    problem = fixture["physical_problem"]
    if type(problem) is not dict:
        fail("physical_problem", "registered physical problem is not an object")
    digest = semantic_sha256(problem)
    if digest != PHYSICAL_PROBLEM_SEMANTIC_SHA256:
        fail(
            "physical_problem",
            "registered physical problem differs from the pinned index-2 hash",
        )
    if fixture.get("physical_problem_semantic_sha256") != digest:
        fail(
            "physical_problem",
            "source bridge fixture carries a mismatched physical problem hash",
        )
    return problem


def _registered_domain(problem: Mapping[str, Any]) -> dict[str, Any]:
    sigma_domains = problem["worldsheet"]["sigma_domains"]
    observation = problem["observation"]
    intervals: list[dict[str, Any]] = []
    for index in range(2):
        domain = sigma_domains[index]
        if domain["closure"] != "lower_closed_upper_open":
            fail("domain", f"sigma domain {index} has an unsupported closure")
        intervals.append(
            {
                "lower": copy.deepcopy(domain["lower"]),
                "upper": copy.deepcopy(domain["upper"]),
                "lower_closed": True,
                "upper_closed": False,
            }
        )
    if observation["window_closure"] != "lower_closed_upper_open":
        fail("domain", "observation window has an unsupported closure")
    intervals.append(
        {
            "lower": copy.deepcopy(observation["t0"]),
            "upper": copy.deepcopy(observation["t1"]),
            "lower_closed": True,
            "upper_closed": False,
        }
    )
    domain = {"axes": list(DOMAIN_AXES), "intervals": intervals}
    _validate_box(domain, "$.domain")
    return domain


def _validate_box(value: Any, path: str) -> dict[str, Any]:
    box = _exact_keys(value, {"axes", "intervals"}, path, "cover_partition")
    if type(box["axes"]) is not list or box["axes"] != list(DOMAIN_AXES):
        fail("cover_partition", f"{path}.axes differs from the fixed order")
    raw_intervals = box["intervals"]
    if type(raw_intervals) is not list or len(raw_intervals) != 3:
        fail("cover_partition", f"{path}.intervals must contain three axes")
    for index, raw in enumerate(raw_intervals):
        item = _exact_keys(
            raw,
            {"lower", "upper", "lower_closed", "upper_closed"},
            f"{path}.intervals[{index}]",
            "cover_partition",
        )
        lower = dyadic_fraction(
            item["lower"], f"{path}.intervals[{index}].lower"
        )
        upper = dyadic_fraction(
            item["upper"], f"{path}.intervals[{index}].upper"
        )
        if not lower < upper:
            fail("cover_partition", f"{path} contains an empty axis interval")
        if type(item["lower_closed"]) is not bool:
            fail("cover_partition", f"{path} lower_closed is not Boolean")
        if type(item["upper_closed"]) is not bool:
            fail("cover_partition", f"{path} upper_closed is not Boolean")
    return dict(box)


def _box_for_arb(box: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for axis, interval in zip(box["axes"], box["intervals"]):
        result[axis] = {
            "lo": copy.deepcopy(interval["lower"]),
            "hi": copy.deepcopy(interval["upper"]),
        }
    return result


def _split_box(
    box: Mapping[str, Any], axis: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, int]]:
    if axis not in DOMAIN_AXES:
        fail("cover_partition", f"unknown split axis {axis!r}")
    index = DOMAIN_AXES.index(axis)
    interval = box["intervals"][index]
    lower = dyadic_fraction(interval["lower"])
    upper = dyadic_fraction(interval["upper"])
    midpoint = (lower + upper) / 2
    left = copy.deepcopy(box)
    right = copy.deepcopy(box)
    left["intervals"][index]["upper"] = dyadic_json(midpoint)
    left["intervals"][index]["upper_closed"] = False
    right["intervals"][index]["lower"] = dyadic_json(midpoint)
    right["intervals"][index]["lower_closed"] = True
    _validate_split(box, left, right, axis, dyadic_json(midpoint))
    return left, right, dyadic_json(midpoint)


def _validate_split(
    parent: Mapping[str, Any],
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    axis: str,
    point: Mapping[str, Any],
) -> None:
    _validate_box(parent, "$.parent")
    _validate_box(left, "$.left")
    _validate_box(right, "$.right")
    split_index = DOMAIN_AXES.index(axis)
    split_point = dyadic_fraction(point, "$.split_point")
    for index in range(3):
        p = parent["intervals"][index]
        l = left["intervals"][index]
        r = right["intervals"][index]
        if index != split_index:
            if not type_strict_equal(p, l) or not type_strict_equal(p, r):
                fail("cover_partition", "a split changed a nonsplit axis")
            continue
        if (
            not type_strict_equal(l["lower"], p["lower"])
            or l["lower_closed"] is not p["lower_closed"]
            or not type_strict_equal(r["upper"], p["upper"])
            or r["upper_closed"] is not p["upper_closed"]
        ):
            fail("cover_partition", "split children do not retain outer bounds")
        if (
            dyadic_fraction(l["upper"]) != split_point
            or dyadic_fraction(r["lower"]) != split_point
            or l["upper_closed"] is not False
            or r["lower_closed"] is not True
        ):
            fail(
                "cover_partition",
                "split boundary does not have left-open/right-closed ownership",
            )
        if not (
            dyadic_fraction(p["lower"])
            < split_point
            < dyadic_fraction(p["upper"])
        ):
            fail("cover_partition", "split point is not strictly interior")


def _normalized_widest_axis(
    box: Mapping[str, Any], domain: Mapping[str, Any]
) -> str:
    scores: list[Fraction] = []
    for interval, root_interval in zip(
        box["intervals"], domain["intervals"]
    ):
        width = dyadic_fraction(interval["upper"]) - dyadic_fraction(
            interval["lower"]
        )
        root_width = dyadic_fraction(
            root_interval["upper"]
        ) - dyadic_fraction(root_interval["lower"])
        scores.append(width / root_width)
    maximum = max(scores)
    return DOMAIN_AXES[scores.index(maximum)]


def _periods_and_radius(
    problem: Mapping[str, Any],
) -> tuple[list[dict[str, int]], dict[str, int]]:
    periods = problem["target_torus"]["periods_L_A"]
    radius = problem["hysteresis"]["r_out"]
    if type(periods) is not list or len(periods) != 9:
        fail("physical_problem", "target period list must have length nine")
    for index, period in enumerate(periods):
        if dyadic_fraction(period, f"$.periods[{index}]") <= 0:
            fail("physical_problem", f"target period {index} is not positive")
    if dyadic_fraction(radius, "$.r_out") <= 0:
        fail("physical_problem", "r_out is not positive")
    return copy.deepcopy(periods), copy.deepcopy(radius)


def build_empty_coordinate_image_range(
    *,
    axis: int,
    d_enclosure: Mapping[str, Any],
    period: Mapping[str, Any],
    radius: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Build the exact one-coordinate empty-image witness, if strict."""

    if type(axis) is not int or type(axis) is bool or axis not in range(9):
        fail("empty_coordinate_image_range", "axis must be an integer in 0..8")
    enclosure = _exact_keys(
        d_enclosure,
        {"lo", "hi"},
        "$.d_enclosure",
        "empty_coordinate_image_range",
    )
    lower = dyadic_fraction(enclosure["lo"], "$.d_enclosure.lo")
    upper = dyadic_fraction(enclosure["hi"], "$.d_enclosure.hi")
    if lower > upper:
        fail("empty_coordinate_image_range", "reversed d enclosure")
    lattice_period = dyadic_fraction(period, "$.period")
    r_out = dyadic_fraction(radius, "$.radius")
    if lattice_period <= 0 or r_out <= 0:
        fail("empty_coordinate_image_range", "period and radius must be positive")

    nmin = ceil_fraction((lower - r_out) / lattice_period)
    nmax = floor_fraction((upper + r_out) / lattice_period)
    if nmin <= nmax:
        return None

    above_previous = (lower - r_out) - nmax * lattice_period
    below_next = nmin * lattice_period - (upper + r_out)
    minimum = min(above_previous, below_next)
    if not above_previous > 0 or not below_next > 0 or not minimum > 0:
        fail(
            "empty_coordinate_image_range",
            "empty integer range lacks a strict exact-dyadic margin",
        )
    return {
        "witness_type": "empty_coordinate_image_range",
        "evaluated_on": "closed_hull_of_owned_half_open_box",
        "axis": axis,
        "d_enclosure": copy.deepcopy(dict(enclosure)),
        "period": copy.deepcopy(dict(period)),
        "radius": copy.deepcopy(dict(radius)),
        "nmin": nmin,
        "nmax": nmax,
        "margins": {
            "above_previous_image": dyadic_json(above_previous),
            "below_next_image": dyadic_json(below_next),
            "minimum": dyadic_json(minimum),
        },
    }


def _evaluate_leaf_witness(
    problem: Mapping[str, Any],
    box: Mapping[str, Any],
    periods: Sequence[Mapping[str, Any]],
    radius: Mapping[str, Any],
    precision_bits: int,
) -> dict[str, Any] | None:
    jets = evaluate_physical_jets(
        problem,
        _box_for_arb(box),
        lattice_image=[0] * 9,
        radius=radius,
        precision_bits=precision_bits,
    )
    if jets.get("problem_sha256") != PHYSICAL_PROBLEM_SEMANTIC_SHA256:
        fail("physical_jets", "physical evaluator returned a foreign problem hash")
    if jets.get("precision_bits") != precision_bits:
        fail("physical_jets", "physical evaluator returned a foreign precision")
    values = jets.get("d")
    if type(values) is not list or len(values) != 9:
        fail("physical_jets", "physical evaluator returned malformed d")
    for axis in TARGET_AXIS_ORDER:
        enclosure = arb_exact_endpoints(values[axis])
        witness = build_empty_coordinate_image_range(
            axis=axis,
            d_enclosure=enclosure,
            period=periods[axis],
            radius=radius,
        )
        if witness is not None:
            return witness
    return None


def _solver_registry(
    *,
    max_nodes: int = DEFAULT_MAX_NODES,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> dict[str, Any]:
    if type(max_nodes) is not int or max_nodes < 1 or max_nodes % 2 != 1:
        fail("solver_registry", "max_nodes must be a positive odd integer")
    if type(max_depth) is not int or max_depth < 0:
        fail("solver_registry", "max_depth must be nonnegative")
    return {
        "schema_version": SOLVER_REGISTRY_SCHEMA,
        "solver_id": "index2-finite-window-empty-coordinate-cover-v1",
        "physical_problem_semantic_sha256": (
            PHYSICAL_PROBLEM_SEMANTIC_SHA256
        ),
        "arb_backend": {
            "python_flint_version": PYTHON_FLINT_VERSION,
            "flint_version": FLINT_VERSION,
            "precision_bits": DEFAULT_PRECISION_BITS,
            "endpoint_encoding": (
                "exact reduced dyadics from Arb lower/upper endpoints"
            ),
        },
        "domain_axes": list(DOMAIN_AXES),
        "domain_topology_scope": (
            "half_open_rectangular_fundamental_domain_cover_only;"
            "no_exact_seam_equivalence_claim"
        ),
        "target_axis_tie_order": list(TARGET_AXIS_ORDER),
        "split_rule": {
            "kind": "normalized_widest_axis_midpoint",
            "axis_tie_order": list(DOMAIN_AXES),
            "ownership": "left_upper_open_right_lower_closed",
            "proof_evaluation": "closed_hull_of_each_owned_box",
        },
        "leaf_rule": {
            "kind": "empty_coordinate_image_range",
            "formula": (
                "nmin=ceil((infD-r_out)/L_A);"
                "nmax=floor((supD+r_out)/L_A);exclude iff nmin>nmax"
            ),
            "strict_contact_policy": "touching_is_not_excluded",
            "axis_selection": "first_excluding_target_axis_in_tie_order",
        },
        "budgets": {
            "max_nodes": max_nodes,
            "max_depth": max_depth,
            "budget_stop": "typed_unresolved_leaf",
        },
    }


def _node_hash(node: Mapping[str, Any]) -> str:
    payload = {
        key: copy.deepcopy(value)
        for key, value in node.items()
        if key != "node_semantic_sha256"
    }
    return semantic_sha256(payload)


class _CoverBuilder:
    def __init__(
        self,
        problem: Mapping[str, Any],
        domain: Mapping[str, Any],
        solver_registry: Mapping[str, Any],
    ) -> None:
        self.problem = problem
        self.domain = domain
        self.registry = solver_registry
        self.periods, self.radius = _periods_and_radius(problem)
        self.max_nodes = solver_registry["budgets"]["max_nodes"]
        self.max_depth = solver_registry["budgets"]["max_depth"]
        self.precision_bits = solver_registry["arb_backend"]["precision_bits"]
        self.nodes: list[dict[str, Any]] = []
        self.node_count = 0
        self.split_count = 0
        self.excluded_count = 0
        self.unresolved_count = 0
        self.maximum_depth = 0

    def build(
        self,
        box: Mapping[str, Any],
        node_id: str = "r",
        parent_id: str | None = None,
        depth: int = 0,
        reserved_nodes: int = 0,
    ) -> dict[str, Any]:
        # ``reserved_nodes`` counts still-uncreated right siblings belonging to
        # ancestors on the current depth-first path.  Reserving them before a
        # left subtree recurses is what guarantees that every legal odd node
        # budget ends in a complete binary tree with typed unresolved leaves,
        # rather than exhausting the budget before an ancestor's right child
        # can be materialized.
        if (
            type(reserved_nodes) is not int
            or reserved_nodes < 0
            or self.node_count + 1 + reserved_nodes > self.max_nodes
        ):
            fail("operation_budget", "invalid internal node reservation")
        self.node_count += 1
        self.maximum_depth = max(self.maximum_depth, depth)
        node: dict[str, Any] = {
            "node_id": node_id,
            "parent_id": parent_id,
            "depth": depth,
            "box": copy.deepcopy(dict(box)),
            "node_kind": "",
            "payload": {},
            "node_semantic_sha256": "",
        }
        self.nodes.append(node)

        witness = _evaluate_leaf_witness(
            self.problem,
            box,
            self.periods,
            self.radius,
            self.precision_bits,
        )
        if witness is not None:
            self.excluded_count += 1
            node["node_kind"] = "leaf"
            node["payload"] = {"witness": witness}
            node["node_semantic_sha256"] = _node_hash(node)
            return node

        if (
            depth >= self.max_depth
            or self.node_count + 2 + reserved_nodes > self.max_nodes
        ):
            self.unresolved_count += 1
            node["node_kind"] = "leaf"
            node["payload"] = {
                "witness": {
                    "witness_type": "unresolved",
                    "reason": (
                        "maximum_depth_exhausted"
                        if depth >= self.max_depth
                        else "node_budget_exhausted"
                    ),
                    "max_nodes": self.max_nodes,
                    "max_depth": self.max_depth,
                    "nodes_created_before_stop": self.node_count,
                    "next_action": "bisect_registered_box",
                }
            }
            node["node_semantic_sha256"] = _node_hash(node)
            return node

        axis = _normalized_widest_axis(box, self.domain)
        left_box, right_box, midpoint = _split_box(box, axis)
        self.split_count += 1
        left_id = node_id + "L"
        right_id = node_id + "R"
        left = self.build(
            left_box,
            left_id,
            node_id,
            depth + 1,
            reserved_nodes + 1,
        )
        right = self.build(
            right_box,
            right_id,
            node_id,
            depth + 1,
            reserved_nodes,
        )
        node["node_kind"] = "split"
        node["payload"] = {
            "split_type": "normalized_widest_axis_midpoint",
            "split_axis": axis,
            "split_point": midpoint,
            "left_child_id": left_id,
            "right_child_id": right_id,
            "left_child_semantic_sha256": left["node_semantic_sha256"],
            "right_child_semantic_sha256": right["node_semantic_sha256"],
        }
        node["node_semantic_sha256"] = _node_hash(node)
        return node


def _build_certificate_uncached(
    *,
    max_nodes: int = DEFAULT_MAX_NODES,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> dict[str, Any]:
    problem = _load_registered_problem()
    domain = _registered_domain(problem)
    registry = _solver_registry(max_nodes=max_nodes, max_depth=max_depth)
    registry_hash = semantic_sha256(registry)
    if (
        max_nodes == DEFAULT_MAX_NODES
        and max_depth == DEFAULT_MAX_DEPTH
        and SOLVER_REGISTRY_SEMANTIC_SHA256
        and registry_hash != SOLVER_REGISTRY_SEMANTIC_SHA256
    ):
        fail("solver_registry", "default registry differs from its code pin")

    builder = _CoverBuilder(problem, domain, registry)
    root = builder.build(domain)
    if builder.node_count != len(builder.nodes):
        fail("cover_partition", "node accounting is inconsistent")
    if builder.node_count != 2 * builder.split_count + 1:
        fail("cover_partition", "tree is not a complete finite binary tree")
    leaf_count = builder.excluded_count + builder.unresolved_count
    if leaf_count != builder.split_count + 1:
        fail("cover_partition", "leaf accounting is inconsistent")

    summary = {
        "node_count": builder.node_count,
        "split_nodes": builder.split_count,
        "leaf_count": leaf_count,
        "excluded_leaves": builder.excluded_count,
        "unresolved_leaves": builder.unresolved_count,
        "maximum_depth": builder.maximum_depth,
        "root_node_semantic_sha256": root["node_semantic_sha256"],
        "partition": "complete_gap_free_half_open_binary_tree",
        "proof_evaluation": "closed_hull_recomputed_at_every_leaf",
    }
    if builder.unresolved_count == 0:
        outcome = {
            "type": "right_censored_no_entry",
            "scope": "registered_finite_half_open_window_only",
            "window": copy.deepcopy(domain),
            "all_leaves_excluded": True,
            "unresolved_leaves": 0,
            "history_at_right_boundary": problem["observation"][
                "initial_history"
            ],
            "all_time_no_entry_claimed": False,
            "exact_seam_equivalence_claimed": False,
        }
    else:
        outcome = {
            "type": "finite_window_cover_unresolved",
            "scope": "registered_finite_half_open_window_only",
            "window": copy.deepcopy(domain),
            "all_leaves_excluded": False,
            "unresolved_leaves": builder.unresolved_count,
            "history_at_right_boundary": "undetermined",
            "all_time_no_entry_claimed": False,
            "exact_seam_equivalence_claimed": False,
        }
    certificate: dict[str, Any] = {
        "schema_version": CERTIFICATE_SCHEMA,
        "certificate_id": "index2-window0-empty-coordinate-cover-v1",
        "physical_problem_semantic_sha256": (
            PHYSICAL_PROBLEM_SEMANTIC_SHA256
        ),
        "solver_registry": registry,
        "solver_registry_semantic_sha256": registry_hash,
        "domain": domain,
        "tree": {
            "storage": "flat_preorder_with_bottom_up_child_hashes",
            "root_node_id": "r",
            "nodes": builder.nodes,
        },
        "summary": summary,
        "outcome": outcome,
        "certificate_semantic_sha256": "",
    }
    certificate["certificate_semantic_sha256"] = semantic_sha256(
        {
            key: value
            for key, value in certificate.items()
            if key != "certificate_semantic_sha256"
        }
    )
    return certificate


@lru_cache(maxsize=1)
def _default_certificate_bytes() -> bytes:
    return canonical_bytes(_build_certificate_uncached())


def build_certificate(
    *,
    max_nodes: int = DEFAULT_MAX_NODES,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> dict[str, Any]:
    if max_nodes == DEFAULT_MAX_NODES and max_depth == DEFAULT_MAX_DEPTH:
        return strict_json_loads(_default_certificate_bytes().decode("utf-8"))
    return _build_certificate_uncached(
        max_nodes=max_nodes, max_depth=max_depth
    )


def verify_certificate(certificate: Any) -> dict[str, Any]:
    obj = _exact_keys(
        certificate,
        {
            "schema_version",
            "certificate_id",
            "physical_problem_semantic_sha256",
            "solver_registry",
            "solver_registry_semantic_sha256",
            "domain",
            "tree",
            "summary",
            "outcome",
            "certificate_semantic_sha256",
        },
        "$",
        "certificate_schema",
    )
    if obj["schema_version"] != CERTIFICATE_SCHEMA:
        fail("certificate_schema", "unknown certificate schema")
    if obj["physical_problem_semantic_sha256"] != (
        PHYSICAL_PROBLEM_SEMANTIC_SHA256
    ):
        fail("physical_problem", "certificate names a foreign problem hash")

    registry = obj["solver_registry"]
    expected_registry = _solver_registry()
    if not type_strict_equal(registry, expected_registry):
        fail("solver_registry", "stored solver registry differs from the code pin")
    registry_hash = semantic_sha256(registry)
    if obj["solver_registry_semantic_sha256"] != registry_hash:
        fail("solver_registry", "stored solver registry hash is false")
    if (
        SOLVER_REGISTRY_SEMANTIC_SHA256
        and registry_hash != SOLVER_REGISTRY_SEMANTIC_SHA256
    ):
        fail("solver_registry", "stored solver registry differs from its code pin")

    stored_hash = obj["certificate_semantic_sha256"]
    expected_hash = semantic_sha256(
        {
            key: value
            for key, value in obj.items()
            if key != "certificate_semantic_sha256"
        }
    )
    if stored_hash != expected_hash:
        fail("certificate_hash", "stored certificate hash is false")

    # Deterministic regeneration rechecks every closed leaf with Arb.  This
    # rejects deletion, overlap, forged endpoints/witnesses, altered split
    # choices, and coordinated ordinary-hash resealing.
    expected = build_certificate()
    if not type_strict_equal(obj, expected):
        fail(
            "certificate_replay",
            "stored certificate differs from deterministic physical replay",
        )
    summary = obj["summary"]
    outcome = obj["outcome"]
    if summary["unresolved_leaves"] == 0:
        if outcome["type"] != "right_censored_no_entry":
            fail("outcome", "closed cover lacks right-censor outcome")
        if outcome["all_time_no_entry_claimed"] is not False:
            fail("outcome", "finite-window certificate claims all-time exclusion")
    elif outcome["type"] == "right_censored_no_entry":
        fail("outcome", "unresolved leaves forbid right-censor outcome")
    return {
        "certificate_semantic_sha256": stored_hash,
        "solver_registry_semantic_sha256": registry_hash,
        "physical_problem_semantic_sha256": (
            PHYSICAL_PROBLEM_SEMANTIC_SHA256
        ),
        "node_count": summary["node_count"],
        "split_nodes": summary["split_nodes"],
        "excluded_leaves": summary["excluded_leaves"],
        "unresolved_leaves": summary["unresolved_leaves"],
        "maximum_depth": summary["maximum_depth"],
        "outcome": outcome["type"],
    }


def build_report(certificate: Mapping[str, Any]) -> dict[str, Any]:
    replay = verify_certificate(certificate)
    report: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "report_id": "index2-finite-window-no-entry-cover-report-v1",
        "certificate_schema_version": CERTIFICATE_SCHEMA,
        "certificate_semantic_sha256": replay[
            "certificate_semantic_sha256"
        ],
        "solver_registry_semantic_sha256": replay[
            "solver_registry_semantic_sha256"
        ],
        "physical_problem_semantic_sha256": replay[
            "physical_problem_semantic_sha256"
        ],
        "backend": copy.deepcopy(
            certificate["solver_registry"]["arb_backend"]
        ),
        "tree_summary": {
            key: replay[key]
            for key in (
                "node_count",
                "split_nodes",
                "excluded_leaves",
                "unresolved_leaves",
                "maximum_depth",
            )
        },
        "outcome": replay["outcome"],
        "claims": {
            "fixed_source_index": 2,
            "complete_registered_window_partition": True,
            "every_leaf_recomputed_on_closure_with_arb": True,
            "empty_coordinate_image_ranges_are_strict": True,
            "finite_window_right_censoring_only": True,
            "all_time_no_entry": False,
            "exact_worldsheet_seam_equivalence": False,
            "population_law": False,
            "dimension_selection": False,
        },
        "report_semantic_sha256": "",
    }
    report["report_semantic_sha256"] = semantic_sha256(
        {
            key: value
            for key, value in report.items()
            if key != "report_semantic_sha256"
        }
    )
    return report


def verify_report(
    report: Any, certificate: Mapping[str, Any]
) -> dict[str, Any]:
    expected = build_report(certificate)
    if not type_strict_equal(report, expected):
        fail("report_replay", "stored report differs from regeneration")
    return expected


def reseal_certificate_hashes(certificate: dict[str, Any]) -> None:
    """Test helper: recompute ordinary node/child/root/certificate hashes.

    This intentionally does not repair scientific content.  It lets hostile
    tests show that coordinated ordinary-hash resealing is rejected by full
    physical replay.
    """

    nodes = certificate["tree"]["nodes"]
    by_id = {node["node_id"]: node for node in nodes}

    def seal(node_id: str) -> str:
        node = by_id[node_id]
        if node["node_kind"] == "split":
            payload = node["payload"]
            left_hash = seal(payload["left_child_id"])
            right_hash = seal(payload["right_child_id"])
            payload["left_child_semantic_sha256"] = left_hash
            payload["right_child_semantic_sha256"] = right_hash
        node["node_semantic_sha256"] = _node_hash(node)
        return node["node_semantic_sha256"]

    root_hash = seal(certificate["tree"]["root_node_id"])
    certificate["summary"]["root_node_semantic_sha256"] = root_hash
    certificate["solver_registry_semantic_sha256"] = semantic_sha256(
        certificate["solver_registry"]
    )
    certificate["certificate_semantic_sha256"] = semantic_sha256(
        {
            key: value
            for key, value in certificate.items()
            if key != "certificate_semantic_sha256"
        }
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument(
        "--certificate", type=Path, default=DEFAULT_CERTIFICATE
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)

    certificate = build_certificate()
    report = build_report(certificate)
    if args.write:
        write_json(args.certificate, certificate)
        write_json(args.report, report)
        return 0

    stored_certificate = strict_json_load(args.certificate)
    stored_report = strict_json_load(args.report)
    verify_certificate(stored_certificate)
    verify_report(stored_report, stored_certificate)
    if not type_strict_equal(stored_certificate, certificate):
        fail("certificate_check", "stored certificate differs from regeneration")
    if not type_strict_equal(stored_report, report):
        fail("report_check", "stored report differs from regeneration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
