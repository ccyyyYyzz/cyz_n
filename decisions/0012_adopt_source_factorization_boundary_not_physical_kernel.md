---
brief: 0012
response_commit: c4698b6
status: conditionally_adopted_as_source_factorization_boundary
supersedes: none
---

# Decision 0012 — adopt the source-factorization boundary, not a completed physical kernel

## Verdict

Response 0012 identifies the right pre-classifier object and repairs the
stability statistic.  Its separation of absolute encounter timing, encounter
marks, conditional channels, recollision history, reverse production and the
initial law is adopted.  So are its finite-CTMC first-entry, entrant
strict-residence, conditional-retention and worst-leakage formulas.

The response is not adopted as a populated target-neutral physical kernel or
an exact executable.  The constitutive tuple

\[
(T_{e,x},K_{e,x},R_{e,x},\Omega_R,\mu_0)
\]

is precisely what remains free.  The grid, rate tables, reset map, work ledger,
response embeddings and numerical error bounds are not instantiated.  A
symbolic interface that becomes complete after these objects are supplied is
not yet the object demanded by Brief 0012.

The durable result is therefore an identifiability boundary and a concrete
measurement route.  It is neither a positive rank-three theorem nor a
source-regime exclusion.

## Adopted exact results

1. In a frozen geometry cell, a finite transient encounter family may be
   factorized as

   \[
   H(d\tau,dm\mid h)=e_h^T e^{\tau T}K(dm)\,d\tau,
   \qquad T\mathbf1+K(M)\mathbf1=0,
   \]

   with the absolute clock and normalized mark/channel laws kept separate.
2. Given a complete finite row generator \(Q\), fixed initial law \(\mu_0\)
   and response cells \(Z_m\) fixed before cardinality is counted, let
   \(Q_{\neg m}\) be killed on first entry and \(Q_m\) killed on exit.  Then

   \[
   A_m(T)=\int_0^T
   \mu_{0,\neg m}e^{tQ_{\neg m}}Q_{\neg m,m}\mathbf1\,dt
   \]

   is first-entry mass and

   \[
   E_m(T,\Delta)=\int_0^T
   \mu_{0,\neg m}e^{tQ_{\neg m}}Q_{\neg m,m}
   e^{\Delta Q_m}\mathbf1\,dt
   \]

   is entrant strict residence.  The ratio \(E_m/A_m\) is defined only when
   \(A_m>0\).
3. Initial strict retention is

   \[
   N_m^{\rm init}(\Delta)=\mu_{0,m}e^{\Delta Q_m}\mathbf1,
   \]

   and worst leakage from a nonempty cell is

   \[
   L_m^{\rm worst}(\Delta)=1-
   \min_{x\in Z_m}e_x^Te^{\Delta Q_m}\mathbf1.
   \]

   Average occupancy remains diagnostic only.
4. Conditional channel tables and an integrated one-encounter mark law do not
   identify an absolute clock.  In a frozen phase-type family,
   \((T,K)\mapsto(aT,aK)\) preserves the integrated mark law and conditional
   channels while rescaling encounter time.
5. A one-mark marginal does not identify recollision correlations.  For the
   response's binary example, iid redraw and persistent history give

   \[
   (1-p/2)^n,
   \qquad
   \tfrac12+\tfrac12(1-p)^n,
   \]

   respectively.
6. A forward conditional channel does not identify reverse production without
   a reservoir density of states, degeneracies and a time-reversal measure.
7. Exposure times, marked event counts, post-miss transition counts, reverse
   counts and an independently prepared initial ensemble give a concrete
   measurement program for the missing tuple.

## Claims not adopted

### 1. The GKM renewal limit is not Poisson

Response 0012's Theorem 2 uses \(T=-\nu I\), hence an exponential encounter
clock, and calls this an exact reproduction of Greene--Kabat--Marnerides.
The cited algorithm instead estimates

\[
t_r\simeq r/\bar v
\]

and redraws the impact parameter at each scheduled recollision.  The
exponential model is a new renewal closure, not the exact GKM source limit.

### 2. A target-neutral physical kernel has not been supplied

Omitting a field named `rank` and imposing \(S_9\) covariance are necessary
but not sufficient non-encoding evidence: an invariant constitutive table can
still depend on the number of directions in a later response interval.  The
free \(T,K,R,\Omega_R,\mu_0\) require a pre-classifier derivation or registered
measurement, not only a symmetric schema.

The displayed microcanonical \(\mu_0\) is also not yet a normalized fixed
measure.  Its equality constraints need a declared surface/reference measure,
variable-particle-number factors and a proof that the normalizer is finite.

### 3. The finite executable and response replay remain architecture

No actual \(q_{\rm dg},q_{\rm rel},q_{\rm enc}\) tables, absolute rate bounds,
finite grid, event reset table, pair-history creation/deletion rules,
quantized work values or finite-horizon error are given.  The post-miss kernel
\(R\) is not explicitly inserted into the finite generator.

On the response side, `B=C=I_2` does not specify embeddings into the augmented
space, cross-direction product maps are absent and no pole, residue,
relation, observability or survival margin is actually evaluated.  Thus the
cells \(Z_m\) and mandatory controls are specified but not replayed.

### 4. Kernel nonidentification is not yet a rank-three margin flip

The response proves that several constitutive inputs are unidentified.  It
does not exhibit two fully source-compatible, target-neutral completed models
whose entrant rank-three margin has opposite sign.  A statistic can in
principle be constant along an unidentified parameter direction.  The safe
conclusion is that no rank-three strict-residence margin has yet been
certified from the supplied sources, not that such a margin has been globally
excluded.

### 5. Several measure-level details remain open

The encounter flux needs one consistent vector/kernel type; continuous-mark
detailed balance needs a reference measure and time-reversal Jacobian; clock
rescaling must remain inside a frozen-geometry cell; and a history-contraction
bound belongs to the full encounter--mark--channel--reset kernel, not
automatically to the bare reset table.

## Canonical status after 0012

- `encounter_factorization = adopted`
- `absolute_clock_mark_channel_separation = adopted`
- `finite_first_entry_and_entrant_residence_formulas = adopted`
- `conditional_retention_and_worst_leakage = adopted`
- `source_factorization_identifiability_boundary = adopted`
- `marked_event_measurement_route = adopted`
- `poisson_clock_as_exact_GKM_limit = false`
- `populated_target_neutral_physical_kernel = false`
- `finite_executable_reduction = false`
- `complete_anonymous_response_replay = false`
- `rank_three_margin_identified_or_excluded = false`
- `genuine_3p1_selection = false`

## Next move

Instantiate one target-neutral event law.  The next round must contain actual
finite state/mark/channel/reset tables and a deterministic reproducer.  It
must either lift the scheduled GKM recollision rule faithfully to the full
anisotropic nine-torus, or derive a first-hit/return law from one explicit
pre-classifier microscopic flow.  Symbolic \(T,K,R\) placeholders are no
longer an acceptable delivery.
