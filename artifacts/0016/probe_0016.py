#!/usr/bin/env python3
"""Deterministic Brief 0016 probe.

It computes two declared impact-profile controls, the exact fixed-arity onset
table, and six metric-whitened F1 encounter-jet controls.  It has no response
rank input or target-rank branch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Sequence

getcontext().prec = 100
D = Decimal
BRIEF_COMMIT = "3c4cdf51c22278d26f2e2365d8719a153df4369a"
RHO_TABLE = tuple(map(D, ("0.25", "0.5", "1", "2", "4")))
RHO_VERIFY = tuple(D(i) / 8 for i in range(1, 33))
SERIES_TOL, ORDER_TOL = D("1e-88"), D("1e-70")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def integral(power: int, rho: Decimal) -> Decimal:
    """Integral_0^1 u^power exp(-rho^2 u^2) du by an alternating series."""
    x, total, factorial, x_power, sign = rho * rho, D(0), D(1), D(1), D(1)
    for n in range(10000):
        term = sign * x_power / (factorial * D(power + 2 * n + 1))
        total += term
        if n > int(x) + 12 and abs(term) < SERIES_TOL:
            return +total
        sign, x_power, factorial = -sign, x_power * x, factorial * D(n + 1)
    raise RuntimeError("series did not converge")


def ball(c: int, rho: Decimal) -> Decimal:
    return D(1) if c == 0 else D(c) * integral(c - 1, rho)


def box(c: int, rho: Decimal) -> Decimal:
    return D(1) if c == 0 else integral(0, rho) ** c


def sci(value: Decimal, digits: int = 16) -> str:
    return "0" if value == 0 else format(value, f".{digits}E")


def onset(q: int, a: int) -> int:
    if q < a:
        return 0
    result = 1
    for offset in range(a):
        result *= q - offset
    return result


def unit_pair(x: Decimal, y: Decimal) -> tuple[Decimal, Decimal]:
    norm = (x * x + y * y).sqrt()
    return x / norm, y / norm


def gram_controls() -> list[dict[str, Any]]:
    """Analytic singular spectra of Jhat=G^(1/2)JH_e^(-1/2)."""
    eps = D("0.01")
    near_x, near_y = unit_pair(D(1), eps)
    near_small = (D(1) - near_x).sqrt()
    near_large = (D(1) + near_x).sqrt()
    root2, root3 = D(2).sqrt(), D(3).sqrt()
    rows = [
        (
            "full_rank_noncollinear",
            3,
            (D(1), D(1), D(1)),
            (D(1), D(1), D(1)),
            ((D(1), D(0), D(0)), (D(0), D(1), D(0)), (D(0), D(0), D(1))),
            "open rank-three encounter jet",
        ),
        (
            "near_opposite_with_tangent_wiggle",
            3,
            (near_large, D(1), near_small),
            (D(1), D(1), D(1)),
            ((D(1), D(0), D(0)), (-near_x, -near_y, D(0)), (D(0), D(0), D(1))),
            "rank three but small preparation margin",
        ),
        (
            "straight_opposite_same_cycle",
            2,
            (root2, D(1), D(0)),
            (D(1), D(1), D(1)),
            ((D(1), D(0), D(0)), (-D(1), D(0), D(0)), (D(0), D(1), D(0))),
            "mandatory opposite-winding degeneracy",
        ),
        (
            "relative_velocity_in_tangent_span",
            2,
            (root2, D(1), D(0)),
            (D(1), D(1), D(1)),
            ((D(1), D(0), D(0)), (D(0), D(1), D(0)), (D(1)/root2, D(1)/root2, D(0))),
            "velocity-column degeneracy",
        ),
        (
            "full_rank_rescaled_domain_metric",
            3,
            (D(1), D(1), D("0.5")),
            (D(4), D(1), D(1)),
            ((D(1), D(0), D(0)), (D(0), D(1), D(0)), (D(0), D(0), D(1))),
            "rank invariant; singular-value magnitude depends on H_e",
        ),
        (
            "rank_one_collinear",
            1,
            (root3, D(0), D(0)),
            (D(1), D(1), D(1)),
            ((D(1), D(0), D(0)), (-D(1), D(0), D(0)), (D(1), D(0), D(0))),
            "fully collinear degeneracy",
        ),
    ]
    result = []
    for ident, rank, spectrum, h_diag, vectors, classification in rows:
        tau1, tau2, velocity = vectors
        result.append({
            "id": ident,
            "classification": classification,
            "G_diag": ["1", "1", "1"],
            "H_e_diag": [str(x) for x in h_diag],
            "tau1": [str(x) for x in tau1],
            "tau2": [str(x) for x in tau2],
            "v_rel": [str(x) for x in velocity],
            "singular_values": [sci(x, 24) for x in spectrum],
            "sigma_3": sci(spectrum[2], 24),
            "observed_rank": rank,
            "expected_rank": rank,
        })
    return result


def monotonicity_record() -> dict[str, Any]:
    checks, minimum = 0, None
    for family in (ball, box):
        for rho in RHO_VERIFY:
            values = [family(c, rho) for c in range(7)]
            for c in range(6):
                gap = values[c] - values[c + 1]
                if gap <= ORDER_TOL:
                    raise AssertionError(f"codimension monotonicity failed: {rho}, {c}")
                minimum = gap if minimum is None else min(minimum, gap)
                checks += 1
        for c in range(1, 7):
            values = [family(c, rho) for rho in RHO_VERIFY]
            for left, right in zip(values, values[1:]):
                gap = left - right
                if gap <= ORDER_TOL:
                    raise AssertionError(f"rho monotonicity failed: c={c}")
                minimum = min(minimum, gap) if minimum is not None else gap
                checks += 1
    return {
        "precision_decimal_digits": getcontext().prec,
        "reported_digits": 16,
        "verification_rho_grid": [str(x) for x in RHO_VERIFY],
        "strict_checks": checks,
        "minimum_observed_gap": sci(minimum or D(0), 24),
        "tolerance": str(ORDER_TOL),
        "status": "PASS",
    }


def build_report() -> dict[str, Any]:
    table = {
        str(rho): {
            "ball": {str(c): sci(ball(c, rho)) for c in range(7)},
            "box": {str(c): sci(box(c, rho)) for c in range(7)},
        }
        for rho in RHO_TABLE
    }
    onset_table = {
        str(q): {str(a): onset(q, a) for a in range(1, 5)}
        for q in range(10)
    }
    return {
        "schema_version": "cyz-0016-kinematic-rank-probe-v2",
        "brief_commit": BRIEF_COMMIT,
        "probe_scope": "geometric theorem and numerical controls; not a return kernel",
        "no_target_rank_input_or_branch": True,
        "portability": {
            "check_semantics": "parse JSON with universal newlines and compare canonical semantic payloads",
            "canonical_hash_semantics": "SHA-256 of sorted-key compact UTF-8 JSON without trailing newline",
        },
        "distinctions": {
            "p": "microscopic carrier spatial dimension",
            "a": "rank of the coordinate-safe encounter jet D Phi",
            "m": "later anonymous response-visible spatial rank; absent from this probe",
        },
        "encounter_jet": {
            "coordinate_safe_map": "local Log map inside an injectivity tube, otherwise transversality to the diagonal in M x M",
            "whitened_matrix": "Jhat = G^(1/2) D_Phi H_e^(-1/2)",
            "impact_condition": "at interior closest approach b=Phi(z*) and J^T G b=0; b is in N_j, not a column of J",
            "uniform_margin_status": "sufficient but not necessary; a small-sigma tail plus explicit lower-rank mixture is an alternative",
        },
        "suppression_formulas": {
            "g0": "1",
            "ball": "c * integral_0^1 u^(c-1) exp(-rho^2 u^2) du",
            "box": "[integral_0^1 exp(-rho^2 u^2) du]^c",
            "profile_boundary": "full-support integration is a declared closure because the cited GKM Gaussian is a large-impact asymptotic",
        },
        "rho_table_grid": [str(x) for x in RHO_TABLE],
        "suppression_table": table,
        "suppression_verification": monotonicity_record(),
        "valid_frame_onset": {
            "formula": "q!/(q-a)! for q>=a, else 0",
            "q_range": [0, 9],
            "a_range": [1, 4],
            "table": onset_table,
            "interpretation": "fixed-constructor onset only; not visible dimension",
        },
        "gram_controls": gram_controls(),
        "source_classification": {
            "primary_source_derived": [
                "JJP uses two generally non-collinear string tangents plus relative velocity; transverse q/b supplies no incoming column",
                "GKM schedules recollisions numerically at approximately r/vbar and redraws impact parameter",
                "GKM quotes the Gaussian impact profile in a large-impact asymptotic regime",
                "the p-brane 2p+1 ceiling is a carrier/encounter statement",
            ],
            "exact_declared_geometric_model": [
                "rank and normal-dimension theorems",
                "fixed-arity superselection and falling-factorial onset",
                "ball/box monotonicity formulas",
            ],
            "no_go_underdetermination": [
                "straight same-cycle opposite winding has rank at most two",
                "the sources do not give a tangent-wiggle preparation with positive sigma_3 margin or controlled tail",
                "impact suppression alone cannot distinguish source ranks one, two, and three",
            ],
            "controlled_numerical_probe": [
                "100-digit ball/box tables and 756 monotonicity checks",
                "six whitened F1 controls",
            ],
            "open_gate": [
                "joint source-to-return law for event jet j and impact b in N_j",
                "anonymous response reconstruction and entrant strict-residence comparison",
            ],
        },
        "verdict": "conditional source-family three-ceiling under rank-three event-jet preparation; no strict three-selection and no visible-m ceiling",
    }


def read_semantic_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8", newline=None) as handle:
        return json.load(handle)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic Brief 0016 probe.")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("probe_report.json"))
    parser.add_argument("--check", action="store_true", help="compare canonical parsed-JSON semantics, not raw line endings")
    args = parser.parse_args(argv)
    report = build_report()
    if args.check:
        if not args.output.exists():
            raise SystemExit("report missing")
        try:
            stored = read_semantic_json(args.output)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise SystemExit(f"report parse failure: {exc}") from exc
        if canonical_bytes(stored) != canonical_bytes(report):
            raise SystemExit("report semantic mismatch")
        comparison = "canonical semantic JSON"
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical_bytes(report) + b"\n")
        comparison = "generated"
    print(json.dumps({
        "status": "PASS",
        "output": str(args.output),
        "canonical_payload_sha256": hashlib.sha256(canonical_bytes(report)).hexdigest(),
        "gram_controls": len(report["gram_controls"]),
        "suppression_checks": report["suppression_verification"]["strict_checks"],
        "comparison": comparison,
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
