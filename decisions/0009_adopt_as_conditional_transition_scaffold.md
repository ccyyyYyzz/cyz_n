---
brief: 0009
response_commit: 31992da
status: conditionally_adopted
supersedes: none
---

# Decision 0009 — adopt the source skeleton, not the claimed three-selection theorem

## Verdict

The repaired final Response 0009 is adopted as a useful **source-faithful
design scaffold** and as
a map of the new measurable closures that are required.  It is not adopted as
an exact derivation or selection of three visible spatial directions.

Its strongest presently valid positive interpretation is:

> after the comparison and probability bounds are repaired, the declared
> model can provide a conditional, scale-relative \(k+1\to k\) rank-transition
> witness with no microscopic rank state and no geometry jump.

For \(k=3\), this is a conditional \(4\to3\) witness.  It does not yet explain
why the same anonymous dynamics prefers \(k=3\) over every other \(k\).

The original `03cf5c1` draft presented the construction through a
three-direction corollary.  The final `31992da` response correctly generalized
the statement to arbitrary \(m\).  That repair is canonical: it exposes rather
than resolves the absence of a preference for three.

## Adopted source boundary

The following source-level statements are retained.

1. The homogeneous anisotropic nine-torus shifted-dilaton equations, their
   Hamiltonian constraint, and the signs of winding/momentum energy and
   pressure are supplied by Easther--Greene--Jackson--Kabat.
2. A wound-string reaction may change occupations and an explicitly declared
   energy reservoir.  It may not directly jump a scale factor, a velocity, a
   dimension, a projector, or an operational rank.
3. The GKM impact amplitude supplies a fixed-(d), source-regime collision
   kernel on restricted isotropic strata.  It does not uniquely determine a
   generic nine-direction anisotropic hazard.
4. A source cosmology does not determine an operational intervention/readout
   port.  A port/action is logically additional.
5. Positive finite-width rates support finite-time concentration or
   metastability, not an exact invariant rank-three phase.
6. The source time coordinate and the rolling shifted-dilaton branch are
   supplied.  Retarded/advanced selection, a universal all-field cone, and a
   duality-complete primitive stringlike orbit remain open.

## Newly declared closures

The following objects are permitted as explicit, measurable hypotheses but
must not be relabelled primary-source derived:

- an occupation-level stochastic lift of the Boltzmann drift;
- a reservoir and its reset law;
- a normalized anisotropic recollision/impact mark kernel;
- the choice between an integrated thinning hazard and an explicit persistent
  mark process;
- a democratic all-direction probe action;
- a multiplicative/character response panel and its physical scale band.

The mean drift of a birth--death process generally contains
\(\mathbb E[W^2]\), not \((\mathbb E W)^2\).  Therefore a stochastic lift is
not uniquely or exactly derived merely because its coordinate drift resembles
the source Boltzmann equation.

## Adopted structural advances

The following parts of 0009 materially advance the program.

1. The microscopic state contains geometry and occupation data but no rank or
   preferred projector.
2. Unit-pair resets can preserve charge and total matter energy while leaving
   geometry continuous.
3. The anisotropic-extension obstruction is real.  A positivity-preserving
   witness should be used, for example
   \[
   H^{(\epsilon)}=H\exp(\epsilon F)
   \]
   on the positive-hazard region, with the zero set treated separately.
4. A predeclared all-nine-direction Fourier port can define a scale-relative
   visible rank without passing that rank to the mechanism.
5. High-bandwidth readout must retain the hidden six directions; low-band rank
   is an intervention-algebra statement, not an ambient-dimension statement.
6. A zero residue is an unobserved mode.  A supplied retarded boundary is not
   a dynamically selected time arrow.
7. First passage, leakage, and response must ultimately be forward predictions
   of one declared model rather than unrelated fitted matrices.

## Exact blockers in the proposed theorems

### 1. The recollapse comparison inequality changes sign

From

\[
\dot h=\nu h+cP,
\qquad
-\bar u\le\nu\le-\underline u<0,
\qquad
P\le-P_-<0,
\]

0009 uses

\[
\dot h\le-\underline u h-cP_-
\]

after (h) becomes negative.  That inequality is valid only for (h\ge0\).
The proof must be split at the first hitting of (h=0); on the negative side
the opposite endpoint \(\bar u\) is required.  Consequently the displayed
recollapse-time bound is not yet proved.

### 2. The leakage union bound misses accumulated losses

The bound (6N_Tp_{\rm blk}\) reuses a one-window Poisson tail.  Annihilations
can accumulate across windows: two windows containing one event each can cross
a two-event buffer even though neither window contains two events.  A safe
finite-horizon bound must be written over the whole interval (T), separately
for every trapped direction, or must use a genuine uniform one-window exit
probability over the entire tube.

The attraction estimate also needs protection for all six trapped directions,
not only the singled-out marginal direction.  If clearance begins during the
proof rather than before it, the attraction time must contain
\(\max(T_{\rm rec},T_{\rm clr})\).

### 3. The displayed PDMP generator is incomplete

The response simultaneously integrates the impact mark into an accepted-event
hazard and retains an undefined \(\mathcal L_{\rm marks}\).  It must choose one
of two complete constructions:

1. integrate out marks and use only the thinned accepted jump kernel; or
2. retain marks as state and write the complete collision/accept/reject kernel.

In addition, \(\mathcal L_K\), cutoff-boundary rules, (F_{\rm probe}\), and
the reservoir drift are not fully specified.  The occupation domain must use
\(\mathbb N_0^9\).  With fixed occupations between jumps,
\(\dot E_0=0\) must be stated explicitly.

### 4. A linear scalar port does not by itself supply multiplication

The circle relations and contextual quotient require products, characters,
or nonlinear/multicorrelation response data.  A linear transfer matrix alone
does not identify the multiplication map used in the rank proof.  The existing
multiplicative/physical-handle panel must be included as an independent
experimental premise, or a concrete nonlinear/mixed response port must be
added.

A passive scalar at zero background can identify frozen directional spectral
parameters.  It does not automatically make the full geometry--occupation
state controllable and observable in the Hautus sense.

### 5. The full PDMP, killed generator, and frozen Jacobian are not one spectrum

The killed semigroup formulas are valid for a fully declared finite generator.
The frozen (2\times2) block is only a local surrogate unless an invariant
subspace or a controlled Galerkin projection is proved.  For the block itself,
Hurwitz stability requires both

\[
a+\Omega>0,
\qquad
a\Omega-gh>0,
\]

and the simple-pole residue formula requires distinct poles.

For a nonstationary attraction trajectory, the exact response is a two-time
propagator/Duhamel kernel.  A frozen resolvent may be used only with a declared
adiabatic or quasi-stationary error bound.  The next executable should instead
use one finite generator (Q\) for both killed-semigroup and
\(C(zI-Q)^{-1}B\) calculations.

## Why the repaired theorem does not select three

The initial 0009 draft illustrated the predecessor family by assuming exactly:

- three already-clear, positive-pressure, low-gap directions;
- one additional low-gap but wound direction that will recollapse;
- six high-gap trapped directions.

Taking the union over all three-element subsets removes coordinate names but
does not remove the input cardinality three.  The final response now makes the
same argument with the formal
replacement

\[
3\mapsto k,
\qquad
4\mapsto k+1,
\qquad
6\mapsto 9-k,
\]

and yields a conditional \(k+1\to k\) statement whenever the corresponding
clearance, pressure, and spectral inequalities are supplied.  Nothing in the
current proof fails structurally for (k\ne3\).

Therefore the final arbitrary-cardinality statement is retained only under the
name **conditional \(k+1\to k\) metastable response-transition lemma**.

## Required target-neutral selection criterion

The next construction must not condition its initial family on a chosen rank.
For a parameter \(\theta\), require:

1. one (S_9\)-exchangeable initial law \(\mu_\theta\) on the raw source state,
   specified without visible-rank conditioning;
2. one (S_9\)-equivariant generator \(Q_\theta\), port, band, and error model;
3. response-defined rank cells \(Z_k\), (k=0,\ldots,9\), used only after the
   dynamics and response have been generated.

For a fixed observation window define the residence score

\[
R_k(\theta)
=
\mathbb E_{\mu_\theta}
\left[
\frac{1}{T_1-T_0}
\int_{T_0}^{T_1}
\mathbf1_{\{X_t\in Z_k\}}\,dt
\right].
\]

A genuine three-selection result requires an open relative parameter cell
\(\Theta_*\) and a uniform margin \(\delta>0\) such that

\[
R_3(\theta)
\ge
\max_{k\ne3}R_k(\theta)+\delta
\qquad
(\theta\in\Theta_*),
\]

together with nontrivial basin mass, a residence/leakage certificate, and
robustness to the predeclared bandwidth/error perturbation.  The numeral three
appears only in the final comparison of outputs, never in \(\mu_\theta\),
\(Q_\theta\), the port, or the acceptance mechanics.

The equal-hazard/all-or-nothing source control must be included as a mandatory
negative result.  A model that gives the same construction for every (k\), or
whose (R_3\) advantage comes entirely from the initial law, has not selected
three.

## Canonical hard-false fields after 0009

- `source_complete_anisotropic_hybrid_derived = false`
- `exact_rank_three_invariant_phase = false`
- `target_neutral_three_preference_proved = false`
- `full_pdmp_generator_completed = false`
- `full_microscopic_hautus_observability = false`
- `same_spectrum_departure_proved = false`
- `time_selected = false`
- `universal_common_cone_derived = false`
- `primitive_stringlike_orbit_selected = false`
- `genuine_3p1_selection = false`

## Next move

The next brief must do exactly three things:

1. repair the source-faithful construction into a complete finite generator;
2. state and prove the arbitrary-(k) conditional lemma with correct
   finite-horizon bounds;
3. either produce the exchangeable all-(k) selection margin above, or prove
   sharply that the declared source/closure family cannot prefer three without
   an additional initial-measure or interaction term.
