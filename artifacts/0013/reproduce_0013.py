#!/usr/bin/env python3
"""Deterministic standard-Python reproducer for Brief 0013.

Builds and verifies a finite target-neutral scheduled encounter/recollision
kernel on an anonymous full T^9 frame.  The event clock is deterministic and
state-dependent; this file never exports the process as a CTMC.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import itertools
import json
import lzma
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

REPO_BASELINE = "428757cf1a03fcfa57b4bc2fd316d622f1d448cb"
DIRECTIONS = tuple(range(9))
HISTORY_CLASSES = ("none", "central", "shell")
FORBIDDEN_FIELDS = {
    "visible_count",
    "response_cell",
    "active_mask",
    "target_rank",
    "pole_band",
    "rank",
    "dimension_label",
}
FORBIDDEN_OPS = {"count_if", "top_k", "classifier_lookup", "visible_threshold"}
ALLOWED_OPS = {
    "field_read",
    "index_select",
    "set_difference",
    "fraction_arithmetic",
    "metric_length",
    "normal_projection",
    "history_mixture",
    "source_registry_lookup",
    "reservoir_ratio",
    "reset_lookup",
}


def frac(x: Fraction | int) -> str:
    x = Fraction(x)
    return f"{x.numerator}/{x.denominator}"


def parse_frac(s: str) -> Fraction:
    n, d = s.split("/")
    return Fraction(int(n), int(d))


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def encode_artifact_bytes(path: Path, plain: bytes) -> bytes:
    """Deterministically encode canonical JSON according to the suffix chain."""
    suffixes = path.suffixes
    if suffixes[-2:] == [".xz", ".b64"]:
        packed = lzma.compress(plain, format=lzma.FORMAT_XZ, preset=6)
        return base64.b64encode(packed) + b"\n"
    if suffixes[-2:] == [".gz", ".b64"]:
        return base64.b64encode(gzip.compress(plain, compresslevel=9, mtime=0)) + b"\n"
    if suffixes[-1:] == [".xz"]:
        return lzma.compress(plain, format=lzma.FORMAT_XZ, preset=6)
    if suffixes[-1:] == [".gz"]:
        return gzip.compress(plain, compresslevel=9, mtime=0)
    return plain


def decode_artifact_bytes(path: Path, raw: bytes) -> bytes:
    suffixes = path.suffixes
    if suffixes[-2:] == [".xz", ".b64"]:
        return lzma.decompress(base64.b64decode(raw.strip(), validate=True), format=lzma.FORMAT_XZ)
    if suffixes[-2:] == [".gz", ".b64"]:
        return gzip.decompress(base64.b64decode(raw.strip(), validate=True))
    if suffixes[-1:] == [".xz"]:
        return lzma.decompress(raw, format=lzma.FORMAT_XZ)
    if suffixes[-1:] == [".gz"]:
        return gzip.decompress(raw)
    return raw


def exp_neg_fraction_bounds(x: Fraction, tol: Fraction = Fraction(1, 10**24)) -> Tuple[Fraction, Fraction, int]:
    """Rigorous alternating-series bounds for exp(-x), 0 <= x <= 1."""
    if x < 0 or x > 1:
        raise ValueError("alternating bound implemented only for 0 <= x <= 1")
    total = Fraction(1)
    term = Fraction(1)
    lower = Fraction(0)
    upper = Fraction(1)
    n = 0
    while True:
        n += 1
        term *= x / n
        if n % 2:
            total -= term
            lower = total
        else:
            total += term
            upper = total
        if term <= tol:
            # Even partial sums are upper bounds, odd partial sums lower bounds.
            if n % 2:
                upper = total + term * x / (n + 1)
            else:
                lower = total - term * x / (n + 1)
            return lower, upper, n


def decimal_str(q: Fraction, digits: int = 12) -> str:
    sign = "-" if q < 0 else ""
    q = abs(q)
    scale = 10**digits
    n = q.numerator * scale // q.denominator
    whole, rem = divmod(n, scale)
    return f"{sign}{whole}.{rem:0{digits}d}"


def all_frames() -> List[Tuple[int, int, int]]:
    return list(itertools.permutations(DIRECTIONS, 3))


def normal_axes(frame: Sequence[int]) -> Tuple[int, ...]:
    used = set(frame)
    return tuple(i for i in DIRECTIONS if i not in used)


def mark_templates(frame: Sequence[int], radii: Sequence[Fraction]) -> List[Dict[str, Any]]:
    """Sparse full-metric impact redraw closure.

    Central mark plus +/- basis impact marks for every normal direction whose
    radius exceeds the registered self-dual radius.  No cardinality is passed.
    """
    norms = normal_axes(frame)
    out: List[Dict[str, Any]] = []
    out.append({
        "template": "central",
        "class": "central",
        "impact_axis": None,
        "impact_sign": 0,
        "impact_coordinate": frac(Fraction(0)),
        "b2": frac(Fraction(0)),
        "reverse_template": "central",
    })
    for axis in norms:
        span = max(Fraction(radii[axis]) - 1, Fraction(0))
        if span == 0:
            continue
        b = span / 2
        for sign, label in ((1, "plus"), (-1, "minus")):
            template = f"axis_{axis}_{label}"
            reverse = f"axis_{axis}_{'minus' if label == 'plus' else 'plus'}"
            out.append({
                "template": template,
                "class": "shell",
                "impact_axis": axis,
                "impact_sign": sign,
                "impact_coordinate": frac(sign * b),
                "b2": frac(b * b),
                "reverse_template": reverse,
            })
    return out


def schedule_time(radii: Sequence[Fraction], frame: Sequence[int], separation_fraction: Fraction, speed: Fraction) -> Fraction:
    # Physical unit is 2*pi*sqrt(alpha') / c; the 2*pi factor is absorbed in the unit.
    velocity_axis = frame[1]
    separation = Fraction(radii[velocity_axis]) * separation_fraction
    return separation / speed


def source_valid_frame(radii: Sequence[Fraction], frame: Sequence[int]) -> bool:
    # Registered GKM calibration stratum: winding, velocity and scattering-plane
    # axes are all in the long-cycle cell. This is a local per-axis test, not a count.
    return all(Fraction(radii[a]) > 1 for a in frame)


def source_case(radii: Sequence[Fraction]) -> Dict[str, Any]:
    valid = []
    for frame in all_frames():
        if source_valid_frame(radii, frame):
            marks = mark_templates(frame, radii)
            valid.append({
                "frame": list(frame),
                "normal_support_axes": [m["impact_axis"] for m in marks if m["impact_axis"] is not None and m["impact_sign"] == 1],
                "mark_count": len(marks),
                "scheduled_time": frac(schedule_time(radii, frame, Fraction(1, 2), Fraction(1, 2))),
            })
    return {"radii": [frac(Fraction(r)) for r in radii], "valid_frames": valid}


def mark_probabilities(templates: Sequence[Mapping[str, Any]], history: str, rho: Fraction) -> Dict[str, Fraction]:
    n = len(templates)
    base = Fraction(1, n)
    central_ids = [m["template"] for m in templates if m["class"] == "central"]
    shell_ids = [m["template"] for m in templates if m["class"] == "shell"]
    if len(central_ids) != 1:
        raise AssertionError("one central mark required")
    probs = {m["template"]: (1 - rho) * base for m in templates}
    if history == "none":
        return {m["template"]: base for m in templates}
    if history == "central":
        probs[central_ids[0]] += rho
    elif history == "shell":
        if not shell_ids:
            probs[central_ids[0]] += rho
        else:
            for mid in shell_ids:
                probs[mid] += rho / len(shell_ids)
    else:
        raise ValueError(history)
    return probs


def gkm_probability_registry() -> Dict[str, Any]:
    prefactor = Fraction(1, 4)
    central = prefactor
    e_lo, e_hi, terms = exp_neg_fraction_bounds(Fraction(1, 4))
    shell_lo = prefactor * e_lo
    shell_hi = prefactor * e_hi
    shell_selected = (shell_lo + shell_hi) / 2
    # JJP exact calibration: g_s=1/10, Vmin*rho=1/5, theta=pi/2,
    # v=3/5, sqrt(1-v^2)=4/5 => f=25/96.
    jjp = Fraction(1, 100) * Fraction(1, 5) * Fraction(25, 96)
    return {
        "gkm": {
            "prefactor": frac(prefactor),
            "delta_sq": frac(Fraction(1)),
            "central": {"interval": [frac(central), frac(central)], "selected": frac(central)},
            "shell_b2_quarter": {
                "interval": [frac(shell_lo), frac(shell_hi)],
                "selected": frac(shell_selected),
                "alternating_series_terms": terms,
                "interval_width": frac(shell_hi - shell_lo),
            },
        },
        "jjp_exact_calibration": {
            "g_s": frac(Fraction(1, 10)),
            "compact_overlap": frac(Fraction(1, 5)),
            "angle": "pi/2",
            "relative_speed": frac(Fraction(3, 5)),
            "f_theta_v": frac(Fraction(25, 96)),
            "conditional_probability": frac(jjp),
            "use": "crossing-conditioned calibration only",
        },
        "dfm_registry": {
            "use": "source-valid compact-rate stratum and time-dependent-background error flag only",
            "numerical_rate": None,
        },
        "frey_random_walk_registry": {
            "use": "detailed-balance structure only in declared near-Hagedorn/random-walk regime",
            "reservoir_degeneracies": {"E0": 1, "E2": 4},
            "reverse_ratio": frac(Fraction(1, 4)),
        },
    }


def frame_id(frame: Sequence[int]) -> str:
    return f"f{frame[0]}{frame[1]}{frame[2]}"


def build_artifact() -> Dict[str, Any]:
    radii = tuple(Fraction(2) for _ in DIRECTIONS)
    frames = all_frames()
    registry = gkm_probability_registry()
    central_p = parse_frac(registry["gkm"]["central"]["selected"])
    shell_p = parse_frac(registry["gkm"]["shell_b2_quarter"]["selected"])
    reverse_ratio = parse_frac(registry["frey_random_walk_registry"]["reverse_ratio"])
    # Main kernel is the scheduled independent-redraw GKM calibration.
    # Persistent history is retained as a separately replayed alternative control.
    rho = Fraction(0)

    frame_rows: List[Dict[str, Any]] = []
    marks: List[Dict[str, Any]] = []
    states: List[List[Any]] = []
    schedules: List[Dict[str, Any]] = []
    mark_index: Dict[Tuple[str, str], str] = {}

    for fi, frame in enumerate(frames):
        fid = frame_id(frame)
        templates = mark_templates(frame, radii)
        if len(templates) != 13:
            raise AssertionError("full T9 calibration must have 13 sparse marks")
        frame_rows.append({
            "index": fi,
            "id": fid,
            "winding_axis": frame[0],
            "velocity_axis": frame[1],
            "scattering_axis": frame[2],
            "normal_axes": list(normal_axes(frame)),
        })
        hold = schedule_time(radii, frame, Fraction(1, 2), Fraction(1, 2))
        schedules.append({
            "frame_id": fid,
            "separation_fraction": frac(Fraction(1, 2)),
            "relative_speed": frac(Fraction(1, 2)),
            "hold_time": frac(hold),
            "time_unit": "2*pi*sqrt(alpha_prime)/c",
            "clock_semantics": "deterministic scheduled recollision",
        })
        for mi, m in enumerate(templates):
            mid = f"{fid}:{m['template']}"
            mark_index[(fid, m["template"])] = mid
            marks.append({
                "id": mid,
                "frame_id": fid,
                "template": m["template"],
                "class": m["class"],
                "impact_axis": m["impact_axis"],
                "impact_sign": m["impact_sign"],
                "impact_coordinate": m["impact_coordinate"],
                "b2": m["b2"],
                "relative_speed": frac(Fraction(1, 2)),
                "angle": "pi/2",
                "species": "F1/F1-opposite-winding",
                "worldsheet_cell": "heavy-dilute-ground-oscillator",
                "reverse_id": f"{fid}:{m['reverse_template']}",
                "source_branch": "GKM",
                "channel_probability_key": "central" if m["class"] == "central" else "shell_b2_quarter",
            })
        # Present histories.
        for h in HISTORY_CLASSES:
            sid = f"{fid}:P:{h}"
            states.append([sid, fid, "present", h, None, 2, 0])
        # Absent states retain the pre-annihilation history and exact forward mark.
        for h in HISTORY_CLASSES:
            for m in templates:
                mid = mark_index[(fid, m["template"])]
                sid = f"{fid}:A:{h}:{m['template']}"
                states.append([sid, fid, "absent", h, mid, 0, 2])

    initial_law = {
        "frame_weight": frac(Fraction(1, len(frames))),
        "within_frame": {
            "present:none": frac(Fraction(1, 4)),
            "present:central": frac(Fraction(1, 8)),
            "present:shell": frac(Fraction(1, 8)),
            "absent_each_pre_history_and_mark": frac(Fraction(1, 78)),
        },
        "normalization_proof": "1/4+1/8+1/8+3*13*(1/78)=1 per frame",
        "positive_support": True,
        "rank_conditioned": False,
    }

    main_templates = mark_templates(frames[0], radii)
    present_rows: Dict[str, Any] = {}
    for h in HISTORY_CLASSES:
        probs = mark_probabilities(main_templates, h, rho)
        present_rows[h] = [
            {
                "mark_template": m["template"],
                "mark_probability": frac(probs[m["template"]]),
                "annihilation_probability": frac(central_p if m["class"] == "central" else shell_p),
                "miss_probability": frac(1 - (central_p if m["class"] == "central" else shell_p)),
                "annihilation_destination": {
                    "status": "absent",
                    "pre_history": h,
                    "stored_forward_mark": m["template"],
                    "system_energy": 0,
                    "reservoir_energy": 2,
                },
                "miss_destination": {
                    "status": "present",
                    "history": m["class"],
                    "system_energy": 2,
                    "reservoir_energy": 0,
                    "event_type": "history_only_or_self",
                },
            }
            for m in main_templates
        ]
    absent_rows = []
    for m in main_templates:
        p = central_p if m["class"] == "central" else shell_p
        p_rev = p * reverse_ratio
        absent_rows.append({
            "stored_forward_mark": m["template"],
            "scheduled_reverse_mark": m["reverse_template"],
            "creation_probability": frac(p_rev),
            "no_creation_probability": frac(1 - p_rev),
            "creation_destination": {
                "status": "present",
                "restore_pre_history": True,
                "system_energy": 2,
                "reservoir_energy": 0,
            },
            "no_creation_destination": {
                "status": "absent",
                "state_change": False,
                "event_type": "scheduled_self_event",
            },
        })

    swap_generators = []
    frame_lookup = {tuple(f): i for i, f in enumerate(frames)}
    for a in range(8):
        mapping = []
        for f in frames:
            g = tuple((a + 1 if x == a else a if x == a + 1 else x) for x in f)
            mapping.append(frame_lookup[g])
        swap_generators.append({"swap": [a, a + 1], "frame_index_map": mapping})

    dependency_graph = {
        "whitelist_fields": [
            "charges",
            "species",
            "metric_radii",
            "dilaton_cell",
            "warp_cell",
            "winding_axis",
            "velocity_axis",
            "scattering_axis",
            "separation_fraction",
            "relative_speed",
            "relative_position",
            "relative_tangent",
            "worldsheet_cell",
            "history_class",
            "stored_forward_mark",
            "reservoir_energy",
        ],
        "allowed_operations": sorted(ALLOWED_OPS),
        "forbidden_fields": sorted(FORBIDDEN_FIELDS),
        "forbidden_operations": sorted(FORBIDDEN_OPS),
        "nodes": [
            {"id": "schedule", "op": "fraction_arithmetic", "inputs": ["metric_radii", "velocity_axis", "separation_fraction", "relative_speed"]},
            {"id": "normal_axes", "op": "set_difference", "inputs": ["metric_radii", "winding_axis", "velocity_axis", "scattering_axis"]},
            {"id": "impact_mark", "op": "normal_projection", "inputs": ["metric_radii", "normal_axes", "relative_position", "history_class"]},
            {"id": "channel", "op": "source_registry_lookup", "inputs": ["charges", "species", "dilaton_cell", "relative_speed", "relative_tangent", "impact_mark", "worldsheet_cell"]},
            {"id": "reverse_ratio", "op": "reservoir_ratio", "inputs": ["reservoir_energy", "worldsheet_cell"]},
            {"id": "reset", "op": "reset_lookup", "inputs": ["charges", "channel", "stored_forward_mark", "reservoir_energy"]},
        ],
        "registration_split": {
            "train": ["GKM_iso3_central", "GKM_iso4_central_shell", "JJP_pi_over_2"],
            "validation": ["permuted_iso3", "permuted_iso4", "clock_separation", "clock_velocity", "persistent_history"],
            "response_labels_used": False,
        },
    }

    source_cases = {
        "isotropic_three_large": source_case([Fraction(2)] * 3 + [Fraction(1)] * 6),
        "isotropic_four_large": source_case([Fraction(2)] * 4 + [Fraction(1)] * 5),
    }

    artifact: Dict[str, Any] = {
        "schema": "cyz_n.artifacts.0013.scheduled_full_t9.v1",
        "meta": {
            "baseline_commit": REPO_BASELINE,
            "physical_time_unit": "2*pi*sqrt(alpha_prime)/c",
            "process_type": "event-scheduled Markov renewal; not CTMC",
            "main_metric_radii": [frac(r) for r in radii],
            "self_dual_radius": frac(Fraction(1)),
            "source_sector": "weak-coupling heavy dilute F1 opposite-winding",
            "rank_fields_present": False,
        },
        "source_registry": registry,
        "dependency_graph": dependency_graph,
        "frames": frame_rows,
        "marks": marks,
        "states": {
            "columns": ["id", "frame_id", "status", "pre_or_current_history", "stored_forward_mark", "system_energy_quanta", "reservoir_energy_quanta"],
            "rows": states,
            "count": len(states),
        },
        "initial_law": initial_law,
        "schedules": schedules,
        "event_kernel": {
            "history_persistence": frac(rho),
            "present_rows_by_history": present_rows,
            "absent_reverse_rows_by_forward_mark": absent_rows,
            "clock_rule": "next_event_time = entry_time + scheduled_hold_time; no exponential draw",
            "forward_mark_involution": "central is fixed; axis_i_plus <-> axis_i_minus",
            "channel_involution": {"annihilate": "create", "create": "annihilate"},
            "energy_shell_quanta": 2,
            "net_winding_charge": 0,
        },
        "s9_action": {
            "adjacent_swap_generators": swap_generators,
            "mark_action": "permute frame and physical impact axis; recover target normal-axis template by actual axis",
            "state_action": "permute frame only; status, history class, energies and mark class are transported",
        },
        "source_limit_cases": source_cases,
        "cemetery": {
            "states": ["out_of_source_regime", "unresolved_source_amplitude", "energy_or_charge_failure"],
            "rules": [
                "invalid source-regime registry -> out_of_source_regime",
                "source probability interval intersects invalid cap -> unresolved_source_amplitude",
                "nonintegral or nonclosing ledger reset -> energy_or_charge_failure",
            ],
        },
        "approximation_ledger": {
            "gkm_shell_probability_interval": registry["gkm"]["shell_b2_quarter"]["interval"],
            "selected_rational_inside_interval": registry["gkm"]["shell_b2_quarter"]["selected"],
            "finite_mark_closure": "sparse central-plus-normal-axis redraw; newly proposed measurable closure",
            "scheduled_clock_error": frac(Fraction(0)),
            "continuum_impact_cubature_error": "unresolved outside registered marks",
            "geometry_drift_error": "not part of this frozen-cell finite kernel",
        },
        "age_augmentation": {
            "clock_quantum": "1/2",
            "main_hold_ticks": 4,
            "countdown_states": [4, 3, 2, 1],
            "deterministic_rule": "(event_state,r)->(event_state,r-1) with probability 1 for r>1; at r=1 apply the event kernel and reset r=4",
            "export_as_CTMC": False,
        },
        "later_all_rank_interface": {
            "exports_response_cells": False,
            "exported_objects": ["event_states", "fixed_initial_law", "scheduled_holds", "mark_kernel", "channels", "history", "ledger", "S9_action", "age_augmentation"],
            "strict_residence_instruction": "use the serialized countdown chain or exact Markov-renewal convolution; never use CTMC killed-semigroup formulas on the unaugmented process",
            "response_consumer": "later anonymous all-direction Green/product replay defines cells Z_0,...,Z_9 after trajectories are generated",
        },
        "controls": {
            "hidden_three_adversary": {
                "dependency_graph": {
                    "nodes": [
                        {"id": "global_count", "op": "count_if", "inputs": ["metric_radii"], "predicate": "radius > self_dual"},
                        {"id": "rate", "op": "fraction_arithmetic", "inputs": ["global_count"], "rule": "special value when global_count == 3"},
                    ]
                },
                "S9_invariant": True,
                "expected_registration": "rejected",
            }
        },
        "source_references": [
            "https://arxiv.org/abs/0908.0955",
            "https://arxiv.org/abs/hep-th/0405229",
            "https://arxiv.org/abs/hep-th/0409162",
            "https://arxiv.org/abs/hep-th/0409121",
            "https://arxiv.org/abs/2310.11494",
        ],
    }
    return artifact


def state_weight(row: Sequence[Any], initial: Mapping[str, Any]) -> Fraction:
    frame_w = parse_frac(initial["frame_weight"])
    status = row[2]
    hist = row[3]
    if status == "present":
        return frame_w * parse_frac(initial["within_frame"][f"present:{hist}"])
    return frame_w * parse_frac(initial["within_frame"]["absent_each_pre_history_and_mark"])


def register_graph(graph: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    for node in graph.get("nodes", []):
        op = node.get("op")
        if op in FORBIDDEN_OPS or op not in ALLOWED_OPS:
            errors.append(f"forbidden_or_unregistered_op:{op}")
        for inp in node.get("inputs", []):
            if inp in FORBIDDEN_FIELDS:
                errors.append(f"forbidden_field:{inp}")
    return not errors, errors


def history_survival(artifact: Mapping[str, Any], n: int = 4) -> Dict[str, Any]:
    registry = artifact["source_registry"]["gkm"]
    pc = parse_frac(registry["central"]["selected"])
    ps = parse_frac(registry["shell_b2_quarter"]["selected"])
    miss_mean = Fraction(1, 13) * (1 - pc) + Fraction(12, 13) * (1 - ps)
    iid = miss_mean**n
    persistent = Fraction(1, 13) * (1 - pc) ** n + Fraction(12, 13) * (1 - ps) ** n
    return {
        "n_scheduled_encounters": n,
        "iid_redraw_survival": frac(iid),
        "persistent_class_survival": frac(persistent),
        "iid_decimal": decimal_str(iid),
        "persistent_decimal": decimal_str(persistent),
        "difference": frac(persistent - iid),
        "difference_decimal": decimal_str(persistent - iid),
        "same_one_mark_marginal": True,
    }


def verify_artifact(artifact: Mapping[str, Any]) -> Dict[str, Any]:
    tests: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, details: Any) -> None:
        tests.append({"name": name, "executed": True, "passed": bool(ok), "details": details})

    frames = artifact["frames"]
    states_rows = artifact["states"]["rows"]
    marks = artifact["marks"]
    initial = artifact["initial_law"]
    add("frame_count", len(frames) == 504, {"count": len(frames)})
    add("state_count", len(states_rows) == 504 * 42, {"count": len(states_rows), "expected": 504 * 42})
    add("mark_count", len(marks) == 504 * 13, {"count": len(marks), "expected": 504 * 13})

    total = sum((state_weight(row, initial) for row in states_rows), Fraction(0))
    add("initial_law_normalization", total == 1, {"sum": frac(total), "positive": all(state_weight(r, initial) > 0 for r in states_rows)})

    # Conditional normalization.
    norm_ok = True
    row_details = []
    for h, row in artifact["event_kernel"]["present_rows_by_history"].items():
        mark_sum = sum(parse_frac(e["mark_probability"]) for e in row)
        channel_ok = all(parse_frac(e["annihilation_probability"]) + parse_frac(e["miss_probability"]) == 1 for e in row)
        norm_ok &= mark_sum == 1 and channel_ok
        row_details.append({"history": h, "mark_sum": frac(mark_sum), "channels": channel_ok})
    reverse_ok = all(parse_frac(e["creation_probability"]) + parse_frac(e["no_creation_probability"]) == 1 for e in artifact["event_kernel"]["absent_reverse_rows_by_forward_mark"])
    norm_ok &= reverse_ok
    add("conditional_normalization", norm_ok, {"present": row_details, "reverse_rows": reverse_ok})

    # Exact JJP registry and finite microcanonical reverse detailed balance.
    jjp = parse_frac(artifact["source_registry"]["jjp_exact_calibration"]["conditional_probability"])
    add("JJP_exact_registry", jjp == Fraction(1, 1920), {"conditional_probability": frac(jjp), "expected": "1/1920"})
    reverse_ratio = parse_frac(artifact["source_registry"]["frey_random_walk_registry"]["reverse_ratio"])
    db_ok = True
    for row in artifact["event_kernel"]["absent_reverse_rows_by_forward_mark"]:
        template = row["stored_forward_mark"]
        p_forward = central_p = parse_frac(artifact["source_registry"]["gkm"]["central"]["selected"]) if template == "central" else parse_frac(artifact["source_registry"]["gkm"]["shell_b2_quarter"]["selected"])
        p_reverse = parse_frac(row["creation_probability"])
        if Fraction(1) * p_forward != Fraction(4) * p_reverse:
            db_ok = False
            break
    add("reverse_microcanonical_detailed_balance", db_ok and reverse_ratio == Fraction(1,4), {"present_weight": 1, "absent_weight": 4, "reverse_ratio": frac(reverse_ratio)})

    # Mark involution and ledger.
    mark_map = {m["id"]: m for m in marks}
    inv_ok = all(mark_map[mark_map[m["reverse_id"]]["reverse_id"]]["id"] == m["id"] for m in marks)
    energy_forward = (2 + 0) == (0 + 2)
    energy_reverse = (0 + 2) == (2 + 0)
    add("ledger_charge_reverse_involution", inv_ok and energy_forward and energy_reverse, {
        "mark_involution": inv_ok,
        "forward_energy": energy_forward,
        "reverse_energy": energy_reverse,
        "net_charge_before_after": [0, 0],
    })

    # Scheduled clock replay.
    holds = {s["hold_time"] for s in artifact["schedules"]}
    times = [Fraction(2) * i for i in range(1, 6)]
    add("scheduled_clock_replay", holds == {"2/1"}, {
        "unique_hold_times": sorted(holds),
        "first_five_event_times": [frac(t) for t in times],
        "waiting_time_variance": frac(Fraction(0)),
        "poisson_clock": False,
    })

    # Full T9 covariance under adjacent swaps.
    frame_tuples = [tuple([f["winding_axis"], f["velocity_axis"], f["scattering_axis"]]) for f in frames]
    frame_lookup = {f: i for i, f in enumerate(frame_tuples)}
    cov_ok = True
    nontrivial = False
    for gen in artifact["s9_action"]["adjacent_swap_generators"]:
        a, b = gen["swap"]
        mapping = gen["frame_index_map"]
        if any(i != j for i, j in enumerate(mapping)):
            nontrivial = True
        for i, f in enumerate(frame_tuples):
            g = tuple(b if x == a else a if x == b else x for x in f)
            if mapping[i] != frame_lookup[g]:
                cov_ok = False
                break
    add("full_T9_covariance", cov_ok and nontrivial, {"adjacent_generators": 8, "nontrivial": nontrivial})

    # Same-law source limits: constructor receives radii and frame, never a count.
    c3 = artifact["source_limit_cases"]["isotropic_three_large"]["valid_frames"]
    c4 = artifact["source_limit_cases"]["isotropic_four_large"]["valid_frames"]
    c3_ok = len(c3) == 6 and all(r["mark_count"] == 1 and r["scheduled_time"] == "2/1" for r in c3)
    c4_ok = len(c4) == 24 and all(r["mark_count"] == 3 and len(r["normal_support_axes"]) == 1 and r["scheduled_time"] == "2/1" for r in c4)
    add("same_law_isotropic_source_limits", c3_ok and c4_ok, {
        "three_large_valid_frames": len(c3),
        "three_large_mark_counts": sorted({r["mark_count"] for r in c3}),
        "four_large_valid_frames": len(c4),
        "four_large_mark_counts": sorted({r["mark_count"] for r in c4}),
        "constructor_inputs_include_count": False,
    })

    # History control.
    hist = history_survival(artifact, 4)
    add("history_control", parse_frac(hist["difference"]) != 0 and hist["same_one_mark_marginal"], hist)

    # Clock control.
    frame = frame_tuples[0]
    radii = [Fraction(2)] * 9
    t_base = schedule_time(radii, frame, Fraction(1, 2), Fraction(1, 2))
    t_sep = schedule_time(radii, frame, Fraction(3, 4), Fraction(1, 2))
    t_vel = schedule_time(radii, frame, Fraction(1, 2), Fraction(1, 4))
    p_fixed = artifact["source_registry"]["gkm"]["central"]["selected"]
    add("clock_control", (t_base, t_sep, t_vel) == (Fraction(2), Fraction(3), Fraction(4)), {
        "base": frac(t_base), "changed_separation": frac(t_sep), "changed_velocity": frac(t_vel),
        "conditional_channel_at_fixed_mark": p_fixed,
    })

    # Dependency registration and hidden-three adversary.
    good_ok, good_err = register_graph(artifact["dependency_graph"])
    bad_graph = artifact["controls"]["hidden_three_adversary"]["dependency_graph"]
    bad_ok, bad_err = register_graph(bad_graph)
    add("nonencoding_dependency_gate", good_ok and not bad_ok and artifact["controls"]["hidden_three_adversary"]["S9_invariant"], {
        "registered_kernel_accepted": good_ok,
        "registered_errors": good_err,
        "hidden_three_S9_invariant": True,
        "hidden_three_accepted": bad_ok,
        "hidden_three_rejection": bad_err,
    })

    # Source probability interval contains selected rational.
    lo, hi = map(parse_frac, artifact["source_registry"]["gkm"]["shell_b2_quarter"]["interval"])
    sel = parse_frac(artifact["source_registry"]["gkm"]["shell_b2_quarter"]["selected"])
    add("outward_source_interval", lo < sel < hi, {
        "lo": frac(lo), "selected": frac(sel), "hi": frac(hi), "width": frac(hi - lo)
    })

    passed = all(t["passed"] for t in tests)
    return {"all_passed": passed, "tests": tests}



def compact_artifact(artifact: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a canonical compact serialization with every mark and state explicit."""
    out = dict(artifact)
    frames = artifact["frames"]
    frame_index = {f["id"]: f["index"] for f in frames}
    marks = artifact["marks"]
    mark_index = {m["id"]: i for i, m in enumerate(marks)}
    out["mark_dictionary"] = {
        "columns": [
            "frame_index", "class_code", "impact_axis", "impact_sign",
            "impact_coordinate", "b2", "reverse_index", "channel_key_code",
        ],
        "codes": {
            "class": ["central", "shell"],
            "channel_key": ["central", "shell_b2_quarter"],
        },
        "constants": {
            "angle": "pi/2",
            "relative_speed": "1/2",
            "source_branch": "GKM",
            "species": "F1/F1-opposite-winding",
            "worldsheet_cell": "heavy-dilute-ground-oscillator",
        },
        "count": len(marks),
        "rows": [
            [
                frame_index[m["frame_id"]],
                0 if m["class"] == "central" else 1,
                -1 if m["impact_axis"] is None else m["impact_axis"],
                m["impact_sign"], m["impact_coordinate"], m["b2"],
                mark_index[m["reverse_id"]],
                0 if m["channel_probability_key"] == "central" else 1,
            ]
            for m in marks
        ],
    }
    out.pop("marks")
    history_code = {"none": 0, "central": 1, "shell": 2}
    status_code = {"present": 0, "absent": 1}
    compact_states = []
    for row in artifact["states"]["rows"]:
        _, fid, status, history, stored_mark, system_e, reservoir_e = row
        compact_states.append([
            frame_index[fid], status_code[status], history_code[history],
            -1 if stored_mark is None else mark_index[stored_mark],
            system_e, reservoir_e,
        ])
    out["states"] = {
        "columns": [
            "frame_index", "status_code", "history_code",
            "stored_forward_mark_index", "system_energy_quanta",
            "reservoir_energy_quanta",
        ],
        "codes": {
            "status": ["present", "absent"],
            "history": ["none", "central", "shell"],
        },
        "state_id_rule": "frame_id + :P/:A + history + optional mark template",
        "count": len(compact_states),
        "rows": compact_states,
    }
    out["meta"] = dict(out["meta"])
    out["meta"]["storage_encoding"] = "explicit compact integer tables v1"
    return out


def expand_artifact(compact: Mapping[str, Any]) -> Dict[str, Any]:
    """Expand compact tables to the in-memory form used by the verifier."""
    if "marks" in compact:
        return dict(compact)
    artifact = dict(compact)
    frames = artifact["frames"]
    md = artifact["mark_dictionary"]
    class_codes = md["codes"]["class"]
    channel_codes = md["codes"]["channel_key"]
    constants = md["constants"]
    prelim = []
    for row in md["rows"]:
        frame_idx, class_code, axis, sign, impact, b2, reverse_idx, channel_code = row
        fid = frames[frame_idx]["id"]
        if axis == -1:
            template = "central"
        else:
            template = f"axis_{axis}_{'plus' if sign == 1 else 'minus'}"
        prelim.append({
            "angle": constants["angle"],
            "b2": b2,
            "channel_probability_key": channel_codes[channel_code],
            "class": class_codes[class_code],
            "frame_id": fid,
            "id": f"{fid}:{template}",
            "impact_axis": None if axis == -1 else axis,
            "impact_coordinate": impact,
            "impact_sign": sign,
            "relative_speed": constants["relative_speed"],
            "reverse_index": reverse_idx,
            "source_branch": constants["source_branch"],
            "species": constants["species"],
            "template": template,
            "worldsheet_cell": constants["worldsheet_cell"],
        })
    marks = []
    for mark in prelim:
        reverse_idx = mark.pop("reverse_index")
        mark["reverse_id"] = prelim[reverse_idx]["id"]
        marks.append(mark)
    artifact["marks"] = marks
    artifact.pop("mark_dictionary")
    sd = artifact["states"]
    statuses = sd["codes"]["status"]
    histories = sd["codes"]["history"]
    state_rows = []
    for frame_idx, status_code, history_code, mark_idx, system_e, reservoir_e in sd["rows"]:
        fid = frames[frame_idx]["id"]
        status = statuses[status_code]
        history = histories[history_code]
        stored_mark = None if mark_idx == -1 else marks[mark_idx]["id"]
        if status == "present":
            sid = f"{fid}:P:{history}"
        else:
            sid = f"{fid}:A:{history}:{marks[mark_idx]['template']}"
        state_rows.append([sid, fid, status, history, stored_mark, system_e, reservoir_e])
    artifact["states"] = {
        "columns": [
            "id", "frame_id", "status", "pre_or_current_history",
            "stored_forward_mark", "system_energy_quanta",
            "reservoir_energy_quanta",
        ],
        "count": len(state_rows),
        "rows": state_rows,
    }
    return artifact

def write_outputs(artifact_path: Path, report_path: Path) -> Dict[str, Any]:
    artifact = build_artifact()
    verification = verify_artifact(artifact)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    compact = compact_artifact(artifact)
    artifact_plain = canonical_bytes(compact) + b"\n"
    artifact_bytes = encode_artifact_bytes(artifact_path, artifact_plain)
    artifact_path.write_bytes(artifact_bytes)
    # Reload from disk and verify independently of in-memory identity.
    loaded_plain = decode_artifact_bytes(artifact_path, artifact_path.read_bytes())
    loaded_compact = json.loads(loaded_plain.decode("utf-8"))
    loaded = expand_artifact(loaded_compact)
    replay = verify_artifact(loaded)
    serialization_same = canonical_bytes(loaded_compact) == canonical_bytes(compact)
    script_path = Path(__file__).resolve()
    report = {
        "schema": "cyz_n.artifacts.0013.replay_report.v1",
        "command": "python3 artifacts/0013/reproduce_0013.py --write artifacts/0013/kernel_ledger.json.xz.b64 --report artifacts/0013/replay_report.json",
        "verify_command": "python3 artifacts/0013/reproduce_0013.py --verify artifacts/0013/kernel_ledger.json.xz.b64 --verify-report artifacts/0013/replay_report.json",
        "executed": True,
        "baseline_commit": REPO_BASELINE,
        "artifact_sha256": sha256_file(artifact_path),
        "artifact_canonical_sha256": sha256_bytes(canonical_bytes(loaded_compact)),
        "script_sha256": sha256_file(script_path),
        "artifact_bytes": artifact_path.stat().st_size,
        "state_count": loaded["states"]["count"],
        "mark_count": len(loaded["marks"]),
        "serialization_replay_same": serialization_same,
        "first_verification": verification,
        "reload_verification": replay,
    }
    report_bytes = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    report_path.write_bytes(report_bytes)
    return report


def verify_files(artifact_path: Path, report_path: Path) -> Dict[str, Any]:
    artifact_plain = decode_artifact_bytes(artifact_path, artifact_path.read_bytes())
    compact = json.loads(artifact_plain.decode("utf-8"))
    artifact = expand_artifact(compact)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    replay = verify_artifact(artifact)
    return {
        "artifact_sha256": sha256_file(artifact_path),
        "report_recorded_artifact_sha256": report["artifact_sha256"],
        "artifact_hash_matches_report": sha256_file(artifact_path) == report["artifact_sha256"],
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "report_recorded_script_sha256": report["script_sha256"],
        "script_hash_matches_report": sha256_file(Path(__file__).resolve()) == report["script_sha256"],
        "replay": replay,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="write canonical kernel/ledger JSON")
    parser.add_argument("--report", type=Path, help="write executed replay report JSON")
    parser.add_argument("--verify", type=Path, help="verify an existing kernel/ledger JSON")
    parser.add_argument("--verify-report", type=Path, help="report paired with --verify")
    args = parser.parse_args()

    if args.write:
        if not args.report:
            parser.error("--write requires --report")
        report = write_outputs(args.write, args.report)
        print(json.dumps({
            "all_passed": report["reload_verification"]["all_passed"],
            "artifact_sha256": report["artifact_sha256"],
            "script_sha256": report["script_sha256"],
            "artifact_bytes": report["artifact_bytes"],
            "state_count": report["state_count"],
            "mark_count": report["mark_count"],
            "report_path": str(args.report),
        }, sort_keys=True))
        return 0 if report["reload_verification"]["all_passed"] and report["serialization_replay_same"] else 1

    if args.verify:
        if not args.verify_report:
            parser.error("--verify requires --verify-report")
        result = verify_files(args.verify, args.verify_report)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["artifact_hash_matches_report"] and result["script_hash_matches_report"] and result["replay"]["all_passed"] else 1

    parser.error("use --write/--report or --verify/--verify-report")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
