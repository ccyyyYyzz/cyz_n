#!/usr/bin/env python3
"""Deterministic analytic controls for Brief 0017.

This standard-library artifact checks a finite-dimensional Gaussian/Wishart
control and several local event-geometry identities.  It deliberately does
not implement a finite-K world-sheet sampler, enumerate all event roots, or
construct a physical Palm law.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Sequence


ARTIFACT_SCHEMA = "cyz-brief-0017-analytic-tail-controls-v1"
TRANSVERSE_DIMENSION = 8
PAIR_COLUMN_COUNT = 2
WISHART_ALPHA = 2.5
ORDERED_WISHART_CONSTANT = 1.0 / 2880.0
FIXED_POINT_CONSTANT = math.sqrt(math.pi / 2.0) / 48.0
VOLUME_PALM_CONSTANT = 1.0 / 105.0
FIXED_POINT_SINGULAR_EXPONENT = 7.0
FIXED_POINT_GRAM_EXPONENT = 3.5
VOLUME_PALM_SINGULAR_EXPONENT = 8.0
EPSILON_GRID = (0.5, 0.25, 0.125, 0.0625)
DELTA_GRID = (0.1, 0.01, 0.001, 0.0001, 0.00001)
INTEGRATION_REL_TOL = 2.0e-13
INTEGRATION_ABS_TOL = 1.0e-20


def format_float(value: float) -> str:
    """Return a deterministic finite binary-float rendering."""

    if not math.isfinite(value):
        raise ValueError("non-finite value cannot be reported")
    if value == 0.0:
        return "0"
    return format(value, ".17g")


def dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vector dimensions differ")
    return math.fsum(a * b for a, b in zip(left, right))


def norm(vector: Sequence[float]) -> float:
    return math.sqrt(max(dot(vector, vector), 0.0))


def subtract(
    left: Sequence[float], right: Sequence[float]
) -> tuple[float, ...]:
    if len(left) != len(right):
        raise ValueError("vector dimensions differ")
    return tuple(a - b for a, b in zip(left, right))


def matrix_determinant_2(matrix: Sequence[Sequence[float]]) -> float:
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError("expected a 2-by-2 matrix")
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def matrix_determinant_3(matrix: Sequence[Sequence[float]]) -> float:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("expected a 3-by-3 matrix")
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    )


def gram(columns: Sequence[Sequence[float]]) -> list[list[float]]:
    if not columns:
        raise ValueError("at least one column is required")
    dimension = len(columns[0])
    if dimension == 0 or any(len(column) != dimension for column in columns):
        raise ValueError("column dimensions differ or are empty")
    return [
        [dot(left, right) for right in columns]
        for left in columns
    ]


def gram_determinant(columns: Sequence[Sequence[float]]) -> float:
    matrix = gram(columns)
    if len(matrix) == 2:
        return matrix_determinant_2(matrix)
    if len(matrix) == 3:
        return matrix_determinant_3(matrix)
    raise ValueError("only two- and three-column Gram determinants are used")


def stable_squared_column_volume(
    columns: Sequence[Sequence[float]],
) -> float:
    """Squared Euclidean column volume by modified Gram-Schmidt."""

    if not columns:
        raise ValueError("at least one column is required")
    dimension = len(columns[0])
    if dimension == 0 or any(len(column) != dimension for column in columns):
        raise ValueError("column dimensions differ or are empty")
    orthonormal: list[tuple[float, ...]] = []
    squared_volume = 1.0
    for column in columns:
        residual = tuple(float(value) for value in column)
        for basis in orthonormal:
            coefficient = dot(residual, basis)
            residual = tuple(
                value - coefficient * basis_value
                for value, basis_value in zip(residual, basis)
            )
        squared_norm = max(dot(residual, residual), 0.0)
        if squared_norm == 0.0:
            return 0.0
        squared_volume *= squared_norm
        inverse_norm = 1.0 / math.sqrt(squared_norm)
        orthonormal.append(
            tuple(value * inverse_norm for value in residual)
        )
    return squared_volume


def positive_definite_determinant(
    matrix: Sequence[Sequence[float]],
) -> float:
    """Stable determinant of a small real symmetric positive matrix."""

    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("expected a nonempty square matrix")
    lower = [[0.0] * size for _ in range(size)]
    for row in range(size):
        for column in range(row + 1):
            correction = math.fsum(
                lower[row][index] * lower[column][index]
                for index in range(column)
            )
            if row == column:
                residue = matrix[row][row] - correction
                if residue <= 0.0:
                    raise ValueError("matrix is not positive definite")
                lower[row][column] = math.sqrt(residue)
            else:
                lower[row][column] = (
                    matrix[row][column] - correction
                ) / lower[column][column]
    return math.prod(lower[index][index] ** 2 for index in range(size))


def squared_distance_hessian(
    jacobian_columns: Sequence[Sequence[float]],
    separation: Sequence[float],
    second_derivatives: Sequence[Sequence[Sequence[float]]],
) -> list[list[float]]:
    """Hessian of F=|Phi|^2/2 from J, Phi and the declared second jet.

    At the evaluation point,

        H_ab = <J_a,J_b> + <Phi, Phi_ab>.
    """

    parameter_count = len(jacobian_columns)
    if parameter_count != 3:
        raise ValueError("the local controls use three encounter parameters")
    ambient_dimension = len(separation)
    if ambient_dimension == 0 or any(
        len(column) != ambient_dimension for column in jacobian_columns
    ):
        raise ValueError("Jacobian and separation dimensions differ")
    if len(second_derivatives) != parameter_count or any(
        len(row) != parameter_count for row in second_derivatives
    ):
        raise ValueError("second derivative tensor has the wrong shape")

    hessian = [[0.0] * parameter_count for _ in range(parameter_count)]
    for left in range(parameter_count):
        for right in range(parameter_count):
            derivative = second_derivatives[left][right]
            if len(derivative) != ambient_dimension:
                raise ValueError("second derivative ambient dimension differs")
            transpose_derivative = second_derivatives[right][left]
            if any(
                abs(a - b) > 1.0e-14
                for a, b in zip(derivative, transpose_derivative)
            ):
                raise ValueError("second derivative tensor is not symmetric")
            hessian[left][right] = (
                dot(jacobian_columns[left], jacobian_columns[right])
                + dot(separation, derivative)
            )
    return hessian


def zero_second_derivatives(
    parameter_count: int, ambient_dimension: int
) -> tuple[tuple[tuple[float, ...], ...], ...]:
    zero = (0.0,) * ambient_dimension
    return tuple(
        tuple(zero for _ in range(parameter_count))
        for _ in range(parameter_count)
    )


def normalised_gaussian_constraint_zero_density(
    jacobian_columns: Sequence[Sequence[float]],
) -> float:
    """Return det(Cov(J^T Z))^-1/2 for Z~N(0,I).

    The universal factor (2*pi)^(-k/2) is intentionally omitted because it
    cancels from the normalised Palm control.
    """

    determinant = stable_squared_column_volume(jacobian_columns)
    if determinant <= 0.0:
        raise ValueError("constraint covariance is singular")
    return 1.0 / math.sqrt(determinant)


def numerical_rank(
    columns: Sequence[Sequence[float]], tolerance: float = 1.0e-12
) -> int:
    """Rank by deterministic Gaussian elimination on the row matrix."""

    if not columns:
        return 0
    row_count = len(columns[0])
    column_count = len(columns)
    if any(len(column) != row_count for column in columns):
        raise ValueError("column dimensions differ")
    work = [
        [float(columns[column][row]) for column in range(column_count)]
        for row in range(row_count)
    ]
    scale = max((abs(value) for row in work for value in row), default=0.0)
    threshold = tolerance * max(1.0, scale)
    rank = 0
    pivot_column = 0
    while rank < row_count and pivot_column < column_count:
        pivot = max(
            range(rank, row_count),
            key=lambda row: abs(work[row][pivot_column]),
        )
        if abs(work[pivot][pivot_column]) <= threshold:
            pivot_column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][pivot_column]
        for column in range(pivot_column, column_count):
            work[rank][column] /= pivot_value
        for row in range(row_count):
            if row == rank:
                continue
            factor = work[row][pivot_column]
            if abs(factor) <= threshold:
                continue
            for column in range(pivot_column, column_count):
                work[row][column] -= factor * work[rank][column]
        rank += 1
        pivot_column += 1
    return rank


def upper_incomplete_gamma_twice(twice_argument: int, x: float) -> float:
    """Return Gamma(twice_argument / 2, x) for integer/half-integer inputs."""

    if twice_argument < 1:
        raise ValueError("gamma argument must be positive")
    if x < 0.0:
        raise ValueError("gamma lower limit must be nonnegative")

    exponential = math.exp(-x)
    if twice_argument % 2:
        value = math.sqrt(math.pi) * math.erfc(math.sqrt(x))
        current = 1
    else:
        value = exponential
        current = 2

    while current < twice_argument:
        z = current / 2.0
        value = z * value + (x**z) * exponential
        current += 2
    return value


def base_smallest_gram_density(y: float) -> float:
    """Density of the smaller ordered eigenvalue of B^T B for iid N(0,1)."""

    if y < 0.0:
        return 0.0
    half_y = y / 2.0
    inner = (
        (2.0**4.5) * upper_incomplete_gamma_twice(9, half_y)
        - y * (2.0**3.5) * upper_incomplete_gamma_twice(7, half_y)
    )
    return (
        ORDERED_WISHART_CONSTANT
        * math.exp(-half_y)
        * (y**WISHART_ALPHA)
        * inner
    )


def volume_weighted_smallest_gram_density(y: float) -> float:
    """Unnormalised density after multiplying by sqrt(det(B^T B))."""

    if y < 0.0:
        return 0.0
    half_y = y / 2.0
    inner = (
        (2.0**5.0) * upper_incomplete_gamma_twice(10, half_y)
        - y * (2.0**4.0) * upper_incomplete_gamma_twice(8, half_y)
    )
    return (
        ORDERED_WISHART_CONSTANT
        * math.exp(-half_y)
        * (y ** (WISHART_ALPHA + 0.5))
        * inner
    )


def composite_simpson(
    function: Callable[[float], float],
    lower: float,
    upper: float,
    intervals: int,
) -> float:
    if intervals < 2 or intervals % 2:
        raise ValueError("Simpson interval count must be positive and even")
    if upper < lower:
        raise ValueError("integration interval is reversed")
    if upper == lower:
        return 0.0
    step = (upper - lower) / intervals
    odd = math.fsum(
        function(lower + index * step)
        for index in range(1, intervals, 2)
    )
    even = math.fsum(
        function(lower + index * step)
        for index in range(2, intervals, 2)
    )
    return (
        step
        * (
            function(lower)
            + function(upper)
            + 4.0 * odd
            + 2.0 * even
        )
        / 3.0
    )


def converged_simpson_unit_interval(
    function: Callable[[float], float],
) -> float:
    previous: float | None = None
    intervals = 128
    while intervals <= 65536:
        current = composite_simpson(function, 0.0, 1.0, intervals)
        if previous is not None:
            error_scale = max(abs(current), abs(previous))
            if abs(current - previous) <= (
                INTEGRATION_ABS_TOL + INTEGRATION_REL_TOL * error_scale
            ):
                return current
        previous = current
        intervals *= 2
    raise ArithmeticError("deterministic Simpson quadrature did not converge")


@lru_cache(maxsize=None)
def fixed_point_cdf(epsilon: float) -> float:
    if epsilon < 0.0:
        raise ValueError("epsilon must be nonnegative")
    if epsilon == 0.0:
        return 0.0
    upper = epsilon * epsilon
    return upper * converged_simpson_unit_interval(
        lambda unit: base_smallest_gram_density(upper * unit)
    )


@lru_cache(maxsize=None)
def volume_palm_cdf(epsilon: float) -> float:
    if epsilon < 0.0:
        raise ValueError("epsilon must be nonnegative")
    if epsilon == 0.0:
        return 0.0
    upper = epsilon * epsilon
    unnormalised = upper * converged_simpson_unit_interval(
        lambda unit: volume_weighted_smallest_gram_density(upper * unit)
    )
    return unnormalised / expected_standard_pair_volume()


def mean_chi(degrees_of_freedom: int) -> float:
    if degrees_of_freedom < 1:
        raise ValueError("chi degrees of freedom must be positive")
    return (
        math.sqrt(2.0)
        * math.gamma((degrees_of_freedom + 1.0) / 2.0)
        / math.gamma(degrees_of_freedom / 2.0)
    )


def expected_standard_pair_volume() -> float:
    """E[|q wedge u|] from the Bartlett/orthogonal decomposition."""

    return mean_chi(8) * mean_chi(7)


def fixed_point_constant_from_density_leading_term() -> float:
    """Integrate the y->0 leading term of the smaller-eigenvalue density."""

    inner_at_zero = (2.0**4.5) * math.gamma(4.5)
    return (
        ORDERED_WISHART_CONSTANT
        * inner_at_zero
        / (WISHART_ALPHA + 1.0)
    )


def volume_palm_constant_from_density_leading_term() -> float:
    """Leading volume-weighted numerator, divided by E|q wedge u|."""

    inner_at_zero = (2.0**5.0) * math.gamma(5.0)
    unnormalised_constant = (
        ORDERED_WISHART_CONSTANT
        * inner_at_zero
        / (WISHART_ALPHA + 1.5)
    )
    return unnormalised_constant / expected_standard_pair_volume()


def log_slope(
    upper_value: float,
    lower_value: float,
    upper_scale: float,
    lower_scale: float,
) -> float:
    if min(upper_value, lower_value, upper_scale, lower_scale) <= 0.0:
        raise ValueError("log slope inputs must be positive")
    return math.log(upper_value / lower_value) / math.log(
        upper_scale / lower_scale
    )


def build_wishart_tail_controls() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    previous_epsilon: float | None = None
    previous_fixed: float | None = None
    previous_volume: float | None = None

    for epsilon in EPSILON_GRID:
        fixed = fixed_point_cdf(epsilon)
        volume = volume_palm_cdf(epsilon)
        row: dict[str, Any] = {
            "epsilon": format_float(epsilon),
            "gram_threshold_x": format_float(epsilon * epsilon),
            "fixed_point_cdf": format_float(fixed),
            "fixed_point_ratio_cdf_over_epsilon7": format_float(
                fixed / epsilon**7
            ),
            "volume_palm_cdf": format_float(volume),
            "volume_palm_ratio_cdf_over_epsilon8": format_float(
                volume / epsilon**8
            ),
        }
        if previous_epsilon is not None:
            assert previous_fixed is not None
            assert previous_volume is not None
            singular_slope = log_slope(
                previous_fixed,
                fixed,
                previous_epsilon,
                epsilon,
            )
            volume_slope = log_slope(
                previous_volume,
                volume,
                previous_epsilon,
                epsilon,
            )
            gram_slope = log_slope(
                previous_fixed,
                fixed,
                previous_epsilon**2,
                epsilon**2,
            )
            row.update(
                {
                    "fixed_point_local_singular_exponent": format_float(
                        singular_slope
                    ),
                    "fixed_point_local_gram_exponent": format_float(
                        gram_slope
                    ),
                    "volume_palm_local_singular_exponent": format_float(
                        volume_slope
                    ),
                }
            )
        rows.append(row)
        previous_epsilon = epsilon
        previous_fixed = fixed
        previous_volume = volume

    final = rows[-1]
    checks = {
        "ordered_wishart_normalization_constant_is_1_over_2880": math.isclose(
            ORDERED_WISHART_CONSTANT,
            1.0 / 2880.0,
            rel_tol=0.0,
            abs_tol=0.0,
        ),
        "expected_standard_pair_volume_is_7": math.isclose(
            expected_standard_pair_volume(),
            7.0,
            rel_tol=2.0e-15,
            abs_tol=2.0e-15,
        ),
        "fixed_point_leading_density_gives_declared_constant": math.isclose(
            fixed_point_constant_from_density_leading_term(),
            FIXED_POINT_CONSTANT,
            rel_tol=3.0e-15,
            abs_tol=3.0e-15,
        ),
        "volume_leading_density_gives_declared_constant": math.isclose(
            volume_palm_constant_from_density_leading_term(),
            VOLUME_PALM_CONSTANT,
            rel_tol=3.0e-15,
            abs_tol=3.0e-15,
        ),
        "fixed_point_constant_converges": abs(
            float(final["fixed_point_ratio_cdf_over_epsilon7"])
            / FIXED_POINT_CONSTANT
            - 1.0
        )
        < 0.003,
        "fixed_point_singular_exponent_converges_to_7": abs(
            float(final["fixed_point_local_singular_exponent"])
            - FIXED_POINT_SINGULAR_EXPONENT
        )
        < 0.01,
        "fixed_point_gram_exponent_converges_to_7_over_2": abs(
            float(final["fixed_point_local_gram_exponent"])
            - FIXED_POINT_GRAM_EXPONENT
        )
        < 0.005,
        "volume_palm_constant_converges": abs(
            float(final["volume_palm_ratio_cdf_over_epsilon8"])
            / VOLUME_PALM_CONSTANT
            - 1.0
        )
        < 0.003,
        "volume_palm_singular_exponent_converges_to_8": abs(
            float(final["volume_palm_local_singular_exponent"])
            - VOLUME_PALM_SINGULAR_EXPONENT
        )
        < 0.01,
    }
    return {
        "fixed_point_constant_exact": "sqrt(pi/2)/48",
        "fixed_point_constant_decimal": format_float(FIXED_POINT_CONSTANT),
        "fixed_point_constant_from_density_leading_term": format_float(
            fixed_point_constant_from_density_leading_term()
        ),
        "fixed_point_singular_exponent": "7",
        "fixed_point_gram_eigenvalue_exponent": "7/2",
        "volume_palm_constant_exact": "1/105",
        "volume_palm_constant_decimal": format_float(VOLUME_PALM_CONSTANT),
        "volume_palm_constant_from_density_leading_term": format_float(
            volume_palm_constant_from_density_leading_term()
        ),
        "volume_palm_singular_exponent": "8",
        "expected_standard_pair_volume": format_float(
            expected_standard_pair_volume()
        ),
        "epsilon_grid": [format_float(value) for value in EPSILON_GRID],
        "rows": rows,
        "checks": checks,
    }


def pair_smallest_singular_value(
    q_norm: float, parallel_u: float, orthogonal_u: float
) -> float:
    """Stable s_min of [[q_norm, parallel_u], [0, orthogonal_u]]."""

    if q_norm < 0.0:
        raise ValueError("q_norm must be nonnegative")
    trace = q_norm**2 + parallel_u**2 + orthogonal_u**2
    determinant = (q_norm * orthogonal_u) ** 2
    discriminant = max(trace * trace - 4.0 * determinant, 0.0)
    largest_eigenvalue = (trace + math.sqrt(discriminant)) / 2.0
    if largest_eigenvalue == 0.0:
        return 0.0
    return abs(q_norm * orthogonal_u) / math.sqrt(largest_eigenvalue)


def build_affine_closest_controls() -> dict[str, Any]:
    """Affine closest Kac-Rice scaling on a declared normalised control."""

    parallel_u = 0.75
    impact_radius = 0.25
    expected_smin_ratio = 1.0 / math.sqrt(1.0 + parallel_u**2)
    rows = []
    for delta in DELTA_GRID:
        longitudinal = (1.0, 0.0, 0.0, 0.0)
        q_column = (0.0, 1.0, 0.0, 0.0)
        relative_time = (0.0, parallel_u, delta, 0.0)
        jacobian = (longitudinal, q_column, relative_time)
        separation = (0.0, 0.0, 0.0, impact_radius)
        second_jet = zero_second_derivatives(3, 4)
        hessian = squared_distance_hessian(
            jacobian,
            separation,
            second_jet,
        )
        # Because the declared second jet vanishes, H=J^T J exactly.  Use the
        # orthogonalised column volume rather than a cancellation-prone
        # determinant of the nearly singular displayed Gram matrix.
        hessian_determinant = stable_squared_column_volume(jacobian)
        constraint_density_scale = (
            normalised_gaussian_constraint_zero_density(jacobian)
        )
        effective_kac_rice_scale = (
            hessian_determinant * constraint_density_scale
        )
        pair_volume = math.sqrt(
            stable_squared_column_volume((q_column, relative_time))
        )
        smallest = pair_smallest_singular_value(1.0, parallel_u, delta)
        rows.append(
            {
                "delta": format_float(delta),
                "gradient_Jt_s": [
                    format_float(dot(column, separation))
                    for column in jacobian
                ],
                "derived_hessian_matrix": [
                    [format_float(value) for value in row]
                    for row in hessian
                ],
                "pair_smallest_singular_value": format_float(smallest),
                "smin_over_delta": format_float(smallest / delta),
                "affine_closest_hessian_determinant": format_float(
                    hessian_determinant
                ),
                "hessian_over_delta_squared": format_float(
                    hessian_determinant / delta**2
                ),
                "constraint_zero_density_scale": format_float(
                    constraint_density_scale
                ),
                "constraint_density_times_delta": format_float(
                    constraint_density_scale * delta
                ),
                "effective_kac_rice_scale": format_float(
                    effective_kac_rice_scale
                ),
                "effective_scale_over_delta": format_float(
                    effective_kac_rice_scale / delta
                ),
                "pair_volume_abs_q_wedge_u": format_float(pair_volume),
                "pair_volume_over_delta": format_float(pair_volume / delta),
            }
        )

    final_ratio = float(rows[-1]["smin_over_delta"])
    checks = {
        "affine_declared_point_is_stationary": all(
            all(float(value) == 0.0 for value in row["gradient_Jt_s"])
            for row in rows
        ),
        "smin_is_linear_in_delta": abs(
            final_ratio / expected_smin_ratio - 1.0
        )
        < 1.0e-9,
        "affine_hessian_is_delta_squared": all(
            float(row["hessian_over_delta_squared"]) == 1.0
            for row in rows
        ),
        "constraint_zero_density_is_delta_inverse": all(
            math.isclose(
                float(row["constraint_density_times_delta"]),
                1.0,
                rel_tol=2.0e-15,
                abs_tol=2.0e-15,
            )
            for row in rows
        ),
        "complete_affine_kac_rice_scale_is_delta": all(
            math.isclose(
                float(row["effective_scale_over_delta"]),
                1.0,
                rel_tol=2.0e-15,
                abs_tol=2.0e-15,
            )
            for row in rows
        ),
        "pair_volume_is_delta": all(
            float(row["pair_volume_over_delta"]) == 1.0
            for row in rows
        ),
    }
    return {
        "model": (
            "In R4: J=[e1,e2,0.75 e2+delta e3], separation=(1/4)e4, "
            "and every second derivative of Phi is zero."
        ),
        "event_semantics": (
            "all regular interior affine closest roots counted by local "
            "stationary Kac-Rice intensity"
        ),
        "warning": (
            "The Hessian determinant alone scales as delta^2.  The "
            "constraint-zero density scales as delta^-1, so their product "
            "and the incoming volume scale as delta."
        ),
        "expected_smin_over_delta_limit": format_float(expected_smin_ratio),
        "rows": rows,
        "checks": checks,
    }


def build_curvature_lifted_controls() -> dict[str, Any]:
    """Conditional local counterexample with curvature-lifted Morse Hessian."""

    impact_radius = 0.25
    rows = []
    for delta in DELTA_GRID:
        e1 = (1.0, 0.0, 0.0, 0.0)
        e2 = (0.0, 1.0, 0.0, 0.0)
        delta_e3 = (0.0, 0.0, delta, 0.0)
        e4 = (0.0, 0.0, 0.0, 1.0)
        zero = (0.0, 0.0, 0.0, 0.0)
        jacobian = (e1, e2, delta_e3)
        separation = tuple(impact_radius * value for value in e4)
        second_jet = (
            (zero, zero, zero),
            (zero, zero, zero),
            (zero, zero, e4),
        )
        hessian = squared_distance_hessian(
            jacobian,
            separation,
            second_jet,
        )
        hessian_determinant = positive_definite_determinant(hessian)
        constraint_density_scale = (
            normalised_gaussian_constraint_zero_density(jacobian)
        )
        effective_scale = hessian_determinant * constraint_density_scale
        rows.append(
            {
                "delta": format_float(delta),
                "kinematic_small_singular_scale": format_float(delta),
                "gradient_Jt_s": [
                    format_float(dot(column, separation))
                    for column in jacobian
                ],
                "derived_hessian_matrix": [
                    [format_float(value) for value in row]
                    for row in hessian
                ],
                "morse_hessian_determinant": format_float(
                    hessian_determinant
                ),
                "hessian_minus_limit_over_delta_squared": format_float(
                    (hessian_determinant - impact_radius) / delta**2
                ),
                "constraint_zero_density_scale": format_float(
                    constraint_density_scale
                ),
                "constraint_density_times_delta": format_float(
                    constraint_density_scale * delta
                ),
                "effective_kac_rice_scale": format_float(effective_scale),
                "effective_scale_times_delta": format_float(
                    effective_scale * delta
                ),
            }
        )

    final = rows[-1]
    checks = {
        "curvature_declared_point_is_stationary": all(
            all(float(value) == 0.0 for value in row["gradient_Jt_s"])
            for row in rows
        ),
        "curvature_lifts_hessian_to_positive_limit": abs(
            float(final["morse_hessian_determinant"]) - impact_radius
        )
        < 2.0e-9,
        "curvature_hessian_formula_holds": all(
            math.isclose(
                float(row["hessian_minus_limit_over_delta_squared"]),
                1.0,
                rel_tol=2.0e-7,
                abs_tol=2.0e-7,
            )
            for row in rows
        ),
        "curved_constraint_zero_density_is_delta_inverse": all(
            math.isclose(
                float(row["constraint_density_times_delta"]),
                1.0,
                rel_tol=2.0e-15,
                abs_tol=2.0e-15,
            )
            for row in rows
        ),
        "conditional_effective_scale_is_delta_inverse": abs(
            float(final["effective_scale_times_delta"]) - impact_radius
        )
        < 2.0e-9,
    }
    return {
        "local_map": (
            "Phi_delta(x1,x2,t) = r e4 + x1 e1 + x2 e2 "
            "+ delta t e3 + (t^2/2) e4"
        ),
        "impact_radius_r": format_float(impact_radius),
        "conditional_tail_implication": (
            "Only if p_g(0)|det Hessian| is the effective closest-event "
            "weight, the principal corank-one density is smooth, the Morse "
            "indicator has positive limiting mass, and no survival factor "
            "cancels it: W_eff~S^-1 changes the fixed-point exponent 7 to 6."
        ),
        "not_a_first_entry_claim": True,
        "not_a_global_closest_selection_claim": True,
        "rows": rows,
        "checks": checks,
    }


def build_opposite_winding_identity_controls() -> dict[str, Any]:
    generic_p1 = (0.20, -0.10, 0.30, 0.05, 0.0, 0.0, 0.0, 0.0)
    generic_q = (0.70, 0.20, -0.40, 0.10, 0.0, 0.0, 0.0, 0.0)
    generic_u = (-0.10, 0.90, 0.50, -0.20, 0.0, 0.0, 0.0, 0.0)
    collinear_u = tuple(2.0 * value for value in generic_q)
    zero8 = (0.0,) * 8
    strict_u = (0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    excited_p1 = (0.0, 0.25, -0.10, 0.0, 0.0, 0.0, 0.0, 0.0)
    excited_u = (0.30, 0.0, 0.40, 0.0, 0.0, 0.0, 0.0, 0.0)

    def evaluate(
        name: str,
        p1: Sequence[float],
        q: Sequence[float],
        velocity: Sequence[float],
    ) -> dict[str, Any]:
        p2 = tuple(q_value - p1_value for q_value, p1_value in zip(q, p1))
        first = (1.0,) + tuple(p1)
        second = (0.0,) + tuple(-value for value in q)
        third = (0.0,) + tuple(velocity)
        left = gram_determinant((first, second, third))
        right_pair = gram_determinant((q, velocity))
        right_triple = gram_determinant((p1, q, velocity))
        right = right_pair + right_triple
        scale = max(1.0, abs(left), abs(right))
        return {
            "name": name,
            "det_JtJ": format_float(left),
            "q_wedge_u_squared": format_float(right_pair),
            "p1_wedge_q_wedge_u_squared": format_float(right_triple),
            "identity_right_hand_side": format_float(right),
            "absolute_residual": format_float(abs(left - right)),
            "identity_holds": abs(left - right) <= 2.0e-14 * scale,
            "p1": [format_float(value) for value in p1],
            "p2": [format_float(value) for value in p2],
            "q_equals_p1_plus_p2": [
                format_float(value) for value in q
            ],
            "relative_velocity_u": [
                format_float(value) for value in velocity
            ],
            "pair_rank": numerical_rank((q, velocity)),
            "encounter_rank": numerical_rank((first, second, third)),
        }

    controls = [
        evaluate(
            "generic_excited_opposite_winding_rank3",
            generic_p1,
            generic_q,
            generic_u,
        ),
        evaluate(
            "collinear_pair_rank2",
            generic_p1,
            generic_q,
            collinear_u,
        ),
        evaluate(
            "exact_straight_p1_p2_zero_rank2",
            zero8,
            zero8,
            strict_u,
        ),
        evaluate(
            "excited_but_q_zero_rank2",
            excited_p1,
            zero8,
            excited_u,
        ),
    ]

    near_rows = []
    near_parallel = 0.75
    near_q = (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    for delta in DELTA_GRID:
        near_u = (
            near_parallel,
            delta,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        )
        full_columns = (
            (1.0,) + zero8,
            (0.0,) + tuple(-value for value in near_q),
            (0.0,) + near_u,
        )
        positive_minor = delta**2
        smallest = pair_smallest_singular_value(
            1.0,
            near_parallel,
            delta,
        )
        near_rows.append(
            {
                "delta": format_float(delta),
                "positive_Gram_determinant_delta_squared": format_float(
                    positive_minor
                ),
                "exact_encounter_rank_from_positive_minor": 3,
                "numerical_encounter_rank": numerical_rank(full_columns),
                "pair_smallest_singular_value": format_float(smallest),
                "smin_over_delta": format_float(smallest / delta),
            }
        )
    expected_near_ratio = 1.0 / math.sqrt(1.0 + near_parallel**2)

    return {
        "identity": (
            "det(J^T J) = |q wedge u|^2 + |p1 wedge q wedge u|^2 "
            "for J~[e1+p1,-q,u]"
        ),
        "controls": controls,
        "near_degenerate_exact_rank3_sequence": {
            "q": [format_float(value) for value in near_q],
            "u": "0.75 q + delta e2",
            "expected_smin_over_delta_limit": format_float(
                expected_near_ratio
            ),
            "rows": near_rows,
        },
        "checks": {
            "opposite_winding_identity_holds": all(
                control["identity_holds"] for control in controls
            ),
            "generic_control_has_pair_rank2_and_encounter_rank3": (
                controls[0]["pair_rank"] == 2
                and controls[0]["encounter_rank"] == 3
            ),
            "collinear_control_has_pair_rank1_and_encounter_rank2": (
                controls[1]["pair_rank"] == 1
                and controls[1]["encounter_rank"] == 2
            ),
            "exact_straight_p1_p2_zero_control_has_rank2": (
                controls[2]["pair_rank"] == 1
                and controls[2]["encounter_rank"] == 2
                and all(value == "0" for value in controls[2]["p1"])
                and all(value == "0" for value in controls[2]["p2"])
            ),
            "excited_q_zero_control_has_rank2": (
                controls[3]["pair_rank"] == 1
                and controls[3]["encounter_rank"] == 2
                and any(value != "0" for value in controls[3]["p1"])
                and all(
                    value == "0"
                    for value in controls[3]["q_equals_p1_plus_p2"]
                )
            ),
            "near_degenerate_sequence_is_exact_rank3": all(
                row["exact_encounter_rank_from_positive_minor"] == 3
                and row["numerical_encounter_rank"] == 3
                and float(row["positive_Gram_determinant_delta_squared"]) > 0.0
                for row in near_rows
            ),
            "near_degenerate_smin_is_linear_in_delta": abs(
                float(near_rows[-1]["smin_over_delta"])
                / expected_near_ratio
                - 1.0
            )
            < 1.0e-9,
        },
    }


def project_to_normal(
    separation: Sequence[float],
    orthonormal_image_basis: Sequence[Sequence[float]],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if any(
        not math.isclose(norm(vector), 1.0, rel_tol=0.0, abs_tol=1.0e-14)
        for vector in orthonormal_image_basis
    ):
        raise ValueError("declared image basis is not normalised")
    for left_index, left in enumerate(orthonormal_image_basis):
        for right in orthonormal_image_basis[left_index + 1 :]:
            if abs(dot(left, right)) > 1.0e-14:
                raise ValueError("declared image basis is not orthogonal")
    longitudinal = tuple(
        math.fsum(
            dot(separation, basis) * basis[index]
            for basis in orthonormal_image_basis
        )
        for index in range(len(separation))
    )
    normal = subtract(separation, longitudinal)
    return normal, longitudinal


def orthonormal_basis_spans_columns(
    basis: Sequence[Sequence[float]],
    columns: Sequence[Sequence[float]],
    tolerance: float = 1.0e-13,
) -> bool:
    """Check both inclusion and rank equality for a declared image basis."""

    if not basis or not columns:
        return False
    if numerical_rank(basis) != numerical_rank(columns):
        return False
    for column in columns:
        normal, _ = project_to_normal(column, basis)
        if norm(normal) > tolerance * max(1.0, norm(column)):
            return False
    return True


def build_event_bundle_projection_controls() -> dict[str, Any]:
    e1 = (1.0, 0.0, 0.0, 0.0)
    e2 = (0.0, 1.0, 0.0, 0.0)
    e3 = (0.0, 0.0, 1.0, 0.0)
    event_jacobian = (e1, e2, e3)
    spatial_image_basis = (e1, e2)
    full_image_basis = event_jacobian

    # A regular inward first-entry root is stationary in the two material
    # coordinates, but not in time.  Its separation is orthogonal to e1,e2,
    # while -s.e3>0 is the inward boundary flux.  Projecting against the full
    # encounter image therefore retains a nonzero longitudinal time phase.
    first_separation = (0.0, 0.0, -2.0, 3.0)
    first_b, first_ell = project_to_normal(
        first_separation, full_image_basis
    )
    closest_separation = (0.0, 0.0, 0.0, 3.0)
    closest_b, closest_ell = project_to_normal(
        closest_separation, full_image_basis
    )
    closest_time_after_entry = 2.0
    propagated_closest = tuple(
        first_value + closest_time_after_entry * velocity_value
        for first_value, velocity_value in zip(first_separation, e3)
    )

    first_normal = all(
        abs(dot(first_b, basis)) <= 1.0e-14
        for basis in full_image_basis
    )
    closest_normal = all(
        abs(dot(closest_b, basis)) <= 1.0e-14
        for basis in full_image_basis
    )
    first_spatial_stationary = all(
        abs(dot(first_separation, basis)) <= 1.0e-14
        for basis in spatial_image_basis
    )
    first_inward_flux = -dot(first_separation, e3)
    first_entry_radius_squared = 13.0
    first_spatial_hessian = gram(spatial_image_basis)
    first_spatial_hessian_positive = (
        first_spatial_hessian[0][0] > 0.0
        and matrix_determinant_2(first_spatial_hessian) > 0.0
    )
    first_on_boundary = math.isclose(
        dot(first_separation, first_separation),
        first_entry_radius_squared,
        rel_tol=0.0,
        abs_tol=0.0,
    )
    first_regular = (
        first_spatial_stationary
        and first_on_boundary
        and first_spatial_hessian_positive
        and first_inward_flux > 0.0
    )
    return {
        "local_affine_map": (
            "Phi(x1,x2,t)=s+x1 e1+x2 e2+t e3 at the declared entry root"
        ),
        "event_jacobian_columns": [
            [format_float(value) for value in column]
            for column in event_jacobian
        ],
        "event_jacobian_rank": numerical_rank(event_jacobian),
        "jacobian_column_roles": [
            "first material tangent",
            "negative second material tangent",
            "relative time velocity",
        ],
        "normal_projector_diag": ["0", "0", "0", "1"],
        "first_entry": {
            "separation_s": [format_float(value) for value in first_separation],
            "impact_b_equals_P_N_s": [
                format_float(value) for value in first_b
            ],
            "longitudinal_phase_ell": [
                format_float(value) for value in first_ell
            ],
            "b_is_normal": first_normal,
            "entry_radius_squared": format_float(
                first_entry_radius_squared
            ),
            "entry_radius": format_float(
                math.sqrt(first_entry_radius_squared)
            ),
            "boundary_equation_F_equals_r_squared_over_2": first_on_boundary,
            "s_is_stationary_in_material_coordinates": (
                first_spatial_stationary
            ),
            "spatial_F_hessian": [
                [format_float(value) for value in row]
                for row in first_spatial_hessian
            ],
            "spatial_hessian_is_positive_definite": (
                first_spatial_hessian_positive
            ),
            "unique_spatial_minimizer": first_spatial_hessian_positive,
            "inward_flux_minus_s_dot_u": format_float(first_inward_flux),
            "inward_crossing_is_regular": first_regular,
            "ell_is_nonzero": norm(first_ell) > 0.0,
            "b_equals_s": first_b == first_separation,
            "reconstruction_holds": all(
                math.isclose(
                    b_value + ell_value,
                    s_value,
                    rel_tol=0.0,
                    abs_tol=1.0e-14,
                )
                for b_value, ell_value, s_value in zip(
                    first_b, first_ell, first_separation
                )
            ),
        },
        "closest_approach": {
            "time_after_entry": format_float(closest_time_after_entry),
            "separation_s": [
                format_float(value) for value in closest_separation
            ],
            "impact_b": [format_float(value) for value in closest_b],
            "longitudinal_phase_ell": [
                format_float(value) for value in closest_ell
            ],
            "b_is_normal": closest_normal,
            "b_equals_s": closest_b == closest_separation,
            "ell_is_zero": norm(closest_ell) == 0.0,
            "is_same_affine_episode_as_first_entry": all(
                math.isclose(
                    propagated,
                    declared,
                    rel_tol=0.0,
                    abs_tol=1.0e-14,
                )
                for propagated, declared in zip(
                    propagated_closest,
                    closest_separation,
                )
            ),
        },
        "checks": {
            "declared_event_jacobian_has_rank3": (
                numerical_rank(event_jacobian) == 3
            ),
            "normal_projector_basis_spans_im_J": (
                orthonormal_basis_spans_columns(
                    full_image_basis,
                    event_jacobian,
                )
            ),
            "first_entry_is_spatially_stationary_and_inward": (
                first_spatial_stationary and first_inward_flux > 0.0
            ),
            "first_entry_is_on_declared_boundary": first_on_boundary,
            "first_entry_has_unique_spatial_Morse_minimum": (
                first_spatial_hessian_positive
            ),
            "first_entry_is_fully_regular_in_declared_affine_control": (
                first_regular
            ),
            "first_entry_uses_projected_b_and_nonzero_ell": (
                first_normal
                and norm(first_ell) > 0.0
                and first_b != first_separation
            ),
            "first_entry_reconstructs_s_as_b_plus_ell": all(
                math.isclose(
                    b_value + ell_value,
                    s_value,
                    rel_tol=0.0,
                    abs_tol=1.0e-14,
                )
                for b_value, ell_value, s_value in zip(
                    first_b, first_ell, first_separation
                )
            ),
            "closest_uses_b_equals_s_and_zero_ell": (
                closest_normal
                and closest_b == closest_separation
                and norm(closest_ell) == 0.0
            ),
            "closest_is_propagated_from_same_affine_entry_episode": all(
                math.isclose(
                    propagated,
                    declared,
                    rel_tol=0.0,
                    abs_tol=1.0e-14,
                )
                for propagated, declared in zip(
                    propagated_closest,
                    closest_separation,
                )
            ),
        },
    }


def build_unique_curved_rank2_control() -> dict[str, Any]:
    """A unique strict minimum although the first derivative has rank two."""

    impact_radius = 0.25
    e1 = (1.0, 0.0, 0.0, 0.0)
    e2 = (0.0, 1.0, 0.0, 0.0)
    zero = (0.0, 0.0, 0.0, 0.0)
    columns = (e1, e2, zero)
    rank = numerical_rank(columns)
    hessian_diag = (1.0, 1.0, impact_radius)
    hessian_positive = all(value > 0.0 for value in hessian_diag)
    return {
        "map": (
            "Phi(x1,x2,t)=r e4+x1 e1+x2 e2+(t^2/2)e4, r=1/4"
        ),
        "event_point": ["0", "0", "0"],
        "jacobian_columns": [
            [format_float(value) for value in column] for column in columns
        ],
        "kinematic_rank": rank,
        "F_gradient_at_event": ["0", "0", "0"],
        "F_hessian_diag_at_event": [
            format_float(value) for value in hessian_diag
        ],
        "hessian_is_positive_definite": hessian_positive,
        "global_uniqueness_reason": (
            "F=0.5[x1^2+x2^2+(r+t^2/2)^2] is strictly larger away "
            "from (0,0,0) when r>0."
        ),
        "unique_strict_minimum": hessian_positive and rank == 2,
        "checks": {
            "unique_curved_control_has_rank2": rank == 2,
            "unique_curved_rank2_control_is_morse": hessian_positive,
            "curvature_not_linear_rank_lifts_the_minimum": (
                rank == 2 and hessian_positive
            ),
        },
    }


def all_boolean_checks_pass(section: Any) -> bool:
    if isinstance(section, dict):
        for key, value in section.items():
            if key == "checks":
                if not isinstance(value, dict):
                    return False
                if not all(
                    isinstance(check, bool) and check
                    for check in value.values()
                ):
                    return False
            elif not all_boolean_checks_pass(value):
                return False
    elif isinstance(section, list):
        return all(all_boolean_checks_pass(value) for value in section)
    return True


def build_report() -> dict[str, Any]:
    wishart = build_wishart_tail_controls()
    affine = build_affine_closest_controls()
    curvature = build_curvature_lifted_controls()
    identity = build_opposite_winding_identity_controls()
    projections = build_event_bundle_projection_controls()
    curved_rank2 = build_unique_curved_rank2_control()

    sections = {
        "wishart_tail_controls": wishart,
        "affine_closest_controls": affine,
        "curvature_lifted_conditional_counterexample": curvature,
        "opposite_winding_rank_identity": identity,
        "event_bundle_projection_controls": projections,
        "unique_curved_rank2_control": curved_rank2,
    }
    all_pass = all_boolean_checks_pass(sections)
    return {
        "artifact": ARTIFACT_SCHEMA,
        "status": "PASS" if all_pass else "FAIL",
        "declarations": {
            "transverse_dimension": TRANSVERSE_DIMENSION,
            "pair_jet_shape": "8x2",
            "fixed_point_control": (
                "B entries iid N(0,1), fixed material pair and fixed time, "
                "before event conditioning"
            ),
            "volume_palm_surrogate": (
                "dP_wedge proportional to sqrt(det(B^T B)) dP"
            ),
            "tail_limit": (
                "epsilon tends to zero at fixed covariance and fixed cutoff"
            ),
            "event_reference_measure_requirement": (
                "A complete event weight must include p_g(0), the root "
                "Jacobian, Morse/inward indicators, and any no-earlier "
                "survival/selection factor exactly once."
            ),
        },
        **sections,
        "boundary": {
            "proves": [
                (
                    "The fixed-point standard iid 8x2 Wishart hard-edge "
                    "constant sqrt(pi/2)/48 and singular-value exponent 7."
                ),
                (
                    "The corresponding smallest-Gram-eigenvalue exponent "
                    "7/2."
                ),
                (
                    "For the declared pure volume-biased surrogate, the "
                    "constant 1/105 and singular-value exponent 8."
                ),
                (
                    "Local affine and curvature-lifted Kac-Rice scaling "
                    "identities in the explicitly declared controls."
                ),
                (
                    "The opposite-winding Gram identity and the distinction "
                    "between first-entry (b=P_N s, possibly ell!=0) and "
                    "interior closest approach (b=s, ell=0)."
                ),
            ],
            "does_not_implement_or_prove": [
                "a finite-K Nambu-Goto or world-sheet sampler",
                "coverage or uniqueness of all physical event roots",
                "a physical first-entry, closest-event, or Palm law",
                "a no-earlier, hysteresis, tie, or episode-selection kernel",
                "a cutoff-uniform tail theorem",
                "a source-derived positive singular-value margin",
                "response-visible rank three or a 3+1 signature",
            ],
            "curvature_warning": (
                "The conditional exponent-6 counterexample applies only "
                "under its listed local closest-event Kac-Rice assumptions; "
                "it is neither a first-entry theorem nor a physical-worldsheet "
                "prediction."
            ),
        },
        "checks": {
            "all_declared_controls_pass": all_pass,
        },
    }


def serialize_report(report: dict[str, Any]) -> str:
    return json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def canonical_report_sha256(report: dict[str, Any]) -> str:
    return hashlib.sha256(serialize_report(report).encode("utf-8")).hexdigest()


def reject_duplicate_json_object_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    """Build one JSON object while rejecting ambiguous duplicate keys."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def read_semantic_json(path: Path) -> Any:
    """Parse type-preserving JSON and reject ambiguous duplicate keys."""

    with path.open("r", encoding="utf-8", newline=None) as handle:
        return json.load(
            handle,
            object_pairs_hook=reject_duplicate_json_object_pairs,
        )


def type_strict_semantic_equal(left: Any, right: Any) -> bool:
    """Recursive JSON equality that does not identify booleans with numbers."""

    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (
            left.keys() == right.keys()
            and all(
                type_strict_semantic_equal(left[key], right[key])
                for key in left
            )
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            type_strict_semantic_equal(a, b)
            for a, b in zip(left, right)
        )
    return left == right


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("analytic_tail_controls.json"),
        help="deterministic JSON report path",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "compare the stored and regenerated reports as parsed JSON, "
            "independent of LF/CRLF checkout conversion"
        ),
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    report = build_report()
    if report["status"] != "PASS":
        raise SystemExit("Brief 0017 analytic controls failed")

    if arguments.check:
        if not arguments.output.exists():
            raise SystemExit(f"Brief 0017 report missing: {arguments.output}")
        try:
            stored = read_semantic_json(arguments.output)
        except (OSError, UnicodeError, ValueError) as error:
            raise SystemExit(
                f"Brief 0017 report parse failure: {error}"
            ) from error
        if not type_strict_semantic_equal(stored, report):
            raise SystemExit("Brief 0017 report semantic mismatch")
        action = "verified canonical semantic JSON"
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            serialize_report(report),
            encoding="utf-8",
            newline="\n",
        )
        action = "wrote"

    print(
        f"{report['status']}: {action}: {arguments.output}; "
        f"canonical_sha256={canonical_report_sha256(report)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
