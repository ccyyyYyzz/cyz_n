#!/usr/bin/env python3
"""Independent replay of the Brief 0019 finite-window no-entry certificate.

The source/problem-binding gate is imported from ``source_binding_replayer``.
Everything after that gate is implemented again here: strict certificate
JSON, reduced dyadics, exact Arb ingress, physical F1 kinematics, coordinate
image exclusion, half-open tree coverage, and bottom-up commitments.

This module deliberately does not import or dynamically load any solver,
physical-jet generator, foundation jet, or certified-solver module.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

import flint
from flint import arb, ctx

import source_binding_replayer as source_binding


CERTIFICATE_SCHEMA = "cyz-brief-0019-physical-no-entry-certificate-v1"
REPORT_SCHEMA = "cyz-brief-0019-physical-no-entry-replayer-report-v1"
PROBLEM_SCHEMA = "cyz-brief-0019-exact-dyadic-f1-problem-v1"
SOLVER_REGISTRY_SCHEMA = "cyz-brief-0019-physical-no-entry-solver-registry-v1"
SUCCESS_OUTCOME = "right_censored_no_entry"

PYTHON_FLINT_VERSION = "0.9.0"
FLINT_VERSION = "3.6.0"
PHYSICAL_PROBLEM_SEMANTIC_SHA256 = (
    "1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca"
)
SOURCE_BINDING_REPLAYER_NORMALIZED_LF_SHA256 = (
    "86e4f959a2f1b2db063172baf342d1854bac143711177e2344656756233803d4"
)

# Filled only after the solver registry is frozen.  A nonempty code anchor is
# mandatory during replay, so an unregistered solver cannot self-authorize.
PINNED_SOLVER_REGISTRY_SHA256 = (
    "e0563bd70cd1d9b330d507605b34f0a7f61f8b6abba1f19c556da8462b51d541"
)

ARTIFACT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = ARTIFACT_DIR.parent.parent
SOURCE_FIXTURE_PATH = ARTIFACT_DIR / "source_state_bridge_fixture.json"
SOURCE_BINDING_PATH = ARTIFACT_DIR / "source_binding_replayer.py"
CERTIFICATE_PATH = ARTIFACT_DIR / "physical_no_entry_certificate.json"
REPORT_PATH = ARTIFACT_DIR / "physical_no_entry_replayer_report.json"
INVENTORY_PATHS = (
    "artifacts/0018/source_registry.json",
    "artifacts/0019/source_state_bridge_fixture.json",
    "artifacts/0019/source_binding_replayer.py",
    "artifacts/0019/physical_no_entry_certificate.json",
    "artifacts/0019/physical_no_entry_replayer.py",
    "artifacts/0019/test_physical_no_entry_replayer.py",
)

HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
DYADIC_KEYS = {"numerator", "exponent"}
INTERVAL_KEYS = {"lower", "upper", "lower_closed", "upper_closed"}
BOX_AXES = ("sigma1", "sigma2", "t")
TARGET_DIMENSION = 9
TRANSVERSE_DIMENSION = 8
WINDING_AXIS = 8
FORBIDDEN_DYNAMIC_NAMES = {
    "physical_arb_jets",
    "physical_no_entry_solver",
    "source_state_bridge",
    "arb_interval_jets",
    "certified_solver_core",
}


class NoEntryReplayError(ValueError):
    """One independent certificate gate failed."""

    def __init__(self, gate: str, message: str):
        super().__init__(f"{gate}: {message}")
        self.gate = gate


def fail(gate: str, message: str) -> None:
    raise NoEntryReplayError(gate, message)


def _exact_keys(
    value: Any,
    expected: set[str],
    path: str,
    gate: str,
) -> dict[str, Any]:
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
        fail(gate, f"{path} must be an integer")
    return value


def _nonnegative_integer(value: Any, path: str, gate: str) -> int:
    result = _integer(value, path, gate)
    if result < 0:
        fail(gate, f"{path} must be nonnegative")
    return result


def _boolean(value: Any, path: str, gate: str) -> bool:
    if type(value) is not bool:
        fail(gate, f"{path} must be a boolean")
    return value


def _string(value: Any, path: str, gate: str) -> str:
    if type(value) is not str or not value:
        fail(gate, f"{path} must be a nonempty string")
    return value


def _sha256_token(value: Any, path: str, gate: str) -> str:
    if type(value) is not str or HEX_SHA256.fullmatch(value) is None:
        fail(gate, f"{path} must be 64 lowercase hexadecimal digits")
    return value


def reject_duplicate_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("strict_json", f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def reject_raw_float(token: str) -> None:
    fail("strict_json", f"raw JSON float token {token!r} is forbidden")


def reject_nonfinite(token: str) -> None:
    fail("strict_json", f"non-finite JSON token {token!r} is forbidden")


def assert_json_tree(value: Any, path: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is list:
        for index, item in enumerate(value):
            assert_json_tree(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                fail("strict_json", f"{path} has a non-string key")
            assert_json_tree(item, f"{path}.{key}")
        return
    fail("strict_json", f"{path} contains {type(value).__name__}")


def strict_loads(text: str) -> Any:
    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_float=reject_raw_float,
            parse_constant=reject_nonfinite,
        )
    except NoEntryReplayError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        fail("strict_json", str(error))
    assert_json_tree(value)
    return value


def strict_load(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        fail("strict_json", f"cannot read {path}: {error}")
    value = strict_loads(text)
    if type(value) is not dict:
        fail("strict_json", f"{path} must contain an object")
    return value


def canonical_bytes(value: Any) -> bytes:
    assert_json_tree(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def semantic_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def source_semantic_sha256(value: Any) -> str:
    """Alias spelling the source bridge's no-final-LF convention."""

    return semantic_sha256(value)


def pretty_json(value: Any) -> str:
    assert_json_tree(value)
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


def normalized_lf_sha256(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as error:
        fail("inventory", f"cannot read {path}: {error}")
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


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


def parse_dyadic(value: Any, path: str = "$dyadic") -> Fraction:
    item = _exact_keys(value, DYADIC_KEYS, path, "dyadic")
    numerator = _integer(item["numerator"], f"{path}.numerator", "dyadic")
    exponent = _integer(item["exponent"], f"{path}.exponent", "dyadic")
    if exponent < 0 or exponent > 1_000_000:
        fail("dyadic", f"{path}.exponent is outside the accepted range")
    if numerator == 0 and exponent != 0:
        fail("dyadic", f"{path} zero is not canonical")
    if numerator != 0 and exponent > 0 and numerator % 2 == 0:
        fail("dyadic", f"{path} is not reduced")
    return Fraction(numerator, 1 << exponent)


def dyadic_json(value: Fraction | int) -> dict[str, int]:
    fraction = Fraction(value)
    denominator = fraction.denominator
    if denominator & (denominator - 1):
        fail("dyadic", "attempted to encode a non-dyadic rational")
    exponent = denominator.bit_length() - 1
    numerator = fraction.numerator
    while exponent and numerator % 2 == 0:
        numerator //= 2
        exponent -= 1
    if numerator == 0:
        exponent = 0
    return {"numerator": numerator, "exponent": exponent}


def _arb_tuple(value: Fraction) -> tuple[int, int]:
    denominator = value.denominator
    if denominator & (denominator - 1):
        fail("arb_ingress", "Arb exact ingress requires a dyadic")
    return value.numerator, -(denominator.bit_length() - 1)


def exact_arb(value: Fraction | int) -> arb:
    return arb(_arb_tuple(Fraction(value)))


def interval_arb(lower: Fraction, upper: Fraction) -> arb:
    if lower > upper:
        fail("arb_ingress", "reversed interval")
    midpoint = (lower + upper) / 2
    radius = (upper - lower) / 2
    return arb(_arb_tuple(midpoint), _arb_tuple(radius))


def exact_arb_fraction(value: arb, path: str) -> Fraction:
    if not value.is_finite() or not value.is_exact():
        fail("arb_endpoint", f"{path} must be a finite exact Arb endpoint")
    try:
        raw_mantissa, raw_exponent = value.man_exp()
    except (ValueError, TypeError, OverflowError) as error:
        fail("arb_endpoint", f"{path} has no exact dyadic form: {error}")
    try:
        mantissa = int(raw_mantissa)
        exponent = int(raw_exponent)
    except (TypeError, ValueError, OverflowError):
        fail("arb_endpoint", f"{path} returned a malformed man-exp pair")
    if exponent >= 0:
        return Fraction(mantissa << exponent, 1)
    return Fraction(mantissa, 1 << (-exponent))


def exact_arb_bounds(value: arb, path: str) -> tuple[Fraction, Fraction]:
    if not value.is_finite():
        fail("arb_evaluation", f"{path} is not finite")
    lower = exact_arb_fraction(value.lower(), f"{path}.lower")
    upper = exact_arb_fraction(value.upper(), f"{path}.upper")
    if lower > upper:
        fail("arb_evaluation", f"{path} produced reversed bounds")
    return lower, upper


@contextmanager
def precision(bits: int) -> Iterator[None]:
    if type(bits) is not int or bits < 64 or bits > 16384:
        fail("arb_backend", "precision_bits must be in [64,16384]")
    previous = ctx.prec
    ctx.prec = bits
    try:
        yield
    finally:
        ctx.prec = previous


def backend_identity() -> dict[str, str]:
    python_flint = getattr(flint, "__version__", None)
    flint_version = getattr(flint, "__FLINT_VERSION__", None)
    if python_flint != PYTHON_FLINT_VERSION:
        fail(
            "arb_backend",
            f"python-flint {python_flint!r} != {PYTHON_FLINT_VERSION!r}",
        )
    if flint_version != FLINT_VERSION:
        fail(
            "arb_backend",
            f"FLINT {flint_version!r} != {FLINT_VERSION!r}",
        )
    return {
        "python_flint": python_flint,
        "flint": flint_version,
        "arithmetic": "arb outward-rounded balls",
    }


def parse_interval(
    value: Any,
    path: str,
    *,
    require_half_open: bool,
) -> tuple[Fraction, Fraction]:
    item = _exact_keys(value, INTERVAL_KEYS, path, "box_schema")
    lower = parse_dyadic(item["lower"], f"{path}.lower")
    upper = parse_dyadic(item["upper"], f"{path}.upper")
    lower_closed = _boolean(
        item["lower_closed"], f"{path}.lower_closed", "box_schema"
    )
    upper_closed = _boolean(
        item["upper_closed"], f"{path}.upper_closed", "box_schema"
    )
    if lower >= upper:
        fail("box_schema", f"{path} must have positive width")
    if require_half_open and (not lower_closed or upper_closed):
        fail("half_open_cover", f"{path} must be lower-closed upper-open")
    return lower, upper


def parse_box(
    value: Any,
    path: str,
    *,
    require_half_open: bool = True,
) -> dict[str, tuple[Fraction, Fraction]]:
    if type(value) is not dict:
        fail("box_schema", f"{path} must be an object")
    if set(value) == set(BOX_AXES):
        axis_objects = value
    else:
        item = _exact_keys(
            value, {"axes", "intervals"}, path, "box_schema"
        )
        if item["axes"] != list(BOX_AXES) or any(
            type(axis) is not str for axis in item["axes"]
        ):
            fail("box_schema", f"{path}.axes differs from the registry")
        intervals = item["intervals"]
        if type(intervals) is not list or len(intervals) != len(BOX_AXES):
            fail("box_schema", f"{path}.intervals must have length three")
        axis_objects = dict(zip(BOX_AXES, intervals))
    return {
        axis: parse_interval(
            axis_objects[axis],
            f"{path}.{axis}",
            require_half_open=require_half_open,
        )
        for axis in BOX_AXES
    }


def _dyadic_vector(
    value: Any,
    length: int,
    path: str,
) -> list[Fraction]:
    if type(value) is not list or len(value) != length:
        fail("physical_problem", f"{path} must have length {length}")
    return [
        parse_dyadic(item, f"{path}[{index}]")
        for index, item in enumerate(value)
    ]


def replay_source_problem_binding(
    physical_problem: Any | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the independent source gate and return its pinned physical problem."""

    if normalized_lf_sha256(SOURCE_BINDING_PATH) != (
        SOURCE_BINDING_REPLAYER_NORMALIZED_LF_SHA256
    ):
        fail(
            "source_binding_code",
            "source-binding replayer differs from the code-pinned version",
        )
    try:
        replay = source_binding.replay_binding_paths()
    except Exception as error:
        fail("source_binding_gate", str(error))
    if type(replay) is not dict:
        fail("source_binding_gate", "source gate returned a non-object")
    if replay.get("physical_problem_semantic_sha256") != (
        PHYSICAL_PROBLEM_SEMANTIC_SHA256
    ):
        fail("problem_commitment", "source gate did not replay pinned problem")

    fixture = strict_load(SOURCE_FIXTURE_PATH)
    if "physical_problem" not in fixture:
        fail("physical_problem", "source fixture lacks physical_problem")
    bound_problem = fixture["physical_problem"]
    if type(bound_problem) is not dict:
        fail("physical_problem", "physical_problem must be an object")
    if (
        source_semantic_sha256(bound_problem)
        != PHYSICAL_PROBLEM_SEMANTIC_SHA256
    ):
        fail("problem_commitment", "bound physical problem hash differs")
    if physical_problem is not None:
        if type(physical_problem) is not dict:
            fail("physical_problem", "provided physical problem is not an object")
        if (
            source_semantic_sha256(physical_problem)
            != PHYSICAL_PROBLEM_SEMANTIC_SHA256
        ):
            fail("problem_commitment", "provided physical problem is not pinned")
        if not type_strict_equal(physical_problem, bound_problem):
            fail("problem_commitment", "provided physical problem differs")
    validate_physical_problem(bound_problem)
    return bound_problem, replay


def validate_physical_problem(problem: Any) -> dict[str, Any]:
    expected_top = {
        "schema_version",
        "equation_family_version",
        "source_commitment",
        "dimensions",
        "f1_convention",
        "target_torus",
        "worldsheet",
        "observation",
        "hysteresis",
        "kinematics",
        "arb_9d_jet_ingress",
        "scope",
    }
    root = _exact_keys(
        problem, expected_top, "$.physical_problem", "physical_problem"
    )
    if root["schema_version"] != PROBLEM_SCHEMA:
        fail("physical_problem", "unsupported problem schema")

    dimensions = _exact_keys(
        root["dimensions"],
        {
            "target",
            "transverse",
            "target_axis_order",
            "transverse_axis_order",
            "winding_axis",
        },
        "$.physical_problem.dimensions",
        "physical_problem",
    )
    if (
        dimensions["target"] != TARGET_DIMENSION
        or dimensions["transverse"] != TRANSVERSE_DIMENSION
        or dimensions["winding_axis"] != WINDING_AXIS
        or dimensions["target_axis_order"] != list(range(TARGET_DIMENSION))
        or dimensions["transverse_axis_order"]
        != list(range(TRANSVERSE_DIMENSION))
    ):
        fail("physical_problem", "dimension or target-axis registry drifted")

    torus = root["target_torus"]
    if type(torus) is not dict:
        fail("physical_problem", "target_torus must be an object")
    periods = _dyadic_vector(
        torus.get("periods_L_A"),
        TARGET_DIMENSION,
        "$.physical_problem.target_torus.periods_L_A",
    )
    if any(period <= 0 for period in periods):
        fail("physical_problem", "all target periods must be positive")
    if torus.get("metric_convention") != "G=identity_9":
        fail("physical_problem", "metric convention is not pinned")
    metric = torus.get("G")
    if type(metric) is not list or len(metric) != TARGET_DIMENSION:
        fail("physical_problem", "metric has wrong shape")
    for row in range(TARGET_DIMENSION):
        parsed = _dyadic_vector(
            metric[row],
            TARGET_DIMENSION,
            f"$.physical_problem.target_torus.G[{row}]",
        )
        expected = [
            Fraction(1 if row == column else 0)
            for column in range(TARGET_DIMENSION)
        ]
        if parsed != expected:
            fail("physical_problem", "metric is not exactly identity")

    worldsheet = root["worldsheet"]
    if type(worldsheet) is not dict:
        fail("physical_problem", "worldsheet must be an object")
    if worldsheet.get("winding_orientations") != [1, -1]:
        fail("physical_problem", "winding orientations drifted")
    domains = worldsheet.get("sigma_domains")
    if type(domains) is not list or len(domains) != 2:
        fail("physical_problem", "two sigma domains are required")
    sigma_bounds = []
    for index, domain in enumerate(domains):
        item = _exact_keys(
            domain,
            {"lower", "upper", "closure"},
            f"$.physical_problem.worldsheet.sigma_domains[{index}]",
            "physical_problem",
        )
        lower = parse_dyadic(
            item["lower"],
            f"$.physical_problem.worldsheet.sigma_domains[{index}].lower",
        )
        upper = parse_dyadic(
            item["upper"],
            f"$.physical_problem.worldsheet.sigma_domains[{index}].upper",
        )
        if lower >= upper or item["closure"] != "lower_closed_upper_open":
            fail("physical_problem", "sigma domain is not positive half-open")
        sigma_bounds.append((lower, upper))
    if sigma_bounds[0] != sigma_bounds[1]:
        fail("physical_problem", "sigma domains differ")

    observation = _exact_keys(
        root["observation"],
        {
            "t0",
            "t1",
            "window_closure",
            "initial_history",
            "continuation_convention",
        },
        "$.physical_problem.observation",
        "physical_problem",
    )
    t0 = parse_dyadic(
        observation["t0"], "$.physical_problem.observation.t0"
    )
    t1 = parse_dyadic(
        observation["t1"], "$.physical_problem.observation.t1"
    )
    if (
        t0 >= t1
        or observation["window_closure"] != "lower_closed_upper_open"
        or observation["initial_history"] != "armed"
    ):
        fail("physical_problem", "observation registry is not armed half-open")

    hysteresis = root["hysteresis"]
    if type(hysteresis) is not dict:
        fail("physical_problem", "hysteresis must be an object")
    r_in = parse_dyadic(
        hysteresis.get("r_in"), "$.physical_problem.hysteresis.r_in"
    )
    r_out = parse_dyadic(
        hysteresis.get("r_out"), "$.physical_problem.hysteresis.r_out"
    )
    if not (Fraction(0) < r_in < r_out):
        fail("physical_problem", "hysteresis radii are not ordered")

    kinematics = root["kinematics"]
    if type(kinematics) is not dict:
        fail("physical_problem", "kinematics must be an object")
    centres = kinematics.get("centres_Q1_Q2")
    if type(centres) is not dict or set(centres) != {"Q1", "Q2"}:
        fail("physical_problem", "centres_Q1_Q2 is malformed")
    _dyadic_vector(
        centres["Q1"],
        TRANSVERSE_DIMENSION,
        "$.physical_problem.kinematics.centres_Q1_Q2.Q1",
    )
    _dyadic_vector(
        centres["Q2"],
        TRANSVERSE_DIMENSION,
        "$.physical_problem.kinematics.centres_Q1_Q2.Q2",
    )
    strings = kinematics.get("strings")
    if type(strings) is not list or len(strings) != 2:
        fail("physical_problem", "exactly two strings are required")
    for index, string in enumerate(strings):
        if type(string) is not dict:
            fail("physical_problem", f"string {index} must be an object")
        if (
            string.get("string_id") != index + 1
            or string.get("orientation") != (1 if index == 0 else -1)
            or string.get("centre_reference") != f"Q{index + 1}"
        ):
            fail("physical_problem", f"string {index} registry drifted")
        _dyadic_vector(
            string.get("transverse_velocity"),
            TRANSVERSE_DIMENSION,
            f"$.physical_problem.kinematics.strings[{index}]."
            "transverse_velocity",
        )
        modes = string.get("modes")
        if type(modes) is not list or len(modes) != 1:
            fail("physical_problem", "the registered physical cell is K=1")
        mode = modes[0]
        if type(mode) is not dict or mode.get("mode_number") != 1:
            fail("physical_problem", "the registered mode number is not one")
        if parse_dyadic(
            mode.get("wave_number"),
            f"$.physical_problem.kinematics.strings[{index}]."
            "modes[0].wave_number",
        ) <= 0:
            fail("physical_problem", "wave number must be positive")
        for key in ("initial_x", "initial_y", "initial_p", "initial_q"):
            _dyadic_vector(
                mode.get(key),
                TRANSVERSE_DIMENSION,
                f"$.physical_problem.kinematics.strings[{index}]."
                f"modes[0].{key}",
            )
    return root


def physical_root_box(problem: Mapping[str, Any]) -> dict[str, Any]:
    domains = problem["worldsheet"]["sigma_domains"]
    observation = problem["observation"]

    def interval(lower: Any, upper: Any) -> dict[str, Any]:
        return {
            "lower": copy.deepcopy(lower),
            "upper": copy.deepcopy(upper),
            "lower_closed": True,
            "upper_closed": False,
        }

    return {
        "sigma1": interval(domains[0]["lower"], domains[0]["upper"]),
        "sigma2": interval(domains[1]["lower"], domains[1]["upper"]),
        "t": interval(observation["t0"], observation["t1"]),
    }


def _mode_value(
    mode: Mapping[str, Any],
    component: int,
    sigma: arb,
    time: arb,
    path: str,
) -> arb:
    wave_number = exact_arb(
        parse_dyadic(mode["wave_number"], f"{path}.wave_number")
    )
    if wave_number.contains(arb(0)):
        fail("physical_kinematics", f"{path}.wave_number contains zero")
    x0 = exact_arb(
        parse_dyadic(mode["initial_x"][component], f"{path}.initial_x")
    )
    y0 = exact_arb(
        parse_dyadic(mode["initial_y"][component], f"{path}.initial_y")
    )
    p0 = exact_arb(
        parse_dyadic(mode["initial_p"][component], f"{path}.initial_p")
    )
    q0 = exact_arb(
        parse_dyadic(mode["initial_q"][component], f"{path}.initial_q")
    )
    kt = wave_number * time
    ks = wave_number * sigma
    cos_time = kt.cos()
    sin_time = kt.sin()
    cos_sigma = ks.cos()
    sin_sigma = ks.sin()
    x_time = x0 * cos_time + (p0 / wave_number) * sin_time
    y_time = y0 * cos_time + (q0 / wave_number) * sin_time
    return x_time * cos_sigma + y_time * sin_sigma


def evaluate_d_enclosures(
    problem: Mapping[str, Any],
    box: Any,
    precision_bits: int,
) -> list[tuple[Fraction, Fraction]]:
    """Independently enclose all nine components of physical d on one box."""

    validate_physical_problem(problem)
    parsed_box = parse_box(box, "$.leaf.box")
    backend_identity()
    with precision(precision_bits):
        sigma1 = interval_arb(*parsed_box["sigma1"])
        sigma2 = interval_arb(*parsed_box["sigma2"])
        time = interval_arb(*parsed_box["t"])
        kinematics = problem["kinematics"]
        centres = kinematics["centres_Q1_Q2"]
        strings = kinematics["strings"]
        q1 = [
            exact_arb(value)
            for value in _dyadic_vector(
                centres["Q1"], TRANSVERSE_DIMENSION, "$.Q1"
            )
        ]
        q2 = [
            exact_arb(value)
            for value in _dyadic_vector(
                centres["Q2"], TRANSVERSE_DIMENSION, "$.Q2"
            )
        ]
        v1 = [
            exact_arb(value)
            for value in _dyadic_vector(
                strings[0]["transverse_velocity"],
                TRANSVERSE_DIMENSION,
                "$.V1",
            )
        ]
        v2 = [
            exact_arb(value)
            for value in _dyadic_vector(
                strings[1]["transverse_velocity"],
                TRANSVERSE_DIMENSION,
                "$.V2",
            )
        ]
        mode1 = strings[0]["modes"][0]
        mode2 = strings[1]["modes"][0]
        values: list[arb] = []
        for component in range(TRANSVERSE_DIMENSION):
            y1 = _mode_value(
                mode1, component, sigma1, time, "$.string1.mode1"
            )
            y2 = _mode_value(
                mode2, component, sigma2, time, "$.string2.mode1"
            )
            value = (
                q1[component]
                - q2[component]
                + (v1[component] - v2[component]) * time
                + y1
                - y2
            )
            values.append(value)
        orientation1 = strings[0]["orientation"]
        orientation2 = strings[1]["orientation"]
        values.append(orientation1 * sigma1 - orientation2 * sigma2)
        if len(values) != TARGET_DIMENSION:
            fail("physical_kinematics", "d has the wrong target dimension")
        return [
            exact_arb_bounds(value, f"$.d[{axis}]")
            for axis, value in enumerate(values)
        ]


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def derive_empty_image_witness(
    lower: Fraction,
    upper: Fraction,
    period: Fraction,
    radius: Fraction,
    axis: int,
) -> dict[str, Any] | None:
    """Derive the exact strict coordinate-image exclusion witness."""

    if lower > upper:
        fail("image_range", "d enclosure is reversed")
    if period <= 0 or radius <= 0:
        fail("image_range", "period and radius must be positive")
    nmin = ceil_fraction((lower - radius) / period)
    nmax = floor_fraction((upper + radius) / period)
    if nmin <= nmax:
        return None
    if nmin != nmax + 1:
        fail("image_range", "empty integer interval is not adjacent")
    above_previous = lower - radius - nmax * period
    below_next = nmin * period - radius - upper
    minimum = min(above_previous, below_next)
    if (
        above_previous <= 0
        or below_next <= 0
        or minimum <= 0
    ):
        fail("strict_image_gap", "coordinate exclusion touches a boundary")
    return {
        "witness_type": "empty_coordinate_image_range",
        "axis": axis,
        "d_enclosure": {
            "lo": dyadic_json(lower),
            "hi": dyadic_json(upper),
        },
        "period": dyadic_json(period),
        "radius": dyadic_json(radius),
        "nmin": nmin,
        "nmax": nmax,
        "evaluated_on": "closed_hull_of_owned_half_open_box",
        "margins": {
            "above_previous_image": dyadic_json(above_previous),
            "below_next_image": dyadic_json(below_next),
            "minimum": dyadic_json(minimum),
        },
    }


def derive_leaf_witness(
    problem: Mapping[str, Any],
    box: Any,
    precision_bits: int,
) -> tuple[dict[str, Any], list[tuple[Fraction, Fraction]]]:
    enclosures = evaluate_d_enclosures(problem, box, precision_bits)
    periods = _dyadic_vector(
        problem["target_torus"]["periods_L_A"],
        TARGET_DIMENSION,
        "$.periods",
    )
    radius = parse_dyadic(problem["hysteresis"]["r_out"], "$.r_out")
    for axis, ((lower, upper), period) in enumerate(
        zip(enclosures, periods)
    ):
        witness = derive_empty_image_witness(
            lower, upper, period, radius, axis
        )
        if witness is not None:
            return witness, enclosures
    fail(
        "unresolved_leaf",
        "leaf has no strict coordinate-image exclusion at registered precision",
    )


def _same_fraction_box(
    left: Mapping[str, tuple[Fraction, Fraction]],
    right: Mapping[str, tuple[Fraction, Fraction]],
) -> bool:
    return all(left[axis] == right[axis] for axis in BOX_AXES)


def _split_expected_children(
    parent: Mapping[str, tuple[Fraction, Fraction]],
    axis: str,
    point: Fraction,
) -> tuple[dict[str, tuple[Fraction, Fraction]], dict[str, tuple[Fraction, Fraction]]]:
    if axis not in BOX_AXES:
        fail("tree_cover", f"unknown split axis {axis!r}")
    lower, upper = parent[axis]
    if point != (lower + upper) / 2:
        fail("split_rule", "split point is not the exact midpoint")
    left = dict(parent)
    right = dict(parent)
    left[axis] = (lower, point)
    right[axis] = (point, upper)
    return left, right


def _node_payload_without_hash(node: Mapping[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(dict(node))
    payload.pop("node_semantic_sha256", None)
    return payload


def _certificate_payload_without_hash(
    certificate: Mapping[str, Any],
) -> dict[str, Any]:
    payload = copy.deepcopy(dict(certificate))
    payload.pop("certificate_semantic_sha256", None)
    return payload


def validate_solver_registry(
    value: Any,
    stored_digest: Any,
) -> dict[str, Any]:
    registry = _exact_keys(
        value,
        {
            "schema_version",
            "solver_id",
            "physical_problem_semantic_sha256",
            "arb_backend",
            "domain_axes",
            "domain_topology_scope",
            "split_rule",
            "target_axis_tie_order",
            "leaf_rule",
            "budgets",
        },
        "$.solver_registry",
        "solver_registry",
    )
    if registry["schema_version"] != SOLVER_REGISTRY_SCHEMA:
        fail("solver_registry", "unsupported solver registry schema")
    if registry["solver_id"] != (
        "index2-finite-window-empty-coordinate-cover-v1"
    ):
        fail("solver_registry", "solver_id differs from the frozen solver")
    if registry["physical_problem_semantic_sha256"] != (
        PHYSICAL_PROBLEM_SEMANTIC_SHA256
    ):
        fail("solver_registry", "solver registry binds a different problem")
    if registry["domain_axes"] != list(BOX_AXES):
        fail("solver_registry", "domain axis order differs")
    if registry["domain_topology_scope"] != (
        "half_open_rectangular_fundamental_domain_cover_only;"
        "no_exact_seam_equivalence_claim"
    ):
        fail("solver_registry", "domain topology scope differs")
    if registry["target_axis_tie_order"] != list(range(TARGET_DIMENSION)):
        fail("solver_registry", "target-axis tie order differs")

    backend = _exact_keys(
        registry["arb_backend"],
        {
            "python_flint_version",
            "flint_version",
            "precision_bits",
            "endpoint_encoding",
        },
        "$.solver_registry.arb_backend",
        "solver_registry",
    )
    if (
        backend["python_flint_version"] != PYTHON_FLINT_VERSION
        or backend["flint_version"] != FLINT_VERSION
        or backend["endpoint_encoding"]
        != "exact reduced dyadics from Arb lower/upper endpoints"
    ):
        fail("solver_registry", "Arb backend registry differs")
    precision_bits = _integer(
        backend["precision_bits"],
        "$.solver_registry.arb_backend.precision_bits",
        "solver_registry",
    )
    if precision_bits < 64 or precision_bits > 16384:
        fail("solver_registry", "registered precision is outside limits")

    split_rule = _exact_keys(
        registry["split_rule"],
        {
            "kind",
            "axis_tie_order",
            "ownership",
            "proof_evaluation",
        },
        "$.solver_registry.split_rule",
        "solver_registry",
    )
    if not type_strict_equal(
        split_rule,
        {
            "kind": "normalized_widest_axis_midpoint",
            "axis_tie_order": list(BOX_AXES),
            "ownership": "left_upper_open_right_lower_closed",
            "proof_evaluation": "closed_hull_of_each_owned_box",
        },
    ):
        fail("solver_registry", "split rule differs")

    leaf_rule = _exact_keys(
        registry["leaf_rule"],
        {
            "kind",
            "formula",
            "axis_selection",
            "strict_contact_policy",
        },
        "$.solver_registry.leaf_rule",
        "solver_registry",
    )
    if not type_strict_equal(
        leaf_rule,
        {
            "kind": "empty_coordinate_image_range",
            "formula": (
                "nmin=ceil((infD-r_out)/L_A);"
                "nmax=floor((supD+r_out)/L_A);exclude iff nmin>nmax"
            ),
            "axis_selection": "first_excluding_target_axis_in_tie_order",
            "strict_contact_policy": "touching_is_not_excluded",
        },
    ):
        fail("solver_registry", "leaf rule differs")

    budgets = _exact_keys(
        registry["budgets"],
        {"max_nodes", "max_depth", "budget_stop"},
        "$.solver_registry.budgets",
        "solver_registry",
    )
    if (
        _integer(
            budgets["max_nodes"],
            "$.solver_registry.budgets.max_nodes",
            "solver_registry",
        )
        != 4095
        or _integer(
            budgets["max_depth"],
            "$.solver_registry.budgets.max_depth",
            "solver_registry",
        )
        != 48
        or budgets["budget_stop"] != "typed_unresolved_leaf"
    ):
        fail("solver_registry", "solver budgets differ")

    digest = semantic_sha256(registry)
    if (
        _sha256_token(
            stored_digest,
            "$.solver_registry_semantic_sha256",
            "solver_registry_hash",
        )
        != digest
    ):
        fail("solver_registry_hash", "stored solver registry hash differs")
    if digest != PINNED_SOLVER_REGISTRY_SHA256:
        fail("solver_registry_hash", "solver registry is not code-pinned")
    backend_identity()
    return registry


def expected_registered_domain(
    problem: Mapping[str, Any],
) -> dict[str, Any]:
    root = physical_root_box(problem)
    return {
        "axes": list(BOX_AXES),
        "intervals": [copy.deepcopy(root[axis]) for axis in BOX_AXES],
    }


def _expected_split_axis(
    box: Mapping[str, tuple[Fraction, Fraction]],
    root_box: Mapping[str, tuple[Fraction, Fraction]],
) -> str:
    normalized_widths = {
        axis: (box[axis][1] - box[axis][0])
        / (root_box[axis][1] - root_box[axis][0])
        for axis in BOX_AXES
    }
    widest = max(normalized_widths.values())
    return next(
        axis for axis in BOX_AXES if normalized_widths[axis] == widest
    )


def replay_tree(
    tree: Any,
    domain: Mapping[str, Any],
    problem: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    tree_obj = _exact_keys(
        tree,
        {"storage", "root_node_id", "nodes"},
        "$.tree",
        "tree_schema",
    )
    if tree_obj["storage"] != "flat_preorder_with_bottom_up_child_hashes":
        fail("tree_schema", "unsupported tree storage")
    if tree_obj["root_node_id"] != "r":
        fail("tree_schema", "root node id must be 'r'")
    nodes = tree_obj["nodes"]
    if type(nodes) is not list or not nodes:
        fail("tree_schema", "tree.nodes must be a nonempty list")
    max_nodes = registry["budgets"]["max_nodes"]
    if len(nodes) > max_nodes:
        fail("tree_budget", "tree exceeds max_nodes")

    node_keys = {
        "node_id",
        "parent_id",
        "depth",
        "box",
        "node_kind",
        "payload",
        "node_semantic_sha256",
    }
    by_id: dict[str, dict[str, Any]] = {}
    serialized_order: list[str] = []
    for index, raw_node in enumerate(nodes):
        node = _exact_keys(
            raw_node,
            node_keys,
            f"$.tree.nodes[{index}]",
            "node_schema",
        )
        node_id = _string(
            node["node_id"],
            f"$.tree.nodes[{index}].node_id",
            "node_schema",
        )
        if re.fullmatch(r"r[LR]*", node_id) is None:
            fail("node_schema", f"node id {node_id!r} is noncanonical")
        if node_id in by_id:
            fail("tree_cover", f"duplicate node id {node_id!r}")
        _sha256_token(
            node["node_semantic_sha256"],
            f"$.tree.nodes[{index}].node_semantic_sha256",
            "node_hash",
        )
        by_id[node_id] = node
        serialized_order.append(node_id)

    root_box = parse_box(domain, "$.domain")
    visited: set[str] = set()
    preorder: list[str] = []
    leaf_count = 0
    split_count = 0
    maximum_depth = 0
    axis_counts = {str(axis): 0 for axis in range(TARGET_DIMENSION)}
    minimum_margin: Fraction | None = None

    def visit(
        node_id: str,
        expected_parent: str | None,
        expected_depth: int,
        expected_box: Mapping[str, tuple[Fraction, Fraction]],
    ) -> str:
        nonlocal leaf_count, split_count, maximum_depth, minimum_margin
        if node_id not in by_id:
            fail("tree_cover", f"missing child node {node_id!r}")
        if node_id in visited:
            fail("tree_cover", f"cycle or shared child at {node_id!r}")
        visited.add(node_id)
        preorder.append(node_id)
        node = by_id[node_id]
        if node["parent_id"] != expected_parent:
            fail("tree_cover", f"{node_id} parent differs")
        if (
            _nonnegative_integer(
                node["depth"], f"$.tree.{node_id}.depth", "tree_cover"
            )
            != expected_depth
        ):
            fail("tree_cover", f"{node_id} depth differs")
        if expected_depth > registry["budgets"]["max_depth"]:
            fail("tree_budget", f"{node_id} exceeds max_depth")
        maximum_depth = max(maximum_depth, expected_depth)
        parsed_box = parse_box(node["box"], f"$.tree.{node_id}.box")
        if not _same_fraction_box(parsed_box, expected_box):
            fail("tree_cover", f"{node_id} box differs from its partition")

        kind = node["node_kind"]
        if kind == "split":
            split_count += 1
            payload = _exact_keys(
                node["payload"],
                {
                    "split_type",
                    "split_axis",
                    "split_point",
                    "left_child_id",
                    "right_child_id",
                    "left_child_semantic_sha256",
                    "right_child_semantic_sha256",
                },
                f"$.tree.{node_id}.payload",
                "split_schema",
            )
            if payload["split_type"] != "normalized_widest_axis_midpoint":
                fail("split_rule", f"{node_id} split type differs")
            expected_axis = _expected_split_axis(parsed_box, root_box)
            if payload["split_axis"] != expected_axis:
                fail("split_rule", f"{node_id} split axis differs")
            split_point = parse_dyadic(
                payload["split_point"],
                f"$.tree.{node_id}.payload.split_point",
            )
            left_box, right_box = _split_expected_children(
                parsed_box, expected_axis, split_point
            )
            left_id = _string(
                payload["left_child_id"],
                f"$.tree.{node_id}.payload.left_child_id",
                "split_schema",
            )
            right_id = _string(
                payload["right_child_id"],
                f"$.tree.{node_id}.payload.right_child_id",
                "split_schema",
            )
            if left_id != f"{node_id}L" or right_id != f"{node_id}R":
                fail("tree_cover", f"{node_id} child ids are noncanonical")
            left_hash = visit(
                left_id, node_id, expected_depth + 1, left_box
            )
            right_hash = visit(
                right_id, node_id, expected_depth + 1, right_box
            )
            if (
                _sha256_token(
                    payload["left_child_semantic_sha256"],
                    f"$.tree.{node_id}.payload.left_child_semantic_sha256",
                    "node_hash",
                )
                != left_hash
                or _sha256_token(
                    payload["right_child_semantic_sha256"],
                    f"$.tree.{node_id}.payload.right_child_semantic_sha256",
                    "node_hash",
                )
                != right_hash
            ):
                fail("bottom_up_hash", f"{node_id} child hash differs")
        elif kind == "leaf":
            leaf_count += 1
            payload = _exact_keys(
                node["payload"],
                {"witness"},
                f"$.tree.{node_id}.payload",
                "leaf_schema",
            )
            expected_witness, _ = derive_leaf_witness(
                problem,
                node["box"],
                registry["arb_backend"]["precision_bits"],
            )
            if not type_strict_equal(
                payload["witness"], expected_witness
            ):
                fail(
                    "leaf_witness",
                    f"{node_id} differs from independent Arb/image replay",
                )
            axis = expected_witness["axis"]
            axis_counts[str(axis)] += 1
            margin = parse_dyadic(
                expected_witness["margins"]["minimum"],
                f"$.tree.{node_id}.payload.witness.margins.minimum",
            )
            if margin <= 0:
                fail("strict_image_gap", f"{node_id} has nonpositive margin")
            minimum_margin = (
                margin
                if minimum_margin is None
                else min(minimum_margin, margin)
            )
        else:
            fail(
                "unresolved_leaf",
                f"{node_id} has forbidden node kind {kind!r}",
            )

        computed_hash = semantic_sha256(_node_payload_without_hash(node))
        if computed_hash != node["node_semantic_sha256"]:
            fail("node_hash", f"{node_id} semantic hash differs")
        return computed_hash

    root_hash = visit("r", None, 0, root_box)
    if len(visited) != len(nodes):
        fail("tree_cover", "tree contains unreachable nodes")
    if preorder != serialized_order:
        fail("tree_preorder", "nodes are not serialized in exact preorder")
    if leaf_count != split_count + 1:
        fail("tree_cover", "tree is not a full finite binary tree")
    if minimum_margin is None:
        fail("tree_cover", "tree has no excluded leaves")
    return {
        "root_node_semantic_sha256": root_hash,
        "node_count": len(nodes),
        "split_nodes": split_count,
        "leaf_count": leaf_count,
        "excluded_leaves": leaf_count,
        "unresolved_leaves": 0,
        "maximum_depth": maximum_depth,
        "leaf_axis_counts": axis_counts,
        "minimum_strict_coordinate_margin": dyadic_json(minimum_margin),
    }


def expected_summary(tree_replay: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "node_count": tree_replay["node_count"],
        "split_nodes": tree_replay["split_nodes"],
        "leaf_count": tree_replay["leaf_count"],
        "excluded_leaves": tree_replay["excluded_leaves"],
        "unresolved_leaves": tree_replay["unresolved_leaves"],
        "maximum_depth": tree_replay["maximum_depth"],
        "root_node_semantic_sha256": tree_replay[
            "root_node_semantic_sha256"
        ],
        "partition": "complete_gap_free_half_open_binary_tree",
        "proof_evaluation": "closed_hull_recomputed_at_every_leaf",
    }


def expected_outcome(domain: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": SUCCESS_OUTCOME,
        "scope": "registered_finite_half_open_window_only",
        "window": copy.deepcopy(dict(domain)),
        "all_leaves_excluded": True,
        "unresolved_leaves": 0,
        "history_at_right_boundary": "armed",
        "all_time_no_entry_claimed": False,
        "exact_seam_equivalence_claimed": False,
    }


def _inventory() -> list[dict[str, str]]:
    return [
        {
            "path": relative,
            "normalized_lf_sha256": normalized_lf_sha256(
                REPOSITORY_ROOT / relative
            ),
        }
        for relative in INVENTORY_PATHS
    ]


def build_report(replay: Mapping[str, Any]) -> dict[str, Any]:
    report = {
        "schema_version": REPORT_SCHEMA,
        "status": "passed",
        "failed_gates": [],
        "checks": {
            "source_and_physical_problem_binding_replayed": True,
            "strict_float_free_certificate_json": True,
            "problem_and_solver_registry_code_pinned": True,
            "half_open_root_and_tree_cover_replayed": True,
            "closed_arb_hulls_recomputed_independently": True,
            "all_9d_d_enclosures_recomputed_from_exact_dyadics": True,
            "least_axis_strict_empty_image_ranges_replayed": True,
            "bottom_up_node_hashes_replayed": True,
            "no_unresolved_leaves": True,
            "finite_window_right_censored_no_entry_only": True,
        },
        "commitments": copy.deepcopy(dict(replay)),
        "normalized_lf_inventory": _inventory(),
        "scope": {
            "claim": (
                "independent replay of finite-window physical no-entry for "
                "the pinned valid source index 2"
            ),
            "does_not_claim": [
                "an exact binary64 seam quotient",
                "all-time no-entry",
                "unconditioned source population pushforward",
                "3+1 selection",
            ],
        },
    }
    report["report_semantic_sha256"] = semantic_sha256(report)
    return report


def verify_report(report: Any, replay: Mapping[str, Any]) -> str:
    expected = build_report(replay)
    obj = _exact_keys(report, set(expected), "$.report", "report_schema")
    if obj["schema_version"] != REPORT_SCHEMA:
        fail("report_schema", "unsupported report schema")
    stored_hash = _sha256_token(
        obj["report_semantic_sha256"],
        "$.report.report_semantic_sha256",
        "report_hash",
    )
    payload = copy.deepcopy(obj)
    del payload["report_semantic_sha256"]
    if stored_hash != semantic_sha256(payload):
        fail("report_hash", "report semantic hash does not replay")
    if not type_strict_equal(obj, expected):
        fail("report_replay", "stored report differs from fresh replay")
    return stored_hash


def replay_certificate_objects(
    certificate: Any,
    *,
    physical_problem: Any | None = None,
) -> dict[str, Any]:
    """Independently replay the complete finite-window certificate."""

    certificate_obj = _exact_keys(
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
        "$.certificate",
        "certificate_schema",
    )
    if certificate_obj["schema_version"] != CERTIFICATE_SCHEMA:
        fail("certificate_schema", "unsupported certificate schema")
    if certificate_obj["certificate_id"] != (
        "index2-window0-empty-coordinate-cover-v1"
    ):
        fail("certificate_schema", "certificate id differs")
    if certificate_obj["physical_problem_semantic_sha256"] != (
        PHYSICAL_PROBLEM_SEMANTIC_SHA256
    ):
        fail("problem_commitment", "certificate binds a different problem")

    problem, source_replay = replay_source_problem_binding(physical_problem)
    registry = validate_solver_registry(
        certificate_obj["solver_registry"],
        certificate_obj["solver_registry_semantic_sha256"],
    )

    domain = certificate_obj["domain"]
    parse_box(domain, "$.domain")
    expected_domain = expected_registered_domain(problem)
    if not type_strict_equal(domain, expected_domain):
        fail("domain_binding", "certificate domain differs from the problem")

    tree_replay = replay_tree(
        certificate_obj["tree"], domain, problem, registry
    )
    summary = expected_summary(tree_replay)
    if not type_strict_equal(certificate_obj["summary"], summary):
        fail("summary", "certificate summary differs from replayed tree")
    outcome = expected_outcome(domain)
    if not type_strict_equal(certificate_obj["outcome"], outcome):
        fail("outcome", "certificate outcome differs from proved outcome")

    certificate_hash = _sha256_token(
        certificate_obj["certificate_semantic_sha256"],
        "$.certificate.certificate_semantic_sha256",
        "certificate_hash",
    )
    if certificate_hash != semantic_sha256(
        _certificate_payload_without_hash(certificate_obj)
    ):
        fail("certificate_hash", "certificate semantic hash differs")

    return {
        "source_registry_canonical_sha256": source_replay[
            "registry_canonical_sha256"
        ],
        "source_draw_sha256": source_replay["source_draw_sha256"],
        "source_state_sha256": source_binding.PINNED_STATE_SHA256[2],
        "physical_problem_semantic_sha256": (
            PHYSICAL_PROBLEM_SEMANTIC_SHA256
        ),
        "solver_registry_semantic_sha256": (
            PINNED_SOLVER_REGISTRY_SHA256
        ),
        "certificate_semantic_sha256": certificate_hash,
        "root_node_semantic_sha256": tree_replay[
            "root_node_semantic_sha256"
        ],
        "node_count": tree_replay["node_count"],
        "split_nodes": tree_replay["split_nodes"],
        "excluded_leaves": tree_replay["excluded_leaves"],
        "unresolved_leaves": 0,
        "maximum_depth": tree_replay["maximum_depth"],
        "leaf_axis_counts": tree_replay["leaf_axis_counts"],
        "minimum_strict_coordinate_margin": tree_replay[
            "minimum_strict_coordinate_margin"
        ],
        "arb_backend": {
            "python_flint": PYTHON_FLINT_VERSION,
            "flint": FLINT_VERSION,
            "precision_bits": registry["arb_backend"]["precision_bits"],
            "arithmetic": "arb outward-rounded balls",
        },
        "domain_topology": (
            "complete gap-free half-open rectangular cover"
        ),
        "proof_evaluation": "closed Arb hull on every owned leaf box",
        "outcome": SUCCESS_OUTCOME,
        "history_at_right_boundary": "armed",
        "all_time_no_entry_claimed": False,
        "exact_seam_equivalence_claimed": False,
    }


def replay_certificate_paths(
    certificate_path: Path = CERTIFICATE_PATH,
) -> dict[str, Any]:
    return replay_certificate_objects(strict_load(certificate_path))


def run(write: bool) -> dict[str, Any]:
    replay = replay_certificate_paths()
    report = build_report(replay)
    if write:
        REPORT_PATH.write_text(
            pretty_json(report), encoding="utf-8", newline="\n"
        )
    else:
        verify_report(strict_load(REPORT_PATH), replay)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Independently replay the physical no-entry certificate"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    print(pretty_json(run(write=arguments.write)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
