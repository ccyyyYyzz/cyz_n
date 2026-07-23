#!/usr/bin/env python3
"""Independent hostile verifier for Brief 0015.

The verifier imports no generator code.  It reads the complete constructor
specification, interprets it independently, expands every compact instance,
checks the scheduled Markov-renewal semantics, and can run isolated hostile
mutations.  All source is plain standard Python.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import copy
import gc
import hashlib
import itertools
import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

ARTIFACT_SCHEMA = "cyz-0015-kernel-artifact-v1"
EXPECTED_GENERATOR_API = "cyz-0015-generator-v1"


class VerificationError(RuntimeError):
    def __init__(self, code: str, message: str, location: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.location = location

    def record(self) -> Dict[str, str]:
        return {"code": self.code, "message": self.message, "location": self.location}


def fail(code: str, message: str, location: str = "") -> None:
    raise VerificationError(code, message, location)


def parse_fraction(value: str | int | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str) or "/" not in value:
        fail("fraction", f"invalid exact fraction {value!r}")
    n, d = value.split("/", 1)
    try:
        q = Fraction(int(n), int(d))
    except Exception as exc:
        fail("fraction", f"invalid exact fraction {value!r}: {exc}")
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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail("json_load", f"cannot load {path}: {exc}", str(path))


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
                fail("spec_missing_path", f"missing constructor specification path {path}", path)
            cur = cur[part]
        self.used.add(path)
        return cur


def verify_constructor_spec(spec: Mapping[str, Any]) -> SpecReader:
    exact_top = {
        "schema_version", "process_type", "ctmc_export", "classification", "direction_set",
        "frame_prior", "alphabets", "input_schema", "validity", "mark_rule",
        "probability_registry", "state_rule", "schedule_rule", "channel_rule",
        "probability_composition", "destination_rule", "history_rule", "reverse_rule",
        "ledger_rule", "initial_law", "s9", "constructor_program", "operation_schemas",
        "forbidden_capabilities", "must_consume", "executable_dependencies",
    }
    if set(spec) != exact_top:
        extra = sorted(set(spec) - exact_top)
        missing = sorted(exact_top - set(spec))
        fail("spec_schema", f"constructor specification keys mismatch extra={extra} missing={missing}")
    reader = SpecReader(spec)
    required = reader.get("must_consume")
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        fail("spec_schema", "must_consume must be a path list")
    for path in required:
        reader.get(path)
    if reader.get("process_type") != "scheduled_markov_renewal":
        fail("scheduled_process_type", "process_type is not scheduled_markov_renewal")
    if reader.get("ctmc_export") != "forbidden":
        fail("ctmc_export", "CTMC export prohibition is absent")
    if reader.get("direction_set") != list(range(9)):
        fail("direction_set", "direction_set is not the canonical anonymous nine-set")
    frame_prior = reader.get("frame_prior")
    if set(frame_prior) != {"status", "enumeration", "arity_input", "minimum_arity", "maximum_arity", "role_catalog", "velocity_role_index"}:
        fail("frame_prior_schema", "frame prior schema is not closed")
    if frame_prior["enumeration"] != "ordered_distinct_roles":
        fail("frame_enumeration", "unsupported frame enumeration")
    if frame_prior["status"] != "proposed_microscopic_closure_parameter":
        fail("frame_prior_status", "frame arity is not labeled as a proposed microscopic prior")
    if frame_prior["arity_input"] != "frame_arity":
        fail("frame_prior_schema", "frame arity input not registered")
    if not (2 <= int(frame_prior["minimum_arity"]) <= int(frame_prior["maximum_arity"]) <= 4):
        fail("frame_prior_schema", "frame arity bounds invalid")
    if int(frame_prior["velocity_role_index"]) != 1:
        fail("frame_prior_schema", "velocity role index changed")
    if len(frame_prior["role_catalog"]) < int(frame_prior["maximum_arity"]):
        fail("frame_prior_schema", "role catalog shorter than maximum arity")
    expected_alphabets = {"histories", "source_cases", "cemetery_reasons", "state_classes", "channel_kinds"}
    if set(reader.get("alphabets")) != expected_alphabets:
        fail("alphabet_schema", "alphabet schema is not closed")
    allowed_fields = reader.get("input_schema.allowed_fields")
    forbidden_fields = set(reader.get("input_schema.forbidden_fields"))
    if "frame_arity" not in allowed_fields or any(x in allowed_fields for x in forbidden_fields):
        fail("input_schema", "constructor input schema contains forbidden or missing fields")
    if any(x in forbidden_fields for x in {"rank", "target_rank", "visible_count", "active_mask", "response_cell"}) is False:
        fail("input_schema", "required forbidden fields absent")
    precedence = reader.get("validity.precedence")
    if sorted(precedence) != sorted(["unresolved_amplitude", "velocity", "coupling_dilution", "geometry", "valid"]):
        fail("precedence_schema", "validity precedence does not contain the exact source cases")
    if reader.get("validity.speed_interval.lower") not in {"closed", "open"} or reader.get("validity.speed_interval.upper") not in {"closed", "open"}:
        fail("interval_schema", "invalid interval closure")
    registry = reader.get("probability_registry.gkm_sparse_v1")
    if set(registry) != {"central_b2", "central_ann_probability", "shell_b2", "shell_ann_probability", "shell_outward_interval", "claim", "unsupported_b2"}:
        fail("registry_schema", "source probability registry has unregistered entries")
    lo, hi = map(parse_fraction, registry["shell_outward_interval"])
    selected = parse_fraction(registry["shell_ann_probability"])
    if not (lo < selected < hi):
        fail("registry_interval", "selected shell probability is not strictly inside its outward interval")
    reverse = reader.get("reverse_rule")
    if reverse["claim"] != "proposed_reverse_ratio_not_detailed_balance":
        if reverse.get("requires_reference_measure_for_detailed_balance", False):
            fail("unsupported_detailed_balance_claim", "detailed-balance label lacks a serialized reference measure and flux identity")
    expected_ops = [
        "enumerate_ordered_distinct_frames",
        "construct_frame_local_marks",
        "evaluate_source_validity",
        "construct_physical_and_killed_states",
        "construct_deterministic_schedules",
        "construct_complete_event_rows",
        "construct_exchangeable_initial_law",
        "construct_adjacent_s9_actions",
    ]
    program = reader.get("constructor_program")
    schemas = reader.get("operation_schemas")
    if not isinstance(program, list) or not isinstance(schemas, Mapping):
        fail("constructor_program", "constructor program missing")
    if [node.get("op") for node in program] != expected_ops:
        if any(node.get("op") == "instance_label_branch" for node in program if isinstance(node, Mapping)):
            fail("instance_label_dependency", "constructor program branches on opaque instance label")
        if any(node.get("op") == "count_if" for node in program if isinstance(node, Mapping)):
            fail("dsl_unknown_op", "count_if is forbidden")
        fail("constructor_program", "constructor stages are incomplete, reordered, or contain an unknown operation")
    stage_ids = set()
    for node in program:
        if set(node) != {"id", "op", "inputs", "params"}:
            fail("constructor_program", "constructor node schema is not closed", str(node.get("id", "")))
        if node["id"] in stage_ids:
            fail("constructor_program", "duplicate constructor node", node["id"])
        stage_ids.add(node["id"])
        op = node["op"]
        if op not in schemas:
            fail("dsl_unknown_op", f"unregistered constructor operation {op}", op)
        schema = schemas[op]
        if node["params"] != schema["params"]:
            fail("dsl_param_schema", f"parameters for {op} do not match closed schema", op)
        if len(node["inputs"]) != schema["input_count"]:
            fail("dsl_param_schema", f"input arity for {op} does not match closed schema", op)
        for inp in node["inputs"]:
            if inp in {"visible_count", "target_rank", "active_mask", "response_cell", "number_above_boundary", "instance_id"}:
                code = "instance_label_dependency" if inp == "instance_id" else "dsl_unwhitelisted_leaf"
                fail(code, f"forbidden constructor input {inp}", op)
    forbidden_caps = set(reader.get("forbidden_capabilities"))
    required_caps = {"environment_read", "file_read", "network_read", "free_form_rule", "unregistered_global", "post_classifier_override", "response_rank_input", "visible_count_input", "active_mask_input", "instance_label_branch", "count_if", "count_alias", "special_cardinality_lookup"}
    if not required_caps.issubset(forbidden_caps):
        fail("nonencoding_schema", "forbidden capability registry is incomplete")
    generators = reader.get("s9.adjacent_generators")
    expected_generators = [{"id": f"s{i}", "swap": [i, i + 1]} for i in range(8)]
    if generators != expected_generators:
        fail("s9_spec", "serialized adjacent S9 generators are missing or corrupted")
    return reader


def verify_control_manifest(spec: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    if set(manifest) != {"schema_version", "constructor_spec_sha256", "constructor_reads_only", "controls", "opaque_id_renaming_control", "report_metadata_policy"}:
        fail("manifest_schema", "control vector manifest schema is not closed")
    if manifest["constructor_spec_sha256"] != canonical_sha256(spec):
        fail("control_manifest_spec_hash", "control manifest does not bind supplied constructor spec")
    if manifest["constructor_reads_only"] != "opaque_id_and_input; report_metadata_is_not_constructor_input":
        fail("manifest_schema", "constructor-read boundary missing")
    ids = set()
    for control in manifest["controls"]:
        if set(control) != {"opaque_id", "input", "obligations", "report_metadata"}:
            fail("manifest_schema", "control vector schema is not closed")
        oid = control["opaque_id"]
        if oid in ids:
            fail("manifest_schema", "duplicate opaque id", oid)
        ids.add(oid)
        if not isinstance(oid, str) or not oid:
            fail("manifest_schema", "opaque id invalid")
        verify_input(spec, control["input"])


def verify_input(spec: Mapping[str, Any], vector: Mapping[str, Any]) -> None:
    allowed = spec["input_schema"]["allowed_fields"]
    if set(vector) != set(allowed):
        extra = sorted(set(vector) - set(allowed))
        missing = sorted(set(allowed) - set(vector))
        fail("control_unregistered_field", f"control fields mismatch extra={extra} missing={missing}")
    radii = vector["metric_radii"]
    if not isinstance(radii, list) or len(radii) != 9 or any(parse_fraction(x) <= 0 for x in radii):
        fail("metric_input", "metric_radii must be nine positive exact fractions")
    arity = int(vector["frame_arity"])  # ARITY_FROM_REGISTERED_INPUT
    if not int(spec["frame_prior"]["minimum_arity"]) <= arity <= int(spec["frame_prior"]["maximum_arity"]):
        fail("frame_arity", "frame arity outside registered prior")
    if arity > len(spec["frame_prior"]["role_catalog"]):
        fail("frame_arity", "frame arity exceeds role catalog")
    if parse_fraction(vector["relative_speed"]) <= 0:
        fail("speed_input", "relative speed must be positive")
    ratio = parse_fraction(vector["proposed_reverse_ratio"])
    if not 0 <= ratio <= 1:
        fail("reverse_ratio", "proposed reverse ratio outside [0,1]")
    if vector["source_registry_id"] not in spec["probability_registry"]:
        fail("registry_id", "unknown source registry")


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


def reverse_template(template: str) -> str:
    if template == "central":
        return template
    if template.endswith("_plus"):
        return template[:-5] + "_minus"
    if template.endswith("_minus"):
        return template[:-6] + "_plus"
    fail("mark_reverse", f"cannot reverse mark template {template}")
    return ""


def interval_contains(value: Fraction, lower: Fraction, upper: Fraction, lower_kind: str, upper_kind: str) -> bool:
    if lower_kind == "closed":
        lo = value >= lower
    elif lower_kind == "open":
        lo = value > lower
    else:
        fail("interval_schema", "unknown lower closure")
    if upper_kind == "closed":
        hi = value <= upper
    elif upper_kind == "open":
        hi = value < upper
    else:
        fail("interval_schema", "unknown upper closure")
    return lo and hi


def zero_charge(spec: Mapping[str, Any]) -> List[int]:
    return list(spec["state_rule"]["global_charge_default"])


def physical_projection(spec: Mapping[str, Any], kind: str, frame: Sequence[int] | None, history: str | None, product_mark: str | None = None) -> Dict[str, Any]:
    key = "present_physical" if kind == "P" else "products_physical"
    base = spec["state_rule"][key]
    return {
        "pair_present": bool(base["pair_present"]),
        "system_energy": base["system_energy"],
        "reservoir_energy": base["reservoir_energy"],
        "work_energy": base["work_energy"],
        "global_charge_vector": zero_charge(spec),
        "frame": list(frame) if frame is not None else None,
    }


def registry_probability(spec: Mapping[str, Any], vector: Mapping[str, Any], b2: str) -> Fraction | None:
    reg = spec["probability_registry"][vector["source_registry_id"]]
    if b2 == reg["central_b2"]:
        return parse_fraction(reg["central_ann_probability"])
    if b2 == reg["shell_b2"]:
        return parse_fraction(reg["shell_ann_probability"])
    return None
