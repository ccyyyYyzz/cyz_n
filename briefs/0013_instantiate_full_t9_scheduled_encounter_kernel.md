# Brief 0013 — instantiate one full-T9 scheduled encounter kernel

Status: active

Baseline commit: `0e4563149b65a6837347cd9778066120ab016f22`.

## Role

Act as the originating mathematical physicist and computational co-theorist.
Do not review Response 0012 and do not write another symbolic interface.  The
source-factorization boundary is settled.  Instantiate one kernel that can be
executed before a response rank exists.

Read, in order:

1. `state/PROJECT_STATE.md`;
2. `responses/0012_target_neutral_encounter_recollision_kernel.md`;
3. `decisions/0012_adopt_source_factorization_boundary_not_physical_kernel.md`;
4. this brief.

The project remains one closed loop.  This is an internal theorem gate, not a
paper split or a journal exercise.

## Correction that must be carried forward

Greene--Kabat--Marnerides 2009 does not use an iid exponential encounter
clock.  In its dilute regime it estimates

\[
t_r\simeq r/\bar v
\]

and redraws an impact parameter at each scheduled recollision.  Therefore
Response 0012's exponential phase-type model is a proposed Poisson renewal
closure, not the exact GKM limit.

The next object should be a finite Markov-renewal or event-scheduled process.
Do not replace a deterministic/state-dependent scheduled time by a CTMC
exponential merely to reuse matrix exponentials.

## Preferred construction

Build one target-neutral lift of the scheduled GKM dilute-string closure to a
rectangular anisotropic nine-torus.  It must operate on the full metric and on
anonymous primitive winding cycles.  It may not first choose a number `d` of
large directions.

For every eligible opposite-charge F1 pair, the state should contain enough
pre-classifier data to determine:

1. the next scheduled encounter or return time in physical units;
2. the full compact impact/orientation/velocity mark at that time;
3. the GKM or JJP conditional channel on its valid source stratum;
4. the post-miss return state and correlations;
5. a paired reverse event and exact finite reservoir ledger.

The anisotropic lift beyond a published source may be a newly proposed,
independently measurable closure.  Label it that way.  A source-limit theorem
must show how the one common full-metric rule reduces on every declared
isotropic GKM stratum; do not regenerate a different law after the stratum's
number of large radii is counted.

If a deterministic microscopic first-hit/return flow on the compact torus is
strictly more defensible than the scheduled-redraw closure, you may use it
instead, but it must satisfy every executable and non-encoding requirement
below and must compare explicitly with the scheduled GKM algorithm.

## Required finite artifacts

This round is not complete unless `main` contains all three:

1. `responses/0013_instantiate_full_t9_scheduled_encounter_kernel.md`;
2. a deterministic standard-Python reproducer under `artifacts/0013/`;
3. one machine-readable kernel/ledger artifact under `artifacts/0013/`.

Use exact integers/rationals wherever possible and outward rational intervals
for transcendental source amplitudes.  The response must state the exact
commands used, the artifact hashes and whether they were actually executed.
Do not report a test as passed unless it was run.  Keep the finite instance
small enough to replay exhaustively.

The artifact must serialize, rather than leave symbolic:

- every finite microscopic/history/reservoir state;
- the normalized fixed initial law;
- every scheduled-time or first-hit rule and its absolute unit;
- every mark and its time-reversal partner;
- every conditional channel and reset destination;
- every forward/reverse energy and charge quantum;
- cemetery transitions and source-validity exits;
- the eight adjacent S9 actions or an exact generator from which they are
  expanded;
- all approximation and unresolved-boundary entries.

Do not submit placeholders named `T`, `K`, `R`, `Omega` or `mu` without their
actual finite entries.

## Non-encoding witness

Permutation covariance by itself is insufficient because an invariant table
can encode "exactly three".  Supply a stronger witness:

1. the kernel generator consumes only a frozen whitelist of microscopic
   fields: charge/species, the full compact metric, dilaton/warp cell,
   relative position/tangent/velocity, world-sheet cell, encounter history and
   reservoir state;
2. the dependency graph from those inputs to scheduled time, mark, channel and
   reset is serialized before any response classifier is called;
3. no function receives a response cell, visible count, active mask, target
   rank, pole band or later threshold;
4. one generated kernel is reused without alteration for all later output
   ranks;
5. construct at least one adversarial S9-invariant hidden-three table and show
   that the registration/dependency gate rejects it even though group
   equivariance passes.

A token scan alone is not this witness.  If the non-encoding property depends
on a declared measurement protocol, give the registration and train/validation
split that makes it falsifiable.

## Exact event and ledger semantics

The finite process must distinguish:

- scheduled encounters from accepted reactions;
- self/miss events from physical state-changing events;
- history-only updates from winding/geometry cell exits;
- forward and reverse marks under an explicit involution;
- system energy from reservoir energy in one global charge basis.

A null or unresolved event may not become an off-diagonal physical generator
jump by accident.  A non-null channel may not evade its reverse atom through a
caller-controlled boolean.  If the model is semi-Markov rather than a CTMC,
give the exact augmented-age/event-schedule evolution and do not export its
matrix as a CTMC row generator.

## Source calibration

Use primary sources only within their stated regimes:

1. [GKM 2009](https://arxiv.org/abs/0908.0955) for the dilute scheduled
   recollision/impact algorithm and impact-space amplitude;
2. [JJP](https://arxiv.org/abs/hep-th/0405229) only for
   crossing-conditioned channels and compact overlap;
3. [DFM](https://arxiv.org/abs/hep-th/0409162) only for its declared compact
   rate strata;
4. [EGJK](https://arxiv.org/abs/hep-th/0409121) for the anisotropic
   winding--geometry source and as an initial-measure caveat;
5. [Frey et al.](https://arxiv.org/abs/2310.11494) only where its
   near-Hagedorn/random-walk forward--reverse rate derivation applies.

Give numerical or exact registry cases.  A citation string is not an
authenticated rate entry.  Outside every source-valid case, go to a declared
cemetery or retain an explicitly measured/proposed closure label.

## Mandatory replays and controls

The reproducer must run at least these controls.

1. **Normalization and ledger replay:** every conditional law sums exactly to
   one; every noncemetery event closes energy and charges; reverse maps are
   involutions and every positive non-null atom has its declared reverse atom.
2. **Scheduled-clock replay:** recover the registered
   \(t_r\simeq r/\bar v\) event schedule in the GKM calibration case.  A
   Poisson waiting-time histogram is a failure, not a match.
3. **Full-T9 covariance:** all event and history tables commute with the eight
   adjacent direction swaps; the state-space action is nontrivial.
4. **Same-law source limits:** restrict the same generated law to at least two
   different isotropic large-radius strata, including the three- and
   four-large-radius controls, without passing their counts into the kernel
   constructor.
5. **History control:** compare scheduled independent impact redraw with one
   persistent-history alternative while preserving the one-mark marginal;
   report a finite-horizon survival/return statistic that changes.
6. **Clock control:** alter the physical separation or velocity input and show
   that absolute scheduled times change while conditional channel values at a
   fixed mark do not.
7. **Hidden-three adversary:** the S9-equivariant but classifier-dependent
   table is rejected before export.
8. **Serialization replay:** reload the machine-readable artifact, recompute
   every certificate and obtain the same hashes without consulting the
   response prose.

## Interface to the later all-rank gate

Export only pre-classifier trajectories or an exact semi-Markov transition
object plus the fixed initial law.  Do not manufacture response cells in this
round.  State precisely how a later anonymous response reconstruction will
consume the same artifact for ranks zero through nine.

Entrant strict residence for a semi-Markov model must be computed on its exact
age-augmented process or by an exact event-schedule formula.  Do not silently
feed a nonexponential process into CTMC killed-semigroup formulas.

## Required theorem boundary

End with the strongest one actually achieved:

1. an explicitly populated, target-neutral finite measurable closure with a
   faithful scheduled-GKM source limit and replayable non-encoding/ledger
   certificates;
2. an explicitly populated first-hit/return alternative with a quantitative
   comparison to GKM and the same certificates;
3. a sharp obstruction to both constructions, identifying one specific
   microscopic quantity that cannot be calculated or registered and one
   concrete measurement that supplies it.

Option 3 is not satisfied by repeating that `T,K,R,Omega,mu` are unknown.  It
must isolate a smaller object than Response 0012 did.  Do not claim rank-three
selection or exclusion in this round.

## Required delivery

Write the response and both finite artifacts directly to `main`, commit and
push.  Do not open a pull request, offer a download, leave code only in chat or
stop at an architecture.
