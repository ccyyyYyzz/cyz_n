#!/usr/bin/env python3
"""Plain standard-Python constructor interpreter for Brief 0015.

This module reads a complete JSON constructor specification and a separate
control-vector manifest.  It emits a compact canonical artifact containing
input vectors, exact expansion hashes, counts, and hashes of every executable
dependency.  It does not export a CTMC and never receives a response rank.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

SCHEMA_VERSION = "cyz-0015-kernel-artifact-v1"
GENERATOR_API_VERSION = "cyz-0015-generator-v1"


class ConstructionError(RuntimeError):
    pass


def parse_fraction(value: str | int | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str) or "/" not in value:
        raise ConstructionError(f"invalid exact fraction: {value!r}")
    n, d = value.split("/", 1)
    q = Fraction(int(n), int(d))
    if q.denominator <= 0:
        raise ConstructionError(f"invalid denominator: {value}")
    return q


def fraction_text(value: Fraction | int) -> str:
    q = Fraction(value)
    return f"{q.numerator}/{q.denominator}"


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def normalized_lf_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def normalized_lf_sha256(path: Path) -> str:
    return hashlib.sha256(normalized_lf_bytes(path)).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_canonical_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(obj) + b"\n")


class SpecReader:
    def __init__(self, obj: Mapping[str, Any]):
        self.obj = obj
        self.used: set[str] = set()

    def get(self, path: str) -> Any:
        cur: Any = self.obj
        for part in path.split("."):
            if not isinstance(cur, Mapping) or part not in cur:
                raise ConstructionError(f"missing specification path: {path}")
            cur = cur[part]
        self.used.add(path)
        return cur


def consume_required_spec_paths(reader: SpecReader) -> None:
    required = reader.get("must_consume")
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        raise ConstructionError("must_consume must be a list of paths")
    for path in required:
        reader.get(path)


def validate_constructor_spec(spec: Mapping[str, Any]) -> SpecReader:
    reader = SpecReader(spec)
    consume_required_spec_paths(reader)
    if reader.get("process_type") != "scheduled_markov_renewal":
        raise ConstructionError("process_type must be scheduled_markov_renewal")
    if reader.get("ctmc_export") != "forbidden":
        raise ConstructionError("CTMC export must be forbidden")
    directions = reader.get("direction_set")
    if directions != list(range(9)):
        raise ConstructionError("direction_set must be the exact anonymous nine-direction set")
    if reader.get("frame_prior.enumeration") != "ordered_distinct_roles":
        raise ConstructionError("unsupported frame enumeration")
    program = reader.get("constructor_program")
    schemas = reader.get("operation_schemas")
    if not isinstance(program, list) or not isinstance(schemas, Mapping):
        raise ConstructionError("constructor program/schema missing")
    seen = set()
    allowed_stage_ops = {
        "enumerate_ordered_distinct_frames",
        "construct_frame_local_marks",
        "evaluate_source_validity",
        "construct_physical_and_killed_states",
        "construct_deterministic_schedules",
        "construct_complete_event_rows",
        "construct_exchangeable_initial_law",
        "construct_adjacent_s9_actions",
    }
    for node in program:
        if set(node) != {"id", "op", "inputs", "params"}:
            raise ConstructionError(f"invalid constructor node schema: {node}")
        if node["id"] in seen:
            raise ConstructionError(f"duplicate constructor node: {node['id']}")
        seen.add(node["id"])
        op = node["op"]
        if op not in allowed_stage_ops or op not in schemas:
            raise ConstructionError(f"unregistered constructor operation: {op}")
        schema = schemas[op]
        if node["params"] != schema["params"] or len(node["inputs"]) != schema["input_count"]:
            raise ConstructionError(f"constructor operation schema mismatch: {op}")
    expected = [
        "enumerate_ordered_distinct_frames",
        "construct_frame_local_marks",
        "evaluate_source_validity",
        "construct_physical_and_killed_states",
        "construct_deterministic_schedules",
        "construct_complete_event_rows",
        "construct_exchangeable_initial_law",
        "construct_adjacent_s9_actions",
    ]
    if [node["op"] for node in program] != expected:
        raise ConstructionError("constructor program stages are incomplete or reordered")
    claim = reader.get("reverse_rule.claim")
    if claim != "proposed_reverse_ratio_not_detailed_balance":
        if reader.get("reverse_rule.requires_reference_measure_for_detailed_balance"):
            raise ConstructionError("unsupported detailed-balance claim without a serialized measure")
    return reader


def validate_control_input(spec: Mapping[str, Any], vector: Mapping[str, Any]) -> None:
    allowed = spec["input_schema"]["allowed_fields"]
    if set(vector) != set(allowed):
        extra = sorted(set(vector) - set(allowed))
        missing = sorted(set(allowed) - set(vector))
        raise ConstructionError(f"control input fields mismatch; extra={extra}, missing={missing}")
    radii = vector["metric_radii"]
    if not isinstance(radii, list) or len(radii) != 9:
        raise ConstructionError("metric_radii must have exactly nine exact components")
    if any(parse_fraction(x) <= 0 for x in radii):
        raise ConstructionError("metric radii must be positive")
    arity = int(vector["frame_arity"])  # ARITY_FROM_REGISTERED_INPUT
    min_a = int(spec["frame_prior"]["minimum_arity"])
    max_a = int(spec["frame_prior"]["maximum_arity"])
    if not (min_a <= arity <= max_a):
        raise ConstructionError("frame_arity outside registered prior range")
    if arity > len(spec["frame_prior"]["role_catalog"]):
        raise ConstructionError("frame_arity exceeds registered role catalog")
    speed = parse_fraction(vector["relative_speed"])
    if speed <= 0:
        raise ConstructionError("relative_speed must be positive")
    ratio = parse_fraction(vector["proposed_reverse_ratio"])
    if ratio < 0 or ratio > 1:
        raise ConstructionError("proposed_reverse_ratio must lie in [0,1]")
    if vector["source_registry_id"] not in spec["probability_registry"]:
        raise ConstructionError("unknown source registry")


def frame_id(frame: Sequence[int]) -> str:
    return "f" + "_".join(str(x) for x in frame)


def mark_template(axis: int | None, sign: int) -> str:
    if axis is None:
        return "central"
    return f"axis_{axis}_{'plus' if sign > 0 else 'minus'}"


def mark_id(fid: str, template: str) -> str:
    return f"{fid}|M|{template}"


def cemetery_mark_id(reason: str) -> str:
    return f"CEM|{reason}"


def present_state_id(fid: str, history: str) -> str:
    return f"{fid}|P|{history}"


def products_state_id(fid: str, history: str, template: str) -> str:
    return f"{fid}|A|{history}|{template}"


def killed_state_id(fid: str, history: str, reason: str) -> str:
    return f"{fid}|K|{history}|{reason}"


def catalog_killed_state_id(reason: str) -> str:
    return f"KC|{reason}"


def event_id(source_state: str, channel: str, mid: str) -> str:
    return f"{source_state}|E|{channel}|{mid}"


def zero_charge(spec: Mapping[str, Any]) -> List[int]:
    return list(spec["state_rule"]["global_charge_default"])


def physical_projection(spec: Mapping[str, Any], kind: str, frame: Sequence[int] | None, history: str | None, product_mark: str | None = None) -> Dict[str, Any]:
    key = "present_physical" if kind == "P" else "products_physical"
    base = dict(spec["state_rule"][key])
    return {
        "pair_present": bool(base["pair_present"]),
        "system_energy": base["system_energy"],
        "reservoir_energy": base["reservoir_energy"],
        "work_energy": base["work_energy"],
        "global_charge_vector": zero_charge(spec),
        "frame": list(frame) if frame is not None else None,
    }


def reverse_template(template: str) -> str:
    if template == "central":
        return template
    if template.endswith("_plus"):
        return template[:-5] + "_minus"
    if template.endswith("_minus"):
        return template[:-6] + "_plus"
    raise ConstructionError(f"cannot time reverse mark template: {template}")


def history_after_miss(mark_class: str) -> str:
    if mark_class not in {"central", "shell"}:
        raise ConstructionError(f"invalid mark class for history: {mark_class}")
    return mark_class


def interval_contains(value: Fraction, lower: Fraction, upper: Fraction, lower_kind: str, upper_kind: str) -> bool:
    if lower_kind == "closed":
        lo = value >= lower
    elif lower_kind == "open":
        lo = value > lower
    else:
        raise ConstructionError("unknown lower interval closure")
    if upper_kind == "closed":
        hi = value <= upper
    elif upper_kind == "open":
        hi = value < upper
    else:
        raise ConstructionError("unknown upper interval closure")
    return lo and hi


def construct_frames(spec: Mapping[str, Any], vector: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    arity = int(vector["frame_arity"])  # ARITY_FROM_REGISTERED_INPUT
    roles = spec["frame_prior"]["role_catalog"][:arity]
    frames: Dict[str, Dict[str, Any]] = {}
    for frame in itertools.permutations(spec["direction_set"], arity):
        fid = frame_id(frame)
        frames[fid] = {"id": fid, "axes": list(frame), "roles": list(roles), "arity": arity}
    return frames


def candidate_marks_for_frame(spec: Mapping[str, Any], vector: Mapping[str, Any], frame: Sequence[int]) -> List[Dict[str, Any]]:
    radii = [parse_fraction(x) for x in vector["metric_radii"]]
    sd = parse_fraction(vector["self_dual_radius"])
    used = set(frame)
    normal_axes = [i for i in spec["direction_set"] if i not in used]
    impact_fraction = parse_fraction(spec["mark_rule"]["impact_coordinate_fraction"])
    rows = [{"template": "central", "class": "central", "impact_axis": None, "impact_sign": 0, "impact_coordinate": "0/1", "b2": "0/1", "reverse_template": "central"}]
    for axis in normal_axes:
        if radii[axis] > sd:
            b = (radii[axis] - sd) * impact_fraction
            for sign in (1, -1):
                template = mark_template(axis, sign)
                rows.append({
                    "template": template,
                    "class": "shell",
                    "impact_axis": axis,
                    "impact_sign": sign,
                    "impact_coordinate": fraction_text(sign * b),
                    "b2": fraction_text(b * b),
                    "reverse_template": reverse_template(template),
                })
    return rows


def construct_candidate_marks(spec: Mapping[str, Any], vector: Mapping[str, Any], frames: Mapping[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    return {fid: candidate_marks_for_frame(spec, vector, row["axes"]) for fid, row in frames.items()}


def ann_probability(spec: Mapping[str, Any], vector: Mapping[str, Any], b2: str) -> Fraction | None:
    reg = spec["probability_registry"][vector["source_registry_id"]]
    if b2 == reg["central_b2"]:
        return parse_fraction(reg["central_ann_probability"])
    if b2 == reg["shell_b2"]:
        return parse_fraction(reg["shell_ann_probability"])
    return None


def construct_source_cases(spec: Mapping[str, Any], vector: Mapping[str, Any], frames: Mapping[str, Any], candidate_marks: Mapping[str, List[Dict[str, Any]]]) -> Dict[str, str]:
    radii = [parse_fraction(x) for x in vector["metric_radii"]]
    sd = parse_fraction(vector["self_dual_radius"])
    speed = parse_fraction(vector["relative_speed"])
    speed_min = parse_fraction(vector["speed_min"])
    speed_max = parse_fraction(vector["speed_max"])
    conditions_global = {
        "unresolved_amplitude": vector["amplitude_status"] != spec["validity"]["amplitude_valid_value"],
        "velocity": not interval_contains(speed, speed_min, speed_max, spec["validity"]["speed_interval"]["lower"], spec["validity"]["speed_interval"]["upper"]),
        "coupling_dilution": parse_fraction(vector["coupling"]) > parse_fraction(vector["coupling_max"]) or not bool(vector["dilute_flag"]),
    }
    out: Dict[str, str] = {}
    for fid, frame_row in frames.items():
        unsupported = any(ann_probability(spec, vector, m["b2"]) is None for m in candidate_marks[fid])
        conditions = dict(conditions_global)
        conditions["unresolved_amplitude"] = conditions["unresolved_amplitude"] or unsupported
        conditions["geometry"] = not all(radii[a] > sd for a in frame_row["axes"])
        conditions["valid"] = True
        chosen = None
        for name in spec["validity"]["precedence"]:
            if conditions.get(name, False):
                chosen = name
                break
        if chosen is None:
            raise ConstructionError("validity precedence failed to select a source case")
        out[fid] = chosen
    return out


def construct_marks(spec: Mapping[str, Any], vector: Mapping[str, Any], frames: Mapping[str, Any], candidate_marks: Mapping[str, List[Dict[str, Any]]], source_cases: Mapping[str, str]) -> Dict[str, Dict[str, Any]]:
    marks: Dict[str, Dict[str, Any]] = {}
    for fid in sorted(frames):
        if source_cases[fid] != "valid":
            continue
        local = candidate_marks[fid]
        p_mark = Fraction(1, len(local))
        for row in local:
            mid = mark_id(fid, row["template"])
            marks[mid] = {
                "id": mid,
                "frame_id": fid,
                **row,
                "mark_probability": fraction_text(p_mark),
                "ann_probability": fraction_text(ann_probability(spec, vector, row["b2"])),
                "reverse_mark_id": mark_id(fid, row["reverse_template"]),
                "kind": "frame_local",
            }
    for reason in spec["alphabets"]["cemetery_reasons"]:
        mid = cemetery_mark_id(reason)
        marks[mid] = {
            "id": mid,
            "frame_id": None,
            "template": reason,
            "class": "cemetery",
            "impact_axis": None,
            "impact_sign": 0,
            "impact_coordinate": "0/1",
            "b2": "0/1",
            "mark_probability": "1/1",
            "ann_probability": "0/1",
            "reverse_template": reason,
            "reverse_mark_id": mid,
            "kind": "cemetery",
        }
    return marks
