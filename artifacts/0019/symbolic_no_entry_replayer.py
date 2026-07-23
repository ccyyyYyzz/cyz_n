#!/usr/bin/env python3
"""Independent replay of the symbolic-pi transverse no-entry certificate.

The only project module imported here is ``symbolic_pi_lift_replayer``.
That module independently rebuilds the canonical lift from
``source_binding_replayer``.  This file does not import the lift generator,
the symbolic jet implementation, the no-entry solver, or any physical
solver.  It implements its own strict certificate parser, q*pi^e parser,
python-flint Arb transverse evaluator, tree/partition replay, budget
semantics, and report.
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
from typing import Any, Callable, Iterator, Mapping, Sequence

import flint
from flint import arb, ctx

import symbolic_pi_lift_replayer as lift_replay


CERTIFICATE_SCHEMA = (
    "cyz-brief-0019-symbolic-transverse-no-entry-certificate-v1"
)
REPORT_SCHEMA = (
    "cyz-brief-0019-symbolic-transverse-no-entry-replayer-report-v1"
)
SOLVER_REGISTRY_SCHEMA = (
    "cyz-brief-0019-symbolic-transverse-no-entry-solver-registry-v1"
)
SUCCESS_OUTCOME = "right_censored_no_entry"

PYTHON_FLINT_VERSION = "0.9.0"
FLINT_VERSION = "3.6.0"
PRECISION_BITS = 192
EXPECTED_NODE_COUNT = 259
EXPECTED_SPLIT_COUNT = 129
EXPECTED_LEAF_COUNT = 130
EXPECTED_MAXIMUM_DEPTH = 9
EXPECTED_AXIS_COUNTS = [14, 66, 12, 10, 4, 0, 0, 24]

CLOSED_STRING_PROBLEM_SHA256 = (
    "3bb6599f211c26d98ecba2077051ad9d0339daf96d580a6399cc5a1ba7f030e0"
)
LIFT_REGISTRY_SHA256 = (
    "c80acb64eeeb3133dff4422fc798f5b75c6feb52cf32502888cac452e2d210a1"
)
PINNED_SOLVER_REGISTRY_SHA256 = (
    "23e404021dcae9b4c75dca810feb404afe6786aa14280f0ae88b0fa4f24fcec5"
)
PINNED_CERTIFICATE_SHA256 = (
    "d2cd11d1f8fd1b3669d988f590ee619e9a7f5ee6af43b3a0671830abc69f7fe1"
)
PINNED_ROOT_SHA256 = (
    "78d1589b4049483b2865e434ef3b3227a576daee654be042c9cd63419474c636"
)
LIFT_REPLAYER_NORMALIZED_LF_SHA256 = (
    "51ade5cf90ddf2f5925470e3275ba4dfd016f3dc252fa6d4fc9c4e88aea8cf12"
)

ARTIFACT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = ARTIFACT_DIR.parent.parent
LIFT_FIXTURE_PATH = ARTIFACT_DIR / "symbolic_pi_lift_fixture.json"
LIFT_REPLAYER_PATH = ARTIFACT_DIR / "symbolic_pi_lift_replayer.py"
CERTIFICATE_PATH = ARTIFACT_DIR / "symbolic_no_entry_certificate.json"
REPORT_PATH = ARTIFACT_DIR / "symbolic_no_entry_replayer_report.json"

INVENTORY_PATHS = (
    "artifacts/0018/source_registry.json",
    "artifacts/0019/source_state_bridge_fixture.json",
    "artifacts/0019/source_binding_replayer.py",
    "artifacts/0019/symbolic_pi_lift_fixture.json",
    "artifacts/0019/symbolic_pi_lift_replayer.py",
    "artifacts/0019/symbolic_no_entry_certificate.json",
    "artifacts/0019/symbolic_no_entry_replayer.py",
    "artifacts/0019/test_symbolic_no_entry_replayer.py",
)

HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
DYADIC_KEYS = {"numerator", "exponent"}
ATOM_KEYS = {"numerator", "denominator", "pi_exponent"}
INTERVAL_KEYS = {"lower", "upper", "lower_closed", "upper_closed"}
DOMAIN_AXES = ("u1", "u2", "t")
TRANSVERSE_AXES = tuple(range(8))
TRANSVERSE_PERIOD = Fraction(8)
RADIUS = Fraction(1, 2)
PI_EXPONENT_MIN = -16
PI_EXPONENT_MAX = 16

FORBIDDEN_PROJECT_IMPORTS = {
    "symbolic_no_entry_solver",
    "symbolic_physical_arb_jets",
    "symbolic_pi_lift",
    "physical_no_entry_solver",
    "physical_no_entry_replayer",
    "physical_arb_jets",
}
FORBIDDEN_DYNAMIC_MECHANISMS = {
    "importlib",
    "eval",
    "exec",
    "__import__",
}


class SymbolicNoEntryReplayError(ValueError):
    """A typed independent replay gate failed."""

    def __init__(self, gate: str, message: str):
        super().__init__(f"{gate}: {message}")
        self.gate = gate
        self.message = message


def fail(gate: str, message: str) -> None:
    raise SymbolicNoEntryReplayError(gate, message)


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
        fail(gate, f"{path} must be an integer; booleans are forbidden")
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


def _reject_duplicate_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("strict_json", f"duplicate object key {key!r}")
        result[key] = value
    return result


def _reject_float(token: str) -> None:
    fail("strict_json", f"ordinary JSON float {token!r} is forbidden")


def _reject_nonfinite(token: str) -> None:
    fail("strict_json", f"non-finite JSON token {token!r} is forbidden")


def assert_float_free_json(value: Any, path: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
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
            parse_float=_reject_float,
            parse_constant=_reject_nonfinite,
        )
    except SymbolicNoEntryReplayError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        fail("strict_json", str(error))
    assert_float_free_json(value)
    return value


def strict_json_load(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        fail("strict_json", f"cannot read {path}: {error}")
    value = strict_json_loads(text)
    if type(value) is not dict:
        fail("strict_json", f"{path} must contain an object")
    return value


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
        fail("dyadic", f"{path}.exponent is outside limits")
    if numerator == 0 and exponent != 0:
        fail("dyadic", f"{path} zero is not canonical")
    if numerator and exponent and numerator % 2 == 0:
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


def parse_atom(
    value: Any, path: str = "$atom"
) -> tuple[Fraction, int]:
    item = _exact_keys(value, ATOM_KEYS, path, "symbolic_atom")
    numerator = _integer(
        item["numerator"], f"{path}.numerator", "symbolic_atom"
    )
    denominator = _integer(
        item["denominator"], f"{path}.denominator", "symbolic_atom"
    )
    exponent = _integer(
        item["pi_exponent"], f"{path}.pi_exponent", "symbolic_atom"
    )
    if denominator <= 0:
        fail("symbolic_atom", f"{path}.denominator must be positive")
    coefficient = Fraction(numerator, denominator)
    if (
        coefficient.numerator != numerator
        or coefficient.denominator != denominator
    ):
        fail("symbolic_atom", f"{path} rational coefficient is not reduced")
    if not PI_EXPONENT_MIN <= exponent <= PI_EXPONENT_MAX:
        fail("symbolic_atom", f"{path}.pi_exponent is outside limits")
    if coefficient == 0 and (denominator != 1 or exponent != 0):
        fail("symbolic_atom", f"{path} zero is not canonical")
    return coefficient, exponent


def pi_free_fraction(value: Any, path: str) -> Fraction:
    coefficient, exponent = parse_atom(value, path)
    if exponent != 0:
        fail("symbolic_atom", f"{path} must be pi-free")
    return coefficient


def _arb_tuple(value: Fraction) -> tuple[int, int]:
    denominator = value.denominator
    if denominator & (denominator - 1):
        fail("arb_ingress", "exact Arb ingress requires a dyadic")
    return value.numerator, -(denominator.bit_length() - 1)


def exact_arb(value: Fraction | int) -> arb:
    return arb(_arb_tuple(Fraction(value)))


def rational_arb(value: Fraction | int) -> arb:
    fraction = Fraction(value)
    if fraction.denominator & (fraction.denominator - 1) == 0:
        return exact_arb(fraction)
    return arb(fraction.numerator) / fraction.denominator


def interval_arb(lower: Fraction, upper: Fraction) -> arb:
    if lower > upper:
        fail("arb_ingress", "reversed interval")
    midpoint = (lower + upper) / 2
    radius = (upper - lower) / 2
    return arb(_arb_tuple(midpoint), _arb_tuple(radius))


def exact_arb_fraction(value: arb, path: str) -> Fraction:
    if not value.is_finite() or not value.is_exact():
        fail("arb_endpoint", f"{path} must be a finite exact endpoint")
    try:
        raw_mantissa, raw_exponent = value.man_exp()
        mantissa = int(raw_mantissa)
        exponent = int(raw_exponent)
    except (TypeError, ValueError, OverflowError) as error:
        fail("arb_endpoint", f"{path} has no exact dyadic form: {error}")
    if exponent >= 0:
        return Fraction(mantissa << exponent)
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
    value: Any, path: str
) -> tuple[Fraction, Fraction]:
    item = _exact_keys(value, INTERVAL_KEYS, path, "box_schema")
    lower = parse_dyadic(item["lower"], f"{path}.lower")
    upper = parse_dyadic(item["upper"], f"{path}.upper")
    if lower >= upper:
        fail("box_schema", f"{path} must have positive width")
    if (
        _boolean(
            item["lower_closed"], f"{path}.lower_closed", "box_schema"
        )
        is not True
        or _boolean(
            item["upper_closed"], f"{path}.upper_closed", "box_schema"
        )
        is not False
    ):
        fail("half_open_cover", f"{path} must be lower-closed upper-open")
    return lower, upper


def parse_box(
    value: Any, path: str
) -> dict[str, tuple[Fraction, Fraction]]:
    item = _exact_keys(value, {"axes", "intervals"}, path, "box_schema")
    if item["axes"] != list(DOMAIN_AXES) or any(
        type(axis) is not str for axis in item["axes"]
    ):
        fail("box_schema", f"{path}.axes differs from the fixed order")
    intervals = item["intervals"]
    if type(intervals) is not list or len(intervals) != 3:
        fail("box_schema", f"{path}.intervals must contain three axes")
    return {
        axis: parse_interval(
            intervals[index], f"{path}.intervals[{index}]"
        )
        for index, axis in enumerate(DOMAIN_AXES)
    }


def _vector_atoms(
    value: Any, length: int, path: str
) -> list[Fraction]:
    if type(value) is not list or len(value) != length:
        fail("symbolic_problem", f"{path} must have length {length}")
    return [
        pi_free_fraction(item, f"{path}[{index}]")
        for index, item in enumerate(value)
    ]


def validate_symbolic_problem(problem: Any) -> dict[str, Any]:
    if type(problem) is not dict:
        fail("symbolic_problem", "closed-string problem must be an object")
    if semantic_sha256(problem) != CLOSED_STRING_PROBLEM_SHA256:
        fail("problem_hash", "closed-string problem differs from code pin")
    if problem.get("schema_version") != (
        "cyz-brief-0019-symbolic-pi-closed-string-problem-v1"
    ):
        fail("symbolic_problem", "closed-string problem schema differs")
    if problem.get("lift_registry_semantic_sha256") != LIFT_REGISTRY_SHA256:
        fail("lift_hash", "problem names a foreign lift registry")

    dimensions = problem.get("dimensions")
    if type(dimensions) is not dict or (
        dimensions.get("transverse") != 8
        or dimensions.get("target") != 9
        or dimensions.get("winding_axis") != 8
        or dimensions.get("transverse_axis_order") != list(range(8))
        or dimensions.get("target_axis_order") != list(range(9))
    ):
        fail("symbolic_problem", "dimension registry differs")

    torus = problem.get("target_torus")
    if type(torus) is not dict:
        fail("symbolic_problem", "target_torus is missing")
    periods = torus.get("periods")
    if type(periods) is not list or len(periods) != 9:
        fail("symbolic_problem", "target periods must have length nine")
    parsed_periods = [
        pi_free_fraction(item, f"$.target_torus.periods[{index}]")
        for index, item in enumerate(periods)
    ]
    if parsed_periods != [TRANSVERSE_PERIOD] * 8 + [Fraction(1)]:
        fail("symbolic_problem", "normalized target periods differ")

    hysteresis = problem.get("hysteresis")
    if type(hysteresis) is not dict or pi_free_fraction(
        hysteresis.get("r_out"), "$.hysteresis.r_out"
    ) != RADIUS:
        fail("symbolic_problem", "registered r_out is not one half")

    observation = problem.get("observation")
    if type(observation) is not dict:
        fail("symbolic_problem", "observation registry is missing")
    t0 = pi_free_fraction(observation.get("t0"), "$.observation.t0")
    t1 = pi_free_fraction(observation.get("t1"), "$.observation.t1")
    if not t0 < t1:
        fail("symbolic_problem", "observation window is empty")
    if (
        observation.get("window_closure")
        != "lower_closed_upper_open"
        or observation.get("time_is_quotient") is not False
        or observation.get("initial_history") != "armed"
    ):
        fail("symbolic_problem", "time-window semantics differ")

    worldsheet = problem.get("worldsheet")
    if type(worldsheet) is not dict:
        fail("seam", "worldsheet registry is missing")
    if worldsheet.get("orientations") != [1, -1]:
        fail("seam", "orientations differ")
    if worldsheet.get("transverse_seam_identity") != (
        "integer n gives exp(i*2*pi*n*(u+1))=exp(i*2*pi*n*u)"
    ):
        fail("seam", "transverse seam identity differs")
    actions = worldsheet.get("seam_image_actions")
    if type(actions) is not dict:
        fail("seam", "seam actions are missing")
    expected_actions = {
        "u1_plus_1": ([1, 0, 0], 1, "a1=o1"),
        "u2_plus_1": ([0, 1, 0], 1, "a2=-o2"),
        "corner_plus_1_plus_1": ([1, 1, 0], 2, "a12=a1+a2"),
    }
    if set(actions) != set(expected_actions):
        fail("seam", "seam-action names differ")
    for name, (shift, winding, rule) in expected_actions.items():
        action = actions[name]
        if type(action) is not dict or (
            action.get("parameter_shift") != shift
            or action.get("separation_winding_shift") != winding
            or action.get("n8_reindex_shift") != winding
            or action.get("exact_rule") != rule
        ):
            fail("seam", f"{name} action differs")

    kinematics = problem.get("kinematics")
    if type(kinematics) is not dict:
        fail("symbolic_problem", "kinematics is missing")
    initial_time = pi_free_fraction(
        kinematics.get("initial_time"), "$.kinematics.initial_time"
    )
    centres = kinematics.get("centres_Q1_Q2")
    if type(centres) is not dict or set(centres) != {"Q1", "Q2"}:
        fail("symbolic_problem", "centre registry differs")
    parsed_centres = {
        name: _vector_atoms(
            centres[name], 8, f"$.kinematics.centres_Q1_Q2.{name}"
        )
        for name in ("Q1", "Q2")
    }
    strings = kinematics.get("strings")
    if type(strings) is not list or len(strings) != 2:
        fail("symbolic_problem", "exactly two strings are required")

    parsed_strings: list[dict[str, Any]] = []
    for string_index, string in enumerate(strings):
        path = f"$.kinematics.strings[{string_index}]"
        if type(string) is not dict:
            fail("symbolic_problem", f"{path} must be an object")
        if (
            string.get("string_id") != string_index + 1
            or string.get("orientation") != [1, -1][string_index]
        ):
            fail("symbolic_problem", f"{path} identity differs")
        velocity = _vector_atoms(
            string.get("transverse_velocity"),
            8,
            f"{path}.transverse_velocity",
        )
        modes = string.get("modes")
        if type(modes) is not list or not modes:
            fail("symbolic_problem", f"{path}.modes must be nonempty")
        parsed_modes: list[dict[str, Any]] = []
        for mode_index, mode in enumerate(modes):
            mode_path = f"{path}.modes[{mode_index}]"
            if type(mode) is not dict:
                fail("symbolic_problem", f"{mode_path} must be an object")
            harmonic = _integer(
                mode.get("mode_number"),
                f"{mode_path}.mode_number",
                "symbolic_problem",
            )
            if harmonic <= 0:
                fail("symbolic_problem", "mode number must be positive")
            expected_frequency = Fraction(harmonic, 8)
            for field in (
                "wave_number",
                "temporal_angular_frequency",
            ):
                if pi_free_fraction(
                    mode.get(field), f"{mode_path}.{field}"
                ) != expected_frequency:
                    fail("symbolic_problem", f"{mode_path}.{field} differs")
            if parse_atom(
                mode.get("spatial_phase_coefficient"),
                f"{mode_path}.spatial_phase_coefficient",
            ) != (Fraction(2 * harmonic), 1):
                fail(
                    "seam",
                    f"{mode_path} lacks an integer-periodic phase",
                )
            parsed_modes.append(
                {
                    "mode_number": harmonic,
                    "initial_x": _vector_atoms(
                        mode.get("initial_x"),
                        8,
                        f"{mode_path}.initial_x",
                    ),
                    "initial_y": _vector_atoms(
                        mode.get("initial_y"),
                        8,
                        f"{mode_path}.initial_y",
                    ),
                    "initial_p": _vector_atoms(
                        mode.get("initial_p"),
                        8,
                        f"{mode_path}.initial_p",
                    ),
                    "initial_q": _vector_atoms(
                        mode.get("initial_q"),
                        8,
                        f"{mode_path}.initial_q",
                    ),
                }
            )
        parsed_strings.append(
            {
                "orientation": string["orientation"],
                "velocity": velocity,
                "modes": parsed_modes,
            }
        )

    return {
        "t0": t0,
        "t1": t1,
        "initial_time": initial_time,
        "centres": parsed_centres,
        "strings": parsed_strings,
        "periods": parsed_periods,
        "radius": RADIUS,
        "transverse_seam": (
            "integer harmonics make axes 0..7 exactly periodic mod one"
        ),
        "winding_seam_shifts": [1, 1],
    }


def replay_symbolic_lift(
    lift_fixture: Any | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Run the independent source/lift gate and return its canonical problem."""

    if normalized_lf_sha256(LIFT_REPLAYER_PATH) != (
        LIFT_REPLAYER_NORMALIZED_LF_SHA256
    ):
        fail("lift_replayer_code", "lift replayer differs from code pin")
    try:
        material = lift_replay._independent_source_material()
        candidate = (
            lift_replay.strict_json_load(LIFT_FIXTURE_PATH)
            if lift_fixture is None
            else copy.deepcopy(lift_fixture)
        )
        commitments = lift_replay.replay_fixture_objects(
            candidate, material
        )
    except Exception as error:
        fail("independent_lift_gate", str(error))
    if type(candidate) is not dict:
        fail("independent_lift_gate", "lift fixture is not an object")
    problem = candidate.get("closed_string_problem")
    if type(problem) is not dict:
        fail("independent_lift_gate", "lift fixture lacks its problem")
    if commitments.get("closed_string_problem_semantic_sha256") != (
        CLOSED_STRING_PROBLEM_SHA256
    ):
        fail("problem_hash", "lift gate returned a foreign problem")
    if commitments.get("lift_registry_semantic_sha256") != (
        LIFT_REGISTRY_SHA256
    ):
        fail("lift_hash", "lift gate returned a foreign registry")
    parsed = validate_symbolic_problem(problem)
    return problem, parsed, commitments


def expected_registered_domain(
    parsed_problem: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "axes": list(DOMAIN_AXES),
        "intervals": [
            {
                "lower": dyadic_json(0),
                "upper": dyadic_json(1),
                "lower_closed": True,
                "upper_closed": False,
            },
            {
                "lower": dyadic_json(0),
                "upper": dyadic_json(1),
                "lower_closed": True,
                "upper_closed": False,
            },
            {
                "lower": dyadic_json(parsed_problem["t0"]),
                "upper": dyadic_json(parsed_problem["t1"]),
                "lower_closed": True,
                "upper_closed": False,
            },
        ],
    }


def _mode_value(
    mode: Mapping[str, Any],
    component: int,
    worldsheet: arb,
    mode_time: arb,
) -> arb:
    harmonic = mode["mode_number"]
    frequency = exact_arb(Fraction(harmonic, 8))
    x0 = rational_arb(mode["initial_x"][component])
    y0 = rational_arb(mode["initial_y"][component])
    p0 = rational_arb(mode["initial_p"][component])
    q0 = rational_arb(mode["initial_q"][component])
    temporal_argument = frequency * mode_time
    temporal_cosine = temporal_argument.cos()
    temporal_sine = temporal_argument.sin()
    spatial_argument = exact_arb(2 * harmonic) * worldsheet
    spatial_sine, spatial_cosine = spatial_argument.sin_cos_pi()
    x_time = (
        x0 * temporal_cosine
        + (p0 / frequency) * temporal_sine
    )
    y_time = (
        y0 * temporal_cosine
        + (q0 / frequency) * temporal_sine
    )
    return x_time * spatial_cosine + y_time * spatial_sine


def evaluate_transverse_d(
    problem: Mapping[str, Any],
    parsed_problem: Mapping[str, Any],
    box: Any,
    precision_bits: int,
) -> list[arb]:
    """Fresh 8-axis Arb evaluator independent of every solver/jet module."""

    if semantic_sha256(problem) != CLOSED_STRING_PROBLEM_SHA256:
        fail("problem_hash", "evaluator received a foreign problem")
    parsed_box = parse_box(box, "$.evaluation_box")
    backend_identity()
    with precision(precision_bits):
        u1 = interval_arb(*parsed_box["u1"])
        u2 = interval_arb(*parsed_box["u2"])
        time = interval_arb(*parsed_box["t"])
        mode_time = time - exact_arb(parsed_problem["initial_time"])
        centres = parsed_problem["centres"]
        strings = parsed_problem["strings"]
        result: list[arb] = []
        for component in TRANSVERSE_AXES:
            string_values: list[arb] = []
            for string, worldsheet in zip(strings, (u1, u2)):
                accumulated = arb(0)
                for mode in string["modes"]:
                    accumulated += _mode_value(
                        mode, component, worldsheet, mode_time
                    )
                string_values.append(accumulated)
            relative_velocity = (
                strings[0]["velocity"][component]
                - strings[1]["velocity"][component]
            )
            result.append(
                rational_arb(centres["Q1"][component])
                - rational_arb(centres["Q2"][component])
                + rational_arb(relative_velocity) * mode_time
                + string_values[0]
                - string_values[1]
            )
        return result


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def derive_empty_image_witness(
    *,
    axis: int,
    lower: Fraction,
    upper: Fraction,
    period: Fraction = TRANSVERSE_PERIOD,
    radius: Fraction = RADIUS,
) -> dict[str, Any] | None:
    """Derive the strict empty lattice-image range for one transverse axis."""

    if type(axis) is not int or axis not in TRANSVERSE_AXES:
        fail("leaf_witness", "axis must be an integer in 0..7")
    if lower > upper:
        fail("leaf_witness", "d enclosure is reversed")
    if period != TRANSVERSE_PERIOD:
        fail("leaf_witness", "transverse period must be exactly eight")
    if radius != RADIUS:
        fail("leaf_witness", "radius must be exactly one half")
    nmin = ceil_fraction((lower - radius) / period)
    nmax = floor_fraction((upper + radius) / period)
    if nmin <= nmax:
        return None
    above_previous = (lower - radius) - nmax * period
    below_next = nmin * period - (upper + radius)
    minimum = min(above_previous, below_next)
    if above_previous <= 0 or below_next <= 0 or minimum <= 0:
        fail("strict_image_gap", "empty range lacks a strict margin")
    return {
        "witness_type": "empty_transverse_coordinate_image_range",
        "evaluated_on": "closed_hull_of_owned_half_open_box",
        "axis": axis,
        "d_enclosure": {
            "lo": dyadic_json(lower),
            "hi": dyadic_json(upper),
        },
        "period": dyadic_json(period),
        "radius": dyadic_json(radius),
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


def derive_leaf_witness(
    problem: Mapping[str, Any],
    parsed_problem: Mapping[str, Any],
    box: Any,
    precision_bits: int,
) -> tuple[dict[str, Any] | None, list[tuple[Fraction, Fraction]]]:
    values = evaluate_transverse_d(
        problem, parsed_problem, box, precision_bits
    )
    # Arb's lower()/upper() extraction itself observes the active precision.
    # Re-enter the registered context so endpoint serialization matches the
    # outward 192-bit hull, rather than rounding it again at ctx's default.
    with precision(precision_bits):
        bounds = [
            exact_arb_bounds(value, f"$.d[{axis}]")
            for axis, value in enumerate(values)
        ]
    for axis, (lower, upper) in enumerate(bounds):
        witness = derive_empty_image_witness(
            axis=axis,
            lower=lower,
            upper=upper,
        )
        if witness is not None:
            return witness, bounds
    return None, bounds


def expected_solver_registry() -> dict[str, Any]:
    return {
        "schema_version": SOLVER_REGISTRY_SCHEMA,
        "solver_id": "index2-symbolic-pi-transverse-cover-v1",
        "closed_string_problem_semantic_sha256": (
            CLOSED_STRING_PROBLEM_SHA256
        ),
        "symbolic_lift_registry_semantic_sha256": LIFT_REGISTRY_SHA256,
        "arb_backend": {
            "python_flint_version": PYTHON_FLINT_VERSION,
            "flint_version": FLINT_VERSION,
            "precision_bits": PRECISION_BITS,
            "endpoint_encoding": (
                "exact reduced dyadics from Arb lower/upper endpoints"
            ),
            "evaluator": (
                "symbolic_physical_arb_jets."
                "evaluate_symbolic_physical_jets"
            ),
            "fail_closed_problem_hash": CLOSED_STRING_PROBLEM_SHA256,
        },
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
        "proof_target_axis_order": list(TRANSVERSE_AXES),
        "proof_independence": {
            "transverse_period": dyadic_json(TRANSVERSE_PERIOD),
            "radius": dyadic_json(RADIUS),
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
            "max_nodes": 4095,
            "max_depth": 48,
            "budget_stop": (
                "typed_unresolved_leaf_with_reserved_nodes"
            ),
        },
    }


def validate_solver_registry(
    registry: Any, stored_digest: Any
) -> dict[str, Any]:
    expected = expected_solver_registry()
    if not type_strict_equal(registry, expected):
        fail("solver_registry", "stored registry differs from replay pin")
    digest = semantic_sha256(registry)
    if _sha256_token(
        stored_digest,
        "$.solver_registry_semantic_sha256",
        "solver_registry_hash",
    ) != digest:
        fail("solver_registry_hash", "stored registry hash differs")
    if digest != PINNED_SOLVER_REGISTRY_SHA256:
        fail("solver_registry_hash", "registry is not code-pinned")
    backend_identity()
    return expected


def _same_box(
    left: Mapping[str, tuple[Fraction, Fraction]],
    right: Mapping[str, tuple[Fraction, Fraction]],
) -> bool:
    return all(left[axis] == right[axis] for axis in DOMAIN_AXES)


def _expected_split_axis(
    box: Mapping[str, tuple[Fraction, Fraction]],
    root: Mapping[str, tuple[Fraction, Fraction]],
) -> str:
    widths = {
        axis: (box[axis][1] - box[axis][0])
        / (root[axis][1] - root[axis][0])
        for axis in DOMAIN_AXES
    }
    maximum = max(widths.values())
    return next(axis for axis in DOMAIN_AXES if widths[axis] == maximum)


def _split_children(
    box: Mapping[str, tuple[Fraction, Fraction]],
    axis: str,
    point: Fraction,
) -> tuple[
    dict[str, tuple[Fraction, Fraction]],
    dict[str, tuple[Fraction, Fraction]],
]:
    lower, upper = box[axis]
    if point != (lower + upper) / 2:
        fail("split_rule", "split point is not the exact midpoint")
    if not lower < point < upper:
        fail("split_rule", "split point is not strictly interior")
    left = dict(box)
    right = dict(box)
    left[axis] = (lower, point)
    right[axis] = (point, upper)
    return left, right


def _node_payload_without_hash(
    node: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in node.items()
        if key != "node_semantic_sha256"
    }


def _certificate_payload_without_hash(
    certificate: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in certificate.items()
        if key != "certificate_semantic_sha256"
    }


def _validate_unresolved_witness(
    witness: Any,
    *,
    depth: int,
    nodes_created: int,
    reserved_nodes: int,
    max_nodes: int,
    max_depth: int,
) -> None:
    obj = _exact_keys(
        witness,
        {
            "witness_type",
            "reason",
            "max_nodes",
            "max_depth",
            "nodes_created_before_stop",
            "reserved_nodes",
            "next_action",
        },
        "$.unresolved",
        "unresolved_budget",
    )
    if obj["witness_type"] != "unresolved":
        fail("unresolved_budget", "witness type differs")
    expected_reason: str | None = None
    if depth >= max_depth:
        expected_reason = "maximum_depth_exhausted"
    elif nodes_created + 2 + reserved_nodes > max_nodes:
        expected_reason = "node_budget_exhausted"
    if expected_reason is None:
        fail("unresolved_budget", "budget did not force an unresolved leaf")
    expected = {
        "witness_type": "unresolved",
        "reason": expected_reason,
        "max_nodes": max_nodes,
        "max_depth": max_depth,
        "nodes_created_before_stop": nodes_created,
        "reserved_nodes": reserved_nodes,
        "next_action": "bisect_registered_box",
    }
    if not type_strict_equal(obj, expected):
        fail("unresolved_budget", "typed unresolved payload differs")


def replay_tree(
    tree: Any,
    domain: Mapping[str, Any],
    problem: Mapping[str, Any],
    parsed_problem: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    tree_obj = _exact_keys(
        tree,
        {"storage", "root_node_id", "nodes"},
        "$.tree",
        "tree_schema",
    )
    if tree_obj["storage"] != (
        "flat_preorder_with_bottom_up_child_hashes"
    ):
        fail("tree_schema", "unsupported tree storage")
    if tree_obj["root_node_id"] != "r":
        fail("tree_schema", "root id must be r")
    nodes = tree_obj["nodes"]
    if type(nodes) is not list or not nodes:
        fail("tree_schema", "tree.nodes must be nonempty")
    max_nodes = registry["budgets"]["max_nodes"]
    max_depth = registry["budgets"]["max_depth"]
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
            fail("node_schema", f"noncanonical node id {node_id!r}")
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
    split_count = 0
    excluded_count = 0
    unresolved_count = 0
    maximum_depth = 0
    axis_counts = [0] * 8
    minimum_margin: Fraction | None = None

    def visit(
        node_id: str,
        expected_parent: str | None,
        expected_depth: int,
        expected_box: Mapping[str, tuple[Fraction, Fraction]],
        reserved_nodes: int,
    ) -> str:
        nonlocal split_count, excluded_count, unresolved_count
        nonlocal maximum_depth, minimum_margin
        if node_id not in by_id:
            fail("tree_cover", f"missing node {node_id!r}")
        if node_id in visited:
            fail("tree_cover", f"cycle/shared child at {node_id!r}")
        visited.add(node_id)
        preorder.append(node_id)
        nodes_created = len(preorder)
        if nodes_created + reserved_nodes > max_nodes:
            fail("tree_budget", f"{node_id} violates node reservation")

        node = by_id[node_id]
        if node["parent_id"] != expected_parent:
            fail("tree_cover", f"{node_id} parent differs")
        depth = _nonnegative_integer(
            node["depth"], f"$.tree.{node_id}.depth", "tree_cover"
        )
        if depth != expected_depth:
            fail("tree_cover", f"{node_id} depth differs")
        if depth > max_depth:
            fail("tree_budget", f"{node_id} exceeds max_depth")
        maximum_depth = max(maximum_depth, depth)
        parsed_box = parse_box(node["box"], f"$.tree.{node_id}.box")
        if not _same_box(parsed_box, expected_box):
            fail("tree_cover", f"{node_id} box breaks the partition")

        fresh_witness, _ = derive_leaf_witness(
            problem,
            parsed_problem,
            node["box"],
            registry["arb_backend"]["precision_bits"],
        )
        kind = node["node_kind"]
        if kind == "split":
            if fresh_witness is not None:
                fail("split_rule", f"{node_id} should be an excluded leaf")
            if depth >= max_depth:
                fail("unresolved_budget", f"{node_id} should stop at depth")
            if nodes_created + 2 + reserved_nodes > max_nodes:
                fail("unresolved_budget", f"{node_id} should stop at budget")
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
            if payload["split_type"] != (
                "normalized_widest_axis_midpoint"
            ):
                fail("split_rule", f"{node_id} split type differs")
            expected_axis = _expected_split_axis(parsed_box, root_box)
            if payload["split_axis"] != expected_axis:
                fail("split_rule", f"{node_id} split axis differs")
            point = parse_dyadic(
                payload["split_point"],
                f"$.tree.{node_id}.payload.split_point",
            )
            left_box, right_box = _split_children(
                parsed_box, expected_axis, point
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
            if left_id != node_id + "L" or right_id != node_id + "R":
                fail("tree_cover", f"{node_id} child ids are noncanonical")
            left_hash = visit(
                left_id,
                node_id,
                depth + 1,
                left_box,
                reserved_nodes + 1,
            )
            right_hash = visit(
                right_id,
                node_id,
                depth + 1,
                right_box,
                reserved_nodes,
            )
            if (
                _sha256_token(
                    payload["left_child_semantic_sha256"],
                    f"$.tree.{node_id}.payload.left_child_semantic_sha256",
                    "bottom_up_hash",
                )
                != left_hash
                or _sha256_token(
                    payload["right_child_semantic_sha256"],
                    f"$.tree.{node_id}.payload.right_child_semantic_sha256",
                    "bottom_up_hash",
                )
                != right_hash
            ):
                fail("bottom_up_hash", f"{node_id} child hash differs")
        elif kind == "leaf":
            payload = _exact_keys(
                node["payload"],
                {"witness"},
                f"$.tree.{node_id}.payload",
                "leaf_schema",
            )
            stored_witness = payload["witness"]
            if (
                type(stored_witness) is dict
                and stored_witness.get("witness_type") == "unresolved"
            ):
                if fresh_witness is not None:
                    fail(
                        "false_unresolved",
                        f"{node_id} is independently excluded",
                    )
                _validate_unresolved_witness(
                    stored_witness,
                    depth=depth,
                    nodes_created=nodes_created,
                    reserved_nodes=reserved_nodes,
                    max_nodes=max_nodes,
                    max_depth=max_depth,
                )
                unresolved_count += 1
            else:
                if fresh_witness is None:
                    fail("leaf_witness", f"{node_id} is not excluded")
                if not type_strict_equal(stored_witness, fresh_witness):
                    fail(
                        "leaf_witness",
                        f"{node_id} interval/image witness differs "
                        "from fresh Arb replay",
                    )
                excluded_count += 1
                axis = fresh_witness["axis"]
                axis_counts[axis] += 1
                margin = parse_dyadic(
                    fresh_witness["margins"]["minimum"],
                    f"$.tree.{node_id}.witness.minimum",
                )
                if margin <= 0:
                    fail("strict_image_gap", f"{node_id} margin is not strict")
                minimum_margin = (
                    margin
                    if minimum_margin is None
                    else min(minimum_margin, margin)
                )
        else:
            fail("node_schema", f"{node_id} has unknown kind {kind!r}")

        computed_hash = semantic_sha256(_node_payload_without_hash(node))
        if computed_hash != node["node_semantic_sha256"]:
            fail("node_hash", f"{node_id} semantic hash differs")
        return computed_hash

    root_hash = visit("r", None, 0, root_box, 0)
    if len(visited) != len(nodes):
        fail("tree_cover", "tree contains unreachable nodes")
    if preorder != serialized_order:
        fail("tree_preorder", "nodes are not in exact flat preorder")
    if len(nodes) != 2 * split_count + 1:
        fail("tree_cover", "tree is not a full finite binary tree")
    leaf_count = excluded_count + unresolved_count
    if leaf_count != split_count + 1:
        fail("tree_cover", "leaf accounting differs")
    return {
        "root_node_semantic_sha256": root_hash,
        "node_count": len(nodes),
        "split_nodes": split_count,
        "leaf_count": leaf_count,
        "excluded_leaves": excluded_count,
        "unresolved_leaves": unresolved_count,
        "maximum_depth": maximum_depth,
        "transverse_axis_counts": axis_counts,
        "minimum_strict_coordinate_margin": (
            dyadic_json(minimum_margin)
            if minimum_margin is not None
            else None
        ),
    }


def expected_summary(
    tree_replay: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "node_count": tree_replay["node_count"],
        "split_nodes": tree_replay["split_nodes"],
        "leaf_count": tree_replay["leaf_count"],
        "excluded_leaves": tree_replay["excluded_leaves"],
        "unresolved_leaves": tree_replay["unresolved_leaves"],
        "maximum_depth": tree_replay["maximum_depth"],
        "transverse_axis_counts": copy.deepcopy(
            tree_replay["transverse_axis_counts"]
        ),
        "proof_target_axes": list(TRANSVERSE_AXES),
        "root_node_semantic_sha256": tree_replay[
            "root_node_semantic_sha256"
        ],
        "partition": "complete_gap_free_half_open_binary_tree",
        "proof_evaluation": "closed_hull_recomputed_at_every_leaf",
    }


def expected_outcome(domain: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": SUCCESS_OUTCOME,
        "scope": "registered_finite_closed_string_window_only",
        "window": copy.deepcopy(dict(domain)),
        "all_leaves_excluded": True,
        "unresolved_leaves": 0,
        "history_at_right_boundary": "armed",
        "all_time_no_entry_claimed": False,
        "exact_worldsheet_quotient_claimed": True,
        "transverse_exclusion_only": True,
        "winding_image_used": False,
        "winding_metric_used": False,
    }


def replay_certificate_objects(
    certificate: Any,
    *,
    lift_fixture: Any | None = None,
) -> dict[str, Any]:
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
        "$.certificate",
        "certificate_schema",
    )
    if obj["schema_version"] != CERTIFICATE_SCHEMA:
        fail("certificate_schema", "unsupported certificate schema")
    if obj["certificate_id"] != (
        "index2-symbolic-pi-window0-transverse-cover-v1"
    ):
        fail("certificate_schema", "certificate id differs")
    if obj["closed_string_problem_semantic_sha256"] != (
        CLOSED_STRING_PROBLEM_SHA256
    ):
        fail("problem_hash", "certificate binds a foreign problem")
    if obj["symbolic_lift_registry_semantic_sha256"] != (
        LIFT_REGISTRY_SHA256
    ):
        fail("lift_hash", "certificate binds a foreign lift")

    problem, parsed_problem, lift_commitments = replay_symbolic_lift(
        lift_fixture
    )
    registry = validate_solver_registry(
        obj["solver_registry"],
        obj["solver_registry_semantic_sha256"],
    )
    certificate_hash = _sha256_token(
        obj["certificate_semantic_sha256"],
        "$.certificate.certificate_semantic_sha256",
        "certificate_hash",
    )
    if certificate_hash != semantic_sha256(
        _certificate_payload_without_hash(obj)
    ):
        fail("certificate_hash", "certificate self-hash differs")

    domain = obj["domain"]
    parse_box(domain, "$.domain")
    expected_domain = expected_registered_domain(parsed_problem)
    if not type_strict_equal(domain, expected_domain):
        fail("domain_binding", "root domain differs from canonical problem")

    tree_replay = replay_tree(
        obj["tree"], domain, problem, parsed_problem, registry
    )
    summary = expected_summary(tree_replay)
    if not type_strict_equal(obj["summary"], summary):
        fail("summary", "stored summary differs from tree replay")
    pinned_topology = (
        tree_replay["node_count"],
        tree_replay["split_nodes"],
        tree_replay["leaf_count"],
        tree_replay["excluded_leaves"],
        tree_replay["unresolved_leaves"],
        tree_replay["maximum_depth"],
        tree_replay["transverse_axis_counts"],
    )
    expected_topology = (
        EXPECTED_NODE_COUNT,
        EXPECTED_SPLIT_COUNT,
        EXPECTED_LEAF_COUNT,
        EXPECTED_LEAF_COUNT,
        0,
        EXPECTED_MAXIMUM_DEPTH,
        EXPECTED_AXIS_COUNTS,
    )
    if pinned_topology != expected_topology:
        fail(
            "default_topology",
            f"expected={expected_topology}, actual={pinned_topology}",
        )
    if tree_replay["root_node_semantic_sha256"] != PINNED_ROOT_SHA256:
        fail("root_hash", "root node differs from code pin")

    outcome = expected_outcome(domain)
    if not type_strict_equal(obj["outcome"], outcome):
        fail("outcome", "outcome/scope differs from proved finite window")
    if tree_replay["minimum_strict_coordinate_margin"] is None:
        fail("strict_image_gap", "no strict leaf margin was replayed")
    # This anchor is deliberately checked only after the scientific replay.
    # Thus a hostile certificate with all ordinary hashes resealed is rejected
    # by its violated partition/witness/outcome gate, not merely by this pin.
    if certificate_hash != PINNED_CERTIFICATE_SHA256:
        fail("certificate_hash", "certificate is not code-pinned")

    return {
        "source_registry_canonical_sha256": lift_commitments[
            "source_registry_canonical_sha256"
        ],
        "source_draw_sha256": lift_commitments["source_draw_sha256"],
        "source_state_sha256": lift_commitments["source_state_sha256"],
        "source_bridge_fixture_semantic_sha256": lift_commitments[
            "source_bridge_fixture_semantic_sha256"
        ],
        "lift_registry_semantic_sha256": LIFT_REGISTRY_SHA256,
        "closed_string_problem_semantic_sha256": (
            CLOSED_STRING_PROBLEM_SHA256
        ),
        "lift_fixture_semantic_sha256": lift_commitments[
            "lift_fixture_semantic_sha256"
        ],
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
        "unresolved_leaves": tree_replay["unresolved_leaves"],
        "maximum_depth": tree_replay["maximum_depth"],
        "transverse_axis_counts": tree_replay[
            "transverse_axis_counts"
        ],
        "minimum_strict_coordinate_margin": tree_replay[
            "minimum_strict_coordinate_margin"
        ],
        "arb_backend": {
            "python_flint": PYTHON_FLINT_VERSION,
            "flint": FLINT_VERSION,
            "precision_bits": PRECISION_BITS,
            "arithmetic": "arb outward-rounded balls",
        },
        "domain_topology": (
            "u1,u2 exact mod-one quotient fundamental domain; "
            "finite half-open physical-time window"
        ),
        "worldsheet_seam": parsed_problem["transverse_seam"],
        "quotient_safety": (
            "one strict transverse coordinate gap excludes every full "
            "target-lattice image independently of winding"
        ),
        "proof_evaluation": (
            "fresh closed Arb hull on every node; stored intervals unused"
        ),
        "outcome": SUCCESS_OUTCOME,
        "scope": "registered_finite_closed_string_window_only",
        "all_time_no_entry_claimed": False,
        "exact_worldsheet_quotient_claimed": True,
        "winding_axis_used": False,
        "winding_image_used": False,
        "winding_metric_used": False,
    }


def replay_certificate_path(
    path: Path = CERTIFICATE_PATH,
) -> dict[str, Any]:
    return replay_certificate_objects(strict_json_load(path))


def _reseal_certificate(certificate: dict[str, Any]) -> None:
    """Refresh ordinary hashes without repairing hostile scientific data."""

    nodes = certificate["tree"]["nodes"]
    by_id = {
        node.get("node_id"): node
        for node in nodes
        if type(node) is dict
    }
    for node in reversed(nodes):
        if type(node) is not dict:
            continue
        if node.get("node_kind") == "split":
            payload = node.get("payload", {})
            if type(payload) is dict:
                left = by_id.get(payload.get("left_child_id"))
                right = by_id.get(payload.get("right_child_id"))
                if type(left) is dict:
                    payload["left_child_semantic_sha256"] = left.get(
                        "node_semantic_sha256", ""
                    )
                if type(right) is dict:
                    payload["right_child_semantic_sha256"] = right.get(
                        "node_semantic_sha256", ""
                    )
        node["node_semantic_sha256"] = semantic_sha256(
            _node_payload_without_hash(node)
        )
    root = by_id.get(certificate["tree"].get("root_node_id"))
    if type(root) is dict:
        certificate["summary"]["root_node_semantic_sha256"] = root[
            "node_semantic_sha256"
        ]
    certificate["solver_registry_semantic_sha256"] = semantic_sha256(
        certificate["solver_registry"]
    )
    certificate["certificate_semantic_sha256"] = semantic_sha256(
        _certificate_payload_without_hash(certificate)
    )


def _first_leaf(certificate: Mapping[str, Any]) -> dict[str, Any]:
    return next(
        node
        for node in certificate["tree"]["nodes"]
        if node["node_kind"] == "leaf"
    )


def hostile_controls() -> dict[str, bool]:
    baseline = strict_json_load(CERTIFICATE_PATH)

    def rejected(
        mutator: Callable[[dict[str, Any]], None],
        *,
        reseal: bool = True,
    ) -> bool:
        hostile = copy.deepcopy(baseline)
        mutator(hostile)
        if reseal:
            _reseal_certificate(hostile)
        try:
            replay_certificate_objects(hostile)
        except SymbolicNoEntryReplayError:
            return True
        return False

    controls: dict[str, bool] = {}
    controls["fabricated_interval_rejected"] = rejected(
        lambda value: _first_leaf(value)["payload"]["witness"][
            "d_enclosure"
        ]["hi"].__setitem__(
            "numerator",
            _first_leaf(value)["payload"]["witness"]["d_enclosure"][
                "hi"
            ]["numerator"]
            + 2,
        )
    )
    controls["deleted_leaf_rejected"] = rejected(
        lambda value: value["tree"]["nodes"].remove(_first_leaf(value))
    )

    def reorder(value: dict[str, Any]) -> None:
        value["tree"]["nodes"][1:3] = reversed(
            value["tree"]["nodes"][1:3]
        )

    controls["reordered_nodes_rejected"] = rejected(reorder)

    def reorder_leaves(value: dict[str, Any]) -> None:
        indices = [
            index
            for index, node in enumerate(value["tree"]["nodes"])
            if node["node_kind"] == "leaf"
        ][:2]
        first, second = indices
        value["tree"]["nodes"][first], value["tree"]["nodes"][second] = (
            value["tree"]["nodes"][second],
            value["tree"]["nodes"][first],
        )

    controls["reordered_leaf_rejected"] = rejected(reorder_leaves)

    def gap(value: dict[str, Any]) -> None:
        leaf = _first_leaf(value)
        interval = leaf["box"]["intervals"][0]
        lower = parse_dyadic(interval["lower"])
        upper = parse_dyadic(interval["upper"])
        interval["upper"] = dyadic_json((lower + upper) / 2)

    controls["gap_or_overlap_rejected"] = rejected(gap)

    def overlap(value: dict[str, Any]) -> None:
        leaf = _first_leaf(value)
        interval = leaf["box"]["intervals"][0]
        upper = parse_dyadic(interval["upper"])
        interval["upper"] = dyadic_json(upper * 2)

    controls["overlap_rejected"] = rejected(overlap)
    controls["closure_mutation_rejected"] = rejected(
        lambda value: _first_leaf(value)["box"]["intervals"][0].__setitem__(
            "upper_closed", True
        )
    )
    controls["split_mutation_rejected"] = rejected(
        lambda value: value["tree"]["nodes"][0]["payload"].__setitem__(
            "split_axis", "u2"
        )
    )
    controls["axis_mutation_rejected"] = rejected(
        lambda value: _first_leaf(value)["payload"]["witness"].__setitem__(
            "axis", 8
        )
    )
    controls["period_mutation_rejected"] = rejected(
        lambda value: _first_leaf(value)["payload"]["witness"].__setitem__(
            "period", dyadic_json(16)
        )
    )
    controls["radius_mutation_rejected"] = rejected(
        lambda value: _first_leaf(value)["payload"]["witness"].__setitem__(
            "radius", dyadic_json(Fraction(1, 4))
        )
    )
    controls["problem_hash_mutation_rejected"] = rejected(
        lambda value: value.__setitem__(
            "closed_string_problem_semantic_sha256", "0" * 64
        )
    )
    controls["registry_mutation_rejected"] = rejected(
        lambda value: value["solver_registry"][
            "proof_target_axis_order"
        ].append(8)
    )
    controls["outcome_mutation_rejected"] = rejected(
        lambda value: value["outcome"].__setitem__("type", "first_entry")
    )
    controls["scope_mutation_rejected"] = rejected(
        lambda value: value["outcome"].__setitem__(
            "scope", "all_time"
        )
    )

    def false_unresolved(value: dict[str, Any]) -> None:
        leaf = _first_leaf(value)
        leaf["payload"]["witness"] = {
            "witness_type": "unresolved",
            "reason": "node_budget_exhausted",
            "max_nodes": 4095,
            "max_depth": 48,
            "nodes_created_before_stop": 1,
            "reserved_nodes": 0,
            "next_action": "bisect_registered_box",
        }

    controls["false_unresolved_complete_rejected"] = rejected(
        false_unresolved
    )
    controls["false_self_hash_rejected"] = rejected(
        lambda value: value.__setitem__(
            "certificate_semantic_sha256", "0" * 64
        ),
        reseal=False,
    )
    controls["boundary_equality_not_excluded"] = (
        derive_empty_image_witness(
            axis=0,
            lower=Fraction(1, 2),
            upper=Fraction(1, 2),
        )
        is None
    )

    lift_fixture = lift_replay.strict_json_load(LIFT_FIXTURE_PATH)

    def lift_rejected(
        mutator: Callable[[dict[str, Any]], None],
    ) -> bool:
        hostile = copy.deepcopy(lift_fixture)
        mutator(hostile)
        lift_replay._reseal_fixture(hostile)
        try:
            replay_certificate_objects(
                copy.deepcopy(baseline), lift_fixture=hostile
            )
        except SymbolicNoEntryReplayError:
            return True
        return False

    controls["coefficient_mutation_lift_gate_rejected"] = lift_rejected(
        lambda value: value["closed_string_problem"]["kinematics"][
            "strings"
        ][0]["modes"][0]["initial_x"][0].__setitem__(
            "numerator",
            value["closed_string_problem"]["kinematics"]["strings"][0][
                "modes"
            ][0]["initial_x"][0]["numerator"]
            + 2,
        )
    )
    controls["source_commitment_lift_gate_rejected"] = lift_rejected(
        lambda value: value["closed_string_problem"][
            "source_commitment"
        ].__setitem__("source_state_sha256", "0" * 64)
    )
    controls["seam_mutation_lift_gate_rejected"] = lift_rejected(
        lambda value: value["closed_string_problem"]["worldsheet"][
            "seam_image_actions"
        ]["u2_plus_1"].__setitem__("n8_reindex_shift", -1)
    )
    controls["metric_mutation_lift_gate_rejected"] = lift_rejected(
        lambda value: value["closed_string_problem"]["target_torus"][
            "metric_diagonal"
        ].__setitem__(8, lift_replay.make_atom(1))
    )
    return controls


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
    hostile = hostile_controls()
    if not all(hostile.values()):
        failed = sorted(name for name, passed in hostile.items() if not passed)
        fail("hostile_controls", f"accepted hostile controls: {failed}")
    report: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "status": "passed",
        "failed_gates": [],
        "checks": {
            "independent_source_and_symbolic_lift_replayed": True,
            "strict_float_free_certificate_replayed": True,
            "certificate_registry_problem_and_lift_hashes_recomputed": True,
            "root_half_open_quotient_domain_replayed": True,
            "flat_preorder_binary_partition_replayed": True,
            "exact_midpoint_split_and_closure_replayed": True,
            "reserved_node_unresolved_budget_semantics_replayed": True,
            "fresh_transverse_arb_enclosure_on_every_node": True,
            "all_leaf_intervals_ignored_then_recomputed": True,
            "strict_empty_8Z_image_ranges_replayed": True,
            "boundary_contact_not_excluded": True,
            "exact_integer_harmonic_worldsheet_seams_replayed": True,
            "winding_coordinate_and_metric_unused": True,
            "default_259_129_130_depth9_zero_unresolved_replayed": True,
            "finite_window_right_censored_scope_only": True,
        },
        "commitments": copy.deepcopy(dict(replay)),
        "hostile_controls": hostile,
        "independent_boundary": {
            "only_project_import": "symbolic_pi_lift_replayer",
            "lift_replayer_normalized_lf_sha256": (
                LIFT_REPLAYER_NORMALIZED_LF_SHA256
            ),
            "forbidden_project_imports": sorted(
                FORBIDDEN_PROJECT_IMPORTS
            ),
            "forbidden_dynamic_mechanisms": sorted(
                FORBIDDEN_DYNAMIC_MECHANISMS
            ),
            "transverse_evaluator": (
                "local python-flint Arb implementation from independently "
                "rebuilt q*pi^e source coefficients"
            ),
        },
        "validation_protocol": {
            "windows": {
                "environment": (
                    "PYTHONPATH includes vendor/python_flint and "
                    "artifacts/0019"
                ),
                "targeted_test_command": (
                    "python -m unittest discover -s artifacts/0019 "
                    "-p test_symbolic_no_entry_replayer.py -v"
                ),
                "registered_test_count": 22,
                "required_test_result": "OK",
                "check_command": (
                    "python artifacts/0019/"
                    "symbolic_no_entry_replayer.py --check"
                ),
                "check_semantics": (
                    "freshly replay certificate and hostile controls, "
                    "rebuild report, then require type-strict equality "
                    "and its semantic self-hash"
                ),
                "required_check_status": "PASS",
            },
            "cross_platform_requirement": (
                "the same pins, exact dyadic endpoints, tree topology, "
                "hostile matrix, and report hash must replay unchanged"
            ),
        },
        "normalized_lf_inventory": _inventory(),
        "scope": {
            "claim": (
                "independent quotient-safe replay of fixed-index-2 "
                "finite-window transverse no-entry"
            ),
            "logic": (
                "a strict gap from every 8Z image in any transverse "
                "coordinate implies full metric distance greater than "
                "r_out regardless of the winding coordinate"
            ),
            "does_not_claim": [
                "all-time no-entry",
                "a winding-coordinate exclusion",
                "the all-512 source population law",
                "dimension dynamics",
                "3+1 selection",
            ],
        },
    }
    report["report_semantic_sha256"] = semantic_sha256(report)
    return report


def verify_report(report: Any, replay: Mapping[str, Any]) -> str:
    expected = build_report(replay)
    obj = _exact_keys(
        report, set(expected), "$.report", "report_schema"
    )
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
        fail("report_hash", "report self-hash differs")
    if not type_strict_equal(obj, expected):
        fail("report_replay", "stored report differs from fresh replay")
    return stored_hash


def run(write: bool) -> dict[str, Any]:
    replay = replay_certificate_path()
    report = build_report(replay)
    if write:
        REPORT_PATH.write_text(
            pretty_json(report), encoding="utf-8", newline="\n"
        )
    else:
        verify_report(strict_json_load(REPORT_PATH), replay)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Independently replay the symbolic-pi transverse no-entry "
            "certificate"
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        report = run(write=arguments.write)
    except SymbolicNoEntryReplayError as error:
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "gate": error.gate,
                    "message": error.message,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    print(
        json.dumps(
            {
                "status": "PASS",
                "certificate_semantic_sha256": report["commitments"][
                    "certificate_semantic_sha256"
                ],
                "root_node_semantic_sha256": report["commitments"][
                    "root_node_semantic_sha256"
                ],
                "report_semantic_sha256": report[
                    "report_semantic_sha256"
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
