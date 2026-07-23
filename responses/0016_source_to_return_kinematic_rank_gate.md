---
brief: 0016
source: browser-hosted GPT collaboration and independent local derivation
captured: 2026-07-23
baseline_commit: c73fc0e8b6286c281b8577a9879de5e7c15fdc4a
status: locally_verified_conditional_source_ceiling
artifacts:
  - artifacts/0016/probe_0016.py
  - artifacts/0016/test_probe_0016.py
  - artifacts/0016/source_to_return_kinematic_probe.json
---

# Response 0016 — source-to-return kinematic-rank gate

## Executive result

This round removes `frame_arity=3` from the list of facts that may be treated
as physical input.

For two local \(p\)-brane carriers the invariant encounter object is the
derivative of their separation from the diagonal.  Its rank satisfies

\[
a(x)=\operatorname{rank}D\Phi_{e,x}\le \min(d,2p+1).
\]

For F1 strings, \(a\le3\).  Rank three is generic only in a declared
nondegenerate local pair-jet ensemble: the two string tangents must be
non-collinear and the relative velocity must leave their span.  Global
opposite winding does not imply this.  A strictly straight pair wound in
opposite directions on the same cycle has \(a\le2\).

The \(D-4=d-3\) impact space in the Jackson--Jones--Polchinski (JJP)
calculation is the normal space to two non-collinear string tangents and a
relative-velocity direction.  The momentum transfer \(q\) lies in that normal
space; it is not a third incoming direction.  Applying the same dimension to
a strictly straight, same-cycle, opposite-winding pair therefore requires an
additional local tangent/wiggle preparation that the cited Boltzmann model
does not provide.

The finite registered process also conserves its constructor arity exactly.
It cannot select arity three from an arity-neutral basin.  Replacing its three
role names by the physical pair jet exposes a real source mechanism:
impact-codimension suppression.  Across a predeclared family of
effective-source models, that mechanism supplies, at strongest, a conditional
source-side **three-ceiling**.  It does not by itself supply strict
three-selection, an anonymous visible-rank ceiling, or a time direction.

Claim classes used below are:

- **[source]** `primary-source derived`;
- **[theorem]** `exact theorem about a declared geometric model`;
- **[closure]** `derived from a newly proposed measurable closure`;
- **[probe]** `controlled numerical probe`;
- **[no-go]** `no-go/underdetermination`;
- **[open]** `open gate`.

## 1. Three integers that remain distinct

\[
\boxed{
p=\text{carrier dimension},\qquad
a=\text{local encounter kinematic rank},\qquad
m=\text{anonymous response-visible spatial rank}.
}
\]

The F1 statement \(p=1\) is microscopic.  The inequality \(a\le3\) is local
encounter geometry.  The value \(m\) is reconstructed only after the
source-to-return process has been attached to anonymous responses.  None of
these implications is reversible. **[theorem]**

## 2. Encounter-rank theorem

### 2.1 Invariant definition

Let \(X_i:\Sigma_i^p\times I\to(M^d,G)\) be two local embeddings.  An exact
intersection means that \((X_1,X_2)\) reaches the diagonal
\(\Delta_M\subset M\times M\).  A finite-impact event instead needs a
predeclared encounter section: for example the interior closest-approach
representative \(z_*\) in an injectivity-radius tube, with a deterministic
tie-breaking rule.  On the rectangular torus the local separation map is

\[
\Phi_e(\sigma,\sigma',t)
=\operatorname{Log}_{X_2(\sigma',t)}X_1(\sigma,t).
\]

At the selected event jet, parallel transport the columns to one target
tangent space and write

\[
J_e=D\Phi_e
=\bigl[T_1,\,-T_2,\,u\bigr],
\qquad
T_i=D_{\sigma_i}X_i,\quad u=v_1-v_2.
\]

Changes of world-volume coordinates multiply \(J_e\) on the right by an
invertible matrix; target coordinate changes multiply it on the left by an
invertible matrix.  Thus

\[
a(e)=\operatorname{rank}J_e
\]

is coordinate independent and

\[
a(e)\le\min(d,2p+1).
\]

The impact normal space is

\[
N_e=(\operatorname{im}J_e)^{\perp_G},
\qquad
\dim N_e=d-a(e).
\]

Equivalently, in a local frame,

\[
P_{N_e}=I-J_e(J_e^\top GJ_e)^+J_e^\top G
\]

is the \(G\)-orthogonal normal projector.

At an interior closest approach, the impact coordinate is the separate datum

\[
b_e=\Phi_e(z_*),\qquad J_e^\top G b_e=0,
\]

so \(b_e\in N_e\).  At a first-entry section one must instead record the
longitudinal phase and use \(b_e=P_{N_e}\Phi_e(z_*)\).  In either convention,
\(J_e\) determines \(a\) and \(N_e\), but it does **not** determine \(b_e\).
An exact diagonal hit is the special case \(b_e=0\). **[theorem]**

### 2.2 General position and its exact limitation

The matrices of rank below \(r=\min(d,2p+1)\) form a determinantal algebraic
set: all \(r\times r\) minors vanish.  Hence, if the pushforward pair-jet law
has a density with respect to Lebesgue measure on the attainable matrix space,
then \(\operatorname{rank}J_e=r\) almost surely.  More generally, for every
positive-probability connected analytic branch \(C\) of a constrained jet
manifold, let \(r_C\) be its maximal attainable rank.  If some
\(r_C\)-minor is not identically zero on \(C\) and the conditional law has a
density with respect to the branch volume, then
\(\operatorname{rank}J_e=r_C\) almost surely conditional on \(C\).  The full
source law may therefore be a mixture of branches with different generic
ranks.

This is a conditional general-position theorem.  Nambu--Goto, winding,
energy-shell or preparation constraints may instead place the entire law on a
lower-rank stratum. **[theorem]**

For F1, set \(J=[\tau_1,-\tau_2,u]\).  With nonzero tangents:

- \(a=3\) exactly when
  \(\dim\operatorname{span}\{\tau_1,\tau_2,u\}=3\);
- \(a=2\) when the tangents are independent and \(u\) lies in their plane,
  or when the tangents are collinear and \(u\) leaves their line;
- \(a=1\) when all nonzero columns lie on one line;
- \(a=0\) only when every column vanishes.

For \(d\ge3\), rank three is equivalently

\[
\det(J^\top GJ)>0.
\]

### 2.3 A physical open-condition margin

A singular-value magnitude is not defined until the encounter-parameter
units are fixed.  Register a target metric \(G_e\) and a domain/jet metric
\(H_e\), including the relative scale assigned to arc length and time.  The
squared singular values are the generalized eigenvalues of

\[
J_e^\top G_eJ_ev=\sigma^2H_ev.
\]

Equivalently, in \(G_e,H_e\)-orthonormal frames, define

\[
\widehat J_e=G_e^{1/2}J_eH_e^{-1/2}.
\]

The nondegenerate F1 stratum has a quantitative margin when

\[
\sigma_3(\widehat J_e)\ge\eta_{\rm kin}>0.
\]

Weyl's inequality gives the useful robustness certificate

\[
\|\delta\widehat J_e\|_2\le\epsilon<\eta_{\rm kin}
\quad\Longrightarrow\quad
\sigma_3(\widehat J_e+\delta\widehat J_e)
\ge\eta_{\rm kin}-\epsilon>0.
\]

Metric, tangent and velocity errors are therefore allowed when their
rewhitened combined operator perturbation stays below the registered margin.
A uniform positive margin is a sufficient certificate for a worst-case open
parameter cell, not a necessary condition for probabilistic stability.  A
source law may instead publish

\[
p_{\le2}=\Pr[\sigma_3=0],
\qquad
\Pr[0<\sigma_3<\varepsilon]\le r(\varepsilon)\to0,
\]

supporting a weaker probabilistic closure in which the lower-rank atom
\(p_{\le2}\) is retained explicitly. **[theorem]**

For the JJP local coordinates with unit tangents,

\[
\tau_1=e_1,\qquad
\tau_2=\cos\theta\,e_1+\sin\theta\,e_2,\qquad
u=ve_3,
\]

the unweighted Gram determinant and smallest singular value are

\[
\det(J^\top J)=v^2\sin^2\theta,
\qquad
\sigma_3(J)=
\min\!\left\{|v|,\sqrt{1-|\cos\theta|}\right\}.
\]

This displays both degeneracies rather than hiding them under the word
“generic.” **[theorem]**

### 2.4 World-volume intersection and the \(2p+1\) ceiling

Two \((p+1)\)-dimensional world volumes in \(D=d+1\) spacetime dimensions
intersect transversely only when

\[
2(p+1)-D\ge0
\quad\Longleftrightarrow\quad
d\le2p+1.
\]

The spatial encounter map has \(2p+1\) source parameters: two sets of \(p\)
carrier coordinates and one relative time.  For a full-rank pair jet its
normal dimension is

\[
\dim N_e=(d-(2p+1))_+.
\]

For \(p=1\), this becomes the familiar three-dimensional ceiling and,
above it, an impact space of dimension \(d-3\).  It is a statement about
carrier intersections.  It is not a theorem that the anonymous response
quotient has rank three. **[source, theorem]**

The general intersection count appears in
[Alexander--Brandenberger--Easson (2000)](https://arxiv.org/abs/hep-th/0005212).

## 3. The opposite-winding falsifier and the JJP/GKM domain

JJP computes the local collision of two straight strings at a nonzero angle.
Their two tangent zero modes span a two-torus with volume proportional to
\(l_1l_2\sin\theta\), and the second string moves in a third spatial
direction.  The probability contains a \(1/\sin\theta\) factor, so the
parallel limit is not an ordinary member of that single-crossing
normalization.  The residual momentum transfer is transverse to those three
incoming spatial directions, producing a \(D-4=d-3\) dimensional cross
section. See equations (3.1)--(3.8) of
[JJP (2005)](https://arxiv.org/abs/hep-th/0405229). **[source]**

[GKM (2009)](https://arxiv.org/abs/0908.0955) imports this
\(D-4\)-dimensional impact transform, then later models two strings moving
oppositely in one direction and wound oppositely around the same cycle.  For
the literal locally straight source state,

\[
\tau_2=-\tau_1,\qquad
J=[\tau_1,\tau_1,u],
\]

so

\[
a\le2,\qquad \dim N_e\ge d-2.
\]

If \(u\notin\operatorname{span}\{\tau_1\}\), the exact result is
\(a=2\), \(\dim N_e=d-2=D-3\).  If \(u\) is also tangent, \(a=1\).
The outgoing transfer \(q\in N_e^*\) cannot be inserted into \(J\) to remove
one of the dimensions that it is supposed to parametrize. **[theorem]**

There is a consistent conditional repair: local oscillator wiggles may make
\(\tau_1,\tau_2\) non-collinear even when their global winding charges are
opposite.  But the cited Boltzmann model supplies neither the conditional
tangent distribution nor a quantitative uniform-margin or tail certificate.
Its string
thickness \(\Delta x\) is a positional width, not a lower bound on the angle
or on \(\sigma_3\).  Hence:

> The JJP/GKM \(d-3\) impact dimension is source-faithful on the non-collinear
> local pair-jet stratum.  Its use for a strictly straight, same-cycle,
> opposite-winding pair requires an unprovided local preparation.

This is an upstream identification failure, not a disproof of the generic
intersection theorem. **[no-go]**

The old labels `(w,v,s)` must therefore not survive as three primitive
incoming roles.  The physical event data are the bundle pair

\[
(j,b),\qquad
j=(z_*,\tau_1,\tau_2,u,G,H),\qquad b\in N_j,
\]

where \(j\) determines \(a,N_j\) and any registered rank margin, while \(b\)
is the separate closest-approach/first-entry datum.  A scattering axis may be
an output inside \(N_j\); it cannot create incoming rank. **[theorem]**

## 4. Fixed-arity superselection theorem

Let the disjoint state space be

\[
\mathcal S=\bigsqcup_a\{a\}\times\mathcal S_a,
\]

and suppose the scheduled kernel is block diagonal:

\[
K\bigl((a,x),d\tau,\{b\}\times dy\bigr)
=\mathbf1_{\{a=b\}}K_a(x,d\tau,dy).
\]

Then for every trajectory, including killed trajectories before their killing
time,

\[
A_t=A_0.
\]

Consequently

\[
\Pr_\mu(A_t=a)=\Pr_\mu(A_0=a)
\]

for every initial law \(\mu\).  No stationary distribution, transient,
return schedule or response post-processing can turn this kernel into a
dynamical selector among arities. **[theorem]**

If \(q\) axes pass the registered radius predicate and a frame is an ordered
distinct \(a\)-tuple, exact enumeration gives

\[
N_{\rm valid}(q,a)
=a!\binom qa
=
\begin{cases}
q!/(q-a)!,&q\ge a,\\
0,&q<a.
\end{cases}
\]

Thus a fixed input \(a=3\) creates a hard onset at \(q=3\).  This is not by
itself malicious target encoding: the same formula becomes a legitimate
finite projection if \(a\) is first output by a source-faithful encounter
law.  It is nevertheless cardinality-threshold-confounded until that
upstream derivation exists, and even a physical \(a=3\) does not define
visible \(m=3\). **[theorem, no-go]**

## 5. Impact-codimension suppression theorem

### 5.1 Conditional reaction profile versus preparation

In the dilute semiclassical source domain, take the conditional large-impact
profile

\[
P_{\rm ann}(b\mid X)
=P_0(X)\exp[-\|b\|_{G_N}^2/\Delta^2(X)],
\qquad b\in N_e,
\]

with

\[
G_N>0,\qquad \Delta(X)>0,\qquad 0\le P_0(X)\le1.
\]

The Gaussian tail is inherited from the impact-parameter amplitude in its
source-valid high-\(b\), weak-coupling regime.  It is a reaction probability
conditional on an encounter and impact coordinate.  It is not a normalized
impact preparation, does not give an absolute first-hit clock, and does not
authorize extrapolation through the unresolved small-\(b\) core.  A physical
compiler must use a source-valid exact/eikonal core profile or route
out-of-domain events to the killed outcome; it may not silently clip a
probability. **[source, open]**

The GKM scheduled estimate \(t_r\simeq r/\bar v\) and its fresh random impact
draw at each recollision are numerical evolution prescriptions, not
consequences of the crossing-conditioned amplitude. **[source]**

### 5.2 Two target-neutral control preparations

Let \(c=\dim N_e\), \(\rho=r/\Delta\), and use \(G_N\)-orthonormal
coordinates.  Uniform impact in a \(c\)-ball gives

\[
g_c^{\rm ball}(\rho)
=c\int_0^1u^{c-1}e^{-\rho^2u^2}\,du
=\frac c2\rho^{-c}
\gamma\!\left(\frac c2,\rho^2\right),
\]

for \(c>0,\rho>0\), with continuous definitions
\(g_0=1\) and \(g_c(0)=1\).

Independent uniform coordinates in a \(c\)-box of half-width \(r\) give

\[
g_c^{\rm box}(\rho)
=\left[
\int_0^1e^{-\rho^2u^2}\,du
\right]^c
=\left[
\frac{\sqrt\pi}{2\rho}\operatorname{erf}\rho
\right]^c.
\]

For the declared mathematical surrogate in which the Gaussian is extended
over the whole ball or box, the averaged reaction probabilities are
\(P_0g_c\).  The integrals are exact for those controls.  Because both
supports include \(b=0\), using them as physical probabilities also declares
a small-\(b\) profile closure unless the source-valid core has independently
been supplied. **[closure, theorem]**

For \(c>0,\rho>0\), both factors strictly decrease with \(\rho\).  For the ball,

\[
\partial_\rho g_c^{\rm ball}
=-2\rho c\int_0^1u^{c+1}e^{-\rho^2u^2}\,du<0.
\]

For fixed \(\rho>0\), let \(U_c=V^{1/c}\) with
\(V\sim{\rm Uniform}(0,1)\).  Then \(U_c\) increases stochastically with \(c\)
while \(e^{-\rho^2u^2}\) decreases, so \(g_c^{\rm ball}\) strictly decreases
with \(c\).  The box result follows from
\(0<g_1^{\rm ball}<1\). **[theorem]**

The unit ball is contained in the unit box.  On the added box region the
radial Gaussian is no larger than its boundary value, whereas throughout the
ball it is no smaller.  Therefore

\[
g_c^{\rm ball}\ge g_c^{\rm box},
\]

with equality for \(c=0,1\) and strict inequality for
\(c\ge2,\rho>0\). **[theorem]**

For \(\rho\ge1,c>0\),

\[
e^{-1}\rho^{-c}
\le g_c^{\rm ball}(\rho)
\le \Gamma(c/2+1)\rho^{-c},
\]

\[
e^{-c}\rho^{-c}
\le g_c^{\rm box}(\rho)
\le
\left(\frac{\sqrt\pi}{2}\right)^c\rho^{-c}.
\]

The lower bounds integrate only the interval \(0\le u\le1/\rho\);
the upper bounds extend the integral to infinity. **[theorem]**

What survives the two preparations is the existence of codimensional
suppression, strict decrease with the size ratio, and algebraic
\(\rho^{-c}\)-scale bounds.  Exact constants and the comparison between
different \(c\) depend on the preparation.  An arbitrary source distribution
concentrated near \(b=0\) can erase the suppression, so no
preparation-independent probability theorem follows from the conditional
profile alone. **[no-go]**

### 5.3 Full-metric construction before any \(m\)

For one event in the full \(T^9\) source, the compiler computes only

\[
c_{\rm full}(e)=9-a(e).
\]

There is no variable response rank in that equation.  To recover the familiar
dimension comparison, define in advance a source-model family
\(\{X^{(\ell)}\}\) with \(\ell\) effectively extended spatial directions,
without using any response output to choose the family member.  For a
general-position F1 pair jet internal to each such source model,

\[
a_\ell=\min(\ell,3),
\qquad
c_\ell=\ell-a_\ell=(\ell-3)_+.
\]

For \(\ell=1,2\) the encounter rank is correspondingly one or two, not three.
For \(\ell\ge3\), the rank-three stratum gives the upper-side impact
codimension.  The formula is therefore a theorem about a predeclared
effective-source family.  Only after anonymous reconstruction may one test
whether its visible output \(m\) agrees with the source index \(\ell\); the
compiler is forbidden to receive `m`, visible count, target stratum or
response band. **[theorem]**

## 6. Why the result is a three-ceiling, not strict three-selection

Across that independently defined effective-source family, a
general-position F1 pair jet has zero impact codimension for
\(\ell\le3\) and positive impact codimension for \(\ell>3\).  Thus this
mechanism can penalize source models with more than three extended
directions, but it does not distinguish \(\ell=1,2,3\).  In a straight
opposite-winding stratum the corresponding local ceiling is lower because
\(a=2\).  None of this yet assigns an anonymous visible \(m\). **[theorem]**

A quantitative strict-selection theorem would need a source score that
separates a lower-side factor from the impact factor.  For example, let

\[
S_\ell(\theta)
=L_\ell(\theta)P_{0,\ell}(\theta)
g_{(\ell-3)_+}(\rho_\ell(\theta))
\]

on a predeclared open parameter cell \(U\).  A sufficient uniform condition is

\[
\inf_{\theta\in U}
\left[S_3(\theta)-\max_{\ell<3}S_\ell(\theta)\right]
\ge\delta_->0,
\]

\[
\inf_{\theta\in U}
\left[S_3(\theta)-\sup_{\ell>3}S_\ell(\theta)\right]
\ge\delta_+>0.
\]

Then the source-family member \(\ell=3\) has the strict score margin
\(\delta=\min(\delta_-,\delta_+)\).  The second inequality can be assisted by
impact-codimension suppression.  The first cannot.  Even these inequalities
would certify only a microscopic source score until a theorem transfers the
gap to anonymous entrant residence. **[theorem]**

[GKM (2012)](https://arxiv.org/abs/1212.2115) supplies a candidate
lower-side narrative through successive anisotropic scale-factor
fluctuations.  Its three-dimensional preference is conditional on the chosen
fluctuation statistics, fluctuations on a timescale
\(t_f\sim\sqrt{\alpha'}\), sufficient coupling before the dilaton rolls weak,
the initial ensemble and later homogenization.  The paper itself calls for a
derivation of the fluctuation statistics and timescale.  Those simulations do
not identify a uniform \(\delta_->0\) over an open source family.
**[source, no-go]**

The verdict of this round is therefore:

\[
\boxed{\texttt{three-ceiling}}
\]

for the predeclared effective-source family, conditional on its
general-position F1 strata, and not `strict three-selection`.  There is no
anonymous visible-rank conclusion at this stage. **[no-go]**

## 7. Minimal repaired physical interface

Let the full source state \(X\) include the metric and slow background,
world-sheet/oscillator states, winding charges, pair histories, reservoir
state and declared probe ports.  The missing object is a covariant
source-to-return Markov-renewal kernel

\[
\mathscr P_X
\bigl(
dT,dj,db,d\chi,dh',dX',d\Delta E_R,d\dagger
\mid h
\bigr).
\]

Here \(j\) is the selected near-encounter jet, including \(z_*,J_e,G,H\) and
the event-section metadata.  Since \(b\) lives in a normal space that varies
with \(j\), this is a bundle-valued kernel on

\[
\mathcal E_X
=\{(j,b):j\in\mathcal J_X,\ b\in N_j\},
\]

not a product kernel with \(b\) in one fixed Euclidean space.

Here:

- \(T\) is the holding time to the first hit or return, not only a
  conditional reaction rate; if an absolute clock is desired, current time
  must be a component of \(X\);
- the pair jet is source output and determines \(a,N_e\), while the event
  rule and separation jointly supply the separate \(b\);
- \(b\) is continuous full-metric impact/orientation data;
- \(\chi\) is the conditional reaction or miss channel;
- \(h'\) records the post-event history, without assuming iid redraw;
- \(X'\) is the updated source state;
- \(\Delta E_R\) closes the energy/charge/work ledger;
- \(\dagger\) is either a reference-measure reverse event or the
  source-invalid cemetery outcome.

The kernel is normalized only after killed mass is included.  Clock, mark and
channel correlations must remain joint unless a factorization theorem is
proved.  For reversal, the forward and reversed path measures must be
mutually related by an explicit reference measure and a derived
Radon--Nikodym factor; a free constant `reverse_ratio` is not a physical
substitute. **[open]**

`frame_arity` is not in the input schema.  A finite implementation may cache
the output rank, but must recompute or certify it from the pair jet.  A
uniform margin may be attached when the claim requires worst-case robustness;
a probabilistic implementation must instead publish the complete small-value
tail and rank-stratum masses.

The preparation is a separate measure

\[
\mu_0(dX,dh)=f_0(X,h)\,\lambda_{\rm ref}(dX,dh).
\]

For a finite projection \(\pi_n\), its initial law is
\((\pi_n)_\#\mu_0\).  Uniformly weighting the states that a discretizer happens
to create changes when cells are split and therefore is not a continuum
preparation law. **[theorem, open]**

The earliest isolated missing component is the joint near-encounter law

\[
\mathcal H_X
\bigl(dT,dj,db\mid h\bigr),
\qquad (j,b)\in\mathcal E_X.
\]

It is not identified merely by naming it.  A construction must preregister
the microscopic world-sheet generator, \(\mu_0\) or a fixed conditional
source state, the closest-approach/first-entry rule, and an unconditioned
sampling rule that does not select events using \(\sigma_3\), rank or a target
response.  It must then report whether globally opposite-wound strings enter
rank-three and rank-two strata, with either a uniform margin certificate or a
controlled singular-value tail.  The cited conditional amplitude does not
identify \(\mathcal H_X\).  Even after it is measured, post-miss history,
reservoir reversal and the remaining preparation law are required for the
complete \((\mu_0,\mathscr P_X)\). **[open]**

## 8. Executable theorem/probe artifact

`artifacts/0016/probe_0016.py` performs four source-independent checks:

1. high-precision ball and box suppression tables for
   \(c=0,\ldots,6\);
2. numerical monotonicity checks using unrounded values;
3. exact ordered-frame onset counts for \(q=0,\ldots,9\) and
   \(a=1,\ldots,4\);
4. analytically labeled and numerically evaluated Gram controls for full-rank,
   near-degenerate, domain-metric rescaling, straight opposite-winding,
   tangent-span velocity and rank-one pair jets.

It writes the deterministic
`artifacts/0016/source_to_return_kinematic_probe.json`.  The artifact has no
input or branch for response rank, visible count or target stratum.  It is a
theorem/control probe, not a physical return-law implementation.  The final
local replay passes 8/8 unit tests; the report SHA-256 is
`08cc622e415d0594b85fa04230f0e87d68184402e9ec1500e1923f42f20e274b`.
**[probe]**

## 9. Next falsifiable composition

The next calculation is not another verifier campaign.  On one fixed
rectangular-\(T^9\) source cell:

1. derive or sample the world-sheet near-encounter law
   \(\mathcal H_X(dT,dj,db\mid h)\) for globally opposite-wound F1 pairs,
   using a preregistered near-encounter section and no rank-conditioned
   sampling;
2. either preregister a worst-case \(\eta_{\rm kin}>0\), or preregister
   singular-value tail bounds, and report the probability mass on every rank
   stratum;
3. use the event-specific pair \((N_j,b)\), not a fixed scattering axis, to
   push the continuous impact law through the source-to-return kernel;
4. make the exact age augmentation and attach anonymous
   \(A,R,B,C,M\) ports;
5. reconstruct \(Z_0,\ldots,Z_9\) and compute first entry, entrant strict
   residence, retention and worst leakage for every response rank.

Failure of a uniform \(\eta_{\rm kin}\) falsifies only the uniform-certificate
version; a probabilistic closure survives only if its preregistered tail and
rank-mixture bounds pass.  A rank-two mass must be propagated through the
mixture rather than discarded.  Dependence of the winner on arbitrary impact
or initial preparations, or absence of a positive all-rank
response-residence margin, falsifies the corresponding selection claim.
Only success of this composition could connect carrier geometry to a visible
spatial rank.

\[
(\mu_0,\mathscr P_X)
\longrightarrow
\text{age-augmented scheduled/return process}
\longrightarrow
\text{anonymous }A,R,B,C,M
\longrightarrow
Z_0,\ldots,Z_9
\longrightarrow
\text{entrant strict residence and leakage}
\longrightarrow
\text{visible cone/signature package}.
\]

The present source family starts with a Lorentzian \(9+1\) background.
Accordingly it can at most explain why three spatial directions become
large/visible.  It does not derive the one time direction or Lorentzian
signature. **[open]**

## 10. Required six-part conclusion

1. **Local rank:** \(a=\operatorname{rank}D\Phi_e\le\min(d,2p+1)\);
   F1 rank three requires two non-collinear tangents and transverse relative
   velocity.  A positive registered margin is a sufficient worst-case
   robustness certificate; a controlled tail is the probabilistic
   alternative.  Strict same-cycle straight opposite winding is rank at most
   two. **[theorem, no-go]**
2. **Superselection:** a block-diagonal fixed-arity kernel conserves arity
   pathwise and cannot select three. **[theorem]**
3. **Impact suppression:** on a rank-\(a\) event the normal dimension is
   \(d-a\); the declared ball and box preparations give the proved
   codimension-dependent factors and bounds above. **[source, theorem,
   closure]**
4. **Verdict:** source-family `three-ceiling`, conditional on its
   general-position F1 strata; not strict three-selection and not yet a
   visible-rank ceiling. **[no-go]**
5. **Smallest missing component:** the bundle-valued near-encounter law
   \(\mathcal H_X(dT,dj,db\mid h)\), including its event rule, local tangent
   distribution, rank mixture and robustness/tail certificate; the full
   return kernel and \(\mu_0\) remain open.
   **[open]**
6. **Next falsifiable calculation:** push a source-derived pair-jet/return law
   through event-specific normal spaces and the anonymous all-rank response
   residence test. **[open]**
