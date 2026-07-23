---
brief: 0016
status: conditionally_adopted_as_source_kinematic_ceiling
supersedes: fixed_frame_arity_as_physical_input
baseline_commit: c73fc0e8b6286c281b8577a9879de5e7c15fdc4a
---

# Decision 0016 — adopt the conditional F1 three-ceiling, not three-selection

## Verdict

The fixed registered frame arity is removed from the physical claim chain.
The adopted local object is the invariant encounter rank

\[
a(e)=\operatorname{rank}D\Phi_e
\le\min(d,2p+1),
\]

computed from the two carrier tangent spaces and relative motion.  For F1,
\(a\le3\), and rank three requires a non-collinear local pair jet with
relative velocity outside its tangent plane.  A positive metric-normalized
singular-value margin is a sufficient worst-case robustness certificate, not
a necessary condition for a probabilistic closure.

The JJP \(D-4=d-3\) impact space is adopted only on that nondegenerate
rank-three stratum.  A strictly straight pair with opposite winding on the
same cycle has rank at most two; the cited GKM source model does not derive a
local tangent/wiggle preparation that repairs this degeneracy.

Across a predeclared effective-source family, the physical result is therefore
a conditional source-side `three-ceiling`.  It is not strict three-selection,
not yet a visible-rank ceiling and not a visible-\(3+1\) result.

## Adopted facts

1. Encounter rank is a coordinate-independent output of transversality to the
   diagonal.  A singular-value margin additionally requires registered target
   and encounter-parameter metrics.  An exact diagonal hit has \(b=0\);
   finite impact requires a preregistered closest-approach or first-entry
   section.  The pair jet determines \(N_j\), not the separate
   \(b\in N_j\).
2. If the pair-jet pushforward has a density on matrix space, the generic rank
   is \(\min(d,2p+1)\).  On each positive-probability connected analytic
   branch \(C\) of a constrained jet manifold, the conditional generic rank
   is its maximal attainable \(r_C\) when an \(r_C\)-minor is not identically
   zero and the conditional law has a branch-volume density.  The full source
   law may mix branches with different generic ranks.  This theorem does not
   apply to a law supported on a lower-rank determinantal subset of a branch.
3. For F1, rank three is equivalent to two non-collinear tangents plus
   relative velocity outside their span.  Straight same-cycle opposite
   winding gives rank at most two.
4. The impact normal space has dimension \(d-a\).  The equality
   \(d-a=D-4=d-3\) holds exactly when \(a=3\).
5. JJP's angled-string source geometry contains the required two independent
   tangents and relative-velocity direction.  Momentum transfer belongs to
   their normal space and cannot be reused as a third incoming column.
6. A block-diagonal fixed-arity scheduled kernel conserves arity pathwise.
   The 0015 process therefore cannot select arity three from an arity-neutral
   open basin.
7. Ordered distinct \(a\)-frames have the exact onset
   \[
   N_{\rm valid}(q,a)=q!/(q-a)!
   \]
   for \(q\ge a\), and none for \(q<a\).  This becomes physical only after
   \(a\) is derived upstream and still does not identify response-visible
   rank.
8. Under the two declared uniform ball and box impact controls, extending the
   Gaussian across the full support gives the exact \(g_c^{\rm ball}\) and
   \(g_c^{\rm box}\) expressions in Response 0016.  Their monotonicity and
   large-\(\rho\) bounds are adopted as theorems of that surrogate.  The
   small-\(b\) extension and the preparations are not source-derived.
9. The deterministic standard-Python artifact reproduces the frame onset,
   suppression tables and six Gram controls, including domain-metric
   rescaling and the fixed scattering-axis falsifier.  Its 8/8 tests pass and
   its final report
   SHA-256 is
   `08cc622e415d0594b85fa04230f0e87d68184402e9ec1500e1923f42f20e274b`.

## Claims not adopted

### Universal rank-three preparation

Global opposite winding does not supply a local non-collinearity distribution
or the distribution of
\(\sigma_3(G^{1/2}D\Phi_eH^{-1/2})\).  String thickness is positional width,
not a tangent margin.  Both a possible uniform lower bound and the weaker
small-singular-value tail of the physical near-encounter ensemble remain
unidentified.

### Preparation-independent impact probability

The amplitude gives a large-impact reaction profile conditional on impact.
It does not give the holding-time law, impact preparation or unresolved core.
The ball and box measures are target-neutral controls whose supports include
the core.  Using their full averages therefore also declares a profile
extension.  A source distribution concentrated near zero impact can change or
remove the codimensional suppression.

### Strict three-selection

For a predeclared family with \(\ell\) effectively extended source
directions, general-position F1 encounters have
\(a_\ell=\min(\ell,3)\) and \(c_\ell=(\ell-3)_+\).  Impact codimension
therefore distinguishes the source-family upper side \(\ell>3\), but not one,
two and three.  A single fixed \(T^9\) event has \(c=9-a\), and this result may
not be relabeled as a variable response-visible \(m\).  The GKM 2012
successive-fluctuation scenario does not establish a lower-side rank-three
residence margin over an identified open source family.

### Physical source-to-return closure

The near-encounter event rule, holding-time law, joint bundle-valued
pair-jet/impact law, post-miss history, reference-measure reverse flux and
continuum preparation remain unidentified.  The GKM recollision time and
fresh impact redraw remain numerical closures.

### Anonymous visible rank and time

Carrier rank and the number of large source axes are not the response-visible
rank.  The anonymous \(Z_0,\ldots,Z_9\) residence comparison has not been run
on a physical kernel.  The F1/\(T^9\) source also begins with Lorentzian
\(9+1\) time and does not derive the one time direction.

## Canonical status after 0016

- `fixed_frame_arity_as_physical_input = false`
- `carrier_dimension_p_distinct_from_encounter_rank_a = true`
- `encounter_rank_a_distinct_from_visible_rank_m = true`
- `coordinate_invariant_encounter_rank = true`
- `metric_normalized_rank_margin_defined = true`
- `source_identified_positive_rank3_margin = false`
- `straight_opposite_winding_rank = at_most_2`
- `JJP_D_minus_4_domain = noncollinear_rank3_stratum`
- `fixed_arity_superselection = true`
- `impact_codimension_suppression_under_declared_controls = true`
- `impact_preparation_source_identified = false`
- `conditional_source_family_F1_three_ceiling = true`
- `visible_rank_three_ceiling = false`
- `strict_three_selection = false`
- `physical_source_to_return_kernel = false`
- `anonymous_visible_rank_three = false`
- `one_time_direction_derived = false`
- `genuine_3p1_selection = false`

## Next move

Freeze the fixed-arity constructor as a software control.  The next physical
calculation must construct the joint near-encounter law

\[
\mathcal H_X(dT,dj,db\mid h),
\qquad b\in N_j,
\]

for globally opposite-wound F1 pairs on one fixed rectangular-\(T^9\) source
cell.  It must preregister the microscopic generator, initial law or fixed
conditional state, closest-approach/first-entry rule and sampling rule, with
no rank-conditioned event selection.  It must measure the mass of each rank
stratum and test either a preregistered uniform \(\sigma_3\) margin or a
controlled small-value tail before applying the event-specific normal
projector.

The resulting continuous event law must then be composed with an exact age
augmentation and anonymous \(A,R,B,C,M\) ports.  The decisive output is an
all-rank entrant strict-residence and leakage comparison, not a count of
source-large axes.
