#!/usr/bin/env python3
"""Generator model expansion for Brief 0015."""
from generator_core import *

def construct_states(spec: Mapping[str, Any], frames: Mapping[str, Any], candidate_marks: Mapping[str, List[Dict[str, Any]]], source_cases: Mapping[str, str]) -> Dict[str, Dict[str, Any]]:
    states: Dict[str, Dict[str, Any]] = {}
    histories = spec["alphabets"]["histories"]
    for fid, frame_row in frames.items():
        frame = frame_row["axes"]
        for hist in histories:
            sid = present_state_id(fid, hist)
            projection = physical_projection(spec, "P", frame, hist)
            states[sid] = {"id": sid, "class": "P", "status": "physical", "frame_id": fid, "frame": list(frame), "history": hist, "origin_mark_template": None, "cemetery_reason": None, "physical_projection": projection}
            if source_cases[fid] == "valid":
                for m in candidate_marks[fid]:
                    aid = products_state_id(fid, hist, m["template"])
                    states[aid] = {"id": aid, "class": "A", "status": "physical", "frame_id": fid, "frame": list(frame), "history": hist, "origin_mark_template": m["template"], "cemetery_reason": None, "physical_projection": physical_projection(spec, "A", frame, hist, m["template"])}
            else:
                reason = source_cases[fid]
                kid = killed_state_id(fid, hist, reason)
                states[kid] = {"id": kid, "class": "K", "status": "killed", "frame_id": fid, "frame": list(frame), "history": hist, "origin_mark_template": None, "cemetery_reason": reason, "physical_projection": dict(projection)}
    for reason in spec["alphabets"]["cemetery_reasons"]:
        sid = catalog_killed_state_id(reason)
        states[sid] = {
            "id": sid,
            "class": "KC",
            "status": "catalog_killed",
            "frame_id": None,
            "frame": None,
            "history": None,
            "origin_mark_template": None,
            "cemetery_reason": reason,
            "physical_projection": {
                "pair_present": False,
                "system_energy": "0/1",
                "reservoir_energy": "0/1",
                "work_energy": "0/1",
                "global_charge_vector": zero_charge(spec),
                "frame": None,
            },
        }
    return states


def hold_time(spec: Mapping[str, Any], vector: Mapping[str, Any], frame: Sequence[int]) -> Fraction:
    velocity_index = int(spec["frame_prior"]["velocity_role_index"])
    axis = frame[velocity_index]
    radius = parse_fraction(vector["metric_radii"][axis])
    separation = radius * parse_fraction(vector["separation_fraction"])
    return separation / parse_fraction(vector["relative_speed"])


def construct_schedules(spec: Mapping[str, Any], vector: Mapping[str, Any], states: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    schedules: Dict[str, Dict[str, Any]] = {}
    phase_count = int(spec["schedule_rule"]["phase_count"])
    for sid, state in states.items():
        if state["status"] in {"killed", "catalog_killed"}:
            schedules[sid] = {"state_id": sid, "kind": spec["schedule_rule"]["killed_schedule"], "clock_semantics": spec["schedule_rule"]["clock_semantics"], "scheduled_hold_time": None, "physical_time_unit": spec["schedule_rule"]["physical_time_unit"], "initial_countdown_phase": None, "phase_count": 0, "event_at_phase": None, "phase_step": None, "schedule_exemption": "absorbing_killed", "not_a_ctmc": True}
        else:
            h = hold_time(spec, vector, state["frame"])
            schedules[sid] = {"state_id": sid, "kind": spec["schedule_rule"]["age_kind"], "clock_semantics": spec["schedule_rule"]["clock_semantics"], "scheduled_hold_time": fraction_text(h), "physical_time_unit": spec["schedule_rule"]["physical_time_unit"], "initial_countdown_phase": int(spec["schedule_rule"]["initial_countdown_phase"]), "phase_count": phase_count, "event_at_phase": int(spec["schedule_rule"]["event_at_phase"]), "phase_step": fraction_text(h / phase_count), "schedule_exemption": None, "not_a_ctmc": bool(spec["schedule_rule"]["not_a_ctmc"])}
    return schedules


def ledger_for(spec: Mapping[str, Any], channel: str) -> Dict[str, Any]:
    if channel in {"annihilate", "proposed_reverse_create"}:
        row = spec["ledger_rule"][channel]
    else:
        row = spec["ledger_rule"]["null"]
    return {
        "delta_system_energy": row["delta_system_energy"],
        "delta_reservoir_energy": row["delta_reservoir_energy"],
        "delta_work_energy": row["delta_work_energy"],
        "delta_global_charge_vector": list(row["delta_global_charge_vector"]),
    }


def make_event(spec: Mapping[str, Any], schedules: Mapping[str, Any], source: Mapping[str, Any], mid: str, channel: str, accepted: bool, probability: Fraction, destination: str, reverse_id: str | None, reverse_exemption: str | None, physical_changed: bool, history_changed: bool, source_case: str, closure_label: str) -> Dict[str, Any]:
    row = {
        "event_id": event_id(source["id"], channel, mid),
        "source_state_id": source["id"],
        "scheduled_hold_time": schedules[source["id"]]["scheduled_hold_time"],
        "physical_time_unit": schedules[source["id"]]["physical_time_unit"],
        "mark_id": mid,
        "channel_id": channel,
        "channel_kind": channel,
        "accepted": bool(accepted),
        "probability": fraction_text(probability),
        "destination_state_id": destination,
        "reverse_event_id": reverse_id,
        "reverse_exemption": reverse_exemption,
        "physical_projection_changed": bool(physical_changed),
        "history_changed": bool(history_changed),
        "source_registry_case": source_case,
        "proposed_closure_label": closure_label,
    }
    row.update(ledger_for(spec, channel))
    return row


def construct_events(spec: Mapping[str, Any], vector: Mapping[str, Any], states: Mapping[str, Any], marks: Mapping[str, Any], schedules: Mapping[str, Any], source_cases: Mapping[str, str]) -> Dict[str, List[Dict[str, Any]]]:
    rows: Dict[str, List[Dict[str, Any]]] = {}
    reverse_ratio = parse_fraction(vector["proposed_reverse_ratio"])
    closure_label = spec["classification"]
    for sid, state in states.items():
        events: List[Dict[str, Any]] = []
        cls = state["class"]
        if cls == "P":
            fid = state["frame_id"]
            case = source_cases[fid]
            if case == "valid":
                local_marks = [m for m in marks.values() if m["frame_id"] == fid and m["kind"] == "frame_local"]
                local_marks.sort(key=lambda x: x["id"])
                for m in local_marks:
                    pm = parse_fraction(m["mark_probability"])
                    pa = parse_fraction(m["ann_probability"])
                    dest_a = products_state_id(fid, state["history"], m["template"])
                    reverse_mid = m["reverse_mark_id"]
                    reverse_eid = event_id(dest_a, "proposed_reverse_create", reverse_mid)
                    events.append(make_event(spec, schedules, state, m["id"], "annihilate", True, pm * pa, dest_a, reverse_eid, None, True, False, case, closure_label))
                    new_hist = history_after_miss(m["class"])
                    dest_p = present_state_id(fid, new_hist)
                    events.append(make_event(spec, schedules, state, m["id"], "miss", False, pm * (1 - pa), dest_p, None, "null_history", False, new_hist != state["history"], case, closure_label))
            else:
                mid = cemetery_mark_id(case)
                dest = killed_state_id(fid, state["history"], case)
                events.append(make_event(spec, schedules, state, mid, "source_invalid", False, Fraction(1), dest, None, "epistemic_domain_exit", False, False, case, closure_label))
        elif cls == "A":
            fid = state["frame_id"]
            original_mid = mark_id(fid, state["origin_mark_template"])
            original_mark = marks[original_mid]
            reverse_mid = original_mark["reverse_mark_id"]
            p_reverse = parse_fraction(original_mark["ann_probability"]) * reverse_ratio
            dest = present_state_id(fid, state["history"])
            forward_eid = event_id(dest, "annihilate", original_mid)
            events.append(make_event(spec, schedules, state, reverse_mid, "proposed_reverse_create", True, p_reverse, dest, forward_eid, None, True, False, "valid", closure_label))
            events.append(make_event(spec, schedules, state, reverse_mid, "reverse_idle", False, 1 - p_reverse, sid, None, "null_idle", False, False, "valid", closure_label))
        elif cls in {"K", "KC"}:
            reason = state["cemetery_reason"]
            mid = cemetery_mark_id(reason)
            events.append(make_event(spec, schedules, state, mid, "killed_absorb", False, Fraction(1), sid, None, "absorbing_killed", False, False, reason, closure_label))
        else:
            raise ConstructionError(f"unhandled state class: {cls}")
        rows[sid] = events
    return rows


def construct_initial_law(spec: Mapping[str, Any], states: Mapping[str, Any]) -> Dict[str, str]:
    excluded = set(spec["initial_law"]["excluded_status"])
    physical = sorted(sid for sid, state in states.items() if state["status"] not in excluded)
    if not physical:
        raise ConstructionError("initial law has empty support")
    weight = fraction_text(Fraction(1, len(physical)))
    return {sid: weight for sid in physical}


def construct_s9_generators(spec: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [dict(x) for x in spec["s9"]["adjacent_generators"]]


def execute_constructor(spec: Mapping[str, Any], vector: Mapping[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    reader = validate_constructor_spec(spec)
    validate_control_input(spec, vector)
    context: Dict[str, Any] = {}
    program = spec["constructor_program"]
    for node in program:
        op = node["op"]
        if op == "enumerate_ordered_distinct_frames":
            context[node["id"]] = construct_frames(spec, vector)
        elif op == "construct_frame_local_marks":
            context[node["id"]] = construct_candidate_marks(spec, vector, context["frames"])
        elif op == "evaluate_source_validity":
            context[node["id"]] = construct_source_cases(spec, vector, context["frames"], context["candidate_marks"])
        elif op == "construct_physical_and_killed_states":
            context[node["id"]] = construct_states(spec, context["frames"], context["candidate_marks"], context["source_cases"])
        elif op == "construct_deterministic_schedules":
            context[node["id"]] = construct_schedules(spec, vector, context["states"])
        elif op == "construct_complete_event_rows":
            context["marks"] = construct_marks(spec, vector, context["frames"], context["candidate_marks"], context["source_cases"])
            context[node["id"]] = construct_events(spec, vector, context["states"], context["marks"], context["schedules"], context["source_cases"])
        elif op == "construct_exchangeable_initial_law":
            context[node["id"]] = construct_initial_law(spec, context["states"])
        elif op == "construct_adjacent_s9_actions":
            context[node["id"]] = construct_s9_generators(spec)
        else:
            raise ConstructionError(f"unhandled registered operation: {op}")
    model = {
        "frames": context["frames"],
        "candidate_marks": context["candidate_marks"],
        "source_cases": context["source_cases"],
        "marks": context["marks"],
        "states": context["states"],
        "schedules": context["schedules"],
        "events": context["events"],
        "initial_law": context["initial_law"],
        "s9_adjacent_generators": context["s9_actions"],
    }
    return model, sorted(spec["must_consume"])


def stream_expanded_sha256(model: Mapping[str, Any]) -> str:
    h = hashlib.sha256()
    for section in ("frames", "source_cases", "marks", "states", "schedules", "events", "initial_law", "s9_adjacent_generators"):
        h.update(section.encode("utf-8") + b"\n")
        value = model[section]
        if isinstance(value, Mapping):
            for key in sorted(value):
                h.update(canonical_bytes([key, value[key]]) + b"\n")
        else:
            for item in value:
                h.update(canonical_bytes(item) + b"\n")
    return h.hexdigest()


def summarize_model(model: Mapping[str, Any]) -> Dict[str, Any]:
    states = model["states"]
    events = model["events"]
    row_sums = []
    positive_non_null = 0
    reverse_declared = 0
    classes: Dict[str, int] = {}
    cases: Dict[str, int] = {}
    for state in states.values():
        classes[state["class"]] = classes.get(state["class"], 0) + 1
    for case in model["source_cases"].values():
        cases[case] = cases.get(case, 0) + 1
    for row in events.values():
        total = sum(parse_fraction(e["probability"]) for e in row)
        row_sums.append(total)
        for e in row:
            if parse_fraction(e["probability"]) > 0 and e["accepted"] and e["channel_kind"] in {"annihilate", "proposed_reverse_create"}:
                positive_non_null += 1
                if e["reverse_event_id"]:
                    reverse_declared += 1
    return {
        "frames_total": len(model["frames"]),
        "valid_frames": sum(1 for c in model["source_cases"].values() if c == "valid"),
        "invalid_frames": sum(1 for c in model["source_cases"].values() if c != "valid"),
        "marks_total": len(model["marks"]),
        "frame_local_marks": sum(1 for m in model["marks"].values() if m["kind"] == "frame_local"),
        "states_total": len(states),
        "state_class_coverage": classes,
        "atoms_total": sum(len(row) for row in events.values()),
        "states_with_stochastic_row": len(events),
        "states_with_unique_schedule": len(model["schedules"]),
        "positive_non_null_atoms": positive_non_null,
        "positive_non_null_atoms_with_declared_reverse": reverse_declared,
        "min_row_sum": fraction_text(min(row_sums)),
        "max_row_sum": fraction_text(max(row_sums)),
        "source_case_counts": cases,
        "initial_support_size": len(model["initial_law"]),
    }


def calibration_times(model: Mapping[str, Any], count: int = 5) -> List[str]:
    candidates = [sid for sid, state in model["states"].items() if state["class"] == "P" and model["source_cases"][state["frame_id"]] == "valid"]
    if not candidates:
        return []
    schedule = model["schedules"][sorted(candidates)[0]]
    hold = parse_fraction(schedule["scheduled_hold_time"])
    return [fraction_text((i + 1) * hold) for i in range(count)]


def build_instance_record(spec: Mapping[str, Any], vector: Mapping[str, Any], opaque_id: str, spec_hash: str, manifest_hash: str) -> Dict[str, Any]:
    model, consumed = execute_constructor(spec, vector)
    return {
        "opaque_id": opaque_id,
        "input": dict(vector),
        "constructor_spec_sha256": spec_hash,
        "control_vector_manifest_sha256": manifest_hash,
        "expanded_sha256": stream_expanded_sha256(model),
        "expanded_counts": summarize_model(model),
        "calibration_event_times": calibration_times(model),
        "consumed_spec_paths_sha256": canonical_sha256(consumed),
    }
