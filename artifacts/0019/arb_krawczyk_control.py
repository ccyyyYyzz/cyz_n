#!/usr/bin/env python3
"""Three-variable Arb Krawczyk inclusion for the Brief 0019 jet fixture."""

from __future__ import annotations

import argparse
import copy
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

from flint import arb

import arb_interval_jets as jets


REPORT_SCHEMA = "cyz-brief-0019-arb-krawczyk-report-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_REPORT = HERE / "arb_krawczyk_report.json"
AXES = ("sigma1", "sigma2", "time")


def uniqueness_box() -> dict[str, Any]:
    width = Fraction(1, 32)
    return {
        axis: jets.closed_interval(-width, width)
        for axis in AXES
    }


def preconditioner() -> list[list[Fraction]]:
    return [
        [Fraction(1, 2), Fraction(), Fraction()],
        [Fraction(), Fraction(1, 2), Fraction()],
        [Fraction(), Fraction(), Fraction(-2)],
    ]


def _matrix_vector(
    matrix: Sequence[Sequence[arb]], vector: Sequence[arb]
) -> list[arb]:
    if len(matrix) != len(vector):
        raise jets.JetError("matrix/vector shape mismatch")
    result: list[arb] = []
    for row in matrix:
        if len(row) != len(vector):
            raise jets.JetError("matrix row shape mismatch")
        total = arb(0)
        for coefficient, value in zip(row, vector):
            total += coefficient * value
        result.append(total)
    return result


def _matrix_multiply(
    left: Sequence[Sequence[arb]],
    right: Sequence[Sequence[arb]],
) -> list[list[arb]]:
    if not left or not right:
        raise jets.JetError("empty matrices are forbidden")
    inner = len(right)
    columns = len(right[0])
    if any(len(row) != inner for row in left):
        raise jets.JetError("left matrix shape mismatch")
    if any(len(row) != columns for row in right):
        raise jets.JetError("right matrix is ragged")
    output: list[list[arb]] = []
    for row in left:
        output_row: list[arb] = []
        for column in range(columns):
            total = arb(0)
            for index in range(inner):
                total += row[index] * right[index][column]
            output_row.append(total)
        output.append(output_row)
    return output


def _arb_matrix(values: Sequence[Sequence[Fraction]]) -> list[list[arb]]:
    return [
        [jets.exact_arb(value) for value in row]
        for row in values
    ]


def _identity_minus(matrix: Sequence[Sequence[arb]]) -> list[list[arb]]:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise jets.JetError("identity subtraction requires a square matrix")
    return [
        [
            arb(1 if row == column else 0) - matrix[row][column]
            for column in range(size)
        ]
        for row in range(size)
    ]


def _box_vector(box: Mapping[str, Any]) -> list[arb]:
    return [
        jets.interval_arb(box[axis], f"$.krawczyk_box.{axis}")
        for axis in AXES
    ]


def _bounds(value: arb) -> dict[str, str]:
    return {"lower": str(value.lower()), "upper": str(value.upper())}


def compute_krawczyk(
    fixture: Mapping[str, Any],
    box: Mapping[str, Any],
    *,
    C_fraction: Sequence[Sequence[Fraction]] | None = None,
    precision_bits: int = jets.DEFAULT_PRECISION_BITS,
) -> dict[str, Any]:
    registered = copy.deepcopy(fixture)
    registered["control_box"] = copy.deepcopy(box)
    point = jets.evaluate_interval_jets(
        registered, "root_box", precision_bits=precision_bits
    )
    enclosure = jets.evaluate_interval_jets(
        registered, "control_box", precision_bits=precision_bits
    )
    C_values = (
        preconditioner() if C_fraction is None else [list(row) for row in C_fraction]
    )
    C = _arb_matrix(C_values)
    x0 = [arb(0), arb(0), arb(0)]
    B_minus_x0 = _box_vector(box)
    centre_term = [
        x - correction
        for x, correction in zip(x0, _matrix_vector(C, point["g"]))
    ]
    C_Dg = _matrix_multiply(C, enclosure["Dg"])
    remainder = _matrix_vector(_identity_minus(C_Dg), B_minus_x0)
    K = [
        centre + residual
        for centre, residual in zip(centre_term, remainder)
    ]

    strict_margins: list[dict[str, arb]] = []
    inclusion: list[bool] = []
    for axis, image in zip(AXES, K):
        interval = jets.interval_arb(box[axis], f"$.krawczyk_box.{axis}")
        lower_margin = image.lower() - interval.lower()
        upper_margin = interval.upper() - image.upper()
        strict_margins.append(
            {"lower": lower_margin, "upper": upper_margin}
        )
        inclusion.append(
            bool(lower_margin > arb(0) and upper_margin > arb(0))
        )
    return {
        "point": point,
        "enclosure": enclosure,
        "preconditioner": C,
        "centre_term": centre_term,
        "remainder_matrix": _identity_minus(C_Dg),
        "K": K,
        "strict_margins": strict_margins,
        "axis_inclusion": inclusion,
        "strict_inclusion": all(inclusion),
    }


def build_report(fixture: Mapping[str, Any]) -> dict[str, Any]:
    jets.check_backend()
    box = uniqueness_box()
    result = compute_krawczyk(fixture, box)
    wide_box = {
        axis: jets.closed_interval(Fraction(-1, 16), Fraction(1, 16))
        for axis in AXES
    }
    wide_result = compute_krawczyk(fixture, wide_box)
    gates = {
        "point_g_is_exact_zero": all(value == arb(0) for value in result["point"]["g"]),
        "three_axis_strict_inclusion": result["strict_inclusion"],
        "wide_box_rejected_as_noninclusion": not wide_result["strict_inclusion"],
        "preconditioner_is_exact_inverse_at_root": (
            result["point"]["det_Dg"] == jets.exact_arb(-2)
        ),
    }
    failed = sorted(name for name, value in gates.items() if not value)
    payload: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "fixture_semantic_sha256": jets.canonical_sha256(fixture),
        "backend": jets.check_backend(),
        "precision_bits": jets.DEFAULT_PRECISION_BITS,
        "krawczyk_box": box,
        "preconditioner": [
            [jets.dyadic_json(value) for value in row]
            for row in preconditioner()
        ],
        "K_enclosures": {
            axis: _bounds(value)
            for axis, value in zip(AXES, result["K"])
        },
        "strict_margins": {
            axis: {
                "lower": _bounds(margins["lower"]),
                "upper": _bounds(margins["upper"]),
            }
            for axis, margins in zip(AXES, result["strict_margins"])
        },
        "gates": gates,
        "failed_gates": failed,
        "scope": {
            "finite_K_trigonometric_fixture": True,
            "three_variable_arb_krawczyk_inclusion": True,
            "source_population_bound": False,
            "global_no_earlier_entry_proved": False,
            "physical_solver_complete": False,
            "three_plus_one_selected": False,
        },
        "status": "PASS" if not failed else "FAIL",
        "code_inventory": {
            "arb_interval_jets.py": jets.normalized_lf_sha256(
                HERE / "arb_interval_jets.py"
            ),
            "arb_krawczyk_control.py": jets.normalized_lf_sha256(Path(__file__)),
        },
    }
    payload["semantic_sha256"] = jets.canonical_sha256(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fixture", type=Path, default=jets.DEFAULT_FIXTURE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    if arguments.write and arguments.check:
        raise SystemExit("--write and --check are mutually exclusive")
    fixture = jets.load_strict_json(arguments.fixture)
    jets.validate_fixture(fixture)
    report = build_report(fixture)
    if arguments.write:
        jets.write_json(arguments.report, report)
    elif arguments.check:
        stored = jets.load_strict_json(arguments.report)
        if not jets.semantic_equal(stored, report):
            raise SystemExit("stored Arb Krawczyk report differs from replay")
    print(
        json.dumps(
            {
                "report_semantic_sha256": report["semantic_sha256"],
                "status": report["status"],
                "strict_inclusion": report["gates"][
                    "three_axis_strict_inclusion"
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
