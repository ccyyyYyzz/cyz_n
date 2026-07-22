---
brief: 0007
source: browser-hosted GPT
captured: 2026-07-23
repository_commit: d87d696d5057b03854a0455ff8d8542c39fcaeb1
status: proposed
---

# Response 0007 — The defect-clearance/stress generator, the species-selection no-go, and the spectral departure theorem

## Executive result

The prescribed WIRRC controller can be replaced by a genuine mesoscopic
generator whose rank transitions are consequences of collision clearance,
persistent defect stress, energy barriers and a pre-quotient response
spectrum.  The generator contains no branch of the form

\[
s<s_p\Rightarrow s\mapsto s+1,
\qquad
s>s_p\Rightarrow s\mapsto s-1,
\]

no potential centered at \(s_p\), no preferred three-plane and no
four-dimensional probe dictionary.

The central construction is the **defect-clearance/stress spectral generator**
(DCS generator).  It has five coupled parts:

\[
\boxed{
\mathcal L
=
\mathcal L_{\rm transport}
+
\mathcal L_{\rm collision}
+
\mathcal L_{\rm chemistry}
+
\mathcal L_{\rm rank}
+
\mathcal L_{\rm port/field}.
}
\tag{1}
\]

The collision part uses the actual worldvolume interaction kernel.  For the
string sector, the source-derived impact-parameter slice of Greene, Kabat and
Marnerides is

\[
\log\Gamma_1
=
\varphi+2\log R-\log4
+(s-3)\log
\frac{2\pi R}{\sqrt{\pi\Delta x^2}}
-\frac{|b|^2}{\Delta x^2},
\qquad
\Delta x^2=4\log R^2.
\tag{2}
\]

A defect-loaded mode has a relaxation pole \(-\Omega_p\) in the same
pre-quotient transfer operator that is measured by the response ports.
Competing exponential clocks give the exact clearance and persistence
probabilities

\[
c_p(s)
=
\frac{\bar\Gamma_p(s)}
     {\bar\Gamma_p(s)+\Omega_p},
\qquad
r_p(s)
=
\frac{\Omega_p}
     {\bar\Gamma_p(s)+\Omega_p}.
\tag{3}
\]

An inactive direction is released only by collision energy that survives its
unbinding barrier.  An active direction is reconfined only by residual defect
stress that survives its binding barrier.  The derived aggregate fluxes are

\[
\mathcal A_s
=
(D-s)
\sum_p
\epsilon_p
\binom{n_p}{2}
c_p(s+1),
\tag{4}
\]

\[
\mathcal S_s
=
s
\sum_p
\tau_p n_p r_p(s).
\tag{5}
\]

The two physical progress rates are

\[
\dot h_+
=
\frac{[\mathcal A_s-E_+]_+}{\Theta_+},
\qquad
\dot h_-
=
\frac{[\mathcal S_s-\Sigma_-]_+}{\Theta_-}.
\tag{6}
\]

Both clocks exist at every rank.  Neither is switched by comparison with a
target.  A release reset occurs when \(h_+=1\); a reconfinement reset occurs
when \(h_-=1\).  Which clock can reach its guard is determined by the
collision/stress spectrum.

This yields the first exact result.

> **Derived rank theorem.**  
> In the zero-thickness single-species limit, let the clean direct-intersection
> kernel satisfy
>
> \[
> c_p(s)=1\quad(s\le2p+1),
> \qquad
> c_p(s)=0\quad(s>2p+1).
> \]
>
> If the scalar barriers obey the open inequalities
>
> \[
> 0<E_+<
> \min_{s<2p+1}
> (D-s)\epsilon_p\binom{n_p}{2},
> \]
>
> \[
> 0<\Sigma_-<
> \min_{s>2p+1}
> s\tau_p n_p,
> \]
>
> then the unique rank at which both derived fluxes vanish is
>
> \[
> s_*=2p+1.
> \]
>
> Every lower rank has release flux and no reconfinement flux; every higher
> rank has reconfinement flux and no release flux.  All complete hybrid
> trajectories reach \(s_*\) in finite flow length, all resets decrease the
> rank Lyapunov function, and the target rank is forward invariant.

For \(p=1\), the theorem gives \(s_*=3\).  For \(p=2\), the same generator gives
\(s_*=5\).  The target is therefore not stored elsewhere in the code.

There are also three exact no-go statements.

1. **Intersection-only rank no-go.**  The collision generator by itself leaves
   the released projector invariant:

   \[
   \mathcal L_{\rm collision}\operatorname{rank}\Pi=0.
   \]

   Worldvolume intersection geometry supplies a collision rate, not a sign for
   rank motion.  The minimal extra rank term is the physically explicit
   clearance-to-unbinding and persistence-to-stress coupling (4)--(6).

2. **Species-selection no-go.**  If defect species do not interconvert, each
   pure-\(p\) sector is invariant.  A pure \(p=2\) state can never become a
   \(p=1\) state, and its derived rank is five.  The intersection kernel alone
   cannot make strings dominate.

   The minimal additional species term is a fragmentation/recombination
   network satisfying local detailed balance.  On the open free-energy region

   \[
   F_p
   \ge
   pF_1+(p-1)\Delta,
   \qquad
   \Delta>0,
   \qquad
   p\ge2,
   \tag{7}
   \]

   higher-dimensional defects are exponentially suppressed.  A quantitative
   perturbation theorem below proves that the rank-three basin persists when
   the remaining higher-\(p\) flux is smaller than the pure-string stability
   gap.  Thus \(p=1\) dominance is possible on an open mesoscopic parameter
   region, but it is not source-derived from the intersection kernel alone.
   The physical origin of (7) remains a named gate.

3. **One-time no-go.**  On any continuous nondegenerate carrier-tensor flow,
   inertia is locally constant.  The rank resets below add or remove positive
   directions only.  Therefore the number of negative directions is invariant.
   The DCS generator selects rank inside a hyperbolic viability sector but does
   not select index one from arbitrary signatures.  Its flow parameter is not
   physical time.  A time component additionally requires an ordered,
   port-asymmetric response germ.

The response coupling is now genuinely pre-quotient.  Port oscillators couple
to the complete carrier state through a matrix \(W\) before \(\Pi\) is chosen.
The full transfer is

\[
\mathcal G_X(z)
=
W^\vee(zI-\mathbb A_X)^{-1}W,
\tag{8}
\]

and the observability Gram is computed on the full microscopic response space,

\[
\mathcal O_X(T)
=
\int_0^T
e^{\mathbb A_X^\vee t}
W W^\vee
e^{\mathbb A_Xt}\,dt.
\tag{9}
\]

Completeness only after quotienting is rejected.  On an active regular branch,
finite two-jet transfer data are restricted from (8), the complete Green
matrix is inverted, and the principal co-metric is reconstructed through the
already adopted equation

\[
H_x^\vee(p_{L,x})=\beta_x,
\qquad
\mathcal L_x
=
\mu_{2,x}^\vee(\ker H_x^\vee).
\tag{10}
\]

Neither \(q\), its signature, a cone flag nor a directed time vector is passed
to the reconstructor.

The same defect relaxation pole that enters (3) produces the departure.  In a
single-species sector the pre-barrier rank fluxes satisfy

\[
\boxed{
\frac{
\mathcal A_{s-1}/[(D-s+1)A_p]
}{
\mathcal S_s/[sB_p]
}
=
\frac{\bar\Gamma_p(s)}{\Omega_p},
}
\tag{11}
\]

where \(A_p=\epsilon_p\binom{n_p}{2}\) and \(B_p=\tau_p n_p\).  The measured
high-bandwidth transfer must develop its defect pole at

\[
\omega_{\rm dep}\simeq\Omega_p.
\tag{12}
\]

For the source-derived string rate, (11) predicts the joint relation

\[
\log
\frac{
\mathcal A_{s-1}sB_1
}{
\mathcal S_s(D-s+1)A_1
}
=
\varphi+2\log R-\log4
+(s-3)\log
\frac{2\pi R}{\sqrt{\pi\Delta x^2}}
-\frac{|b|^2}{\Delta x^2}
-\log\omega_{\rm dep}.
\tag{13}
\]

A manually injected high-bandwidth channel cannot satisfy this
same-generator identity and is not a valid departure.

The DCS generator therefore closes the rank-rate, pre-quotient response and
same-spectrum departure seams at the mesoscopic level.  It gives a precise
species-selection obstruction and the smallest additional chemistry that can
produce an open \(p=1\)-dominated region.  It does not yet derive, from one
fundamental action, both the fragmentation hierarchy (7) and an attractive
index-one universal-carrier sector.

---

# 1. Source boundary and classification of claims

## 1.1 Source-derived input

Only the following physical rate statement is imported.

Greene, Kabat and Marnerides derive an impact-parameter-dependent winding
interaction rate in the heavy, diluted string regime.  The audited slice used
here is (2).  Its important structural content is:

- explicit dependence on the number \(s\) of large spatial dimensions;
- impact suppression through \(|b|^2/\Delta x^2\);
- radius and dilaton dependence;
- qualitatively different behavior between \(s=3\) and \(s>3\).

Their later paper, also by Greene, Kabat and Marnerides, studies successive
Hagedorn fluctuations.  It does not supply the generator constructed here.

No graph, tensor, CDT or matrix-model action is used in the present
derivation.

## 1.2 Newly proposed mesoscopic laws

The following are new and are not attributed to those papers:

1. the exponential-race reduction (3);
2. the clearance and persistent-stress couplings (4)--(6);
3. the fragmentation/recombination chemistry;
4. the common carrier mediator for multi-field response;
5. the pre-quotient port Hamiltonian and its finite response protocol.

Each is exposed as a model term and is separately killable.

## 1.3 Exact mathematical statements

The no-go theorems, positivity/non-explosion theorem, sharp rank theorem,
birth-death stationary formula, species perturbation theorem, response
observability theorem, same-spectrum relation and repaired hybrid selection
theorem are exact statements about the displayed model.

---

# 2. Microscopic and mesoscopic state space

## 2.1 Anonymous carrier

Let

\[
E\simeq\mathbb R^{D+1}
\]

carry a calibrated positive bookkeeping inner product.  This inner product is
not the event metric.

A state contains an orthogonal projector

\[
\Pi^2=\Pi=\Pi^\vee,
\qquad
r=\operatorname{rank}\Pi,
\qquad
s=r-1.
\tag{14}
\]

Here \(s\) is the number of released directions transverse to the single
history parameter used by the source-derived collision calculation.  Writing
\(r=s+1\) is a bookkeeping convention of that kinetic reduction, not a proof
that the history parameter is a response-visible physical time.  The ordered
response test in Section 10 must still identify a time component; if it does
not, the full \(3+1\) target remains unresolved.

Every admitted transverse rank occurs.  No carrier basis vector is called a
physical time or space direction.

A symmetric, nondegenerate carrier kinetic tensor

\[
C\in\operatorname{Sym}^2E
\tag{15}
\]

is a dynamical state variable.  Its active restriction is

\[
q_\Pi
=
C|_{\operatorname{im}\Pi}.
\tag{16}
\]

The rank dynamics does not assume an inertia for \(q_\Pi\).  The target
viability sector will require index one, but the one-time no-go below shows
that the current generator cannot select it from every signature.

## 2.2 Defect microstate

For each admitted worldvolume dimension

\[
p\in\{1,\ldots,P_{\max}\},
\]

the state contains a finite set of defects

\[
\mathcal D_p
=
\{
(W_{p,a},R_{p,a},k_{p,a},e_{p,a},\tau_p)
\}_{a=1}^{n_p}.
\tag{17}
\]

Here:

- \(W_{p,a}\) is an anonymous oriented \(p\)-plane or winding carrier;
- \(R_{p,a}\) is a radius/length scale;
- \(k_{p,a}\) is momentum or velocity data;
- \(e_{p,a}\) is energy;
- \(\tau_p>0\) is tension or mass density.

Pair data include the closest-approach vector \(b_{ab}\), relative velocity,
wavepacket width and any internal charge needed to decide whether annihilation
is allowed.

An energy cap

\[
\sum_{p,a}e_{p,a}
+
E_{\rm reservoirs}
+
E_{\rm fields}
\le E_{\max}
\tag{18}
\]

and a positive lower defect energy imply a finite occupation bound.

## 2.3 Rank reservoirs

For every inactive unit direction \(u\in\ker\Pi\) there is an unbinding
reservoir \(H_u^+\).  For every active direction \(v\in\operatorname{im}\Pi\)
there is a persistent-stress reservoir \(H_v^-\).

The equivariant reduced control uses the normalized aggregate variables

\[
h_+,h_-\in[0,1).
\tag{19}
\]

Their guards \(h_\pm=1\) are not target conditions.  They are ordinary
unbinding and rebinding barriers.

## 2.4 Fields and common carrier mediator

For every declared field species \(a\), let \(F_a\) be its finite internal
fiber.  Before quotienting, its principal tensor is a state variable

\[
\mathsf P_a^{\rm pre}
\in
\operatorname{Sym}^2E
\otimes
\operatorname{End}(F_a).
\tag{20}
\]

Write

\[
\mathsf P_a^{\rm pre}
=
C\otimes K_a+E_a,
\tag{21}
\]

where \(E_a\) is the off-common-carrier component.  The decomposition is
relative to the dynamical \(C\), not to a supplied target co-metric.

The minimal universal-mediator energy is

\[
\mathcal E_{\rm med}
=
\frac12
\sum_a
\kappa_a
\|E_a\|_F^2
+
\sum_a U_a(K_a).
\tag{22}
\]

The \(U_a\) keep the field factors in a declared compact set but do not fix
their values.  The overdamped part of the generator contains

\[
\dot E_a=-\gamma_aE_a.
\tag{23}
\]

This law follows from the quadratic mediator energy (22).  It is a newly
proposed physical term, not a subgradient flow toward a supplied \(q\).

## 2.5 Pre-quotient ports

Let the complete microscopic response state be

\[
\mathcal H_{\rm pre}
=
\bigoplus_a
\left(
\mathbb R
\oplus E^*
\oplus\operatorname{Sym}^2E^*
\right)
\otimes F_a
\oplus
\mathcal H_{\rm def}.
\tag{24}
\]

Port coordinates \(z_{\rm p}\) couple through the pre-quotient interaction

\[
H_{\rm port}
=
\frac12
\langle p_{\rm p},p_{\rm p}\rangle
+
\frac12
\langle z_{\rm p},\Omega_{\rm p}^2z_{\rm p}\rangle
-
\langle z_{\rm p},W^\vee\xi\rangle
-
\langle u,z_{\rm p}\rangle.
\tag{25}
\]

Here \(\xi\in\mathcal H_{\rm pre}\), \(u\) is the controlled source and
\(W\) is a microscopic port-coupling matrix.  Eliminating the port coordinates
gives source and readout maps derived from the same term:

\[
B=W,
\qquad
R=W^\vee.
\tag{26}
\]

They are defined before \(\Pi\).

---

# 3. The full generator

## 3.1 Piecewise-deterministic Markov form

In the interior of every rank sector, define

\[
\mathcal L f(X)
=
F(X)\cdot\nabla f(X)
+
\sum_{\zeta\in\mathfrak R}
r_\zeta(X)
\bigl[
f(J_\zeta X)-f(X)
\bigr].
\tag{27}
\]

The reaction list \(\mathfrak R\) contains:

- defect transport and impact updates;
- pair collision/annihilation;
- fragmentation and recombination;
- defect production/absorption by the energy reservoir;
- optional microscopic noise terms with bounded rates.

Rank changes are boundary resets at \(h_\pm=1\).  Equivalently, a Poissonized
coarse reduction replaces the boundary guards by birth and death rates.

## 3.2 Collision generator

For an annihilable pair \(a<b\) of species \(p\),

\[
\mathcal L_{\rm collision}f
=
\sum_{p}
\sum_{a<b}
\Gamma_{p,ab}(X)
\left[
f(A_{p,ab}X)-f(X)
\right].
\tag{28}
\]

The reset \(A_{p,ab}\):

1. removes or converts the two defects according to their charges;
2. deposits the released energy into the anonymous unbinding covariance;
3. updates the defect relaxation amplitudes;
4. preserves total energy including the reservoir.

For \(p=1\), the rate may use (2), averaged over the actual preparation
distribution.  For general \(p\), the finite-thickness collision kernel is a
new model input constrained by the direct-intersection limit.

## 3.3 Species chemistry

For every split \(p=q+(p-q)\), \(1\le q<p\), include

\[
p
\rightleftarrows
q+(p-q).
\]

The mass-action generator is

\[
\begin{aligned}
\mathcal L_{\rm chem}f(n)
={}&
\sum_{p=2}^{P_{\max}}
\sum_{q=1}^{p-1}
\kappa_{p,q}n_p
\left[
f(n-e_p+e_q+e_{p-q})-f(n)
\right]
\\
&+
\sum_{p=2}^{P_{\max}}
\sum_{q=1}^{p-1}
\bar\kappa_{p,q}
n_qn_{p-q}
\left[
f(n+e_p-e_q-e_{p-q})-f(n)
\right].
\end{aligned}
\tag{29}
\]

Energy differences are transferred to the common reservoir.  Local detailed
balance with fugacities \(z_p>0\) is

\[
\kappa_{p,q}z_p
=
\bar\kappa_{p,q}z_qz_{p-q}.
\tag{30}
\]

Immigration and absorption may be added with their own detailed-balance pairs.

## 3.4 Defect relaxation pole and clearance race

A defect-loaded response amplitude \(a_{p,\ell}\) has linear relaxation

\[
\dot a_{p,\ell}
=
-\Omega_{p,\ell}a_{p,\ell}
+
\text{carrier/port coupling}.
\tag{31}
\]

During the coherence interval, collision and relaxation are independent
exponential clocks of rates \(\bar\Gamma_p(s)\) and \(\Omega_p\).  Therefore

\[
\Pr(\text{collision before relaxation})
=
c_p(s)
=
\frac{\bar\Gamma_p(s)}
     {\bar\Gamma_p(s)+\Omega_p},
\tag{32}
\]

\[
\Pr(\text{relaxation before collision})
=
r_p(s)
=
\frac{\Omega_p}
     {\bar\Gamma_p(s)+\Omega_p}.
\tag{33}
\]

This derivation is the source of both rank directions.

## 3.5 Rank progress equations

Define the post-release clearance power

\[
\mathcal A_s(X)
=
(D-s)
\sum_p
\epsilon_p
\binom{n_p}{2}
c_p(s+1),
\tag{34}
\]

and the current-sector residual stress

\[
\mathcal S_s(X)
=
s
\sum_p
\tau_p n_p r_p(s).
\tag{35}
\]

The use of \(s+1\) in (34) is transition-state physics: a proposed new direction
is sustainable only when defects continue to clear in the enlarged sector.

The progress equations are (6).  The barriers

\[
E_+,\ \Sigma_-,\ \Theta_+,\ \Theta_->0
\tag{36}
\]

are scalar material parameters.  They do not depend on \(s_p\).

## 3.6 Rank marks and resets

The release direction is sampled from an equivariant mark measure

\[
\nu_+(du\mid X)
\propto
\langle u,\Sigma_+(X)u\rangle\,d\sigma_{\ker\Pi}(u),
\tag{37}
\]

where \(\Sigma_+\) is the annihilation-energy covariance.

The reconfinement direction is sampled from

\[
\nu_-(dv\mid X)
\propto
\langle v,\Sigma_-(X)v\rangle\,d\sigma_{\operatorname{im}\Pi}(v),
\tag{38}
\]

where \(\Sigma_-\) is persistent defect stress.

At \(h_+=1\),

\[
\Pi^+=\Pi+uu^\vee.
\tag{39}
\]

At \(h_-=1\),

\[
\Pi^-=\Pi-vv^\vee.
\tag{40}
\]

Every rank reset consumes the corresponding accumulated work and sets

\[
h_+^+=h_-^+=0.
\tag{40a}
\]

Resetting both normalized accumulators prevents an opposite clock that was
arbitrarily close to its old guard from generating a Zeno pair of jumps.

The full pre-quotient tensors \(C,\mathsf P_a^{\rm pre},W\), and therefore the
microscopic source/readout maps \(B=W\), \(R=W^\vee\), are not rewritten.
Their active restrictions change functorially:

\[
q_{\Pi^\pm}
=
C|_{\operatorname{im}\Pi^\pm},
\tag{41}
\]

\[
\mathsf P_{a,\Pi^\pm}
=
\mathsf P_a^{\rm pre}
|_{\operatorname{Sym}^2(\operatorname{im}\Pi^\pm)^*}.
\tag{42}
\]

Existing response state is pushed through the inclusion/restriction map.
Historical records are retained with an explicit reset marker; they are never
retrospectively projected into the new quotient.

Defect orientations are carried in \(E\).  Their active projections update
under \(\Pi^\pm\), and any lost stress energy is deposited in the reservoir.

## 3.7 Carrier and field flow

A dimension-neutral equivariant carrier potential may be used,

\[
U_C(C,\Sigma_{\rm def})
=
u_2\operatorname{tr}(C^2)
+
u_4\operatorname{tr}(C^4)
-
g_C\operatorname{tr}(C\Sigma_{\rm def}),
\tag{43}
\]

with

\[
\dot C=-\gamma_C\nabla_CU_C.
\tag{44}
\]

No signature is preferred by (43).

The field residuals obey (23), so

\[
\frac{d}{dt}
\mathcal E_{\rm med}
\le
-
\sum_a
\kappa_a\gamma_a
\|E_a\|_F^2
\tag{45}
\]

when the factor variables are held in their compact viability set.  With
slowly varying \(C,K_a\), the usual perturbation term is retained explicitly.

---

# 4. Positivity, normalization, non-explosion and equivariance

## Theorem 1 — well-posed DCS process

Assume:

1. the energy cap (18);
2. finitely many carrier dimensions and species;
3. positive lower defect energies;
4. locally Lipschitz continuous flow fields on each compact rank sector;
5. bounded collision, fragmentation and port rates;
6. strictly positive reset barriers.

Then:

- all jump rates are nonnegative;
- \(\mathcal L1=0\);
- the total stochastic jump rate is uniformly bounded;
- no finite-time explosion occurs;
- guard resets cannot accumulate in finite time;
- every maximal trajectory is complete;
- continuous pieces are absolutely continuous;
- the process defines a conservative Markov semigroup.

### Proof

The energy cap and lower defect energy bound give a finite occupation bound.
Every rank sector is compact after the declared coefficient bounds.  Hence all
continuous vector fields and stochastic rates have finite suprema.  The
stochastic jump count is dominated by a Poisson process of finite rate.

A rank reset consumes a positive reservoir amount.  Since reservoir speeds
have a finite upper bound, every pair of rank resets has a positive minimum
dwell time.  Thus there is no Zeno accumulation.  The identity
\(\mathcal L1=0\) follows term by term from (27).

## Theorem 2 — anonymity and equivariance

Let \(U\in O(E)\).  Transform

\[
\Pi\mapsto U\Pi U^\vee,
\quad
C\mapsto UCU^\vee,
\quad
W_{p,a}\mapsto UW_{p,a},
\quad
W\mapsto UW,
\]

and transform every full carrier tensor and port vector accordingly.

If collision rates depend only on invariant impact, energy, tension and
principal-angle data, then

\[
\mathcal L(f\circ U)
=
(\mathcal Lf)\circ U.
\tag{46}
\]

### Proof

Every scalar rate is invariant.  The mark measures (37)--(38) are pushed
forward into themselves.  The reset maps commute with the group action.
Every continuous tensor equation is equivariant.  No carrier direction is
preferred.

---

# 5. Why intersection geometry alone cannot select rank or species

## Theorem 3 — intersection-only rank no-go

Let

\[
\mathcal L_0
=
\mathcal L_{\rm transport}
+
\mathcal L_{\rm collision}
\]

act on defects while leaving \(\Pi\) unchanged at every collision reset.  Then

\[
\mathcal L_0\,\operatorname{rank}\Pi=0.
\tag{47}
\]

Consequently no worldvolume collision kernel, including a sharply
dimension-dependent one, produces rank motion without an explicit physical
coupling from collision products or persistent stress to the rank sector.

### Proof

The function \(\operatorname{rank}\Pi\) is constant along the transport flow
and unchanged by every collision reset.  Substitution into the generator gives
zero.

### Minimal repair

Equations (34)--(36) are the minimal mesoscopic repair:

- collision success deposits unbinding work;
- collision failure leaves persistent stress;
- universal energy barriers convert those physical quantities into spectral
  rank crossings.

Removing the first coupling gives a death-only model.  Removing the second
gives a birth-only model.  Neither can have a full bidirectional basin.

## Theorem 4 — independent-species no-go

Suppose \(\mathcal L_{\rm chem}=0\) and collision resets never change the
worldvolume dimension \(p\).  Then the support set

\[
\operatorname{supp}n
=
\{p:n_p>0\}
\]

can only lose species; it cannot create an absent species.  In particular, the
pure-\(p\) sectors are invariant.

Hence a pure \(p=2\) state cannot dynamically enter a \(p=1\)-dominated basin.
The intersection kernel does not select stringlike defects.

### Minimal repair

A cross-species reaction such as (29) is logically necessary.  A tension or
free-energy law is also necessary to decide the direction of that chemistry.

---

# 6. Derived rank drift

## 6.1 Averaged birth-death chain

When defect collision/chemistry mixes faster than rank changes, average
(34)--(35) over its conditional stationary distribution at fixed \(s\).  The
Poissonized rank generator is

\[
\overline{\mathcal L}_{\rm rank}f(s)
=
b_s[f(s+1)-f(s)]
+
d_s[f(s-1)-f(s)],
\tag{48}
\]

where

\[
b_s
=
\Theta_+^{-1}
\left[
(D-s)
\sum_p A_pc_p(s+1)
-
E_+
\right]_+,
\tag{49}
\]

\[
d_s
=
\Theta_-^{-1}
\left[
s
\sum_p B_pr_p(s)
-
\Sigma_-
\right]_+.
\tag{50}
\]

For product-Poisson defect equilibrium,

\[
A_p
=
\frac12\epsilon_p z_p^2,
\qquad
B_p
=
\tau_pz_p.
\tag{51}
\]

The derived mean rank drift is

\[
\overline{\mathcal L}_{\rm rank}s
=
b_s-d_s.
\tag{51a}
\]

Whenever all adjacent rates are positive, define the discrete effective
potential, up to an additive constant, by

\[
U_{\rm eff}(s+1)-U_{\rm eff}(s)
=
-\log\frac{b_s}{d_{s+1}}.
\tag{51b}
\]

Its minima are determined by the rates; no preferred rank is inserted.

For finite state spaces, the standard Poisson-equation averaging argument gives
convergence of the slow rank process to (48) as the chemistry/rank timescale
ratio tends to zero.  A uniform fast-generator spectral gap gives a finite-time
error of order that ratio.  This is a controlled asymptotic theorem, not a
claim that every microscopic string gas is already in that limit.

## 6.2 Exact sharp-intersection theorem

Let

\[
s_p=2p+1.
\tag{52}
\]

Assume a single species \(p\) and the zero-thickness limit

\[
c_p(s)
=
\begin{cases}
1,&s\le s_p,\\
0,&s>s_p.
\end{cases}
\tag{53}
\]

Assume

\[
0<E_+<
\min_{s<s_p}
(D-s)A_p,
\tag{54}
\]

\[
0<\Sigma_-<
\min_{s>s_p}
sB_p.
\tag{55}
\]

## Theorem 5 — rank revealed by the DCS generator

Under (53)--(55),

\[
b_s>0,\ d_s=0
\quad(s<s_p),
\tag{56}
\]

\[
b_{s_p}=d_{s_p}=0,
\tag{57}
\]

\[
b_s=0,\ d_s>0
\quad(s>s_p).
\tag{58}
\]

Thus \(s_p\) is the unique absorbing rank and every initial rank reaches it
almost surely.

For the birth-death version,

\[
\mathbb E_s\tau_{s_p}
=
\sum_{k=s}^{s_p-1}\frac1{b_k}
\qquad(s<s_p),
\tag{59}
\]

\[
\mathbb E_s\tau_{s_p}
=
\sum_{k=s_p+1}^{s}\frac1{d_k}
\qquad(s>s_p).
\tag{60}
\]

For the threshold PDMP, let

\[
\gamma_+
=
\min_{s<s_p}
\frac{(D-s)A_p-E_+}{\Theta_+},
\tag{61}
\]

\[
\gamma_-
=
\min_{s>s_p}
\frac{sB_p-\Sigma_-}{\Theta_-}.
\tag{62}
\]

Then

\[
\tau_{s_p}
\le
\frac{|s(0)-s_p|}
{\min(\gamma_+,\gamma_-)}.
\tag{63}
\]

### Proof

For \(s<s_p\), both \(s\) and \(s+1\) are at or below the clean-intersection
threshold.  Hence \(c_p(s+1)=1\) and \(r_p(s)=0\), proving (56).

At \(s=s_p\), the post-release sector has \(s_p+1\), so
\(c_p(s_p+1)=0\), while \(r_p(s_p)=0\), proving (57).

For \(s>s_p\), both \(c_p(s+1)=0\) and \(r_p(s)=1\), proving (58).
The hitting-time formulas are the sums of independent one-step waiting times.
The deterministic bound follows from the progress-rate lower bounds.

The generator never compares \(s\) with \(s_p\).  The comparison appears only
in the proof after the zeros of the physical rates have been computed.

## 6.3 Finite-width stationary law

When all \(b_s,d_s\) are positive, the chain is irreducible and has stationary
law

\[
\pi_0^{-1}
=
1+
\sum_{s=1}^{D}
\prod_{k=0}^{s-1}
\frac{b_k}{d_{k+1}},
\tag{64}
\]

\[
\pi_s
=
\pi_0
\prod_{k=0}^{s-1}
\frac{b_k}{d_{k+1}}.
\tag{65}
\]

Define

\[
\rho_s=\frac{b_s}{d_{s+1}}.
\tag{66}
\]

A unique stationary mode \(s_*\) is present when

\[
\rho_s>1
\quad(s<s_*),
\qquad
\rho_s<1
\quad(s\ge s_*).
\tag{67}
\]

The stability margin is

\[
g_{\rm mode}
=
\min
\left\{
\inf_{s<s_*}\log\rho_s,\,
\inf_{s\ge s_*}-\log\rho_s
\right\}.
\tag{68}
\]

A zero of the mean drift \(b_s-d_s\) is not enough.  Condition (67), or an
equivalent negative local linearization, is required.

---

# 7. Defect-species competition and whether \(p=1\) dominates

## 7.1 Detailed-balance stationary chemistry

Under (30), the product-Poisson law

\[
\pi_{\rm def}(n)
=
Z^{-1}
\prod_{p=1}^{P_{\max}}
\frac{z_p^{n_p}}{n_p!}
\tag{69}
\]

is reversible for the fragmentation/recombination reactions.

Let

\[
z_p=e^{-\beta F_p}.
\tag{70}
\]

Assume the strict fragmentation free-energy hierarchy

\[
F_p
\ge
pF_1+(p-1)\Delta,
\qquad
\Delta>0.
\tag{71}
\]

Then

\[
z_p
\le
z_1^p
e^{-\beta(p-1)\Delta}.
\tag{72}
\]

If \(z_1\le1\),

\[
\sum_{p\ge2}z_p
\le
z_1
\frac{e^{-\beta\Delta}}
     {1-e^{-\beta\Delta}}.
\tag{73}
\]

The strict inequality \(\Delta>0\) defines an open parameter region.

Point defects \(p=0\) may be present in the complete microscopic theory, but
they do not carry extended winding stress and are not rank-active in
(34)--(35).  The reason they are rank-inactive must itself come from the
microscopic charge algebra.

## 7.2 Stability of the string-selected rank

Let \(b_s^{(1)},d_s^{(1)}\) denote the pure-string rates and let their unique
stationary mode be three with gap \(g_1>0\) as in (68).

Let mixed-species rates be

\[
b_s=b_s^{(1)}+\delta b_s,
\qquad
d_s=d_s^{(1)}+\delta d_s.
\]

## Theorem 6 — open \(p=1\)-dominance region

If

\[
\sup_s
\left|
\log
\frac{b_s/d_{s+1}}
     {b_s^{(1)}/d_{s+1}^{(1)}}
\right|
<
g_1,
\tag{74}
\]

then the mixed-species chain has the same unique mode \(s_*=3\).

If the rate coefficients grow at most exponentially with \(p\), the fugacity
bound (72) makes (74) hold for all sufficiently large \(\beta\Delta\).  Hence
there is an open mesoscopic parameter region in which \(p=1\) dominates the
rank dynamics.

### Proof

For \(s<3\), the pure log ratio is at least \(g_1\).  Perturbation by less than
\(g_1\) leaves it positive.  For \(s\ge3\), the pure log ratio is at most
\(-g_1\); the same perturbation leaves it negative.  Equation (67) therefore
still has unique mode three.

The second statement follows because (72) bounds every higher-species
contribution by a convergent geometric series.

## What has and has not been explained

The theorem proves that a fragmentation free-energy hierarchy can make
strings dominate on an open region.  It does not derive the hierarchy (71)
from the Greene--Kabat--Marnerides dynamics or from another audited fundamental
action.

Thus the precise minimal extra physical term is:

> a species-changing reaction network plus a microscopic free-energy/charge
> law for which stringlike defects are the lightest stable rank-active
> indecomposable objects.

Without that term, \(p=1\) is an initial condition, not an explanation.

---

# 8. Pre-quotient source/readout coupling

## 8.1 Linearized microscopic transfer

Linearize the continuous state equations around a mesoscopic state \(X\):

\[
\dot\xi
=
\mathbb A_X\xi
+
W u,
\qquad
y=W^\vee\xi.
\tag{75}
\]

The matrix \(\mathbb A_X\) acts on the complete space (24) and contains:

- the full carrier two-jet block;
- all field polarizations;
- defect relaxation modes \(-\Omega_{p,\ell}\);
- mediator and reservoir fluctuations.

The transfer matrix is (8).

No event projector is used to define \(W\), \(u\) or \(y\).

## 8.2 Microscopic observability

Define the finite-time observability Gram (9).

## Theorem 7 — pre-quotient non-hiding criterion

For finite-dimensional \(\mathcal H_{\rm pre}\), the following are equivalent.

1. \(\ker\mathcal O_X(T)=0\) for some \(T>0\).
2. No nonzero microscopic response state is invisible to every port record.
3. The Hautus condition holds for every eigenvalue \(z\) of \(\mathbb A_X\):

   \[
   \operatorname{rank}
   \begin{pmatrix}
   zI-\mathbb A_X\\
   W^\vee
   \end{pmatrix}
   =
   \dim\mathcal H_{\rm pre}.
   \tag{76}
   \]

### Proof

This is the finite-dimensional observability theorem applied before any
quotient.

A full readout only after replacing \(\mathcal H_{\rm pre}\) by
\(\Pi\mathcal H_{\rm pre}\) proves nothing about hidden microscopic directions.

## 8.3 Active two-jet Green matrix

At a rank state \(\Pi\), the active branch response is the restriction of
(75), not an independently supplied operator.  Let

\[
G_{\Pi,x}
\]

be the complete finite two-jet transfer matrix emitted by the linearization.
The control must:

1. register all entries needed by the bounded two-jet class;
2. verify \(G_{\Pi,x}\) is invertible;
3. form

   \[
   L_{\Pi,x}=G_{\Pi,x}^{-1};
   \tag{77}
   \]

4. verify algebraic order at most two;
5. compute

   \[
   p_{L,x}
   =
   \ell_{L,x}|_{K_x};
   \tag{78}
   \]

6. verify \(p_{L,x}\ne0\).

The neutral reconstructor then uses (10).  It is not given \(C\) or
\(q_\Pi\).

---

# 9. Multi-field common-cone dynamics

## 9.1 Exact mediator contraction

Let

\[
E_a
=
\mathsf P_a^{\rm pre}-C\otimes K_a.
\]

Under (23),

\[
\frac{d}{dt}\|E_a\|_F^2
=
-2\gamma_a\|E_a\|_F^2.
\tag{79}
\]

Thus

\[
\|E_a(t)\|_F
\le
e^{-\gamma_at}\|E_a(0)\|_F.
\tag{80}
\]

This contraction is dimension-neutral and uses the dynamical carrier tensor
\(C\), not a supplied reconstructed line.

At a rank reset, the active tensor is obtained by restriction.  Therefore

\[
E_{a,\Pi^\pm}
=
E_a|_{\operatorname{Sym}^2(\operatorname{im}\Pi^\pm)^*}.
\tag{81}
\]

Restriction cannot increase the Frobenius norm:

\[
\|E_{a,\Pi^\pm}\|_F
\le
\|E_a\|_F.
\tag{82}
\]

Hence the common-cone residual obeys the required jump inequality.

## Theorem 8 — common-cone no-go without a mediator

If the generator contains no term coupling different field kinetic tensors and
each \(\mathsf P_a^{\rm pre}\) evolves independently, then the difference
between two field principal tensors is not forced to contract.  In particular,
a state with two inequivalent cones can remain invariant.

Therefore worldvolume collision geometry alone does not imply a universal
multi-field cone.  A universal mediator or another microscopic equivalence
principle is a logically separate physical term.

## Strong fixed-cone certification

Even with (79), the operational claim still quantifies over every feasible
symbol and factor as required by response 0005.  The generator-level
contraction is not a substitute for:

\[
\mathsf P_a=q\otimes K_a,
\qquad
\inf_{\rm feasible}\sigma_{\min}(K_a)>0.
\tag{83}
\]

---

# 10. One-time hyperbolicity and ordered response

## Theorem 9 — signature-sector obstruction

Let \(C(t)\) be a continuous path of nondegenerate real symmetric tensors.
Then its inertia is constant.

Suppose every rank release extends \(q_\Pi\) by a positive direction and every
reconfinement removes a positive direction.  Then the number of negative
directions of \(q_\Pi\) is invariant under the full DCS flow.

### Proof

Eigenvalues of a continuous symmetric path can change sign only by crossing
zero.  Nondegeneracy forbids the crossing.  Adding or removing a positive
direction leaves the negative index unchanged.

### Consequence

The DCS rank generator does not select one time.  It has an open index-one
viability sector, but a state beginning with two negative directions remains
in a two-time sector unless it crosses a degenerate configuration.

A microscopic term that makes index one the unique attractive nondegenerate
sector is still missing.  Writing a penalty \((n_--1)^2\) would merely encode
the answer and is not accepted.

## Physical time component

The Markov or relaxation parameter used in (27) is not a spacetime coordinate.

A directed physical response requires a port-order asymmetry.  Define the
reversal-odd transfer part

\[
\mathcal A_{ij}(z)
=
\mathcal G_{ij}^{\rm ret}(z)
-
\mathcal G_{ji}^{\rm ret}(-z).
\tag{84}
\]

If all registered transfer data are even under port reversal,

\[
\mathcal A_{ij}=0,
\tag{85}
\]

the physical time component remains unresolved even when the principal form is
Lorentzian.

Only after a nonzero component-pure directed germ is reconstructed may the
response-0005 \(\mathbb Z_2\) no-flip theorem select a time half-cone.

---

# 11. Same-spectrum departure

## 11.1 Schur-complement transfer

Split the pre-quotient linearization into active jet and defect modes:

\[
\mathbb A_X
=
\begin{pmatrix}
A_J & G_{Jd}\\
G_{dJ} & -\Omega_d
\end{pmatrix}.
\tag{86}
\]

The active transfer contains the Schur complement

\[
A_{\rm eff}(z)
=
A_J
+
G_{Jd}(z+\Omega_d)^{-1}G_{dJ}.
\tag{87}
\]

At

\[
|z|\ll\Omega_{\min},
\]

the defect block can be adiabatically eliminated.  At

\[
|z|\simeq\Omega_{\min},
\tag{88}
\]

the same block produces an additional pole or leakage direction.

No new response channel is inserted.

## 11.2 Rank-rate/pole identity

For one dominant species, define

\[
A_p=\epsilon_p\binom{n_p}{2},
\qquad
B_p=\tau_pn_p.
\]

The pre-barrier per-direction slopes are

\[
a_s^+
=
A_pc_p(s+1),
\qquad
a_s^-
=
B_pr_p(s).
\tag{89}
\]

Equations (32)--(33) imply

\[
\boxed{
\frac{a_{s-1}^+}{a_s^-}
=
\frac{A_p}{B_p}
\frac{\bar\Gamma_p(s)}{\Omega_p}.
}
\tag{90}
\]

The response departure pole is

\[
\omega_{\rm dep}=\Omega_p
\tag{91}
\]

up to the calibrated damping convention.

For strings, substitution of (2) gives (13).

## 11.3 Attraction-time relation

In the threshold PDMP, a one-step release time is

\[
\tau_\uparrow(s)
=
\frac{\Theta_+}
{
[(D-s)A_1c_1(s+1)-E_+]_+
},
\tag{92}
\]

and a one-step reconfinement time is

\[
\tau_\downarrow(s)
=
\frac{\Theta_-}
{
[sB_1r_1(s)-\Sigma_-]_+
}.
\tag{93}
\]

Through (2)--(3), the attraction times, impact distribution, radius, dilaton
and departure pole are not independent fit parameters.

The generator is falsified if:

- measured rank transition rates vary with \(R,b,\varphi\) differently from
  (2)--(3);
- no pole or leakage appears near the fitted \(\Omega_p\);
- a high-bandwidth response appears without a corresponding defect spectral
  mode;
- the inferred pole cannot reproduce the clearance/persistence ratio (90).

---

# 12. Repaired microscopic selection theorem

## 12.1 Raw microscopic fiber

Let the finite microscopic records be \(\mathscr D\).  The raw fiber is

\[
\mathfrak M_{\mathscr D}
=
\left\{
M:
\operatorname{Pred}_{\rm micro}(M)\in\mathscr D,\ 
M\text{ obeys only predeclared energy, complexity and order bounds}
\right\}/\mathcal G_{\rm micro}.
\tag{93a}
\]

Rank three, \(p=1\), regularity, one-time hyperbolicity, common-cone truth,
observability, completeness and successful selection are not membership
conditions.

## 12.2 Actual target stratum

For a microscopic candidate \(M\), define \(Z_I(M)\) without reference to
successful certification.

A state \(X\) belongs to \(Z_I(M)\) when, as a fact about the candidate state
and for every scale \(\lambda\) in a nonzero interval \(I\):

1. the actual released event rank is four;
2. the actual active branch is regular;
3. the actual carrier tensor has ordered inertia \((1,3)\);
4. every actual field tensor is \(q_\Pi\otimes K_a\) with \(K_a\) invertible;
5. the actual response atlas glues the cone by tangent congruence;
6. the actual Lorentz bundle is time-orientable and the actual directed records
   select one component;
7. the actual scale maps preserve old cotangent directions.

This definition contains no word such as “certified” or “reconstructed”.
A positive theorem separately requires

\[
Z_I(M)\ne\varnothing
\tag{93b}
\]

for every microscopic candidate in the claim.

## 12.3 Forward tube

Let \(\mathcal U_I(M)\) be a positive-radius set on which:

- energy and occupation bounds hold;
- the rank-flux separation margin is positive;
- the fragmentation free-energy gap is positive;
- pre-quotient observability has zero kernel;
- field-factor invertibility margins are positive;
- carrier and overlap tensors remain nondegenerate;
- every reset map is defined;
- the response residual does not increase at a reset.

Trajectories must remain in this tube until they hit \(Z_I(M)\).

## 12.4 Hybrid Lyapunov function

In the exact sharp single-string sector, let \(s_*=3\) be the rank derived by
Theorem 5.  At any non-target rank only one of the progress clocks is active.
Put

\[
c(X)=h_+(X)+h_-(X).
\]

Define

\[
V_{\rm rank}(X)
=
\begin{cases}
|s-s_*|-c(X),&s\ne s_*,\\
0,&s=s_*.
\end{cases}
\tag{94}
\]

Let \(\mathcal F_{\rm chem}\) be the detailed-balance free-energy distance to
the \(p=1\)-dominated chemistry region, and let

\[
V_{\rm con}
=
\sum_a\|E_a\|_F^2.
\]

Set

\[
V
=
V_{\rm rank}
+
\alpha\mathcal F_{\rm chem}
+
\beta V_{\rm con}.
\tag{95}
\]

## Theorem 10 — source-derived hybrid arrival theorem

This theorem is for the deterministic mass-action/PDMP kinetic reduction.
For the finite stochastic chemistry, the analogous statement is a
Foster--Lyapunov concentration theorem and does not give a pathwise worst-case
arrival time without an additional bounded-waiting artifact.

Assume, uniformly over the complete microscopic raw candidate fiber:

1. the sharp or barrier-separated rate conditions of Theorem 5;
2. a positive fragmentation dissipation bound

   \[
   D^+\mathcal F_{\rm chem}
   \le-\gamma_{\rm chem}
   \quad
   \text{outside the species target set};
   \]

3. the mediator contraction (79);
4. complete non-Zeno trajectories in the forward tube;
5. every rank reset decreases \(|s-s_*|\) by one and satisfies
   (82);
6. no chemistry reset increases \(\mathcal F_{\rm chem}\);
7. the target stratum is forward invariant.

Then, outside \(Z_I(M)\),

\[
D^+V
\le
-\gamma_{\min}<0
\tag{96}
\]

on continuous pieces, and at every reset

\[
V(X^+)\le V(X^-).
\tag{97}
\]

If

\[
V_{\max}
\le
\gamma_{\min}L_{\min},
\tag{98}
\]

every trajectory in the forward tube reaches \(Z_I(M)\) before
\(L_{\min}\).

### Proof

The rank part decreases at the derived progress rate.  The chemistry and
mediator terms decrease by assumptions 2--3.  Equations (82) and the
one-step rank motion prove the jump inequality.  Piecewise integration of
(96), together with (97), gives the finite arrival bound.  Non-Zeno
completeness ensures the trajectory exists through arrival.

## Composition with operational reconstruction

Only after Theorem 10 has established actual arrival is response 0005 applied
to the data emitted by each state.  Certification of selection requires, for
every microscopic interval-consistent candidate:

- actual target truth \(X\in Z_I(M)\) after arrival;
- successful operational reconstruction at every scale in \(I\);
- the three independent completeness artifacts;
- scoped field/polarization completeness;
- one full microscopic/response structure orbit;
- resolved non-\(3+1\) predecessor with pre-quotient non-hiding.

Missing observability, chemistry, coverage, arrival or response evidence gives
`inconclusive`, not target exclusion.

## Theorem 11 — microscopic selection verdicts

First test the raw fiber (93a).

- If \(\mathfrak M_{\mathscr D}=\varnothing\), report microscopic
  class/data incompatibility separately.
- For a nonempty fiber, return `certified within class` only if every
  \(M\in\mathfrak M_{\mathscr D}\) has a nonempty target stratum, every
  trajectory in the declared basin satisfies Theorem 10, the complete
  operational reconstruction route succeeds after arrival, all externally
  scoped completeness artifacts hold, and all resulting microscopic/response
  packages occupy one registered full-structure orbit.
- Return `class-excluded` only if every
  \(M\in\mathfrak M_{\mathscr D}\) has an exact or positively separated
  obstruction to the actual existence or attraction of \(Z_I(M)\).
- Return `inconclusive` in every other nonempty-fiber case.

A missing fragmentation proof, non-hiding proof, response pole, rank margin,
common-cone artifact or time record is a route failure.  It is not by itself a
target obstruction.

---

# 13. Minimal executable experiment

## 13.1 Finite state

Use

\[
D=7,
\qquad
P_{\max}=3,
\qquad
E_{\max}<\infty.
\]

Represent:

- every projector rank \(1,\ldots,D+1\);
- defect species \(p=1,2,3\);
- finite orientation and impact grids;
- reservoir clocks \(h_\pm\);
- one dynamical carrier tensor \(C\);
- two field sectors;
- a full pre-quotient port matrix \(W\);
- explicit defect modes with poles \(\Omega_p\).

No target rank is supplied.

## 13.2 Reaction and rate data

Use (2) for the \(p=1\) source-derived slice.  For \(p=2,3\), use an explicitly
labeled test kernel with the correct direct-intersection threshold and finite
width.

Implement (29) with detailed balance.  Scan the free-energy gap \(\Delta\)
through positive and negative values.

Compute (32)--(35) and integrate the threshold PDMP.

## 13.3 Acceptance tests

The code must discover the rank zeros from the rates.

For a pure \(p\) zero-thickness run:

\[
p=1\Rightarrow s_*=3,
\qquad
p=2\Rightarrow s_*=5.
\tag{99}
\]

For mixed species, record:

\[
\operatorname*{arg\,max}_s\pi_s,
\qquad
g_{\rm mode},
\qquad
\sum_{p\ge2}\frac{z_p}{z_1}.
\tag{100}
\]

The \(p=1\)-dominance claim is accepted only when (74) is verified.

## 13.4 Response replay

At each rank:

1. construct \(\mathbb A_X,W\) on the full pre-quotient state;
2. verify the Hautus condition (76);
3. emit the transfer (8);
4. restrict to the active two-jet sector;
5. invert the complete Green matrix;
6. reconstruct the event dimension and principal line without passing
   \(\Pi,C,q\) or signature;
7. perform full polarization tomography;
8. verify the overlap/time package.

The predecessor must be resolved before quotienting.

## 13.5 Departure sweep

Measure the defect pole \(\Omega_1\).  Sweep:

\[
R,\quad b,\quad\varphi,\quad\text{source bandwidth}.
\]

Compare measured rank fluxes and attraction times with (13), (90), (92) and
(93).  The high-bandwidth response must arise from the existing defect block in
(86).

---

# 14. Mandatory adversaries

## 14.1 Controller keyed to \(s_p\)

Replace (34)--(36) by a rule that directly inspects
\(\operatorname{sign}(s-s_p)\).

**Result:** rejected by the non-encoding audit.  Replacing the numeral three by
\(2p+1\) does not repair it.

## 14.2 Birth-only or death-only generator

Set the persistent-stress coupling or clearance coupling to zero.

**Result:** the process has no bidirectional basin.  It runs to a boundary or
cannot leave one side of the target.

## 14.3 Zero drift with repelling linearization

Choose rates with

\[
b_{s_0}=d_{s_0}
\]

but

\[
\rho_{s_0-1}<1<\rho_{s_0}.
\]

**Result:** \(s_0\) is not a stable stationary mode.  A zero of \(b-d\) is
insufficient; condition (67) fails.

## 14.4 \(p=2\) still returns three

Run the pure-\(p=2\) kernel through the same code.

**Required result:**

\[
s_*=5.
\]

If the code returns three, a hidden target has been inserted.

## 14.5 Mixed state without \(p=1\) dominance

Choose \(\Delta\le0\), or fugacities for which higher-\(p\) flux violates
(74).

**Result:** rank three is not certified.  The chain may select another mode or
be multimodal.  This is not repaired by reporting the string-sector mode
alone.

## 14.6 Bad rank reset

Choose a reset that:

- increases \(\sum_a\|E_a\|^2\);
- destroys the Green inverse;
- changes inertia through an untracked zero crossing;
- discards pre-quotient response records.

**Result:** (97) fails and the hybrid selection theorem abstains.

## 14.7 Readout complete only after quotient

Choose \(W\) with a nonzero kernel on \(\mathcal H_{\rm pre}\), but make
\(W|_{\Pi\mathcal H_{\rm pre}}\) invertible.

**Result:** microscopic non-hiding fails.  A resolved non-\(3+1\) predecessor
has not been proved.

## 14.8 Even port-reversal transfer

Impose

\[
\mathcal G_{ij}^{\rm ret}(z)
=
\mathcal G_{ji}^{\rm ret}(-z).
\]

**Result:** the physical time component is unresolved.  The DCS flow parameter
cannot replace it.

## 14.9 Inequivalent field cones

Set

\[
\mathsf P_1=C\otimes I,
\qquad
\mathsf P_2=(C+R)\otimes I,
\qquad
R\not\propto C,
\]

and remove the mediator coupling.

**Result:** the off-common-cone witness is nonempty.  Visible rank may be four,
but the full target fails.

## 14.10 Manually injected high-bandwidth channel

Append a response pole that is absent from \(\mathbb A_X\) and does not enter
(32)--(35).

**Result:** it fails the same-spectrum identities (90)--(93) and is not a
mechanism-derived departure.

---

# 15. Thirty-day kill program

## Days 1--5 — generator and exact rank theorem

Implement the finite PDMP and its Poissonized birth-death reduction.  Verify:

- \(\mathcal L1=0\);
- bounded total rates;
- no Zeno resets;
- equivariance under random \(O(E)\) frame changes;
- Theorem 5 for \(p=1,2,3\).

Search the code for any branch keyed to \(s_p\) or target rank.

## Days 6--10 — species chemistry

Implement (29)--(30).  Verify the product-Poisson stationary law and the
fugacity bound.  Scan \(\Delta,\beta,z_1\), compute the mixed rank chain and
test (74).

Kill the \(p=1\)-dominance claim if no positive-volume parameter region has a
strict rank-three mode gap.

## Days 11--15 — pre-quotient response

Build \(\mathbb A_X,W\) before quotienting.  Compute the full observability
Gram and Hautus ranks.  Delete microscopic port directions and verify that
post-quotient completeness does not pass.

Emit complete two-jet Green matrices and replay response 0005 anonymously.

## Days 16--20 — mediator and resets

Implement (22)--(23), full field tensors and the exact restriction resets.
Verify (79)--(82) under random rank changes.

Run inequivalent-cone and inertia-changing reset adversaries.

## Days 21--25 — same-spectrum departure

Insert defect modes only through the block (86).  Measure \(\Omega_p\), rank
fluxes and transfer poles.  Test (90) and the string relation (13) under radius
and impact sweeps.

Kill the generator if a fitted rank clock and the measured departure pole
cannot be described by one \(\Omega_p\).

## Days 26--30 — closed-loop audit

Construct the actual microscopic target stratum \(Z_I(M)\), forward tube and
Lyapunov function.  Verify complete trajectories, piecewise absolute
continuity, no Zeno behavior and (97).

Run all ten adversaries and the repaired universal verdict engine.

---

# 16. Evidence ledger

| status | content |
|---|---|
| `source-derived exact` | The algebraic form of the Greene--Kabat--Marnerides string interaction-rate slice (2), as stated in its heavy/dilute impact-parameter model; the authorship and scope of arXiv:1212.2115. |
| `source-derived conditional/numerical` | Using the string rate as the collision input of a homogeneous kinetic reduction; impact/radius averaging; any claim that its source regime supplies the strict barrier inequalities over an open cosmological basin. |
| `newly proposed law` | The clearance/stress barrier coupling, exponential-race reduction, fragmentation/recombination chemistry, universal carrier mediator, pre-quotient port Hamiltonian and their coupled PDMP. |
| `executable control` | The finite-energy finite-state generator; exact sharp-rank theorem; birth-death stationary law; product-Poisson chemistry; pre-quotient Hautus test; anonymous two-jet replay; same-spectrum pole/rate identities; adversary suite. |
| `open gate` | Fundamental derivation of the fragmentation hierarchy making strings the lightest stable rank-active species; microscopic derivation of the universal mediator; dynamical selection of one-time index-one hyperbolicity; realistic continuous-impact raw-fiber certification. |

---

# 17. Minimal theorem and remaining hard gate

> **Source-derived mesoscopic rank-selection theorem.**  
> Let a bounded microscopic candidate family contain anonymous carrier
> projectors, defect microstates of variable worldvolume dimension, physical
> energy and stress reservoirs, pre-quotient ports, complete field tensors and
> defect relaxation modes.  Let its generator be (27)--(45), with no
> target-keyed rate branch.
>
> Suppose the collision kernel and defect pole determine clearance and
> persistence by (32)--(33), the rank barriers satisfy the strict separation
> inequalities, the chemistry has a positive \(p=1\)-dominance gap, and the
> pre-quotient observability kernel is zero.
>
> Then the rank drift is derived from the generator.  In the sharp pure-\(p\)
> sector its unique target is \(s=2p+1\); in the open chemistry region of
> Theorem 6 the mixed system retains the string-sector target \(s=3\).  Complete
> hybrid trajectories satisfy the reset inequality and the finite-arrival
> budget.  The same linearized generator emits the Green data and the defect
> pole that sets the response departure.
>
> Composed with the repaired all-candidate response theorem, this gives a
> conditional operational selection certificate whenever the actual target
> stratum additionally has index-one hyperbolicity, fixed-\(q\) all-field
> factorization, complete overlap/time cocycles and one full microscopic
> structure orbit.

The generator obtained here is not the final fundamental answer.  The
remaining hard gate is

\[
\boxed{
\begin{gathered}
\text{derive from one microscopic action, rather than postulate,}\\
\text{(i) the fragmentation/free-energy law that makes \(p=1\) the lightest
rank-active species,}\\
\text{(ii) a universal carrier mediator, and}\\
\text{(iii) an attractive nondegenerate index-one sector with an ordered
response component.}
\end{gathered}
}
\tag{101}
\]

Until (101) is closed, the project has a source-anchored mesoscopic generator
for bidirectional rank release, a precise species-selection no-go, a minimal
chemical repair, a pre-quotient response coupling and a same-spectrum
departure, but not a fundamental derivation of the complete visible
\(3+1\) package.

---

# References

1. Brian Greene, Daniel Kabat and Stefanos Marnerides,
   *Dynamical Decompactification and Three Large Dimensions*,
   arXiv:0908.0955.
2. Brian Greene, Daniel Kabat and Stefanos Marnerides,
   *On three dimensions as the preferred dimensionality of space via the
   Brandenberger--Vafa mechanism*,
   arXiv:1212.2115.
