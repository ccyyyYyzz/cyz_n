#!/usr/bin/env python3
"""Source-bound Arb interval jets for the registered physical K=1 problem.

The public evaluator accepts only the physical problem committed by
``source_state_bridge_fixture.json``.  Every registered scalar and every box
endpoint is converted from a reduced exact dyadic to an Arb ball; all
trigonometric and algebraic operations are then performed with Arb outward
rounding.

The three jet variables are ordered as ``(sigma1, sigma2, t)``.  Target-space
components are ordered as axes ``0..8``.
"""

from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

import flint
from flint import arb, ctx


DEFAULT_PRECISION_BITS = 192
MINIMUM_PRECISION_BITS = 192
PYTHON_FLINT_VERSION = "0.9.0"
FLINT_VERSION = "3.6.0"
PHYSICAL_PROBLEM_SEMANTIC_SHA256 = (
    "1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca"
)

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE_BRIDGE_FIXTURE = HERE / "source_state_bridge_fixture.json"
VARIABLE_ORDER = ("sigma1", "sigma2", "t")
TARGET_DIMENSION = 9
TRANSVERSE_DIMENSION = 8


class PhysicalJetError(ValueError):
    """A physical-problem, exact-box, or Arb-runtime gate failed."""


def _fail(path: str, message: str) -> None:
    raise PhysicalJetError(f"{path}: {message}")


def _exact_keys(
    value: Any, expected: set[str], path: str
) -> Mapping[str, Any]:
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


def _reject_duplicate_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PhysicalJetError(f"$: duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise PhysicalJetError(f"$: non-finite JSON token {value!r}")


def _reject_float(value: str) -> None:
    raise PhysicalJetError(
        f"$: non-dyadic JSON floating-point token {value!r}"
    )


def load_strict_json(path: Path) -> Any:
    """Load JSON while rejecting duplicate keys, floats, and non-finite tokens."""

    with path.open("r", encoding="utf-8", newline=None) as handle:
        return json.load(
            handle,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
            parse_float=_reject_float,
        )


def _assert_float_free_json(value: Any, path: str = "$") -> None:
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                _fail(path, "JSON object key is not a string")
            _assert_float_free_json(item, f"{path}.{key}")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _assert_float_free_json(item, f"{path}[{index}]")
        return
    if value is None or type(value) in {str, int, bool}:
        return
    _fail(path, f"non-JSON or floating value of type {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    """Return the exact canonical byte convention used by the source bridge."""

    _assert_float_free_json(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def semantic_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def validate_physical_problem(problem: Any) -> str:
    """Bind evaluation to the single registered physical problem."""

    if type(problem) is not dict:
        _fail("$.physical_problem", "expected an object")
    digest = semantic_sha256(problem)
    if digest != PHYSICAL_PROBLEM_SEMANTIC_SHA256:
        _fail(
            "$.physical_problem",
            "semantic SHA-256 is not the source-code-pinned physical problem "
            f"({digest})",
        )
    return digest


def load_registered_physical_problem(
    path: Path = DEFAULT_SOURCE_BRIDGE_FIXTURE,
) -> dict[str, Any]:
    """Load and verify the registered problem from the source-bridge fixture."""

    fixture = load_strict_json(path)
    if type(fixture) is not dict:
        _fail("$", "source bridge fixture must be an object")
    if "physical_problem" not in fixture:
        _fail("$", "source bridge fixture lacks physical_problem")
    if "physical_problem_semantic_sha256" not in fixture:
        _fail("$", "source bridge fixture lacks its problem digest")
    if (
        fixture["physical_problem_semantic_sha256"]
        != PHYSICAL_PROBLEM_SEMANTIC_SHA256
    ):
        _fail(
            "$.physical_problem_semantic_sha256",
            "fixture declaration differs from the source-code pin",
        )
    problem = fixture["physical_problem"]
    validate_physical_problem(problem)
    return problem


def dyadic_fraction(value: Any, path: str = "$dyadic") -> Fraction:
    """Parse one canonical reduced ``numerator / 2**exponent`` scalar."""

    item = _exact_keys(value, {"numerator", "exponent"}, path)
    numerator = _integer(item["numerator"], f"{path}.numerator")
    exponent = _integer(item["exponent"], f"{path}.exponent")
    if exponent < 0:
        _fail(f"{path}.exponent", "must be nonnegative")
    if numerator == 0 and exponent != 0:
        _fail(path, "zero must use exponent zero")
    if numerator != 0 and exponent > 0 and numerator % 2 == 0:
        _fail(path, "dyadic is not reduced")
    return Fraction(numerator, 2**exponent)


def dyadic_json(value: Fraction | int) -> dict[str, int]:
    """Serialize a dyadic rational in unique reduced form."""

    fraction = Fraction(value)
    denominator = fraction.denominator
    if denominator & (denominator - 1):
        raise PhysicalJetError("value is not dyadic")
    exponent = denominator.bit_length() - 1
    numerator = fraction.numerator
    while exponent and numerator % 2 == 0:
        numerator //= 2
        exponent -= 1
    if numerator == 0:
        exponent = 0
    return {"numerator": numerator, "exponent": exponent}


def point_interval(value: Fraction | int) -> dict[str, Any]:
    encoded = dyadic_json(value)
    return {"lo": encoded, "hi": dict(encoded)}


def closed_interval(
    lower: Fraction | int, upper: Fraction | int
) -> dict[str, Any]:
    if Fraction(lower) > Fraction(upper):
        raise PhysicalJetError("reversed interval")
    return {"lo": dyadic_json(lower), "hi": dyadic_json(upper)}


def _arb_tuple(value: Fraction) -> tuple[int, int]:
    denominator = value.denominator
    if denominator & (denominator - 1):
        raise PhysicalJetError("only dyadic Arb inputs are permitted")
    return value.numerator, -(denominator.bit_length() - 1)


def exact_arb(value: Fraction | int) -> arb:
    return arb(_arb_tuple(Fraction(value)))


def _parse_interval(
    value: Any, path: str
) -> tuple[Fraction, Fraction]:
    item = _exact_keys(value, {"lo", "hi"}, path)
    lower = dyadic_fraction(item["lo"], f"{path}.lo")
    upper = dyadic_fraction(item["hi"], f"{path}.hi")
    if lower > upper:
        _fail(path, "interval is reversed")
    return lower, upper


def interval_arb(value: Any, path: str = "$interval") -> arb:
    """Create the exact hull of two registered dyadic endpoints."""

    lower, upper = _parse_interval(value, path)
    midpoint = (lower + upper) / 2
    radius = (upper - lower) / 2
    return arb(_arb_tuple(midpoint), _arb_tuple(radius))


@contextmanager
def precision(bits: int) -> Iterator[None]:
    if type(bits) is not int or bits < MINIMUM_PRECISION_BITS:
        raise PhysicalJetError(
            f"Arb precision must be an integer of at least "
            f"{MINIMUM_PRECISION_BITS} bits"
        )
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
        raise PhysicalJetError(
            "python-flint runtime mismatch: "
            f"expected {PYTHON_FLINT_VERSION}, got {python_flint!r}"
        )
    if flint_version != FLINT_VERSION:
        raise PhysicalJetError(
            "FLINT runtime mismatch: "
            f"expected {FLINT_VERSION}, got {flint_version!r}"
        )
    return {
        "python_flint": python_flint,
        "flint": flint_version,
        "arithmetic": "arb outward-rounded balls",
    }


def _exact_arb_fraction(value: arb) -> Fraction:
    if not isinstance(value, arb):
        raise PhysicalJetError("expected an Arb value")
    try:
        mantissa, exponent = value.man_exp()
    except (TypeError, ValueError) as error:
        raise PhysicalJetError(
            "Arb endpoint is not exact and finite"
        ) from error
    result = Fraction(int(mantissa))
    if int(exponent) >= 0:
        return result * (2 ** int(exponent))
    return result / (2 ** (-int(exponent)))


def arb_exact_endpoints(
    value: arb, *, precision_bits: int = DEFAULT_PRECISION_BITS
) -> dict[str, dict[str, int]]:
    """Serialize outward Arb bounds as exact reduced dyadic endpoints.

    ``arb.lower`` and ``arb.upper`` round respectively toward minus and plus
    infinity at the requested precision.  Their exact floating-point values
    are then serialized without decimal text or binary64 conversion.
    """

    if not isinstance(value, arb):
        raise PhysicalJetError("expected an Arb value")
    with precision(precision_bits):
        lower = _exact_arb_fraction(value.lower())
        upper = _exact_arb_fraction(value.upper())
    return {"lo": dyadic_json(lower), "hi": dyadic_json(upper)}


# Descriptive alias retained as part of the stable serialization API.
serialize_arb_exact_endpoints = arb_exact_endpoints


def registered_seam_phase_mismatch(
    problem: Mapping[str, Any],
    *,
    precision_bits: int = DEFAULT_PRECISION_BITS,
) -> arb:
    """Return ``k*L_w - 2*pi`` for the frozen dyadic physical problem.

    The registered ``L_w`` is built from the binary64 value of pi whereas
    Arb's ``pi`` is the mathematical constant.  Consequently this quantity is
    small but provably nonzero; callers must not silently identify the two
    sigma-domain endpoints as an exact analytic seam.
    """

    validate_physical_problem(problem)
    check_backend()
    wave_number_fraction = dyadic_fraction(
        problem["kinematics"]["strings"][0]["modes"][0]["wave_number"],
        "$.physical_problem.kinematics.strings[0].modes[0].wave_number",
    )
    winding_length_fraction = dyadic_fraction(
        problem["f1_convention"]["winding_length"],
        "$.physical_problem.f1_convention.winding_length",
    )
    with precision(precision_bits):
        return (
            exact_arb(wave_number_fraction)
            * exact_arb(winding_length_fraction)
            - 2 * arb.pi()
        )


def _validate_box(
    problem: Mapping[str, Any], box: Any
) -> dict[str, tuple[Fraction, Fraction]]:
    item = _exact_keys(box, set(VARIABLE_ORDER), "$.box")
    parsed = {
        name: _parse_interval(item[name], f"$.box.{name}")
        for name in VARIABLE_ORDER
    }
    sigma_domains = problem["worldsheet"]["sigma_domains"]
    for name, domain in zip(("sigma1", "sigma2"), sigma_domains):
        domain_lower = dyadic_fraction(
            domain["lower"], f"$.physical_problem.worldsheet.{name}.lower"
        )
        domain_upper = dyadic_fraction(
            domain["upper"], f"$.physical_problem.worldsheet.{name}.upper"
        )
        lower, upper = parsed[name]
        if lower < domain_lower or upper > domain_upper:
            _fail(
                f"$.box.{name}",
                "box lies outside the registered worldsheet-domain closure",
            )
    time_lower = dyadic_fraction(
        problem["observation"]["t0"], "$.physical_problem.observation.t0"
    )
    time_upper = dyadic_fraction(
        problem["observation"]["t1"], "$.physical_problem.observation.t1"
    )
    lower, upper = parsed["t"]
    if lower < time_lower or upper > time_upper:
        _fail(
            "$.box.t",
            "box lies outside the registered observation-window closure",
        )
    return parsed


def _validate_lattice_image(value: Any) -> tuple[int, ...]:
    if value is None:
        return (0,) * TARGET_DIMENSION
    if type(value) not in {list, tuple} or len(value) != TARGET_DIMENSION:
        _fail(
            "$.lattice_image",
            f"expected a vector of length {TARGET_DIMENSION}",
        )
    return tuple(
        _integer(component, f"$.lattice_image[{index}]")
        for index, component in enumerate(value)
    )


def _validate_radius(
    problem: Mapping[str, Any], value: Any
) -> Fraction:
    encoded = (
        problem["hysteresis"]["r_out"]
        if value is None
        else value
    )
    radius = dyadic_fraction(encoded, "$.radius")
    if radius <= 0:
        _fail("$.radius", "must be strictly positive")
    return radius


def _arb_vector(
    values: Any, length: int, path: str
) -> list[arb]:
    if type(values) is not list or len(values) != length:
        _fail(path, f"expected a vector of length {length}")
    return [
        exact_arb(dyadic_fraction(value, f"{path}[{index}]"))
        for index, value in enumerate(values)
    ]


def _arb_matrix(
    values: Any, size: int, path: str
) -> list[list[arb]]:
    if type(values) is not list or len(values) != size:
        _fail(path, f"expected a {size}x{size} matrix")
    return [
        _arb_vector(row, size, f"{path}[{row_index}]")
        for row_index, row in enumerate(values)
    ]


def _zero_vector(length: int) -> list[arb]:
    return [arb(0) for _ in range(length)]


def _zero_matrix(rows: int, columns: int) -> list[list[arb]]:
    return [[arb(0) for _ in range(columns)] for _ in range(rows)]


def _metric_dot(
    left: Sequence[arb],
    metric: Sequence[Sequence[arb]],
    right: Sequence[arb],
) -> arb:
    if not (
        len(left) == len(metric) == len(right)
        and all(len(row) == len(right) for row in metric)
    ):
        raise PhysicalJetError("metric-dot shape mismatch")
    total = arb(0)
    for row, left_value in enumerate(left):
        for column, right_value in enumerate(right):
            total += (
                left_value * metric[row][column] * right_value
            )
    return total


def _matrix_integer_vector(
    matrix: Sequence[Sequence[arb]], vector: Sequence[int]
) -> list[arb]:
    if not (
        len(matrix) == len(vector)
        and all(len(row) == len(vector) for row in matrix)
    ):
        raise PhysicalJetError("matrix/vector shape mismatch")
    result: list[arb] = []
    for row in matrix:
        total = arb(0)
        for coefficient, integer in zip(row, vector):
            total += coefficient * integer
        result.append(total)
    return result


def _mode_component_jet(
    mode: Mapping[str, Any],
    component: int,
    sigma: arb,
    time: arb,
    path: str,
) -> tuple[arb, arb, arb, arb, arb, arb]:
    """Return ``Y, Y_sigma, Y_t, Y_ss, Y_st, Y_tt`` for one mode."""

    wave_number = exact_arb(
        dyadic_fraction(mode["wave_number"], f"{path}.wave_number")
    )
    if wave_number.contains(arb(0)):
        _fail(f"{path}.wave_number", "wave number contains zero")
    x0 = exact_arb(
        dyadic_fraction(
            mode["initial_x"][component],
            f"{path}.initial_x[{component}]",
        )
    )
    y0 = exact_arb(
        dyadic_fraction(
            mode["initial_y"][component],
            f"{path}.initial_y[{component}]",
        )
    )
    p0 = exact_arb(
        dyadic_fraction(
            mode["initial_p"][component],
            f"{path}.initial_p[{component}]",
        )
    )
    q0 = exact_arb(
        dyadic_fraction(
            mode["initial_q"][component],
            f"{path}.initial_q[{component}]",
        )
    )

    kt = wave_number * time
    ks = wave_number * sigma
    ct, st = kt.cos(), kt.sin()
    cs, ss = ks.cos(), ks.sin()

    x_t = x0 * ct + (p0 / wave_number) * st
    y_t = y0 * ct + (q0 / wave_number) * st
    p_t = -wave_number * x0 * st + p0 * ct
    q_t = -wave_number * y0 * st + q0 * ct

    value = x_t * cs + y_t * ss
    sigma_first = wave_number * (-x_t * ss + y_t * cs)
    time_first = p_t * cs + q_t * ss
    sigma_second = -(wave_number * wave_number) * value
    sigma_time = wave_number * (-p_t * ss + q_t * cs)
    time_second = sigma_second
    return (
        value,
        sigma_first,
        time_first,
        sigma_second,
        sigma_time,
        time_second,
    )


def evaluate_physical_jets(
    problem: Mapping[str, Any],
    box: Mapping[str, Any],
    lattice_image: Sequence[int] | None = None,
    radius: Mapping[str, Any] | None = None,
    *,
    precision_bits: int = DEFAULT_PRECISION_BITS,
) -> dict[str, Any]:
    """Evaluate the registered physical ``d/F/g_r`` jets on one exact box.

    Parameters
    ----------
    problem:
        The exact ``physical_problem`` object from the source-bridge fixture.
        No other problem hash is accepted.
    box:
        Exact-key mapping ``sigma1, sigma2, t``.  Each value is a closed
        interval whose ``lo`` and ``hi`` are reduced dyadics.
    lattice_image:
        Integer vector ``n`` in ``Z^9``.  The default is the zero image and
        ``separation = d - Lambda*n``.
    radius:
        Positive reduced dyadic used in ``g_r``.  The registered ``r_out`` is
        the default.
    precision_bits:
        Arb working precision, at least 192 bits.
    """

    problem_digest = validate_physical_problem(problem)
    parsed_box = _validate_box(problem, box)
    image = _validate_lattice_image(lattice_image)
    radius_fraction = _validate_radius(problem, radius)
    check_backend()

    with precision(precision_bits):
        variables = [
            interval_arb(box[name], f"$.box.{name}")
            for name in VARIABLE_ORDER
        ]
        sigma1, sigma2, time = variables
        # Parsing above is intentionally retained as a pre-Arb domain proof.
        if tuple(parsed_box) != VARIABLE_ORDER:
            raise PhysicalJetError("internal variable-order mismatch")

        kinematics = problem["kinematics"]
        initial_time = exact_arb(
            dyadic_fraction(
                kinematics["initial_time"],
                "$.physical_problem.kinematics.initial_time",
            )
        )
        mode_time = time - initial_time
        centres = kinematics["centres_Q1_Q2"]
        Q1 = _arb_vector(
            centres["Q1"],
            TRANSVERSE_DIMENSION,
            "$.physical_problem.kinematics.centres_Q1_Q2.Q1",
        )
        Q2 = _arb_vector(
            centres["Q2"],
            TRANSVERSE_DIMENSION,
            "$.physical_problem.kinematics.centres_Q1_Q2.Q2",
        )
        strings = kinematics["strings"]
        velocities = [
            _arb_vector(
                string["transverse_velocity"],
                TRANSVERSE_DIMENSION,
                f"$.physical_problem.kinematics.strings[{index}]"
                ".transverse_velocity",
            )
            for index, string in enumerate(strings)
        ]

        d = _zero_vector(TARGET_DIMENSION)
        d_a = [_zero_vector(TARGET_DIMENSION) for _ in range(3)]
        d_ab = [
            [_zero_vector(TARGET_DIMENSION) for _ in range(3)]
            for _ in range(3)
        ]

        for component in range(TRANSVERSE_DIMENSION):
            string_jets: list[list[arb]] = []
            for string_index, (string, sigma) in enumerate(
                zip(strings, (sigma1, sigma2))
            ):
                accumulated = [arb(0) for _ in range(6)]
                for mode_index, mode in enumerate(string["modes"]):
                    jet = _mode_component_jet(
                        mode,
                        component,
                        sigma,
                        mode_time,
                        "$.physical_problem.kinematics.strings"
                        f"[{string_index}].modes[{mode_index}]",
                    )
                    for derivative_index, value in enumerate(jet):
                        accumulated[derivative_index] += value
                string_jets.append(accumulated)

            jet1, jet2 = string_jets
            relative_velocity = (
                velocities[0][component] - velocities[1][component]
            )
            # Q1-Q2 occurs exactly once.  All string-2 mode contributions
            # carry the minus sign from d = X1-X2.
            d[component] = (
                Q1[component]
                - Q2[component]
                + relative_velocity * mode_time
                + jet1[0]
                - jet2[0]
            )
            d_a[0][component] = jet1[1]
            d_a[1][component] = -jet2[1]
            d_a[2][component] = (
                relative_velocity + jet1[2] - jet2[2]
            )
            d_ab[0][0][component] = jet1[3]
            d_ab[1][1][component] = -jet2[3]
            d_ab[2][2][component] = jet1[5] - jet2[5]
            d_ab[0][2][component] = jet1[4]
            d_ab[2][0][component] = jet1[4]
            d_ab[1][2][component] = -jet2[4]
            d_ab[2][1][component] = -jet2[4]

        winding_axis = problem["dimensions"]["winding_axis"]
        orientation1, orientation2 = problem["worldsheet"][
            "winding_orientations"
        ]
        d[winding_axis] = (
            orientation1 * sigma1 - orientation2 * sigma2
        )
        d_a[0][winding_axis] = arb(orientation1)
        d_a[1][winding_axis] = arb(-orientation2)

        metric = _arb_matrix(
            problem["target_torus"]["G"],
            TARGET_DIMENSION,
            "$.physical_problem.target_torus.G",
        )
        lattice = _arb_matrix(
            problem["target_torus"]["Lambda"],
            TARGET_DIMENSION,
            "$.physical_problem.target_torus.Lambda",
        )
        lattice_shift = _matrix_integer_vector(lattice, image)
        separation = [
            value - shift for value, shift in zip(d, lattice_shift)
        ]

        F = _metric_dot(separation, metric, separation) / 2
        F_a = [
            _metric_dot(d_a[axis], metric, separation)
            for axis in range(3)
        ]
        F_ab = _zero_matrix(3, 3)
        for row in range(3):
            for column in range(3):
                F_ab[row][column] = _metric_dot(
                    d_ab[row][column], metric, separation
                ) + _metric_dot(d_a[row], metric, d_a[column])

        radius_arb = exact_arb(radius_fraction)
        boundary = F - radius_arb * radius_arb / 2
        g_r = [F_a[0], F_a[1], boundary]
        Dg_r = [
            [F_ab[0][0], F_ab[0][1], F_ab[0][2]],
            [F_ab[1][0], F_ab[1][1], F_ab[1][2]],
            [F_a[0], F_a[1], F_a[2]],
        ]

        return {
            "problem_sha256": problem_digest,
            "precision_bits": precision_bits,
            "variable_order": VARIABLE_ORDER,
            "variables": variables,
            "lattice_image": image,
            "lattice_shift": lattice_shift,
            "radius": radius_arb,
            "d": d,
            "d_a": d_a,
            "d_ab": d_ab,
            "separation": separation,
            "F": F,
            "F_a": F_a,
            "F_ab": F_ab,
            "g_r": g_r,
            "Dg_r": Dg_r,
        }
