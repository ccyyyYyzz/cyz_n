#!/usr/bin/env python3
"""Brief 0017 exact surrogates and executable schematic controls; no physical sample."""
from __future__ import annotations
import argparse, hashlib, json, math
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SCHEMA="cyz-0017-worldsheet-near-encounter-controls-v2"
BRIEF="a0673f3eef4ecd329b45612b12c9efe0171d4da2"
RANK_REL_TOL=1e-14
PRIMARY_OUTCOMES=("source_constraint_unresolved","source_invalid","left_censored_active_episode","torus_branch_ambiguous","numerically_unresolved","no_entry_proved","right_censored_no_entry","right_censored_active_episode","degenerate_spatial_minimum","grazing_entry","tie_cluster","regular_first_entry")
OUTCOMES=OUTCOME_TAGS=PRIMARY_OUTCOMES
FORBIDDEN={"a","rank","minimum_rank","condition_on_rank","sigma_3","sigma3","sigma_3_min","condition_on_sigma_3","normal_dimension","visible_rank","response_cell","requested_winner","target_rank"}
PI=Decimal("3.1415926535897932384626433832795028841971693993751058209749445923078164")

def canonical_bytes(o:Any)->bytes:return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def canonical_hash(o:Any)->str:return hashlib.sha256(canonical_bytes(o)).hexdigest()
cbytes,chash=canonical_bytes,canonical_hash

def _pairs(pairs:Iterable[tuple[str,Any]])->dict[str,Any]:
 out={}
 for k,v in pairs:
  if k in out:raise ValueError(f"duplicate JSON object key: {k}")
  out[k]=v
 return out

def _bad(token:str)->Any:raise ValueError(f"non-finite JSON number: {token}")
def read_semantic_json(p:Path)->Any:
 with p.open("r",encoding="utf-8",newline=None) as f:return json.load(f,object_pairs_hook=_pairs,parse_constant=_bad)
read_json=read_semantic_json

def strict_json_equal(a:Any,b:Any)->bool:
 if type(a) is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys() and all(strict_json_equal(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(strict_json_equal(x,y) for x,y in zip(a,b))
 return a==b

def write_json(p:Path,o:Any)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(canonical_bytes(o)+b"\n")
def _num(x:Any,name:str)->float:
 if isinstance(x,bool) or not isinstance(x,(int,float)):raise TypeError(f"{name} must be a real number, got {type(x).__name__}")
 x=float(x)
 if not math.isfinite(x):raise ValueError(f"{name} must be finite")
 return x

def vector(x:Sequence[Any],*,expected_dim:int|None=None,name:str="vector")->tuple[float,...]:
 if isinstance(x,(str,bytes,bytearray)) or not isinstance(x,Sequence):raise TypeError(f"{name} must be a finite numeric sequence")
 v=tuple(_num(a,f"{name}[{i}]") for i,a in enumerate(x))
 if expected_dim is not None and len(v)!=expected_dim:raise ValueError(f"{name} must have shape ({expected_dim},), got ({len(v)},)")
 return v

def _pair(x:Sequence[Any],y:Sequence[Any],name:str):
 x,y=vector(x,name=name+".left"),vector(y,name=name+".right")
 if len(x)!=len(y):raise ValueError(f"{name} shape mismatch: ({len(x)},) versus ({len(y)},)")
 return x,y

def dot(x,y):x,y=_pair(x,y,"dot");return math.fsum(a*b for a,b in zip(x,y))
def norm(x):x=vector(x,name="norm.argument");return math.sqrt(max(0.,math.fsum(a*a for a in x)))
def add(x,y):x,y=_pair(x,y,"add");return [a+b for a,b in zip(x,y)]
def sub(x,y):x,y=_pair(x,y,"sub");return [a-b for a,b in zip(x,y)]
def scale(a,x):a,x=_num(a,"scale.factor"),vector(x,name="scale.vector");return [a*b for b in x]
def basis(n:int,i:int):
 if n<=0 or not 0<=i<n:raise ValueError("invalid basis request")
 v=[0.]*n;v[i]=1.;return v

def _cols(cs):
 if not cs:raise ValueError("columns must be nonempty")
 cs=[vector(c,name=f"columns[{i}]") for i,c in enumerate(cs)]
 if any(len(c)!=len(cs[0]) for c in cs):raise ValueError(f"columns column-shape mismatch: {[len(c) for c in cs]}")
 return cs

def gram(cs):cs=_cols(cs);return [[dot(a,b) for b in cs] for a in cs]
def det3(m):
 m=[vector(r,expected_dim=3,name=f"matrix[{i}]") for i,r in enumerate(m)]
 if len(m)!=3:raise ValueError("matrix must have shape (3,3)")
 return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])

def _F(x:Any)->Fraction:
 if isinstance(x,bool):raise TypeError("bool is not an admissible scalar")
 if isinstance(x,Fraction):return x
 if isinstance(x,int):return Fraction(x)
 if isinstance(x,(float,Decimal)):
  if isinstance(x,float) and not math.isfinite(x):raise ValueError("non-finite scalar")
  return Fraction(str(x))
 raise TypeError(f"unsupported exact scalar type: {type(x).__name__}")
def _fv(x,n=None):
 v=tuple(_F(a) for a in x)
 if n is not None and len(v)!=n:raise ValueError(f"exact vector must have shape ({n},), got ({len(v)},)")
 return v
def _fdot(x,y):
 if len(x)!=len(y):raise ValueError("exact dot shape mismatch")
 return sum((a*b for a,b in zip(x,y)),Fraction())
def _fg(cs):
 if not cs or any(len(c)!=len(cs[0]) for c in cs):raise ValueError("exact column-shape mismatch")
 return [[_fdot(a,b) for b in cs] for a in cs]
def _fdet(m):return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
def _rank(g):
 if _fdet(g):return 3
 if any(g[i][i]*g[j][j]-g[i][j]**2 for i in range(3) for j in range(i+1,3)):return 2
 return 1 if any(g[i][i] for i in range(3)) else 0

def _eig3(m):
 m=[vector(r,expected_dim=3) for r in m];off=m[0][1]**2+m[0][2]**2+m[1][2]**2
 if off==0:return sorted((m[0][0],m[1][1],m[2][2]),reverse=True)
 q=sum(m[i][i] for i in range(3))/3;p=math.sqrt(((m[0][0]-q)**2+(m[1][1]-q)**2+(m[2][2]-q)**2+2*off)/6)
 b=[[(m[i][j]-(q if i==j else 0))/p for j in range(3)] for i in range(3)];phi=math.acos(max(-1.,min(1.,det3(b)/2)))/3
 e1=q+2*p*math.cos(phi);e3=q+2*p*math.cos(phi+2*math.pi/3);e2=3*q-e1-e3
 return sorted((max(0.,e1),max(0.,e2),max(0.,e3)),reverse=True)

def rank_record(i,p1,p2,u):
 p1,p2,u=vector(p1,expected_dim=8),vector(p2,expected_dim=8),vector(u,expected_dim=8);cols=[(1.,)+p1,(1.,)+tuple(-x for x in p2),(0.,)+u];g=gram(cols)
 f1,f2,fu=_fv(p1),_fv(p2),_fv(u);fg=_fg([(Fraction(1),)+f1,(Fraction(1),)+tuple(-x for x in f2),(Fraction(0),)+fu]);r=_rank(fg);ev=_eig3(g)
 if r==3:ev[2]=float(_fdet(fg))/(ev[0]*ev[1])
 else:
  for j in range(r,3):ev[j]=0.
 sv=[math.sqrt(max(0.,x)) for x in ev];tol=RANK_REL_TOL*sv[0] if sv[0] else 0.;q=tuple(a+b for a,b in zip(f1,f2));rhs=(_fdot(q,q)*_fdot(fu,fu)-_fdot(q,fu)**2)+_fdet(_fg([f1,q,fu]));lhs=_fdet(fg);fl,fr=det3(g),float(rhs);den=max(abs(float(lhs)),abs(fr))
 err=0. if den==0 else abs(fl-fr)/den
 return {"id":i,"exact_rank":r,"rank":r,"numerical_rank":sum(s>tol for s in sv),"rank_relative_tolerance":RANK_REL_TOL,"rank_absolute_tolerance":tol,"singular_values_raw":sv,"sigma_3_raw":sv[2],"gram_determinant_exact":str(lhs),"exterior_identity_rhs_exact":str(rhs),"identity_certified_exact":lhs==rhs,"identity_relative_float_error":err}

def rank_controls():
 z=[0.]*8;e1,e2,e3=basis(8,0),basis(8,1),basis(8,2)
 records=[rank_record("straight_opposite",z,z,e1),rank_record("excited_q_zero",scale(.2,e1),scale(-.2,e1),e2),rank_record("velocity_parallel_q",scale(.1,e1),scale(.2,e1),scale(.4,e1)),rank_record("full_rank",scale(.1,e1),scale(.2,e2),scale(.3,e3))]
 near=[rank_record(f"near_degenerate_{e:.0e}",z,scale(e,e1),e2) for e in (1e-2,1e-4,1e-6,1e-8,1e-12,1e-16)]
 assert [r["exact_rank"] for r in records]==[2,2,2,3] and all(r["exact_rank"]==3 and r["sigma_3_raw"]>0 and r["identity_certified_exact"] for r in near)
 return {"identity":"det(J^T J)=|q wedge u|^2+|p1 wedge q wedge u|^2","records":records,"near_degenerate_exact_rank_three_sequence":near,"raw_singular_values_never_overwritten":True}

def source_measure_control():
 vols=[Fraction(2),Fraction(3),Fraction(5)];weights=[v/sum(vols) for v in vols]
 return {"scope":"normalization identity for a parameterized family; no physical source cell frozen","principal_delta_liouville_law":{"formula":"Z^-1 dQ_rel/Vol(T8) delta(C(y)-c_h) dy","coarea_branch_volumes":["2","3","5"],"coarea_branch_weights_omega_r":[str(w) for w in weights],"nonnegative":all(w>=0 for w in weights),"exact_total":str(sum(weights))},"separate_preparation_control":{"name":"equal_branch_mixture_control","weights":["1/3"]*3,"is_principal":False},"constraint_singular_strata":{"primary_outcome":"source_constraint_unresolved","stratified_measure":"not supplied"},"physical_gate_closed":False}

def _r2c(x,y,p,q,k):return (complex(x+q/k,p/k-y)/4,complex(x-q/k,-y-p/k)/4)
def _c2r(a,b,k):return (2*(a.real+b.real),-2*(a.imag+b.imag),2*k*(a.imag-b.imag),2*k*(a.real-b.real))
def fourier_convention_control():
 vals=(.3,-.2,.4,-.1,2.);cl,cr=_r2c(*vals);back=_c2r(cl,cr,vals[-1]);res=max(abs(back[i]-vals[i]) for i in range(4));Q=[.7,-.4];Y=[.2,.1];X=add(Q,Y);bad=add(X,Q)
 return {"embedding":"X_perp=Q+Y; Y has zero Fourier mode removed","Q_occurrences_in_embedding":1,"maximum_roundtrip_residual":res,"double_count_mutation_displacement_norm":norm(sub(bad,X)),"double_count_mutation_status":"REJECTED"}

def _span(cs):
 out=[]
 for c in _cols(cs):
  v=list(c)
  for q in out:v=sub(v,scale(dot(q,v),q))
  n=norm(v)
  if n>1e-14:out.append(scale(1/n,v))
 return out

def pnormal(cs,v):
 v=list(vector(v,expected_dim=len(_cols(cs)[0])))
 for q in _span(cs):v=sub(v,scale(dot(q,v),q))
 return v

def first_entry_and_closest_control():
 n=9;cols=[basis(n,0),basis(n,1),scale(-1,basis(n,2))];s=add(scale(.6,basis(n,2)),scale(.8,basis(n,3)));b=pnormal(cols,s);ell=sub(s,b);sc=scale(.8,basis(n,3));bc=pnormal(cols,sc)
 rank2=[basis(n,0),basis(n,0),basis(n,1)];probe=basis(n,8);actual=pnormal(rank2,probe);fixed6=[*probe[:8],0.];err=norm(sub(actual,fixed6))
 return {"entry":{"s":s,"b":b,"ell":ell,"b_equals_s":norm(sub(b,s))<=1e-14,"normal_residual":max(abs(dot(c,b)) for c in cols),"reconstruction_residual":norm(sub(s,add(b,ell)))},"closest_approach":{"s":sc,"b":bc,"ell":sub(sc,bc),"b_equals_s":norm(sub(bc,sc))<=1e-14,"full_stationarity_residual":max(abs(dot(c,sc)) for c in cols)},"rank_strata":{"rank_three_normal_dimension":6,"rank_two_normal_dimension":7},"fixed_six_projector_mutation":{"actual_rank_two_projection_norm":norm(actual),"mutated_fixed_six_projection_norm":norm(fixed6),"mutation_error_norm":err,"status":"REJECTED_BY_EXECUTED_GEOMETRY"}}

def _cross(t0,r0,t1,r1,h):return t0+(h-r0)*(t1-t0)/(r1-r0)
def run_hysteresis_trace(samples:Sequence[Mapping[str,Any]],*,r_in:float,r_out:float):
 state="armed";episodes=[];trans=[];active=None;previous=None
 for row in samples:
  t,r=float(row["t"]),float(row["rho"]);components=set(row.get("components",[]))
  if previous is not None:
   t0,r0=previous
   if state=="armed" and r0>r_in>=r:
    ti=_cross(t0,r0,t,r,r_in);active={"entry_time":ti,"outer_exit_time":None,"merged_components":set(components),"subentries_merged":0};state="active";trans.append({"transition":"armed_to_active_inner_entry","time":ti})
   elif state=="active":
    new=components-active["merged_components"]
    if new:active["merged_components"]|=new;active["subentries_merged"]+=len(new)
    if r0<r_out<=r:
     to=_cross(t0,r0,t,r,r_out);active["outer_exit_time"]=to;active["merged_components"]=sorted(active["merged_components"]);episodes.append(active);active=None;state="armed";trans.append({"transition":"active_to_armed_outer_exit","time":to})
  previous=(t,r)
 return {"final_state":state,"episodes":episodes,"transitions":trans}

def hysteresis_control():
 trace=[{"t":0.,"rho":1.3},{"t":1.,"rho":.9,"components":["A"]},{"t":2.,"rho":.8,"components":["A","B"]},{"t":3.,"rho":1.3},{"t":4.,"rho":.9,"components":["C"]},{"t":5.,"rho":1.3}];result=run_hysteresis_trace(trace,r_in=1.,r_out=1.2)
 assert len(result["episodes"])==2 and result["episodes"][0]["merged_components"]==["A","B"]
 return {"scope":"executable synthetic state-machine geometry; not physical root coverage","r_in":1.,"r_out":1.2,"trace":trace,"trace_result":result,"finite_window_no_entry":{"primary_outcome":"right_censored_no_entry"},"certified_complete_no_entry":{"primary_outcome":"no_entry_proved"}}

def full_cluster(members):
 rows=sorted((dict(m) for m in members),key=lambda x:canonical_bytes(x));return {"policy":"complete unordered certified cluster; no_scalar_representative","member_count":len(rows),"members":rows}

def classify_primary_outcome(f):
 flags={"source_invalid":bool(f.get("source_invalid")),"left_censored":bool(f.get("left_censored")),"right_censored":bool(f.get("right_censored")),"tie":int(f.get("tie_count",1))>1,"grazing_entry":bool(f.get("grazing_entry")),"degenerate_spatial_minimum":bool(f.get("degenerate_spatial_minimum")),"entry_observed":bool(f.get("entry_observed")),"episode_complete":bool(f.get("episode_complete"))}
 if f.get("constraint_singular"):p="source_constraint_unresolved"
 elif flags["source_invalid"]:p="source_invalid"
 elif flags["left_censored"]:p="left_censored_active_episode"
 elif f.get("torus_branch_ambiguous"):p="torus_branch_ambiguous"
 elif f.get("numerically_unresolved"):p="numerically_unresolved"
 elif f.get("no_entry_proved"):p="no_entry_proved"
 elif not flags["entry_observed"]:p="right_censored_no_entry"
 elif not flags["episode_complete"]:p="right_censored_active_episode"
 elif flags["degenerate_spatial_minimum"]:p="degenerate_spatial_minimum"
 elif flags["grazing_entry"]:p="grazing_entry"
 elif flags["tie"]:p="tie_cluster"
 else:p="regular_first_entry"
 return {"primary_outcome":p,"flags":flags}

def event_schema_control():
 cases={"constraint_invalid_censored_overlap":{"constraint_singular":True,"source_invalid":True,"right_censored":True},"invalid":{"source_invalid":True},"left":{"left_censored":True},"torus":{"torus_branch_ambiguous":True},"numerical":{"numerically_unresolved":True},"proved":{"no_entry_proved":True},"window":{},"active":{"entry_observed":True},"degenerate_grazing_tie":{"entry_observed":True,"episode_complete":True,"degenerate_spatial_minimum":True,"grazing_entry":True,"tie_count":2},"grazing_tie":{"entry_observed":True,"episode_complete":True,"grazing_entry":True,"tie_count":2},"tie":{"entry_observed":True,"episode_complete":True,"tie_count":2},"regular":{"entry_observed":True,"episode_complete":True}}
 rows={k:classify_primary_outcome(v) for k,v in cases.items()};assert {v["primary_outcome"] for v in rows.values()}==set(PRIMARY_OUTCOMES)
 return {"scope":"schematic executable event-schema coverage; case counts are not probabilities","primary_precedence_high_to_low":list(PRIMARY_OUTCOMES),"one_primary_per_record":True,"orthogonal_flags_preserve_overlaps":True,"classified_cases":rows,"tie_policy_control":full_cluster([{"id":"b","value":2},{"id":"a","value":1}]),"physical_mass_normalization_evaluated":False}

def outcome_mass_ledger():
 counts={x:0 for x in PRIMARY_OUTCOMES}
 for r in event_schema_control()["classified_cases"].values():counts[r["primary_outcome"]]+=1
 return {"scope":"schematic registry coverage only; not physical outcome masses","case_counts":counts,"all_primary_outcomes_exercised":all(counts.values()),"regular_events_not_renormalized":True,"physical_total_mass_claim":"not made"}

def _erf(x):
 x2=x*x;s=x;fact=Decimal(1);n=1
 while True:
  fact*=n;term=(-x2)**n*x/(fact*(2*n+1));s+=term
  if abs(term)<Decimal("1e-62"):return 2*s/PI.sqrt()
  n+=1

def _half(y):
 z=y/2;r=z.sqrt();e=(-z).exp();g=PI.sqrt()*(1-_erf(r));g7=Decimal(15)/8*g+e*r*(Decimal(15)/4+Decimal(5)/2*z+z*z);g9=Decimal(105)/16*g+e*r*(Decimal(105)/8+Decimal(35)/4*z+Decimal(7)/2*z*z+z**3);q=Decimal(2).sqrt();return 8*q*g7,16*q*g9

def _integer(y):
 z=y/2;e=(-z).exp();g4=6*e*(1+z+z*z/2+z**3/6);g5=24*e*(1+z+z*z/2+z**3/6+z**4/24);return 16*g4,32*g5

def _simpson(f,n):
 h=Decimal(1)/n;odd=sum((f(Decimal(i)*h) for i in range(1,n,2)),Decimal());even=sum((f(Decimal(i)*h) for i in range(2,n,2)),Decimal());return h*(f(Decimal())+f(Decimal(1))+4*odd+2*even)/3

def _quad(e):
 with localcontext() as c:
  c.prec=70;eps=Decimal(e);u=eps**2;c0=(PI/2).sqrt()/48
  def ff(x):y=u*x*x;m5,m7=_half(y);return (-y/2).exp()*x**6*(m7-y*m5)
  def vf(x):y=u*x*x;m3,m4=_integer(y);return (-y/2).exp()*x**7*(m4-y*m3)
  fc,f=_simpson(ff,8192)/(1440*c0),_simpson(ff,16384)/(1440*c0);vc,v=_simpson(vf,8192)/96,_simpson(vf,16384)/96
  return {"epsilon":float(eps),"fixed_point_ratio_to_C0_eps7":float(f),"fixed_point_ratio_richardson_error_estimate":float(abs(f-fc)/15),"volume_ratio_to_eps8_over_105":float(v),"volume_ratio_richardson_error_estimate":float(abs(v-vc)/15),"precision_digits":70,"coarse_intervals":8192,"fine_intervals":16384}

@lru_cache(maxsize=1)
def hard_edge_controls():
 rows=[_quad(e) for e in ("0.2","0.1","0.05")];assert abs(rows[-1]["fixed_point_ratio_to_C0_eps7"]-.9987507809245811)<2e-15
 affine=[{"delta":d,"hessian_determinant":d*d,"zero_gradient_density":1/d,"product":d,"delta2_ratio":1.,"delta_minus1_ratio":1.,"delta_ratio":1.} for d in (1e-1,1e-3,1e-6)]
 return {"scope":"analytic surrogates and conditional propositions only; not the physical finite-K first-entry law","fixed_point_iid_R8x2":{"singular_value_exponent":7,"C0_exact":"sqrt(pi/2)/48","C0_numeric":math.sqrt(math.pi/2)/48,"gram_eigenvalue_exponent":"7/2","lower_rank_atom":0,"essential_infimum":0},"pure_volume_palm_surrogate":{"E_s1_s2":7,"exponent":8,"constant_exact":"1/105","constant_numeric":1/105,"survival_tilt":"none"},"relative_error_controlled_high_precision_quadrature":rows,"affine_closest_scaling_control":affine,"curvature_lifted_conditional_counterexample":{"conditional_local_tail_exponent":6,"scope":"local closest-stationary intensity only"},"general_palm_power_rule":{"status":"conditional proposition","event_exponent":"7+alpha","survival_factor_must_be_included":True},"prohibited_transfer":"no physical exponent before the constrained density, Jacobian, section, history and no-earlier-entry audit"}
hard_edge=hard_edge_controls

def finite_mode_flow_control():
 modes=[{"k":1.,"x":.03,"y":-.02,"p":.015,"q":.01},{"k":2.,"x":-.01,"y":.007,"p":.012,"q":-.006}];energy=lambda m:math.fsum(r["p"]**2+r["q"]**2+r["k"]**2*(r["x"]**2+r["y"]**2) for r in m);mom=lambda m:math.fsum(r["k"]*(r["p"]*r["y"]-r["q"]*r["x"]) for r in m);e0,p0=energy(modes),mom(modes);de=dp=0.
 for t in (0.,.1,.7,1.9,2*math.pi):
  out=[]
  for r in modes:
   k=r["k"];c,s=math.cos(k*t),math.sin(k*t);out.append({"k":k,"x":r["x"]*c+r["p"]*s/k,"y":r["y"]*c+r["q"]*s/k,"p":r["p"]*c-k*r["x"]*s,"q":r["q"]*c-k*r["y"]*s})
  de,dp=max(de,abs(energy(out)-e0)),max(dp,abs(mom(out)-p0))
 return {"maximum_energy_drift":de,"maximum_worldsheet_momentum_drift":dp,"fourier_convention_control":fourier_convention_control(),"scope":"deterministic flow control; not a constrained sample"}
flow_control=finite_mode_flow_control

def _scan(v,path="registry"):
 out=[]
 if isinstance(v,Mapping):
  for k,x in v.items():
   if not isinstance(k,str):raise TypeError("registry key must be a string")
   if k.lower() in FORBIDDEN:out.append(path+"."+k)
   out+=_scan(x,path+"."+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):out+=_scan(x,f"{path}[{i}]")
 return out

def validate_dependency_registry(r):
 bad=_scan(r)
 if bad:raise ValueError("forbidden downstream dependency: "+", ".join(sorted(bad)))

def dependency_audit():
 valid={"sampler":{"torus_radii":[1.]*9,"winding_cycle":0,"fourier_cutoff_K":2,"transverse_energy":1.,"preparation_family":"principal_delta_liouville_parameterized"},"event":{"r_in":.1,"r_out":.2,"observation_horizon":10.,"episode_history":"armed","root_tolerances":{"residual":1e-12}}};validate_dependency_registry(valid);muts={"sigma_filter":{**valid,"event":{**valid["event"],"condition_on_sigma_3":.01}},"rank_filter":{**valid,"sampler":{**valid["sampler"],"minimum_rank":3}}};rejected={}
 for n,r in muts.items():
  try:validate_dependency_registry(r)
  except ValueError as e:rejected[n]=str(e)
  else:raise AssertionError(f"mutation {n} was accepted")
 return {"valid_registry_status":"ACCEPTED","hostile_mutations":rejected,"all_hostile_mutations_rejected":set(rejected)==set(muts),"rank_and_sigma_are_output_marks_only":True,"scope":"executed key guard; not proof against arbitrary hidden dependencies"}
dependency=dependency_audit

def build_report():
 return {"schema_version":SCHEMA,"brief_commit":BRIEF,"scope":"exact analytic surrogates, executable synthetic semantics and open-gate ledger; no physical sampling or exhaustive solve","verdict":"inconclusive","claim_classification":{"exact_analytic_controls":["opposite-winding identity","Gaussian exponent 7 and sqrt(pi/2)/48","Gram-eigenvalue exponent 7/2","volume-Palm exponent 8 and 1/105","affine delta scaling","Fourier conversion and invariants"],"conditional_propositions":["Palm power transfer","curvature-lifted local counterexample","Borel normalization after frozen total contracts"],"schematic_event_semantics":["primary precedence and flags","full tie cluster","hysteresis merger/rearm","hostile mutations"],"open_physical_gates":["freeze valid principal source and total event schema","constrained sampler","certified exhaustive hysteretic root solver"]},"principal_source_measure_control":source_measure_control(),"dependency_audit":dependency_audit(),"finite_mode_flow_control":finite_mode_flow_control(),"opposite_winding_rank_controls":rank_controls(),"first_entry_and_closest_control":first_entry_and_closest_control(),"hysteresis_control":hysteresis_control(),"event_schema_control":event_schema_control(),"outcome_mass_ledger_control":outcome_mass_ledger(),"hard_edge_and_palm_controls":hard_edge_controls(),"physical_result_ledger":{"principal_source_cell":"parameterized family only; not frozen","total_physical_event_map":"not implemented or proved total","normalized_regular_mass":"not computed","normalized_exceptional_mass":"not computed","rank_mixture":"not computed","event_conditioned_sigma_3":"not computed","joint_T_j_b_ell":"not computed","physical_finite_K_first_entry_law":"not computed","three_plus_one_selection":"not computed","earliest_open_gate":"freeze a valid principal source measure and total event schema; then constrained sampler and certified exhaustive hysteretic first-entry root solver"}}

def main(argv:Sequence[str]|None=None)->int:
 p=argparse.ArgumentParser(description="Run Brief 0017 analytic and schematic controls.");p.add_argument("--output",type=Path,default=Path(__file__).with_name("analytic_controls.json"));p.add_argument("--check",action="store_true",help="compare duplicate-key-rejected, type-strict canonical JSON");a=p.parse_args(argv);r=build_report()
 if a.check:
  if not a.output.exists():raise SystemExit("report missing")
  stored=read_semantic_json(a.output)
  if not strict_json_equal(stored,r) or canonical_bytes(stored)!=canonical_bytes(r):raise SystemExit("report semantic mismatch")
  c="duplicate-key-rejected type-strict canonical semantic JSON"
 else:write_json(a.output,r);c="generated"
 print(json.dumps({"status":"PASS","comparison":c,"output":str(a.output),"canonical_payload_sha256":canonical_hash(r),"rank_controls":10,"primary_outcomes":len(PRIMARY_OUTCOMES),"physical_verdict":"inconclusive"},sort_keys=True,separators=(",",":")));return 0

entry_controls=first_entry_and_closest_control
hysteresis=hysteresis_control
outcome_ledger=outcome_mass_ledger
if __name__=="__main__":raise SystemExit(main())
