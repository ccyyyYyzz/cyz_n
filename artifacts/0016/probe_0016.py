#!/usr/bin/env python3
"""Deterministic standard-Python probe for Brief 0016.

The probe separates carrier dimension p, local encounter kinematic rank a, and
anonymous response-visible spatial rank m.  It does not receive or branch on a
response rank.  It evaluates two declared impact-profile controls, emits the
fixed-arity onset table, and replays coordinate-whitened F1 Gram controls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, getcontext, localcontext
from pathlib import Path
from typing import Any, Iterable, Sequence

getcontext().prec = 100
D = Decimal

RHO_TABLE = (D("0.25"), D("0.5"), D("1"), D("2"), D("4"))
RHO_VERIFY = tuple(D(i) / D(8) for i in range(1, 33))  # 0.125 ... 4
C_VALUES = tuple(range(7))
SERIES_TOL = D("1e-88")
ORDER_TOL = D("1e-70")
RANK_TOL = D("1e-35")
REPORTED_DIGITS = 16


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def decimal_text(x: Decimal, digits: int = REPORTED_DIGITS) -> str:
    if x == 0:
        return "0"
    with localcontext() as ctx:
        ctx.prec = max(getcontext().prec, digits + 20)
        return format(x, f".{digits}E")


def integral_unit_exp(power: int, rho: Decimal) -> Decimal:
    """High-precision series for integral_0^1 u^power exp(-rho^2 u^2) du."""
    if power < 0 or rho < 0:
        raise ValueError("power and rho must be nonnegative")
    x = rho * rho
    total = D(0)
    factorial = D(1)
    x_power = D(1)
    sign = D(1)
    for n in range(10000):
        denominator = factorial * D(power + 2 * n + 1)
        term = sign * x_power / denominator
        total += term
        if n > int(x) + 12 and abs(term) < SERIES_TOL:
            return +total
        sign = -sign
        x_power *= x
        factorial *= D(n + 1)
    raise RuntimeError("series did not converge")


def g_ball(c: int, rho: Decimal) -> Decimal:
    if c == 0:
        return D(1)
    return D(c) * integral_unit_exp(c - 1, rho)


def g_box(c: int, rho: Decimal) -> Decimal:
    if c == 0:
        return D(1)
    base = integral_unit_exp(0, rho)
    return base ** c


def falling_factorial(q: int, a: int) -> int:
    if q < a:
        return 0
    out = 1
    for k in range(a):
        out *= q - k
    return out


def transpose(matrix: Sequence[Sequence[Decimal]]) -> list[list[Decimal]]:
    return [list(row) for row in zip(*matrix)]


def matmul(a: Sequence[Sequence[Decimal]], b: Sequence[Sequence[Decimal]]) -> list[list[Decimal]]:
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def jacobi_eigenvalues_symmetric(matrix: Sequence[Sequence[Decimal]]) -> list[Decimal]:
    a = [list(row) for row in matrix]
    n = len(a)
    for _ in range(200):
        p, q = 0, 1
        maximum = D(0)
        for i in range(n):
            for j in range(i + 1, n):
                if abs(a[i][j]) > maximum:
                    maximum = abs(a[i][j])
                    p, q = i, j
        if maximum < D("1e-85"):
            break
        apq = a[p][q]
        tau = (a[q][q] - a[p][p]) / (D(2) * apq)
        sign = D(1) if tau >= 0 else D(-1)
        t = sign / (abs(tau) + (D(1) + tau * tau).sqrt())
        c = D(1) / (D(1) + t * t).sqrt()
        s = t * c
        app = a[p][p]
        aqq = a[q][q]
        a[p][p] = c * c * app - D(2) * s * c * apq + s * s * aqq
        a[q][q] = s * s * app + D(2) * s * c * apq + c * c * aqq
        a[p][q] = a[q][p] = D(0)
        for k in range(n):
            if k in (p, q):
                continue
            akp = a[k][p]
            akq = a[k][q]
            a[k][p] = a[p][k] = c * akp - s * akq
            a[k][q] = a[q][k] = s * akp + c * akq
    return sorted((max(D(0), a[i][i]) for i in range(n)), reverse=True)


def whiten_columns(raw_columns: Sequence[Sequence[Decimal]], g_diag: Sequence[Decimal], h_diag: Sequence[Decimal]) -> list[list[Decimal]]:
    d = len(g_diag)
    n = len(h_diag)
    if len(raw_columns) != n or any(len(col) != d for col in raw_columns):
        raise ValueError("column dimensions do not match G and H")
    out = [[D(0) for _ in range(n)] for _ in range(d)]
    for j, col in enumerate(raw_columns):
        hs = h_diag[j].sqrt()
        for i in range(d):
            out[i][j] = g_diag[i].sqrt() * col[i] / hs
    return out


def singular_values(raw_columns: Sequence[Sequence[Decimal]], g_diag: Sequence[Decimal], h_diag: Sequence[Decimal]) -> list[Decimal]:
    jhat = whiten_columns(raw_columns, g_diag, h_diag)
    gram = matmul(transpose(jhat), jhat)
    return [ev.sqrt() for ev in jacobi_eigenvalues_symmetric(gram)]


def unit(v: Sequence[Decimal]) -> list[Decimal]:
    norm = sum(x * x for x in v).sqrt()
    return [x / norm for x in v]


def gram_controls() -> list[dict[str, Any]]:
    z = D(0)
    o = D(1)
    eps = D("0.01")
    e1 = [o, z, z]
    e2 = [z, o, z]
    e3 = [z, z, o]
    tau2_near = unit([-o, -eps, z])
    controls = [
        {
            "id": "full_rank_noncollinear",
            "tau1": e1,
            "tau2": e2,
            "v_rel": e3,
            "G_diag": [o, o, o],
            "H_e_diag": [o, o, o],
            "expected_rank": 3,
            "classification": "open rank-three encounter jet",
        },
        {
            "id": "near_opposite_with_tangent_wiggle",
            "tau1": e1,
            "tau2": tau2_near,
            "v_rel": e3,
            "G_diag": [o, o, o],
            "H_e_diag": [o, o, o],
            "expected_rank": 3,
            "classification": "rank three but small preparation margin",
        },
        {
            "id": "straight_opposite_same_cycle",
            "tau1": e1,
            "tau2": [-o, z, z],
            "v_rel": e2,
            "G_diag": [o, o, o],
            "H_e_diag": [o, o, o],
            "expected_rank": 2,
            "classification": "mandatory opposite-winding degeneracy",
        },
        {
            "id": "relative_velocity_in_tangent_span",
            "tau1": e1,
            "tau2": e2,
            "v_rel": unit([o, o, z]),
            "G_diag": [o, o, o],
            "H_e_diag": [o, o, o],
            "expected_rank": 2,
            "classification": "velocity-column degeneracy",
        },
        {
            "id": "full_rank_rescaled_domain_metric",
            "tau1": e1,
            "tau2": e2,
            "v_rel": e3,
            "G_diag": [o, o, o],
            "H_e_diag": [D(4), o, o],
            "expected_rank": 3,
            "classification": "rank invariant; sigma magnitude depends on H_e",
        },
        {
            "id": "rank_one_collinear",
            "tau1": e1,
            "tau2": [-o, z, z],
            "v_rel": e1,
            "G_diag": [o, o, o],
            "H_e_diag": [o, o, o],
            "expected_rank": 1,
            "classification": "fully collinear degeneracy",
        },
    ]
    result = []
    for item in controls:
        # D Phi = [tau1, -tau2, v_rel].
        columns = [item["tau1"], [-x for x in item["tau2"]], item["v_rel"]]
        svals_raw = singular_values(columns, item["G_diag"], item["H_e_diag"])
        svals = [D(0) if s <= RANK_TOL else s for s in svals_raw]
        rank = sum(1 for s in svals if s > 0)
        if rank != item["expected_rank"]:
            raise AssertionError(f"{item['id']}: expected rank {item['expected_rank']}, observed {rank}")
        result.append({
            "id": item["id"],
            "classification": item["classification"],
            "G_diag": [str(x) for x in item["G_diag"]],
            "H_e_diag": [str(x) for x in item["H_e_diag"]],
            "tau1": [str(x) for x in item["tau1"]],
            "tau2": [str(x) for x in item["tau2"]],
            "v_rel": [str(x) for x in item["v_rel"]],
            "singular_values": [decimal_text(x, 24) for x in svals],
            "sigma_3": decimal_text(svals[2], 24),
            "observed_rank": rank,
            "expected_rank": item["expected_rank"],
        })
    return result


def verify_suppression_ordering() -> dict[str, Any]:
    checks = 0
    minimum_gap = None
    for family in (g_ball, g_box):
        # Strict decrease in codimension for rho > 0.
        for rho in RHO_VERIFY:
            values = [family(c, rho) for c in C_VALUES]
            for c in range(6):
                gap = values[c] - values[c + 1]
                if gap <= ORDER_TOL:
                    raise AssertionError(f"codimension monotonicity failed at rho={rho}, c={c}")
                minimum_gap = gap if minimum_gap is None else min(minimum_gap, gap)
                checks += 1
        # Strict decrease in rho for c > 0.
        for c in range(1, 7):
            values = [family(c, rho) for rho in RHO_VERIFY]
            for i in range(len(values) - 1):
                gap = values[i] - values[i + 1]
                if gap <= ORDER_TOL:
                    raise AssertionError(f"rho monotonicity failed at c={c}, i={i}")
                minimum_gap = min(minimum_gap, gap) if minimum_gap is not None else gap
                checks += 1
    return {
        "precision_decimal_digits": getcontext().prec,
        "reported_digits": REPORTED_DIGITS,
        "verification_rho_grid": [str(x) for x in RHO_VERIFY],
        "strict_checks": checks,
        "minimum_observed_gap": decimal_text(minimum_gap or D(0), 24),
        "tolerance": str(ORDER_TOL),
        "status": "PASS",
    }


def build_report() -> dict[str, Any]:
    suppression = {}
    for rho in RHO_TABLE:
        suppression[str(rho)] = {
            "ball": {str(c): decimal_text(g_ball(c, rho)) for c in C_VALUES},
            "box": {str(c): decimal_text(g_box(c, rho)) for c in C_VALUES},
        }
    onset = {
        str(q): {str(a): falling_factorial(q, a) for a in range(1, 5)}
        for q in range(10)
    }
    report = {
        "schema_version": "cyz-0016-kinematic-rank-probe-v1",
        "brief_commit": "3c4cdf51c22278d26f2e2365d8719a153df4369a",
        "probe_scope": "geometric theorem and deterministic numerical controls; not a physical return kernel",
        "no_target_rank_input_or_branch": True,
        "distinctions": {
            "p": "microscopic carrier spatial dimension",
            "a": "rank of the coordinate-safe encounter jet D Phi",
            "m": "later anonymous response-visible spatial rank; absent from this probe",
        },
        "encounter_jet": {
            "coordinate_safe_map": "local Log map inside an injectivity tube, otherwise transversality to the diagonal in M x M",
            "whitened_matrix": "Jhat = G^(1/2) D_Phi H_e^(-1/2)",
            "impact_condition": "at an interior closest approach b=Phi(z*) and J^T G b=0; b is in N_j and is not a column of J",
            "uniform_margin_status": "sufficient but not necessary; a small-sigma tail plus explicit lower-rank mixture is an alternative",
        },
        "suppression_formulas": {
            "g0": "1",
            "ball": "c * integral_0^1 u^(c-1) exp(-rho^2 u^2) du",
            "box": "[integral_0^1 exp(-rho^2 u^2) du]^c",
            "profile_boundary": "full-support Gaussian integration is a declared closure because the cited GKM Gaussian is a large-impact asymptotic",
        },
        "rho_table_grid": [str(x) for x in RHO_TABLE],
        "suppression_table": suppression,
        "suppression_verification": verify_suppression_ordering(),
        "valid_frame_onset": {
            "formula": "q!/(q-a)! for q>=a, else 0",
            "q_range": [0, 9],
            "a_range": [1, 4],
            "table": onset,
            "interpretation": "fixed-constructor onset only; not visible dimension",
        },
        "gram_controls": gram_controls(),
        "source_classification": {
            "primary_source_derived": [
                "JJP local collision uses two generally non-collinear string tangents and relative velocity; transverse q/b do not supply an incoming column",
                "GKM schedules recollisions numerically at approximately r/vbar and redraws impact parameter; this is a numerical closure",
                "GKM Gaussian impact profile is quoted in a large-impact asymptotic regime",
                "the p-brane 2p+1 intersection ceiling is a carrier/encounter statement",
            ],
            "exact_declared_geometric_model": [
                "rank and normal-dimension theorems",
                "fixed-arity superselection and falling-factorial onset",
                "ball/box monotonicity formulas",
            ],
            "no_go_underdetermination": [
                "straight same-cycle opposite winding has rank at most two",
                "the cited sources do not provide a local tangent-wiggle preparation with positive sigma_3 margin or controlled tail",
                "impact suppression alone cannot distinguish source ranks one, two, and three on the lower side",
            ],
            "controlled_numerical_probe": [
                "high-precision ball/box tables and monotonicity checks",
                "six whitened Gram controls",
            ],
            "open_gate": [
                "joint preparation and source-to-return law for event jet j, impact b in N_j, absolute return time, history, reaction, reservoir transfer, and killed exits",
                "anonymous response reconstruction and entrant strict-residence comparison",
            ],
        },
        "verdict": "conditional source-family three-ceiling under rank-three event-jet preparation; no strict three-selection and no visible-m ceiling",
    }
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic Brief 0016 kinematic-rank and impact-codimension probe.")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("probe_report.json"))
    parser.add_argument("--check", action="store_true", help="compare generated canonical payload with an existing report")
    args = parser.parse_args(argv)
    report = build_report()
    payload = canonical_bytes(report) + b"\n"
    if args.check:
        if not args.output.exists() or args.output.read_bytes() != payload:
            raise SystemExit("report mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    print(json.dumps({
        "status": "PASS",
        "output": str(args.output),
        "canonical_payload_sha256": hashlib.sha256(canonical_bytes(report)).hexdigest(),
        "gram_controls": len(report["gram_controls"]),
        "suppression_checks": report["suppression_verification"]["strict_checks"],
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
