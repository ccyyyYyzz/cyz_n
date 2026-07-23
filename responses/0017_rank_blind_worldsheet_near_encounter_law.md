---
brief: 0017
source: browser-hosted GPT collaboration with independent derivation amendments
captured: 2026-07-23
branch: brief-0017
brief_commit: a0673f3eef4ecd329b45612b12c9efe0171d4da2
status: proposed
artifacts:
  - artifacts/0017/probe_0017.py
  - artifacts/0017/test_probe_0017.py
  - artifacts/0017/analytic_controls.json
---

# Response 0017 — Rank-blind finite-K world-sheet near encounters and the first-entry Palm boundary

## Executive result

Fix two graph-like, globally opposite-wound F1 strings on one rectangular
\(T^9\), a quadratic Nambu--Goto Fourier cutoff \(K\), an unconditioned
constrained Liouville preparation, an observation horizon, and

\[
0<r_{\rm in}<r_{\rm out}<\operatorname{inj}(T^9_R).
\]

The analytic finite-mode flow and a hysteretic first-entry map define a Borel
map

\[
\Psi_h:\Gamma_{K,h}\to\mathfrak E_h,
\]

where \(\mathfrak E_h\) is the disjoint union of regular episodes and every
exceptional, ambiguous, invalid, no-entry and censored outcome.  The first
rank-blind finite-\(K\) geometric law is

\[
\boxed{\widetilde{\mathcal H}^{(K)}_h=(\Psi_h)_\#\mu_{E,K,h}.}
\]

It is normalized.  Its preparation and stopping rule do not read encounter
rank, \(\sigma_3\), normal dimension, response rank or a requested winner.
Those quantities are marks computed only after the first-entry representative
or cluster has been emitted.

At regular first entry the stored impact data are

\[
\boxed{b=P_Ns,\qquad \ell=(I-P_N)s,\qquad s=b+\ell.}
\]

Generally \(\ell\ne0\).  Only a verified interior full closest approach may
use \(b=s\), \(\ell=0\).  Closest approach is a secondary episode mark, not
the holding time.

For opposite winding, with transverse slopes \(p_1,p_2\), relative velocity
\(u\), and \(q_s=p_1+p_2\),

\[
J=[e_w+p_1,e_w-p_2,u]\sim[e_w+p_1,-q_s,u],
\]

so

\[
\boxed{\operatorname{rank}J=3\iff q_s\wedge u\ne0,}
\]

and

\[
\boxed{\det(J^TJ)=|q_s\wedge u|^2+|p_1\wedge q_s\wedge u|^2.}
\]

Straight opposite winding, \(q_s=0\), and \(u\parallel q_s\) are genuine
lower-rank strata and are retained.

For the exact fixed-point control

\[
B=[q_s,u]\in\mathbb R^{8\times2},\qquad B_{Ai}\stackrel{\rm iid}{\sim}N(0,1),
\]

\[
\boxed{\Pr[s_{\min}(B)\le\varepsilon]
\sim\frac{\sqrt{\pi/2}}{48}\varepsilon^7.}
\]

This exponent is not an event theorem.  In the strictly delimited affine,
isotropic, all-regular-root benchmark with smooth uniform translation and no
survival tilt, the complete coarea/flux bias is \(s_1s_2\),
\(\mathbb E[s_1s_2]=7\), and

\[
\boxed{\Pr_{\rm volume}[s_{\min}(B)\le\varepsilon]
\sim\frac1{105}\varepsilon^8.}
\]

The physical first-entry Palm density additionally contains the constraint
density, full Jacobian, Morse/inward indicators, armed-history and
no-earlier-entry factors, plus any competition among components or pairs.  A
curved local closest-point intensity can instead scale as \(\varepsilon^6\).
No exponent is therefore assigned here to the physical first-entry law.

The final physical verdict is

```text
inconclusive
```

because the microcanonical sampler and certified global first-entry solver
have not been run.  The normalized physical outcome masses, encounter-rank
mixture, event-conditioned \(\sigma_3\) tail, regulator sensitivity and joint
numerical law of \((T,j,b,\ell)\) remain unknown.

## Claim classes

### `primary-source derived`

- Sakellariadou supplies a flat-space Nambu--Goto wave evolution and a discrete
  torus intersection model, not this continuous impact law.
- Mitchell--Turok, Deo--Jain--Tan and Mañes provide statistical-string and
  state-counting precedents, not a unique classical first-entry preparation.
- Hindmarsh--Skliros provide a coherent-state bridge to classical loops, not a
  cosmological probability measure over loops.
- EGJK provide the anisotropic \(T^9\) setting and one macroscopic ensemble.
- Danos--Frey--Mazumdar constrain the interaction/equilibrium regime.
- GKM provide a conditional large-impact profile and numerically schedule
  recollisions at \(t_r\simeq r/\bar v\) with a fresh impact redraw.  This is a
  numerical closure, not a first-principles return theorem.
- JJP provide reaction probabilities conditional on supplied local collision
  geometry, not a prior first-entry law.

### `exact theorem of the preregistered finite-K model`

- normalized rank-blind pushforward law and Borel event map;
- preservation of all exceptional mass;
- opposite-winding rank identity;
- stratified Borel normal field;
- first-entry/closest-approach decomposition.

### `exact analytic control / conditional proposition`

These statements are not theorems of the preregistered finite-\(K\) physical
world-sheet law:

- the coefficient \(\sqrt{\pi/2}/48\) is an exact theorem of the standardized
  iid Gaussian fixed-point matrix control;
- the coefficient \(1/105\) is an exact theorem of the strictly delimited
  affine, isotropic, all-regular-root incoming-volume-biased control with no
  survival tilt; and
- the general Palm power-transfer formula is conditional on the stated regular
  variation, integrability and normalization hypotheses.

They are analytic audits of possible event tilts.  None is transferred to the
microcanonical hysteretic first-entry law without its constraint-density,
Jacobian, Morse/inward, armed-history and no-earlier-entry calculation.

### `new measurable closure`

The finite-\(K\) graph sector, coarea-normalized microcanonical branch weights,
hysteresis thresholds, tie-cluster convention, source-validity predicate and
Gaussian diagnostic are declared closures.

### `controlled numerical result`

The standard-Python probe checks the hard-edge constants by deterministic
quadrature, rank identities, near-degenerate controls, stratified projectors,
entry/closest semantics, hysteresis, no-entry tags, all outcome tags, and
finite-mode conservation.  It is not a Monte Carlo population result.

### `no-go/underdetermination`

A fixed-point exponent cannot be relabeled as a first-entry, episode-closest or
globally earliest-event exponent.  Almost-sure rank three does not imply a
uniform \(\sigma_3\) margin.  A defined pushforward law does not identify its
masses without a sampler and exhaustive event solver.

---

# 1. Finite-K source registry

Use physical-length coordinates on

\[
M=T^9_R=\prod_{A=0}^8\mathbb R/L_A\mathbb Z,
\qquad L_A=2\pi R_A,
\qquad \operatorname{inj}(M)=\tfrac12\min_A L_A.
\]

Choose winding cycle \(w\), \(\sigma_i\in[0,L_w)\), and static gauge

\[
X_1^w=+\sigma_1,\qquad X_2^w=-\sigma_2,
\]

\[
X_i^\perp=Q_i+Y_i(t,\sigma_i)\pmod{T^8_\perp}.
\]

The winding label, metric and world-sheet data transform together under torus
relabeling.  Folds, overhangs, cusp-scale structure, winding changes and exact
nonlinear Nambu--Goto evolution remain outside this graph-sector model.

## 1.1 Real Fourier basis

At \(t=0\),

\[
Y_i^A(t=0,\sigma_i)=\sum_{n=1}^K(x_{in}^A\cos k_n\sigma_i+y_{in}^A\sin k_n\sigma_i),
\]

\[
\dot Y_i^A=V_i^A+\sum_{n=1}^K(p_{in}^A\cos k_n\sigma+q_{in}^A\sin k_n\sigma),
\qquad k_n=2\pi n/L_w.
\]

The exact flow is

\[
\begin{aligned}
x_n(t)&=x_n\cos k_nt+(p_n/k_n)\sin k_nt,\\
p_n(t)&=p_n\cos k_nt-k_nx_n\sin k_nt,
\end{aligned}
\]

and similarly for \((y_n,q_n)\).  For
\(Y_n=c_n^Le^{ik_n(\sigma-t)}+c_n^Re^{ik_n(\sigma+t)}+\text{c.c.}\),

\[
\begin{aligned}
c_n^L&=\tfrac14[x_n+q_n/k_n+i(p_n/k_n-y_n)],\\
c_n^R&=\tfrac14[x_n-q_n/k_n-i(y_n+p_n/k_n)].
\end{aligned}
\]

The conserved quadratic quantities are

\[
H_i=\frac{T_FL_w}{2}|V_i|^2+
\frac{T_FL_w}{4}\sum_n(|p_{in}|^2+|q_{in}|^2+k_n^2|x_{in}|^2+k_n^2|y_{in}|^2),
\]

\[
\mathcal P_{\sigma,i}=\frac{T_FL_w}{2}\sum_nk_n(p_{in}\cdot y_{in}-q_{in}\cdot x_{in}).
\]

## 1.2 Microcanonical measure

Let \(y\) collect \(V_i,x_{in},y_{in},p_{in},q_{in}\), and keep
\(Q_{\rm rel}\in T^8_\perp\) separate.  Define

\[
C(y)=(H_1+H_2,\,T_FL_w(V_1+V_2),\,\mathcal P_{\sigma,1},\,\mathcal P_{\sigma,2})
\]

and fix \(c_h=(E_\perp,P_{\rm tot},\pi_1,\pi_2)\).  On each nonempty regular
branch \(\Sigma_{K,h}^{(r)}\subset C^{-1}(c_h)\),
\(\operatorname{rank}DC=11\), put

\[
\Gamma_{K,h}^{(r)}=T^8_\perp\times\Sigma_{K,h}^{(r)},
\]

\[
d\nu_{K,h}^{(r)}=
\frac{dQ_{\rm rel}}{\operatorname{Vol}(T^8_\perp)}
\frac{d\mathcal H^{N-11}(y)}{\sqrt{\det(DC(y)DC(y)^T)}}.
\]

Energy bounds the coefficient shell and the center torus is compact, so each
regular branch has finite mass.  For declared rank-blind branch weights
\(\omega_r\),

\[
\boxed{\mu_{E,K,h}=\sum_r\omega_r
\frac{\nu_{K,h}^{(r)}}{\nu_{K,h}^{(r)}(\Gamma_{K,h}^{(r)})}.}
\]

Weights may not depend on rank, \(\sigma_3\), normal dimension, response cells
or a winner.  Singular constraint branches require their own declared measure
or are tagged `source_invalid`.

## 1.3 Source-validity boundary

With

\[
r_{x,in}=\sqrt{x_{in}^2+(p_{in}/k_n)^2},\qquad
r_{y,in}=\sqrt{y_{in}^2+(q_{in}/k_n)^2},
\]

a time-uniform bound is

\[
B_i=|V_i|+\sum_nk_n(|r_{x,in}|+|r_{y,in}|).
\]

Preregister \(B_i\le\epsilon_{\rm graph}^*\) and
\(k_{\max}\ell_s\le\kappa_{\rm UV}^*\).  Invalid samples are emitted as
`source_invalid`; they are not redrawn.  Conditioning on validity would be a
separate named preparation with its removed mass printed.

---

# 2. Hysteretic event map and normalized law

For \(z=(\sigma_1,\sigma_2,t)\), search every torus image capable of entering
the outer tube and define

\[
s_\omega(z)=\operatorname{Log}_{X_2}X_1,
\qquad F_\omega(z)=\tfrac12\|s_\omega(z)\|^2,
\]

\[
\rho_\omega(t)=\min_{\sigma_1,\sigma_2}\|s_\omega\|,
\qquad
\mathcal M_\omega(t)=\operatorname*{argmin}_{\sigma_1,\sigma_2}F_\omega.
\]

For armed history,

\[
T_{\rm in}=\inf\{t>0:\rho(t)\le r_{\rm in}\},
\qquad
T_{\rm out}=\inf\{t>T_{\rm in}:\rho(t)\ge r_{\rm out}\}.
\]

The interval \([T_{\rm in},T_{\rm out})\) is one episode; rearming occurs only
after outer exit.  Regular inward entry has

\[
\nabla_\xi F=0,\quad F=r_{\rm in}^2/2,\quad
\nabla^2_{\xi\xi}F\succ0,\quad\partial_tF<0.
\]

Closest approach is the minimizer cluster of \(\rho(t)\) inside the episode.
A unique interior full closest point additionally has \(\partial_tF=0\) and
\(\nabla^2_{\xi,t}F\succ0\).

The disjoint outcome registry is

```text
regular_first_entry; tie_cluster; ambiguous_tie; grazing_entry;
degenerate_spatial_minimum; left_censored_active_episode;
right_censored_no_entry; right_censored_active_episode; no_entry_proved;
source_invalid; torus_branch_ambiguous; numerically_unresolved
```

Unresolved ties are cluster-valued or explicitly ambiguous.  Finite-window
non-observation is censoring; `no_entry_proved` requires a complete certified
period or global lower bound.

> **Theorem 1.**  The analytic finite-mode flow, compact minimizer
> correspondence, closed-set hitting times, derivative classifications and
> cluster-valued tie rule make \(\Psi_h\) Borel.  Hence
> \(\widetilde{\mathcal H}^{(K)}_h=(\Psi_h)_\#\mu_{E,K,h}\) is normalized and
> preserves every rank and exceptional stratum.

The proof uses continuity of finite Fourier flow and \(\rho\), measurability of
closed-set hitting times, the Borel graph of the compact argmin correspondence,
and Borel derivative inequalities.  Rank is evaluated only after the event
record exists.

For each tag \(\alpha\),

\[
M_\alpha=\mu_{E,K,h}(\Psi_h^{-1}\mathfrak E_\alpha),
\qquad\sum_\alpha M_\alpha=1.
\]

This response defines but does not estimate these physical masses.

---

# 3. Pair jet, stratified normal field, and impact phase

At a selected representative,

\[
J_j=[\tau_1,-\tau_2,u],\qquad
\widehat J_j=G_j^{1/2}J_jH_j^{-1/2},\qquad a(j)=\operatorname{rank}J_j.
\]

Store all three singular values.  On \(\mathcal J_a=\{j:a(j)=a\}\),

\[
N_j=(\operatorname{im}J_j)^{\perp_{G_j}},\quad
\dim N_j=9-a,
\]

\[
P_{N_j}=I-J_j(J_j^TG_jJ_j)^+J_j^TG_j.
\]

The pseudoinverse is continuous at fixed rank and Borel globally; therefore
\(\mathcal N=\{(j,b):b\in N_j\}\) is a stratified Borel normal field.  Rank
two has a seven-dimensional fiber; rank three has six dimensions.

At spatial first entry, \(s\perp\tau_1,\tau_2\) but generally
\(s\not\perp u\).  Thus

\[
\boxed{b_{\rm in}=P_{N_j}s_{\rm in},\quad
\ell_{\rm in}=(I-P_{N_j})s_{\rm in},\quad s=b+\ell.}
\]

At an interior full closest point, \(J^TG s=0\), so and only so
\(b_c=s_c\), \(\ell_c=0\).

---

# 4. Opposite-winding rank identity

With \(\tau_1=e_w+p_1\), \(-\tau_2=e_w-p_2\), and \(q_s=p_1+p_2\), a
determinant-one column operation yields

\[
[e_w+p_1,e_w-p_2,u]\sim[e_w+p_1,-q_s,u].
\]

Because \(q_s,u\perp e_w\),

\[
\boxed{a=3\iff q_s\wedge u\ne0,}
\]

\[
\boxed{\det(J^TJ)=|q_s\wedge u|^2+|p_1\wedge q_s\wedge u|^2.}
\]

Therefore straight opposite winding, \(q_s=0\), and \(u\parallel q_s\) have
rank at most two.  A continuous law may still have rank three almost surely
while approaching these strata arbitrarily closely, so exact rank is not a
robustness margin.

---

# 5. Exact hard-edge and Palm controls

## 5.1 Fixed point

For iid standard Gaussian \(B\in\mathbb R^{8\times2}\), ordered eigenvalues of
\(B^TB\) have density

\[
f(\lambda_1,\lambda_2)=\frac1{2880}e^{-(\lambda_1+\lambda_2)/2}
(\lambda_1\lambda_2)^{5/2}(\lambda_1-\lambda_2).
\]

Writing \(y=\lambda_2\), the inner integral tends to
\(2^{9/2}\Gamma(9/2)\) and
\(\int_0^{\varepsilon^2}y^{5/2}dy=2\varepsilon^7/7\).  Hence

\[
\boxed{\Pr[s_{\min}\le\varepsilon]
=\frac{\sqrt{\pi/2}}{48}\varepsilon^7+o(\varepsilon^7).}
\]

The coefficient is \(0.0261107111940729\ldots\).  There is no rank-one atom,
but the essential infimum is zero.

## 5.2 Affine all-root volume bias

Weight the same law by \(V=s_1s_2=\sqrt{\det(B^TB)}\).  Bartlett decomposition
gives \(\mathbb EV=7\).  Multiplying the density by
\(\sqrt{\lambda_1\lambda_2}\), the unnormalized leading tail is
\(\varepsilon^8/15\).  Therefore

\[
\boxed{\Pr_{\rm volume}[s_{\min}\le\varepsilon]
=\varepsilon^8/105+o(\varepsilon^8).}
\]

This applies only to the declared affine, isotropic, smooth-translation,
all-regular-root intensity with no survival tilt.  For affine first entry,
spatial coarea and inward flux combine as

\[
\sqrt{\det(A^TA)}\,\|P_{A^\perp}u\|=\sqrt{\det(J^TJ)}.
\]

For affine closest approach the zero-gradient density contributes
\(\det(J^TJ)^{-1/2}\) and the Hessian contributes \(\det(J^TJ)\), giving the
same net weight.  A Hessian-only argument is wrong.

## 5.3 Physical first-entry weight

For

\[
g=(\partial_{\sigma_1}F,\partial_{\sigma_2}F,F-r_{\rm in}^2/2),
\]

the complete conditional local weight is

\[
\boxed{\mathcal W_{\rm in}(B)=p_{g\mid B}(0)
\mathbb E[|\det Dg|\,1_{\rm Morse}1_{\rm inward}
S_{\rm armed}S_{\rm earlier}\mid g=0,B].}
\]

Constraint density, Jacobian, indicators and no-earlier-entry survival must be
handled together.  Fixed point, all-root Palm, hysteretic first entry,
episode-selected closest, and globally earliest selection are different laws.

If the fixed-point tail is \(C\varepsilon^7\) and

\[
m(s)=\mathbb E[\mathcal W\mid s_{\min}=s]
\sim w_0s^\alpha L(s),\qquad\alpha>-7,
\]

then

\[
\boxed{\Pr_{\rm event}[s_{\min}\le\varepsilon]
\sim\frac{7Cw_0}{(7+\alpha)\mathbb E\mathcal W}
\varepsilon^{7+\alpha}L(\varepsilon).}
\]

Incoming-volume bias has \(\alpha=1\).  A survival power adds its exponent.
An integrable absolutely continuous weight creates neither an exact lower-rank
atom nor a positive essential margin.

## 5.4 Curved closest counterexample

For

\[
\Phi_\delta=re_4+x_1e_1+x_2e_2+\delta te_3+\tfrac12t^2e_4,
\]

\[
s_{\min}\asymp\delta,\qquad
\nabla^2F=\operatorname{diag}(1,1,\delta^2+r).
\]

If \(p_{g\mid B}(0)\asymp\delta^{-1}\), the local closest-stationary intensity
has an \(\varepsilon^6\) tail.  This is a conditional counterexample, not a
first-entry or globally earliest-event exponent.

---

# 6. Deterministic artifact and observed checks

Delivered:

```text
artifacts/0017/probe_0017.py
artifacts/0017/test_probe_0017.py
artifacts/0017/analytic_controls.json
```

Executed on LF files:

```text
python3 -m py_compile artifacts/0017/probe_0017.py artifacts/0017/test_probe_0017.py
python3 artifacts/0017/probe_0017.py --help
python3 artifacts/0017/probe_0017.py --output artifacts/0017/analytic_controls.json
python3 artifacts/0017/probe_0017.py --check --output artifacts/0017/analytic_controls.json
python3 -m unittest discover -s artifacts/0017 -p "test_probe_0017.py" -v
```

All exited zero; 12 tests passed.  A fresh copy of both Python files and the
JSON report was converted to CRLF, then `py_compile`, `--help`, semantic
`--check`, and all 12 tests again exited zero.  JSON checking uses a
duplicate-key-rejecting parser and type-strict canonical semantics, not raw
line endings.

Environment:

```text
Python 3.13.5; GCC 14.2.0
Linux 6.12.13 x86_64; glibc 2.41
```

Hashes:

```text
probe_0017.py normalized-LF SHA-256
9dbde7bdea25f8495960d132c5bf1ea8901be1fb5c581095b282866747ac5ecf

test_probe_0017.py normalized-LF SHA-256
8079cef00596e573ccbb22831f0f316a3710b98f91b98f87ac50c2aa6a02bebf

analytic_controls.json file SHA-256
9e5a083f02d774f3437d67e343426162b11b0bf0d5f12715ad60f1eab2a788d3

analytic_controls canonical payload SHA-256
d0aef9c27fb357f99848a32ee6c45cb4c83cf573969f2dba68c0b2b0160ca73b
```

At \(\varepsilon=0.05\), deterministic quadrature gives ratios
\(0.9985753405\) to \(C_0\varepsilon^7\) and \(0.9987507809\) to
\(\varepsilon^8/105\).

The controls verify rank-two straight, \(q_s=0\), and parallel-velocity cases;
a non-collinear rank-three case; four rank-three cases with decreasing positive
\(\sigma_3\); entry \(b\ne s\), \(\ell\ne0\); closest \(b=s\); normal
dimensions seven and six; rejection of a fixed-six projector; hysteretic
entry/closest/exit/rearm; censoring versus proved no entry; all 12 outcome tags;
and finite-mode energy/world-sheet momentum conservation.

---

# 7. Verdict and next gate

```text
verdict: inconclusive
normalized regular mass: not computed
normalized exceptional mass: not computed
rank mixture: not computed
event-conditioned sigma_3: not computed
joint T,j,b,ell: defined, not numerically identified
K/preparation sensitivity: not computed
```

The earliest physical gate is a normalized constrained microcanonical sampler
plus certified hysteretic first-entry root coverage on the preregistered
finite-\(K\) source cell.  It must retain source-invalid, tied, grazing,
degenerate, lower-rank, no-entry and censored mass.

After that, attach a separately registered channel/history law

\[
\mathscr C_X(d\chi,dh',dX',d\Delta E_R,d\dagger\mid j,b,\ell,X),
\]

then compose

\[
\mu_{E,K,h}\to\widetilde{\mathcal H}^{(K)}_X\to\mathscr P_X
\to\text{age/episode augmentation}
\to\text{anonymous }A,R,B,C,M
\]

\[
\to Z_0,\ldots,Z_9\to\text{all-rank entrant residence and leakage}.
\]

At no point are \(p=1\), \(a=3\), and \(m=3\) identified.  The source family
starts with Lorentzian \(9+1\); it does not derive one time direction or
Lorentzian signature.

## Primary sources

1. M. Sakellariadou, *Numerical Experiments in String Cosmology*, Nucl. Phys.
   B 468 (1996), arXiv:hep-th/9511075,
   DOI:10.1016/0550-3213(96)00123-X.
2. D. Mitchell and N. Turok, *Statistical Properties of Cosmic Strings*,
   Nucl. Phys. B 294 (1987), DOI:10.1016/0550-3213(87)90626-2.
3. N. Deo, S. Jain and C.-I. Tan, *String Statistical Mechanics Above
   Hagedorn Energy Density*, Phys. Rev. D 40 (1989),
   DOI:10.1103/PhysRevD.40.2626.
4. J. L. Mañes, *String Form Factors*, JHEP 01 (2004) 033,
   arXiv:hep-th/0312035.
5. J. L. Mañes, *Portrait of the String as a Random Walk*, JHEP 03 (2005) 070,
   arXiv:hep-th/0412104.
6. M. Hindmarsh and D. Skliros, *Covariant Closed String Coherent States*,
   Phys. Rev. Lett. 106 (2011), arXiv:1006.2559.
7. R. Easther, B. R. Greene, M. G. Jackson and D. Kabat, *String Windings in
   the Early Universe*, JCAP 02 (2005) 009, arXiv:hep-th/0409121.
8. R. Danos, A. R. Frey and A. Mazumdar, *Interaction Rates in String Gas
   Cosmology*, Phys. Rev. D 70 (2004), arXiv:hep-th/0409162.
9. B. Greene, D. Kabat and S. Marnerides, *Dynamical Decompactification and
   Three Large Dimensions*, Phys. Rev. D 82 (2010), arXiv:0908.0955.
10. M. G. Jackson, N. T. Jones and J. Polchinski, *Collisions of Cosmic F- and
    D-strings*, JHEP 10 (2005) 013, arXiv:hep-th/0405229.
