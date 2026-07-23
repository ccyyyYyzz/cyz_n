#!/usr/bin/env python3
"""Independent implementation of the fixed registered Brief 0015 model."""
from __future__ import annotations
import hashlib
import itertools
from fractions import Fraction
from typing import Any, Mapping, Sequence
from verifier_core import *

# No generator module is imported.  The algorithms below implement only the
# exact contract selected by verifier_core.REGISTERED_SPEC_SHA256; they are not
# a general interpreter for modified constructor programs or semantic rules.

def frame_id(axes: Sequence[int]) -> str: return "f" + "_".join(str(x) for x in axes)
def mark_template(axis: int | None, sign: int) -> str: return "central" if axis is None else f"axis_{axis}_{'plus' if sign > 0 else 'minus'}"
def reverse_template(template: str) -> str:
    if template == "central": return template
    if template.endswith("_plus"): return template[:-5] + "_minus"
    if template.endswith("_minus"): return template[:-6] + "_plus"
    fail("mark_template", f"cannot reverse template {template}")
def mark_id(fid: str, template: str) -> str: return f"{fid}|M|{template}"
def cemetery_mark_id(reason: str) -> str: return f"CEM|{reason}"
def present_id(fid: str, history: str) -> str: return f"{fid}|P|{history}"
def products_id(fid: str, history: str, template: str) -> str: return f"{fid}|A|{history}|{template}"
def killed_id(fid: str, history: str, reason: str) -> str: return f"{fid}|K|{history}|{reason}"
def catalog_killed_id(reason: str) -> str: return f"KC|{reason}"
def event_id(source_id: str, channel: str, mid: str) -> str: return f"{source_id}|E|{channel}|{mid}"
def zero_charge(spec: Mapping[str, Any]) -> list[int]: return list(spec["state_rule"]["global_charge_default"])

def interval_contains(value: Fraction, lower: Fraction, upper: Fraction, lower_kind: str, upper_kind: str) -> bool:
    if lower_kind not in {"open","closed"} or upper_kind not in {"open","closed"}: fail("interval_schema", "unknown interval closure")
    return (value >= lower if lower_kind == "closed" else value > lower) and (value <= upper if upper_kind == "closed" else value < upper)

def projection(spec: Mapping[str, Any], kind: str, axes: Sequence[int] | None) -> dict[str, Any]:
    key = "present_physical" if kind == "P" else "products_physical"
    src = spec["state_rule"][key]
    return {"pair_present": bool(src["pair_present"]), "system_energy": src["system_energy"], "reservoir_energy": src["reservoir_energy"], "work_energy": src["work_energy"], "global_charge_vector": zero_charge(spec), "frame": list(axes) if axes is not None else None}

def build_frames(spec: Mapping[str, Any], vector: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    arity = vector["frame_arity"]
    roles = list(spec["frame_prior"]["role_catalog"][:arity])
    rows: dict[str, dict[str, Any]] = {}
    for axes in itertools.permutations(spec["direction_set"], arity):
        fid = frame_id(axes)
        rows[fid] = {"id": fid, "axes": list(axes), "roles": list(roles), "arity": arity}
    return rows

def candidate_marks_for_frame(spec: Mapping[str, Any], vector: Mapping[str, Any], axes: Sequence[int]) -> list[dict[str, Any]]:
    radii = [parse_fraction(x) for x in vector["metric_radii"]]
    sd = parse_fraction(vector["self_dual_radius"])
    impact_fraction = parse_fraction(spec["mark_rule"]["impact_coordinate_fraction"])
    rows = [{"template":"central","class":"central","impact_axis":None,"impact_sign":0,"impact_coordinate":"0/1","b2":"0/1","reverse_template":"central"}]
    normal_axes = [i for i in spec["direction_set"] if i not in set(axes)]
    for axis in normal_axes:
        if radii[axis] > sd:
            b = (radii[axis] - sd) * impact_fraction
            for sign in spec["ordering_rules"]["candidate_marks"]["sign_order"]:
                template = mark_template(axis, sign)
                rows.append({"template":template,"class":"shell","impact_axis":axis,"impact_sign":sign,"impact_coordinate":fraction_text(sign*b),"b2":fraction_text(b*b),"reverse_template":reverse_template(template)})
    return rows

def build_candidate_marks(spec: Mapping[str, Any], vector: Mapping[str, Any], frames: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {fid: candidate_marks_for_frame(spec, vector, frame["axes"]) for fid, frame in frames.items()}

def registered_probability(spec: Mapping[str, Any], vector: Mapping[str, Any], b2: str) -> Fraction | None:
    registry = spec["probability_registry"][vector["source_registry_id"]]
    if b2 == registry["central_b2"]: return parse_fraction(registry["central_ann_probability"])
    if b2 == registry["shell_b2"]: return parse_fraction(registry["shell_ann_probability"])
    return None

def build_source_cases(spec: Mapping[str, Any], vector: Mapping[str, Any], frames: Mapping[str, Any], candidates: Mapping[str, list[dict[str, Any]]]) -> dict[str, str]:
    radii = [parse_fraction(x) for x in vector["metric_radii"]]
    sd = parse_fraction(vector["self_dual_radius"])
    speed = parse_fraction(vector["relative_speed"])
    global_flags = {
        "unresolved_amplitude": vector["amplitude_status"] != spec["validity"]["amplitude_valid_value"],
        "velocity": not interval_contains(speed, parse_fraction(vector["speed_min"]), parse_fraction(vector["speed_max"]), spec["validity"]["speed_interval"]["lower"], spec["validity"]["speed_interval"]["upper"]),
        "coupling_dilution": parse_fraction(vector["coupling"]) > parse_fraction(vector["coupling_max"]) or not bool(vector["dilute_flag"]),
    }
    out: dict[str, str] = {}
    for fid, frame in frames.items():
        flags = dict(global_flags)
        flags["unresolved_amplitude"] = flags["unresolved_amplitude"] or any(registered_probability(spec, vector, m["b2"]) is None for m in candidates[fid])
        flags["geometry"] = not all(radii[a] > sd for a in frame["axes"])
        flags["valid"] = True
        selected = next((case for case in spec["validity"]["precedence"] if flags.get(case, False)), None)
        if selected is None: fail("source_validity", "validity precedence did not select a case", fid)
        out[fid] = selected
    return out

def build_marks(spec: Mapping[str, Any], vector: Mapping[str, Any], frames: Mapping[str, Any], candidates: Mapping[str, list[dict[str, Any]]], cases: Mapping[str, str]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for fid in sorted(frames):
        if cases[fid] != "valid": continue
        p_mark = Fraction(1, len(candidates[fid]))
        for candidate in candidates[fid]:
            p_ann = registered_probability(spec, vector, candidate["b2"])
            if p_ann is None: fail("registry_probability", "valid mark lacks registered probability", fid)
            mid = mark_id(fid, candidate["template"])
            out[mid] = {"id":mid,"frame_id":fid,**candidate,"mark_probability":fraction_text(p_mark),"ann_probability":fraction_text(p_ann),"reverse_mark_id":mark_id(fid,candidate["reverse_template"]),"kind":"frame_local"}
    for reason in spec["alphabets"]["cemetery_reasons"]:
        mid = cemetery_mark_id(reason)
        out[mid] = {"id":mid,"frame_id":None,"template":reason,"class":"cemetery","impact_axis":None,"impact_sign":0,"impact_coordinate":"0/1","b2":"0/1","reverse_template":reason,"mark_probability":"1/1","ann_probability":"0/1","reverse_mark_id":mid,"kind":"cemetery"}
    return out

def build_states(spec: Mapping[str, Any], frames: Mapping[str, Any], candidates: Mapping[str, list[dict[str, Any]]], cases: Mapping[str, str]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for fid, frame in frames.items():
        for history in spec["alphabets"]["histories"]:
            pid = present_id(fid, history)
            pproj = projection(spec, "P", frame["axes"])
            out[pid] = {"id":pid,"class":"P","status":"physical","frame_id":fid,"frame":frame["axes"],"history":history,"origin_mark_template":None,"cemetery_reason":None,"physical_projection":pproj}
            if cases[fid] == "valid":
                for mark in candidates[fid]:
                    aid = products_id(fid, history, mark["template"])
                    out[aid] = {"id":aid,"class":"A","status":"physical","frame_id":fid,"frame":frame["axes"],"history":history,"origin_mark_template":mark["template"],"cemetery_reason":None,"physical_projection":projection(spec,"A",frame["axes"])}
            else:
                reason = cases[fid]
                kid = killed_id(fid, history, reason)
                out[kid] = {"id":kid,"class":"K","status":"killed","frame_id":fid,"frame":frame["axes"],"history":history,"origin_mark_template":None,"cemetery_reason":reason,"physical_projection":dict(pproj)}
    for reason in spec["alphabets"]["cemetery_reasons"]:
        sid = catalog_killed_id(reason)
        out[sid] = {"id":sid,"class":"KC","status":"catalog_killed","frame_id":None,"frame":None,"history":None,"origin_mark_template":None,"cemetery_reason":reason,"physical_projection":{"pair_present":False,"system_energy":"0/1","reservoir_energy":"0/1","work_energy":"0/1","global_charge_vector":zero_charge(spec),"frame":None}}
    return out

def hold_time(spec: Mapping[str, Any], vector: Mapping[str, Any], axes: Sequence[int]) -> Fraction:
    axis = axes[int(spec["frame_prior"]["velocity_role_index"])]
    return parse_fraction(vector["metric_radii"][axis]) * parse_fraction(vector["separation_fraction"]) / parse_fraction(vector["relative_speed"])

def build_schedules(spec: Mapping[str, Any], vector: Mapping[str, Any], states: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    phase_count = int(spec["schedule_rule"]["phase_count"])
    for sid, state in states.items():
        if state["status"] in spec["initial_law"]["excluded_status"]:
            out[sid] = {"state_id":sid,"kind":spec["schedule_rule"]["killed_schedule"],"clock_semantics":spec["schedule_rule"]["clock_semantics"],"scheduled_hold_time":None,"physical_time_unit":spec["schedule_rule"]["physical_time_unit"],"initial_countdown_phase":None,"phase_count":0,"event_at_phase":None,"phase_step":None,"schedule_exemption":"absorbing_killed","not_a_ctmc":True}
        else:
            hold = hold_time(spec, vector, state["frame"])
            out[sid] = {"state_id":sid,"kind":spec["schedule_rule"]["age_kind"],"clock_semantics":spec["schedule_rule"]["clock_semantics"],"scheduled_hold_time":fraction_text(hold),"physical_time_unit":spec["schedule_rule"]["physical_time_unit"],"initial_countdown_phase":int(spec["schedule_rule"]["initial_countdown_phase"]),"phase_count":phase_count,"event_at_phase":int(spec["schedule_rule"]["event_at_phase"]),"phase_step":fraction_text(hold/phase_count),"schedule_exemption":None,"not_a_ctmc":bool(spec["schedule_rule"]["not_a_ctmc"])}
    return out

def ledger(spec: Mapping[str, Any], channel: str) -> dict[str, Any]:
    source = spec["ledger_rule"][channel] if channel in {"annihilate","proposed_reverse_create"} else spec["ledger_rule"]["null"]
    return {key:(list(value) if isinstance(value,list) else value) for key,value in source.items()}

def make_event(spec: Mapping[str, Any], schedules: Mapping[str, Any], state: Mapping[str, Any], mid: str, channel: str, accepted: bool, probability: Fraction, destination: str, reverse_id: str | None, reverse_exemption: str | None, projection_changed: bool, history_changed: bool, source_case: str) -> dict[str, Any]:
    row = {"event_id":event_id(state["id"],channel,mid),"source_state_id":state["id"],"scheduled_hold_time":schedules[state["id"]]["scheduled_hold_time"],"physical_time_unit":schedules[state["id"]]["physical_time_unit"],"mark_id":mid,"channel_id":channel,"channel_kind":channel,"accepted":accepted,"probability":fraction_text(probability),"destination_state_id":destination,"reverse_event_id":reverse_id,"reverse_exemption":reverse_exemption,"physical_projection_changed":projection_changed,"history_changed":history_changed,"source_registry_case":source_case,"proposed_closure_label":spec["classification"]}
    row.update(ledger(spec, channel))
    return row

def build_events(spec: Mapping[str, Any], vector: Mapping[str, Any], states: Mapping[str, Any], marks: Mapping[str, Any], schedules: Mapping[str, Any], cases: Mapping[str, str]) -> dict[str, list[dict[str, Any]]]:
    by_frame: dict[str, list[dict[str, Any]]] = {}
    for mark in marks.values():
        if mark["kind"] == "frame_local": by_frame.setdefault(mark["frame_id"], []).append(mark)
    for rows in by_frame.values(): rows.sort(key=lambda x: x["id"])
    ratio = parse_fraction(vector["proposed_reverse_ratio"])
    channel_order = spec["ordering_rules"]["event_rows"]["channel_order"]
    out: dict[str, list[dict[str, Any]]] = {}
    for sid, state in states.items():
        row: list[dict[str, Any]] = []
        if state["class"] == "P":
            fid = state["frame_id"]
            case = cases[fid]
            if case == "valid":
                for mark in by_frame[fid]:
                    p_mark = parse_fraction(mark["mark_probability"]); p_ann = parse_fraction(mark["ann_probability"])
                    aid = products_id(fid, state["history"], mark["template"])
                    reverse = event_id(aid, "proposed_reverse_create", mark["reverse_mark_id"])
                    row.append(make_event(spec,schedules,state,mark["id"],"annihilate",True,p_mark*p_ann,aid,reverse,None,True,False,case))
                    next_history = mark["class"]
                    row.append(make_event(spec,schedules,state,mark["id"],"miss",False,p_mark*(1-p_ann),present_id(fid,next_history),None,"null_history",False,next_history != state["history"],case))
            else:
                mid = cemetery_mark_id(case)
                row = [make_event(spec,schedules,state,mid,"source_invalid",False,Fraction(1),killed_id(fid,state["history"],case),None,"epistemic_domain_exit",False,False,case)]
        elif state["class"] == "A":
            fid = state["frame_id"]
            origin = marks[mark_id(fid,state["origin_mark_template"])]
            reverse_mid = origin["reverse_mark_id"]
            probability = parse_fraction(origin["ann_probability"]) * ratio
            destination = present_id(fid,state["history"])
            forward_id = event_id(destination,"annihilate",origin["id"])
            row = [make_event(spec,schedules,state,reverse_mid,"proposed_reverse_create",True,probability,destination,forward_id,None,True,False,"valid"), make_event(spec,schedules,state,reverse_mid,"reverse_idle",False,1-probability,sid,None,"null_idle",False,False,"valid")]
        else:
            reason = state["cemetery_reason"]
            row = [make_event(spec,schedules,state,cemetery_mark_id(reason),"killed_absorb",False,Fraction(1),sid,None,"absorbing_killed",False,False,reason)]
        out[sid] = sorted(row, key=lambda event: (event["mark_id"], channel_order.index(event["channel_kind"])))
    return out

def build_initial_law(spec: Mapping[str, Any], states: Mapping[str, Any]) -> dict[str, str]:
    support = sorted(sid for sid,state in states.items() if state["status"] not in spec["initial_law"]["excluded_status"])
    weight = fraction_text(Fraction(1,len(support)))
    return {sid:weight for sid in support}

def execute_registered_constructor(
    spec: Mapping[str, Any], vector: Mapping[str, Any]
) -> dict[str, Any]:
    verify_constructor_spec(spec); verify_input(spec, vector)
    frames = build_frames(spec, vector)
    candidates = build_candidate_marks(spec, vector, frames)
    cases = build_source_cases(spec, vector, frames, candidates)
    marks = build_marks(spec, vector, frames, candidates, cases)
    states = build_states(spec, frames, candidates, cases)
    schedules = build_schedules(spec, vector, states)
    events = build_events(spec, vector, states, marks, schedules, cases)
    initial = build_initial_law(spec, states)
    return {"frames":frames,"candidate_marks":candidates,"source_cases":cases,"marks":marks,"states":states,"schedules":schedules,"events":events,"initial_law":initial,"s9_adjacent_generators":[dict(x) for x in spec["s9"]["adjacent_generators"]]}


def execute_constructor(
    spec: Mapping[str, Any], vector: Mapping[str, Any]
) -> dict[str, Any]:
    """Compatibility entrypoint for the fixed registered implementation."""
    return execute_registered_constructor(spec, vector)

def expanded_hash(spec: Mapping[str, Any], model: Mapping[str, Any]) -> str:
    digest = hashlib.sha256()
    for section in spec["ordering_rules"]["expanded_hash_sections"]:
        digest.update(section.encode("utf-8") + b"\n")
        value = model[section]
        if isinstance(value, Mapping):
            for key in sorted(value): digest.update(canonical_bytes([key,value[key]]) + b"\n")
        else:
            for record in value: digest.update(canonical_bytes(record) + b"\n")
    return digest.hexdigest()

def model_summary(model: Mapping[str, Any]) -> dict[str, Any]:
    classes: dict[str,int] = {}; cases: dict[str,int] = {}
    for state in model["states"].values(): classes[state["class"]] = classes.get(state["class"],0)+1
    for case in model["source_cases"].values(): cases[case] = cases.get(case,0)+1
    row_sums = [sum(parse_fraction(e["probability"]) for e in row) for row in model["events"].values()]
    positive = reverse = 0
    for row in model["events"].values():
        for event in row:
            if parse_fraction(event["probability"]) > 0 and event["accepted"] and event["channel_kind"] in {"annihilate","proposed_reverse_create"}:
                positive += 1; reverse += int(event["reverse_event_id"] is not None)
    return {"frames_total":len(model["frames"]),"valid_frames":cases.get("valid",0),"invalid_frames":len(model["frames"])-cases.get("valid",0),"marks_total":len(model["marks"]),"frame_local_marks":sum(m["kind"]=="frame_local" for m in model["marks"].values()),"states_total":len(model["states"]),"state_class_coverage":classes,"atoms_total":sum(len(row) for row in model["events"].values()),"states_with_stochastic_row":len(model["events"]),"states_with_unique_schedule":len(model["schedules"]),"positive_non_null_atoms":positive,"positive_non_null_atoms_with_declared_reverse":reverse,"min_row_sum":fraction_text(min(row_sums)),"max_row_sum":fraction_text(max(row_sums)),"source_case_counts":cases,"initial_support_size":len(model["initial_law"])}

def calibration_times(model: Mapping[str, Any], count: int = 5) -> list[str]:
    sources = sorted(sid for sid,state in model["states"].items() if state["class"] == "P" and model["source_cases"][state["frame_id"]] == "valid")
    if not sources: return []
    hold = parse_fraction(model["schedules"][sources[0]]["scheduled_hold_time"])
    return [fraction_text((i+1)*hold) for i in range(count)]
