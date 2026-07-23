# Brief 0014 — close the framewise scheduled kernel and make the verifier hostile

Status: active

Baseline response commit: `becc395613d73505724f4d8b6c993893078921fb`.

## Role

Act as the originating mathematical physicist and computational co-theorist.
Do not defend Response 0013 and do not replace its large table by another
architectural description.  Preserve the valid scheduled-clock and rational
registry pieces, then construct the finite stochastic object that Response
0013 claimed but did not serialize.

Read, in order:

1. `state/PROJECT_STATE.md`;
2. `responses/0013_instantiate_full_t9_scheduled_encounter_kernel.md`;
3. `decisions/0013_adopt_scheduled_scaffold_reject_incomplete_kernel.md`;
4. this brief.

The project remains one closed loop.  This round still precedes response-rank
classification and may not claim selection of three.

## The exact defect to repair

Response 0013 serialized frame-local marks and states for all 504 frames but
generated event rows only from the absolute normal-axis templates of `f012`.
This leaves 6,048 products states without a reverse row and prevents a
complete `S9` action on event atoms.  Its verifier then checks frame maps and
hard-coded energy identities rather than traversing the missing kernel.

The next result is not complete until the event object is closed on its
serialized state IDs and a verifier that did not generate the object can
detect every required hostile mutation.

## Required delivery

Commit all of the following under new `0014` paths:

1. `responses/0014_close_framewise_kernel_with_hostile_verifier.md`;
2. a deterministic standard-Python generator under `artifacts/0014/`;
3. a separate standard-Python verifier under `artifacts/0014/` that imports no
   code from the generator;
4. one machine-readable compact kernel/ledger artifact under
   `artifacts/0014/`;
5. one machine-readable verification and mutation report under
   `artifacts/0014/`.

The generator and verifier may share only the serialized schema, not helper
functions or expected booleans.  Execute both.  State the commands, exit codes,
canonical hashes and hostile-test outcomes.  Keep the expanded object small
enough for exhaustive replay; a compact rule is acceptable only if the
independent verifier expands it exactly and checks closure.

Do not create or leave a `contents: write` GitHub Actions workflow as a file
transport mechanism.  Deliver repository files, not a download-only bundle.

## Mandatory event-atom schema

After exact expansion, every positive atom must have at least:

```text
event_id
source_state_id
scheduled_hold_time and physical_time_unit
mark_id
channel_id and channel_kind
accepted
probability
destination_state_id
reverse_event_id or an explicit cemetery exemption
delta_system_energy
delta_reservoir_energy
delta_global_charge_vector
physical_projection_changed
history_changed
source_registry_case or proposed_closure_label
```

For every serialized noncemetery source state, the atom probabilities must be
nonnegative and sum exactly to one.  Every destination must exist.  Every
state must have exactly one applicable schedule row.  Null or unresolved
atoms may update history but may not change the physical projection.

An accepted non-null atom may not evade its reverse through a boolean.  Its
reverse must have swapped source/destination, the declared time-reversed mark
and compatible channel kind.  Energy plus reservoir/work and every global
charge coordinate must close from the actual atom fields.

## Frame-local closure

Generate marks and rows from each state's actual frame.  An event for `f013`
must use the normal axes of `f013`, including `axis_2_plus/minus` and excluding
axes already in that frame.  The verifier must report:

- number of states with a stochastic row;
- number with a unique schedule;
- number of positive non-null atoms;
- number with a valid reverse;
- number of dangling mark or destination IDs;
- minimum and maximum row sums;
- exact coverage by state class.

All uncovered counts must be zero where closure requires zero.

## Exact age evolution

Serialize the initial countdown phase and either:

1. expand the residual-time transition object exactly; or
2. serialize a finite rule whose full expansion is independently replayed.

The verifier must generate a trajectory from the artifact and recover event
times `2,4,6,8,10` in the calibration.  Changing one hold time or replacing
the countdown rule with a Poisson/exponential tag must fail.  Do not export a
CTMC row generator.

## Full-process `S9` certificate

Expand all eight adjacent actions on states, marks, cemetery states and event
atoms.  Verify:

1. bijection and involution;
2. the nonadjacent commuting and adjacent braid Coxeter relations;
3. nontrivial state action;
4. covariance of schedules, probabilities, channels, histories, destinations,
   reverse IDs and ledger vectors;
5. invariance of the fixed initial law.

Checking only a frame-index map is a failure.

## Executable source-validity and cemetery routing

Include cemetery states in the finite state space.  Give executable validity
predicates for every source-derived registry case and explicit transition rows
for invalid or unresolved inputs.  At minimum run one valid case and separate
velocity, coupling/dilution, geometry and unresolved-amplitude exits.  Each
cemetery state must be absorbing.  Removing its states or routing rules must
make verification fail.

The anisotropic sparse mark law, reservoir degeneracies and initial law remain
new proposed measurable closures unless independently derived.  Either supply
a normalized discretization of the GKM continuous impact law with a rigorous
cubature error, or use the narrower phrase

```text
GKM-scheduled, proposed sparse impact closure
```

and do not claim a faithful full source limit.

## Non-encoding program, not token scan

Use a finite registered dependency DSL that actually generates schedule,
mark, channel and reset rows.  Every node input must be either an exact frozen
microscopic whitelist leaf or the ID of a preceding node.  Every operation
must have a closed parameter schema.  Lookup tables are part of the registered
program and must be scanned structurally.  Free-form rules, unregistered
globals, environment reads, file reads and closure variables are forbidden.

Hash the registered program and record that same hash in every generated
kernel instance.  The verifier must reject, not merely label, all of:

1. explicit `count_if == 3`;
2. `fraction_arithmetic(metric_radii)` with a hidden exactly-three branch;
3. a count alias such as `number_above_boundary`;
4. a source lookup table with a special three-case;
5. an unregistered global or environment value;
6. a post-construction override keyed by response rank.

The ordinary kernel must be generated by this registered program.  A clean
declarative graph sitting beside unrelated Python code is insufficient.

## Same-law three/four replay

The constructor must accept the full nine-component metric and other allowed
microscopic inputs.  It may not accept or compute a response rank, visible
count, active mask or stratum selector.  Invoke that same registered program
on the three-large and four-large metrics and instantiate their complete
state, event, reverse, ledger, cemetery and age kernels.  Record the same
program hash and independently verify both.  A table containing only valid
frame counts and mark counts is not a full-kernel replay.

## Mandatory hostile mutations

Reload the machine artifact, apply each mutation independently, and require
the separate verifier to return nonzero with a localized reason:

1. change one row probability;
2. delete one state row or schedule row;
3. replace one mark or destination ID by a ghost ID;
4. change one reverse event ID;
5. change one system-energy or charge quantum;
6. turn one null/history atom into a physical occupation jump;
7. corrupt one state, mark or event `S9` image while leaving frame maps intact;
8. remove cemetery states or source-validity routing;
9. alter one age hold or replace the scheduled tag by Poisson;
10. inject each hidden-three program listed above.

The mutation report must be computed from verifier exit status and error
records.  Prewritten `expected_rejected: true`, `passed: true`, comparison of a
constant with itself or exceptions caused only by malformed JSON do not count.

## Cross-platform serialization

Use canonical decoded-payload hashes as the transport-independent identity.
Normalize script text to LF before hashing or add scoped repository attributes
that force LF.  Demonstrate that verification is not invalidated solely by a
CRLF checkout.  The verify command must regenerate the expected canonical
payload, not only reread and shallow-check the supplied one.

## Required theorem boundary

End with the strongest result actually achieved:

1. a complete framewise scheduled finite closure with independently replayed
   stochasticity, age evolution, reverse/ledger, cemetery, `S9`, same-law and
   semantic non-encoding certificates; or
2. a sharp obstruction naming the smallest field or transition needed to
   close one of those properties and one concrete measurement/derivation that
   supplies it.

Do not call a state/mark registry a kernel.  Do not claim rank-three selection
or exclusion.

