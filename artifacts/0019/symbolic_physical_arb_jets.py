#!/usr/bin/env python3
"""Outward-rounded Arb jets for the symbolic-pi closed-string lift.

The worldsheet coordinates are ``(u1, u2, t)`` with ``u_i`` normalized
modulo one.  A mode with integer harmonic ``m`` has spatial phase
``2*pi*m*u`` and time frequency ``m/8``.  The winding coordinate is also
normalized, while its physical length is retained by
``G[8,8] = (16*pi)**2``.

No numerical comparison of endpoint balls is used to establish a seam.
The exact seam map follows from integer Fourier harmonics and the integer
winding image shifts returned by :func:`exact_seam_image_shift`.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence

from flint import arb

import physical_arb_jets as base


DEFAULT_PRECISION_BITS = 192
MINIMUM_PRECISION_BITS = 192
VARIABLE_ORDER = ("u1", "u2", "t")
TARGET_DIMENSION = 9
TRANSVERSE_DIMENSION = 8
WINDING_AXIS = 8
TRANSVERSE_PERIOD = Fraction(8)
NORMALIZED_WINDING_PERIOD = Fraction(1)
WINDING_LENGTH_COEFFICIENT = Fraction(16)
TIME_FREQUENCY_DENOMINATOR = 8

SymbolicPhysicalJetError = base.PhysicalJetError
dyadic_fraction = base.dyadic_fraction
dyadic_json = base.dyadic_json
point_interval = base.point_interval
closed_interval = base.closed_interval
exact_arb = base.exact_arb
interval_arb = base.interval_arb
precision = base.precision
check_backend = base.check_backend
arb_exact_endpoints = base.arb_exact_endpoints
serialize_arb_exact_endpoints = base.serialize_arb_exact_endpoints


def _fail(path: str, message: str) -> None:
    raise SymbolicPhysicalJetError(f"{path}: {message}")


def _integer(value: Any, path: str) -> int:
    if type(value) is not int:
        _fail(path, "expected an integer; booleans are forbidden")
    return value


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if type(value) is not dict:
        _fail(path, "expected an object")
    return value


def _sequence(value: Any, length: int, path: str) -> Sequence[Any]:
    if type(value) not in {list, tuple} or len(value) != length:
        _fail(path, f"expected a sequence of length {length}")
    return value


def _parse_interval(
    value: Any, path: str
) -> tuple[Fraction, Fraction]:
    item = _mapping(value, path)
    if set(item) != {"lo", "hi"}:
        _fail(path, "expected exact keys ['hi', 'lo']")
    lower = dyadic_fraction(item["lo"], f"{path}.lo")
    upper = dyadic_fraction(item["hi"], f"{path}.hi")
    if lower > upper:
        _fail(path, "interval is reversed")
    return lower, upper


def _dyadic_vector(
    value: Any, length: int, path: str
) -> tuple[Fraction, ...]:
    items = _sequence(value, length, path)
    return tuple(
        dyadic_fraction(item, f"{path}[{index}]")
        for index, item in enumerate(items)
    )


def _source_problem(problem: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the direct closed-string problem carrying source coefficients."""
    if "kinematics" in problem:
        return problem
    _fail("$.problem", "missing direct exact-source kinematics")
    raise AssertionError("unreachable")


def _normalized_worldsheet(problem: Mapping[str, Any]) -> Mapping[str, Any]:
    candidate = problem.get("worldsheet")
    if type(candidate) is dict:
        return candidate
    _fail("$.problem", "missing normalized worldsheet object")
    raise AssertionError("unreachable")


def _u_domains(problem: Mapping[str, Any]) -> tuple[Any, Any]:
    registry = _mapping(
        problem.get("variable_registry"), "$.problem.variable_registry"
    )
    if registry.get("variable_order") != list(VARIABLE_ORDER):
        _fail(
            "$.problem.variable_registry.variable_order",
            "expected ['u1','u2','t']",
        )
    domains = registry.get("domains")
    if type(domains) is dict:
        if not {"u1", "u2", "t"} <= set(domains):
            _fail(
                "$.problem.variable_registry.domains",
                "missing u1/u2/t domain",
            )
        return domains["u1"], domains["u2"]
    items = _sequence(
        domains, 3, "$.problem.variable_registry.domains"
    )
    return items[0], items[1]


def _orientations(
    problem: Mapping[str, Any], source: Mapping[str, Any]
) -> tuple[int, int]:
    worldsheet = _normalized_worldsheet(problem)
    raw = worldsheet.get("orientations")
    values = _sequence(raw, 2, "$.problem.worldsheet.orientations")
    result = (
        _integer(values[0], "$.problem.worldsheet.orientations[0]"),
        _integer(values[1], "$.problem.worldsheet.orientations[1]"),
    )
    if result != (1, -1):
        _fail(
            "$.problem.worldsheet.orientations",
            "registered lift requires orientations (+1,-1)",
        )
    return result


def _observation(problem: Mapping[str, Any], source: Mapping[str, Any]) -> Mapping[str, Any]:
    candidate = problem.get("observation")
    if type(candidate) is dict:
        return candidate
    candidate = source.get("observation")
    if type(candidate) is dict:
        return candidate
    _fail("$.problem.observation", "missing observation window")
    raise AssertionError("unreachable")


def _hysteresis(problem: Mapping[str, Any], source: Mapping[str, Any]) -> Mapping[str, Any]:
    candidate = problem.get("hysteresis")
    if type(candidate) is dict:
        return candidate
    candidate = source.get("hysteresis")
    if type(candidate) is dict:
        return candidate
    _fail("$.problem.hysteresis", "missing hysteresis radii")
    raise AssertionError("unreachable")


def _periods(problem: Mapping[str, Any]) -> tuple[Fraction, ...]:
    torus = _mapping(problem.get("target_torus"), "$.problem.target_torus")
    raw = _sequence(
        torus.get("periods"),
        TARGET_DIMENSION,
        "$.problem.target_torus.periods",
    )
    periods = tuple(
        _pi_zero_fraction(
            value, f"$.problem.target_torus.periods[{index}]"
        )
        for index, value in enumerate(raw)
    )
    expected = (TRANSVERSE_PERIOD,) * 8 + (NORMALIZED_WINDING_PERIOD,)
    if periods != expected:
        _fail(
            "$.problem.target_torus",
            "normalized periods must be (8,...,8,1)",
        )
    return periods


def _symbolic_scalar_parts(value: Any, path: str) -> tuple[Fraction, int]:
    """Parse the lift's strict ``q*pi**e`` scalar.

    The atom has the unique object form
    ``{numerator, denominator, pi_exponent}``.  The rational coefficient is
    stored in reduced form with positive denominator; zero is uniquely
    ``{0,1,0}``.
    """

    item = _mapping(value, path)
    if set(item) != {"numerator", "denominator", "pi_exponent"}:
        _fail(
            path,
            "expected strict q*pi^e atom keys "
            "['denominator','numerator','pi_exponent']",
        )
    numerator = _integer(item["numerator"], f"{path}.numerator")
    denominator = _integer(item["denominator"], f"{path}.denominator")
    power = _integer(item["pi_exponent"], f"{path}.pi_exponent")
    if denominator <= 0:
        _fail(f"{path}.denominator", "must be positive")
    coefficient = Fraction(numerator, denominator)
    if coefficient.numerator != numerator or coefficient.denominator != denominator:
        _fail(path, "rational coefficient is not reduced")
    if coefficient == 0 and (denominator != 1 or power != 0):
        _fail(path, "zero must be encoded exactly as {0,1,0}")
    return coefficient, power


def symbolic_atom(
    coefficient: Fraction | int, pi_exponent: int = 0
) -> dict[str, int]:
    coefficient = Fraction(coefficient)
    if type(pi_exponent) is not int:
        raise SymbolicPhysicalJetError("pi exponent must be an integer")
    if coefficient == 0:
        pi_exponent = 0
    return {
        "numerator": coefficient.numerator,
        "denominator": coefficient.denominator,
        "pi_exponent": pi_exponent,
    }


def _pi_zero_fraction(value: Any, path: str) -> Fraction:
    coefficient, power = _symbolic_scalar_parts(value, path)
    if power != 0:
        _fail(path, "expected a pi^0 rational")
    return coefficient


def _rational_arb(value: Fraction | int) -> arb:
    rational = Fraction(value)
    denominator = rational.denominator
    if denominator & (denominator - 1) == 0:
        return exact_arb(rational)
    return arb(rational.numerator) / denominator


def symbolic_scalar_arb(value: Any, path: str = "$symbolic") -> arb:
    coefficient, power = _symbolic_scalar_parts(value, path)
    result = _rational_arb(coefficient)
    if power > 0:
        result *= arb.pi() ** power
    elif power < 0:
        result /= arb.pi() ** (-power)
    return result


@dataclass(frozen=True)
class _Convention:
    source: Mapping[str, Any]
    orientations: tuple[int, int]
    periods: tuple[Fraction, ...]


def _dyadic_atom(value: Any, path: str) -> dict[str, int]:
    return symbolic_atom(dyadic_fraction(value, path))


def build_problem_adapter(
    source_problem: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the jet-facing closed-string view of the pinned dyadic source.

    This adapter is intentionally deterministic and contains no binary64
    conversion.  The canonical lift module adds its registry and provenance
    commitments around the same mathematical fields.
    """

    source = _mapping(source_problem, "$.source_problem")
    kinematics = _mapping(
        source.get("kinematics"), "$.source_problem.kinematics"
    )
    strings_out: list[dict[str, Any]] = []
    for string_index, string_value in enumerate(
        _sequence(
            kinematics.get("strings"),
            2,
            "$.source_problem.kinematics.strings",
        )
    ):
        string = _mapping(
            string_value,
            f"$.source_problem.kinematics.strings[{string_index}]",
        )
        modes_out: list[dict[str, Any]] = []
        modes = string.get("modes")
        if type(modes) is not list or not modes:
            _fail(
                f"$.source_problem.kinematics.strings[{string_index}].modes",
                "expected a nonempty mode list",
            )
        for mode_index, mode_value in enumerate(modes):
            mode = _mapping(
                mode_value,
                "$.source_problem.kinematics.strings"
                f"[{string_index}].modes[{mode_index}]",
            )
            harmonic = _integer(
                mode.get("mode_number"),
                "$.source_problem.kinematics.strings"
                f"[{string_index}].modes[{mode_index}].mode_number",
            )
            frequency = Fraction(harmonic, TIME_FREQUENCY_DENOMINATOR)
            modes_out.append(
                {
                    "mode_number": harmonic,
                    "temporal_angular_frequency": symbolic_atom(frequency),
                    "wave_number": symbolic_atom(frequency),
                    "spatial_phase_coefficient": symbolic_atom(
                        2 * harmonic, 1
                    ),
                    "initial_x": [
                        _dyadic_atom(
                            item,
                            "$.source_problem.kinematics.strings"
                            f"[{string_index}].modes[{mode_index}]"
                            f".initial_x[{component}]",
                        )
                        for component, item in enumerate(mode["initial_x"])
                    ],
                    "initial_y": [
                        _dyadic_atom(
                            item,
                            "$.source_problem.kinematics.strings"
                            f"[{string_index}].modes[{mode_index}]"
                            f".initial_y[{component}]",
                        )
                        for component, item in enumerate(mode["initial_y"])
                    ],
                    "initial_p": [
                        _dyadic_atom(
                            item,
                            "$.source_problem.kinematics.strings"
                            f"[{string_index}].modes[{mode_index}]"
                            f".initial_p[{component}]",
                        )
                        for component, item in enumerate(mode["initial_p"])
                    ],
                    "initial_q": [
                        _dyadic_atom(
                            item,
                            "$.source_problem.kinematics.strings"
                            f"[{string_index}].modes[{mode_index}]"
                            f".initial_q[{component}]",
                        )
                        for component, item in enumerate(mode["initial_q"])
                    ],
                }
            )
        strings_out.append(
            {
                "string_id": string.get("string_id"),
                "orientation": string.get("orientation"),
                "centre_reference": string.get("centre_reference"),
                "transverse_velocity": [
                    _dyadic_atom(
                        item,
                        "$.source_problem.kinematics.strings"
                        f"[{string_index}].transverse_velocity[{component}]",
                    )
                    for component, item in enumerate(
                        string["transverse_velocity"]
                    )
                ],
                "modes": modes_out,
            }
        )
    centres = _mapping(
        kinematics.get("centres_Q1_Q2"),
        "$.source_problem.kinematics.centres_Q1_Q2",
    )
    observation = _mapping(
        source.get("observation"), "$.source_problem.observation"
    )
    hysteresis = _mapping(
        source.get("hysteresis"), "$.source_problem.hysteresis"
    )
    zero, one = symbolic_atom(0), symbolic_atom(1)
    return {
        "schema_version": "cyz-brief-0019-symbolic-pi-closed-string-problem-v1",
        "problem_id": "jet-adapter-index2-symbolic-pi-closed-string-v1",
        "equation_family_version": "f1-normalized-closed-string-k1-v1",
        "dimensions": {
            "target": TARGET_DIMENSION,
            "transverse": TRANSVERSE_DIMENSION,
            "winding_axis": WINDING_AXIS,
        },
        "exact_parameters": {
        "L_star": symbolic_atom(16, 1),
        "T_F": symbolic_atom(Fraction(1, 2), -1),
        "M": symbolic_atom(8),
        "ell_s": symbolic_atom(1),
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
                    "lower": _dyadic_atom(
                        observation["t0"],
                        "$.source_problem.observation.t0",
                    ),
                    "upper": _dyadic_atom(
                        observation["t1"],
                        "$.source_problem.observation.t1",
                    ),
                    "closure": "lower_closed_upper_open",
                },
            },
        },
        "target_torus": {
            "periods": [symbolic_atom(8) for _ in range(8)]
            + [symbolic_atom(1)],
            "metric_diagonal": [symbolic_atom(1) for _ in range(8)]
            + [symbolic_atom(256, 2)],
            "lattice_convention": "diagonal normalized coordinate periods",
        },
        "worldsheet": {
            "orientations": [1, -1],
            "winding_embedding": "xi_i^w=o_i*u_i",
            "seam_image_actions": {
                "u1_plus_1_n8_shift": 1,
                "u2_plus_1_n8_shift": 1,
                "corner_n8_shift": 2,
            },
        },
        "kinematics": {
            "initial_time": _dyadic_atom(
                kinematics["initial_time"],
                "$.source_problem.kinematics.initial_time",
            ),
            "centres_Q1_Q2": {
                name: [
                    _dyadic_atom(
                        item,
                        "$.source_problem.kinematics.centres_Q1_Q2"
                        f".{name}[{component}]",
                    )
                    for component, item in enumerate(centres[name])
                ]
                for name in ("Q1", "Q2")
            },
            "strings": strings_out,
        },
        "hysteresis": {
            "r_in": _dyadic_atom(
                hysteresis["r_in"], "$.source_problem.hysteresis.r_in"
            ),
            "r_out": _dyadic_atom(
                hysteresis["r_out"], "$.source_problem.hysteresis.r_out"
            ),
        },
        "observation": {
            "t0": _dyadic_atom(
                observation["t0"], "$.source_problem.observation.t0"
            ),
            "t1": _dyadic_atom(
                observation["t1"], "$.source_problem.observation.t1"
            ),
        },
    }


def _validate_convention(problem: Any) -> _Convention:
    problem_map = _mapping(problem, "$.problem")
    source = _source_problem(problem_map)
    dimensions = problem_map.get("dimensions", source.get("dimensions"))
    dimensions = _mapping(dimensions, "$.problem.dimensions")
    if (
        dimensions.get("target") != TARGET_DIMENSION
        or dimensions.get("transverse") != TRANSVERSE_DIMENSION
        or dimensions.get("winding_axis") != WINDING_AXIS
    ):
        _fail("$.problem.dimensions", "expected the registered 8+1 split")

    worldsheet = _normalized_worldsheet(problem_map)
    domains = _u_domains(problem_map)
    for index, domain in enumerate(domains):
        domain_map = _mapping(domain, f"$.problem.worldsheet.u_domains[{index}]")
        lower_key = "lower" if "lower" in domain_map else "lo"
        upper_key = "upper" if "upper" in domain_map else "hi"
        if lower_key not in domain_map or upper_key not in domain_map:
            _fail(
                f"$.problem.worldsheet.u_domains[{index}]",
                "missing lower/upper endpoints",
            )
        lower = _pi_zero_fraction(
            domain_map[lower_key],
            f"$.problem.worldsheet.u_domains[{index}].{lower_key}",
        )
        upper = _pi_zero_fraction(
            domain_map[upper_key],
            f"$.problem.worldsheet.u_domains[{index}].{upper_key}",
        )
        if (lower, upper) != (Fraction(0), Fraction(1)):
            _fail(
                f"$.problem.worldsheet.u_domains[{index}]",
                "normalized seam domain must have closure [0,1]",
            )

    orientations = _orientations(problem_map, source)
    periods = _periods(problem_map)

    parameters = _mapping(
        problem_map.get("exact_parameters"), "$.problem.exact_parameters"
    )
    required_parameters = {
        "L_star": (Fraction(16), 1),
        "T_F": (Fraction(1, 2), -1),
        "M": (Fraction(8), 0),
        "ell_s": (Fraction(1), 0),
    }
    for name, expected in required_parameters.items():
        if _symbolic_scalar_parts(
            parameters.get(name), f"$.problem.exact_parameters.{name}"
        ) != expected:
            _fail(
                f"$.problem.exact_parameters.{name}",
                f"expected exact registered value {expected}",
            )
    if _integer(parameters.get("K"), "$.problem.exact_parameters.K") != 1:
        _fail("$.problem.exact_parameters.K", "expected integer cutoff K=1")

    torus = _mapping(problem_map["target_torus"], "$.problem.target_torus")
    metric_diagonal = torus.get("metric_diagonal")
    entries = _sequence(
        metric_diagonal,
        TARGET_DIMENSION,
        "$.problem.target_torus.metric_diagonal",
    )
    for axis in range(8):
        if _symbolic_scalar_parts(
            entries[axis],
            f"$.problem.target_torus.metric_diagonal[{axis}]",
        ) != (Fraction(1), 0):
            _fail(
                f"$.problem.target_torus.metric_diagonal[{axis}]",
                "transverse metric entry must be one",
            )
    if _symbolic_scalar_parts(
        entries[8], "$.problem.target_torus.metric_diagonal[8]"
    ) != (Fraction(256), 2):
        _fail(
            "$.problem.target_torus.metric_diagonal[8]",
            "normalized winding metric must be (16*pi)^2",
        )

    return _Convention(source, orientations, periods)


def _validate_box(
    problem: Mapping[str, Any],
    source: Mapping[str, Any],
    box: Any,
) -> dict[str, tuple[Fraction, Fraction]]:
    item = _mapping(box, "$.box")
    if set(item) != set(VARIABLE_ORDER):
        _fail("$.box", f"expected exact keys {sorted(VARIABLE_ORDER)}")
    parsed = {
        name: _parse_interval(item[name], f"$.box.{name}")
        for name in VARIABLE_ORDER
    }
    for name in ("u1", "u2"):
        lower, upper = parsed[name]
        if lower < 0 or upper > 1:
            _fail(f"$.box.{name}", "box lies outside normalized closure [0,1]")
    observation = _observation(problem, source)
    t0 = _pi_zero_fraction(observation["t0"], "$.problem.observation.t0")
    t1 = _pi_zero_fraction(observation["t1"], "$.problem.observation.t1")
    lower, upper = parsed["t"]
    if lower < t0 or upper > t1:
        _fail("$.box.t", "box lies outside the registered time closure")
    return parsed


def _validate_lattice_image(value: Any) -> tuple[int, ...]:
    if value is None:
        return (0,) * TARGET_DIMENSION
    items = _sequence(value, TARGET_DIMENSION, "$.lattice_image")
    return tuple(
        _integer(component, f"$.lattice_image[{index}]")
        for index, component in enumerate(items)
    )


def _validate_radius(
    problem: Mapping[str, Any],
    source: Mapping[str, Any],
    value: Any,
) -> Fraction:
    hysteresis = _hysteresis(problem, source)
    encoded = hysteresis["r_out"] if value is None else value
    # API overrides remain reduced dyadics; registered radii use lift atoms.
    if type(encoded) is dict and set(encoded) == {
        "numerator",
        "denominator",
        "pi_exponent",
    }:
        radius = _pi_zero_fraction(encoded, "$.radius")
    else:
        radius = dyadic_fraction(encoded, "$.radius")
    if radius <= 0:
        _fail("$.radius", "radius must be strictly positive")
    return radius


def _arb_vector(values: Any, length: int, path: str) -> list[arb]:
    items = _sequence(values, length, path)
    return [
        _rational_arb(_pi_zero_fraction(item, f"{path}[{index}]"))
        for index, item in enumerate(items)
    ]


def _zero_vector(length: int) -> list[arb]:
    return [arb(0) for _ in range(length)]


def _mode_component_jet(
    mode: Mapping[str, Any],
    component: int,
    u: arb,
    time: arb,
    path: str,
) -> tuple[arb, arb, arb, arb, arb, arb]:
    """Return ``Y,Y_u,Y_t,Y_uu,Y_ut,Y_tt`` for an integer mode."""

    harmonic = _integer(mode.get("mode_number"), f"{path}.mode_number")
    if harmonic <= 0:
        _fail(f"{path}.mode_number", "harmonic must be positive")
    time_frequency = Fraction(harmonic, TIME_FREQUENCY_DENOMINATOR)
    frequency_fields = [
        name
        for name in ("temporal_angular_frequency", "wave_number")
        if name in mode
    ]
    if not frequency_fields:
        _fail(path, "missing exact temporal angular frequency")
    for frequency_field in frequency_fields:
        stored_frequency = _pi_zero_fraction(
            mode[frequency_field], f"{path}.{frequency_field}"
        )
        if stored_frequency != time_frequency:
            _fail(
                f"{path}.{frequency_field}",
                "must equal the exact symbolic-lift frequency m/8",
            )
    spatial_phase = _symbolic_scalar_parts(
        mode.get("spatial_phase_coefficient"),
        f"{path}.spatial_phase_coefficient",
    )
    if spatial_phase != (Fraction(2 * harmonic), 1):
        _fail(
            f"{path}.spatial_phase_coefficient",
            "must equal exactly 2*pi*m",
        )

    k = exact_arb(time_frequency)
    omega = exact_arb(2 * harmonic) * arb.pi()
    x0 = _rational_arb(
        _pi_zero_fraction(mode["initial_x"][component], f"{path}.initial_x[{component}]")
    )
    y0 = _rational_arb(
        _pi_zero_fraction(mode["initial_y"][component], f"{path}.initial_y[{component}]")
    )
    p0 = _rational_arb(
        _pi_zero_fraction(mode["initial_p"][component], f"{path}.initial_p[{component}]")
    )
    q0 = _rational_arb(
        _pi_zero_fraction(mode["initial_q"][component], f"{path}.initial_q[{component}]")
    )

    kt = k * time
    ct, st = kt.cos(), kt.sin()
    # sin_pi/cos_pi preserve exact integer endpoint identities and avoid
    # introducing a rounded numerical representation of 2*pi.
    spatial_argument = exact_arb(2 * harmonic) * u
    ss, cs = spatial_argument.sin_cos_pi()

    x_t = x0 * ct + (p0 / k) * st
    y_t = y0 * ct + (q0 / k) * st
    p_t = -k * x0 * st + p0 * ct
    q_t = -k * y0 * st + q0 * ct

    value = x_t * cs + y_t * ss
    u_first = omega * (-x_t * ss + y_t * cs)
    time_first = p_t * cs + q_t * ss
    u_second = -(omega * omega) * value
    u_time = omega * (-p_t * ss + q_t * cs)
    time_second = -(k * k) * value
    return value, u_first, time_first, u_second, u_time, time_second


def _metric_dot(
    left: Sequence[arb],
    right: Sequence[arb],
    winding_metric: arb,
) -> arb:
    if len(left) != TARGET_DIMENSION or len(right) != TARGET_DIMENSION:
        raise SymbolicPhysicalJetError("metric-dot shape mismatch")
    total = arb(0)
    for axis in range(TRANSVERSE_DIMENSION):
        total += left[axis] * right[axis]
    total += winding_metric * left[WINDING_AXIS] * right[WINDING_AXIS]
    return total


def exact_seam_image_shift(
    problem: Mapping[str, Any], worldsheet_axis: int
) -> tuple[int, ...]:
    """Return the exact image shift induced by ``u_axis -> u_axis + 1``.

    This is an integer-algebra statement.  It relies only on the registered
    integer harmonics and winding orientations, never on Arb endpoint balls.
    """

    convention = _validate_convention(problem)
    if worldsheet_axis not in (0, 1):
        _fail("$.worldsheet_axis", "expected 0 or 1")
    strings = _sequence(
        convention.source["kinematics"]["strings"],
        2,
        "$.problem.kinematics.strings",
    )
    for string_index, string in enumerate(strings):
        modes = string.get("modes")
        if type(modes) is not list or not modes:
            _fail(
                f"$.problem.kinematics.strings[{string_index}].modes",
                "at least one integer mode is required",
            )
        for mode_index, mode in enumerate(modes):
            harmonic = _integer(
                mode.get("mode_number"),
                "$.problem.kinematics.strings"
                f"[{string_index}].modes[{mode_index}].mode_number",
            )
            if harmonic <= 0:
                _fail("$.problem.kinematics", "mode number must be positive")
    shift = [0] * TARGET_DIMENSION
    orientation = convention.orientations[worldsheet_axis]
    shift[WINDING_AXIS] = orientation if worldsheet_axis == 0 else -orientation
    return tuple(shift)


def evaluate_symbolic_physical_jets(
    problem: Mapping[str, Any],
    box: Mapping[str, Any],
    lattice_image: Sequence[int] | None = None,
    radius: Mapping[str, Any] | None = None,
    *,
    precision_bits: int = DEFAULT_PRECISION_BITS,
) -> dict[str, Any]:
    """Evaluate all first/second ``d`` jets and the derived ``F/g_r`` jets."""

    if type(precision_bits) is not int or precision_bits < MINIMUM_PRECISION_BITS:
        raise SymbolicPhysicalJetError(
            f"Arb precision must be an integer of at least "
            f"{MINIMUM_PRECISION_BITS} bits"
        )
    convention = _validate_convention(problem)
    problem_map = _mapping(problem, "$.problem")
    source = convention.source
    _validate_box(problem_map, source, box)
    image = _validate_lattice_image(lattice_image)
    radius_fraction = _validate_radius(problem_map, source, radius)
    check_backend()

    with precision(precision_bits):
        variables = [
            interval_arb(box[name], f"$.box.{name}")
            for name in VARIABLE_ORDER
        ]
        u1, u2, time = variables
        kinematics = _mapping(
            source["kinematics"], "$.problem.kinematics"
        )
        initial_time = exact_arb(
            _pi_zero_fraction(
                kinematics["initial_time"],
                "$.problem.kinematics.initial_time",
            )
        )
        mode_time = time - initial_time
        centres = _mapping(
            kinematics["centres_Q1_Q2"],
            "$.problem.kinematics.centres_Q1_Q2",
        )
        Q1 = _arb_vector(
            centres["Q1"], TRANSVERSE_DIMENSION, "$.problem.kinematics.centres_Q1_Q2.Q1"
        )
        Q2 = _arb_vector(
            centres["Q2"], TRANSVERSE_DIMENSION, "$.problem.kinematics.centres_Q1_Q2.Q2"
        )
        strings = _sequence(
            kinematics["strings"], 2, "$.problem.kinematics.strings"
        )
        velocities = [
            _arb_vector(
                string["transverse_velocity"],
                TRANSVERSE_DIMENSION,
                f"$.problem.kinematics.strings[{index}].transverse_velocity",
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
            for string_index, (string, u) in enumerate(zip(strings, (u1, u2))):
                modes = string.get("modes")
                if type(modes) is not list or not modes:
                    _fail(
                        f"$.problem.kinematics.strings[{string_index}].modes",
                        "expected a nonempty mode list",
                    )
                accumulated = [arb(0) for _ in range(6)]
                for mode_index, mode in enumerate(modes):
                    jet = _mode_component_jet(
                        mode,
                        component,
                        u,
                        mode_time,
                        "$.problem.kinematics.strings"
                        f"[{string_index}].modes[{mode_index}]",
                    )
                    for derivative_index, value in enumerate(jet):
                        accumulated[derivative_index] += value
                string_jets.append(accumulated)

            jet1, jet2 = string_jets
            relative_velocity = velocities[0][component] - velocities[1][component]
            d[component] = (
                Q1[component]
                - Q2[component]
                + relative_velocity * mode_time
                + jet1[0]
                - jet2[0]
            )
            d_a[0][component] = jet1[1]
            d_a[1][component] = -jet2[1]
            d_a[2][component] = relative_velocity + jet1[2] - jet2[2]
            d_ab[0][0][component] = jet1[3]
            d_ab[1][1][component] = -jet2[3]
            d_ab[2][2][component] = jet1[5] - jet2[5]
            d_ab[0][2][component] = jet1[4]
            d_ab[2][0][component] = jet1[4]
            d_ab[1][2][component] = -jet2[4]
            d_ab[2][1][component] = -jet2[4]

        orientation1, orientation2 = convention.orientations
        d[WINDING_AXIS] = orientation1 * u1 - orientation2 * u2
        d_a[0][WINDING_AXIS] = arb(orientation1)
        d_a[1][WINDING_AXIS] = arb(-orientation2)

        lattice_shift = [
            exact_arb(period) * integer
            for period, integer in zip(convention.periods, image)
        ]
        separation = [
            value - shift for value, shift in zip(d, lattice_shift)
        ]

        winding_length = exact_arb(WINDING_LENGTH_COEFFICIENT) * arb.pi()
        winding_metric = winding_length * winding_length
        F = _metric_dot(separation, separation, winding_metric) / 2
        F_a = [
            _metric_dot(d_a[axis], separation, winding_metric)
            for axis in range(3)
        ]
        F_ab = [[arb(0) for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for column in range(3):
                F_ab[row][column] = _metric_dot(
                    d_ab[row][column], separation, winding_metric
                ) + _metric_dot(d_a[row], d_a[column], winding_metric)

        radius_arb = exact_arb(radius_fraction)
        boundary = F - radius_arb * radius_arb / 2
        g_r = [F_a[0], F_a[1], boundary]
        Dg_r = [
            [F_ab[0][0], F_ab[0][1], F_ab[0][2]],
            [F_ab[1][0], F_ab[1][1], F_ab[1][2]],
            [F_a[0], F_a[1], F_a[2]],
        ]
        return {
            "problem_sha256": base.semantic_sha256(problem_map),
            "precision_bits": precision_bits,
            "variable_order": VARIABLE_ORDER,
            "variables": variables,
            "lattice_image": image,
            "lattice_shift": lattice_shift,
            "radius": radius_arb,
            "winding_length": winding_length,
            "winding_metric": winding_metric,
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


# Short alias for callers that already distinguish the symbolic lift by module.
evaluate_physical_jets = evaluate_symbolic_physical_jets
