#!/usr/bin/env python3
"""Semantic checks for the independent fixed registered Brief 0015 verifier."""
from __future__ import annotations
import copy
import gc
from fractions import Fraction
from typing import Any, Mapping
from verifier_core import *
from verifier_model import *

def _index_events(model: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {event["event_id"]: event for row in model["events"].values() for event in row}

def _expected_state_id(state: Mapping[str, Any]) -> str:
    cls = state["class"]
    if cls == "P": return present_id(state["frame_id"], state["history"])
    if cls == "A": return products_id(state["frame_id"], state["history"], state["origin_mark_template"])
    if cls == "K": return killed_id(state["frame_id"], state["history"], state["cemetery_reason"])
    if cls == "KC": return catalog_killed_id(state["cemetery_reason"])
    fail("state_class", f"unknown state class {cls}", state.get("id", ""))

def verify_model(spec: Mapping[str, Any], vector: Mapping[str, Any], model: Mapping[str, Any], location: str = "") -> dict[str, Any]:
    # Refuse every non-registered specification before inspecting supplied
    # model data.  These checks certify one fixed contract, not a general DSL.
    verify_constructor_spec(spec)
    verify_input(spec, vector)
    required_sections = {"frames","candidate_marks","source_cases","marks","states","schedules","events","initial_law","s9_adjacent_generators"}
    if set(model) != required_sections: fail("model_schema", "expanded model sections mismatch", location)
    # Typed records and IDs.
    for fid, frame in model["frames"].items():
        verify_record(spec,"frame_record",frame,f"{location}.frames.{fid}")
        if fid != frame["id"] or fid != frame_id(frame["axes"]): fail("frame_id", "frame ID grammar mismatch", fid)
        if frame["arity"] != int(vector["frame_arity"]) or len(frame["axes"]) != frame["arity"] or len(set(frame["axes"])) != frame["arity"]: fail("frame_arity", "frame arity/axes mismatch", fid)
        if frame["roles"] != spec["frame_prior"]["role_catalog"][:frame["arity"]]: fail("frame_roles", "frame roles do not match registered prefix", fid)
    expected_frame_count = 1
    for n in range(9, 9-int(vector["frame_arity"]), -1): expected_frame_count *= n
    if len(model["frames"]) != expected_frame_count: fail("frame_coverage", "ordered frame enumeration incomplete", location)
    for fid, rows in model["candidate_marks"].items():
        if fid not in model["frames"]: fail("candidate_mark_frame", "candidate marks reference missing frame", fid)
        for i, row in enumerate(rows): verify_record(spec,"candidate_mark_record",row,f"{location}.candidate_marks.{fid}.{i}")
    if set(model["source_cases"]) != set(model["frames"]): fail("source_case_coverage", "source cases do not cover frames", location)
    for fid, case in model["source_cases"].items():
        if case not in spec["alphabets"]["source_cases"]: fail("source_case", "unknown source case", fid)
    for mid, mark in model["marks"].items():
        verify_record(spec,"mark_record",mark,f"{location}.marks.{mid}")
        if mid != mark["id"]: fail("mark_id", "mark mapping key differs from record ID", mid)
        if mark["kind"] == "frame_local":
            if mark["frame_id"] not in model["frames"] or mid != mark_id(mark["frame_id"],mark["template"]): fail("mark_id", "frame-local mark ID invalid", mid)
            if model["source_cases"][mark["frame_id"]] != "valid": fail("mark_validity", "frame-local mark registered for invalid frame", mid)
            if mark["reverse_mark_id"] not in model["marks"]: fail("reverse_mark", "reverse mark missing", mid)
            if model["marks"][mark["reverse_mark_id"]]["reverse_mark_id"] != mid: fail("reverse_mark", "mark involution fails", mid)
        else:
            if mid != cemetery_mark_id(mark["template"]): fail("cemetery_mark", "cemetery mark ID invalid", mid)
    for sid, state in model["states"].items():
        verify_record(spec,"state_record",state,f"{location}.states.{sid}")
        if sid != state["id"] or sid != _expected_state_id(state): fail("state_id", "state ID grammar mismatch", sid)
        proj = state["physical_projection"]
        if state["class"] in {"P","A","K"} and proj["frame"] != state["frame"]: fail("state_projection", "state projection frame mismatch", sid)
        if state["class"] == "K":
            source = model["states"].get(present_id(state["frame_id"],state["history"]))
            if source is None or proj != source["physical_projection"]: fail("killed_payload", "killed lift does not preserve source projection", sid)
            if state["cemetery_reason"] != model["source_cases"][state["frame_id"]]: fail("killed_reason", "killed reason differs from source case", sid)
    state_ids = set(model["states"])
    if set(model["schedules"]) != state_ids: fail("schedule_coverage", "one schedule per state not satisfied", location)
    if set(model["events"]) != state_ids: fail("row_coverage", "one stochastic row per state not satisfied", location)
    event_index = _index_events(model)
    if len(event_index) != sum(len(row) for row in model["events"].values()): fail("event_id", "duplicate event ID", location)
    for sid, schedule in model["schedules"].items():
        verify_record(spec,"schedule_record",schedule,f"{location}.schedules.{sid}")
        if schedule["state_id"] != sid: fail("schedule_id", "schedule state ID mismatch", sid)
        state = model["states"][sid]
        if state["status"] in spec["initial_law"]["excluded_status"]:
            if schedule["kind"] != "absorbing_exempt" or schedule["schedule_exemption"] != "absorbing_killed" or schedule["scheduled_hold_time"] is not None or schedule["phase_count"] != 0: fail("killed_schedule", "killed schedule not absorbing/exempt", sid)
        else:
            if schedule["kind"] != "finite_countdown" or schedule["clock_semantics"] != "deterministic_scheduled" or not schedule["not_a_ctmc"]: fail("scheduled_semantics", "physical schedule is not deterministic scheduled Markov-renewal", sid)
            hold = parse_fraction(schedule["scheduled_hold_time"]); step = parse_fraction(schedule["phase_step"])
            if hold <= 0 or step * schedule["phase_count"] != hold or schedule["event_at_phase"] != schedule["phase_count"]: fail("scheduled_clock", "countdown age rule inconsistent", sid)
            expected = hold_time(spec, vector, state["frame"])
            if hold != expected: fail("scheduled_clock", "hold time does not follow registered metric rule", sid)
    accepted_non_null = set(spec["channel_rule"]["accepted_non_null"])
    null_channels = set(spec["channel_rule"]["null_history_channels"])
    min_sum: Fraction | None = None; max_sum: Fraction | None = None; positive_non_null = valid_reverse = 0
    for sid, row in model["events"].items():
        state = model["states"][sid]
        total = Fraction(0)
        for event in row:
            verify_record(spec,"event_record",event,f"{location}.events.{event.get('event_id','?')}")
            eid = event["event_id"]
            if event["channel_id"] != event["channel_kind"]: fail("channel_schema", "channel_id and channel_kind differ", eid)
            if event["source_state_id"] != sid or eid != event_id(sid,event["channel_id"],event["mark_id"]): fail("event_id", "event ID/source grammar mismatch", eid)
            probability = parse_fraction(event["probability"])
            if probability < 0: fail("negative_probability", "negative event probability", eid)
            total += probability
            if event["mark_id"] not in model["marks"]: fail("dangling_mark", f"event references missing mark {event['mark_id']}", eid)
            if event["destination_state_id"] not in model["states"]: fail("dangling_destination", f"event references missing destination {event['destination_state_id']}", eid)
            if event["scheduled_hold_time"] != model["schedules"][sid]["scheduled_hold_time"] or event["physical_time_unit"] != model["schedules"][sid]["physical_time_unit"]: fail("event_schedule", "event schedule fields mismatch state schedule", eid)
            destination = model["states"][event["destination_state_id"]]
            sp = state["physical_projection"]; dp = destination["physical_projection"]
            expected_deltas = {
                "delta_system_energy": fraction_text(parse_fraction(dp["system_energy"])-parse_fraction(sp["system_energy"])),
                "delta_reservoir_energy": fraction_text(parse_fraction(dp["reservoir_energy"])-parse_fraction(sp["reservoir_energy"])),
                "delta_work_energy": fraction_text(parse_fraction(dp["work_energy"])-parse_fraction(sp["work_energy"])),
                "delta_global_charge_vector": [b-a for a,b in zip(sp["global_charge_vector"],dp["global_charge_vector"])],
            }
            for field, expected in expected_deltas.items():
                if event[field] != expected: fail("charge_ledger" if field=="delta_global_charge_vector" else "energy_ledger", f"{field} does not match source/destination", eid)
            projection_changed = sp != dp
            if bool(event["physical_projection_changed"]) != projection_changed: fail("projection_flag", "physical projection flag disagrees with endpoint payload", eid)
            if event["channel_kind"] in null_channels and projection_changed: fail("null_projection", "null/history atom changes physical projection", eid)
            if event["channel_kind"] == "source_invalid":
                if projection_changed or any(parse_fraction(event[x]) != 0 for x in ["delta_system_energy","delta_reservoir_energy","delta_work_energy"]) or any(event["delta_global_charge_vector"]): fail("killed_payload", "source-invalid killed exit changes physical payload", eid)
                if destination["class"] != "K" or destination["cemetery_reason"] != event["source_registry_case"]: fail("source_validity_routing", "source-invalid exit does not reach matching killed lift", eid)
                if event["reverse_exemption"] != "epistemic_domain_exit": fail("source_validity_routing", "epistemic reverse exemption absent", eid)
            if state["class"] in {"K","KC"}:
                if len(row) != 1 or event["channel_kind"] != "killed_absorb" or event["destination_state_id"] != sid or event["reverse_exemption"] != "absorbing_killed": fail("killed_absorbing_row", "killed state is not exactly absorbing", sid)
            if probability > 0 and event["accepted"] and event["channel_kind"] in accepted_non_null:
                positive_non_null += 1
                rid = event["reverse_event_id"]
                if rid is None or rid not in event_index: fail("reverse_link", "positive non-null atom lacks reverse", eid)
                reverse = event_index[rid]
                if reverse["reverse_event_id"] != eid or reverse["source_state_id"] != event["destination_state_id"] or reverse["destination_state_id"] != sid: fail("reverse_link", "reverse endpoints or involution mismatch", eid)
                if model["marks"][event["mark_id"]]["reverse_mark_id"] != reverse["mark_id"]: fail("reverse_mark", "reverse event mark is not time reversed", eid)
                compatible = {("annihilate","proposed_reverse_create"),("proposed_reverse_create","annihilate")}
                if (event["channel_kind"],reverse["channel_kind"]) not in compatible: fail("reverse_channel", "reverse channel kind incompatible", eid)
                for field in ["delta_system_energy","delta_reservoir_energy","delta_work_energy"]:
                    if parse_fraction(event[field]) + parse_fraction(reverse[field]) != 0: fail("reverse_ledger", "reverse energy ledger not opposite", eid)
                if [a+b for a,b in zip(event["delta_global_charge_vector"],reverse["delta_global_charge_vector"])] != zero_charge(spec): fail("reverse_ledger", "reverse charge ledger not opposite", eid)
                valid_reverse += 1
        if total != 1: fail("row_sum", f"row probabilities sum to {fraction_text(total)}", sid)
        min_sum = total if min_sum is None or total < min_sum else min_sum
        max_sum = total if max_sum is None or total > max_sum else max_sum
    # Exact initial law.
    excluded = set(spec["initial_law"]["excluded_status"])
    expected_support = {sid for sid,state in model["states"].items() if state["status"] not in excluded}
    if set(model["initial_law"]) != expected_support: fail("initial_support", "initial law support differs from registered physical support", location)
    total_weight = sum(parse_fraction(w) for w in model["initial_law"].values())
    if total_weight != 1 or any(parse_fraction(w) <= 0 for w in model["initial_law"].values()): fail("initial_normalization", "initial law not positive and normalized", location)
    weights = {parse_fraction(w) for w in model["initial_law"].values()}
    if len(weights) != 1: fail("initial_exchangeability", "registered uniform initial law has unequal weights", location)
    # Record schemas on S9 list.
    if model["s9_adjacent_generators"] != spec["s9"]["adjacent_generators"]: fail("s9_spec", "model S9 list differs from specification", location)
    for i,row in enumerate(model["s9_adjacent_generators"]): verify_record(spec,"s9_generator_record",row,f"{location}.s9.{i}")
    # Frame-local f013 check for arity 3 if it exists.
    if int(vector["frame_arity"]) == 3 and "f0_1_3" in model["frames"] and model["source_cases"]["f0_1_3"] == "valid":
        templates = {m["template"] for m in model["marks"].values() if m["frame_id"] == "f0_1_3"}
        if not {"axis_2_plus","axis_2_minus"}.issubset(templates) or any(x in templates for x in {"axis_0_plus","axis_1_plus","axis_3_plus"}): fail("frame_local_marks", "f013 does not use its own normal axes", "f0_1_3")
    classes: dict[str,int] = {}; cases: dict[str,int] = {}
    for state in model["states"].values(): classes[state["class"]] = classes.get(state["class"],0)+1
    for case in model["source_cases"].values(): cases[case] = cases.get(case,0)+1
    return {"frames_total":len(model["frames"]),"valid_frames":cases.get("valid",0),"invalid_frames":len(model["frames"])-cases.get("valid",0),"marks_total":len(model["marks"]),"frame_local_marks":sum(m["kind"]=="frame_local" for m in model["marks"].values()),"states_total":len(model["states"]),"state_class_coverage":classes,"atoms_total":sum(len(row) for row in model["events"].values()),"states_with_stochastic_row":len(model["events"]),"states_with_unique_schedule":len(model["schedules"]),"positive_non_null_atoms":positive_non_null,"positive_non_null_atoms_with_declared_reverse":valid_reverse,"min_row_sum":fraction_text(min_sum or 0),"max_row_sum":fraction_text(max_sum or 0),"source_case_counts":cases,"initial_support_size":len(model["initial_law"])}

def swap_map(index: int) -> dict[int,int]:
    return {i:(index+1 if i==index else index if i==index+1 else i) for i in range(9)}
def permute_axes(axes: list[int] | None, permutation: Mapping[int,int]) -> list[int] | None:
    return None if axes is None else [permutation[x] for x in axes]
def permute_template(template: str, permutation: Mapping[int,int]) -> str:
    if template == "central" or not template.startswith("axis_"): return template
    parts = template.split("_"); return f"axis_{permutation[int(parts[1])]}_{parts[2]}"
def permute_frame_id(fid: str | None, permutation: Mapping[int,int]) -> str | None:
    if fid is None: return None
    axes = [int(x) for x in fid[1:].split("_")]
    return frame_id([permutation[x] for x in axes])
def permute_mark_id(mid: str, permutation: Mapping[int,int]) -> str:
    if mid.startswith("CEM|"): return mid
    fid, _, template = mid.partition("|M|")
    return mark_id(permute_frame_id(fid,permutation),permute_template(template,permutation))
def permute_state_id(sid: str, state: Mapping[str,Any], permutation: Mapping[int,int]) -> str:
    if state["class"] == "KC": return sid
    fid = permute_frame_id(state["frame_id"],permutation)
    if state["class"] == "P": return present_id(fid,state["history"])
    if state["class"] == "A": return products_id(fid,state["history"],permute_template(state["origin_mark_template"],permutation))
    return killed_id(fid,state["history"],state["cemetery_reason"])
def permute_vector(vector: Mapping[str,Any], permutation: Mapping[int,int]) -> dict[str,Any]:
    out = copy.deepcopy(vector); old = vector["metric_radii"]; new = [None]*9
    for i in range(9): new[permutation[i]] = old[i]
    out["metric_radii"] = new
    return out

def verify_s9_covariance(spec: Mapping[str,Any], vector: Mapping[str,Any], model: Mapping[str,Any], generators: list[int] | None = None) -> dict[str,Any]:
    verify_constructor_spec(spec)
    verify_input(spec, vector)
    checked: dict[str,Any] = {}
    generator_indices = generators if generators is not None else list(range(8))
    original_event_index = _index_events(model)
    for index in generator_indices:
        permutation = swap_map(index)
        target_vector = permute_vector(vector,permutation)
        target = execute_constructor(spec,target_vector)
        # Build state mapping first.
        state_map = {sid:permute_state_id(sid,state,permutation) for sid,state in model["states"].items()}
        mark_map = {mid:permute_mark_id(mid,permutation) for mid in model["marks"]}
        if set(state_map.values()) != set(target["states"]): fail("s9_state_bijection", "S9 state image is not a bijection", f"s{index}")
        if set(mark_map.values()) != set(target["marks"]): fail("s9_mark_bijection", "S9 mark image is not a bijection", f"s{index}")
        for fid, frame in model["frames"].items():
            tfid = permute_frame_id(fid,permutation); expected = copy.deepcopy(frame); expected["id"] = tfid; expected["axes"] = permute_axes(frame["axes"],permutation)
            if target["frames"].get(tfid) != expected: fail("s9_frame_covariance", "frame record not covariant", f"s{index}:{fid}")
        for fid, rows in model["candidate_marks"].items():
            tfid = permute_frame_id(fid,permutation); expected=[]
            for row in rows:
                r=copy.deepcopy(row); r["impact_axis"] = None if r["impact_axis"] is None else permutation[r["impact_axis"]]; r["template"] = permute_template(r["template"],permutation); r["reverse_template"] = permute_template(r["reverse_template"],permutation); expected.append(r)
            expected.sort(key=lambda r:(0 if r["template"]=="central" else 1, -1 if r["impact_axis"] is None else r["impact_axis"], 0 if r["impact_sign"]==1 else 1))
            if target["candidate_marks"].get(tfid) != expected: fail("s9_mark_covariance", "candidate mark records not covariant", f"s{index}:{fid}")
            if target["source_cases"].get(tfid) != model["source_cases"][fid]: fail("s9_validity_covariance", "source case not covariant", f"s{index}:{fid}")
        for mid, mark in model["marks"].items():
            tmid = mark_map[mid]; expected = copy.deepcopy(mark); expected["id"] = tmid; expected["frame_id"] = permute_frame_id(mark["frame_id"],permutation); expected["template"] = permute_template(mark["template"],permutation); expected["reverse_template"] = permute_template(mark["reverse_template"],permutation); expected["reverse_mark_id"] = permute_mark_id(mark["reverse_mark_id"],permutation); expected["impact_axis"] = None if mark["impact_axis"] is None else permutation[mark["impact_axis"]]
            if target["marks"].get(tmid) != expected: fail("s9_mark_covariance", "mark record not covariant", f"s{index}:{mid}")
        event_target_index = _index_events(target)
        for sid, state in model["states"].items():
            tsid = state_map[sid]; expected = copy.deepcopy(state); expected["id"] = tsid; expected["frame_id"] = permute_frame_id(state["frame_id"],permutation); expected["frame"] = permute_axes(state["frame"],permutation); expected["origin_mark_template"] = None if state["origin_mark_template"] is None else permute_template(state["origin_mark_template"],permutation); expected["physical_projection"]["frame"] = permute_axes(state["physical_projection"]["frame"],permutation); charge=state["physical_projection"]["global_charge_vector"]; pcharge=[0]*9
            for i,x in enumerate(charge): pcharge[permutation[i]]=x
            expected["physical_projection"]["global_charge_vector"] = pcharge
            if target["states"].get(tsid) != expected: fail("s9_state_covariance", "state record not covariant", f"s{index}:{sid}")
            schedule = copy.deepcopy(model["schedules"][sid]); schedule["state_id"] = tsid
            if target["schedules"].get(tsid) != schedule: fail("s9_schedule_covariance", "schedule record not covariant", f"s{index}:{sid}")
            for event in model["events"][sid]:
                expected_event = copy.deepcopy(event)
                expected_event["source_state_id"] = tsid
                expected_event["mark_id"] = mark_map[event["mark_id"]]
                expected_event["destination_state_id"] = state_map[event["destination_state_id"]]
                expected_event["event_id"] = event_id(tsid,event["channel_id"],expected_event["mark_id"])
                expected_event["reverse_event_id"] = None
                # Reverse IDs are mapped semantically by their referenced event record.
                if event["reverse_event_id"] is not None:
                    original_reverse = original_event_index[event["reverse_event_id"]]
                    expected_event["reverse_event_id"] = event_id(state_map[original_reverse["source_state_id"]],original_reverse["channel_id"],mark_map[original_reverse["mark_id"]])
                dcharge=[0]*9
                for i,x in enumerate(event["delta_global_charge_vector"]): dcharge[permutation[i]]=x
                expected_event["delta_global_charge_vector"] = dcharge
                target_event = event_target_index.get(expected_event["event_id"])
                if target_event != expected_event: fail("s9_event_covariance", "event atom not covariant", f"s{index}:{event['event_id']}")
        # Initial law is covariant.
        mapped_initial = {state_map[sid]:weight for sid,weight in model["initial_law"].items()}
        if mapped_initial != target["initial_law"]: fail("s9_initial_covariance", "initial law not covariant", f"s{index}")
        checked[f"s{index}"] = {"states":len(state_map),"marks":len(mark_map),"events":sum(len(row) for row in model["events"].values())}
        del target, target_vector, state_map, mark_map, event_target_index
        gc.collect()
    return checked

def apply_model_patch(model: dict[str,Any], patch: Mapping[str,Any] | None) -> None:
    if not patch: return
    name = patch.get("mutation")
    if patch.get("target") != "model": return
    # Stable first IDs, selected lazily because invalid controls contain no valid frame.
    physical_sid = next((s for s in sorted(model["states"]) if model["states"][s]["class"] == "P" and model["source_cases"][model["states"][s]["frame_id"]] == "valid"), None)
    invalid_sid = next((s for s in sorted(model["states"]) if model["states"][s]["class"] == "P" and model["source_cases"][model["states"][s]["frame_id"]] != "valid"), None)
    physical_mutations={"change_row_probability","delete_state_row","delete_schedule_row","ghost_mark_id","ghost_destination_id","change_reverse_event_id","change_system_energy_quantum","change_charge_quantum","null_history_physical_jump","alter_age_hold","replace_scheduled_by_poisson"}
    if name in physical_mutations and physical_sid is None: fail("patch_setup","mutation requires a valid physical frame")
    event = model["events"][physical_sid][0] if physical_sid is not None else None
    if name == "change_row_probability": event["probability"] = fraction_text(parse_fraction(event["probability"])+Fraction(1,1000))
    elif name == "delete_state_row": del model["events"][physical_sid]
    elif name == "delete_schedule_row": del model["schedules"][physical_sid]
    elif name == "ghost_mark_id": event["mark_id"] = "ghost_mark"
    elif name == "ghost_destination_id": event["destination_state_id"] = "ghost_state"
    elif name == "change_reverse_event_id": event["reverse_event_id"] = "ghost_reverse"
    elif name == "change_system_energy_quantum": event["delta_system_energy"] = "999/1"
    elif name == "change_charge_quantum": event["delta_global_charge_vector"][0] += 1
    elif name == "null_history_physical_jump":
        miss = next(e for e in model["events"][physical_sid] if e["channel_kind"] == "miss")
        miss["destination_state_id"] = event["destination_state_id"]; miss["physical_projection_changed"] = True; miss["delta_system_energy"]="-2/1"; miss["delta_reservoir_energy"]="2/1"
    elif name == "alter_age_hold": model["schedules"][physical_sid]["scheduled_hold_time"] = "3/1"
    elif name == "replace_scheduled_by_poisson": model["schedules"][physical_sid]["clock_semantics"] = "poisson"
    elif name in {"remove_cemetery_states","remove_source_validity_routing","killed_payload","killed_ledger","killed_reason","killed_absorbing_row"}:
        if invalid_sid is None: fail("patch_setup", "mutation requires invalid instance")
        source_event = model["events"][invalid_sid][0]; kid=source_event["destination_state_id"]
        if name == "remove_cemetery_states":
            for sid in [s for s,state in model["states"].items() if state["class"] in {"K","KC"}]: model["states"].pop(sid,None); model["events"].pop(sid,None); model["schedules"].pop(sid,None)
        elif name == "remove_source_validity_routing": source_event["destination_state_id"] = invalid_sid
        elif name == "killed_payload": model["states"][kid]["physical_projection"]["system_energy"] = "999/1"
        elif name == "killed_ledger": source_event["delta_system_energy"] = "-2/1"
        elif name == "killed_reason": model["states"][kid]["cemetery_reason"] = "velocity" if model["states"][kid]["cemetery_reason"] != "velocity" else "geometry"
        elif name == "killed_absorbing_row": model["events"][kid][0]["reverse_exemption"] = None
    elif name == "frame_arity_without_regeneration":
        # Model generated for one arity but caller will verify against patched vector.
        pass
    elif name in {"s9_state_image","s9_mark_image","s9_event_image"}:
        pass
    else: fail("unknown_patch", f"unknown model mutation {name}")
