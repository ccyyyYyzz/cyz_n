#!/usr/bin/env python3
"""Deterministic analytic/event controls for Brief 0017; no physical Monte Carlo."""
from __future__ import annotations
import argparse, hashlib, inspect, json, math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA="cyz-0017-worldsheet-near-encounter-controls-v1"
BRIEF="a0673f3eef4ecd329b45612b12c9efe0171d4da2"
OUTCOMES=("regular_first_entry","tie_cluster","ambiguous_tie","grazing_entry",
"degenerate_spatial_minimum","left_censored_active_episode","right_censored_no_entry",
"right_censored_active_episode","no_entry_proved","source_invalid",
"torus_branch_ambiguous","numerically_unresolved")
FORBIDDEN={"a","rank","sigma_3","normal_dimension","m","visible_rank",
"response_cell","requested_winner","target_rank"}
TOL=1e-12

def cbytes(o:Any)->bytes:return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def chash(o:Any)->str:return hashlib.sha256(cbytes(o)).hexdigest()
def read_json(p:Path)->Any:
    with p.open("r",encoding="utf-8",newline=None) as f:return json.load(f)
def write_json(p:Path,o:Any)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(cbytes(o)+b"\n")
def dot(x,y):return sum(a*b for a,b in zip(x,y))
def norm(x):return math.sqrt(max(0.,dot(x,x)))
def add(x,y):return [a+b for a,b in zip(x,y)]
def sub(x,y):return [a-b for a,b in zip(x,y)]
def scale(a,x):return [a*u for u in x]
def basis(n,i):v=[0.]*n;v[i]=1.;return v
def det3(m):return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
def gram(cols):return [[dot(a,b) for b in cols] for a in cols]
def eigsym(m):
    a=[r[:] for r in m];n=len(a)
    for _ in range(160):
        p,q,mx=0,1,0.
        for i in range(n):
            for j in range(i+1,n):
                if abs(a[i][j])>mx:p,q,mx=i,j,abs(a[i][j])
        if mx<1e-15:break
        ang=.5*math.atan2(2*a[p][q],a[q][q]-a[p][p]);c,s=math.cos(ang),math.sin(ang)
        app,aqq,apq=a[p][p],a[q][q],a[p][q]
        for k in range(n):
            if k in (p,q):continue
            x,y=a[k][p],a[k][q];a[k][p]=a[p][k]=c*x-s*y;a[k][q]=a[q][k]=s*x+c*y
        a[p][p]=c*c*app-2*s*c*apq+s*s*aqq;a[q][q]=s*s*app+2*s*c*apq+c*c*aqq;a[p][q]=a[q][p]=0.
    return sorted((max(0.,a[i][i]) for i in range(n)),reverse=True)
def svals(cols):return [math.sqrt(x) for x in eigsym(gram(cols))]
def qspan(cols,tol=1e-12):
    out=[]
    for col in cols:
        v=list(col)
        for q in out:v=sub(v,scale(dot(q,v),q))
        z=norm(v)
        if z>tol:out.append(scale(1/z,v))
    return out
def rank(cols):return len(qspan(cols))
def pnormal(cols,v):
    out=list(v)
    for q in qspan(cols):out=sub(out,scale(dot(q,out),q))
    return out
def wedge2(x,y):return max(0.,dot(x,x)*dot(y,y)-dot(x,y)**2)
def wedge3(x,y,z):return max(0.,det3(gram([x,y,z])))

def rank_record(i,p1,p2,u):
    cols=[[1.]+list(p1),[1.]+[-x for x in p2],[0.]+list(u)];q=add(p1,p2);r=rank(cols);sv=svals(cols)
    if r<3:sv=sv[:r]+[0.]*(3-r)
    lhs=det3(gram(cols));rhs=wedge2(q,u)+wedge3(p1,q,u)
    return {"id":i,"rank":r,"sigma_3":sv[2],"singular_values":sv,"p1":list(p1),"p2":list(p2),"q":q,"u":list(u),"gram_determinant":lhs,"exterior_identity_rhs":rhs,"identity_absolute_error":abs(lhs-rhs)}
def rank_controls():
    z=[0.]*8;e1,e2,e3=basis(8,0),basis(8,1),basis(8,2)
    rows=[rank_record("straight_opposite",z,z,e1),rank_record("excited_q_zero",scale(.2,e1),scale(-.2,e1),e2),rank_record("velocity_parallel_q",scale(.1,e1),scale(.2,e1),scale(.4,e1)),rank_record("full_rank",scale(.1,e1),scale(.2,e2),scale(.3,e3))]
    near=[rank_record(f"near_degenerate_{e:g}",z,scale(e,e1),e2) for e in (1e-1,1e-2,1e-3,1e-4)]
    assert [x["rank"] for x in rows]==[2,2,2,3] and all(x["rank"]==3 for x in near)
    assert all(x["identity_absolute_error"]<1e-12 for x in rows+near)
    assert all(near[i+1]["sigma_3"]<near[i]["sigma_3"] for i in range(3))
    return {"identity":"det(J^T J)=|q wedge u|^2+|p1 wedge q wedge u|^2","records":rows,"near_degenerate_rank_three_sequence":near}

def entry_controls():
    n=9;cols=[basis(n,0),basis(n,1),scale(-1,basis(n,2))]
    s=add(scale(.6,basis(n,2)),scale(.8,basis(n,3)));b=pnormal(cols,s);ell=sub(s,b)
    sc=scale(.8,basis(n,3));bc=pnormal(cols,sc);ellc=sub(sc,bc)
    r3=rank(cols);r2cols=[basis(n,0),basis(n,0),basis(n,1)];r2=rank(r2cols)
    actual=pnormal(r2cols,basis(n,2));fixed=[0.,0.,0.]+[0.]*6
    assert abs(norm(s)-1)<TOL and dot(s,cols[2])<0 and norm(ell)>0
    assert max(abs(dot(c,b)) for c in cols)<TOL and norm(sub(s,add(b,ell)))<TOL
    assert norm(sub(bc,sc))<TOL and norm(ellc)<TOL and (r3,r2)==(3,2)
    assert norm(actual)>1-TOL and norm(fixed)<TOL
    return {"entry":{"s":s,"b":b,"ell":ell,"s_dot_u":dot(s,cols[2]),"normal_residual":max(abs(dot(c,b)) for c in cols),"reconstruction_residual":norm(sub(s,add(b,ell))),"b_equals_s":norm(sub(b,s))<=TOL},"closest_approach":{"s":sc,"b":bc,"ell":ellc,"b_equals_s":True,"full_stationarity_residual":max(abs(dot(c,sc)) for c in cols)},"rank_strata":{"rank_three_normal_dimension":9-r3,"rank_two_normal_dimension":9-r2},"fixed_six_projector_mutation":{"actual_rank_two_projection_norm":norm(actual),"mutated_fixed_six_projection_norm":0.,"status":"REJECTED"}}

def hysteresis():
    b,li,rin,rout=.8,1.6,1.,1.2;tin=li-math.sqrt(rin*rin-b*b);tc=li;tout=li+math.sqrt(rout*rout-b*b)
    assert 0<tin<tc<tout
    return {"history_at_start":"armed","r_in":rin,"r_out":rout,"entry_time":tin,"closest_time":tc,"outer_exit_time":tout,"holding_time_is_entry_time":True,"closest_is_secondary_episode_mark":True,"rearm_only_after_outer_exit":True,"finite_window_no_entry":{"minimum_observed_radius":1.4,"horizon_complete":False,"outcome":"right_censored_no_entry"},"complete_period_no_entry":{"certified_global_lower_bound":1.3,"period_exhausted":True,"outcome":"no_entry_proved"}}
def outcome_ledger():
    w={x:Fraction(1,len(OUTCOMES)) for x in OUTCOMES};t=sum(w.values(),Fraction())
    assert t==1
    return {"scope":"synthetic event-semantics control; not physical outcome masses","weights":{k:f"{v.numerator}/{v.denominator}" for k,v in w.items()},"exact_total":"1/1","all_exceptional_mass_retained":True,"regular_events_not_renormalized":True}

def ugamma(s,z):
    if abs(s-round(s))<1e-12:
        n=round(s);return math.factorial(n-1)*math.exp(-z)*sum(z**k/math.factorial(k) for k in range(n))
    v=math.sqrt(math.pi)*math.erfc(math.sqrt(z));cur=.5
    while cur+1<=s+1e-12:v=cur*v+z**cur*math.exp(-z);cur+=1
    return v
def moment(p,y):return 2**(p+1)*ugamma(p+1,y/2)
def simpson(f,a,b,tol=1e-13,depth=18):
    fa,fb=f(a),f(b);c=(a+b)/2;fc=f(c);whole=(b-a)*(fa+4*fc+fb)/6
    def rec(a,b,fa,fb,fc,w,t,d):
        c=(a+b)/2;l=(a+c)/2;r=(c+b)/2;fl,fr=f(l),f(r);wl=(c-a)*(fa+4*fl+fc)/6;wr=(b-c)*(fc+4*fr+fb)/6;de=wl+wr-w
        return wl+wr+de/15 if d==0 or abs(de)<=15*t else rec(a,c,fa,fc,fl,wl,t/2,d-1)+rec(c,b,fc,fb,fr,wr,t/2,d-1)
    return rec(a,b,fa,fb,fc,whole,tol,depth)
def p_fixed(e):
    u=e*e
    return simpson(lambda y:0. if y==0 else math.exp(-y/2)*y**2.5*(moment(3.5,y)-y*moment(2.5,y))/2880,0,u)
def p_volume(e):
    u=e*e
    return simpson(lambda y:0. if y==0 else math.exp(-y/2)*y**3*(moment(4,y)-y*moment(3,y))/2880,0,u)/7
def hard_edge():
    c0=math.sqrt(math.pi/2)/48;c1=1/105
    rows=[{"epsilon":e,"fixed_point_probability":p_fixed(e),"fixed_point_ratio_to_C0_eps7":p_fixed(e)/(c0*e**7),"volume_biased_probability":p_volume(e),"volume_ratio_to_eps8_over_105":p_volume(e)/(c1*e**8)} for e in (.2,.1,.05)]
    assert abs(c0-.026110711194)<1e-12
    return {"fixed_point_iid_R8x2":{"ordered_wishart_density_constant":"1/2880","tail":"P[s_min<=eps]~C0 eps^7","C0_exact":"sqrt(pi/2)/48","C0_numeric":c0,"lower_rank_atom":0,"essential_infimum":0},"all_regular_roots_affine_volume_surrogate":{"radon_nikodym_weight":"s1*s2/E[s1*s2]","E_s1_s2":7,"tail":"P_volume[s_min<=eps]~eps^8/105","constant_exact":"1/105","constant_numeric":c1,"survival_tilt":"none"},"deterministic_quadrature":rows,"general_palm_power_rule":{"fixed_point_exponent":7,"conditional_mean_weight":"m(s)~w0*s^alpha*L(s), alpha>-7","event_exponent":"7+alpha","constant":"7*C*w0/((7+alpha)*E[W])","survival_factor_must_be_included":True},"curved_closest_counterexample":{"assumption":"p_g(0)~s_min^-1 while Morse determinant tends to a positive limit","conditional_local_exponent":6,"scope":"local closest-stationary intensity only; not first entry, episode-selected closest, or globally earliest event"},"prohibited_transfer":"no exponent is assigned to the physical first-entry law before constraint density, Jacobian, Morse/inward indicators, armed survival, and earliest-selection factors are audited jointly"}

def flow_control():
    modes=[{"k":1.,"x":.03,"y":-.02,"p":.015,"q":.01},{"k":2.,"x":-.01,"y":.007,"p":.012,"q":-.006}]
    energy=lambda ms:sum(r["p"]**2+r["q"]**2+r["k"]**2*(r["x"]**2+r["y"]**2) for r in ms)
    mom=lambda ms:sum(r["k"]*(r["p"]*r["y"]-r["q"]*r["x"]) for r in ms)
    e0,p0=energy(modes),mom(modes);de=dp=0.
    for t in (0,.1,.7,1.9,2*math.pi):
        out=[]
        for r in modes:
            k=r["k"];c,s=math.cos(k*t),math.sin(k*t);out.append({"k":k,"x":r["x"]*c+r["p"]*s/k,"y":r["y"]*c+r["q"]*s/k,"p":r["p"]*c-k*r["x"]*s,"q":r["q"]*c-k*r["y"]*s})
        de=max(de,abs(energy(out)-e0));dp=max(dp,abs(mom(out)-p0))
    assert de<1e-14 and dp<1e-14
    gb=sum(r["k"]*(math.hypot(r["x"],r["p"]/r["k"])+math.hypot(r["y"],r["q"]/r["k"])) for r in modes)
    return {"K":2,"basis":"real sine-cosine initial-data basis","maximum_energy_drift":de,"maximum_worldsheet_momentum_drift":dp,"time_uniform_triangle_graph_bound":gb,"scope":"deterministic flow control; not a microcanonical sample"}
def dependency():
    s={"torus_radii","winding_cycle","string_tension","string_length","fourier_cutoff_K","transverse_energy","target_momentum","level_matching","r_in","r_out","observation_horizon","episode_history","preparation_family"};e={"finite_mode_state","torus_metric","domain_metric_H","r_in","r_out","observation_horizon","episode_history","root_tolerances"};seen=sorted((s|e)&FORBIDDEN)
    assert not seen and "condition_on_rank" not in inspect.getsource(build_report)
    return {"registered_sampler_inputs":sorted(s),"registered_event_inputs":sorted(e),"forbidden_source_inputs":sorted(FORBIDDEN),"forbidden_seen":seen,"rank_and_sigma_computed_only_as_output_marks":True,"scope":"deterministic dependency control; not a universal hidden-variable theorem"}

def build_report():
    return {"schema_version":SCHEMA,"brief_commit":BRIEF,"scope":"exact analytic and event-semantics controls; no physical Monte Carlo executed","verdict":"inconclusive","rank_blind_finite_K_law":{"principal_measure":"normalized branch-volume microcanonical Liouville measure on the regular constrained finite-K phase manifold","event_map":"hysteretic first-entry stopping-time map with cluster-valued or exceptional outputs","full_law":"pushforward of the unconditioned source measure onto the disjoint regular/exceptional episode space","closest_approach":"secondary episode mark only","normal_object":"stratified Borel normal field with fiber dimension 9-a(j)","all_mass_retained":True,"physical_masses_computed":False},"dependency_audit":dependency(),"finite_mode_flow_control":flow_control(),"opposite_winding_rank_controls":rank_controls(),"first_entry_and_closest_control":entry_controls(),"hysteresis_control":hysteresis(),"outcome_mass_ledger_control":outcome_ledger(),"hard_edge_and_palm_controls":hard_edge(),"physical_result_ledger":{"normalized_regular_mass":"not computed","normalized_exceptional_mass":"not computed","rank_mixture":"not computed","event_conditioned_sigma_3":"not computed","joint_T_j_b_ell":"mathematically defined, not numerically identified","microcanonical_vs_gaussian_sensitivity":"not computed","K_regulator_sensitivity":"not computed","earliest_open_gate":"normalized constrained microcanonical sampler plus certified hysteretic first-entry root coverage on the preregistered finite-K source cell"}}
def main(argv:Sequence[str]|None=None)->int:
    ap=argparse.ArgumentParser(description="Run deterministic Brief 0017 analytic/event controls.");ap.add_argument("--output",type=Path,default=Path(__file__).with_name("analytic_controls.json"));ap.add_argument("--check",action="store_true",help="compare canonical parsed JSON, independent of line endings");a=ap.parse_args(argv);r=build_report()
    if a.check:
        if not a.output.exists():raise SystemExit("report missing")
        if cbytes(read_json(a.output))!=cbytes(r):raise SystemExit("report semantic mismatch")
        comp="canonical semantic JSON"
    else:write_json(a.output,r);comp="generated"
    print(json.dumps({"status":"PASS","comparison":comp,"output":str(a.output),"canonical_payload_sha256":chash(r),"rank_controls":8,"outcome_tags":len(OUTCOMES)},sort_keys=True,separators=(",",":")));return 0
if __name__=="__main__":raise SystemExit(main())
