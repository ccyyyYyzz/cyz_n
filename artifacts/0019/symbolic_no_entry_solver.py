#!/usr/bin/env python3
"""Canonical symbolic-pi finite-window transverse no-entry cover.

The solver consumes the independently verified symbolic-pi closed-string
lift, covers ``u1,u2 in [0,1)`` and the registered half-open time window,
and evaluates the closed hull of every owned leaf with the fail-closed
``symbolic_physical_arb_jets`` evaluator.  A leaf is excluded only when one
of transverse target axes 0..7 has a strictly empty radius-expanded lattice
image range.  Consequently the proof is invariant under the exact
worldsheet seam reindexing and does not use the winding image or winding
metric.
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

import symbolic_physical_arb_jets as symbolic_jets  # noqa: E402
import symbolic_pi_lift as symbolic_lift  # noqa: E402


CERTIFICATE_SCHEMA = (
    "cyz-brief-0019-symbolic-transverse-no-entry-certificate-v1"
)
REPORT_SCHEMA = (
    "cyz-brief-0019-symbolic-transverse-no-entry-report-v1"
)
SOLVER_REGISTRY_SCHEMA = (
    "cyz-brief-0019-symbolic-transverse-no-entry-solver-registry-v1"
)

CLOSED_STRING_PROBLEM_SEMANTIC_SHA256 = (
    "3bb6599f211c26d98ecba2077051ad9d0339daf96d580a6399cc5a1ba7f030e0"
)
SYMBOLIC_LIFT_REGISTRY_SEMANTIC_SHA256 = (
    "c80acb64eeeb3133dff4422fc798f5b75c6feb52cf32502888cac452e2d210a1"
)
# Frozen after the complete registry schema and default budgets are built.
SOLVER_REGISTRY_SEMANTIC_SHA256 = (
    "23e404021dcae9b4c75dca810feb404afe6786aa14280f0ae88b0fa4f24fcec5"
)

PYTHON_FLINT_VERSION = "0.9.0"
FLINT_VERSION = "3.6.0"
DEFAULT_PRECISION_BITS = 192
DEFAULT_MAX_NODES = 4095
DEFAULT_MAX_DEPTH = 48
EXPECTED_NODE_COUNT = 259
EXPECTED_SPLIT_COUNT = 129
EXPECTED_LEAF_COUNT = 130
EXPECTED_MAXIMUM_DEPTH = 9
EXPECTED_AXIS_COUNTS = [14, 66, 12, 10, 4, 0, 0, 24]

DOMAIN_AXES = ("u1", "u2", "t")
TRANSVERSE_TARGET_AXES = tuple(range(8))
TRANSVERSE_PERIOD = Fraction(8)
REGISTERED_RADIUS = Fraction(1, 2)

LIFT_FIXTURE = HERE / "symbolic_pi_lift_fixture.json"
DEFAULT_CERTIFICATE = HERE / "symbolic_no_entry_certificate.json"
DEFAULT_REPORT = HERE / "symbolic_no_entry_report.json"


class SymbolicNoEntryError(ValueError):
    """A symbolic cover or certificate failed a typed gate."""


def fail(gate: str, message: str) -> None:
    raise SymbolicNoEntryError(f"{gate}: {message}")


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
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite,
            parse_float=_reject_float,
        )
    except SymbolicNoEntryError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        fail("strict_json", str(error))
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
        return set(left) == set(right) and all(
            type_strict_equal(left[key], right[key]) for key in left
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
    value: Any,
    expected: set[str],
    path: str,
    gate: str,
) -> Mapping[str, Any]:
    if type(value) is not dict:
        fail(gate, f"{path} must be an object")
    actual = set(value)
    if actual != expected:
        fail(
            gate,
            f"{path} keys differ; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}",
        )
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
    if exponent < 0 or exponent > 1_000_000:
        fail("dyadic_encoding", f"{path}.exponent is outside limits")
    if numerator == 0 and exponent != 0:
        fail("dyadic_encoding", f"{path} zero must have exponent zero")
    if numerator and exponent and numerator % 2 == 0:
        fail("dyadic_encoding", f"{path} is not reduced")
    return Fraction(numerator, 1 << exponent)


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


def _pi_free_fraction(value: Any, path: str) -> Fraction:
    try:
        fraction, pi_exponent = symbolic_lift.parse_symbolic_atom(
            value, path
        )
    except Exception as error:
        fail("symbolic_problem", f"{path} is invalid: {error}")
    if pi_exponent != 0:
        fail("symbolic_problem", f"{path} must be pi-free")
    return fraction


def _load_registered_problem() -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        fixture = symbolic_lift.strict_json_load(LIFT_FIXTURE)
        replay = symbolic_lift.verify_fixture(fixture)
    except Exception as error:
        fail("symbolic_lift", str(error))
    if type(fixture) is not dict:
        fail("symbolic_lift", "lift fixture is not an object")
    problem = fixture.get("closed_string_problem")
    if type(problem) is not dict:
        fail("symbolic_lift", "lift fixture lacks closed_string_problem")
    digest = symbolic_lift.semantic_sha256(problem)
    if digest != CLOSED_STRING_PROBLEM_SEMANTIC_SHA256:
        fail("symbolic_lift", "closed-string problem hash differs")
    if replay.get("closed_string_problem_semantic_sha256") != digest:
        fail("symbolic_lift", "lift replay returned a foreign problem")
    if replay.get("lift_registry_semantic_sha256") != (
        SYMBOLIC_LIFT_REGISTRY_SEMANTIC_SHA256
    ):
        fail("symbolic_lift", "lift registry hash differs")
    if symbolic_jets.CANONICAL_CLOSED_STRING_PROBLEM_SEMANTIC_SHA256 != (
        digest
    ):
        fail("symbolic_jets", "jet evaluator pins a different problem")
    return problem, replay


def _registered_domain(problem: Mapping[str, Any]) -> dict[str, Any]:
    observation = _exact_keys(
        problem.get("observation"),
        {
            "t0",
            "t1",
            "window_closure",
            "initial_history",
            "continuation_convention",
            "time_is_quotient",
            "window_transport",
        },
        "$.problem.observation",
        "domain",
    )
    if observation["window_closure"] != "lower_closed_upper_open":
        fail("domain", "time window must be lower-closed upper-open")
    if observation["time_is_quotient"] is not False:
        fail("domain", "registered time must not be relabelled a quotient")
    t0 = _pi_free_fraction(observation["t0"], "$.observation.t0")
    t1 = _pi_free_fraction(observation["t1"], "$.observation.t1")
    if not t0 < t1:
        fail("domain", "registered time window is empty")

    def interval(lower: Fraction, upper: Fraction) -> dict[str, Any]:
        return {
            "lower": dyadic_json(lower),
            "upper": dyadic_json(upper),
            "lower_closed": True,
            "upper_closed": False,
        }

    domain = {
        "axes": list(DOMAIN_AXES),
        "intervals": [
            interval(Fraction(0), Fraction(1)),
            interval(Fraction(0), Fraction(1)),
            interval(t0, t1),
        ],
    }
    _validate_box(domain, "$.domain")
    return domain


def _validate_box(value: Any, path: str) -> dict[str, Any]:
    box = _exact_keys(
        value, {"axes", "intervals"}, path, "cover_partition"
    )
    if box["axes"] != list(DOMAIN_AXES) or any(
        type(axis) is not str for axis in box["axes"]
    ):
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
            fail("cover_partition", f"{path} contains an empty interval")
        if item["lower_closed"] is not True:
            fail("cover_partition", f"{path} lower endpoint is not owned")
        if item["upper_closed"] is not False:
            fail("cover_partition", f"{path} upper endpoint must be open")
    return dict(box)


def _box_for_arb(box: Mapping[str, Any]) -> dict[str, Any]:
    _validate_box(box, "$.owned_box")
    return {
        axis: {
            "lo": copy.deepcopy(interval["lower"]),
            "hi": copy.deepcopy(interval["upper"]),
        }
        for axis, interval in zip(box["axes"], box["intervals"])
    }


def _split_box(
    box: Mapping[str, Any],
    axis: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, int]]:
    if axis not in DOMAIN_AXES:
        fail("cover_partition", f"unknown split axis {axis!r}")
    index = DOMAIN_AXES.index(axis)
    interval = box["intervals"][index]
    lower = dyadic_fraction(interval["lower"])
    upper = dyadic_fraction(interval["upper"])
    midpoint = (lower + upper) / 2
    left = copy.deepcopy(dict(box))
    right = copy.deepcopy(dict(box))
    left["intervals"][index]["upper"] = dyadic_json(midpoint)
    left["intervals"][index]["upper_closed"] = False
    right["intervals"][index]["lower"] = dyadic_json(midpoint)
    right["intervals"][index]["lower_closed"] = True
    encoded = dyadic_json(midpoint)
    _validate_split(box, left, right, axis, encoded)
    return left, right, encoded


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
    if axis not in DOMAIN_AXES:
        fail("cover_partition", "split axis is outside the registry")
    split_index = DOMAIN_AXES.index(axis)
    split_point = dyadic_fraction(point, "$.split_point")
    for index in range(3):
        p = parent["intervals"][index]
        l = left["intervals"][index]
        r = right["intervals"][index]
        if index != split_index:
            if not type_strict_equal(p, l) or not type_strict_equal(p, r):
                fail("cover_partition", "split changed a nonsplit axis")
            continue
        if (
            not type_strict_equal(l["lower"], p["lower"])
            or l["lower_closed"] is not p["lower_closed"]
            or not type_strict_equal(r["upper"], p["upper"])
            or r["upper_closed"] is not p["upper_closed"]
        ):
            fail("cover_partition", "children changed outer ownership")
        if (
            dyadic_fraction(l["upper"]) != split_point
            or dyadic_fraction(r["lower"]) != split_point
            or l["upper_closed"] is not False
            or r["lower_closed"] is not True
        ):
            fail("cover_partition", "split ownership is not left-open/right-closed")
        if not (
            dyadic_fraction(p["lower"])
            < split_point
            < dyadic_fraction(p["upper"])
        ):
            fail("cover_partition", "split point is not strictly interior")


def _normalized_widest_axis(
    box: Mapping[str, Any],
    domain: Mapping[str, Any],
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
    torus = _exact_keys(
        problem.get("target_torus"),
        {
            "metric_convention",
            "metric_diagonal",
            "lattice_convention",
            "lattice_matrix_diagonal",
            "periods",
            "image_separation",
        },
        "$.problem.target_torus",
        "symbolic_problem",
    )
    periods = torus["periods"]
    if type(periods) is not list or len(periods) != 9:
        fail("symbolic_problem", "target periods must have length nine")
    for axis in TRANSVERSE_TARGET_AXES:
        if _pi_free_fraction(
            periods[axis], f"$.target_torus.periods[{axis}]"
        ) != TRANSVERSE_PERIOD:
            fail("symbolic_problem", "transverse target period is not eight")
    radius = _pi_free_fraction(
        problem["hysteresis"]["r_out"], "$.hysteresis.r_out"
    )
    if radius != REGISTERED_RADIUS:
        fail("symbolic_problem", "registered r_out is not one half")
    return (
        [dyadic_json(TRANSVERSE_PERIOD) for _ in TRANSVERSE_TARGET_AXES],
        dyadic_json(radius),
    )


def build_empty_coordinate_image_range(
    *,
    axis: int,
    d_enclosure: Mapping[str, Any],
    period: Mapping[str, Any],
    radius: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Build one strict transverse coordinate-image exclusion witness."""

    if (
        type(axis) is not int
        or type(axis) is bool
        or axis not in TRANSVERSE_TARGET_AXES
    ):
        fail(
            "empty_coordinate_image_range",
            "axis must be a transverse integer in 0..7",
        )
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
    if lattice_period != TRANSVERSE_PERIOD:
        fail("empty_coordinate_image_range", "period must be exactly eight")
    if r_out != REGISTERED_RADIUS:
        fail("empty_coordinate_image_range", "radius must be exactly one half")

    nmin = ceil_fraction((lower - r_out) / lattice_period)
    nmax = floor_fraction((upper + r_out) / lattice_period)
    if nmin <= nmax:
        return None
    above_previous = (lower - r_out) - nmax * lattice_period
    below_next = nmin * lattice_period - (upper + r_out)
    minimum = min(above_previous, below_next)
    if above_previous <= 0 or below_next <= 0 or minimum <= 0:
        fail(
            "empty_coordinate_image_range",
            "empty range lacks a strict dyadic margin",
        )
    return {
        "witness_type": "empty_transverse_coordinate_image_range",
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
        "winding_image_used": False,
        "winding_metric_used": False,
    }


def _evaluate_leaf_witness(
    problem: Mapping[str, Any],
    box: Mapping[str, Any],
    periods: Sequence[Mapping[str, Any]],
    radius: Mapping[str, Any],
    precision_bits: int,
) -> dict[str, Any] | None:
    try:
        jets = symbolic_jets.evaluate_symbolic_physical_jets(
            problem,
            _box_for_arb(box),
            lattice_image=[0] * 9,
            radius=radius,
            precision_bits=precision_bits,
        )
    except Exception as error:
        fail("symbolic_physical_jets", str(error))
    if jets.get("problem_sha256") != CLOSED_STRING_PROBLEM_SEMANTIC_SHA256:
        fail("symbolic_physical_jets", "evaluator returned a foreign problem")
    if jets.get("precision_bits") != precision_bits:
        fail("symbolic_physical_jets", "evaluator returned foreign precision")
    if tuple(jets.get("variable_order", ())) != DOMAIN_AXES:
        fail("symbolic_physical_jets", "evaluator variable order differs")
    values = jets.get("d")
    if type(values) is not list or len(values) != 9:
        fail("symbolic_physical_jets", "evaluator returned malformed d")
    for axis in TRANSVERSE_TARGET_AXES:
        try:
            enclosure = symbolic_jets.arb_exact_endpoints(values[axis])
        except Exception as error:
            fail("symbolic_physical_jets", f"axis {axis}: {error}")
        witness = build_empty_coordinate_image_range(
            axis=axis,
            d_enclosure=enclosure,
            period=periods[axis],
            radius=radius,
        )
        if witness is not None:
            return witness
    return None


def _backend_registry() -> dict[str, Any]:
    try:
        backend = symbolic_jets.check_backend()
    except Exception as error:
        fail("arb_backend", str(error))
    if backend.get("python_flint") != PYTHON_FLINT_VERSION:
        fail("arb_backend", "python-flint version differs")
    if backend.get("flint") != FLINT_VERSION:
        fail("arb_backend", "FLINT version differs")
    return {
        "python_flint_version": PYTHON_FLINT_VERSION,
        "flint_version": FLINT_VERSION,
        "precision_bits": DEFAULT_PRECISION_BITS,
        "endpoint_encoding": (
            "exact reduced dyadics from Arb lower/upper endpoints"
        ),
        "evaluator": (
            "symbolic_physical_arb_jets.evaluate_symbolic_physical_jets"
        ),
        "fail_closed_problem_hash": CLOSED_STRING_PROBLEM_SEMANTIC_SHA256,
    }


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
        "solver_id": "index2-symbolic-pi-transverse-cover-v1",
        "closed_string_problem_semantic_sha256": (
            CLOSED_STRING_PROBLEM_SEMANTIC_SHA256
        ),
        "symbolic_lift_registry_semantic_sha256": (
            SYMBOLIC_LIFT_REGISTRY_SEMANTIC_SHA256
        ),
        "arb_backend": _backend_registry(),
        "domain_axes": list(DOMAIN_AXES),
        "domain_topology_scope": (
            "exact_closed_string_quotient_fundamental_domain;"
            "u1_u2_mod_one;t_finite_half_open"
        ),
        "exact_seam_gate": {
            "provider": "symbolic_pi_lift.verify_fixture",
            "transverse_identity": (
                "integer Fourier harmonics are exactly periodic under u_i+1"
            ),
            "winding_reindex": (
                "verified but unused by transverse exclusion witnesses"
            ),
        },
        "proof_target_axis_order": list(TRANSVERSE_TARGET_AXES),
        "proof_independence": {
            "transverse_period": dyadic_json(TRANSVERSE_PERIOD),
            "radius": dyadic_json(REGISTERED_RADIUS),
            "winding_axis_used": False,
            "winding_image_used": False,
            "winding_metric_used": False,
        },
        "split_rule": {
            "kind": "normalized_widest_axis_midpoint",
            "axis_tie_order": list(DOMAIN_AXES),
            "ownership": "left_upper_open_right_lower_closed",
            "proof_evaluation": "closed_hull_of_each_owned_box",
        },
        "leaf_rule": {
            "kind": "empty_transverse_coordinate_image_range",
            "formula": (
                "nmin=ceil((infD-r_out)/8);"
                "nmax=floor((supD+r_out)/8);exclude iff nmin>nmax"
            ),
            "strict_contact_policy": "touching_is_not_excluded",
            "axis_selection": "first_excluding_axis_in_0_through_7",
        },
        "budgets": {
            "max_nodes": max_nodes,
            "max_depth": max_depth,
            "budget_stop": "typed_unresolved_leaf_with_reserved_nodes",
        },
    }


def _node_hash(node: Mapping[str, Any]) -> str:
    return semantic_sha256(
        {
            key: copy.deepcopy(value)
            for key, value in node.items()
            if key != "node_semantic_sha256"
        }
    )


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
        self.axis_counts = [0 for _ in TRANSVERSE_TARGET_AXES]

    def build(
        self,
        box: Mapping[str, Any],
        node_id: str = "r",
        parent_id: str | None = None,
        depth: int = 0,
        reserved_nodes: int = 0,
    ) -> dict[str, Any]:
        # Each ancestor whose left subtree is active has one not-yet-created
        # right child.  Reserving those nodes makes every legal odd budget end
        # in a complete tree with typed unresolved leaves.
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
            self.axis_counts[witness["axis"]] += 1
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
                    "reserved_nodes": reserved_nodes,
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
    problem, lift_replay = _load_registered_problem()
    domain = _registered_domain(problem)
    registry = _solver_registry(max_nodes=max_nodes, max_depth=max_depth)
    registry_hash = semantic_sha256(registry)
    is_default = (
        max_nodes == DEFAULT_MAX_NODES
        and max_depth == DEFAULT_MAX_DEPTH
    )
    if (
        is_default
        and SOLVER_REGISTRY_SEMANTIC_SHA256
        and registry_hash != SOLVER_REGISTRY_SEMANTIC_SHA256
    ):
        fail("solver_registry", "default registry differs from code pin")

    builder = _CoverBuilder(problem, domain, registry)
    root = builder.build(domain)
    if builder.node_count != len(builder.nodes):
        fail("cover_partition", "node accounting is inconsistent")
    if builder.node_count != 2 * builder.split_count + 1:
        fail("cover_partition", "tree is not a complete finite binary tree")
    leaf_count = builder.excluded_count + builder.unresolved_count
    if leaf_count != builder.split_count + 1:
        fail("cover_partition", "leaf accounting is inconsistent")

    if is_default:
        expected = (
            EXPECTED_NODE_COUNT,
            EXPECTED_SPLIT_COUNT,
            EXPECTED_LEAF_COUNT,
            EXPECTED_MAXIMUM_DEPTH,
            EXPECTED_AXIS_COUNTS,
        )
        actual = (
            builder.node_count,
            builder.split_count,
            leaf_count,
            builder.maximum_depth,
            builder.axis_counts,
        )
        if actual != expected or builder.unresolved_count != 0:
            fail(
                "default_topology",
                f"default cover drifted; expected={expected}, actual={actual}",
            )

    summary = {
        "node_count": builder.node_count,
        "split_nodes": builder.split_count,
        "leaf_count": leaf_count,
        "excluded_leaves": builder.excluded_count,
        "unresolved_leaves": builder.unresolved_count,
        "maximum_depth": builder.maximum_depth,
        "transverse_axis_counts": list(builder.axis_counts),
        "proof_target_axes": list(TRANSVERSE_TARGET_AXES),
        "root_node_semantic_sha256": root["node_semantic_sha256"],
        "partition": "complete_gap_free_half_open_binary_tree",
        "proof_evaluation": "closed_hull_recomputed_at_every_leaf",
    }
    if builder.unresolved_count == 0:
        outcome = {
            "type": "right_censored_no_entry",
            "scope": "registered_finite_closed_string_window_only",
            "window": copy.deepcopy(domain),
            "all_leaves_excluded": True,
            "unresolved_leaves": 0,
            "history_at_right_boundary": problem["observation"][
                "initial_history"
            ],
            "all_time_no_entry_claimed": False,
            "exact_worldsheet_quotient_claimed": True,
            "transverse_exclusion_only": True,
            "winding_image_used": False,
            "winding_metric_used": False,
        }
    else:
        outcome = {
            "type": "finite_window_cover_unresolved",
            "scope": "registered_finite_closed_string_window_only",
            "window": copy.deepcopy(domain),
            "all_leaves_excluded": False,
            "unresolved_leaves": builder.unresolved_count,
            "history_at_right_boundary": "undetermined",
            "all_time_no_entry_claimed": False,
            "exact_worldsheet_quotient_claimed": True,
            "transverse_exclusion_only": True,
            "winding_image_used": False,
            "winding_metric_used": False,
        }

    certificate: dict[str, Any] = {
        "schema_version": CERTIFICATE_SCHEMA,
        "certificate_id": (
            "index2-symbolic-pi-window0-transverse-cover-v1"
        ),
        "closed_string_problem_semantic_sha256": (
            CLOSED_STRING_PROBLEM_SEMANTIC_SHA256
        ),
        "symbolic_lift_registry_semantic_sha256": (
            lift_replay["lift_registry_semantic_sha256"]
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
    if (
        max_nodes == DEFAULT_MAX_NODES
        and max_depth == DEFAULT_MAX_DEPTH
    ):
        return strict_json_loads(
            _default_certificate_bytes().decode("utf-8")
        )
    return _build_certificate_uncached(
        max_nodes=max_nodes, max_depth=max_depth
    )


def verify_certificate(certificate: Any) -> dict[str, Any]:
    obj = _exact_keys(
        certificate,
        {
            "schema_version",
            "certificate_id",
            "closed_string_problem_semantic_sha256",
            "symbolic_lift_registry_semantic_sha256",
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
    if obj["certificate_id"] != (
        "index2-symbolic-pi-window0-transverse-cover-v1"
    ):
        fail("certificate_schema", "certificate id differs")
    if obj["closed_string_problem_semantic_sha256"] != (
        CLOSED_STRING_PROBLEM_SEMANTIC_SHA256
    ):
        fail("symbolic_problem", "certificate names a foreign problem")
    if obj["symbolic_lift_registry_semantic_sha256"] != (
        SYMBOLIC_LIFT_REGISTRY_SEMANTIC_SHA256
    ):
        fail("symbolic_lift", "certificate names a foreign lift registry")
    _load_registered_problem()

    expected_registry = _solver_registry()
    if not type_strict_equal(obj["solver_registry"], expected_registry):
        fail("solver_registry", "stored registry differs from code pin")
    registry_hash = semantic_sha256(obj["solver_registry"])
    if obj["solver_registry_semantic_sha256"] != registry_hash:
        fail("solver_registry", "stored solver registry hash is false")
    if (
        SOLVER_REGISTRY_SEMANTIC_SHA256
        and registry_hash != SOLVER_REGISTRY_SEMANTIC_SHA256
    ):
        fail("solver_registry", "stored registry differs from hash pin")

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

    expected = build_certificate()
    if not type_strict_equal(obj, expected):
        fail(
            "certificate_replay",
            "stored certificate differs from deterministic symbolic replay",
        )
    summary = obj["summary"]
    outcome = obj["outcome"]
    if summary["unresolved_leaves"] != 0:
        fail("outcome", "default certificate contains unresolved leaves")
    if outcome["type"] != "right_censored_no_entry":
        fail("outcome", "closed cover lacks right-censor outcome")
    if outcome["exact_worldsheet_quotient_claimed"] is not True:
        fail("outcome", "symbolic quotient claim is missing")
    if outcome["all_time_no_entry_claimed"] is not False:
        fail("outcome", "finite-window cover claims all-time exclusion")
    if (
        outcome["winding_image_used"] is not False
        or outcome["winding_metric_used"] is not False
    ):
        fail("outcome", "transverse proof claims winding dependence")
    return {
        "certificate_semantic_sha256": stored_hash,
        "solver_registry_semantic_sha256": registry_hash,
        "closed_string_problem_semantic_sha256": (
            CLOSED_STRING_PROBLEM_SEMANTIC_SHA256
        ),
        "symbolic_lift_registry_semantic_sha256": (
            SYMBOLIC_LIFT_REGISTRY_SEMANTIC_SHA256
        ),
        "node_count": summary["node_count"],
        "split_nodes": summary["split_nodes"],
        "excluded_leaves": summary["excluded_leaves"],
        "unresolved_leaves": summary["unresolved_leaves"],
        "maximum_depth": summary["maximum_depth"],
        "transverse_axis_counts": copy.deepcopy(
            summary["transverse_axis_counts"]
        ),
        "outcome": outcome["type"],
        "exact_worldsheet_quotient": True,
        "winding_image_used": False,
        "winding_metric_used": False,
    }


def build_report(certificate: Mapping[str, Any]) -> dict[str, Any]:
    replay = verify_certificate(certificate)
    report: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "report_id": (
            "index2-symbolic-pi-transverse-no-entry-cover-report-v1"
        ),
        "certificate_schema_version": CERTIFICATE_SCHEMA,
        "certificate_semantic_sha256": replay[
            "certificate_semantic_sha256"
        ],
        "solver_registry_semantic_sha256": replay[
            "solver_registry_semantic_sha256"
        ],
        "closed_string_problem_semantic_sha256": replay[
            "closed_string_problem_semantic_sha256"
        ],
        "symbolic_lift_registry_semantic_sha256": replay[
            "symbolic_lift_registry_semantic_sha256"
        ],
        "backend": copy.deepcopy(
            certificate["solver_registry"]["arb_backend"]
        ),
        "tree_summary": {
            key: copy.deepcopy(replay[key])
            for key in (
                "node_count",
                "split_nodes",
                "excluded_leaves",
                "unresolved_leaves",
                "maximum_depth",
                "transverse_axis_counts",
            )
        },
        "outcome": replay["outcome"],
        "claims": {
            "fixed_source_index": 2,
            "exact_symbolic_pi_closed_string_lift": True,
            "exact_worldsheet_quotient": True,
            "complete_registered_window_partition": True,
            "every_leaf_recomputed_on_closure_with_arb": True,
            "strict_transverse_empty_image_ranges": True,
            "proof_target_axes": list(TRANSVERSE_TARGET_AXES),
            "transverse_period": dyadic_json(TRANSVERSE_PERIOD),
            "radius": dyadic_json(REGISTERED_RADIUS),
            "winding_image_used": False,
            "winding_metric_used": False,
            "finite_window_right_censoring_only": True,
            "all_time_no_entry": False,
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
    report: Any,
    certificate: Mapping[str, Any],
) -> dict[str, Any]:
    expected = build_report(certificate)
    if not type_strict_equal(report, expected):
        fail("report_replay", "stored report differs from regeneration")
    return expected


def reseal_certificate_hashes(certificate: dict[str, Any]) -> None:
    """Refresh ordinary hashes without repairing hostile scientific content."""

    nodes = certificate["tree"]["nodes"]
    by_id = {node["node_id"]: node for node in nodes}
    for node in reversed(nodes):
        if node["node_kind"] == "split":
            payload = node["payload"]
            left = by_id.get(payload["left_child_id"])
            right = by_id.get(payload["right_child_id"])
            if left is not None:
                payload["left_child_semantic_sha256"] = left[
                    "node_semantic_sha256"
                ]
            if right is not None:
                payload["right_child_semantic_sha256"] = right[
                    "node_semantic_sha256"
                ]
        node["node_semantic_sha256"] = _node_hash(node)
    root = by_id.get(certificate["tree"]["root_node_id"])
    if root is not None:
        certificate["summary"]["root_node_semantic_sha256"] = root[
            "node_semantic_sha256"
        ]
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
        fail("certificate_check", "stored certificate differs")
    if not type_strict_equal(stored_report, report):
        fail("report_check", "stored report differs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
