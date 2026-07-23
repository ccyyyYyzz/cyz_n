---
brief: 0017
status: conditionally_adopted_as_rank_blind_analytic_and_event_semantics
supersedes: 0016_missing_near_encounter_law_definition
external_repair_commit: 62323ad285e5e96c2fc816f818c0701a86ee4692
verified_integration_commit: a47fa10
---

# Decision 0017 — adopt the rank-blind analytic controls, not a physical first-entry law

## Verdict

Brief 0017 closes the mathematical interface for an unconditioned
bundle-valued F1 near-encounter law.  It fixes the first-entry/outer-exit
history semantics, keeps every exceptional outcome, derives the invariant
rank and normal objects from the selected event, and identifies the analytic
hard-edge controls against which a later physical population must be tested.

It does not yet compute that population.  The finite-\(K\) physical
first-entry law, its rank mixture and its event-conditioned
\(\sigma_3\)-tail remain inconclusive.

## Adopted facts

1. Event selection is rank blind.  Rank, normal dimension,
   \(P_N,b,\ell\) and reaction data are downstream marks and may not enter the
   source draw or root selection.
2. The ideal output is a pushforward of the unconditioned source measure onto
   a disjoint regular/exceptional event space.  Invalid, censored, tied,
   degenerate, grazing, torus-ambiguous and numerically unresolved mass is
   retained rather than redrawn or renormalized away.
3. First entry is a hysteretic stopping-time object.  Repeated inner contacts
   before strict outer overshoot remain in one episode; closest approach is a
   secondary completed-episode mark.
4. For opposite-wound F1 pairs,
   \[
   \det(J^\top J)
   =|q\wedge u|^2+|p_1\wedge q\wedge u|^2 .
   \]
   Exact rank-two and arbitrarily near-degenerate exact-rank-three controls
   are retained without replacing small positive singular values by zero.
5. For the fixed-point iid \(\mathbb R^{8\times2}\) Gaussian surrogate,
   \[
   \Pr(\sigma_{\min}\le\epsilon)
   \sim\frac{\sqrt{\pi/2}}{48}\epsilon^7,
   \]
   equivalently the smallest Gram eigenvalue has exponent \(7/2\).
6. Under the declared pure volume-Palm surrogate, the exponent becomes eight
   with coefficient \(1/105\).  The affine Kac--Rice factors scale as
   \(\delta^2,\delta^{-1},\delta\).
7. These exponents are analytic controls, not the physical first-entry
   exponent.  Constraint density, spatial Morse determinant, inward flux,
   armed survival and no-earlier-entry selection can alter the tail; the
   curvature-lifted control demonstrates that transfer is conditional.
8. A simple branchwise boundary root satisfies
   \[
   \det Dg=F_t\det H_{\sigma\sigma}.
   \]
   This is only a local regularity identity.  Global spatial minimality,
   image coverage, no-earlier-entry, ordering, outer exit and closest coverage
   remain separate certificates.

## Reproducibility boundary

The repaired external controls and the independent analytic-tail package pass
27 discovered tests on Windows.  The repaired report also replays under WSL
Linux with the same canonical payload SHA-256

```text
35194fabc947a4832b7fec59f9ac717595ff97dc0fabab0bb746f9b682139a59
```

after replacing platform-dependent float eigenvalues by a deterministic
high-precision Decimal Jacobi calculation.  The independent analytic-tail
report canonical SHA-256 is

```text
7c6120573e17b0e8fa4c8a9d036bd213fbc8354376d3ae623241716012aebc22
```

The source-measure and event-ledger examples inside the 0017 controls remain
parameterized or synthetic.  Their counts are not physical probabilities.

## Canonical status after 0017

- `rank_blind_event_interface = true`
- `first_entry_hysteresis_semantics = true`
- `exceptional_mass_retained = true`
- `raw_small_singular_values_retained = true`
- `gaussian_fixed_point_tail_exponent_7 = analytic_control_only`
- `pure_volume_palm_tail_exponent_8 = analytic_control_only`
- `physical_principal_source_cell_frozen = false`
- `total_executable_event_record_contract = false`
- `certified_exhaustive_root_solver = false`
- `physical_finite_K_first_entry_law = false`
- `event_conditioned_rank_mixture = not_computed`
- `event_conditioned_sigma3_tail = not_computed`
- `three_plus_one_selection = false`

## Next move

Freeze and derive one exact principal finite-\(K\) source, implement a
constrained sampler without validity redraw, and close a total event-record
schema.  Then implement a replayable interval solver with gap-free image/box
coverage and compute the unconditioned law of

\[
(T,j,b,\ell,a,\sigma_3)
\]

before composing any dimension-selection dynamics.
