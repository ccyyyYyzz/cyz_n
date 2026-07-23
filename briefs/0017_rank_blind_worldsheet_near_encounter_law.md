# Brief 0017 — rank-blind world-sheet near-encounter law

Status: active

Baseline commit: `46eb9b8a5f29cb2eba2d8041ce08f64e0827018f`.

## Role

Act as the originating mathematical physicist and computational co-theorist.
Construct the first continuous, rank-blind near-encounter law upstream of the
fixed scheduled certificate.  Do not review the 0015 verifier, optimize a
journal submission, divide the program into papers, or call a carrier-side
result visible \(3+1\).

Read, in order:

1. `state/PROJECT_STATE.md`;
2. `responses/0016_source_to_return_kinematic_rank_gate.md`;
3. `decisions/0016_adopt_conditional_three_ceiling_not_selection.md`;
4. this brief.

Use only primary sources for physical claims.  Every result must be labeled as
one of:

- `primary-source derived`;
- `exact theorem of the preregistered finite-\(K\) model`;
- `new measurable closure`;
- `controlled numerical result`;
- `no-go/underdetermination`;
- `open physical gate`.

The finite-\(K\) law requested here is a conditional laboratory.  It is not
already a first-principles early-universe preparation.

## Governing correction

Decision 0016 removed fixed frame arity from the physical claim chain.  The
remaining upstream object is

\[
\mathcal H_X(dT,dj,db\mid h),
\qquad b\in N_j,
\]

for two globally opposite-wound F1 strings on one fixed rectangular \(T^9\)
source cell.  The event law must generate its local pair jet, encounter rank,
normal space, impact coordinate and holding time.  None may be supplied by a
response rank, a requested winner, or a predeclared \(d-3\) impact space.

The main event in this round is a hysteretic first-entry stopping time.  An
interior closest approach is a secondary mark inside the resulting encounter
episode.  The two sections are not interchangeable.  At first entry the
separation generally has a longitudinal component in the encounter kinematic
span.  Therefore

\[
b=P_{N_j}s,\qquad
\ell=s-b
\]

must be recorded.  The identity \(b=s\) is valid only at an interior closest
approach satisfying full stationarity in both world-sheet labels and time.

## Goal

The goal is to define, implement and audit one normalized joint law for a pair
of finite-mode, globally opposite-wound, graph-like F1 strings.  The law must
be generated before rank is evaluated.  It must preserve the correlations
among first-entry time, pair jet, normal impact coordinate, longitudinal
phase, episode geometry and every exceptional outcome.

The smallest admissible main model is the quadratic static-gauge sector of
the Nambu--Goto action with a fixed Fourier cutoff \(K\).  Its principal
preparation is a rank-blind microcanonical Liouville measure.  A canonical
Gaussian ensemble may be used only as an analytic control.  The GKM and JJP
reaction probabilities enter only after the geometric law has produced
\((T,j,b,\ell)\).

The decisive outputs of this round are:

1. the normalized first-entry/episode law, including all exceptional mass;
2. the event-conditioned mass of every encounter-rank stratum;
3. the event-conditioned distribution of the metric-normalized
   \(\sigma_3\), including any atom at zero;
4. the joint distribution of \(T,j,b,\ell\), not separate marginals;
5. a regulator and preparation sensitivity ledger;
6. a precise statement of whether the finite-\(K\) source law is usable,
   excluded, or still inconclusive.

## Non-goals

This round must not claim that a finite-mode classical ensemble is the unique
quantum F1 preparation.  It must not assume thermalization in a regime where
the cited source calculations find interactions too weak to establish it.
It must not identify almost-sure rank three with a uniform positive
singular-value margin.

This round must not infer the encounter-conditioned \(\sigma_3\) tail from a
fixed world-sheet point.  First-entry and closest-approach sampling introduce
Kac--Rice/Palm weights and global survival conditions.  These can change the
tail exponent.

This round must not use a fixed normal dimension.  The normal object changes
dimension with rank and must be represented as a stratified Borel normal
field.  Lower-rank, tied, grazing, degenerate, no-event, source-invalid and
censored outcomes may not be discarded or resampled.

This round does not yet supply annihilation, reconnection, post-miss
world-sheet evolution, a reverse reservoir channel, an anonymous response
interface, a visible spatial rank, a cone, a signature, or a derived time
direction.

## 1. Preregistered source cell

### 1.1 Frozen rectangular torus and winding sector

Fix a rectangular spatial torus

\[
M=T^9_R,\qquad
G=\operatorname{diag}(R_1^2,\ldots,R_9^2)
\]

in dimensionless angular coordinates, or the equivalent Euclidean metric in
physical-length coordinates.  The convention must be chosen once and used in
the event solver, the target-space singular values and the normal projector.

Select one winding cycle \(w\).  The source registry must treat its label as
part of the state.  A permutation of the torus axes must carry the winding
label, metric and all world-sheet data together.  On the fixed-\(w\) cell the
stabilizer action on the eight transverse directions must remain explicit.

Let

\[
L_w=2\pi R_w,\qquad
\epsilon_1=+1,\qquad
\epsilon_2=-1 .
\]

Use physical arc-length \(\sigma_i\in[0,L_w)\) and static gauge

\[
X_i^0=t,\qquad
X_i^w(t,\sigma_i)=\epsilon_i\sigma_i\pmod {L_w},
\]

\[
X_i^\perp(t,\sigma_i)
=Q_i+Y_i(t,\sigma_i)\pmod {T^8_\perp}.
\]

This is a graph-like single-winding sector.  Folds, overhangs, cusp-scale
structure and changes of winding number lie outside this first model.  They
must be listed as later robustness gates rather than silently represented by
the Fourier cutoff.

### 1.2 Finite-mode generator

Use the quadratic transverse Nambu--Goto action

\[
S_{2,K}
=\frac{T_F}{2}\sum_{i=1}^2
\int dt\int_0^{L_w}d\sigma_i
\left(
|\dot Y_i|^2-|Y_i'|^2
\right),
\]

with real left- and right-moving Fourier modes truncated to
\(1\le n\le K\).  A convenient representation is

\[
Y_i(\sigma,t)
=V_i t+
\sum_{n=1}^{K}
\left[
c^L_{in}e^{ik_n(\sigma-t)}
+c^R_{in}e^{ik_n(\sigma+t)}
+\text{complex conjugate}
\right],
\qquad
k_n=\frac{2\pi n}{L_w}.
\]

The implementation may use an equivalent real sine-cosine basis.  It must
publish the exact conversion, coefficient measure and normalization.  The
linear finite-mode flow is to be evaluated analytically.  A time-stepping
integrator may be used only as an independently checked control.

The transverse Hamiltonian is

\[
H_{\perp,K}
=\frac{T_F}{2}\sum_{i=1}^2
\int_0^{L_w}d\sigma_i
\left(
|\dot Y_i|^2+|Y_i'|^2
\right).
\]

The constant winding rest energy is recorded separately.  The registry must
also fix total target momentum and the closed-string global world-sheet
momentum or left-right level-matching condition.  A Gaussian ensemble that
ignores those constraints is only an unconstrained diagnostic.

### 1.3 Source-validity cell

Preregister the target string length \(\ell_s=\sqrt{\alpha'}\), the mode
cutoff \(k_{\max}=2\pi K/L_w\), and a small-graph validity threshold.  At
minimum the source ledger must report

\[
\epsilon_{\rm graph}
=\max_i
\left\{
\|Y_i'\|_\infty,\|\dot Y_i\|_\infty
\right\},
\qquad
k_{\max}\ell_s .
\]

The response must state which inequalities define the quadratic source-valid
cell before sampling.  A sampled trajectory outside that cell is a
`source_invalid` outcome.  It may not be redrawn until it passes.

The cutoff \(K\) is physical registration data for this round, not an
innocent numerical resolution.  Classical Fourier ensembles can become
rough or ultraviolet-sensitive as \(K\) increases.  A finite-\(K\) result
must not be called a continuum result without a convergence theorem.

### 1.4 Principal microcanonical measure

Let \(\Gamma_{K,h}\) be the finite-dimensional phase space satisfying the
fixed winding, target momentum and level-matching constraints.  Register

\[
h=
\left(
R_A,T_F,\ell_s,K,E_\perp,P_{\rm tot},
\mathcal P_{\sigma,1},\mathcal P_{\sigma,2},
r_{\rm in},r_{\rm out},\mathcal T,
\text{episode history}
\right).
\]

The principal preparation is the branch-volume Liouville measure

\[
d\mu_{E,K,h}
=Z_h^{-1}
\frac{d^8Q_{\rm rel}}{\operatorname{Vol}(T^8_\perp)}
\delta(H_{\perp,K}-E_\perp)
\delta^8(P_1+P_2-P_{\rm tot})
\prod_{i=1}^2
\delta(\mathcal P_{\sigma,i}-\pi_i)
d\Gamma_K .
\]

An equivalent product of fixed left- and right-moving energy shells is
admissible if it enforces the same registered constraints.  The choice
between one total shell and separate string or chirality shells changes the
physical preparation.  It must therefore be a named source-family control,
not an implementation detail.

The relative transverse center \(Q_{\rm rel}=Q_1-Q_2\) is uniform on the
transverse torus unless the source history supplies a different measured
law.  The two strings may not be independently redrawn after a miss.  Their
same Fourier state evolves until the episode exits, the hysteresis re-arms,
or a separately defined physical reaction changes the state.

No density in \(\mu_{E,K,h}\) may depend on:

\[
a,\quad \sigma_3,\quad \dim N_j,\quad
m,\quad Z_m,\quad
\text{a requested response winner}.
\]

### 1.5 Canonical Gaussian control

For analytic checks only, define

\[
d\mu_{\beta,K,h}
\propto
\frac{d^8Q_{\rm rel}}{\operatorname{Vol}(T^8_\perp)}
e^{-\beta H_{\perp,K}}
\delta^8(P_1+P_2-P_{\rm tot})
d\Gamma_K ,
\]

with a separately registered treatment of level matching.  This control is
useful because local slopes and velocities can become Gaussian.  It does not
replace the microcanonical law, and agreement between the two ensembles is
an output to be tested.

### 1.6 Initial episode history

The source history contains an episode-state variable with at least

\[
\{\texttt{armed},\texttt{active},
\texttt{left\_censored},\texttt{exited}\}.
\]

The main law begins in the `armed` state after a verified previous exit
beyond \(r_{\rm out}\).  If an unconditional source preparation places mass
inside the hysteresis band or the inner tube at the initial time, that mass
is reported as `left_censored` or `active`.  It may not be rejected until an
armed sample is obtained unless the conditional armed law is explicitly
declared as a different preparation.

## 2. Hysteretic first-entry event map

### 2.1 Local separation and spatial minimum

Choose thresholds

\[
0<r_{\rm in}<r_{\rm out}
<\operatorname{inj}(T^9_R).
\]

The strict injectivity-radius bound applies to \(r_{\rm out}\), not only to
\(r_{\rm in}\).  It ensures that every separation used inside an episode has
a unique local logarithm.

For

\[
z=(\sigma_1,\sigma_2,t)
\]

define

\[
s_X(z)
=\operatorname{Log}_{X_2(t,\sigma_2)}
X_1(t,\sigma_1),
\qquad
F_X(z)=\frac12\|s_X(z)\|_G^2 .
\]

At fixed time let

\[
\rho_X(t)
=\min_{\sigma_1,\sigma_2}
\|s_X(\sigma_1,\sigma_2,t)\|_G
\]

and retain the entire minimizer set

\[
\mathcal M_X(t)
=\operatorname*{arg\,min}_{\sigma_1,\sigma_2}
F_X(\sigma_1,\sigma_2,t).
\]

The implementation must search all torus image branches compatible with the
outer tube before applying the unique logarithm.  A coordinate minimum-image
shortcut is admissible only after its equivalence has been proved for the
registered rectangular metric and thresholds.

### 2.2 First-entry stopping time

For an armed history, define

\[
T_{\rm in}
=\inf\left\{
t>0:\rho_X(t)\le r_{\rm in}
\right\}.
\]

The sample remains unarmed after entry.  The associated exit time is

\[
T_{\rm out}
=\inf\left\{
t>T_{\rm in}:\rho_X(t)\ge r_{\rm out}
\right\}.
\]

The interval

\[
[T_{\rm in},T_{\rm out})
\]

is one encounter episode.  A later entry is eligible only after the outer
exit re-arms the process.  This hysteresis is part of the stopping-time law.
It is not a post-processing filter.

For a unique regular spatial minimizer
\((\sigma_{1*},\sigma_{2*})\) at first entry, the local equations are

\[
\partial_{\sigma_1}F_X=0,\qquad
\partial_{\sigma_2}F_X=0,\qquad
F_X=\frac12r_{\rm in}^2,
\]

\[
\nabla_{\sigma\sigma}^2F_X\succ0,\qquad
\partial_tF_X<0 .
\]

The last condition identifies a regular inward crossing.  A first hit with
\(\partial_tF_X=0\) is grazing and belongs to a separate outcome class.

### 2.3 Episode-level closest approach

Within a completed episode define

\[
T_{\rm c}
\in
\operatorname*{arg\,min}_{t\in[T_{\rm in},T_{\rm out}]}
\rho_X(t).
\]

The closest-approach mark includes every minimizing time and every spatial
minimizer at that time.  A unique interior Morse closest approach satisfies

\[
\partial_{\sigma_1}F_X
=\partial_{\sigma_2}F_X
=\partial_tF_X=0,
\qquad
\nabla^2_{\sigma_1,\sigma_2,t}F_X\succ0.
\]

Closest approach is a secondary mark.  It must not replace
\(T_{\rm in}\) as the holding time.  If the observation horizon ends before
outer exit, the episode and its closest mark are right-censored.

### 2.4 Ties, clusters and exceptional sections

Zero-probability ties may be resolved by a deterministic rule only after a
proof or an independently validated bound establishes zero mass.  A
lexicographic world-sheet label is not generally invariant under residual
world-sheet translations, string exchange or torus relabeling.

If ties have positive or unresolved mass, the response must preregister one
of the following symmetry-respecting outputs:

1. the complete minimizer cluster with a cluster-valued mark;
2. an equivariant tie kernel driven by an independent seed included in the
   source state;
3. an explicit `ambiguous_tie` outcome.

The same rule applies to multiple simultaneous first-entry components.
Grazing crossings, degenerate spatial Hessians, cut-locus ambiguities,
episode mergers and numerically unresolved roots retain separate mass.  They
may not be perturbed, jittered or resampled into the regular class.

The final outcome registry must distinguish at least:

- `regular_first_entry`;
- `tie_cluster`;
- `ambiguous_tie`;
- `grazing_entry`;
- `degenerate_spatial_minimum`;
- `left_censored_active_episode`;
- `right_censored_no_entry`;
- `right_censored_active_episode`;
- `no_entry_proved`;
- `source_invalid`;
- `torus_branch_ambiguous`;
- `numerically_unresolved`.

`No_entry_proved` is reserved for a complete certified search over a declared
finite recurrence period or other complete horizon.  Failure to observe an
entry during a finite window is right censoring, not proof of no event.

## 3. Pair jet, stratified normal field and impact decomposition

### 3.1 Metric-normalized pair jet

At every selected first-entry representative, parallel transport the columns
to one target tangent space and define

\[
J_j=D_{\sigma_1,\sigma_2,t}s_X
=\left[
\tau_1,-\tau_2,u
\right].
\]

On the flat rectangular torus,

\[
\tau_i=\partial_{\sigma_i}X_i,\qquad
u=\dot X_1-\dot X_2 .
\]

Register a target metric \(G_j\) and a domain metric \(H_j\).  The latter
fixes the relative units of the two physical arc-length parameters and time.
Define

\[
\widehat J_j
=G_j^{1/2}J_jH_j^{-1/2},
\qquad
a(j)=\operatorname{rank}J_j .
\]

For F1,

\[
0\le a(j)\le3.
\]

The response must publish all three singular values of \(\widehat J_j\),
including exact or numerical zeros, rather than reporting only a thresholded
rank.

### 3.2 Stratified Borel normal field

Let

\[
\mathcal J_a
=\{j:a(j)=a\},
\qquad
\mathcal J
=\bigsqcup_{a=0}^{3}\mathcal J_a .
\]

On a fixed-rank stratum define

\[
N_j
=\left(\operatorname{im}J_j\right)^{\perp_{G_j}},
\qquad
\dim N_j=9-a(j),
\]

and

\[
P_{N_j}
=I-J_j(J_j^\top G_jJ_j)^+J_j^\top G_j .
\]

Across rank changes the pseudoinverse and projector need not be continuous.
They are Borel measurable.  The correct global object is therefore

\[
\mathcal N
=\left\{
(j,b):j\in\mathcal J,\ b\in N_j
\right\},
\]

a stratified Borel normal field.  It is a vector bundle only after
restriction to one fixed-rank stratum.  Serialization must carry the rank,
the projector or an equivalent orthonormal normal frame, and the target
metric with every \(b\).

No fixed \(\mathbb R^6\) impact space is allowed.  On a rank-two event the
normal dimension is seven.  On a rank-three event it is six.  The event law
must retain both without changing its source sampling rule.

### 3.3 First-entry impact and longitudinal phase

Let

\[
s_e=s_X(\sigma_{1*},\sigma_{2*},T_{\rm in}).
\]

At a regular spatial minimizer,

\[
s_e\perp_G\tau_1,\qquad
s_e\perp_G\tau_2,
\]

but generally

\[
s_e\not\perp_G u .
\]

The first-entry mark is therefore

\[
\boxed{
b_e=P_{N_j}s_e,\qquad
\ell_e=(I-P_{N_j})s_e,\qquad
s_e=b_e+\ell_e .
}
\]

The orthogonality and reconstruction checks

\[
J_j^\top G_jb_e=0,\qquad
\|s_e-b_e-\ell_e\|_{G_j}=0
\]

are mandatory numerical invariants.

At a unique interior closest approach, full stationarity gives

\[
J_{j_c}^{\top}G_{j_c}s_c=0.
\]

Only on that secondary section may the response write

\[
b_c=s_c,\qquad \ell_c=0.
\]

A first-entry implementation that always sets \(b=s\) fails this brief.

## 4. Normalized marked law

Let \(\Psi_h(\omega)\) map a finite-mode source state to one of the regular or
exceptional outcomes above.  A regular completed episode contains at least

\[
\left(
T_{\rm in},j_{\rm in},b_{\rm in},\ell_{\rm in},
T_{\rm c},j_{\rm c},b_{\rm c},
T_{\rm out},
\text{minimizer metadata}
\right).
\]

Define the full marked law

\[
\widetilde{\mathcal H}^{(K)}_X
=\left(\Psi_h\right)_\#\mu_{E,K,h}.
\]

The requested kernel

\[
\mathcal H_X^{(K)}(dT,dj,db\mid h)
\]

is a marginal of this full law.  Marginalization may not erase
\(\ell\), tie/cluster metadata, episode status or exceptional outcome mass
from the stored source artifact.

The total-mass identity is

\[
\widetilde{\mathcal H}^{(K)}_X
\left(
\mathcal E_{\rm regular}
\sqcup
\mathcal E_{\rm exceptional}
\right)=1.
\]

If a conditional law given `regular_first_entry` is reported, its
normalizing mass must be printed alongside it.  The response may not
renormalize regular events to one and leave the missing mass implicit.

The joint law must retain clock--jet--impact correlations.  A factorization

\[
\mathcal H(dT,dj,db\mid h)
=H_T(dT\mid h)H_j(dj\mid h)H_b(db\mid h)
\]

is forbidden unless independently proved for the registered source cell.

## 5. Opposite-winding rank identity

In the quadratic graph sector, write the transverse slopes and relative
velocity at a selected representative as

\[
p_i=Y_i',\qquad
u=\dot Y_1-\dot Y_2 .
\]

With \(e_w\) the unit winding direction,

\[
\tau_1=e_w+p_1,\qquad
-\tau_2=e_w-p_2 .
\]

Set

\[
q=p_1+p_2 .
\]

The determinant-one column operation

\[
\left[
e_w+p_1,e_w-p_2,u
\right]
\longmapsto
\left[
e_w+p_1,-q,u
\right]
\]

gives the exact finite-model identity

\[
\boxed{
a=3
\quad\Longleftrightarrow\quad
q\wedge u\ne0
}
\]

because \(q\) and \(u\) are transverse to \(e_w\).  In an orthonormal target
frame,

\[
\det(J^\top J)
=
|q\wedge u|^2
+|p_1\wedge q\wedge u|^2 .
\]

The response must reproduce this identity symbolically and numerically.
For anisotropic \(G\), it must first whiten the target metric or use the
corresponding Gram exterior norm.

Mandatory exact controls are:

\[
p_1=p_2=0
\quad\Longrightarrow\quad
a\le2,
\]

\[
q=0
\quad\Longrightarrow\quad
a\le2,
\]

\[
u\parallel q
\quad\Longrightarrow\quad
a\le2.
\]

A continuous excited ensemble may give \(a=3\) almost surely while
approaching these controls arbitrarily closely.  Exact rank alone is
therefore not a robustness certificate.

## 6. Singular-value program

### 6.1 Uniform margin is not the default target

The microcanonical and Gaussian controls generally have support arbitrarily
near \(q\wedge u=0\).  Unless the registered constrained support excludes a
neighborhood of the lower-rank set by an independent physical law, the
expected result is

\[
\operatorname*{ess\,inf}\sigma_3(\widehat J)=0.
\]

This does not by itself create a positive rank-two atom.  It means that the
probabilistic small-\(\sigma_3\) tail, rather than a uniform
\(\eta_{\rm kin}>0\), is the relevant object.

The response must report separately

\[
p_{\le2}
=\Pr[\sigma_3=0],
\]

and

\[
F_{\rm enc}(\varepsilon)
=\Pr[
0<\sigma_3\le\varepsilon
\mid\text{declared encounter outcome}
].
\]

The metric and source scales used to make \(\varepsilon\) dimensionless must
be registered.

### 6.2 Fixed-point Gaussian tail is an audit proposition

At one world-sheet point selected independently of the random fields, an
unconstrained isotropic Gaussian surrogate suggests that the normalized
matrix

\[
B=[q,u]\in\mathbb R^{8\times2}
\]

has a real Gaussian law.  The rank-one determinantal set has codimension
seven.  This motivates the candidate asymptotic

\[
\Pr[
s_{\min}(B)<\varepsilon
]
\stackrel{?}{=}
C\varepsilon^7+o(\varepsilon^7).
\]

This is a proposition to audit, not an adopted result.  The audit must check:

1. the exact covariance and independence of \(q\) and \(u\);
2. the effect of target momentum and level-matching constraints;
3. the relation between \(s_{\min}(B)\) and
   \(\sigma_3(\widehat J)\);
4. the normalization supplied by \(G\) and \(H\);
5. the replacement of the Gaussian law by the microcanonical shell;
6. the behavior near the compact support boundary;
7. the effect of first-entry or closest-approach conditioning.

No conclusion of Brief 0017 may cite the exponent seven unless the relevant
version has passed these audits.

### 6.3 First-entry Kac--Rice/Palm weight

Let \(\xi=(\sigma_1,\sigma_2)\).  For a unique spatial Morse minimizer, the
regular first-entry zeros are those of

\[
g(\xi,t)
=
\left(
\partial_{\sigma_1}F_X,
\partial_{\sigma_2}F_X,
F_X-\frac12r_{\rm in}^2
\right).
\]

At \(\nabla_\xi F_X=0\), its local Kac--Rice Jacobian factor is

\[
W_{\rm in}
=
\left|
\det\nabla_{\xi\xi}^2F_X
\right|
\left(-\partial_tF_X\right)_+ .
\]

The first-entry law also contains the armed-history condition and the global
factor that no earlier eligible entry occurred.  Therefore the event
distribution of \(q,u\) is not the fixed-point distribution.

For a unique interior closest approach, the local weight is

\[
W_{\rm c}
=
\left|
\det\nabla_{\xi,t}^2F_X
\right|
\mathbf1_{\nabla_{\xi,t}^2F_X\succ0},
\]

together with membership in the selected episode and its own exclusion
conditions.

If, near \(s_{\min}=0\),

\[
0<c_-
\le
\mathbb E[W\mid q,u]
\le c_+<\infty,
\]

then a fixed-point tail exponent can survive the Palm tilt.  If instead

\[
\mathbb E[W\mid q,u]
\asymp s_{\min}^{\alpha},
\]

the exponent can shift by \(\alpha\).  If the regular weight vanishes on a
degenerate or grazing branch, that branch is not to be redrawn.  Its mass
must remain in the appropriate exceptional outcome.

The event-conditioned tail is thus an open calculation even if the
fixed-point Gaussian proposition is proved.

## 7. Why the other source routes are downstream or incomplete

The fixed-level or microcanonical quantum closed-string density matrix gives
state counts, momentum/winding distributions and correlation functions.  It
does not by itself give a simultaneous classical sample of position,
tangent and velocity.  A local spacetime POVM, coherent-state resolution,
smearing scale and two-string localization rule would be required before
\(T,j,b\) become classical random variables.  Choosing those objects is a
new physical closure.

The EGJK and GKM Boltzmann variables evolve homogeneous geometry and string
occupations.  GKM also supplies a conditional impact-parameter reaction
profile and a numerical recollision/redraw rule.  These ingredients do not
generate a local tangent ensemble.  Using their \(d-3\) impact space before
computing \(a(j)\) would reintroduce the rank-three assumption that Brief
0016 removed.

The Sakellariadou discrete Nambu--Goto model provides a useful independent
control because its diamond-lattice update exactly evolves the flat-space
wave equation and records string intersections.  Its same-site event has
\(b=0\), and its tangent law has lattice atoms.  It cannot be used as the
main continuous \(\sigma_3\)-tail model.

## 8. Numerical implementation stages

### Stage A — frozen registry and dependency audit

Before drawing a sample, publish the complete source registry.  It must
contain the torus radii, winding label, \(T_F,\ell_s,K,E_\perp\), momentum and
level-matching constraints, principal and control measures, random-number
algorithm and seeds, \(r_{\rm in},r_{\rm out}\), observation horizon,
source-validity bounds, \(G,H\), event tolerances and confidence procedure.

Publish a dependency graph demonstrating that the sampler, event section,
tie handler and validity predicate do not read rank, \(\sigma_3\), normal
dimension, visible rank, response cells or a desired winner.

### Stage B — measure sampler and exact flow

Implement the microcanonical constrained sampler and verify its energy,
momentum, level-matching and relative-center marginals.  Compare two
independent sampling algorithms if possible.  Evolve the finite Fourier
modes analytically and check conservation along every sampled path.

The Gaussian control must use a distinct registry and output namespace.  It
may not silently supply samples to the principal microcanonical result.

### Stage C — certified hysteretic event finder

Compute \(\rho_X(t)\) and the complete spatial minimizer set.  Locate every
candidate entry root of

\[
\partial_{\sigma_1}F
=\partial_{\sigma_2}F
=0,\qquad
F=r_{\rm in}^2/2
\]

in the observation window.  Use interval isolation, an exhaustive
trigonometric-polynomial method, or two demonstrably independent solvers.
A dense grid followed by local optimization is not by itself proof that the
first root was found.

Run the hysteresis state machine, identify inward, grazing and degenerate
crossings, and preserve ties as registered clusters or ambiguous outcomes.
After entry, continue the same world-sheet state until outer exit or
censoring.  Then locate and classify the episode-level closest approach.

### Stage D — pair-jet and normal-field construction

At every regular and exceptional representative, compute \(J,G,H\), all
singular values, rank-stratum metadata and the Borel projector.  Store

\[
s,\quad b,\quad\ell,\quad N_j,\quad P_{N_j}.
\]

Verify

\[
s=b+\ell,\qquad
J^\top Gb=0.
\]

At first entry, actively test that examples with \(\ell\ne0\) are retained.
At an interior closest approach verify \(b=s\) only within numerical
certification error.

### Stage E — rank mixture and tail estimation

Report the unconditional source-state distribution, the regular first-entry
distribution, the full first-entry law including exceptional outcomes, and
the closest-approach secondary law.  For each, publish:

\[
\Pr[a=0],\ldots,\Pr[a=3],
\qquad
\Pr[\sigma_3=0],
\qquad
F(\varepsilon)
\]

on a preregistered dimensionless \(\varepsilon\) grid.

Rare-tail estimation may use importance sampling or subset simulation only
if the likelihood ratio is explicit and validated on ordinary-event
controls.  Rank-conditioned samples may estimate a diagnostic integral, but
they may not replace the main rank-blind event law.

Compute or estimate the Kac--Rice first-entry weight and compare its induced
jet distribution with direct stopping-time samples.  Test whether the
conditional weight remains bounded near small \(\sigma_3\) or changes the
tail exponent.

### Stage F — convergence and adversarial controls

Vary \(K,E_\perp,r_{\rm in},r_{\rm out},\mathcal T\), event-search
resolution and numerical precision.  Compare the microcanonical law with
the Gaussian control without merging them.  Report which observables are
stable and which retain regulator dependence.

Apply torus translations, residual world-sheet translations, string
exchange, winding-orientation reversal and transverse-axis permutations.
The pushed event law, tie clusters and normal-field data must transform
covariantly.

### Stage G — machine-readable result contract

The eventual result artifact must contain:

1. the full source registry and provenance;
2. sampler and conservation diagnostics;
3. total counts and probability mass for every outcome tag;
4. regular first-entry, exceptional and closest-approach summaries;
5. joint summaries of \(T,\sigma_3,\|b\|,\|\ell\|,a\);
6. the fixed-point and Palm-tail audit results;
7. convergence and symmetry tables;
8. every failed or inconclusive gate;
9. a deterministic conclusion in
   \(\{\texttt{certified\_within\_declared\_model},
   \texttt{declared\_model\_excluded},
   \texttt{inconclusive}\}\).

The artifact must never serialize only regular events.

## 9. Acceptance conditions

The finite-\(K\) near-encounter law is accepted within its declared model
only if all of the following hold.

First, the source measure is normalized on its constrained phase space and
is independent of all downstream rank and response quantities.  Every
source-invalid sample remains accounted for.

Second, the hysteretic first-entry solver has demonstrated root coverage at
the registered resolution or returns `numerically_unresolved`.  All
exceptional and censored masses are explicit, and all outcome masses sum to
one within a preregistered numerical interval.

Third, the implementation distinguishes first entry from closest approach.
It uses

\[
b=P_Ns,\quad\ell=s-b
\]

at entry and permits \(b=s\) only after full closest-approach stationarity is
verified.

Fourth, the normal object is rank variable.  Rank-two samples produce
seven-dimensional normal fibers and rank-three samples produce
six-dimensional fibers without changing the sampler or event rule.

Fifth, the opposite-winding rank identity and every mandatory exact control
pass.  The stored singular values reproduce the Gram determinant within
certified error.

Sixth, no fixed-point Gaussian tail is reported as an encounter theorem
without the Palm-weight and no-earlier-entry audit.  Exact lower-rank atoms
and small positive singular values are reported separately.

Seventh, the conclusion remains covariant under the registered source
symmetries.  Positive-mass ties are handled by an equivariant kernel,
cluster-valued output or explicit ambiguity.

Eighth, the response states the finite-\(K\), quadratic and graph-sector
limitations next to every physical interpretation.

## 10. Mandatory falsifiers and hostile controls

The response must include a strictly straight opposite-winding pair.  It has
\(p_1=p_2=0\) and rank at most two.  A constructor that reports rank three
for this control is rejected.

It must include an excited collinear-wiggle pair with \(p_1+p_2=0\), and a
pair with \(u\parallel p_1+p_2\).  Both have rank at most two despite
nonzero oscillator energy.

It must include a near-degenerate sequence with

\[
\sigma_3\downarrow0
\]

while exact rank remains three.  A hard numerical rank threshold may label
the sequence for diagnostics, but it may not erase its singular-value data.

It must include a regular first-entry example with

\[
s^\top Gu\ne0.
\]

For this control \(\ell\ne0\) generically.  An implementation that stores
\(b=s\) fails.

It must include a unique interior closest approach.  That control must
satisfy \(b=s\) and \(\ell=0\) after full stationarity is certified.

It must include tied, grazing and degenerate synthetic controls.  Deleting,
jittering or resampling those records must change the report and fail the
mass ledger.

It must include a mutation that replaces the stratified projector by a
fixed six-dimensional projector.  The mutation must fail on a rank-two
control.

It must include a mutation that accepts events only when
\(\sigma_3>\varepsilon\).  The dependency audit must reject it before any
result is emitted.

It must include a mutation with

\[
r_{\rm out}\ge\operatorname{inj}(T^9).
\]

The source registry must reject the ambiguous logarithm domain.

It must include a finite-window path with no observed entry and a distinct
complete-period path with certified no entry.  The first is censored; only
the second may be labeled `no_entry_proved`.

It must include a source-invalid high-slope or ultraviolet control.  That
sample enters `source_invalid` and is not replaced.

## 11. Success and failure branches

### Branch A — usable probabilistic rank-three preparation

If the normalized law is stable on a declared finite-\(K\) cell, has no
unresolved lower-rank atom beyond a certified bound, and has a controlled
event-conditioned small-\(\sigma_3\) tail, adopt it only as a conditional
probabilistic rank-three preparation.  Do not promote it to a uniform
margin, a visible-rank result or a continuum theorem.

### Branch B — nonzero lower-rank mixture

If rank-zero, rank-one or rank-two events have positive mass, retain the
mixture:

\[
\mathcal H
=\sum_{a=0}^{3}p_a\mathcal H_a .
\]

Every component must pass through its own normal fiber and downstream
reaction law.  A positive rank-two mass does not invalidate the event law,
but it invalidates a pure rank-three preparation claim.

### Branch C — heavy or uncontrolled near-degenerate tail

If the event-conditioned \(\sigma_3\) tail is too heavy for a preregistered
probabilistic robustness bound, reject that robustness claim.  Almost-sure
rank three does not rescue it.

### Branch D — regulator or preparation dependence

If the result changes materially with \(K\), shell factorization, Gaussian
versus microcanonical preparation, or source-validity cutoff, classify the
physical inference as inconclusive.  Preserve any exact finite-\(K\)
theorems, but proceed to a quantum coherent-state or exact constrained
Nambu--Goto preparation before composing a reaction kernel.

### Branch E — unresolved event geometry

If ties, grazing events, degenerate minimizers or torus-branch ambiguities
have positive unresolved mass, retain a cluster-valued or ambiguous event
law.  Do not force a scalar event representative.

### Branch F — no-entry or censoring dominance

If most mass is right-censored, the holding-time law is not identified on
the chosen horizon.  If a complete recurrence search proves no entry on
positive mass, preserve that mass as physical freeze-out for this source
cell.

### Branch G — quadratic source excluded

If the source-validity cemetery is large or the conclusions disappear under
the first exact-Nambu--Goto robustness control, exclude the quadratic
graph-sector model.  Do not tune the validity predicate until rank three
returns.

## 12. Primary-source boundary

Use the following primary sources and state exactly which ingredient each
does and does not provide.

1. M. Sakellariadou, *Numerical Experiments in String Cosmology*,
   Nucl. Phys. B 468, 319--335 (1996),
   arXiv:hep-th/9511075,
   DOI:10.1016/0550-3213(96)00123-X.  This source supplies the
   flat-space Nambu--Goto wave solution and an exact discrete torus
   evolution/intersection model.  Its lattice event is not the continuous
   impact law requested here.
2. D. Mitchell and N. Turok, *Statistical Properties of Cosmic Strings*,
   Nucl. Phys. B 294, 1138--1163 (1987),
   DOI:10.1016/0550-3213(87)90626-2.  This source supplies a primary
   statistical-string ensemble precedent, not a unique local
   first-entry law for opposite-wound quantum F1 pairs.
3. N. Deo, S. Jain and C.-I. Tan,
   *String Statistical Mechanics Above Hagedorn Energy Density*,
   Phys. Rev. D 40, 2626 (1989),
   DOI:10.1103/PhysRevD.40.2626.  This source supplies microcanonical
   closed-string state counting, not a classical world-sheet POVM.
4. J. L. Mañes, *String Form Factors*, JHEP 01 (2004) 033,
   arXiv:hep-th/0312035,
   DOI:10.1088/1126-6708/2004/01/033.  This source derives form factors
   of randomly excited closed strings.  It does not choose a classical
   event trajectory.
5. J. L. Mañes, *Portrait of the String as a Random Walk*,
   JHEP 03 (2005) 070, arXiv:hep-th/0412104,
   DOI:10.1088/1126-6708/2005/03/070.  This source derives
   density correlations and a Brownian description for highly excited
   strings.  It also exposes the nontriviality of replacing the ensemble
   by one classical background.
6. M. Hindmarsh and D. Skliros,
   *Covariant Closed String Coherent States*,
   Phys. Rev. Lett. 106, 081602 (2011),
   arXiv:1006.2559,
   DOI:10.1103/PhysRevLett.106.081602.  This source gives the
   coherent-state bridge to classical closed-string loops.  It does not
   select the cosmological probability measure over those loops.
7. R. Easther, B. R. Greene, M. G. Jackson and D. Kabat,
   *String Windings in the Early Universe*, JCAP 02 (2005) 009,
   arXiv:hep-th/0409121,
   DOI:10.1088/1475-7516/2005/02/009.  This source supplies the
   anisotropic \(T^9\) string-gas setting and one macroscopic initial
   ensemble, not a local tangent/impact law.
8. R. Danos, A. R. Frey and A. Mazumdar,
   *Interaction Rates in String Gas Cosmology*,
   Phys. Rev. D 70, 106010 (2004),
   arXiv:hep-th/0409162,
   DOI:10.1103/PhysRevD.70.106010.  This source constrains the
   interaction and equilibrium regime.  It does not supply a universal
   return process.
9. B. Greene, D. Kabat and S. Marnerides,
   *Dynamical Decompactification and Three Large Dimensions*,
   Phys. Rev. D 82, 043528 (2010),
   arXiv:0908.0955,
   DOI:10.1103/PhysRevD.82.043528.  This source supplies a
   conditional impact profile and its declared recollision/redraw
   algorithm.  It does not derive the local pair-jet preparation.
10. M. G. Jackson, N. T. Jones and J. Polchinski,
    *Collisions of Cosmic F- and D-strings*, JHEP 10 (2005) 013,
    arXiv:hep-th/0405229,
    DOI:10.1088/1126-6708/2005/10/013.  This source supplies
    crossing-conditioned angle/velocity-dependent reaction probabilities.
    It does not supply the prior law of angle, velocity, impact or first
    encounter.

Do not use a review to strengthen a claim beyond these primary sources.

## 13. Downstream interface

If the geometric law passes, compose it with a separately registered
reaction/history kernel:

\[
\mathscr C_X
\left(
d\chi,dh',dX',d\Delta E_R,d\dagger
\mid
j,b,\ell,X
\right).
\]

The composite source-to-return law is then

\[
\mathscr P_X
\left(
dT,dj,db,d\ell,d\chi,dh',
dX',d\Delta E_R,d\dagger
\mid h
\right).
\]

JJP or GKM channel data may populate \(\mathscr C_X\) only on their
source-valid strata.  The channel kernel must read the event-specific
normal field.  It may not replace it with the rank-three normal space on
lower-rank events.

After the continuous source law is closed, make the exact age/episode
augmentation.  Then attach anonymous \(A,R,B,C,M\) ports, reconstruct
\(Z_0,\ldots,Z_9\), and compute first entry, entrant strict residence,
retention and worst leakage for every response rank.  The finite scheduled
certificate remains a software control until it is shown to be the
projection of this continuous law.

The required logical order is

\[
\mu_{E,K,h}
\longrightarrow
\widetilde{\mathcal H}^{(K)}_X
\longrightarrow
\mathscr P_X
\longrightarrow
\text{age/episode augmentation}
\longrightarrow
\text{anonymous }A,R,B,C,M
\longrightarrow
Z_0,\ldots,Z_9
\longrightarrow
\text{all-rank residence and leakage}.
\]

At no point may

\[
p=1,\qquad a=3,\qquad m=3
\]

be identified.  This source family begins with Lorentzian \(9+1\), so even a
successful visible spatial-rank calculation would still not derive one time
direction or Lorentzian signature.

## Required conclusion

The response must end with one of three verdicts:

1. `certified within the declared finite-K world-sheet model`;
2. `declared finite-K world-sheet model excluded`;
3. `inconclusive`.

It must then state, in separate paragraphs:

- the normalized regular and exceptional first-entry masses;
- the encounter-rank mixture;
- the event-conditioned \(\sigma_3\) result and its Palm-weight status;
- whether \(T,j,b,\ell\) are jointly identified;
- the regulator and preparation dependence;
- the earliest still-missing physical component;
- the exact next composition into the response layer.

A successful outcome is a rank-blind near-encounter law with an honest
probabilistic rank and singular-value ledger.  It is not yet strict
three-selection, a visible-rank theorem, or an explanation of \(3+1\).
