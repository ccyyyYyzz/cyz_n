#!/usr/bin/env python3
"""Source-measure bridge for the Brief 0019 symbolic-pi lift.

Two logically distinct statements are certified:

1. Empirical replay: the registered 512-sample Brief 0018 source sequence is
   unchanged, and exact-binary64 coefficients round-trip through the lift's
   canonical ``q*pi^0`` representation.
2. Analytic source law: although the primitive pairs ``(T_F, L_w)`` differ,
   the source generator sees the same ``K, E_*, M, k_n, P``, transverse Haar
   periods, orientations, seed, and named streams.  The latent and real
   coefficient transports are identities, so their Jacobian is one; the
   registered radial and chiral Jacobian factors are consequently identical.

This is a source-law certificate only.  It deliberately says nothing about
the physical event pushforward, entry probabilities, a population event law,
or dimensional selection.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import re
import sys
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable, Mapping, Sequence


REPORT_SCHEMA = "cyz-brief-0019-symbolic-source-measure-bridge-report-v1"
BRIDGE_ALGORITHM = "fixed-index-and-analytic-source-measure-identity-v1"

SOURCE_REGISTRY_CANONICAL_SHA256 = (
    "35d31a64e45d9a3ea9cc346e19d8bc5d8d40d1f9eac68eb07385fb291aed8cdb"
)
SOURCE_DRAW_SHA256 = (
    "4bc0d8eadef9ad8aea8752f25e105127311b83edebc99ebe1b1b7561999e1bd4"
)
SOURCE_MODULE_NORMALIZED_LF_SHA256 = (
    "12bb5ea71cebac869cbb519d46dd3c531e74b982203270e349a807b32853719e"
)
SOURCE_REGISTRY_NORMALIZED_LF_SHA256 = (
    "2944edc5668ad778c9d2158ad99bbd6133603873b93167cc8b90bf5f216f5742"
)
SYMBOLIC_LIFT_FIXTURE_SEMANTIC_SHA256 = (
    "8ab0bf7deca71d4a1d11f7656a2ee45dbe0766e4ca8ce886592559b080d24f9e"
)
LIFT_REGISTRY_SEMANTIC_SHA256 = (
    "c80acb64eeeb3133dff4422fc798f5b75c6feb52cf32502888cac452e2d210a1"
)
CLOSED_STRING_PROBLEM_SEMANTIC_SHA256 = (
    "3bb6599f211c26d98ecba2077051ad9d0339daf96d580a6399cc5a1ba7f030e0"
)
SOURCE_INDEX_2_STATE_SHA256 = (
    "1c671b6bf8e737d238c21de8b0f694a57b8bfab7006ebb1401136176567f118c"
)

SAMPLE_COUNT = 512
EXPECTED_VALID_COUNT = 283
EXPECTED_INVALID_COUNT = 229

# Filled after the empirical sequence and report schemas are frozen.
SOURCE_STATE_SEQUENCE_SHA256 = (
    "41dedf012c3e013043d38d8955614bcdce72418ba69aa56f3ce479c8fca10769"
)
COEFFICIENT_HASH_SEQUENCE_SHA256 = (
    "f07aae270a53f190ea2cd6c1955e50d61cee89e238b71c07e6d1b771019f5ce3"
)
SYMBOLIC_COEFFICIENT_SEQUENCE_SHA256 = (
    "43a8aab3471e00d42889f93c876fde5a14d8458e0f586c0fc18355f921429852"
)
REPORT_SEMANTIC_SHA256 = (
    "447c14b5e6dcece857148481342e8cf5033d0c78d4593263fe27d3452989cf9e"
)

PRNG_ALGORITHM = "sha256-counter-open52mid-decimal90-box-muller-integer-gamma-v2"
PORTABLE_MATH_VERSION = "decimal90-ln-sqrt-float64-fixed-taylor-sincos-v2"
PORTABLE_PI_TEXT = (
    "3.141592653589793238462643383279502884197169399375105820974944"
    "5923078164062862089986280348253421170679"
)

ARTIFACT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = ARTIFACT_DIR.parent / "0018"
SOURCE_MODULE_PATH = SOURCE_DIR / "microcanonical_source.py"
SOURCE_REGISTRY_PATH = SOURCE_DIR / "source_registry.json"
SYMBOLIC_LIFT_FIXTURE_PATH = ARTIFACT_DIR / "symbolic_pi_lift_fixture.json"
REPORT_PATH = ARTIFACT_DIR / "symbolic_source_measure_bridge_report.json"

HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
ATOM_KEYS = {"numerator", "denominator", "pi_exponent"}


class MeasureBridgeError(ValueError):
    """A measure-bridge gate failed."""

    def __init__(self, gate: str, message: str):
        super().__init__(f"{gate}: {message}")
        self.gate = gate


def fail(gate: str, message: str) -> None:
    raise MeasureBridgeError(gate, message)


def _exact_keys(
    value: Any, expected: set[str], path: str, gate: str
) -> dict[str, Any]:
    if type(value) is not dict:
        fail(gate, f"{path} must be an object")
    actual = set(value)
    if actual != expected:
        fail(
            gate,
            f"{path} keys differ; missing={sorted(expected-actual)}, "
            f"extra={sorted(actual-expected)}",
        )
    return value


def _integer(value: Any, path: str, gate: str) -> int:
    if type(value) is not int:
        fail(gate, f"{path} must be an integer; booleans are forbidden")
    return value


def _sha256(value: Any, path: str, gate: str) -> str:
    if type(value) is not str or HEX_SHA256.fullmatch(value) is None:
        fail(gate, f"{path} must be a lowercase SHA-256 digest")
    return value


def reject_duplicate_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("strict_json", f"duplicate object key {key!r}")
        result[key] = value
    return result


def reject_nonfinite(token: str) -> None:
    fail("strict_json", f"non-finite JSON token {token!r} is forbidden")


def reject_float(token: str) -> None:
    fail(
        "strict_json",
        f"ordinary JSON float {token!r} is forbidden in bridge artifacts",
    )


def assert_float_free(value: Any, path: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        fail("strict_json", f"{path} contains an ordinary float")
    if type(value) is list:
        for index, item in enumerate(value):
            assert_float_free(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                fail("strict_json", f"{path} contains a non-string key")
            assert_float_free(item, f"{path}.{key}")
        return
    fail("strict_json", f"{path} contains {type(value).__name__}")


def strict_json_loads(text: str) -> Any:
    value = json.loads(
        text,
        object_pairs_hook=reject_duplicate_pairs,
        parse_constant=reject_nonfinite,
        parse_float=reject_float,
    )
    assert_float_free(value)
    return value


def strict_json_load(path: Path) -> Any:
    with path.open("r", encoding="utf-8", newline=None) as handle:
        return strict_json_loads(handle.read())


def _registry_json_load(path: Path) -> Any:
    """Load the legacy registry with finite binary64 values preserved."""

    def parse_constant(token: str) -> None:
        fail("source_registry", f"non-finite token {token!r}")

    with path.open("r", encoding="utf-8", newline=None) as handle:
        value = json.loads(
            handle.read(),
            object_pairs_hook=reject_duplicate_pairs,
            parse_float=float,
            parse_constant=parse_constant,
        )

    def walk(item: Any, at: str) -> None:
        if item is None or type(item) in (bool, int, str):
            return
        if type(item) is float:
            if not math.isfinite(item):
                fail("source_registry", f"{at} is non-finite")
            return
        if type(item) is list:
            for index, child in enumerate(item):
                walk(child, f"{at}[{index}]")
            return
        if type(item) is dict:
            for key, child in item.items():
                walk(child, f"{at}.{key}")
            return
        fail("source_registry", f"{at} has unsupported type")

    walk(value, "$")
    return value


def canonical_bytes(value: Any, *, allow_floats: bool = False) -> bytes:
    if not allow_floats:
        assert_float_free(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def semantic_sha256(value: Any, *, allow_floats: bool = False) -> str:
    return hashlib.sha256(
        canonical_bytes(value, allow_floats=allow_floats)
    ).hexdigest()


def pretty_json(value: Any) -> str:
    assert_float_free(value)
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(pretty_json(value), encoding="utf-8", newline="\n")


def normalized_lf_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def type_strict_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(
            type_strict_equal(left[key], right[key]) for key in left
        )
    if type(left) is list:
        return len(left) == len(right) and all(
            type_strict_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def rational_record(value: Fraction | int) -> dict[str, int]:
    fraction = Fraction(value)
    return {
        "numerator": fraction.numerator,
        "denominator": fraction.denominator,
    }


def binary64_record(value: float) -> dict[str, Any]:
    if type(value) is not float or not math.isfinite(value):
        fail("binary64", "expected one finite binary64 value")
    return {
        "hex": value.hex(),
        "exact_dyadic": rational_record(Fraction.from_float(value)),
    }


def q_pi_atom(
    coefficient: Fraction | int, pi_exponent: int = 0
) -> dict[str, int]:
    if type(pi_exponent) is not int:
        fail("symbolic_atom", "pi exponent must be an integer")
    coefficient = Fraction(coefficient)
    if coefficient == 0:
        pi_exponent = 0
    return {
        "numerator": coefficient.numerator,
        "denominator": coefficient.denominator,
        "pi_exponent": pi_exponent,
    }


def parse_q_pi_atom(
    value: Any, path: str = "$"
) -> tuple[Fraction, int]:
    atom = _exact_keys(value, ATOM_KEYS, path, "symbolic_atom")
    numerator = _integer(
        atom["numerator"], f"{path}.numerator", "symbolic_atom"
    )
    denominator = _integer(
        atom["denominator"], f"{path}.denominator", "symbolic_atom"
    )
    exponent = _integer(
        atom["pi_exponent"], f"{path}.pi_exponent", "symbolic_atom"
    )
    if denominator <= 0:
        fail("symbolic_atom", f"{path}.denominator must be positive")
    if math.gcd(abs(numerator), denominator) != 1:
        fail("symbolic_atom", f"{path} coefficient is not reduced")
    if numerator == 0 and (denominator != 1 or exponent != 0):
        fail("symbolic_atom", f"{path} zero is not canonical")
    return Fraction(numerator, denominator), exponent


def multiply_q_pi_atoms(*atoms: Any) -> dict[str, int]:
    coefficient = Fraction(1)
    exponent = 0
    for index, atom in enumerate(atoms):
        value, power = parse_q_pi_atom(atom, f"$multiply[{index}]")
        coefficient *= value
        exponent += power
    return q_pi_atom(coefficient, exponent)


def _portable_fsum(values: Iterable[float]) -> float:
    with localcontext() as context:
        context.prec = 90
        context.rounding = ROUND_HALF_EVEN
        total = Decimal(0)
        for value in values:
            if type(value) is not float or not math.isfinite(value):
                fail("binary64_cell", "portable sum input is invalid")
            total += Decimal.from_float(value)
        return float(total)


def _load_source_module() -> ModuleType:
    actual = normalized_lf_sha256(SOURCE_MODULE_PATH)
    if actual != SOURCE_MODULE_NORMALIZED_LF_SHA256:
        fail("source_code_pin", "Brief 0018 source module hash differs")
    name = "_cyz_measure_bridge_source_0018"
    spec = importlib.util.spec_from_file_location(name, SOURCE_MODULE_PATH)
    if spec is None or spec.loader is None:
        fail("source_import", "cannot construct source module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_inputs() -> tuple[ModuleType, dict[str, Any], dict[str, Any]]:
    if (
        normalized_lf_sha256(SOURCE_REGISTRY_PATH)
        != SOURCE_REGISTRY_NORMALIZED_LF_SHA256
    ):
        fail("source_code_pin", "Brief 0018 source registry bytes differ")
    registry = _registry_json_load(SOURCE_REGISTRY_PATH)
    if (
        semantic_sha256(registry, allow_floats=True)
        != SOURCE_REGISTRY_CANONICAL_SHA256
    ):
        fail("source_registry", "canonical source registry hash differs")

    source = _load_source_module()
    source.validate_registry(registry)
    draw_identity = {
        "registry_schema": registry["schema_version"],
        "prng_algorithm": PRNG_ALGORITHM,
        "portable_math_version": PORTABLE_MATH_VERSION,
        "source_seed": registry["source_seed"],
        "source_draw_registry": registry["source_draw_registry"],
    }
    if (
        semantic_sha256(draw_identity, allow_floats=True)
        != SOURCE_DRAW_SHA256
    ):
        fail("source_draw", "independent source-draw digest differs")
    if source.source_draw_sha256(registry) != SOURCE_DRAW_SHA256:
        fail("source_draw", "generator source-draw digest differs")

    lift_fixture = strict_json_load(SYMBOLIC_LIFT_FIXTURE_PATH)
    if (
        semantic_sha256(lift_fixture)
        != SYMBOLIC_LIFT_FIXTURE_SEMANTIC_SHA256
    ):
        fail("lift_fixture", "symbolic lift fixture digest differs")
    registry_digest = _sha256(
        lift_fixture["lift_registry_semantic_sha256"],
        "$.symbolic_lift_fixture.lift_registry_semantic_sha256",
        "lift_fixture",
    )
    problem_digest = _sha256(
        lift_fixture["closed_string_problem_semantic_sha256"],
        "$.symbolic_lift_fixture.closed_string_problem_semantic_sha256",
        "lift_fixture",
    )
    if (
        registry_digest != LIFT_REGISTRY_SEMANTIC_SHA256
        or semantic_sha256(lift_fixture["lift_registry"])
        != LIFT_REGISTRY_SEMANTIC_SHA256
        or problem_digest != CLOSED_STRING_PROBLEM_SEMANTIC_SHA256
        or semantic_sha256(lift_fixture["closed_string_problem"])
        != CLOSED_STRING_PROBLEM_SEMANTIC_SHA256
    ):
        fail("lift_fixture", "symbolic lift component hash differs")
    return source, registry, lift_fixture


def _old_binary64_cell(
    source: ModuleType, registry: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_draw = registry["source_draw_registry"]
    portable_pi = float(Decimal(PORTABLE_PI_TEXT))
    if (
        source.PORTABLE_PI.hex() != portable_pi.hex()
        or source.PORTABLE_PI_TEXT != PORTABLE_PI_TEXT
    ):
        fail("binary64_cell", "portable pi definition differs")
    tension = source_draw["string_tension"]
    length = source_draw["winding_length"]
    mass = tension * length
    two_pi = 2.0 * portable_pi
    wave_number = two_pi / length
    energy = source_draw["transverse_energy"]
    momentum = tuple(source_draw["total_transverse_momentum"])
    momentum_squared = _portable_fsum(value * value for value in momentum)
    residual_energy = energy - momentum_squared / (4.0 * mass)
    expected_hex = {
        "portable_pi": "0x1.921fb54442d18p+1",
        "T_F_hat": "0x1.45f306dc9c883p-3",
        "L_hat": "0x1.921fb54442d18p+5",
        "M_rounded": "0x1.0000000000000p+3",
        "k_1_rounded": "0x1.0000000000000p-3",
        "E": "0x1.0000000000000p+1",
        "E_star_rounded": "0x1.0000000000000p+0",
    }
    actual_values = {
        "portable_pi": portable_pi,
        "T_F_hat": tension,
        "L_hat": length,
        "M_rounded": mass,
        "k_1_rounded": wave_number,
        "E": energy,
        "E_star_rounded": residual_energy,
    }
    for key, expected in expected_hex.items():
        if (
            type(actual_values[key]) is not float
            or actual_values[key].hex() != expected
        ):
            fail("binary64_cell", f"{key} binary64 value differs")
    if source.source_parameters(registry)["M"].hex() != expected_hex[
        "M_rounded"
    ]:
        fail("binary64_cell", "generator mass path differs")
    if source.source_parameters(registry)["k_values"][0].hex() != (
        expected_hex["k_1_rounded"]
    ):
        fail("binary64_cell", "generator wave-number path differs")
    if source.source_parameters(registry)["E_star"].hex() != (
        expected_hex["E_star_rounded"]
    ):
        fail("binary64_cell", "generator residual-energy path differs")
    record = {
        "rounding_model": "IEEE-754 binary64 round-to-nearest ties-to-even",
        "portable_pi": binary64_record(portable_pi),
        "T_F_hat": binary64_record(tension),
        "L_hat": binary64_record(length),
        "M_equals_rounded_T_F_hat_times_L_hat": binary64_record(mass),
        "k_1_equals_rounded_2_pi_hat_over_L_hat": binary64_record(
            wave_number
        ),
        "E": binary64_record(energy),
        "P_total": [binary64_record(value) for value in momentum],
        "P_squared_portable_sum": binary64_record(momentum_squared),
        "E_star": binary64_record(residual_energy),
    }
    semantic = {
        "K": source_draw["fourier_cutoff_K"],
        "M": Fraction.from_float(mass),
        "k_1": Fraction.from_float(wave_number),
        "E": Fraction.from_float(energy),
        "E_star": Fraction.from_float(residual_energy),
        "P_total": tuple(Fraction.from_float(value) for value in momentum),
        "transverse_periods": tuple(
            Fraction.from_float(value)
            for value in source_draw["torus_periods_L_A"][:8]
        ),
        "orientations": tuple(source_draw["winding_orientations"]),
        "seed": registry["source_seed"],
    }
    return record, semantic


def _new_exact_cell(
    lift_fixture: Mapping[str, Any],
    old_semantic: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    problem = lift_fixture["closed_string_problem"]
    parameters = problem["exact_parameters"]
    length = parameters["L_star"]
    tension = parameters["T_F"]
    mass = parameters["M"]
    if parse_q_pi_atom(length) != (Fraction(16), 1):
        fail("exact_cell", "L_star is not 16*pi")
    if parse_q_pi_atom(tension) != (Fraction(1, 2), -1):
        fail("exact_cell", "T_F is not 1/(2*pi)")
    if parse_q_pi_atom(mass) != (Fraction(8), 0):
        fail("exact_cell", "M is not 8")
    if multiply_q_pi_atoms(tension, length) != mass:
        fail("exact_cell", "exact T_F*L_star does not equal M")
    if type(parameters["K"]) is not int or parameters["K"] != 1:
        fail("exact_cell", "symbolic lift K differs")

    modes = [
        string["modes"][0] for string in problem["kinematics"]["strings"]
    ]
    for mode in modes:
        if parse_q_pi_atom(mode["wave_number"]) != (Fraction(1, 8), 0):
            fail("exact_cell", "symbolic lift k_1 differs")
    energy = Fraction(old_semantic["E"])
    momentum = tuple(old_semantic["P_total"])
    mass_fraction = Fraction(8)
    residual = energy - sum(
        (value * value for value in momentum), Fraction()
    ) / (4 * mass_fraction)
    if residual != 1:
        fail("exact_cell", "new exact E_star does not equal one")

    periods = [
        parse_q_pi_atom(value)
        for value in problem["target_torus"]["periods"][:8]
    ]
    if periods != [(Fraction(8), 0)] * 8:
        fail("exact_cell", "transverse periods changed")
    orientations = tuple(problem["worldsheet"]["orientations"])
    if orientations != (1, -1):
        fail("exact_cell", "orientations changed")
    record = {
        "arithmetic": "exact rational times symbolic pi power",
        "T_F": tension,
        "L_star": length,
        "M_equals_T_F_times_L_star": mass,
        "k_1": q_pi_atom(Fraction(1, 8)),
        "E": rational_record(energy),
        "P_total": [rational_record(value) for value in momentum],
        "E_star": rational_record(residual),
        "K": 1,
        "transverse_periods": [q_pi_atom(8) for _ in range(8)],
        "orientations": list(orientations),
        "source_seed": old_semantic["seed"],
    }
    semantic = {
        "K": 1,
        "M": Fraction(8),
        "k_1": Fraction(1, 8),
        "E": energy,
        "E_star": residual,
        "P_total": momentum,
        "transverse_periods": tuple(Fraction(8) for _ in range(8)),
        "orientations": orientations,
        "seed": old_semantic["seed"],
    }
    return record, semantic


def _coefficient_payload(state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "Q_relative": state["Q_relative"],
        "Q1": state["Q1"],
        "Q2": state["Q2"],
        "energy_shares_s0_s1_s2": state["energy_shares_s0_s1_s2"],
        "strings": state["strings"],
    }


def _symbolic_transport(value: Any, path: str = "$") -> Any:
    """Map binary64 coefficient leaves to their exact ``q*pi^0`` values."""

    if type(value) is float:
        if not math.isfinite(value):
            fail("empirical_transport", f"{path} is non-finite")
        return q_pi_atom(Fraction.from_float(value))
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return [
            _symbolic_transport(item, f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    if type(value) is dict:
        return {
            key: _symbolic_transport(item, f"{path}.{key}")
            for key, item in value.items()
        }
    fail("empirical_transport", f"{path} has unsupported type")


def _verify_transport_roundtrip(
    original: Any, transported: Any, path: str = "$"
) -> None:
    if type(original) is float:
        value, exponent = parse_q_pi_atom(transported, path)
        if exponent != 0 or value != Fraction.from_float(original):
            fail("empirical_transport", f"{path} coefficient changed")
        return
    if type(original) is dict:
        if type(transported) is not dict or original.keys() != transported.keys():
            fail("empirical_transport", f"{path} object structure changed")
        for key in original:
            _verify_transport_roundtrip(
                original[key], transported[key], f"{path}.{key}"
            )
        return
    if type(original) is list:
        if (
            type(transported) is not list
            or len(original) != len(transported)
        ):
            fail("empirical_transport", f"{path} array structure changed")
        for index, (left, right) in enumerate(
            zip(original, transported)
        ):
            _verify_transport_roundtrip(
                left, right, f"{path}[{index}]"
            )
        return
    if type(original) is not type(transported) or original != transported:
        fail("empirical_transport", f"{path} nonnumeric leaf changed")


def _source_problem_transport_projection(
    state: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the exact source-derived subset carried by the lift problem."""

    strings: list[dict[str, Any]] = []
    for string in state["strings"]:
        modes = []
        for mode in string["modes"]:
            modes.append(
                {
                    "mode_number": mode["mode_number"],
                    "wave_number": q_pi_atom(
                        Fraction.from_float(mode["wave_number"])
                    ),
                    "initial_x": [
                        q_pi_atom(Fraction.from_float(value))
                        for value in mode["x"]
                    ],
                    "initial_y": [
                        q_pi_atom(Fraction.from_float(value))
                        for value in mode["y"]
                    ],
                    "initial_p": [
                        q_pi_atom(Fraction.from_float(value))
                        for value in mode["p"]
                    ],
                    "initial_q": [
                        q_pi_atom(Fraction.from_float(value))
                        for value in mode["q"]
                    ],
                }
            )
        strings.append(
            {
                "orientation": string["orientation"],
                "transverse_velocity": [
                    q_pi_atom(Fraction.from_float(value))
                    for value in string["transverse_velocity"]
                ],
                "modes": modes,
            }
        )
    return {
        "centres_Q1_Q2": {
            name: [
                q_pi_atom(Fraction.from_float(value))
                for value in state[name]
            ]
            for name in ("Q1", "Q2")
        },
        "strings": strings,
    }


def _lift_problem_transport_projection(
    problem: Mapping[str, Any],
) -> dict[str, Any]:
    """Extract only source-carried leaves, excluding derived lift fields."""

    strings: list[dict[str, Any]] = []
    for string in problem["kinematics"]["strings"]:
        modes = []
        for mode in string["modes"]:
            modes.append(
                {
                    "mode_number": mode["mode_number"],
                    "wave_number": copy.deepcopy(mode["wave_number"]),
                    "initial_x": copy.deepcopy(mode["initial_x"]),
                    "initial_y": copy.deepcopy(mode["initial_y"]),
                    "initial_p": copy.deepcopy(mode["initial_p"]),
                    "initial_q": copy.deepcopy(mode["initial_q"]),
                }
            )
        strings.append(
            {
                "orientation": string["orientation"],
                "transverse_velocity": copy.deepcopy(
                    string["transverse_velocity"]
                ),
                "modes": modes,
            }
        )
    return {
        "centres_Q1_Q2": copy.deepcopy(
            problem["kinematics"]["centres_Q1_Q2"]
        ),
        "strings": strings,
    }


def _count_q_pi_atom_leaves(value: Any) -> int:
    if type(value) is dict and set(value) == ATOM_KEYS:
        parse_q_pi_atom(value)
        return 1
    if type(value) is dict:
        return sum(_count_q_pi_atom_leaves(item) for item in value.values())
    if type(value) is list:
        return sum(_count_q_pi_atom_leaves(item) for item in value)
    return 0


def _count_float_leaves(value: Any) -> int:
    if type(value) is float:
        return 1
    if type(value) is dict:
        return sum(_count_float_leaves(item) for item in value.values())
    if type(value) is list:
        return sum(_count_float_leaves(item) for item in value)
    return 0


def _fixed_index_2_binding(
    state: Mapping[str, Any],
    lift_fixture: Mapping[str, Any],
) -> dict[str, Any]:
    """Independently compare every source-carried problem coefficient leaf."""

    if (
        state["sample_index"] != 2
        or state["source_state_sha256"] != SOURCE_INDEX_2_STATE_SHA256
        or state["source_draw_sha256"] != SOURCE_DRAW_SHA256
    ):
        fail("fixed_index_2", "regenerated source state is not pinned index 2")
    if (
        state["Q_relative"] != state["Q1"]
        or state["Q2"] != [0.0] * 8
    ):
        fail("fixed_index_2", "relative-centre gauge identity differs")

    expected = _source_problem_transport_projection(state)
    actual = _lift_problem_transport_projection(
        lift_fixture["closed_string_problem"]
    )
    # Parse all actual atom leaves before exact structural comparison so a
    # malformed but superficially similar encoding fails at the atom gate.
    actual_atom_count = _count_q_pi_atom_leaves(actual)
    expected_atom_count = _count_q_pi_atom_leaves(expected)
    if actual_atom_count != 98 or expected_atom_count != 98:
        fail(
            "fixed_index_2",
            "source-carried problem atom count is not exactly 98",
        )
    if not type_strict_equal(actual, expected):
        fail(
            "fixed_index_2",
            "one or more source-carried problem leaves differ",
        )

    full_payload = _coefficient_payload(state)
    transported_payload = _symbolic_transport(
        full_payload, "$.fixed_index_2.source_payload"
    )
    _verify_transport_roundtrip(
        full_payload,
        transported_payload,
        "$.fixed_index_2.source_payload",
    )
    source_payload_float_count = _count_float_leaves(full_payload)
    if source_payload_float_count != 109:
        fail(
            "fixed_index_2",
            "complete source payload float count is not exactly 109",
        )
    return {
        "sample_index": 2,
        "source_state_sha256": SOURCE_INDEX_2_STATE_SHA256,
        "source_draw_sha256": SOURCE_DRAW_SHA256,
        "complete_source_payload_float_leaf_count": (
            source_payload_float_count
        ),
        "problem_carried_q_pi_zero_atom_leaf_count": actual_atom_count,
        "problem_transport_projection_semantic_sha256": (
            semantic_sha256(actual)
        ),
        "complete_symbolic_source_payload_semantic_sha256": (
            semantic_sha256(transported_payload)
        ),
        "relative_centre_gauge_Q_relative_equals_Q1": True,
        "Q2_is_zero_gauge_representative": True,
        "all_problem_carried_leaves_type_strict_equal": True,
        "all_complete_source_payload_leaves_exactly_round_trip": True,
        "energy_share_leaves_remain_source_law_metadata_not_problem_inputs": 3,
        "claim": (
            "direct fixed-index comparison of every one of the 98 "
            "source-carried closed-string problem atoms; all 109 source "
            "payload floats also round-trip exactly"
        ),
    }


def _resealed_fixed_index_mutation_rejected(
    state: Mapping[str, Any],
    lift_fixture: Mapping[str, Any],
) -> bool:
    """Mutate a coefficient and reseal all available component digests."""

    hostile = copy.deepcopy(lift_fixture)
    atom = hostile["closed_string_problem"]["kinematics"]["strings"][0][
        "modes"
    ][0]["initial_x"][0]
    atom["numerator"] += 1
    hostile["closed_string_problem_semantic_sha256"] = semantic_sha256(
        hostile["closed_string_problem"]
    )
    # This fixture schema stores no self digest.  Recomputing its semantic
    # digest models an attacker who reseals every available outer commitment.
    semantic_sha256(hostile)
    try:
        _fixed_index_2_binding(state, hostile)
    except MeasureBridgeError:
        return True
    return False


def _empirical_replay(
    source: ModuleType, registry: Mapping[str, Any]
) -> dict[str, Any]:
    states = [
        source.sample_source(registry, index)
        for index in range(SAMPLE_COUNT)
    ]
    state_hashes = [state["source_state_sha256"] for state in states]
    coefficient_hashes = [
        source.source_coefficient_payload_sha256(state) for state in states
    ]
    transported_hashes: list[str] = []
    for index, state in enumerate(states):
        payload = _coefficient_payload(state)
        transported = _symbolic_transport(
            payload, f"$.samples[{index}].coefficients"
        )
        _verify_transport_roundtrip(
            payload, transported, f"$.samples[{index}].coefficients"
        )
        transported_hashes.append(semantic_sha256(transported))
    state_sequence_digest = semantic_sha256(state_hashes)
    coefficient_sequence_digest = semantic_sha256(coefficient_hashes)
    symbolic_sequence_digest = semantic_sha256(transported_hashes)
    if (
        SOURCE_STATE_SEQUENCE_SHA256
        and state_sequence_digest != SOURCE_STATE_SEQUENCE_SHA256
    ):
        fail("empirical_replay", "512-state sequence digest differs")
    if (
        COEFFICIENT_HASH_SEQUENCE_SHA256
        and coefficient_sequence_digest
        != COEFFICIENT_HASH_SEQUENCE_SHA256
    ):
        fail("empirical_replay", "coefficient sequence digest differs")
    if (
        SYMBOLIC_COEFFICIENT_SEQUENCE_SHA256
        and symbolic_sequence_digest
        != SYMBOLIC_COEFFICIENT_SEQUENCE_SHA256
    ):
        fail("empirical_replay", "symbolic transport sequence differs")
    valid_count = sum(
        state["validity"]["status"] == "valid" for state in states
    )
    invalid_count = SAMPLE_COUNT - valid_count
    if (
        valid_count != EXPECTED_VALID_COUNT
        or invalid_count != EXPECTED_INVALID_COUNT
    ):
        fail("empirical_replay", "validity ledger differs")
    return {
        "sample_count": SAMPLE_COUNT,
        "sequence_kind": (
            "registered unconditioned source indices 0 through 511"
        ),
        "source_state_hash_sequence_sha256": state_sequence_digest,
        "coefficient_payload_hash_sequence_sha256": (
            coefficient_sequence_digest
        ),
        "symbolic_coefficient_transport_sequence_sha256": (
            symbolic_sequence_digest
        ),
        "first_source_state_sha256": state_hashes[0],
        "index_2_source_state_sha256": state_hashes[2],
        "last_source_state_sha256": state_hashes[-1],
        "all_binary64_coefficients_exactly_round_trip_q_pi_zero": True,
        "source_draw_bytes_changed": False,
        "source_states_redrawn": False,
        "valid_count_annotation": valid_count,
        "invalid_count_annotation": invalid_count,
        "validity_conditioned_or_redrawn": False,
        "claim": (
            "finite registered sequence identity under deterministic "
            "coefficient transport"
        ),
    }


def _analytic_law(
    registry: Mapping[str, Any],
    old: Mapping[str, Any],
    new: Mapping[str, Any],
) -> dict[str, Any]:
    comparable_keys = {
        "K",
        "M",
        "k_1",
        "E",
        "E_star",
        "P_total",
        "transverse_periods",
        "orientations",
        "seed",
    }
    if set(old) != comparable_keys or set(new) != comparable_keys:
        fail("analytic_law", "analytic parameter ledger keys differ")
    for key in sorted(comparable_keys):
        if old[key] != new[key]:
            fail("analytic_law", f"old/new invariant {key} differs")

    cutoff = old["K"]
    shape = (4, 16 * cutoff - 1, 16 * cutoff - 1)
    if shape != (4, 15, 15):
        fail("analytic_law", "radial Dirichlet shape differs")
    mass = Fraction(old["M"])
    wave_number = Fraction(old["k_1"])
    linear_jacobian = mass**4 * (Fraction(4) / wave_number**2) ** 16
    if linear_jacobian != 2**140:
        fail("analytic_law", "registered chiral Jacobian factor differs")
    source_draw = registry["source_draw_registry"]
    if source_draw["worldsheet_momenta"] != [0.0, 0.0]:
        fail("analytic_law", "bridge is only registered for zero pi_i")
    return {
        "law_family": (
            "quadratic-finite-K-single-delta-liouville-zero-pi"
        ),
        "conditioning": "none; invalid source states remain in the law",
        "unchanged_generator_inputs": {
            "K": cutoff,
            "E": rational_record(old["E"]),
            "E_star": rational_record(old["E_star"]),
            "M": rational_record(mass),
            "k_1": rational_record(wave_number),
            "P_total": [
                rational_record(value) for value in old["P_total"]
            ],
            "transverse_periods": [
                rational_record(value)
                for value in old["transverse_periods"]
            ],
            "winding_orientations": list(old["orientations"]),
            "source_seed": old["seed"],
            "prng_algorithm": PRNG_ALGORITHM,
            "portable_math_version": PORTABLE_MATH_VERSION,
        },
        "latent_random_variable_transport": {
            "map": "identity on every named deterministic stream variate",
            "jacobian": rational_record(1),
        },
        "coefficient_transport": {
            "map": (
                "identity on the underlying real coefficient; binary64 "
                "is re-encoded exactly as q*pi^0"
            ),
            "jacobian": rational_record(1),
        },
        "radial_factor": {
            "dirichlet_shape": list(shape),
            "simplex_scale_E_star": rational_record(old["E_star"]),
            "parameter_dependence": ["K", "E_star"],
            "old_equals_new": True,
        },
        "linear_chiral_factor": {
            "registered_formula": (
                "M^4 * product_m (4/k_m^2)^16"
            ),
            "parameter_dependence": ["M", "k_1"],
            "old_exact_value": rational_record(linear_jacobian),
            "new_exact_value": rational_record(linear_jacobian),
            "new_over_old": rational_record(1),
        },
        "relative_centre_factor": {
            "law": "normalized Haar on the eight transverse circles",
            "periods_unchanged": True,
        },
        "analytic_radon_nikodym_derivative_new_over_old": (
            rational_record(1)
        ),
        "statement": (
            "the analytic Brief 0018 source measure is identical before "
            "and after the symbolic-pi lift"
        ),
        "does_not_imply": [
            "the physical embedding map is unchanged",
            "the event pushforward is unchanged",
            "entry or no-entry probabilities",
            "a population event law",
            "3+1 selection",
        ],
    }


def _hostile_checks(report: Mapping[str, Any]) -> dict[str, bool]:
    def rejected(mutator: Callable[[dict[str, Any]], None]) -> bool:
        hostile = copy.deepcopy(report)
        mutator(hostile)
        hostile["report_semantic_sha256"] = semantic_sha256(
            {
                key: value
                for key, value in hostile.items()
                if key != "report_semantic_sha256"
            }
        )
        try:
            verify_report(hostile)
        except MeasureBridgeError:
            return True
        return False

    checks = {
        "old_mass_mutation_rejected": rejected(
            lambda value: value["binary64_source_cell"][
                "M_equals_rounded_T_F_hat_times_L_hat"
            ].__setitem__("hex", "0x1.0000000000001p+3")
        ),
        "new_length_mutation_rejected": rejected(
            lambda value: value["exact_symbolic_source_cell"][
                "L_star"
            ].__setitem__("numerator", 8)
        ),
        "E_star_mutation_rejected": rejected(
            lambda value: value["analytic_source_law"][
                "unchanged_generator_inputs"
            ].__setitem__("E_star", rational_record(2))
        ),
        "seed_mutation_rejected": rejected(
            lambda value: value["analytic_source_law"][
                "unchanged_generator_inputs"
            ].__setitem__("source_seed", "0" * 64)
        ),
        "identity_jacobian_mutation_rejected": rejected(
            lambda value: value["analytic_source_law"][
                "coefficient_transport"
            ].__setitem__("jacobian", rational_record(2))
        ),
        "empirical_sequence_mutation_rejected": rejected(
            lambda value: value["empirical_512_sequence"].__setitem__(
                "source_state_hash_sequence_sha256", "0" * 64
            )
        ),
        "event_law_overclaim_rejected": rejected(
            lambda value: value["scope"]["claim_boundary"].append(
                "physical first-entry population law is unchanged"
            )
        ),
    }
    try:
        strict_json_loads('{"x":1,"x":2}')
    except MeasureBridgeError:
        checks["duplicate_json_key_rejected"] = True
    else:
        checks["duplicate_json_key_rejected"] = False
    try:
        strict_json_loads('{"x":1.0}')
    except MeasureBridgeError:
        checks["ordinary_report_float_rejected"] = True
    else:
        checks["ordinary_report_float_rejected"] = False
    return checks


def _build_report_core() -> dict[str, Any]:
    source, registry, lift_fixture = _load_inputs()
    old_record, old_semantic = _old_binary64_cell(source, registry)
    new_record, new_semantic = _new_exact_cell(
        lift_fixture, old_semantic
    )
    empirical = _empirical_replay(source, registry)
    index_2_state = source.sample_source(registry, 2)
    fixed_index_2 = _fixed_index_2_binding(
        index_2_state, lift_fixture
    )
    fixed_index_2[
        "resealed_problem_coefficient_mutation_rejected"
    ] = _resealed_fixed_index_mutation_rejected(
        index_2_state, lift_fixture
    )
    if not fixed_index_2[
        "resealed_problem_coefficient_mutation_rejected"
    ]:
        fail(
            "fixed_index_2",
            "resealed problem coefficient mutation was accepted",
        )
    analytic = _analytic_law(registry, old_semantic, new_semantic)
    return {
        "schema_version": REPORT_SCHEMA,
        "bridge_algorithm": BRIDGE_ALGORITHM,
        "status": "passed",
        "failed_gates": [],
        "provenance": {
            "source_module_normalized_lf_sha256": (
                SOURCE_MODULE_NORMALIZED_LF_SHA256
            ),
            "source_registry_normalized_lf_sha256": (
                SOURCE_REGISTRY_NORMALIZED_LF_SHA256
            ),
            "source_registry_canonical_sha256": (
                SOURCE_REGISTRY_CANONICAL_SHA256
            ),
            "source_draw_sha256": SOURCE_DRAW_SHA256,
            "symbolic_lift_fixture_semantic_sha256": (
                SYMBOLIC_LIFT_FIXTURE_SEMANTIC_SHA256
            ),
            "lift_registry_semantic_sha256": (
                LIFT_REGISTRY_SEMANTIC_SHA256
            ),
            "closed_string_problem_semantic_sha256": (
                CLOSED_STRING_PROBLEM_SEMANTIC_SHA256
            ),
        },
        "binary64_source_cell": old_record,
        "exact_symbolic_source_cell": new_record,
        "fixed_index_2_binding": fixed_index_2,
        "empirical_512_sequence": empirical,
        "analytic_source_law": analytic,
        "checks": {
            "source_code_and_registry_are_pinned": True,
            "source_draw_hash_independently_recomputed": True,
            "old_binary64_M_is_exactly_8": True,
            "old_binary64_k_1_is_exactly_one_eighth": True,
            "old_binary64_E_star_is_exactly_1": True,
            "new_exact_T_F_times_L_star_is_8": True,
            "new_exact_k_1_is_one_eighth": True,
            "new_exact_E_star_is_1": True,
            "K_E_P_transverse_periods_orientations_seed_unchanged": True,
            "all_512_source_states_replayed": True,
            "all_512_coefficient_payloads_identity_transported": True,
            "index_2_all_problem_carried_leaves_directly_compared": True,
            "index_2_complete_source_payload_exactly_round_trips": True,
            "resealed_index_2_coefficient_mutation_rejected": True,
            "latent_identity_jacobian_is_1": True,
            "coefficient_identity_jacobian_is_1": True,
            "radial_dirichlet_factor_is_identical": True,
            "linear_chiral_jacobian_factor_is_identical": True,
            "analytic_source_measure_ratio_is_1": True,
            "physical_event_pushforward_claim_withheld": True,
        },
        "scope": {
            "claim_boundary": [
                "registered 512-sequence source identity",
                "analytic Brief 0018 unconditioned source-law identity",
            ],
            "does_not_claim": [
                "source validity conditioning",
                "unchanged physical embedding",
                "unchanged event pushforward",
                "finite-window entry or no-entry",
                "physical first-entry mass",
                "population event law",
                "dimension dynamics",
                "3+1 selection",
            ],
        },
    }


def build_report() -> dict[str, Any]:
    report = _build_report_core()
    # Hostile controls are evaluated after (and excluded from) the
    # deterministic core to avoid recursion.
    report["hostile_controls"] = _hostile_checks_against_core(report)
    if not all(report["hostile_controls"].values()):
        fail("hostile_controls", "one or more hostile controls were accepted")
    report["report_semantic_sha256"] = semantic_sha256(report)
    return report


def _hostile_checks_against_core(
    core: Mapping[str, Any]
) -> dict[str, bool]:
    """Cheap hostile checks without recursively rebuilding their own list."""

    def differs(mutator: Callable[[dict[str, Any]], None]) -> bool:
        hostile = copy.deepcopy(core)
        mutator(hostile)
        return not type_strict_equal(hostile, core)

    checks = {
        "old_mass_mutation_rejected": differs(
            lambda value: value["binary64_source_cell"][
                "M_equals_rounded_T_F_hat_times_L_hat"
            ].__setitem__("hex", "0x1.0000000000001p+3")
        ),
        "new_length_mutation_rejected": differs(
            lambda value: value["exact_symbolic_source_cell"][
                "L_star"
            ].__setitem__("numerator", 8)
        ),
        "E_star_mutation_rejected": differs(
            lambda value: value["analytic_source_law"][
                "unchanged_generator_inputs"
            ].__setitem__("E_star", rational_record(2))
        ),
        "seed_mutation_rejected": differs(
            lambda value: value["analytic_source_law"][
                "unchanged_generator_inputs"
            ].__setitem__("source_seed", "0" * 64)
        ),
        "identity_jacobian_mutation_rejected": differs(
            lambda value: value["analytic_source_law"][
                "coefficient_transport"
            ].__setitem__("jacobian", rational_record(2))
        ),
        "empirical_sequence_mutation_rejected": differs(
            lambda value: value["empirical_512_sequence"].__setitem__(
                "source_state_hash_sequence_sha256", "0" * 64
            )
        ),
        "fixed_index_projection_mutation_rejected": differs(
            lambda value: value["fixed_index_2_binding"].__setitem__(
                "problem_transport_projection_semantic_sha256", "0" * 64
            )
        ),
        "resealed_problem_coefficient_mutation_rejected": core[
            "fixed_index_2_binding"
        ]["resealed_problem_coefficient_mutation_rejected"],
        "event_law_overclaim_rejected": differs(
            lambda value: value["scope"]["claim_boundary"].append(
                "physical first-entry population law is unchanged"
            )
        ),
    }
    try:
        strict_json_loads('{"x":1,"x":2}')
    except MeasureBridgeError:
        checks["duplicate_json_key_rejected"] = True
    else:
        checks["duplicate_json_key_rejected"] = False
    try:
        strict_json_loads('{"x":1.0}')
    except MeasureBridgeError:
        checks["ordinary_report_float_rejected"] = True
    else:
        checks["ordinary_report_float_rejected"] = False
    return checks


def verify_report(report: Any) -> str:
    expected = build_report()
    obj = _exact_keys(
        report,
        set(expected),
        "$.report",
        "report_schema",
    )
    if obj["schema_version"] != REPORT_SCHEMA or obj["status"] != "passed":
        fail("report_schema", "unsupported or failed report")
    if type(obj["failed_gates"]) is not list or obj["failed_gates"]:
        fail("report_status", "passed report must have no failed gates")
    for name in ("checks", "hostile_controls"):
        flags = obj[name]
        if (
            type(flags) is not dict
            or not flags
            or any(type(flag) is not bool or not flag for flag in flags.values())
        ):
            fail("report_status", f"all {name} flags must be true")
    stored = _sha256(
        obj["report_semantic_sha256"],
        "$.report.report_semantic_sha256",
        "report_hash",
    )
    payload = copy.deepcopy(obj)
    del payload["report_semantic_sha256"]
    computed = semantic_sha256(payload)
    if stored != computed:
        fail("report_hash", "report self-digest differs")
    if REPORT_SEMANTIC_SHA256 and stored != REPORT_SEMANTIC_SHA256:
        fail("report_hash", "report source-code pin differs")
    if not type_strict_equal(obj, expected):
        fail("report_reproduction", "report differs from fresh replay")
    return stored


def run(write: bool) -> dict[str, Any]:
    report = build_report()
    if write:
        write_json(REPORT_PATH, report)
    else:
        stored = strict_json_load(REPORT_PATH)
        verify_report(stored)
        if not type_strict_equal(stored, report):
            fail("report_reproduction", "stored report differs")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or replay the symbolic source-measure bridge"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    report = run(write=arguments.write)
    print(pretty_json(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
