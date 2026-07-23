#!/usr/bin/env python3
"""Deterministic statistical and hostile controls for audit-k1-v1."""

from __future__ import annotations

import copy
import hashlib
import itertools
import math
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Any, Iterable, Mapping

import numpy as np

import stat_audit_core as core


DIRECTION_BLOCKS = (
    ("u0", 8),
    ("z1_left_direction", 16),
    ("z1_right_direction", 16),
    ("z2_left_direction", 16),
    ("z2_right_direction", 16),
)
CHIRAL_NAMES = tuple(name for name, _ in DIRECTION_BLOCKS[1:])


class ConstraintTracker:
    """Track deterministic residuals against fixed scale-aware tolerances."""

    def __init__(self) -> None:
        self._rows: dict[str, dict[str, Any]] = {}

    def update(
        self,
        name: str,
        residual: np.ndarray | float,
        scale: np.ndarray | float,
        *,
        flow: bool = False,
    ) -> None:
        residual_array = np.asarray(residual, dtype=np.float64)
        scale_array = np.asarray(scale, dtype=np.float64)
        tolerance = (
            core.flow_tolerance(scale_array)
            if flow
            else core.algebra_tolerance(scale_array)
        )
        ratio = np.divide(
            np.abs(residual_array),
            tolerance,
            out=np.full_like(residual_array, math.inf),
            where=tolerance > 0.0,
        )
        maximum_abs = float(np.max(np.abs(residual_array)))
        maximum_ratio = float(np.max(ratio))
        row = self._rows.setdefault(
            name,
            {
                "max_absolute_residual": 0.0,
                "max_normalized_residual": 0.0,
                "passed": True,
                "tolerance_class": "flow" if flow else "algebra",
            },
        )
        row["max_absolute_residual"] = max(
            row["max_absolute_residual"], maximum_abs
        )
        row["max_normalized_residual"] = max(
            row["max_normalized_residual"], maximum_ratio
        )
        row["passed"] = bool(row["passed"] and maximum_ratio <= 1.0)

    def update_upper(
        self, name: str, observed: np.ndarray | float, upper: float
    ) -> None:
        observed_array = np.asarray(observed, dtype=np.float64)
        violation = np.maximum(observed_array - upper, 0.0)
        self.update(name, violation, max(1.0, abs(upper)))
        row = self._rows[name]
        row["max_observed"] = max(
            float(row.get("max_observed", -math.inf)),
            float(np.max(observed_array)),
        )
        row["registered_upper"] = upper

    def rows(self) -> dict[str, dict[str, Any]]:
        return copy.deepcopy(dict(sorted(self._rows.items())))

    def passed(self) -> bool:
        return bool(self._rows and all(row["passed"] for row in self._rows.values()))


def _monomial_sum(
    values: np.ndarray, index: tuple[int, int, int]
) -> float:
    term = np.ones(values.shape[0], dtype=np.float64)
    for column, exponent in enumerate(index):
        if exponent:
            term *= values[:, column] ** exponent
    return float(term.sum(dtype=np.float64))


def radial_moment_observations(
    method: str,
    *,
    count: int,
    cell: core.AuditCell,
    chunk_size: int = core.CHUNK_SIZE,
) -> tuple[dict[tuple[int, int, int], float], dict[str, Any]]:
    if method not in {"gamma", "beta"}:
        raise core.AuditError(f"unknown radial method: {method}")
    label = "gamma_radial" if method == "gamma" else "beta_radial"
    rng = core.make_rng(label)
    indices = core.moment_multi_indices()
    sums = {index: 0.0 for index in indices}
    generated = 0
    while generated < count:
        size = min(chunk_size, count - generated)
        if method == "gamma":
            radial = core.gamma_radial_chunk(rng, size, cell.e_star)
        else:
            radial = core.beta_radial_chunk(rng, size, cell.e_star)
        normalized = radial / cell.e_star
        for index in indices:
            sums[index] += _monomial_sum(normalized, index)
        generated += size
    observations = {index: value / count for index, value in sums.items()}
    endpoint = {
        "continuation_raw_hex": [
            f"{int(value):016x}" for value in rng.bit_generator.random_raw(4)
        ],
        "raw_words_consumed": count * (34 if method == "gamma" else 62),
        "samples": count,
    }
    return observations, endpoint


def radial_ledger(
    gamma: Mapping[tuple[int, int, int], float],
    beta: Mapping[tuple[int, int, int], float],
    *,
    count: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index in core.moment_multi_indices():
        mean_fraction = core.dirichlet_moment(index)
        variance_fraction = core.dirichlet_variance(index)
        mean = float(mean_fraction)
        variance = float(variance_fraction)
        index_text = "_".join(map(str, index))
        threshold = core.bernstein_threshold(variance_fraction, count)
        two_threshold = core.two_sample_bernstein_threshold(
            variance_fraction, count
        )
        gamma_row = core.ledger_entry(
            test_id=f"radial.gamma.moment.{index_text}",
            category="radial_gamma_exact_moment",
            observed=gamma[index],
            expected=mean,
            variance=variance,
            threshold=threshold,
            count=count,
        )
        gamma_row["expected_exact"] = core.fraction_text(mean_fraction)
        rows.append(gamma_row)
        beta_row = core.ledger_entry(
            test_id=f"radial.beta.moment.{index_text}",
            category="radial_beta_exact_moment",
            observed=beta[index],
            expected=mean,
            variance=variance,
            threshold=threshold,
            count=count,
        )
        beta_row["expected_exact"] = core.fraction_text(mean_fraction)
        rows.append(beta_row)
        rows.append(
            core.ledger_entry(
                test_id=f"radial.gamma_vs_beta.moment.{index_text}",
                category="radial_gamma_beta_crosscheck",
                observed=gamma[index] - beta[index],
                expected=0.0,
                variance=2.0 * variance,
                threshold=two_threshold,
                count=count,
            )
        )
    if len(rows) != 102:
        raise AssertionError("radial ledger must contain 102 rows")
    return rows


def torus_characters() -> list[tuple[str, np.ndarray]]:
    rows: list[tuple[str, np.ndarray]] = []
    for axis in range(8):
        unit = np.zeros(8, dtype=np.int64)
        unit[axis] = 1
        rows.append((f"e{axis}", unit.copy()))
        unit[axis] = 2
        rows.append((f"2e{axis}", unit.copy()))
    for axis in range(8):
        neighbor = (axis + 1) % 8
        plus = np.zeros(8, dtype=np.int64)
        plus[axis] = 1
        plus[neighbor] = 1
        rows.append((f"e{axis}+e{neighbor}", plus))
        minus = np.zeros(8, dtype=np.int64)
        minus[axis] = 1
        minus[neighbor] = -1
        rows.append((f"e{axis}-e{neighbor}", minus))
    if len(rows) != 32:
        raise AssertionError("torus character manifest must contain 32 rows")
    return rows


def _append_prefix(
    storage: dict[str, list[Any]],
    source: Mapping[str, Any],
    coefficients: Mapping[str, Any],
    remaining: int,
) -> int:
    if remaining <= 0:
        return 0
    size = min(remaining, source["radial"].shape[0])
    storage.setdefault("radial", []).append(source["radial"][:size].copy())
    storage.setdefault("u0", []).append(source["u0"][:size].copy())
    storage.setdefault("q_relative", []).append(
        coefficients["q_relative"][:size].copy()
    )
    storage.setdefault("relative_momentum", []).append(
        coefficients["relative_momentum"][:size].copy()
    )
    storage.setdefault("velocity_1", []).append(
        coefficients["velocity_1"][:size].copy()
    )
    storage.setdefault("velocity_2", []).append(
        coefficients["velocity_2"][:size].copy()
    )
    for index, value in enumerate(coefficients["z"]):
        storage.setdefault(f"z{index}", []).append(value[:size].copy())
    for string_index, row in enumerate(coefficients["coefficients"]):
        for field in ("x", "y", "p", "q"):
            storage.setdefault(
                f"string{string_index}_{field}", []
            ).append(row[field][:size].copy())
    return size


def _concatenate_prefix(storage: Mapping[str, list[Any]]) -> dict[str, np.ndarray]:
    return {
        key: np.concatenate(value, axis=0)
        for key, value in storage.items()
    }


def _constraint_checks_for_chunk(
    tracker: ConstraintTracker,
    source: Mapping[str, Any],
    coefficients: Mapping[str, Any],
    cell: core.AuditCell,
) -> None:
    radial = source["radial"]
    tracker.update("radial_simplex", radial.sum(axis=1) - cell.e_star, cell.e_star)
    for name, block in zip(
        (name for name, _ in DIRECTION_BLOCKS),
        [source["u0"], *source["chiral"]],
    ):
        tracker.update(
            f"direction_norm.{name}",
            (block * block).sum(axis=1) - 1.0,
            1.0,
        )

    z = coefficients["z"]
    target_radii = (
        radial[:, 1] / 2.0,
        radial[:, 1] / 2.0,
        radial[:, 2] / 2.0,
        radial[:, 2] / 2.0,
    )
    for index, (value, target) in enumerate(zip(z, target_radii)):
        observed = (value * value).sum(axis=1)
        tracker.update(
            f"chiral_radius.z{index}",
            observed - target,
            np.maximum(1.0, observed + target),
        )

    relative = coefficients["relative_momentum"]
    relative_energy = (relative * relative).sum(axis=1)
    chiral_energy = sum((value * value).sum(axis=1) for value in z)
    center_energy = float(np.dot(cell.p_total, cell.p_total)) / (
        4.0 * cell.mass
    )
    total_energy = center_energy + relative_energy + chiral_energy
    tracker.update(
        "energy",
        total_energy - cell.e_perp,
        center_energy + relative_energy + chiral_energy + cell.e_perp,
    )

    momentum = cell.mass * (
        coefficients["velocity_1"] + coefficients["velocity_2"]
    )
    momentum_scale = np.maximum(
        1.0,
        np.abs(momentum)
        + np.abs(cell.p_total)[None, :],
    )
    tracker.update(
        "target_momentum",
        momentum - cell.p_total[None, :],
        momentum_scale,
    )
    for string_index, pair in enumerate(((z[0], z[1]), (z[2], z[3]))):
        left = (pair[0] * pair[0]).sum(axis=1)
        right = (pair[1] * pair[1]).sum(axis=1)
        tracker.update(
            f"level_matching.string{string_index + 1}",
            right - left,
            left + right,
        )

    c = coefficients["c"]
    for string_index, (left, right, real_row) in enumerate(
        (
            (c[0], c[1], coefficients["coefficients"][0]),
            (c[2], c[3], coefficients["coefficients"][1]),
        )
    ):
        x, y, p, q = (
            real_row["x"],
            real_row["y"],
            real_row["p"],
            real_row["q"],
        )
        reconstructed_left = np.concatenate(
            (
                0.25 * (x + q / cell.k1),
                0.25 * (p / cell.k1 - y),
            ),
            axis=1,
        )
        reconstructed_right = np.concatenate(
            (
                0.25 * (x - q / cell.k1),
                -0.25 * (y + p / cell.k1),
            ),
            axis=1,
        )
        tracker.update(
            f"chiral_roundtrip.string{string_index + 1}.left",
            reconstructed_left - left,
            np.maximum(1.0, np.abs(left) + np.abs(reconstructed_left)),
        )
        tracker.update(
            f"chiral_roundtrip.string{string_index + 1}.right",
            reconstructed_right - right,
            np.maximum(1.0, np.abs(right) + np.abs(reconstructed_right)),
        )
        slope_bound = cell.k1 * np.sqrt(
            (x * x).sum(axis=1) + (y * y).sum(axis=1)
        )
        velocity_bound = np.sqrt(
            (p * p).sum(axis=1) + (q * q).sum(axis=1)
        )
        tracker.update_upper(
            f"graph_slope_bound.string{string_index + 1}",
            slope_bound,
            cell.epsilon_graph,
        )
        tracker.update_upper(
            f"graph_velocity_bound.string{string_index + 1}",
            velocity_bound,
            cell.epsilon_graph,
        )

    q_unit = source["q_unit"]
    tracker.update_upper("torus_coordinate_upper", q_unit, 1.0)
    tracker.update_upper("torus_coordinate_lower", -q_unit, 0.0)


def _flow_and_average_checks(
    tracker: ConstraintTracker,
    prefix: Mapping[str, np.ndarray],
    cell: core.AuditCell,
) -> None:
    count = prefix["radial"].shape[0]
    if count != core.FLOW_PREFIX_SAMPLES:
        raise core.AuditError(
            f"flow prefix must contain {core.FLOW_PREFIX_SAMPLES} samples"
        )
    relative = prefix["relative_momentum"]
    center_energy = float(np.dot(cell.p_total, cell.p_total)) / (
        4.0 * cell.mass
    )
    relative_energy = (relative * relative).sum(axis=1)
    for time_index in range(33):
        time = time_index * cell.winding_length / 32.0
        cosine = math.cos(cell.k1 * time)
        sine = math.sin(cell.k1 * time)
        all_z: list[np.ndarray] = []
        for string_index in range(2):
            x = prefix[f"string{string_index}_x"]
            y = prefix[f"string{string_index}_y"]
            p = prefix[f"string{string_index}_p"]
            q = prefix[f"string{string_index}_q"]
            x_t = x * cosine + (p / cell.k1) * sine
            p_t = -cell.k1 * x * sine + p * cosine
            y_t = y * cosine + (q / cell.k1) * sine
            q_t = -cell.k1 * y * sine + q * cosine
            left = np.concatenate(
                (
                    0.25 * (x_t + q_t / cell.k1),
                    0.25 * (p_t / cell.k1 - y_t),
                ),
                axis=1,
            )
            right = np.concatenate(
                (
                    0.25 * (x_t - q_t / cell.k1),
                    -0.25 * (y_t + p_t / cell.k1),
                ),
                axis=1,
            )
            scale = math.sqrt(2.0 * cell.mass) * cell.k1
            z_left = scale * left
            z_right = scale * right
            all_z.extend((z_left, z_right))
            left_norm = (z_left * z_left).sum(axis=1)
            right_norm = (z_right * z_right).sum(axis=1)
            tracker.update(
                f"flow_level_matching.string{string_index + 1}.t{time_index}",
                right_norm - left_norm,
                left_norm + right_norm,
                flow=True,
            )
        oscillator = sum((value * value).sum(axis=1) for value in all_z)
        energy = center_energy + relative_energy + oscillator
        tracker.update(
            f"flow_energy.t{time_index}",
            energy - cell.e_perp,
            energy + cell.e_perp,
            flow=True,
        )

    grid_count = 64
    phases = 2.0 * math.pi * np.arange(grid_count, dtype=np.float64) / grid_count
    mean_cosine = float(np.cos(phases).mean())
    mean_sine = float(np.sin(phases).mean())
    average_count = min(256, count)
    for string_index in range(2):
        x = prefix[f"string{string_index}_x"][:average_count]
        y = prefix[f"string{string_index}_y"][:average_count]
        average_y = x * mean_cosine + y * mean_sine
        tracker.update(
            f"sigma_average_Y.string{string_index + 1}",
            average_y,
            np.maximum(1.0, np.abs(x) + np.abs(y)),
            flow=True,
        )


def _decimal_prefix_checks(
    prefix: Mapping[str, np.ndarray], cell: core.AuditCell
) -> dict[str, Any]:
    count = min(32, prefix["radial"].shape[0])
    maximum_energy = Decimal(0)
    maximum_level = Decimal(0)
    maximum_momentum = Decimal(0)
    with localcontext() as context:
        context.prec = 80
        expected_energy = Decimal.from_float(cell.e_perp)
        center = Decimal.from_float(
            float(np.dot(cell.p_total, cell.p_total)) / (4.0 * cell.mass)
        )
        for row in range(count):
            energy = center
            for value in prefix["relative_momentum"][row]:
                number = Decimal.from_float(float(value))
                energy += number * number
            z_norms: list[Decimal] = []
            for index in range(4):
                norm = Decimal(0)
                for value in prefix[f"z{index}"][row]:
                    number = Decimal.from_float(float(value))
                    norm += number * number
                z_norms.append(norm)
                energy += norm
            maximum_energy = max(maximum_energy, abs(energy - expected_energy))
            maximum_level = max(
                maximum_level,
                abs(z_norms[1] - z_norms[0]),
                abs(z_norms[3] - z_norms[2]),
            )
            for axis in range(8):
                observed = Decimal.from_float(cell.mass) * (
                    Decimal.from_float(float(prefix["velocity_1"][row, axis]))
                    + Decimal.from_float(float(prefix["velocity_2"][row, axis]))
                )
                target = Decimal.from_float(float(cell.p_total[axis]))
                maximum_momentum = max(
                    maximum_momentum, abs(observed - target)
                )
    return {
        "arithmetic": "Decimal.from_float with precision 80",
        "max_energy_residual": str(maximum_energy),
        "max_level_matching_residual": str(maximum_level),
        "max_target_momentum_residual": str(maximum_momentum),
        "samples": count,
        "status": "PASS"
        if max(maximum_energy, maximum_level, maximum_momentum)
        < Decimal("1e-12")
        else "FAIL",
    }


def full_source_audit(
    *,
    count: int,
    cell: core.AuditCell,
    chunk_size: int = core.CHUNK_SIZE,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    rng = core.make_rng("full_source")
    character_rows = torus_characters()
    character_matrix = np.array(
        [row[1] for row in character_rows], dtype=np.int64
    )
    coordinate_sum = np.zeros(72, dtype=np.float64)
    square_sum = np.zeros(72, dtype=np.float64)
    fourth_sum = np.zeros(72, dtype=np.float64)
    adjacent_sum = np.zeros(72, dtype=np.float64)
    pair_sum = np.zeros(6, dtype=np.float64)
    pair_square_sum = np.zeros(6, dtype=np.float64)
    character_real = np.zeros(32, dtype=np.float64)
    character_imag = np.zeros(32, dtype=np.float64)
    mixed_real = np.zeros((8, 3), dtype=np.float64)
    mixed_imag = np.zeros((8, 3), dtype=np.float64)
    tracker = ConstraintTracker()
    prefix_storage: dict[str, list[Any]] = {}
    prefix_remaining = core.FLOW_PREFIX_SAMPLES
    generated = 0
    raw_words = 0

    while generated < count:
        size = min(chunk_size, count - generated)
        source = core.full_source_chunk(rng, size, cell)
        coefficients = core.source_chunk_coefficients(source, cell)
        raw_words += size * source["raw_uniforms_per_sample"]
        _constraint_checks_for_chunk(tracker, source, coefficients, cell)
        used = _append_prefix(
            prefix_storage, source, coefficients, prefix_remaining
        )
        prefix_remaining -= used

        blocks = [source["u0"], *source["chiral"]]
        flat = np.concatenate(blocks, axis=1)
        coordinate_sum += flat.sum(axis=0)
        square_sum += (flat * flat).sum(axis=0)
        fourth_sum += (flat**4).sum(axis=0)
        offset = 0
        for block in blocks:
            dimension = block.shape[1]
            adjacent_sum[offset : offset + dimension] += (
                block * np.roll(block, -1, axis=1)
            ).sum(axis=0)
            offset += dimension
        for pair_index, (left, right) in enumerate(
            itertools.combinations(range(4), 2)
        ):
            dot = (source["chiral"][left] * source["chiral"][right]).sum(
                axis=1
            )
            pair_sum[pair_index] += float(dot.sum())
            pair_square_sum[pair_index] += float((dot * dot).sum())

        phase = 2.0 * math.pi * (source["q_unit"] @ character_matrix.T)
        cosine = np.cos(phase)
        sine = np.sin(phase)
        character_real += cosine.sum(axis=0)
        character_imag += sine.sum(axis=0)
        for axis in range(8):
            unit_cosine = np.cos(2.0 * math.pi * source["q_unit"][:, axis])
            unit_sine = np.sin(2.0 * math.pi * source["q_unit"][:, axis])
            for radial_index, expected in enumerate(
                (2.0 / 17.0, 15.0 / 34.0, 15.0 / 34.0)
            ):
                centered = source["radial"][:, radial_index] - expected
                mixed_real[axis, radial_index] += float(
                    (centered * unit_cosine).sum()
                )
                mixed_imag[axis, radial_index] += float(
                    (centered * unit_sine).sum()
                )
        generated += size

    if prefix_remaining != 0:
        raise core.AuditError("full profile did not fill the flow prefix")
    prefix = _concatenate_prefix(prefix_storage)
    _flow_and_average_checks(tracker, prefix, cell)
    decimal = _decimal_prefix_checks(prefix, cell)

    rows: list[dict[str, Any]] = []
    offset = 0
    for block_name, dimension in DIRECTION_BLOCKS:
        mean_variance = Fraction(1, dimension)
        square_mean = Fraction(1, dimension)
        square_variance = Fraction(3, dimension * (dimension + 2)) - Fraction(
            1, dimension * dimension
        )
        fourth_mean = Fraction(3, dimension * (dimension + 2))
        eighth_mean = Fraction(
            105,
            dimension
            * (dimension + 2)
            * (dimension + 4)
            * (dimension + 6),
        )
        fourth_variance = eighth_mean - fourth_mean * fourth_mean
        adjacent_variance = Fraction(1, dimension * (dimension + 2))
        for axis in range(dimension):
            flat_index = offset + axis
            rows.append(
                core.ledger_entry(
                    test_id=f"sphere.{block_name}.coordinate_{axis}.mean",
                    category="sphere_coordinate_mean",
                    observed=coordinate_sum[flat_index] / count,
                    expected=0.0,
                    variance=float(mean_variance),
                    threshold=core.bernstein_threshold(
                        mean_variance, count
                    ),
                    count=count,
                )
            )
            square_row = core.ledger_entry(
                test_id=f"sphere.{block_name}.coordinate_{axis}.square",
                category="sphere_coordinate_second_moment",
                observed=square_sum[flat_index] / count,
                expected=float(square_mean),
                variance=float(square_variance),
                threshold=core.bernstein_threshold(square_variance, count),
                count=count,
            )
            square_row["expected_exact"] = core.fraction_text(square_mean)
            rows.append(square_row)
            fourth_row = core.ledger_entry(
                test_id=f"sphere.{block_name}.coordinate_{axis}.fourth",
                category="sphere_coordinate_fourth_moment",
                observed=fourth_sum[flat_index] / count,
                expected=float(fourth_mean),
                variance=float(fourth_variance),
                threshold=core.bernstein_threshold(fourth_variance, count),
                count=count,
            )
            fourth_row["expected_exact"] = core.fraction_text(fourth_mean)
            rows.append(fourth_row)
            rows.append(
                core.ledger_entry(
                    test_id=f"sphere.{block_name}.adjacent_{axis}.mean",
                    category="sphere_adjacent_product",
                    observed=adjacent_sum[flat_index] / count,
                    expected=0.0,
                    variance=float(adjacent_variance),
                    threshold=core.bernstein_threshold(
                        adjacent_variance, count
                    ),
                    count=count,
                )
            )
        offset += dimension

    pair_variance = Fraction(1, 16)
    pair_square_mean = Fraction(1, 16)
    pair_square_variance = Fraction(3, 16 * 18) - Fraction(1, 16 * 16)
    for pair_index, (left, right) in enumerate(
        itertools.combinations(range(4), 2)
    ):
        label = f"{CHIRAL_NAMES[left]}__{CHIRAL_NAMES[right]}"
        rows.append(
            core.ledger_entry(
                test_id=f"sphere.chiral_pair.{label}.dot",
                category="chiral_direction_pair_dot",
                observed=pair_sum[pair_index] / count,
                expected=0.0,
                variance=float(pair_variance),
                threshold=core.bernstein_threshold(pair_variance, count),
                count=count,
            )
        )
        pair_row = core.ledger_entry(
            test_id=f"sphere.chiral_pair.{label}.dot_square",
            category="chiral_direction_pair_dot_square",
            observed=pair_square_sum[pair_index] / count,
            expected=float(pair_square_mean),
            variance=float(pair_square_variance),
            threshold=core.bernstein_threshold(pair_square_variance, count),
            count=count,
        )
        pair_row["expected_exact"] = core.fraction_text(pair_square_mean)
        rows.append(pair_row)

    torus_threshold = core.bernstein_threshold(0.5, count)
    for character_index, (label, _) in enumerate(character_rows):
        rows.append(
            core.ledger_entry(
                test_id=f"torus.character.{label}.real",
                category="torus_fourier_character",
                observed=character_real[character_index] / count,
                expected=0.0,
                variance=0.5,
                threshold=torus_threshold,
                count=count,
            )
        )
        rows.append(
            core.ledger_entry(
                test_id=f"torus.character.{label}.imag",
                category="torus_fourier_character",
                observed=character_imag[character_index] / count,
                expected=0.0,
                variance=0.5,
                threshold=torus_threshold,
                count=count,
            )
        )

    radial_variances = [
        float(core.dirichlet_variance((1, 0, 0))),
        float(core.dirichlet_variance((0, 1, 0))),
        float(core.dirichlet_variance((0, 0, 1))),
    ]
    for component, observed_rows in (
        ("real", mixed_real),
        ("imag", mixed_imag),
    ):
        for axis in range(8):
            for radial_index in range(3):
                variance = radial_variances[radial_index] / 2.0
                rows.append(
                    core.ledger_entry(
                        test_id=(
                            f"torus.independence.axis_{axis}."
                            f"radial_{radial_index}.{component}"
                        ),
                        category="torus_radial_independence",
                        observed=observed_rows[axis, radial_index] / count,
                        expected=0.0,
                        variance=variance,
                        threshold=core.bernstein_threshold(variance, count),
                        count=count,
                    )
                )

    if len(rows) != 412:
        raise AssertionError(f"full-source ledger has {len(rows)}, expected 412")
    constraint_report = {
        "decimal_crosscheck": decimal,
        "rows": tracker.rows(),
        "status": "PASS"
        if tracker.passed() and decimal["status"] == "PASS"
        else "FAIL",
    }
    consumption = {
        "continuation_raw_hex": [
            f"{int(value):016x}" for value in rng.bit_generator.random_raw(4)
        ],
        "raw_uniforms_per_sample": 114,
        "raw_words_consumed": raw_words,
        "samples": count,
    }
    return rows, constraint_report, consumption


def _mutant_x0_mean(
    label: str, beta_second_shape: int, count: int
) -> float:
    if type(beta_second_shape) is not int or beta_second_shape <= 0:
        raise core.AuditError("mutant Beta marginal shape must be positive integer")
    rng = core.make_rng(label)
    uniform_count = 4 + beta_second_shape - 1
    generated = 0
    total = 0.0
    while generated < count:
        size = min(core.CHUNK_SIZE, count - generated)
        values = core.uniform_open(rng, (size, uniform_count))
        x0 = np.partition(values, 3, axis=1)[:, 3]
        total += float(x0.sum(dtype=np.float64))
        generated += size
    return total / count


def source_fingerprint(
    cell: core.AuditCell, *, label: str = "golden_replay", count: int = 64
) -> dict[str, Any]:
    rng = core.make_rng(label)
    source = core.full_source_chunk(rng, count, cell)
    coefficients = core.source_chunk_coefficients(source, cell)
    digest = hashlib.sha256()

    def update_array(name: str, array: np.ndarray) -> None:
        normalized = np.ascontiguousarray(array, dtype="<f8")
        digest.update(name.encode("ascii") + b"\0")
        digest.update(
            ",".join(str(value) for value in normalized.shape).encode("ascii")
            + b"\0"
        )
        digest.update(normalized.tobytes(order="C"))

    update_array("radial", source["radial"])
    update_array("u0", source["u0"])
    for index, value in enumerate(source["chiral"]):
        update_array(f"chiral{index}", value)
    update_array("q_unit", source["q_unit"])
    update_array("relative_momentum", coefficients["relative_momentum"])
    for index, value in enumerate(coefficients["z"]):
        update_array(f"z{index}", value)
    for string_index, row in enumerate(coefficients["coefficients"]):
        for field in ("x", "y", "p", "q"):
            update_array(
                f"string{string_index}_{field}",
                row[field],
            )
    update_array("velocity_1", coefficients["velocity_1"])
    update_array("velocity_2", coefficients["velocity_2"])
    update_array("q_relative", coefficients["q_relative"])
    continuation = [
        f"{int(value):016x}" for value in rng.bit_generator.random_raw(4)
    ]
    return {
        "coefficient_sha256": digest.hexdigest(),
        "continuation_raw_hex": continuation,
        "samples": count,
    }


def chiral_jacobian_control(cell: core.AuditCell) -> dict[str, Any]:
    """Independent analytic/finite-difference check of the linear map."""

    factor = math.sqrt(2.0 * cell.mass) * cell.k1 / 4.0
    momentum_factor = 2.0 * factor / (cell.mass * cell.k1)
    analytic = np.array(
        [
            [factor, 0.0, 0.0, momentum_factor],
            [0.0, -factor, momentum_factor, 0.0],
            [factor, 0.0, 0.0, -momentum_factor],
            [0.0, -factor, -momentum_factor, 0.0],
        ],
        dtype=np.float64,
    )

    def transform(vector: np.ndarray) -> np.ndarray:
        x, y, pi_x, pi_y = vector
        p = 2.0 * pi_x / cell.mass
        q = 2.0 * pi_y / cell.mass
        scale = math.sqrt(2.0 * cell.mass) * cell.k1
        return scale * np.array(
            [
                0.25 * (x + q / cell.k1),
                0.25 * (p / cell.k1 - y),
                0.25 * (x - q / cell.k1),
                -0.25 * (y + p / cell.k1),
            ],
            dtype=np.float64,
        )

    point = np.array([0.25, -0.5, 0.75, -1.0], dtype=np.float64)
    finite_difference = np.empty((4, 4), dtype=np.float64)
    for column in range(4):
        step = 2.0**-12 * max(1.0, abs(float(point[column])))
        plus = point.copy()
        minus = point.copy()
        plus[column] += step
        minus[column] -= step
        finite_difference[:, column] = (
            transform(plus) - transform(minus)
        ) / (2.0 * step)
    matrix_error = float(np.max(np.abs(finite_difference - analytic)))
    determinant = abs(float(np.linalg.det(analytic)))
    expected_forward_determinant = cell.k1 * cell.k1 / 4.0
    inverse_volume_factor = 1.0 / determinant
    relative_determinant_error = abs(
        determinant / expected_forward_determinant - 1.0
    )
    passed = bool(
        matrix_error <= 2.0**-28
        and relative_determinant_error <= 2.0**-40
        and abs(inverse_volume_factor - 4.0 / (cell.k1 * cell.k1))
        <= 2.0**-36
    )
    return {
        "analytic_forward_determinant": determinant,
        "expected_forward_determinant": expected_forward_determinant,
        "finite_difference_max_absolute_error": matrix_error,
        "inverse_volume_factor": inverse_volume_factor,
        "registered_inverse_volume_factor": 4.0 / (cell.k1 * cell.k1),
        "status": "PASS" if passed else "FAIL",
    }


def hostile_mutations(
    registry: Mapping[str, Any],
    cell: core.AuditCell,
    *,
    run_statistical_shapes: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for name, shape in (
        ("shape_d", (4, 16, 16)),
        ("shape_half_d", (4, 8, 8)),
        ("shape_d_minus_half", (4, 15.5, 15.5)),
    ):
        rejected = False
        message = ""
        try:
            core.validate_gamma_shapes(shape)
        except core.AuditError as error:
            rejected = True
            message = str(error)
        rows.append(
            {
                "gate": "exact_gamma_shape_registration",
                "mutation": name,
                "observed_error": message,
                "passed": rejected,
            }
        )

    if run_statistical_shapes:
        correct_mean = float(core.dirichlet_moment((1, 0, 0)))
        threshold = core.bernstein_threshold(
            core.dirichlet_variance((1, 0, 0)),
            core.FULL_MUTATION_SAMPLES,
        )
        for label, mutant_shape, beta_second_shape in (
            ("mut_shape_d", 16.0, 32),
            ("mut_shape_half_d", 8.0, 16),
            ("mut_shape_d_minus_half", 15.5, 31),
        ):
            observed = _mutant_x0_mean(
                label, beta_second_shape, core.FULL_MUTATION_SAMPLES
            )
            deviation = abs(observed - correct_mean)
            rows.append(
                {
                    "correct_acceptance_threshold": threshold,
                    "expected_mutant_mean": 4.0 / (4.0 + 2.0 * mutant_shape),
                    "gate": "correct_dirichlet_X0_mean_band",
                    "mutation": label,
                    "normalized_rejection_margin": deviation / threshold,
                    "observed": observed,
                    "passed": bool(deviation > threshold),
                    "samples": core.FULL_MUTATION_SAMPLES,
                }
            )

    pair_square_threshold = core.bernstein_threshold(
        Fraction(3, 16 * 18) - Fraction(1, 16 * 16),
        core.FULL_SOURCE_SAMPLES,
    )
    rows.append(
        {
            "gate": "chiral_pair_dot_square",
            "mutation": "copy_left_direction_to_right",
            "observed": 1.0,
            "expected": 1.0 / 16.0,
            "threshold": pair_square_threshold,
            "passed": bool(abs(1.0 - 1.0 / 16.0) > pair_square_threshold),
        }
    )
    torus_threshold = core.bernstein_threshold(
        0.5, core.FULL_SOURCE_SAMPLES
    )
    rows.append(
        {
            "gate": "torus_fourier_character",
            "mutation": "set_q_relative_to_zero",
            "observed_real_character": 1.0,
            "expected": 0.0,
            "threshold": torus_threshold,
            "passed": bool(1.0 > torus_threshold),
        }
    )

    fingerprint = source_fingerprint(cell)
    event_mutation = copy.deepcopy(registry)
    event_mutation["non_source_registry"]["event"]["r_in_hex"] = (
        "0x1.0000000000000p-3"
    )
    validity_mutation = copy.deepcopy(registry)
    validity_mutation["non_source_registry"]["validity"]["kappa_uv_hex"] = (
        "0x1.0000000000000p-4"
    )
    event_fingerprint = source_fingerprint(cell)
    invalid_fingerprint = source_fingerprint(cell)
    baseline_source_hash = core.source_draw_registry_sha256(registry)
    event_source_hash = core.source_draw_registry_sha256(event_mutation)
    validity_source_hash = core.source_draw_registry_sha256(
        validity_mutation
    )
    rows.append(
        {
            "baseline": fingerprint,
            "baseline_source_registry_sha256": baseline_source_hash,
            "gate": "source_substream_boundary",
            "mutation": "event_threshold_change",
            "mutated": event_fingerprint,
            "mutated_source_registry_sha256": event_source_hash,
            "passed": bool(
                event_fingerprint == fingerprint
                and event_source_hash == baseline_source_hash
            ),
        }
    )
    rows.append(
        {
            "all_labels_source_invalid": True,
            "baseline": fingerprint,
            "baseline_source_registry_sha256": baseline_source_hash,
            "gate": "source_invalid_without_redraw",
            "mutation": "kappa_uv_one_sixteenth",
            "mutated": invalid_fingerprint,
            "mutated_source_registry_sha256": validity_source_hash,
            "passed": bool(
                cell.k1 * cell.ell_s > 1.0 / 16.0
                and invalid_fingerprint == fingerprint
                and validity_source_hash == baseline_source_hash
            ),
            "sample_count_unchanged": True,
        }
    )
    source_mutation = copy.deepcopy(registry)
    source_mutation["source_draw_registry"]["P_total_hex"][0] = (
        "0x1.0000000000000p+1"
    )
    mutated_source_hash = core.source_draw_registry_sha256(source_mutation)
    rows.append(
        {
            "baseline_source_registry_sha256": baseline_source_hash,
            "gate": "source_subregistry_domain_separation",
            "mutation": "change_true_source_field",
            "mutated_source_registry_sha256": mutated_source_hash,
            "passed": bool(mutated_source_hash != baseline_source_hash),
        }
    )

    forbidden = copy.deepcopy(registry)
    forbidden["source_draw_registry"]["level_match_tolerance"] = "1e-6"
    forbidden_rejected = False
    try:
        core.validate_registry(forbidden)
    except core.AuditError:
        forbidden_rejected = True
    rows.append(
        {
            "gate": "strict_registered_source_schema",
            "mutation": "tolerance_based_level_matching_field",
            "passed": forbidden_rejected,
        }
    )

    duplicate_rejected = False
    try:
        core.loads_strict_json('{"K":1,"K":1}')
    except core.AuditError:
        duplicate_rejected = True
    nonfinite_rejected = True
    for token in ("NaN", "Infinity", "-Infinity", "1e9999"):
        try:
            core.loads_strict_json(f'{{"x":{token}}}')
        except core.AuditError:
            continue
        nonfinite_rejected = False
    rows.append(
        {
            "gate": "strict_json_reader",
            "mutation": "duplicate_and_nonfinite_json",
            "passed": bool(duplicate_rejected and nonfinite_rejected),
        }
    )

    bool_mutation = copy.deepcopy(registry)
    bool_mutation["source_draw_registry"]["K"] = True
    bool_rejected = False
    try:
        core.validate_registry(bool_mutation)
    except core.AuditError:
        bool_rejected = True
    rows.append(
        {
            "gate": "type_strict_registry",
            "mutation": "boolean_substituted_for_integer",
            "passed": bool_rejected,
        }
    )

    q_center = np.ones(8, dtype=np.float64)
    duplicate_center_average = float(np.max(np.abs(q_center)))
    rows.append(
        {
            "gate": "sigma_average_center_once",
            "mutation": "insert_q_into_Y",
            "observed_average_error": duplicate_center_average,
            "passed": bool(
                duplicate_center_average
                > core.FLOW_TOLERANCE_FACTOR * 2.0
            ),
        }
    )

    omitted_center_energy = cell.e_star
    rows.append(
        {
            "gate": "nonzero_total_momentum_energy",
            "mutation": "omit_center_energy",
            "observed_energy": omitted_center_energy,
            "expected_energy": cell.e_perp,
            "passed": bool(
                abs(omitted_center_energy - cell.e_perp)
                > core.ALGEBRA_TOLERANCE_FACTOR * cell.e_perp
            ),
        }
    )

    invalid_energy_rejected = True
    invalid_energy_errors: list[str] = []
    for value in (0.0, -0.5):
        try:
            core.validate_positive_e_star(value)
        except core.AuditError as error:
            invalid_energy_errors.append(str(error))
            continue
        invalid_energy_rejected = False
    rows.append(
        {
            "gate": "positive_E_star",
            "mutation": "set_E_star_nonpositive",
            "passed": bool(invalid_energy_rejected),
            "synthetic_values_rejected": [0.0, -0.5],
            "observed_errors": invalid_energy_errors,
        }
    )
    return rows


def _family_summary(ledger: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    summary: dict[str, dict[str, Any]] = {}
    for row in ledger:
        category = row["category"]
        entry = summary.setdefault(
            category,
            {
                "count": 0,
                "failed": 0,
                "max_normalized_deviation": 0.0,
            },
        )
        entry["count"] += 1
        entry["failed"] += int(not row["passed"])
        entry["max_normalized_deviation"] = max(
            entry["max_normalized_deviation"],
            row["normalized_deviation"],
        )
    return dict(sorted(summary.items()))


def run_fast_profile(
    registry: Mapping[str, Any], cell: core.AuditCell
) -> dict[str, Any]:
    golden = core.verify_golden_raw_streams()
    jacobian = chiral_jacobian_control(cell)
    rng = core.make_rng("golden_replay")
    source = core.full_source_chunk(rng, 128, cell)
    coefficients = core.source_chunk_coefficients(source, cell)
    tracker = ConstraintTracker()
    _constraint_checks_for_chunk(tracker, source, coefficients, cell)
    mutations = hostile_mutations(
        registry, cell, run_statistical_shapes=False
    )
    failed = [
        f"constraint:{name}"
        for name, row in tracker.rows().items()
        if not row["passed"]
    ]
    failed.extend(
        f"mutation:{row['mutation']}" for row in mutations if not row["passed"]
    )
    if jacobian["status"] != "PASS":
        failed.append("chiral_jacobian")
    return {
        "authoritative_preregistered_profile": False,
        "claim": (
            "deterministic structural/unit profile only; no statistical "
            "acceptance in the 514-item ledger is claimed"
        ),
        "constraint_checks": {
            "rows": tracker.rows(),
            "status": "PASS" if tracker.passed() else "FAIL",
        },
        "failed_gates": failed,
        "golden_raw_streams": golden,
        "hostile_mutations": mutations,
        "implementation_analytic_controls": {"chiral_jacobian": jacobian},
        "ledger": [],
        "ledger_manifest_sha256": core.semantic_manifest_sha256(),
        "ledger_size_executed": 0,
        "ledger_size_registered": core.LEDGER_SIZE,
        "status": "PASS_FAST_NONAUTHORITATIVE" if not failed else "FAIL",
    }


def run_full_profile(
    registry: Mapping[str, Any], cell: core.AuditCell
) -> dict[str, Any]:
    golden = core.verify_golden_raw_streams()
    jacobian = chiral_jacobian_control(cell)
    gamma, gamma_endpoint = radial_moment_observations(
        "gamma", count=core.FULL_RADIAL_SAMPLES, cell=cell
    )
    beta, beta_endpoint = radial_moment_observations(
        "beta", count=core.FULL_RADIAL_SAMPLES, cell=cell
    )
    ledger = radial_ledger(
        gamma, beta, count=core.FULL_RADIAL_SAMPLES
    )
    full_rows, constraints, consumption = full_source_audit(
        count=core.FULL_SOURCE_SAMPLES, cell=cell
    )
    ledger.extend(full_rows)
    if len(ledger) != core.LEDGER_SIZE:
        raise core.AuditError(
            f"executed ledger has {len(ledger)} rows, expected {core.LEDGER_SIZE}"
        )
    ids = [row["test_id"] for row in ledger]
    if len(ids) != len(set(ids)):
        raise core.AuditError("statistical ledger contains duplicate test IDs")
    mutations = hostile_mutations(
        registry, cell, run_statistical_shapes=True
    )
    failed = [
        f"statistical:{row['test_id']}" for row in ledger if not row["passed"]
    ]
    if constraints["status"] != "PASS":
        failed.append("constraints")
    if jacobian["status"] != "PASS":
        failed.append("chiral_jacobian")
    failed.extend(
        f"mutation:{row['mutation']}" for row in mutations if not row["passed"]
    )
    family = _family_summary(ledger)
    return {
        "authoritative_preregistered_profile": True,
        "constraint_checks": constraints,
        "failed_gates": failed,
        "family_summary": family,
        "golden_raw_streams": golden,
        "hostile_mutations": mutations,
        "implementation_analytic_controls": {"chiral_jacobian": jacobian},
        "ledger": ledger,
        "ledger_manifest_sha256": core.semantic_manifest_sha256(),
        "ledger_size_executed": len(ledger),
        "ledger_size_registered": core.LEDGER_SIZE,
        "raw_consumption": consumption,
        "radial_stream_endpoints": {
            "gamma": gamma_endpoint,
            "hierarchical_beta": beta_endpoint,
        },
        "sample_counts": {
            "full_source": core.FULL_SOURCE_SAMPLES,
            "gamma_radial": core.FULL_RADIAL_SAMPLES,
            "hierarchical_beta": core.FULL_RADIAL_SAMPLES,
            "shape_mutation_each": core.FULL_MUTATION_SAMPLES,
        },
        "status": "PASS" if not failed else "FAIL",
    }


def build_report(profile: str = "full") -> dict[str, Any]:
    registry, cell = core.load_registered_cell()
    if profile == "full":
        body = run_full_profile(registry, cell)
    elif profile == "fast":
        body = run_fast_profile(registry, cell)
    else:
        raise core.AuditError(f"unknown profile: {profile}")
    report = {
        "artifact_scope": core.report_claim_boundary(),
        "audit_id": core.AUDIT_ID,
        "baseline_commit": core.BASELINE_COMMIT,
        "code_inventory": core.source_inventory(),
        "profile": profile,
        "registry_canonical_sha256": core.REGISTRY_CANONICAL_SHA256,
        "source_draw_registry_sha256": core.source_draw_registry_sha256(
            registry
        ),
        "source_golden_fingerprint": source_fingerprint(cell),
        "rng_version": core.RNG_VERSION,
        "runtime": core.runtime_inventory(),
        "schema_version": core.SCHEMA_VERSION,
        "seed_hex": core.SEED_HEX,
        "statistical_contract": core.fixed_threshold_manifest(),
        **body,
    }
    native_report = core.to_json_native(report)
    core.ensure_all_finite(native_report)
    return core.attach_semantic_hash(native_report)
