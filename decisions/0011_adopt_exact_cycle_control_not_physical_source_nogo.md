---
brief: 0011
response_commit: 59a10b9
status: conditionally_adopted_as_exact_control
supersedes: none
---

# Decision 0011 — adopt the exact cycle control, not the claimed physical source-family no-go

## Verdict

Response 0011 repairs the logical error in Response 0010 and produces a real
global winner crossing in one explicit finite exchangeable model.  The
six-state cycle, its fixed product initial law and its endpoint score tables
are adopted as an exact all-rank **occupancy control**.

The stronger description of that cycle as an embedded, source-compatible
winding--geometry family is not adopted.  The response does not give the
geometry grid, occupations, reservoir states, work/energy labels or reaction
propensities needed to prove that its two endpoint generators belong to the
previously declared source-authorized hybrid.  Its response replay is also
still an architecture rather than a complete finite Green/relation artifact.

Accordingly, the cycle proves architecture-level all-rank underdetermination.
It does not yet prove a physical no-uniform-margin theorem for the audited
winding--geometry completion fiber.

## Adopted exact results

1. The local generator

   \[
   q_v=
   \begin{pmatrix}
   -1&1&0&0&0&0\\
   0&-1&1&0&0&0\\
   0&0&-1&1&0&0\\
   0&0&0&-v&v&0\\
   0&0&0&0&-10&10\\
   10&0&0&0&0&-10
   \end{pmatrix}
   \]

   and the ninefold Kronecker sum define a finite irreducible,
   \(S_9\)-equivariant CTMC for every \(v>0\).
2. The fixed law
   \((1/6,\ldots,1/6)^{\otimes9}\) is positive-support,
   exchangeable and rank-unconditioned.
3. The varied scalar \(v\) is a common local rate and contains no visible
   count or rank-three branch.
4. For the supplied binary low/high labels and the window \([3,4]\), the exact
   binomial reduction gives:

   - \(v=65/92\): rank three is the unique average-occupancy winner and
     \(\Delta_3\simeq 0.05028933\);
   - \(v=5/4\): rank two is the unique average-occupancy winner and
     \(\Delta_3\simeq-0.06413748\);
   - the crossing occurs at
     \(v_*\simeq0.93280813\), or
     \(\tau_*\simeq0.41636695\) on the declared linear path.

   Independent matrix-exponential quadrature reproduces these values.
5. The response correctly retracts the generic claims that every rank can
   win and that a nonzero Duhamel derivative alone reverses a winner.
6. The label-stable Duhamel theorem is exact when the projectors are proved
   constant on an open response-margin neighborhood.
7. The row-generator / column-augmented-channel orientation is correctly
   \(Q/Q^T\), reset maps have an unambiguous source and target, empty-cell
   leakage is undefined, and continuum recollapse is separated from finite
   first-passage probability.
8. A reachable orbit-rate ledger is correctly called a complete sufficient
   specification rather than a proved minimal statistic.

## Claims not adopted

### 1. The cycle is not yet embedded in the source-authorized hybrid

The six named states are not supplied with explicit
\(\lambda,h,\bar\phi,\nu,P,E,\ell\), occupation and reservoir values.  The four
geometry rates are not obtained from the declared dilaton-gravity upwind
field and grid spacings.  Some displayed cycle edges combine radius and
velocity changes that were separate coordinate moves in the earlier finite
operator.

The sentence "choose the labels so that the work identity holds" is not an
energy ledger.  Likewise, the constant reverse rate \(v\) is not connected to
reactant populations, reservoir energy or a microscopic reverse-channel
law.  Source compatibility is therefore a conjectured embedding, not a
proved property of the two completions.

### 2. The response classifier is not yet fully executable

The local oscillator matrices are explicit, but the complete augmented
probability/product spaces, indexed \(B,C,M\) matrices, calibration rules and
uniform residue/relation/survival margins are not.  The score calculation uses
the supplied local indicator \(\chi\); it does not independently reconstruct
that indicator from a replayable Green/relation calculation.

The correct label is therefore `supplied-local-label exact control`, not a
completed anonymous response theorem.

### 3. Average occupancy is not strict basin residence

The endpoint crossing is proved for

\[
R_k^{\rm occ}
=\int_3^4\Pr(K_t=k)\,dt.
\]

No endpoint table is given for strict no-exit residence, entrant strict
residence, conditional retention or worst leakage.  Rapid circulation can
change an occupancy winner without producing a stable selected basin.  The
result is therefore an occupancy-margin control, not yet a stable-selection
gate no-go.

### 4. The generic residual construction remains an enclosure architecture

A union of residual bins is a finite validated set state, but the response
does not define unique rates and normalization for subsequent set-valued
updates.  The explicit cycle tries to avoid this issue with the singleton
residual \(\{0\}\), whose invariance depends on the missing work ledger noted
above.

## Canonical status after 0011

- `explicit_exchangeable_cycle_winner_crossing = adopted`
- `cycle_occupancy_tables_and_crossing = adopted`
- `local_label_stable_duhamel_theorem = adopted`
- `row_Q_column_QT_orientation = adopted`
- `complete_sufficient_kernel_ledger = adopted`
- `source_compatible_cycle_embedding = false`
- `fully_replayed_cycle_response_classifier = false`
- `strict_residence_winner_crossing = false`
- `physical_source_family_global_nogo = false`
- `target_neutral_three_preference_proved = false`
- `genuine_3p1_selection = false`

## Next move

Do not spend another round polishing the abstract cycle.  Retain it as a
mandatory negative control and move to the missing physical input: one
pre-classifier, target-neutral marked encounter/recollision process with an
absolute encounter clock, normalized impact marks, compactification
dependence, history, reverse channels and a fixed exchangeable initial law.
Only after that input is fixed should the same anonymous all-rank strict
residence gate be replayed.

