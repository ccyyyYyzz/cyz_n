#!/usr/bin/env python3
"""Outward-rounded interval-jet control for Brief 0019.

This module is deliberately smaller than the eventual event solver.  It
evaluates one genuine finite-K trigonometric world-sheet fixture with Arb
balls and derives d, its first and second jets, F, g and Dg.  Ordinary
binary64 arithmetic is not used for any asserted enclosure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

import flint
from flint import arb, ctx


PYTHON_FLINT_VERSION = "0.9.0"
FLINT_VERSION = "3.6.0"
DEFAULT_PRECISION_BITS = 192
FIXTURE_SCHEMA = "cyz-brief-0019-arb-jet-fixture-v1"
REPORT_SCHEMA = "cyz-brief-0019-arb-jet-report-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_FIXTURE = HERE / "arb_interval_jet_fixture.json"
DEFAULT_REPORT = HERE / "arb_interval_jet_report.json"


class JetError(ValueError):
    """The registered interval-jet object is invalid or not certified."""


def _fail(path: str, message: str) -> None:
    raise JetError(f"{path}: {message}")


def reject_duplicate_pairs(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JetError(f"$: duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise JetError(f"$: non-finite JSON token {value!r}")


def load_strict_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8", newline=None) as handle:
        return json.load(
            handle,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_constant,
        )


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _exact_keys(value: Any, expected: set[str], path: str) -> Mapping[str, Any]:
    if type(value) is not dict:
        _fail(path, "expected an object")
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        _fail(path, f"missing keys {missing}")
    if extra:
        _fail(path, f"unexpected keys {extra}")
    return value


def _integer(value: Any, path: str) -> int:
    if type(value) is not int:
        _fail(path, "expected an integer; booleans are forbidden")
    return value


def dyadic_fraction(value: Any, path: str = "$dyadic") -> Fraction:
    item = _exact_keys(value, {"numerator", "exponent"}, path)
    numerator = _integer(item["numerator"], f"{path}.numerator")
    exponent = _integer(item["exponent"], f"{path}.exponent")
    if exponent < 0:
        _fail(f"{path}.exponent", "must be nonnegative")
    if numerator == 0 and exponent != 0:
        _fail(path, "zero must use exponent zero")
    if numerator != 0 and exponent > 0 and numerator % 2 == 0:
        _fail(path, "dyadic is not in reduced form")
    return Fraction(numerator, 2**exponent)


def dyadic_json(value: Fraction | int) -> dict[str, int]:
    fraction = Fraction(value)
    denominator = fraction.denominator
    if denominator & (denominator - 1):
        raise ValueError("value is not dyadic")
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
        raise JetError("only dyadic exact endpoints are registered")
    return value.numerator, -(denominator.bit_length() - 1)


def exact_arb(value: Fraction | int) -> arb:
    return arb(_arb_tuple(Fraction(value)))


def interval_arb(value: Any, path: str = "$interval") -> arb:
    item = _exact_keys(value, {"lo", "hi"}, path)
    lower = dyadic_fraction(item["lo"], f"{path}.lo")
    upper = dyadic_fraction(item["hi"], f"{path}.hi")
    if lower > upper:
        _fail(path, "reversed interval")
    midpoint = (lower + upper) / 2
    radius = (upper - lower) / 2
    return arb(_arb_tuple(midpoint), _arb_tuple(radius))


def point_interval(value: Fraction | int) -> dict[str, Any]:
    encoded = dyadic_json(value)
    return {"lo": encoded, "hi": dict(encoded)}


def closed_interval(
    lower: Fraction | int, upper: Fraction | int
) -> dict[str, Any]:
    if Fraction(lower) > Fraction(upper):
        raise ValueError("reversed interval")
    return {"lo": dyadic_json(lower), "hi": dyadic_json(upper)}


@contextmanager
def precision(bits: int) -> Iterator[None]:
    if type(bits) is not int or bits < 64:
        raise JetError("Arb precision must be an integer of at least 64 bits")
    previous = ctx.prec
    ctx.prec = bits
    try:
        yield
    finally:
        ctx.prec = previous


def check_backend() -> dict[str, str]:
    python_flint = getattr(flint, "__version__", None)
    flint_version = getattr(flint, "__FLINT_VERSION__", None)
    if python_flint != PYTHON_FLINT_VERSION:
        raise JetError(
            "python-flint runtime mismatch: "
            f"expected {PYTHON_FLINT_VERSION}, got {python_flint!r}"
        )
    if flint_version != FLINT_VERSION:
        raise JetError(
            f"FLINT runtime mismatch: expected {FLINT_VERSION}, "
            f"got {flint_version!r}"
        )
    return {
        "python_flint": python_flint,
        "flint": flint_version,
        "arithmetic": "arb outward-rounded balls",
    }


def _arb_vector(
    values: Any, length: int, path: str
) -> list[arb]:
    if type(values) is not list or len(values) != length:
        _fail(path, f"expected a vector of length {length}")
    return [
        exact_arb(dyadic_fraction(value, f"{path}[{index}]"))
        for index, value in enumerate(values)
    ]


def _interval_vector(
    values: Any, length: int, path: str
) -> list[arb]:
    if type(values) is not list or len(values) != length:
        _fail(path, f"expected an interval vector of length {length}")
    return [
        interval_arb(value, f"{path}[{index}]")
        for index, value in enumerate(values)
    ]


def _zero_vector(length: int) -> list[arb]:
    return [arb(0) for _ in range(length)]


def _zero_matrix(rows: int, columns: int) -> list[list[arb]]:
    return [[arb(0) for _ in range(columns)] for _ in range(rows)]


def _vector_add(left: Sequence[arb], right: Sequence[arb]) -> list[arb]:
    if len(left) != len(right):
        raise JetError("vector shape mismatch")
    return [a + b for a, b in zip(left, right)]


def _vector_subtract(left: Sequence[arb], right: Sequence[arb]) -> list[arb]:
    if len(left) != len(right):
        raise JetError("vector shape mismatch")
    return [a - b for a, b in zip(left, right)]


def _vector_scale(scale: arb, vector: Sequence[arb]) -> list[arb]:
    return [scale * value for value in vector]


def _metric_dot(
    left: Sequence[arb],
    metric_diagonal: Sequence[arb],
    right: Sequence[arb],
) -> arb:
    if not (len(left) == len(metric_diagonal) == len(right)):
        raise JetError("metric-dot shape mismatch")
    total = arb(0)
    for a, metric, b in zip(left, metric_diagonal, right):
        total += a * metric * b
    return total


def _mode_jet(
    coefficients: Mapping[str, Any],
    wave_number: arb,
    sigma: arb,
    time: arb,
    path: str,
) -> tuple[arb, arb, arb, arb, arb, arb]:
    item = _exact_keys(
        coefficients,
        {"x", "y", "p", "q"},
        path,
    )
    x0 = exact_arb(dyadic_fraction(item["x"], f"{path}.x"))
    y0 = exact_arb(dyadic_fraction(item["y"], f"{path}.y"))
    p0 = exact_arb(dyadic_fraction(item["p"], f"{path}.p"))
    q0 = exact_arb(dyadic_fraction(item["q"], f"{path}.q"))
    if wave_number.contains(arb(0)):
        _fail(path, "wave number interval contains zero")

    kt = wave_number * time
    ks = wave_number * sigma
    ct = kt.cos()
    st = kt.sin()
    cs = ks.cos()
    ss = ks.sin()

    x_t = x0 * ct + (p0 / wave_number) * st
    y_t = y0 * ct + (q0 / wave_number) * st
    p_t = -wave_number * x0 * st + p0 * ct
    q_t = -wave_number * y0 * st + q0 * ct

    value = x_t * cs + y_t * ss
    d_sigma = wave_number * (-x_t * ss + y_t * cs)
    d_time = p_t * cs + q_t * ss
    d_sigma_sigma = -(wave_number * wave_number) * value
    d_time_time = d_sigma_sigma
    d_sigma_time = wave_number * (-p_t * ss + q_t * cs)
    return (
        value,
        d_sigma,
        d_time,
        d_sigma_sigma,
        d_sigma_time,
        d_time_time,
    )


def validate_fixture(fixture: Any) -> Mapping[str, Any]:
    root = _exact_keys(
        fixture,
        {
            "schema_version",
            "fixture_id",
            "target_dimension",
            "transverse_dimension",
            "winding_axis",
            "winding_orientations",
            "metric_diagonal",
            "lattice_shift",
            "radius",
            "relative_centre",
            "relative_velocity",
            "wave_numbers",
            "strings",
            "root_box",
            "control_box",
            "expected_point_values",
        },
        "$",
    )
    if root["schema_version"] != FIXTURE_SCHEMA:
        _fail("$.schema_version", "unsupported fixture schema")
    if type(root["fixture_id"]) is not str or not root["fixture_id"]:
        _fail("$.fixture_id", "expected a nonempty string")
    target_dimension = _integer(root["target_dimension"], "$.target_dimension")
    transverse_dimension = _integer(
        root["transverse_dimension"], "$.transverse_dimension"
    )
    winding_axis = _integer(root["winding_axis"], "$.winding_axis")
    if target_dimension != transverse_dimension + 1:
        _fail("$", "target dimension must be transverse dimension plus one")
    if winding_axis != target_dimension - 1:
        _fail("$.winding_axis", "control freezes winding axis last")
    orientations = root["winding_orientations"]
    if orientations != [1, -1] or any(type(value) is not int for value in orientations):
        _fail("$.winding_orientations", "expected exact orientations [1,-1]")
    for name in ("metric_diagonal", "lattice_shift"):
        _arb_vector(root[name], target_dimension, f"$.{name}")
    _arb_vector(
        root["relative_centre"],
        transverse_dimension,
        "$.relative_centre",
    )
    _arb_vector(
        root["relative_velocity"],
        transverse_dimension,
        "$.relative_velocity",
    )
    radius = dyadic_fraction(root["radius"], "$.radius")
    if radius <= 0:
        _fail("$.radius", "radius must be positive")
    if type(root["wave_numbers"]) is not list or not root["wave_numbers"]:
        _fail("$.wave_numbers", "expected at least one Fourier mode")
    wave_numbers = [
        dyadic_fraction(value, f"$.wave_numbers[{index}]")
        for index, value in enumerate(root["wave_numbers"])
    ]
    if any(value <= 0 for value in wave_numbers):
        _fail("$.wave_numbers", "wave numbers must be positive")
    strings = root["strings"]
    if type(strings) is not list or len(strings) != 2:
        _fail("$.strings", "expected exactly two strings")
    for string_index, modes in enumerate(strings):
        if type(modes) is not list or len(modes) != len(wave_numbers):
            _fail(
                f"$.strings[{string_index}]",
                "mode count does not match wave-number count",
            )
        for mode_index, components in enumerate(modes):
            if type(components) is not list or len(components) != transverse_dimension:
                _fail(
                    f"$.strings[{string_index}][{mode_index}]",
                    "transverse component count mismatch",
                )
            for component_index, coefficients in enumerate(components):
                _exact_keys(
                    coefficients,
                    {"x", "y", "p", "q"},
                    (
                        f"$.strings[{string_index}][{mode_index}]"
                        f"[{component_index}]"
                    ),
                )
                for key, value in coefficients.items():
                    dyadic_fraction(
                        value,
                        (
                            f"$.strings[{string_index}][{mode_index}]"
                            f"[{component_index}].{key}"
                        ),
                    )
    for box_name in ("root_box", "control_box"):
        box = _exact_keys(
            root[box_name],
            {"sigma1", "sigma2", "time"},
            f"$.{box_name}",
        )
        for axis in ("sigma1", "sigma2", "time"):
            interval_arb(box[axis], f"$.{box_name}.{axis}")
    expected = _exact_keys(
        root["expected_point_values"],
        {
            "F_sigma1",
            "F_sigma2",
            "F_time",
            "F_boundary",
            "H_11",
            "H_12",
            "H_22",
            "det_Dg",
            "Ft_det_H",
        },
        "$.expected_point_values",
    )
    for key, value in expected.items():
        dyadic_fraction(value, f"$.expected_point_values.{key}")
    return root


def evaluate_interval_jets(
    fixture: Mapping[str, Any],
    box_name: str,
    *,
    precision_bits: int = DEFAULT_PRECISION_BITS,
) -> dict[str, Any]:
    validate_fixture(fixture)
    if box_name not in {"root_box", "control_box"}:
        raise JetError("box_name must be root_box or control_box")
    with precision(precision_bits):
        target_dimension = fixture["target_dimension"]
        transverse_dimension = fixture["transverse_dimension"]
        box = fixture[box_name]
        variables = [
            interval_arb(box["sigma1"], f"$.{box_name}.sigma1"),
            interval_arb(box["sigma2"], f"$.{box_name}.sigma2"),
            interval_arb(box["time"], f"$.{box_name}.time"),
        ]
        sigma1, sigma2, time = variables
        centre = _arb_vector(
            fixture["relative_centre"],
            transverse_dimension,
            "$.relative_centre",
        )
        velocity = _arb_vector(
            fixture["relative_velocity"],
            transverse_dimension,
            "$.relative_velocity",
        )
        wave_numbers = [
            exact_arb(
                dyadic_fraction(value, f"$.wave_numbers[{index}]")
            )
            for index, value in enumerate(fixture["wave_numbers"])
        ]

        d = _zero_vector(target_dimension)
        first = [_zero_vector(target_dimension) for _ in range(3)]
        second = [
            [_zero_vector(target_dimension) for _ in range(3)]
            for _ in range(3)
        ]

        for component in range(transverse_dimension):
            value1 = arb(0)
            sigma1_first = arb(0)
            time1_first = arb(0)
            sigma1_second = arb(0)
            sigma1_time = arb(0)
            time1_second = arb(0)
            value2 = arb(0)
            sigma2_native = arb(0)
            time2_native = arb(0)
            sigma2_native_second = arb(0)
            sigma2_time_native = arb(0)
            time2_native_second = arb(0)
            for mode_index, wave_number in enumerate(wave_numbers):
                jet1 = _mode_jet(
                    fixture["strings"][0][mode_index][component],
                    wave_number,
                    sigma1,
                    time,
                    f"$.strings[0][{mode_index}][{component}]",
                )
                jet2 = _mode_jet(
                    fixture["strings"][1][mode_index][component],
                    wave_number,
                    sigma2,
                    time,
                    f"$.strings[1][{mode_index}][{component}]",
                )
                value1 += jet1[0]
                sigma1_first += jet1[1]
                time1_first += jet1[2]
                sigma1_second += jet1[3]
                sigma1_time += jet1[4]
                time1_second += jet1[5]
                value2 += jet2[0]
                sigma2_native += jet2[1]
                time2_native += jet2[2]
                sigma2_native_second += jet2[3]
                sigma2_time_native += jet2[4]
                time2_native_second += jet2[5]

            d[component] = (
                centre[component]
                + velocity[component] * time
                + value1
                - value2
            )
            first[0][component] = sigma1_first
            first[1][component] = -sigma2_native
            first[2][component] = (
                velocity[component] + time1_first - time2_native
            )
            second[0][0][component] = sigma1_second
            second[1][1][component] = -sigma2_native_second
            second[2][2][component] = time1_second - time2_native_second
            second[0][2][component] = sigma1_time
            second[2][0][component] = sigma1_time
            second[1][2][component] = -sigma2_time_native
            second[2][1][component] = -sigma2_time_native

        winding_axis = fixture["winding_axis"]
        orientation1, orientation2 = fixture["winding_orientations"]
        d[winding_axis] = orientation1 * sigma1 - orientation2 * sigma2
        first[0][winding_axis] = arb(orientation1)
        first[1][winding_axis] = arb(-orientation2)

        lattice_shift = _arb_vector(
            fixture["lattice_shift"],
            target_dimension,
            "$.lattice_shift",
        )
        separation = _vector_subtract(d, lattice_shift)
        metric = _arb_vector(
            fixture["metric_diagonal"],
            target_dimension,
            "$.metric_diagonal",
        )
        radius = exact_arb(dyadic_fraction(fixture["radius"], "$.radius"))
        F = _metric_dot(separation, metric, separation) / 2
        F_first = [
            _metric_dot(first[axis], metric, separation)
            for axis in range(3)
        ]
        F_second = _zero_matrix(3, 3)
        for row in range(3):
            for column in range(3):
                F_second[row][column] = _metric_dot(
                    second[row][column], metric, separation
                ) + _metric_dot(first[row], metric, first[column])

        boundary = F - radius * radius / 2
        g = [F_first[0], F_first[1], boundary]
        Dg = [
            [F_second[0][0], F_second[0][1], F_second[0][2]],
            [F_second[1][0], F_second[1][1], F_second[1][2]],
            [F_first[0], F_first[1], F_first[2]],
        ]
        H = [
            [F_second[0][0], F_second[0][1]],
            [F_second[1][0], F_second[1][1]],
        ]
        det_H = H[0][0] * H[1][1] - H[0][1] * H[1][0]
        det_Dg = (
            Dg[0][0] * (Dg[1][1] * Dg[2][2] - Dg[1][2] * Dg[2][1])
            - Dg[0][1] * (Dg[1][0] * Dg[2][2] - Dg[1][2] * Dg[2][0])
            + Dg[0][2] * (Dg[1][0] * Dg[2][1] - Dg[1][1] * Dg[2][0])
        )
        factorized = F_first[2] * det_H
        return {
            "variables": variables,
            "d": d,
            "d_first": first,
            "d_second": second,
            "separation": separation,
            "F": F,
            "F_first": F_first,
            "F_second": F_second,
            "g": g,
            "Dg": Dg,
            "H_sigma_sigma": H,
            "det_H_sigma_sigma": det_H,
            "det_Dg": det_Dg,
            "Ft_det_H": factorized,
            "det_identity_residual": det_Dg - factorized,
            "precision_bits": precision_bits,
        }


def _contains_exact(value: arb, expected: Fraction) -> bool:
    return bool(value.contains(exact_arb(expected)))


def _bounds(value: arb) -> dict[str, str]:
    return {
        "lower": str(value.lower()),
        "upper": str(value.upper()),
    }


def build_fixture() -> dict[str, Any]:
    zero = dyadic_json(0)
    one = dyadic_json(1)
    eight = dyadic_json(8)
    half = dyadic_json(Fraction(1, 2))
    eighth = dyadic_json(Fraction(1, 8))
    coefficient_zero = {"x": zero, "y": zero, "p": zero, "q": zero}
    transverse_y = {"x": zero, "y": eight, "p": zero, "q": zero}
    point_zero = point_interval(0)
    return {
        "schema_version": FIXTURE_SCHEMA,
        "fixture_id": "finite-k1-regular-inward-root-v1",
        "target_dimension": 3,
        "transverse_dimension": 2,
        "winding_axis": 2,
        "winding_orientations": [1, -1],
        "metric_diagonal": [one, one, one],
        "lattice_shift": [zero, zero, zero],
        "radius": half,
        "relative_centre": [half, zero],
        "relative_velocity": [dyadic_json(-1), zero],
        "wave_numbers": [eighth],
        "strings": [
            [[dict(coefficient_zero), dict(transverse_y)]],
            [[dict(coefficient_zero), dict(transverse_y)]],
        ],
        "root_box": {
            "sigma1": point_zero,
            "sigma2": point_zero,
            "time": point_zero,
        },
        "control_box": {
            "sigma1": closed_interval(Fraction(-1, 8), Fraction(1, 8)),
            "sigma2": closed_interval(Fraction(-1, 8), Fraction(1, 8)),
            "time": closed_interval(Fraction(-1, 16), Fraction(1, 16)),
        },
        "expected_point_values": {
            "F_sigma1": zero,
            "F_sigma2": zero,
            "F_time": dyadic_json(Fraction(-1, 2)),
            "F_boundary": zero,
            "H_11": dyadic_json(2),
            "H_12": zero,
            "H_22": dyadic_json(2),
            "det_Dg": dyadic_json(-2),
            "Ft_det_H": dyadic_json(-2),
        },
    }


def normalized_lf_sha256(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def build_report(fixture: Mapping[str, Any]) -> dict[str, Any]:
    backend = check_backend()
    result = evaluate_interval_jets(fixture, "root_box")
    expected = {
        key: dyadic_fraction(
            value, f"$.expected_point_values.{key}"
        )
        for key, value in fixture["expected_point_values"].items()
    }
    gates = {
        "F_sigma1_contains_zero": _contains_exact(
            result["F_first"][0], expected["F_sigma1"]
        ),
        "F_sigma2_contains_zero": _contains_exact(
            result["F_first"][1], expected["F_sigma2"]
        ),
        "F_time_contains_expected": _contains_exact(
            result["F_first"][2], expected["F_time"]
        ),
        "boundary_contains_zero": _contains_exact(
            result["g"][2], expected["F_boundary"]
        ),
        "H11_contains_expected": _contains_exact(
            result["H_sigma_sigma"][0][0], expected["H_11"]
        ),
        "H12_contains_expected": _contains_exact(
            result["H_sigma_sigma"][0][1], expected["H_12"]
        ),
        "H22_contains_expected": _contains_exact(
            result["H_sigma_sigma"][1][1], expected["H_22"]
        ),
        "det_Dg_contains_expected": _contains_exact(
            result["det_Dg"], expected["det_Dg"]
        ),
        "Ft_det_H_contains_expected": _contains_exact(
            result["Ft_det_H"], expected["Ft_det_H"]
        ),
        "det_factorization_residual_contains_zero": bool(
            result["det_identity_residual"].contains(arb(0))
        ),
        "inward_flux_strictly_negative": bool(
            result["F_first"][2].upper() < arb(0)
        ),
        "spatial_hessian_diagonal_strictly_positive": bool(
            result["H_sigma_sigma"][0][0].lower() > arb(0)
            and result["H_sigma_sigma"][1][1].lower() > arb(0)
            and result["det_H_sigma_sigma"].lower() > arb(0)
        ),
    }
    failed = sorted(name for name, passed in gates.items() if not passed)
    payload = {
        "schema_version": REPORT_SCHEMA,
        "fixture_semantic_sha256": canonical_sha256(fixture),
        "backend": backend,
        "precision_bits": DEFAULT_PRECISION_BITS,
        "gates": gates,
        "failed_gates": failed,
        "point_enclosures": {
            "F_sigma1": _bounds(result["F_first"][0]),
            "F_sigma2": _bounds(result["F_first"][1]),
            "F_time": _bounds(result["F_first"][2]),
            "F_boundary": _bounds(result["g"][2]),
            "H11": _bounds(result["H_sigma_sigma"][0][0]),
            "H12": _bounds(result["H_sigma_sigma"][0][1]),
            "H22": _bounds(result["H_sigma_sigma"][1][1]),
            "det_Dg": _bounds(result["det_Dg"]),
            "Ft_det_H": _bounds(result["Ft_det_H"]),
            "det_identity_residual": _bounds(
                result["det_identity_residual"]
            ),
        },
        "code_inventory": {
            "arb_interval_jets.py": normalized_lf_sha256(Path(__file__)),
        },
        "scope": {
            "finite_K_interval_jet_fixture": True,
            "outward_rounded_proof_arithmetic": True,
            "candidate_float_arithmetic_authoritative": False,
            "physical_exhaustive_root_solver_complete": False,
            "population_law_computed": False,
            "three_plus_one_selected": False,
        },
        "status": "PASS" if not failed else "FAIL",
    }
    payload["semantic_sha256"] = canonical_sha256(payload)
    return payload


def semantic_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(
            semantic_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            semantic_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    if arguments.write and arguments.check:
        raise SystemExit("--write and --check are mutually exclusive")

    fixture = build_fixture()
    validate_fixture(fixture)
    report = build_report(fixture)
    if arguments.write:
        write_json(arguments.fixture, fixture)
        write_json(arguments.report, report)
    elif arguments.check:
        stored_fixture = load_strict_json(arguments.fixture)
        stored_report = load_strict_json(arguments.report)
        if not semantic_equal(stored_fixture, fixture):
            raise SystemExit("stored Arb fixture differs from regeneration")
        if not semantic_equal(stored_report, report):
            raise SystemExit("stored Arb report differs from regeneration")
    summary = {
        "fixture_semantic_sha256": canonical_sha256(fixture),
        "report_semantic_sha256": report["semantic_sha256"],
        "status": report["status"],
    }
    print(
        json.dumps(
            summary,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
