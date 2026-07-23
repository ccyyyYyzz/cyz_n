#!/usr/bin/env python3
"""Independent replay of the Brief 0019 symbolic-pi closed-string lift.

This module deliberately does not import the symbolic lift generator, the
Arb jet evaluator, or any solver.  Its only project dependency is
``source_binding_replayer``: that module independently regenerates source
index 2 from the Brief 0018 registry.  Starting from that regenerated state,
this file separately rebuilds the complete symbolic registry and closed-
string problem, replays their exact algebra, and compares them with the
stored lift fixture.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import source_binding_replayer as source_replay


ARTIFACT_DIR = Path(__file__).resolve().parent
SOURCE_REGISTRY_PATH = ARTIFACT_DIR.parent / "0018" / "source_registry.json"
SOURCE_FIXTURE_PATH = ARTIFACT_DIR / "source_state_bridge_fixture.json"
LIFT_FIXTURE_PATH = ARTIFACT_DIR / "symbolic_pi_lift_fixture.json"
REPORT_PATH = ARTIFACT_DIR / "symbolic_pi_lift_replayer_report.json"

FIXTURE_SCHEMA = "cyz-brief-0019-symbolic-pi-lift-fixture-v1"
REGISTRY_SCHEMA = "cyz-brief-0019-symbolic-pi-lift-registry-v1"
PROBLEM_SCHEMA = "cyz-brief-0019-symbolic-pi-closed-string-problem-v1"
SCALAR_SCHEMA = "cyz-canonical-rational-times-pi-power-v1"
REPORT_SCHEMA = (
    "cyz-brief-0019-independent-symbolic-pi-lift-replayer-report-v1"
)
EQUATION_FAMILY = "f1-normalized-closed-string-k1-v1"

SOURCE_REGISTRY_SHA256 = (
    "35d31a64e45d9a3ea9cc346e19d8bc5d8d40d1f9eac68eb07385fb291aed8cdb"
)
SOURCE_DRAW_SHA256 = (
    "4bc0d8eadef9ad8aea8752f25e105127311b83edebc99ebe1b1b7561999e1bd4"
)
SOURCE_STATE_SHA256 = (
    "1c671b6bf8e737d238c21de8b0f694a57b8bfab7006ebb1401136176567f118c"
)
SOURCE_FIXTURE_SHA256 = (
    "5af600527155e1c1dbd68b8e531aa1a640e4ee2edb8317f46334ac6b219dee60"
)
LEGACY_PROBLEM_SHA256 = (
    "1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca"
)
LIFT_REGISTRY_SHA256 = (
    "c80acb64eeeb3133dff4422fc798f5b75c6feb52cf32502888cac452e2d210a1"
)
CLOSED_STRING_PROBLEM_SHA256 = (
    "3bb6599f211c26d98ecba2077051ad9d0339daf96d580a6399cc5a1ba7f030e0"
)
SOURCE_EXACT_STATE_SHA256 = (
    "10fd59b2684e051c44e9a277325e5f051ed1a6049ca8c57a5a2b03728a6f188b"
)
SOURCE_BINARY64_STATE_SHA256 = (
    "a4aca7850b9c110ae778387a3c9ba05f68c02566dcf533f2dacd6a75164e8303"
)

PI_EXPONENT_MIN = -16
PI_EXPONENT_MAX = 16
ATOM_KEYS = {"numerator", "denominator", "pi_exponent"}
VARIABLE_ORDER = ("u1", "u2", "t")


class SymbolicLiftReplayError(ValueError):
    """One independent replay gate failed."""

    def __init__(self, gate: str, message: str):
        super().__init__(f"{gate}: {message}")
        self.gate = gate
        self.message = message


def fail(gate: str, message: str) -> None:
    raise SymbolicLiftReplayError(gate, message)


def _integer(value: Any, path: str) -> int:
    if type(value) is not int:
        fail("type", f"{path} must be an integer; Booleans are forbidden")
    return value


def _object(value: Any, path: str) -> Mapping[str, Any]:
    if type(value) is not dict:
        fail("type", f"{path} must be an object")
    return value


def _exact_keys(
    value: Any, expected: set[str], path: str, gate: str = "schema"
) -> Mapping[str, Any]:
    obj = _object(value, path)
    missing = sorted(expected - set(obj))
    extra = sorted(set(obj) - expected)
    if missing or extra:
        fail(gate, f"{path} keys differ; missing={missing}, extra={extra}")
    return obj


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


def _reject_constant(token: str) -> None:
    fail("strict_json", f"non-finite JSON token {token!r} is forbidden")


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except SymbolicLiftReplayError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        fail("strict_json", str(error))
    raise AssertionError("unreachable")


def strict_json_load(path: Path) -> Any:
    return strict_json_loads(path.read_text(encoding="utf-8"))


def _assert_float_free(value: Any, path: str = "$") -> None:
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                fail("canonical_json", f"{path} has a non-string key")
            _assert_float_free(item, f"{path}.{key}")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _assert_float_free(item, f"{path}[{index}]")
        return
    if value is None or type(value) in {str, int, bool}:
        return
    fail("canonical_json", f"{path} contains {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    _assert_float_free(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def semantic_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def pretty_json(value: Any) -> str:
    _assert_float_free(value)
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


def normalized_lf_sha256(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


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


def make_atom(
    coefficient: Fraction | int,
    pi_exponent: int = 0,
) -> dict[str, int]:
    q = Fraction(coefficient)
    exponent = _integer(pi_exponent, "$.pi_exponent")
    if q == 0:
        exponent = 0
    if not PI_EXPONENT_MIN <= exponent <= PI_EXPONENT_MAX:
        fail("symbolic_atom", "pi exponent lies outside the versioned bound")
    return {
        "numerator": q.numerator,
        "denominator": q.denominator,
        "pi_exponent": exponent,
    }


def parse_atom(value: Any, path: str = "$atom") -> tuple[Fraction, int]:
    atom = _exact_keys(value, ATOM_KEYS, path, "symbolic_atom")
    numerator = _integer(atom["numerator"], f"{path}.numerator")
    denominator = _integer(atom["denominator"], f"{path}.denominator")
    exponent = _integer(atom["pi_exponent"], f"{path}.pi_exponent")
    if denominator <= 0:
        fail("symbolic_atom", f"{path}.denominator must be positive")
    if math.gcd(abs(numerator), denominator) != 1:
        fail("symbolic_atom", f"{path} rational is not reduced")
    if numerator == 0 and (denominator != 1 or exponent != 0):
        fail("symbolic_atom", f"{path} zero is not canonical")
    if not PI_EXPONENT_MIN <= exponent <= PI_EXPONENT_MAX:
        fail("symbolic_atom", f"{path} exponent is outside the grammar")
    return Fraction(numerator, denominator), exponent


def multiply_atoms(*values: Mapping[str, Any]) -> dict[str, int]:
    coefficient = Fraction(1)
    exponent = 0
    for index, value in enumerate(values):
        q, power = parse_atom(value, f"$multiply[{index}]")
        coefficient *= q
        exponent += power
    return make_atom(coefficient, exponent)


def atom_power(value: Mapping[str, Any], exponent: int) -> dict[str, int]:
    power = _integer(exponent, "$power.exponent")
    coefficient, pi_power = parse_atom(value, "$power.base")
    if coefficient == 0 and power < 0:
        fail("symbolic_atom", "negative power of zero")
    return make_atom(coefficient**power, pi_power * power)


def parse_dyadic(value: Any, path: str = "$dyadic") -> Fraction:
    item = _exact_keys(value, {"numerator", "exponent"}, path, "dyadic")
    numerator = _integer(item["numerator"], f"{path}.numerator")
    exponent = _integer(item["exponent"], f"{path}.exponent")
    if exponent < 0:
        fail("dyadic", f"{path}.exponent must be nonnegative")
    if numerator == 0 and exponent != 0:
        fail("dyadic", f"{path} zero is not canonical")
    if numerator != 0 and exponent > 0 and numerator % 2 == 0:
        fail("dyadic", f"{path} is not reduced")
    return Fraction(numerator, 1 << exponent)


def dyadic_atom(value: Any, path: str = "$dyadic") -> dict[str, int]:
    return make_atom(parse_dyadic(value, path))


def binary64_atom(value: Any, path: str) -> dict[str, int]:
    if type(value) is not float or not math.isfinite(value):
        fail("binary64", f"{path} must be a finite binary64")
    numerator, denominator = value.as_integer_ratio()
    return make_atom(Fraction(numerator, denominator))


def _convert_dyadic_vector(
    values: Any, length: int, path: str
) -> list[dict[str, int]]:
    if type(values) is not list or len(values) != length:
        fail("source_identity", f"{path} must have length {length}")
    return [
        dyadic_atom(value, f"{path}[{index}]")
        for index, value in enumerate(values)
    ]


def _independent_source_material() -> dict[str, Any]:
    registry = source_replay.strict_registry_load(SOURCE_REGISTRY_PATH)
    source_fixture = source_replay.strict_fixture_load(SOURCE_FIXTURE_PATH)
    binding = source_replay.replay_binding_objects(registry, source_fixture)
    if (
        binding["registry_canonical_sha256"] != SOURCE_REGISTRY_SHA256
        or binding["source_draw_sha256"] != SOURCE_DRAW_SHA256
        or binding["fixture_semantic_sha256"] != SOURCE_FIXTURE_SHA256
        or binding["physical_problem_semantic_sha256"]
        != LEGACY_PROBLEM_SHA256
        or binding["first_valid_index"] != 2
    ):
        fail("source_replay", "independent source-binding commitments differ")

    state = source_replay.independently_generate_source(registry, 2)
    replay = source_replay.validate_source_sample(state, registry)
    if (
        replay["state_core_sha256"] != SOURCE_STATE_SHA256
        or replay["validity"]["status"] != "valid"
    ):
        fail("source_replay", "independent index-2 source does not replay")
    exact_state = source_replay.exact_dyadic_tree(state)
    encoded_state = source_replay.encode_binary64_tree(state)
    if semantic_sha256(exact_state) != SOURCE_EXACT_STATE_SHA256:
        fail("source_replay", "exact source-state projection hash differs")
    if semantic_sha256(encoded_state) != SOURCE_BINARY64_STATE_SHA256:
        fail("source_replay", "binary64 source-state hash differs")
    return {
        "registry": registry,
        "source_fixture": source_fixture,
        "binding": binding,
        "state": state,
        "exact_state": exact_state,
        "encoded_state": encoded_state,
    }


def _upstream_provenance(material: Mapping[str, Any]) -> dict[str, Any]:
    state = material["state"]
    return {
        "source_bridge_fixture_semantic_sha256": SOURCE_FIXTURE_SHA256,
        "legacy_cut_open_physical_problem_semantic_sha256": (
            LEGACY_PROBLEM_SHA256
        ),
        "legacy_problem_role": (
            "provenance_only_not_a_closed_string_problem_identifier"
        ),
        "source_registry_canonical_sha256": SOURCE_REGISTRY_SHA256,
        "source_draw_sha256": SOURCE_DRAW_SHA256,
        "source_sample_index": 2,
        "source_sample_schema": state["schema_version"],
        "source_state_sha256": SOURCE_STATE_SHA256,
        "complete_exact_dyadic_projection_semantic_sha256": (
            semantic_sha256(material["exact_state"])
        ),
        "complete_serialized_state_semantic_sha256": (
            semantic_sha256(material["encoded_state"])
        ),
    }


def rebuild_lift_registry(
    material: Mapping[str, Any],
) -> dict[str, Any]:
    zero = make_atom(0)
    one = make_atom(1)
    length = make_atom(16, 1)
    tension = make_atom(Fraction(1, 2), -1)
    mass = make_atom(8)
    k_one = make_atom(Fraction(1, 8))
    phase_one = make_atom(2, 1)
    return {
        "schema_version": REGISTRY_SCHEMA,
        "registry_id": "index2-symbolic-pi-closed-string-lift-v1",
        "scalar_grammar": {
            "schema_version": SCALAR_SCHEMA,
            "atom_keys": ["numerator", "denominator", "pi_exponent"],
            "semantics": "(numerator/denominator)*pi^pi_exponent",
            "canonical_rational": (
                "gcd(abs(numerator),denominator)=1; denominator>0"
            ),
            "canonical_zero": zero,
            "pi_exponent_min": PI_EXPONENT_MIN,
            "pi_exponent_max": PI_EXPONENT_MAX,
            "ordinary_json_floats_forbidden": True,
            "booleans_as_integers_forbidden": True,
            "duplicate_object_keys_forbidden": True,
        },
        "upstream_provenance": _upstream_provenance(material),
        "exact_parameters": {
            "ell_s": one,
            "L_star": length,
            "T_F": tension,
            "M": mass,
            "K": 1,
            "k_1": k_one,
        },
        "exact_identities": {
            "T_F_times_L_star": {
                "lhs": multiply_atoms(tension, length),
                "rhs_M": mass,
            },
            "k_1_times_L_star": {
                "lhs": multiply_atoms(k_one, length),
                "rhs_2pi": phase_one,
            },
            "winding_metric": {
                "lhs_L_star_squared": atom_power(length, 2),
                "rhs_G_ww": make_atom(256, 2),
            },
        },
        "coordinate_chart": {
            "variable_order": list(VARIABLE_ORDER),
            "normalized_worldsheet_quotients": {
                "u1": "R/Z",
                "u2": "R/Z",
                "t": "not_a_quotient",
            },
            "sigma_relation": "sigma_i=L_star*u_i",
            "transverse_mode_phase": "2*pi*n*u_i",
            "normalized_winding_coordinate": "xi_i^w=o_i*u_i",
            "target_periods": [make_atom(8) for _ in range(8)] + [one],
            "target_metric_diagonal": [one for _ in range(8)]
            + [make_atom(256, 2)],
        },
        "source_transport": {
            "coefficient_map": (
                "identity_after_exact_dyadic_to_q*pi^0_reencoding"
            ),
            "source_draw_bytes_changed": False,
            "source_coefficients_changed": False,
            "invariants": {"M": mass, "k_1": k_one},
            "measure_scope": "fixed_index_deterministic_identity_only",
            "does_not_claim": [
                "population_pushforward",
                "measure_preserving_jacobian",
                "entry_probability",
            ],
        },
        "arb_backend_registry": {
            "implementation": "python-flint Arb",
            "python_flint_version": "0.9.0",
            "flint_version": "3.6.0",
            "precision_bits": 192,
            "symbolic_ingress": (
                "construct rational exactly; evaluate pi with Arb outward "
                "rounding; never substitute binary64(pi)"
            ),
        },
        "scope": {
            "claim": (
                "exact fixed-index source-preserving closed-string "
                "coordinate lift"
            ),
            "does_not_claim": [
                "worldsheet entry or no-entry",
                "population law",
                "dimension dynamics",
                "3+1 selection",
            ],
        },
    }


def _rebuild_strings(exact_state: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_strings = exact_state["strings"]
    if type(source_strings) is not list or len(source_strings) != 2:
        fail("source_identity", "index-2 source must contain two strings")
    rebuilt: list[dict[str, Any]] = []
    for string_index, source_string in enumerate(source_strings):
        source_modes = source_string["modes"]
        if type(source_modes) is not list or len(source_modes) != 1:
            fail("source_identity", "registered source must have K=1")
        modes: list[dict[str, Any]] = []
        for mode_index, source_mode in enumerate(source_modes):
            harmonic = _integer(
                source_mode["mode_number"],
                f"$.source.strings[{string_index}].modes[{mode_index}].mode_number",
            )
            frequency = Fraction(harmonic, 8)
            if parse_dyadic(source_mode["wave_number"]) != frequency:
                fail("source_identity", "source wave number is not n/8")
            modes.append(
                {
                    "mode_number": harmonic,
                    "temporal_angular_frequency": make_atom(frequency),
                    "wave_number": make_atom(frequency),
                    "spatial_phase_coefficient": make_atom(2 * harmonic, 1),
                    "initial_x": _convert_dyadic_vector(
                        source_mode["x"], 8, "$.source.mode.x"
                    ),
                    "initial_y": _convert_dyadic_vector(
                        source_mode["y"], 8, "$.source.mode.y"
                    ),
                    "initial_p": _convert_dyadic_vector(
                        source_mode["p"], 8, "$.source.mode.p"
                    ),
                    "initial_q": _convert_dyadic_vector(
                        source_mode["q"], 8, "$.source.mode.q"
                    ),
                }
            )
        rebuilt.append(
            {
                "string_id": string_index + 1,
                "orientation": source_string["orientation"],
                "centre_reference": f"Q{string_index + 1}",
                "transverse_velocity": _convert_dyadic_vector(
                    source_string["transverse_velocity"],
                    8,
                    f"$.source.strings[{string_index}].transverse_velocity",
                ),
                "modes": modes,
            }
        )
    return rebuilt


def rebuild_closed_string_problem(
    material: Mapping[str, Any],
    registry_digest: str,
) -> dict[str, Any]:
    exact_state = material["exact_state"]
    registry = material["registry"]
    downstream = registry["downstream_context"]
    strings = _rebuild_strings(exact_state)
    orientations = [string["orientation"] for string in strings]
    if orientations != [1, -1]:
        fail("seam", "independent source orientations are not (+1,-1)")
    a1 = orientations[0]
    a2 = -orientations[1]
    corner = a1 + a2
    zero = make_atom(0)
    one = make_atom(1)
    t0 = binary64_atom(downstream["observation_window"][0], "$.t0")
    t1 = binary64_atom(downstream["observation_window"][1], "$.t1")
    r_in = binary64_atom(downstream["r_in"], "$.r_in")
    r_out = binary64_atom(downstream["r_out"], "$.r_out")
    return {
        "schema_version": PROBLEM_SCHEMA,
        "problem_id": "index2-symbolic-pi-closed-string-v1",
        "equation_family_version": EQUATION_FAMILY,
        "lift_registry_semantic_sha256": registry_digest,
        "source_commitment": {
            "source_registry_canonical_sha256": SOURCE_REGISTRY_SHA256,
            "source_draw_sha256": SOURCE_DRAW_SHA256,
            "source_sample_index": 2,
            "source_state_sha256": SOURCE_STATE_SHA256,
            "coefficient_transport": (
                "exact_dyadic_to_canonical_q*pi^0_identity"
            ),
        },
        "dimensions": {
            "target": 9,
            "target_axis_order": list(range(9)),
            "transverse": 8,
            "transverse_axis_order": list(range(8)),
            "winding_axis": 8,
        },
        "exact_parameters": {
            "L_star": make_atom(16, 1),
            "T_F": make_atom(Fraction(1, 2), -1),
            "M": make_atom(8),
            "ell_s": one,
            "K": 1,
        },
        "variable_registry": {
            "variable_order": list(VARIABLE_ORDER),
            "domains": {
                "u1": {
                    "lower": zero,
                    "upper": one,
                    "closure": "lower_closed_upper_open",
                    "quotient": "R/Z",
                },
                "u2": {
                    "lower": zero,
                    "upper": one,
                    "closure": "lower_closed_upper_open",
                    "quotient": "R/Z",
                },
                "t": {
                    "lower": t0,
                    "upper": t1,
                    "closure": "lower_closed_upper_open",
                    "quotient": "none",
                },
            },
        },
        "target_torus": {
            "periods": [make_atom(8) for _ in range(8)] + [one],
            "lattice_matrix_diagonal": [
                make_atom(8) for _ in range(8)
            ]
            + [one],
            "metric_diagonal": [one for _ in range(8)]
            + [make_atom(256, 2)],
            "lattice_convention": (
                "Lambda=diag(8,...,8,1) in normalized coordinates"
            ),
            "metric_convention": "G=diag(1,...,1,(16*pi)^2)",
            "image_separation": "s_n=d-Lambda*n for n in Z^9",
        },
        "solver_geometry": {
            "domain_metric_diagonal": [
                make_atom(256, 2),
                make_atom(256, 2),
                one,
            ],
            "coordinate_jacobian_chart": list(VARIABLE_ORDER),
            "krawczyk_rule": (
                "use the coordinate Jacobian in the registered "
                "(u1,u2,t) chart"
            ),
            "rank_rule": (
                "certify exact rank by minors or interval exclusion; "
                "rank is invariant under this invertible chart change"
            ),
            "physical_singular_value_formula": "G^(1/2)*J*H^(-1/2)",
        },
        "worldsheet": {
            "coordinate_units": "u_i=sigma_i/L_star",
            "orientations": orientations,
            "winding_embedding": "xi_i^w=o_i*u_i",
            "winding_separation": "d_w=o1*u1-o2*u2",
            "seam_image_actions": {
                "u1_plus_1": {
                    "parameter_shift": [1, 0, 0],
                    "separation_winding_shift": a1,
                    "n8_reindex_shift": a1,
                    "exact_rule": "a1=o1",
                },
                "u2_plus_1": {
                    "parameter_shift": [0, 1, 0],
                    "separation_winding_shift": a2,
                    "n8_reindex_shift": a2,
                    "exact_rule": "a2=-o2",
                },
                "corner_plus_1_plus_1": {
                    "parameter_shift": [1, 1, 0],
                    "separation_winding_shift": corner,
                    "n8_reindex_shift": corner,
                    "exact_rule": "a12=a1+a2",
                },
            },
            "transverse_seam_identity": (
                "integer n gives exp(i*2*pi*n*(u+1))="
                "exp(i*2*pi*n*u)"
            ),
            "seam_claim": (
                "exact target-lattice reindexing, not endpoint "
                "floating-point comparison"
            ),
            "upper_to_lower_reindex_rule": "n_lower=n_upper-a_i*e_w",
        },
        "kinematics": {
            "initial_time": zero,
            "centres_Q1_Q2": {
                "Q1": _convert_dyadic_vector(
                    exact_state["Q1"], 8, "$.source.Q1"
                ),
                "Q2": _convert_dyadic_vector(
                    exact_state["Q2"], 8, "$.source.Q2"
                ),
            },
            "strings": strings,
            "mode_ode": [
                "dot(x)=p",
                "dot(y)=q",
                "dot(p)=-(n/8)^2*x",
                "dot(q)=-(n/8)^2*y",
            ],
            "transverse_embedding": (
                "X_i^perp=Q_i+V_i*t+sum_n("
                "x_in(t)*cos(2*pi*n*u_i)+"
                "y_in(t)*sin(2*pi*n*u_i))"
            ),
            "separation": (
                "d_perp=(Q1-Q2)+(V1-V2)*t+(Y1-Y2); "
                "d_w=o1*u1-o2*u2"
            ),
            "centre_term_multiplicity": 1,
        },
        "hysteresis": {
            "distance_convention": "F_n=(1/2)*s_n^T*G*s_n",
            "r_in": r_in,
            "r_out": r_out,
        },
        "observation": {
            "t0": t0,
            "t1": t1,
            "window_closure": "lower_closed_upper_open",
            "initial_history": downstream["initial_history"],
            "continuation_convention": (
                "right-censor at excluded t1; carry active/armed history "
                "to a subsequent adjacent window without boundary re-arming"
            ),
            "time_is_quotient": False,
            "window_transport": (
                "unchanged exact dyadic endpoints from the registered "
                "source bridge"
            ),
        },
        "arb_backend_ingress": {
            "variable_order": list(VARIABLE_ORDER),
            "target_component_order": list(range(9)),
            "implementation": "python-flint Arb",
            "python_flint_version": "0.9.0",
            "flint_version": "3.6.0",
            "precision_bits": 192,
            "scalar_ingress": (
                "canonical q*pi^e; rational exact and Arb pi outward-rounded"
            ),
            "required_outputs": [
                "d",
                "d_a",
                "d_ab",
                "F_a",
                "F_ab",
                "g_r",
                "Dg_r",
            ],
        },
        "scope": {
            "claim": (
                "exact source-bound normalized closed-string problem "
                "and seam algebra"
            ),
            "does_not_claim": [
                "entry or no-entry over the registered window",
                "population pushforward or Jacobian",
                "population law",
                "dimension dynamics",
                "3+1 selection",
            ],
        },
    }


def rebuild_fixture(material: Mapping[str, Any]) -> dict[str, Any]:
    registry = rebuild_lift_registry(material)
    registry_digest = semantic_sha256(registry)
    problem = rebuild_closed_string_problem(material, registry_digest)
    return {
        "schema_version": FIXTURE_SCHEMA,
        "lift_registry": registry,
        "lift_registry_semantic_sha256": registry_digest,
        "closed_string_problem": problem,
        "closed_string_problem_semantic_sha256": semantic_sha256(problem),
    }


def _verify_source_identity(
    problem: Mapping[str, Any], exact_state: Mapping[str, Any]
) -> None:
    for centre in ("Q1", "Q2"):
        for old, new in zip(
            exact_state[centre], problem["kinematics"]["centres_Q1_Q2"][centre]
        ):
            if parse_atom(new) != (parse_dyadic(old), 0):
                fail("source_identity", f"{centre} coefficient changed")
    for string_index, source_string in enumerate(exact_state["strings"]):
        target_string = problem["kinematics"]["strings"][string_index]
        if (
            source_string["orientation"] != target_string["orientation"]
            or target_string["string_id"] != string_index + 1
        ):
            fail("source_identity", "string identity or orientation changed")
        for old, new in zip(
            source_string["transverse_velocity"],
            target_string["transverse_velocity"],
        ):
            if parse_atom(new) != (parse_dyadic(old), 0):
                fail("source_identity", "velocity coefficient changed")
        for mode_index, source_mode in enumerate(source_string["modes"]):
            target_mode = target_string["modes"][mode_index]
            for old_name, new_name in (
                ("x", "initial_x"),
                ("y", "initial_y"),
                ("p", "initial_p"),
                ("q", "initial_q"),
            ):
                for old, new in zip(
                    source_mode[old_name], target_mode[new_name]
                ):
                    if parse_atom(new) != (parse_dyadic(old), 0):
                        fail(
                            "source_identity",
                            f"{new_name} coefficient changed",
                        )


def _verify_exact_geometry(
    problem: Mapping[str, Any], material: Mapping[str, Any]
) -> dict[str, Any]:
    exact = problem["exact_parameters"]
    length = exact["L_star"]
    if parse_atom(length) != (Fraction(16), 1):
        fail("exact_identity", "L_star is not 16*pi")
    if parse_atom(exact["T_F"]) != (Fraction(1, 2), -1):
        fail("exact_identity", "T_F is not 1/(2*pi)")
    if parse_atom(exact["M"]) != (Fraction(8), 0) or exact["K"] != 1:
        fail("exact_identity", "M or K differs")
    if multiply_atoms(exact["T_F"], length) != exact["M"]:
        fail("exact_identity", "T_F*L_star != M")

    expected_periods = [make_atom(8) for _ in range(8)] + [make_atom(1)]
    torus = problem["target_torus"]
    if (
        torus["periods"] != expected_periods
        or torus["lattice_matrix_diagonal"] != expected_periods
    ):
        fail("target_geometry", "normalized lattice periods differ")
    length_squared = atom_power(length, 2)
    if torus["metric_diagonal"] != (
        [make_atom(1) for _ in range(8)] + [length_squared]
    ):
        fail("target_geometry", "target winding metric is not L_star^2")
    if problem["solver_geometry"]["domain_metric_diagonal"] != [
        length_squared,
        length_squared,
        make_atom(1),
    ]:
        fail("domain_geometry", "H is not diag(L_star^2,L_star^2,1)")

    orientations = problem["worldsheet"]["orientations"]
    if orientations != [1, -1]:
        fail("seam", "orientations differ")
    expected_shifts = {
        "u1_plus_1": orientations[0],
        "u2_plus_1": -orientations[1],
        "corner_plus_1_plus_1": orientations[0] - orientations[1],
    }
    for name, shift in expected_shifts.items():
        action = problem["worldsheet"]["seam_image_actions"][name]
        if (
            action["separation_winding_shift"] != shift
            or action["n8_reindex_shift"] != shift
        ):
            fail("seam", f"{name} shift is false")

    for string in problem["kinematics"]["strings"]:
        for mode in string["modes"]:
            harmonic = mode["mode_number"]
            expected_k = make_atom(Fraction(harmonic, 8))
            expected_phase = make_atom(2 * harmonic, 1)
            if (
                mode["wave_number"] != expected_k
                or mode["temporal_angular_frequency"] != expected_k
                or mode["spatial_phase_coefficient"] != expected_phase
                or multiply_atoms(expected_k, length) != expected_phase
            ):
                fail("mode_identity", "k, phase, or k*L identity differs")

    downstream = material["registry"]["downstream_context"]
    expected_t0 = binary64_atom(downstream["observation_window"][0], "$.t0")
    expected_t1 = binary64_atom(downstream["observation_window"][1], "$.t1")
    if (
        problem["observation"]["t0"] != expected_t0
        or problem["observation"]["t1"] != expected_t1
        or parse_atom(problem["observation"]["t1"])[1] != 0
        or problem["observation"]["time_is_quotient"] is not False
    ):
        fail("time_window", "time window changed or became a quotient")
    _verify_source_identity(problem, material["exact_state"])
    return {
        "L_star": "16*pi",
        "T_F_times_L_star": "8",
        "mode_frequency_rule": "k_n=n/8",
        "winding_metric": "L_star^2",
        "domain_metric": "diag(L_star^2,L_star^2,1)",
        "seam_shifts": {
            "u1_plus_1": expected_shifts["u1_plus_1"],
            "u2_plus_1": expected_shifts["u2_plus_1"],
            "corner": expected_shifts["corner_plus_1_plus_1"],
        },
    }


def replay_fixture_objects(
    candidate: Any,
    material: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_material = (
        _independent_source_material() if material is None else material
    )
    expected = rebuild_fixture(source_material)
    obj = _exact_keys(
        candidate,
        {
            "schema_version",
            "lift_registry",
            "lift_registry_semantic_sha256",
            "closed_string_problem",
            "closed_string_problem_semantic_sha256",
        },
        "$.fixture",
        "fixture_schema",
    )
    if obj["schema_version"] != FIXTURE_SCHEMA:
        fail("fixture_schema", "unsupported lift fixture schema")

    registry_digest = semantic_sha256(obj["lift_registry"])
    problem_digest = semantic_sha256(obj["closed_string_problem"])
    if (
        registry_digest != LIFT_REGISTRY_SHA256
        or obj["lift_registry_semantic_sha256"] != registry_digest
        or semantic_sha256(expected["lift_registry"]) != registry_digest
    ):
        fail("registry_hash", "lift registry does not replay its pinned hash")
    if (
        problem_digest != CLOSED_STRING_PROBLEM_SHA256
        or obj["closed_string_problem_semantic_sha256"] != problem_digest
        or semantic_sha256(expected["closed_string_problem"]) != problem_digest
    ):
        fail("problem_hash", "closed-string problem does not replay its pin")
    if not type_strict_equal(obj, expected):
        fail("fixture_reproduction", "fixture differs from independent rebuild")

    geometry = _verify_exact_geometry(
        obj["closed_string_problem"], source_material
    )
    if canonical_bytes(obj).decode("utf-8").count(LEGACY_PROBLEM_SHA256) != 1:
        fail(
            "provenance_boundary",
            "legacy problem hash must occur once in registry provenance",
        )
    return {
        "source_registry_canonical_sha256": SOURCE_REGISTRY_SHA256,
        "source_draw_sha256": SOURCE_DRAW_SHA256,
        "source_state_sha256": SOURCE_STATE_SHA256,
        "source_bridge_fixture_semantic_sha256": SOURCE_FIXTURE_SHA256,
        "legacy_cut_open_problem_semantic_sha256": LEGACY_PROBLEM_SHA256,
        "lift_registry_semantic_sha256": registry_digest,
        "closed_string_problem_semantic_sha256": problem_digest,
        "lift_fixture_semantic_sha256": semantic_sha256(obj),
        "source_exact_state_semantic_sha256": SOURCE_EXACT_STATE_SHA256,
        "source_binary64_state_semantic_sha256": (
            SOURCE_BINARY64_STATE_SHA256
        ),
        "exact_geometry": geometry,
    }


def replay_fixture_path(path: Path = LIFT_FIXTURE_PATH) -> dict[str, Any]:
    return replay_fixture_objects(strict_json_load(path))


def _reseal_fixture(value: dict[str, Any]) -> None:
    registry_digest = semantic_sha256(value["lift_registry"])
    value["lift_registry_semantic_sha256"] = registry_digest
    value["closed_string_problem"][
        "lift_registry_semantic_sha256"
    ] = registry_digest
    value["closed_string_problem_semantic_sha256"] = semantic_sha256(
        value["closed_string_problem"]
    )


def hostile_controls() -> dict[str, bool]:
    baseline = strict_json_load(LIFT_FIXTURE_PATH)
    material = _independent_source_material()
    source_fixture = source_replay.strict_fixture_load(SOURCE_FIXTURE_PATH)
    binary64_length = dyadic_atom(
        source_fixture["physical_problem"]["f1_convention"]["winding_length"]
    )

    mutations: dict[str, Callable[[dict[str, Any]], None]] = {
        "binary64_pi_length_substitution_rejected": (
            lambda value: value["closed_string_problem"][
                "exact_parameters"
            ].__setitem__("L_star", binary64_length)
        ),
        "mass_mutation_rejected": (
            lambda value: value["closed_string_problem"][
                "exact_parameters"
            ].__setitem__("M", make_atom(7))
        ),
        "temporal_frequency_mutation_rejected": (
            lambda value: value["closed_string_problem"]["kinematics"][
                "strings"
            ][0]["modes"][0].__setitem__("wave_number", make_atom(1, 0))
        ),
        "spatial_phase_mutation_rejected": (
            lambda value: value["closed_string_problem"]["kinematics"][
                "strings"
            ][0]["modes"][0].__setitem__(
                "spatial_phase_coefficient", make_atom(1, 1)
            )
        ),
        "target_metric_mutation_rejected": (
            lambda value: value["closed_string_problem"]["target_torus"][
                "metric_diagonal"
            ].__setitem__(8, make_atom(64, 2))
        ),
        "domain_metric_mutation_rejected": (
            lambda value: value["closed_string_problem"]["solver_geometry"][
                "domain_metric_diagonal"
            ].__setitem__(0, make_atom(1))
        ),
        "lattice_period_mutation_rejected": (
            lambda value: value["closed_string_problem"]["target_torus"][
                "lattice_matrix_diagonal"
            ].__setitem__(0, make_atom(7))
        ),
        "seam_shift_mutation_rejected": (
            lambda value: value["closed_string_problem"]["worldsheet"][
                "seam_image_actions"
            ]["u2_plus_1"].__setitem__("n8_reindex_shift", -1)
        ),
        "seam_action_deletion_rejected": (
            lambda value: value["closed_string_problem"]["worldsheet"][
                "seam_image_actions"
            ].pop("u1_plus_1")
        ),
        "orientation_mutation_rejected": (
            lambda value: value["closed_string_problem"]["worldsheet"].__setitem__(
                "orientations", [1, 1]
            )
        ),
        "symbolic_time_endpoint_rejected": (
            lambda value: value["closed_string_problem"][
                "observation"
            ].__setitem__("t1", make_atom(16, 1))
        ),
        "source_coefficient_mutation_rejected": (
            lambda value: value["closed_string_problem"]["kinematics"][
                "strings"
            ][0]["modes"][0]["initial_x"][0].__setitem__(
                "numerator",
                value["closed_string_problem"]["kinematics"]["strings"][0][
                    "modes"
                ][0]["initial_x"][0]["numerator"]
                + 2,
            )
        ),
        "source_commitment_mutation_rejected": (
            lambda value: value["closed_string_problem"][
                "source_commitment"
            ].__setitem__("source_state_sha256", "0" * 64)
        ),
        "registry_parameter_mutation_rejected": (
            lambda value: value["lift_registry"]["exact_parameters"].__setitem__(
                "M", make_atom(9)
            )
        ),
        "atom_extra_key_rejected": (
            lambda value: value["closed_string_problem"]["exact_parameters"][
                "M"
            ].__setitem__("unit", "mass")
        ),
        "atom_noncanonical_zero_rejected": (
            lambda value: value["closed_string_problem"]["variable_registry"][
                "domains"
            ]["u1"].__setitem__(
                "lower",
                {
                    "numerator": 0,
                    "denominator": 1,
                    "pi_exponent": 1,
                },
            )
        ),
    }
    results: dict[str, bool] = {}
    for name, mutator in mutations.items():
        hostile = copy.deepcopy(baseline)
        mutator(hostile)
        _reseal_fixture(hostile)
        try:
            replay_fixture_objects(hostile, material)
        except SymbolicLiftReplayError:
            results[name] = True
        else:
            results[name] = False

    try:
        strict_json_loads('{"x":1,"x":2}')
    except SymbolicLiftReplayError:
        results["duplicate_json_key_rejected"] = True
    else:
        results["duplicate_json_key_rejected"] = False
    try:
        strict_json_loads('{"x":1.0}')
    except SymbolicLiftReplayError:
        results["ordinary_json_float_rejected"] = True
    else:
        results["ordinary_json_float_rejected"] = False
    return results


def _inventory() -> list[dict[str, str]]:
    paths = [
        ARTIFACT_DIR / "source_binding_replayer.py",
        ARTIFACT_DIR / "symbolic_pi_lift_replayer.py",
        ARTIFACT_DIR / "test_symbolic_pi_lift_replayer.py",
        SOURCE_REGISTRY_PATH,
        SOURCE_FIXTURE_PATH,
        LIFT_FIXTURE_PATH,
    ]
    return [
        {
            "path": path.relative_to(ARTIFACT_DIR.parent.parent).as_posix(),
            "normalized_lf_sha256": normalized_lf_sha256(path),
        }
        for path in paths
    ]


def build_report(replay: Mapping[str, Any]) -> dict[str, Any]:
    hostile = hostile_controls()
    if not all(hostile.values()):
        failed = sorted(name for name, passed in hostile.items() if not passed)
        fail("hostile_controls", f"accepted hostile mutations: {failed}")
    report: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "status": "passed",
        "failed_gates": [],
        "checks": {
            "independent_source_binding_replayed": True,
            "strict_float_free_lift_json_replayed": True,
            "strict_q_pi_power_atoms_replayed": True,
            "canonical_registry_rebuilt_without_generator": True,
            "canonical_problem_rebuilt_without_generator": True,
            "pinned_registry_and_problem_hashes_recomputed": True,
            "source_coefficient_identity_replayed": True,
            "M_k_L_exact_identities_replayed": True,
            "target_and_domain_metrics_replayed": True,
            "exact_seam_image_actions_replayed": True,
            "registered_dyadic_time_window_replayed": True,
            "population_and_dimension_claims_withheld": True,
        },
        "commitments": copy.deepcopy(dict(replay)),
        "hostile_controls": hostile,
        "normalized_lf_inventory": _inventory(),
        "scope": {
            "claim": (
                "independent source-bound replay of the fixed-index "
                "symbolic-pi closed-string lift"
            ),
            "does_not_claim": [
                "finite-window entry or no-entry",
                "population pushforward or Jacobian",
                "population law",
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
        report,
        set(expected),
        "$.report",
        "report_schema",
    )
    if obj["schema_version"] != REPORT_SCHEMA:
        fail("report_schema", "unsupported replayer report")
    stored = obj["report_semantic_sha256"]
    payload = copy.deepcopy(obj)
    del payload["report_semantic_sha256"]
    if stored != semantic_sha256(payload):
        fail("report_hash", "report semantic hash does not replay")
    if not type_strict_equal(obj, expected):
        fail("report_reproduction", "stored report differs from fresh replay")
    return stored


def run(write: bool) -> dict[str, Any]:
    replay = replay_fixture_path()
    report = build_report(replay)
    if write:
        REPORT_PATH.write_text(
            pretty_json(report), encoding="utf-8", newline="\n"
        )
    else:
        stored = strict_json_load(REPORT_PATH)
        verify_report(stored, replay)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Independently replay the symbolic-pi closed-string lift"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = run(write=args.write)
    except SymbolicLiftReplayError as error:
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
                "lift_registry_semantic_sha256": report["commitments"][
                    "lift_registry_semantic_sha256"
                ],
                "closed_string_problem_semantic_sha256": report[
                    "commitments"
                ]["closed_string_problem_semantic_sha256"],
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
