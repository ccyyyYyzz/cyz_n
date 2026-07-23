#!/usr/bin/env python3
"""Generator-side implementation of the one registered Brief 0015 constructor.

This module is not a general interpreter for ``constructor_program``.  The
generator-side registration checks bind this implementation to one exact
canonical specification before this code can run.
"""
from __future__ import annotations
from generator_core import *
from typing import Any, Mapping, Sequence

# The exact specification digest selects this hand-audited implementation.
# ``constructor_program`` is registration metadata; these functions do not
# dispatch or interpret arbitrary operation nodes.
def build_frames(spec,v):
    a=v['frame_arity']; roles=spec['frame_prior']['role_catalog'][:a]
    return {frame_id(x):{'id':frame_id(x),'axes':list(x),'roles':list(roles),'arity':a} for x in itertools.permutations(spec['direction_set'],a)}

def candidate_marks(spec,v,axes):
    radii=list(map(parse_fraction,v['metric_radii'])); sd=parse_fraction(v['self_dual_radius']); f=parse_fraction(spec['mark_rule']['impact_coordinate_fraction'])
    out=[{'template':'central','class':'central','impact_axis':None,'impact_sign':0,'impact_coordinate':'0/1','b2':'0/1','reverse_template':'central'}]
    for axis in [i for i in spec['direction_set'] if i not in set(axes)]:
        if radii[axis]>sd:
            b=(radii[axis]-sd)*f
            for sign in spec['ordering_rules']['candidate_marks']['sign_order']:
                t=mark_template(axis,sign); out.append({'template':t,'class':'shell','impact_axis':axis,'impact_sign':sign,'impact_coordinate':frac(sign*b),'b2':frac(b*b),'reverse_template':reverse_template(t)})
    return out

def build_candidate_marks(spec,v,frames): return {fid:candidate_marks(spec,v,r['axes']) for fid,r in frames.items()}
def reg_prob(spec,v,b2):
    r=spec['probability_registry'][v['source_registry_id']]
    if b2==r['central_b2']: return parse_fraction(r['central_ann_probability'])
    if b2==r['shell_b2']: return parse_fraction(r['shell_ann_probability'])
    return None

def build_cases(spec,v,frames,cands):
    radii=list(map(parse_fraction,v['metric_radii'])); sd=parse_fraction(v['self_dual_radius']); speed=parse_fraction(v['relative_speed'])
    global_flags={'unresolved_amplitude':v['amplitude_status']!=spec['validity']['amplitude_valid_value'],'velocity':not interval_contains(speed,parse_fraction(v['speed_min']),parse_fraction(v['speed_max']),spec['validity']['speed_interval']['lower'],spec['validity']['speed_interval']['upper']),'coupling_dilution':parse_fraction(v['coupling'])>parse_fraction(v['coupling_max']) or not v['dilute_flag']}
    out={}
    for fid,fr in frames.items():
        flags=dict(global_flags); flags['unresolved_amplitude']|=any(reg_prob(spec,v,m['b2']) is None for m in cands[fid]); flags['geometry']=not all(radii[a]>sd for a in fr['axes']); flags['valid']=True
        out[fid]=next(x for x in spec['validity']['precedence'] if flags.get(x,False))
    return out

def build_marks(spec,v,frames,cands,cases):
    out={}
    for fid in sorted(frames):
        if cases[fid]!='valid': continue
        p=Fraction(1,len(cands[fid]))
        for m in cands[fid]:
            mid=mark_id(fid,m['template']); pa=reg_prob(spec,v,m['b2'])
            if pa is None: raise ConstructionError('valid mark lacks registered probability')
            out[mid]={'id':mid,'frame_id':fid,**m,'mark_probability':frac(p),'ann_probability':frac(pa),'reverse_mark_id':mark_id(fid,m['reverse_template']),'kind':'frame_local'}
    for reason in spec['alphabets']['cemetery_reasons']:
        mid=cemetery_mark_id(reason); out[mid]={'id':mid,'frame_id':None,'template':reason,'class':'cemetery','impact_axis':None,'impact_sign':0,'impact_coordinate':'0/1','b2':'0/1','reverse_template':reason,'mark_probability':'1/1','ann_probability':'0/1','reverse_mark_id':mid,'kind':'cemetery'}
    return out

def build_states(spec,frames,cands,cases):
    out={}
    for fid,fr in frames.items():
        for h in spec['alphabets']['histories']:
            pid=present_id(fid,h); pp=physical_projection(spec,'P',fr['axes']); out[pid]={'id':pid,'class':'P','status':'physical','frame_id':fid,'frame':fr['axes'],'history':h,'origin_mark_template':None,'cemetery_reason':None,'physical_projection':pp}
            if cases[fid]=='valid':
                for m in cands[fid]:
                    aid=products_id(fid,h,m['template']); out[aid]={'id':aid,'class':'A','status':'physical','frame_id':fid,'frame':fr['axes'],'history':h,'origin_mark_template':m['template'],'cemetery_reason':None,'physical_projection':physical_projection(spec,'A',fr['axes'])}
            else:
                r=cases[fid]; kid=killed_id(fid,h,r); out[kid]={'id':kid,'class':'K','status':'killed','frame_id':fid,'frame':fr['axes'],'history':h,'origin_mark_template':None,'cemetery_reason':r,'physical_projection':dict(pp)}
    for r in spec['alphabets']['cemetery_reasons']:
        sid=catalog_killed_id(r); out[sid]={'id':sid,'class':'KC','status':'catalog_killed','frame_id':None,'frame':None,'history':None,'origin_mark_template':None,'cemetery_reason':r,'physical_projection':{'pair_present':False,'system_energy':'0/1','reservoir_energy':'0/1','work_energy':'0/1','global_charge_vector':zero_charge(spec),'frame':None}}
    return out

def hold(spec,v,axes):
    axis=axes[spec['frame_prior']['velocity_role_index']]
    return parse_fraction(v['metric_radii'][axis])*parse_fraction(v['separation_fraction'])/parse_fraction(v['relative_speed'])
def build_schedules(spec,v,states):
    out={}; phases=spec['schedule_rule']['phase_count']
    for sid,s in states.items():
        if s['status'] in spec['initial_law']['excluded_status']:
            out[sid]={'state_id':sid,'kind':spec['schedule_rule']['killed_schedule'],'clock_semantics':spec['schedule_rule']['clock_semantics'],'scheduled_hold_time':None,'physical_time_unit':spec['schedule_rule']['physical_time_unit'],'initial_countdown_phase':None,'phase_count':0,'event_at_phase':None,'phase_step':None,'schedule_exemption':'absorbing_killed','not_a_ctmc':True}
        else:
            h=hold(spec,v,s['frame']); out[sid]={'state_id':sid,'kind':spec['schedule_rule']['age_kind'],'clock_semantics':spec['schedule_rule']['clock_semantics'],'scheduled_hold_time':frac(h),'physical_time_unit':spec['schedule_rule']['physical_time_unit'],'initial_countdown_phase':spec['schedule_rule']['initial_countdown_phase'],'phase_count':phases,'event_at_phase':spec['schedule_rule']['event_at_phase'],'phase_step':frac(h/phases),'schedule_exemption':None,'not_a_ctmc':spec['schedule_rule']['not_a_ctmc']}
    return out

def ledger(spec,ch):
    src=spec['ledger_rule'][ch] if ch in ('annihilate','proposed_reverse_create') else spec['ledger_rule']['null']
    return {k:(list(v) if isinstance(v,list) else v) for k,v in src.items()}
def event(spec,schedules,state,mid,ch,accepted,p,dest,rev,exempt,phys,hist,case):
    r={'event_id':event_id(state['id'],ch,mid),'source_state_id':state['id'],'scheduled_hold_time':schedules[state['id']]['scheduled_hold_time'],'physical_time_unit':schedules[state['id']]['physical_time_unit'],'mark_id':mid,'channel_id':ch,'channel_kind':ch,'accepted':accepted,'probability':frac(p),'destination_state_id':dest,'reverse_event_id':rev,'reverse_exemption':exempt,'physical_projection_changed':phys,'history_changed':hist,'source_registry_case':case,'proposed_closure_label':spec['classification']}; r.update(ledger(spec,ch)); return r

def build_events(spec,v,states,marks,schedules,cases):
    byframe={}
    for m in marks.values():
        if m['kind']=='frame_local': byframe.setdefault(m['frame_id'],[]).append(m)
    for x in byframe.values(): x.sort(key=lambda m:m['id'])
    ratio=parse_fraction(v['proposed_reverse_ratio']); out={}
    for sid,s in states.items():
        row=[]
        if s['class']=='P':
            fid=s['frame_id']; case=cases[fid]
            if case=='valid':
                for m in byframe[fid]:
                    pm,pa=parse_fraction(m['mark_probability']),parse_fraction(m['ann_probability']); aid=products_id(fid,s['history'],m['template']); rid=event_id(aid,'proposed_reverse_create',m['reverse_mark_id'])
                    row.append(event(spec,schedules,s,m['id'],'annihilate',True,pm*pa,aid,rid,None,True,False,case))
                    nh=m['class']; row.append(event(spec,schedules,s,m['id'],'miss',False,pm*(1-pa),present_id(fid,nh),None,'null_history',False,nh!=s['history'],case))
            else:
                mid=cemetery_mark_id(case); row=[event(spec,schedules,s,mid,'source_invalid',False,Fraction(1),killed_id(fid,s['history'],case),None,'epistemic_domain_exit',False,False,case)]
        elif s['class']=='A':
            fid=s['frame_id']; om=marks[mark_id(fid,s['origin_mark_template'])]; rm=om['reverse_mark_id']; p=parse_fraction(om['ann_probability'])*ratio; dest=present_id(fid,s['history']); fid_ev=event_id(dest,'annihilate',om['id'])
            row=[event(spec,schedules,s,rm,'proposed_reverse_create',True,p,dest,fid_ev,None,True,False,'valid'),event(spec,schedules,s,rm,'reverse_idle',False,1-p,sid,None,'null_idle',False,False,'valid')]
        else:
            r=s['cemetery_reason']; row=[event(spec,schedules,s,cemetery_mark_id(r),'killed_absorb',False,Fraction(1),sid,None,'absorbing_killed',False,False,r)]
        out[sid]=sorted(row,key=lambda e:(e['mark_id'],spec['ordering_rules']['event_rows']['channel_order'].index(e['channel_kind'])))
    return out

def build_initial(spec,states):
    support=sorted(sid for sid,s in states.items() if s['status'] not in spec['initial_law']['excluded_status']); w=frac(Fraction(1,len(support))); return {sid:w for sid in support}

def execute_registered_constructor(spec,v):
    validate_spec(spec); validate_input(spec,v)
    frames=build_frames(spec,v); cands=build_candidate_marks(spec,v,frames); cases=build_cases(spec,v,frames,cands); marks=build_marks(spec,v,frames,cands,cases); states=build_states(spec,frames,cands,cases); schedules=build_schedules(spec,v,states); events=build_events(spec,v,states,marks,schedules,cases); initial=build_initial(spec,states)
    return {'frames':frames,'candidate_marks':cands,'source_cases':cases,'marks':marks,'states':states,'schedules':schedules,'events':events,'initial_law':initial,'s9_adjacent_generators':[dict(x) for x in spec['s9']['adjacent_generators']]}

def expanded_hash(spec,model):
    h=hashlib.sha256()
    for sec in spec['ordering_rules']['expanded_hash_sections']:
        h.update(sec.encode()+b'\n'); value=model[sec]
        if isinstance(value,Mapping):
            for k in sorted(value): h.update(canonical_bytes([k,value[k]])+b'\n')
        else:
            for x in value: h.update(canonical_bytes(x)+b'\n')
    return h.hexdigest()
def summary(model):
    rows=[sum(parse_fraction(e['probability']) for e in r) for r in model['events'].values()]; classes={}; cases={}; pos=rev=0
    for s in model['states'].values(): classes[s['class']]=classes.get(s['class'],0)+1
    for c in model['source_cases'].values(): cases[c]=cases.get(c,0)+1
    for r in model['events'].values():
        for e in r:
            if parse_fraction(e['probability'])>0 and e['accepted'] and e['channel_kind'] in spec_channel_nonnull(model): pos+=1; rev+=bool(e['reverse_event_id'])
    return {'frames_total':len(model['frames']),'valid_frames':cases.get('valid',0),'invalid_frames':len(model['frames'])-cases.get('valid',0),'marks_total':len(model['marks']),'frame_local_marks':sum(m['kind']=='frame_local' for m in model['marks'].values()),'states_total':len(model['states']),'state_class_coverage':classes,'atoms_total':sum(map(len,model['events'].values())),'states_with_stochastic_row':len(model['events']),'states_with_unique_schedule':len(model['schedules']),'positive_non_null_atoms':pos,'positive_non_null_atoms_with_declared_reverse':rev,'min_row_sum':frac(min(rows)),'max_row_sum':frac(max(rows)),'source_case_counts':cases,'initial_support_size':len(model['initial_law'])}
def spec_channel_nonnull(model): return {'annihilate','proposed_reverse_create'}
def calibration_times(model,n=5):
    p=sorted(sid for sid,s in model['states'].items() if s['class']=='P' and model['source_cases'][s['frame_id']]=='valid')
    if not p:return []
    h=parse_fraction(model['schedules'][p[0]]['scheduled_hold_time']); return [frac((i+1)*h) for i in range(n)]
