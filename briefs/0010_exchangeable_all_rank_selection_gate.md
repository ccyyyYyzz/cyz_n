# Brief 0010 — exchangeable all-rank selection gate

Status: active

Baseline commit: `9993d6aa4346ed010023967b64f9a0f3c9210862`.

## Role

Act as the originating mathematical physicist.  Do not act as a referee and do
not merely summarize the audit.  Repair the strongest valid construction and
then decide the real selection question.

Read, in order:

1. `state/PROJECT_STATE.md`;
2. `responses/0009_source_authorized_winding_geometry_hybrid.md`;
3. `decisions/0009_adopt_as_conditional_transition_scaffold.md`;
4. this brief.

The project remains one closed loop.  Do not discuss journals or divide the
program into papers.

## Canonical correction

Response 0009 now correctly exposes an arbitrary-cardinality conditional
transition: for

\[
|L|=m,
\]

its mechanism attempts to carry a visible-rank-\(m+1\) predecessor into a
visible-rank-\(m\) tube.  This is useful, but it proves no preference for
\(m=3\).  Permuting a three-element subset removes axis names; it does not
remove the supplied cardinality three.

Your task is not to relabel that corollary as selection.  Derive a genuine
all-rank comparison from one target-neutral initial law and one generator, or
prove sharply why the current source/closure family cannot do so.

## Part I — complete and repair the finite model

Give one fully specified finite generator \(Q_\theta\), not pseudocode.  The
parameter vector \(\theta\) may contain physical couplings, impact/recollision
parameters, band calibration and interval-error parameters.  It may not contain
a target rank, a preferred subset, or a controller keyed to three.

Repair all of the following.

1. Occupations live in \(\mathbb N_0\), with explicit cutoff boundary rules.
2. Choose exactly one impact-mark semantics:
   - integrate marks into one thinned accepted-event kernel; or
   - retain marks as state and write the full encounter/accept/reject generator.
   Do not use both an integrated accepted hazard and an undefined
   \(\mathcal L_{\rm marks}\).
3. State every winding and momentum reaction, reverse channel, reservoir reset,
   continuous reservoir drift, cemetery transition and probe transition.
   When occupations are fixed between reactions, state \(\dot E_0=0\).
4. Prove nonnegativity, row-sum zero, energy/charge accounting, nonexplosion,
   source-domain stopping and \(S_9\) equivariance.
5. Keep the anisotropic mark law explicitly classified as a new measurable
   closure.  The GKM amplitude is source-derived; the generic anisotropic
   recollision distribution is not.
6. Do not claim that a stochastic birth--death lift exactly derives the source
   mean Boltzmann equation unless the moment closure is proved.

You may use a finite interval/Galerkin state abstraction, but then give the
actual enclosure map and residual budget.  A list saying that such an
implementation could be made is not an executable.

## Part II — repair the arbitrary-m conditional lemma

State the conditional transition theorem for every \(m=0,\ldots,8\), not only
for three.

### Geometry comparison

The old inequality

\[
\dot h\le-\underline u h-c_gP_-
\]

fails after \(h<0\).  Give a correct piecewise proof: first control the
nonnegative-\(h\) interval, then use the correct \(\bar u\) endpoint on the
negative side, exhibit a forward negative region, and integrate a valid finite
recollapse-time bound.

### Attraction and leakage

The probability theorem must:

1. protect all \(9-m\) trapped directions during attraction;
2. include \(T_{\rm clr}\) in the arrival time when clearance is not already
   complete;
3. define response error either as a deterministic spectral enclosure or as a
   coverage probability, never add an unlabeled norm error to a probability;
4. account for annihilation losses accumulated across time windows;
5. use either one full-horizon Poisson bound per trapped direction or a genuine
   uniform one-window exit probability over the entire tube;
6. include every exit face in \(\tau_{\rm exit}\): occupation, pressure, gap,
   source-validity, residue/observability, approximation and cemetery exits;
7. treat reverse creation without falsely assuming the death intensity remains
   bounded by its initial value;
8. specify the relative topology of the open cell when occupations are discrete
   and the Hamiltonian constraint is exact.

If only a subset of exit modes is bounded, name that subset rather than calling
the result a total tube-exit probability.

## Part III — the actual three-selection test

For each physical parameter \(\theta\), declare one initial law
\(\mu_\theta\) satisfying all of the following:

1. it is \(S_9\)-exchangeable;
2. it is generated without conditioning on visible rank, the number of clear
   directions, or a preferred subset;
3. its parameterization does not contain the numeral three or any equivalent
   target cardinality;
4. its source-valid support and initial-measure uncertainty are explicit.

Use one generator, port, bandwidth family and error model for all output ranks.
Let \(Z_m\) be the response-defined rank-\(m\) cell, introduced only after the
trajectory and anonymous response have been generated.  At minimum compute or
bound, for every \(m=0,\ldots,9\):

\[
H_m(T)=\Pr_{\mu_\theta}\!\left[\tau_{Z_m}\le T\right],
\]

\[
R_m(T_0,T_1)=
\mathbb E_{\mu_\theta}
\left[
\frac1{T_1-T_0}
\int_{T_0}^{T_1}\mathbf1_{Z_m}(X_t)\,dt
\right],
\]

and a finite-horizon residence/leakage quantity.  Separate attraction from
initial mass already placed in \(Z_m\).

A genuine result requires an open relative parameter cell \(\Theta_*\) and a
uniform positive margin \(\delta\) such that

\[
R_3(\theta)
\ge
\max_{m\ne3}R_m(\theta)+\delta
\qquad
(\theta\in\Theta_*),
\]

with analogous basin and robustness statements.  The number three may appear
in this final comparison of outputs; it may not appear in \(\mu_\theta\),
\(Q_\theta\), the port, the band, or the reaction mechanics.

If the current source-faithful family cannot yield this margin, prove the
sharpest no-go or underdetermination result.  Identify the smallest additional
initial-measure, interaction or action term that could be measured without
encoding three.

## Mandatory all-rank controls

1. Run the same code and parameters over every output rank \(m=0,\ldots,9\).
2. Include the Easther--Greene--Jackson--Kabat all-or-nothing control; it must
   not be reported as a three preference.
3. Include a symmetric equal-hazard control.  Any rank advantage arising only
   from initial mass must be reported as initial-measure bias.
4. Include parameter cells producing non-three winners or no separated winner.
5. Randomly permute all directions and ports; only output labels may permute.
6. Perturb the predeclared band/error interval.  If the winner loses its margin,
   report inconclusive.
7. Demonstrate that the conditional \(m+1\to m\) lemma works for at least
   \(m=2,3,4\); otherwise a hidden three-branch is present.

## One finite operator, not three related surrogates

For the positive finite control, use the same finite \(Q_\theta\) to compute:

\[
\Pr(\tau_{\rm exit}>T),
\qquad
\Pr(\tau_{Z_m}\le T),
\qquad
C(zI-Q_\theta)^{-1}B,
\]

and every claimed pole and residue.  A killed restriction may be used for a
declared target/exit event, but it must be derived from \(Q_\theta\) and need
not share the full spectrum.

Do not replace the full generator by an unrelated frozen \(2\times2\) matrix.
If a projection is used, prove invariance or give a quantitative projection
error.  For a nonstationary trajectory, use a two-time propagator/Duhamel
response unless a quasi-stationary or adiabatic approximation is certified.

The result sought here is joint forward compatibility and falsifiability.  Use
the word identifiability only if the physical parameter-to-data map is proved
injective on the declared parameter cell.

## Operational response boundary

A linear passive scalar transfer does not automatically supply the
multiplication map, character panel or physical-handle completeness used by the
relation quotient.  Either:

1. add and normalize a concrete nonlinear, mixed, or correlation port that
   measures the required products; or
2. carry the existing multiplicative/character panel as a separate explicit
   experimental premise.

Do not claim full microscopic Hautus observability of geometry, occupations and
marks merely because all nine scalar harmonics are visible.  State exactly
which pre-quotient sector is controllable/observable.

## Required conclusion

End with exactly one of:

1. a complete finite all-rank model plus a proved open-cell, exchangeable-law
   three-selection margin; or
2. a complete arbitrary-\(m\) conditional model plus a sharp theorem that the
   current source/closure family does not select three, followed by the smallest
   measurable non-target-keyed missing term.

Classify every substantive statement as `primary-source derived`, `derived
from a newly proposed action`, `exact theorem about a declared model`,
`controlled asymptotic/numerical conjecture`, `no-go/underdetermination`, or
`open gate`.

## Delivery contract

Write the full answer to
`responses/0010_exchangeable_all_rank_selection_gate.md`, then commit and push
it directly to `main`.  Do not open a pull request, offer a download, or leave
the result only in chat.
