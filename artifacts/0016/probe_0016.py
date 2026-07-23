#!/usr/bin/env python3
"""Deterministic standard-library probe for Brief 0016.

This artifact evaluates two independent pieces of the brief:

* the local F1 encounter rank of J = [tau_1, -tau_2, u_rel], obtained from
  the symmetric 3-by-3 Gram matrix J^T J; and
* impact-preparation suppression factors for uniform balls and boxes.

It deliberately does not implement a return law or infer a response-visible
rank.  In particular, an outgoing/scattering axis is not an input column of
the incoming encounter Jacobian.
"""

from __future__ import annotations

import argparse
import json
import math
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any, Iterable, Sequence


ARTIFACT_SCHEMA = "cyz-brief-0016-probe-v1"
DECIMAL_PRECISION = 100
REPORTED_SIGNIFICANT_DIGITS = 18
SPATIAL_DIMENSION = 9
RHO_GRID = ("0", "0.25", "0.5", "1", "2", "4", "8")
MAX_CODIMENSION = 6
RANK_REL_TOL = 1.0e-10
RANK_ABS_TOL = 1.0e-12
KINEMATIC_MARGIN = 1.0e-4

# A fixed decimal expansion is preferable to a platform-dependent conversion
# through binary float.  It is used only for checking analytic large-rho
# bounds, not for evaluating the reported suppression factors.
PI_DECIMAL = Decimal(
    "3.141592653589793238462643383279502884197169399375105820974944592"
    "3078164062862089986280348253421170679"
)


def dot(left: Sequence[float], right: Sequence[float]) -> float:
    """Euclidean dot product with a dimension check."""

    if len(left) != len(right):
        raise ValueError("vector dimensions differ")
    return math.fsum(x * y for x, y in zip(left, right))


def negate(vector: Sequence[float]) -> tuple[float, ...]:
    return tuple(-value for value in vector)


def gram3(columns: Sequence[Sequence[float]]) -> list[list[float]]:
    """Return the symmetric 3-by-3 Gram matrix of three equal-length columns."""

    if len(columns) != 3:
        raise ValueError("the F1 encounter Jacobian must have exactly 3 columns")
    if not columns[0]:
        raise ValueError("empty vectors are not allowed")
    if any(len(column) != len(columns[0]) for column in columns):
        raise ValueError("column dimensions differ")

    gram = [[0.0] * 3 for _ in range(3)]
    for row in range(3):
        for column in range(row, 3):
            value = dot(columns[row], columns[column])
            gram[row][column] = value
            gram[column][row] = value
    return gram


def whiten_columns(
    columns: Sequence[Sequence[float]],
    target_metric_diag: Sequence[float],
    domain_metric_diag: Sequence[float],
) -> tuple[tuple[float, ...], ...]:
    """Return G^(1/2) J H^(-1/2) for positive diagonal control metrics."""

    if len(columns) != 3 or len(domain_metric_diag) != 3:
        raise ValueError("the F1 control requires three columns/domain scales")
    if not columns or len(target_metric_diag) != len(columns[0]):
        raise ValueError("target metric dimension differs from the columns")
    if any(value <= 0.0 for value in target_metric_diag):
        raise ValueError("target metric must be positive")
    if any(value <= 0.0 for value in domain_metric_diag):
        raise ValueError("domain metric must be positive")

    return tuple(
        tuple(
            math.sqrt(target_metric_diag[row])
            * column[row]
            / math.sqrt(domain_metric_diag[column_index])
            for row in range(len(column))
        )
        for column_index, column in enumerate(columns)
    )


def symmetric_eigenvalues_3x3(matrix: Sequence[Sequence[float]]) -> list[float]:
    """Compute eigenvalues of a real symmetric 3-by-3 matrix by Jacobi sweeps.

    The matrix is scaled before iteration.  Jacobi rotations are backward
    stable for this small symmetric problem and avoid the cancellation-prone
    cubic formula.  Small negative roundoff residues of a positive
    semidefinite Gram matrix are clipped to zero.
    """

    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("expected a 3-by-3 matrix")
    for row in range(3):
        for column in range(3):
            if not math.isfinite(matrix[row][column]):
                raise ValueError("matrix contains a non-finite value")
            if abs(matrix[row][column] - matrix[column][row]) > 1.0e-13:
                raise ValueError("matrix is not symmetric")

    scale = max(abs(value) for row in matrix for value in row)
    if scale == 0.0:
        return [0.0, 0.0, 0.0]

    work = [[float(value) / scale for value in row] for row in matrix]
    machine_epsilon = 2.220446049250313e-16

    for _ in range(64):
        pivot_row, pivot_column = max(
            ((0, 1), (0, 2), (1, 2)),
            key=lambda pair: abs(work[pair[0]][pair[1]]),
        )
        off_diagonal = work[pivot_row][pivot_column]
        diagonal_scale = max(
            1.0, abs(work[0][0]), abs(work[1][1]), abs(work[2][2])
        )
        if abs(off_diagonal) <= 8.0 * machine_epsilon * diagonal_scale:
            break

        app = work[pivot_row][pivot_row]
        aqq = work[pivot_column][pivot_column]
        tau = (aqq - app) / (2.0 * off_diagonal)
        if tau >= 0.0:
            tangent = 1.0 / (tau + math.hypot(1.0, tau))
        else:
            tangent = -1.0 / (-tau + math.hypot(1.0, tau))
        cosine = 1.0 / math.sqrt(1.0 + tangent * tangent)
        sine = tangent * cosine

        for index in range(3):
            if index in (pivot_row, pivot_column):
                continue
            aip = work[index][pivot_row]
            aiq = work[index][pivot_column]
            rotated_ip = cosine * aip - sine * aiq
            rotated_iq = sine * aip + cosine * aiq
            work[index][pivot_row] = rotated_ip
            work[pivot_row][index] = rotated_ip
            work[index][pivot_column] = rotated_iq
            work[pivot_column][index] = rotated_iq

        work[pivot_row][pivot_row] = (
            cosine * cosine * app
            - 2.0 * sine * cosine * off_diagonal
            + sine * sine * aqq
        )
        work[pivot_column][pivot_column] = (
            sine * sine * app
            + 2.0 * sine * cosine * off_diagonal
            + cosine * cosine * aqq
        )
        work[pivot_row][pivot_column] = 0.0
        work[pivot_column][pivot_row] = 0.0
    else:
        raise ArithmeticError("Jacobi eigensolver did not converge")

    eigenvalues = sorted(
        (work[index][index] * scale for index in range(3)), reverse=True
    )
    largest = max(eigenvalues[0], 0.0)
    clipping_tolerance = 64.0 * machine_epsilon * max(largest, scale)
    cleaned = [
        0.0 if value < 0.0 and abs(value) <= clipping_tolerance else value
        for value in eigenvalues
    ]
    if any(value < 0.0 for value in cleaned):
        raise ArithmeticError("Gram matrix has a materially negative eigenvalue")
    return cleaned


def singular_values_from_gram(gram: Sequence[Sequence[float]]) -> list[float]:
    return [math.sqrt(value) for value in symmetric_eigenvalues_3x3(gram)]


def analyze_event(
    name: str,
    tau1: Sequence[float],
    tau2: Sequence[float],
    relative_velocity: Sequence[float],
    *,
    spatial_dimension: int = SPATIAL_DIMENSION,
    target_metric_diag: Sequence[float] | None = None,
    domain_metric_diag: Sequence[float] | None = None,
) -> dict[str, Any]:
    """Analyze J = [tau1, -tau2, relative_velocity] in a flat local chart."""

    if len(tau1) != spatial_dimension:
        raise ValueError("tau1 does not match the declared spatial dimension")
    columns = (tuple(tau1), negate(tau2), tuple(relative_velocity))
    target_metric_diag = (
        tuple(target_metric_diag)
        if target_metric_diag is not None
        else (1.0,) * spatial_dimension
    )
    domain_metric_diag = (
        tuple(domain_metric_diag)
        if domain_metric_diag is not None
        else (1.0, 1.0, 1.0)
    )
    whitened = whiten_columns(
        columns,
        target_metric_diag,
        domain_metric_diag,
    )
    gram = gram3(whitened)
    singular_values = singular_values_from_gram(gram)
    threshold = max(RANK_ABS_TOL, RANK_REL_TOL * singular_values[0])
    rank = sum(value > threshold for value in singular_values)
    normal_dimension = spatial_dimension - rank
    spacetime_dimension = spatial_dimension + 1
    source_impact_dimension = spacetime_dimension - 4

    return {
        "name": name,
        "tau1": list(tau1),
        "tau2": list(tau2),
        "relative_velocity": list(relative_velocity),
        "jacobian_column_convention": ["tau1", "-tau2", "relative_velocity"],
        "target_metric_diag": [
            format_float(value) for value in target_metric_diag
        ],
        "domain_metric_diag": [
            format_float(value) for value in domain_metric_diag
        ],
        "analyzed_matrix": "G^(1/2) J H^(-1/2)",
        "gram_matrix": [[format_float(value) for value in row] for row in gram],
        "eigenvalues_descending": [
            format_float(value)
            for value in symmetric_eigenvalues_3x3(gram)
        ],
        "singular_values_descending": [
            format_float(value) for value in singular_values
        ],
        "rank_threshold": format_float(threshold),
        "kinematic_rank": rank,
        "smallest_singular_value": format_float(singular_values[-1]),
        "passes_declared_rank3_margin": (
            rank == 3 and singular_values[-1] >= KINEMATIC_MARGIN
        ),
        "normal_dimension_d_minus_rank": normal_dimension,
        "gkm_impact_dimension_D_minus_4": source_impact_dimension,
        "gkm_dimension_matches_local_normal": (
            normal_dimension == source_impact_dimension
        ),
    }


def format_float(value: float) -> str:
    if value == 0.0:
        return "0"
    return format(value, ".17g")


def decimal_suppression_ball(codimension: int, rho: Decimal) -> Decimal:
    """Evaluate c*integral_0^1 u^(c-1) exp(-rho^2 u^2) du.

    The integral is evaluated with the cancellation-free positive series:

        exp(-z) * sum_{k>=0} z^k / (c/2 + 1)_k,  z=rho^2.

    Once the term ratio is below one, a geometric majorant bounds the omitted
    positive tail.  All comparisons use the unrounded Decimal result.
    """

    if codimension < 0:
        raise ValueError("codimension must be nonnegative")
    if rho < 0:
        raise ValueError("rho must be nonnegative")
    if codimension == 0 or rho == 0:
        return Decimal(1)

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        z = rho * rho
        half_codimension = Decimal(codimension) / Decimal(2)
        exponential = (-z).exp()
        term = Decimal(1)
        total = Decimal(1)
        tail_tolerance = Decimal(10) ** (-(DECIMAL_PRECISION - 25))

        for index in range(1, 10000):
            term *= z / (half_codimension + Decimal(index))
            total += term
            next_ratio = z / (
                half_codimension + Decimal(index) + Decimal(1)
            )
            if next_ratio < 1:
                tail_bound = (
                    exponential
                    * term
                    * next_ratio
                    / (Decimal(1) - next_ratio)
                )
                if tail_bound <= tail_tolerance:
                    return +(exponential * total)
        raise ArithmeticError("suppression series did not converge")


def decimal_suppression_box(codimension: int, rho: Decimal) -> Decimal:
    """Evaluate [sqrt(pi) erf(rho)/(2 rho)]^c.

    The bracket is exactly the c=1 ball integral, so reusing that high
    precision integral avoids importing a non-standard erf implementation.
    """

    if codimension < 0:
        raise ValueError("codimension must be nonnegative")
    if rho < 0:
        raise ValueError("rho must be nonnegative")
    if codimension == 0 or rho == 0:
        return Decimal(1)
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        one_coordinate_factor = decimal_suppression_ball(1, rho)
        return +(one_coordinate_factor ** codimension)


def decimal_string(value: Decimal) -> str:
    """Return a deterministic 18-significant-digit decimal string."""

    with localcontext() as context:
        context.prec = REPORTED_SIGNIFICANT_DIGITS
        rounded = +value
    return format(rounded, "g")


def valid_frame_count(large_direction_count: int, arity: int) -> int:
    if large_direction_count < 0:
        raise ValueError("large_direction_count must be nonnegative")
    if arity < 1:
        raise ValueError("arity must be positive")
    if large_direction_count < arity:
        return 0
    return math.prod(
        range(large_direction_count - arity + 1, large_direction_count + 1)
    )


def basis_vector(index: int, dimension: int = SPATIAL_DIMENSION) -> tuple[float, ...]:
    return tuple(1.0 if coordinate == index else 0.0 for coordinate in range(dimension))


def build_kinematic_controls() -> list[dict[str, Any]]:
    e1 = basis_vector(0)
    e2 = basis_vector(1)
    e3 = basis_vector(2)
    zero_tail = (0.0,) * (SPATIAL_DIMENSION - 3)

    # JJP-type local incoming data: two non-collinear string tangents and
    # relative velocity transverse to their plane.
    jjp_tau2 = (0.6, 0.8, 0.0) + zero_tail

    # Nearly opposite tangents, but with a small independent component.  The
    # event remains rank three under the numerical rank tolerance while
    # failing the stronger declared eta_kin margin.
    epsilon = 1.0e-6
    normalization = math.hypot(1.0, epsilon)
    near_opposite_tau2 = (
        -1.0 / normalization,
        epsilon / normalization,
        0.0,
    ) + zero_tail

    return [
        analyze_event(
            "jjp_noncollinear_rank3",
            e1,
            jjp_tau2,
            e3,
        ),
        analyze_event(
            "near_opposite_rank3_below_margin",
            e1,
            near_opposite_tau2,
            e3,
        ),
        analyze_event(
            "full_rank_rescaled_domain_metric",
            e1,
            negate(e2),
            e3,
            domain_metric_diag=(4.0, 1.0, 1.0),
        ),
        analyze_event(
            "strict_opposite_winding_rank2",
            e1,
            negate(e1),
            e2,
        ),
        analyze_event(
            "independent_tangents_velocity_in_span_rank2",
            e1,
            e2,
            tuple(left + right for left, right in zip(e1, e2)),
        ),
        analyze_event(
            "opposite_winding_collinear_velocity_rank1",
            e1,
            negate(e1),
            tuple(2.0 * value for value in e1),
        ),
    ]


def build_scattering_axis_counterexample(
    controls: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    rank2_control = next(
        item for item in controls if item["name"] == "strict_opposite_winding_rank2"
    )
    scattering_axis = basis_vector(2)
    incoming_columns = (
        tuple(rank2_control["tau1"]),
        negate(rank2_control["tau2"]),
        tuple(rank2_control["relative_velocity"]),
    )
    axis_is_nonzero = dot(scattering_axis, scattering_axis) > RANK_ABS_TOL
    orthogonal = axis_is_nonzero and all(
        abs(dot(scattering_axis, column)) <= RANK_ABS_TOL
        for column in incoming_columns
    )
    if not orthogonal:
        raise AssertionError("declared scattering axis is not normal to incoming span")

    # Re-analyze exactly the same source jets.  Merely declaring an outgoing
    # normal axis cannot alter D Phi_e or its incoming rank.
    repeated = analyze_event(
        "strict_opposite_winding_rank2_repeated",
        rank2_control["tau1"],
        rank2_control["tau2"],
        rank2_control["relative_velocity"],
    )
    if repeated["normal_dimension_d_minus_rank"] != SPATIAL_DIMENSION - 2:
        raise AssertionError("fixed scattering axis changed the incoming normal space")

    return {
        "incoming_control": rank2_control["name"],
        "fixed_scattering_axis": list(scattering_axis),
        "axis_is_nonzero_and_orthogonal_to_every_incoming_column": orthogonal,
        "incoming_rank_before_declaring_axis": rank2_control["kinematic_rank"],
        "incoming_rank_after_declaring_axis": repeated["kinematic_rank"],
        "incoming_normal_dimension_after_declaring_axis": repeated[
            "normal_dimension_d_minus_rank"
        ],
        "gkm_D_minus_4_dimension": repeated[
            "gkm_impact_dimension_D_minus_4"
        ],
        "counterexample_passes": (
            orthogonal
            and repeated["kinematic_rank"] == 2
            and not repeated["gkm_dimension_matches_local_normal"]
        ),
        "reason": (
            "A fixed scattering axis is outgoing/normal data, not a third "
            "incoming column of D Phi_e. Appending or naming it cannot turn "
            "the rank-2 opposite-winding source jet into a rank-3 encounter."
        ),
    }


def build_suppression_table() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    all_ball_monotone = True
    all_box_monotone = True
    all_ball_box_ordered = True
    all_bounds_hold = True
    ball_columns: dict[int, list[Decimal]] = {
        codimension: [] for codimension in range(MAX_CODIMENSION + 1)
    }
    box_columns: dict[int, list[Decimal]] = {
        codimension: [] for codimension in range(MAX_CODIMENSION + 1)
    }

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        for rho_text in RHO_GRID:
            rho = Decimal(rho_text)
            ball_values = [
                decimal_suppression_ball(codimension, rho)
                for codimension in range(MAX_CODIMENSION + 1)
            ]
            box_values = [
                decimal_suppression_box(codimension, rho)
                for codimension in range(MAX_CODIMENSION + 1)
            ]
            for codimension, value in enumerate(ball_values):
                ball_columns[codimension].append(value)
            for codimension, value in enumerate(box_values):
                box_columns[codimension].append(value)

            if rho == 0:
                ball_monotone = all(value == 1 for value in ball_values)
                box_monotone = all(value == 1 for value in box_values)
            else:
                ball_monotone = all(
                    ball_values[index] < ball_values[index - 1]
                    for index in range(1, len(ball_values))
                )
                box_monotone = all(
                    box_values[index] < box_values[index - 1]
                    for index in range(1, len(box_values))
                )
            all_ball_monotone &= ball_monotone
            all_box_monotone &= box_monotone

            ball_box_ordered = all(
                ball_values[codimension] >= box_values[codimension]
                for codimension in range(MAX_CODIMENSION + 1)
            ) and all(
                ball_values[codimension] > box_values[codimension]
                for codimension in range(2, MAX_CODIMENSION + 1)
            ) if rho > 0 else all(
                ball_values[codimension] == box_values[codimension] == 1
                for codimension in range(MAX_CODIMENSION + 1)
            )
            all_ball_box_ordered &= ball_box_ordered

            bound_checks = []
            if rho >= 1:
                for codimension in range(1, MAX_CODIMENSION + 1):
                    ball_lower = (-Decimal(1)).exp() * rho ** (-codimension)
                    # Gamma(c/2 + 1) is evaluated by a short exact
                    # integer/half-integer recurrence.
                    ball_upper = (
                        decimal_gamma_half_integer(codimension + 2)
                        * rho ** (-codimension)
                    )
                    box_lower = (
                        (-Decimal(1)).exp() / rho
                    ) ** codimension
                    box_upper = (
                        PI_DECIMAL.sqrt() / (Decimal(2) * rho)
                    ) ** codimension
                    holds = (
                        ball_lower <= ball_values[codimension] <= ball_upper
                        and box_lower <= box_values[codimension] <= box_upper
                    )
                    all_bounds_hold &= holds
                    bound_checks.append(
                        {
                            "codimension": codimension,
                            "ball_bound_holds": (
                                ball_lower
                                <= ball_values[codimension]
                                <= ball_upper
                            ),
                            "box_bound_holds": (
                                box_lower
                                <= box_values[codimension]
                                <= box_upper
                            ),
                        }
                    )

            rows.append(
                {
                    "rho": rho_text,
                    "ball": {
                        str(codimension): decimal_string(value)
                        for codimension, value in enumerate(ball_values)
                    },
                    "box": {
                        str(codimension): decimal_string(value)
                        for codimension, value in enumerate(box_values)
                    },
                    "strictly_decreasing_in_codimension": {
                        "ball": ball_monotone,
                        "box": box_monotone,
                    },
                    "ball_at_least_box": ball_box_ordered,
                    "large_rho_bound_checks": bound_checks,
                }
            )

    ball_rho_monotone = all(
        all(
            values[index] < values[index - 1]
            for index in range(1, len(values))
        )
        for codimension, values in ball_columns.items()
        if codimension > 0
    )
    box_rho_monotone = all(
        all(
            values[index] < values[index - 1]
            for index in range(1, len(values))
        )
        for codimension, values in box_columns.items()
        if codimension > 0
    )

    checks = {
        "ball_codimension_ordering_holds_on_declared_grid": all_ball_monotone,
        "box_codimension_ordering_holds_on_declared_grid": all_box_monotone,
        "ball_strictly_decreasing_across_rho_for_positive_codimension": (
            ball_rho_monotone
        ),
        "box_strictly_decreasing_across_rho_for_positive_codimension": (
            box_rho_monotone
        ),
        "ball_at_least_box_on_declared_grid": all_ball_box_ordered,
        "declared_large_rho_bounds_hold_for_rho_at_least_one": all_bounds_hold,
        "ordering_checked_at_decimal_precision": DECIMAL_PRECISION,
        "reported_significant_digits": REPORTED_SIGNIFICANT_DIGITS,
    }
    return rows, checks


def decimal_gamma_half_integer(twice_argument: int) -> Decimal:
    """Gamma(twice_argument / 2) for positive integer/half-integer inputs."""

    if twice_argument < 1:
        raise ValueError("gamma argument must be positive")
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        if twice_argument % 2 == 0:
            integer_argument = twice_argument // 2
            return Decimal(math.factorial(integer_argument - 1))

        # Gamma(1/2) = sqrt(pi), then Gamma(z+1) = z Gamma(z).
        value = PI_DECIMAL.sqrt()
        current_twice_argument = 1
        while current_twice_argument < twice_argument:
            value *= Decimal(current_twice_argument) / Decimal(2)
            current_twice_argument += 2
        return +value


def build_valid_frame_table() -> list[dict[str, Any]]:
    return [
        {
            "q": q,
            "counts_by_arity": {
                str(arity): valid_frame_count(q, arity)
                for arity in range(1, 5)
            },
        }
        for q in range(10)
    ]


def build_report() -> dict[str, Any]:
    controls = build_kinematic_controls()
    suppression, suppression_checks = build_suppression_table()
    scattering_counterexample = build_scattering_axis_counterexample(controls)

    gkm_equivalence_check = all(
        control["gkm_dimension_matches_local_normal"]
        == (control["kinematic_rank"] == 3)
        for control in controls
    )
    expected_control_ranks = {
        "jjp_noncollinear_rank3": 3,
        "near_opposite_rank3_below_margin": 3,
        "full_rank_rescaled_domain_metric": 3,
        "strict_opposite_winding_rank2": 2,
        "independent_tangents_velocity_in_span_rank2": 2,
        "opposite_winding_collinear_velocity_rank1": 1,
    }
    control_ranks_pass = all(
        control["kinematic_rank"] == expected_control_ranks[control["name"]]
        for control in controls
    )

    checks = {
        "kinematic_control_ranks_match": control_ranks_pass,
        "gkm_D_minus_4_matches_local_normal_if_and_only_if_rank3": (
            gkm_equivalence_check
        ),
        "fixed_scattering_axis_counterexample_passes": (
            scattering_counterexample["counterexample_passes"]
        ),
        **suppression_checks,
    }
    checks["all_pass"] = all(
        value
        for key, value in checks.items()
        if key.endswith("_passes")
        or key.endswith("_match")
        or key.endswith("_holds")
        or key.endswith("_grid")
        or "if_and_only_if" in key
        or "strictly_decreasing" in key
    )

    return {
        "artifact": ARTIFACT_SCHEMA,
        "status": "PASS" if checks["all_pass"] else "FAIL",
        "declarations": {
            "local_metric": "Euclidean orthonormal chart (G = I)",
            "encounter_parameter_metric": (
                "positive diagonal H per control (identity by default); a "
                "physical run must register the arc-length/time scale"
            ),
            "encounter_jacobian": "J = [tau1, -tau2, relative_velocity]",
            "spatial_dimension_d": SPATIAL_DIMENSION,
            "spacetime_dimension_D": SPATIAL_DIMENSION + 1,
            "rank_relative_tolerance": format_float(RANK_REL_TOL),
            "rank_absolute_tolerance": format_float(RANK_ABS_TOL),
            "declared_rank3_margin_eta_kin": format_float(KINEMATIC_MARGIN),
            "rho_grid": list(RHO_GRID),
            "codimension_grid": list(range(MAX_CODIMENSION + 1)),
            "decimal_internal_precision": DECIMAL_PRECISION,
            "reported_significant_digits": REPORTED_SIGNIFICANT_DIGITS,
            "suppression_profile_scope": (
                "declared full-support Gaussian surrogate; extending the "
                "large-impact source profile through b=0 is a control closure"
            ),
        },
        "formulas": {
            "kinematic_rank": "a = rank([tau1, -tau2, relative_velocity])",
            "normal_dimension": "c = d - a",
            "gkm_impact_dimension": "D - 4 = d - 3",
            "ball": (
                "g_ball(c,rho) = c integral_0^1 "
                "u^(c-1) exp(-rho^2 u^2) du, with g_ball(0,rho)=1"
            ),
            "box": (
                "g_box(c,rho) = "
                "[sqrt(pi) erf(rho)/(2 rho)]^c, with g_box(0,rho)=1"
            ),
            "valid_frame_onset": (
                "N_valid(q,a) = q!/(q-a)! for q>=a, else 0"
            ),
            "ball_large_rho_bounds": (
                "exp(-1) rho^(-c) <= g_ball(c,rho) "
                "<= Gamma(c/2+1) rho^(-c), rho>=1"
            ),
            "box_large_rho_bounds": (
                "[exp(-1)/rho]^c <= g_box(c,rho) "
                "<= [sqrt(pi)/(2 rho)]^c, rho>=1"
            ),
        },
        "kinematic_controls": controls,
        "fixed_scattering_axis_counterexample": scattering_counterexample,
        "suppression_table": suppression,
        "valid_frame_onset": build_valid_frame_table(),
        "checks": checks,
        "source_classification": [
            {
                "claim": (
                    "rank(J), dim ker-normal = d-rank(J), and the equality "
                    "d-rank(J)=D-4 iff rank(J)=3"
                ),
                "classification": "exact theorem about a declared geometric model",
            },
            {
                "claim": (
                    "The GKM/JJP D-4 impact count applies to the rank-3 "
                    "non-collinear incoming stratum."
                ),
                "classification": "primary-source derived",
                "scope": (
                    "conditional on the source preparation occupying the "
                    "rank-3 non-collinear stratum"
                ),
            },
            {
                "claim": (
                    "Uniform-ball and independent-uniform-box averages and "
                    "their codimension monotonicity"
                ),
                "classification": "exact theorem about a declared geometric model",
                "scope": (
                    "the preparations and the full-support Gaussian profile "
                    "are declarations, not primary-source outputs"
                ),
            },
            {
                "claim": (
                    "The numerical values, Gram eigensolver controls, and "
                    "near-degenerate tolerance classification"
                ),
                "classification": "controlled numerical probe",
            },
            {
                "claim": (
                    "eta_kin=1e-4 is a preregistered diagnostic threshold "
                    "for these controls, not a source-derived physical margin"
                ),
                "classification": "derived from a newly proposed measurable closure",
            },
            {
                "claim": (
                    "A fixed outgoing scattering axis cannot repair a rank-2 "
                    "incoming opposite-winding source jet."
                ),
                "classification": "no-go/underdetermination",
            },
        ],
        "boundary": {
            "proves": (
                "A local encounter-rank/codimension calculation and suppression "
                "under two declared impact preparations."
            ),
            "does_not_prove": [
                "a source preparation with a positive rank-3 margin",
                "a source-valid small-impact reaction profile",
                "a first-principles return law",
                "response-visible spatial rank three",
                "one time direction or a 3+1 signature",
            ],
            "verdict": (
                "The D-4 impact dimension is recovered for rank-3 incoming "
                "geometry, not for strict straight opposite winding. Naming "
                "a scattering axis does not remove that obstruction."
            ),
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


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("source_to_return_kinematic_probe.json"),
        help="deterministic JSON output path",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail unless every declared numerical/theorem control passes",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    report = build_report()
    serialized = serialize_report(report)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8", newline="\n")

    if arguments.check and report["status"] != "PASS":
        raise SystemExit("Brief 0016 probe checks failed")
    print(f"{report['status']}: wrote {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
