---
brief: 0013
response_commit: becc395613d73505724f4d8b6c993893078921fb
status: conditionally_adopted_as_scheduled_clock_and_registry_scaffold
supersedes: none
---

# Decision 0013 — keep the scheduled scaffold, reject the claimed complete kernel

## Verdict

Response 0013 makes real progress beyond the symbolic factorization boundary:
it supplies a deterministic non-Poisson schedule, exact rational finite mark
registries, an exchangeable proposed initial law, a reproducible canonical
payload and a proposed countdown interface.  Those pieces are adopted as a
finite scheduled-closure scaffold.

The response is not adopted as Brief 0013 outcome 1.  Its serialized states
and marks are not connected to a complete state-to-state event kernel.  The
replayer certifies selected summaries and hard-coded identities rather than
the transition object asserted in the prose.  Consequently exact full-process
`S9` covariance, reverse atoms, ledger closure, cemetery routing and semantic
non-encoding have not been established.

This decision does not evaluate any visible response rank and does not weaken
the existing prohibition on a rank-three claim.

## Independently replayed facts that are adopted

1. The standard-Python generator is deterministic.  Two independent runs
   with the declared `.json.xz.b64` suffix produced identical bytes:

   ```text
   encoded artifact SHA-256
   834215c9f241c4f1a3d796e5a012855fbe7156714dad55286649c107baf68cd5

   canonical payload SHA-256
   62a5d667fa0aa31e15bfdd64760457e3cb89ea033c5470b50e98b0825d137722
   ```

2. The declared clock is deterministic, not exponential.  The registered
   calibration gives `hold_time = 2`, while the separation and velocity
   controls give `3` and `4` exactly.
3. The rational outward enclosure of the selected `exp(-1/4)` shell factor is
   valid.
4. The 504 ordered frame enumeration, its frame-level adjacent `S9` maps and
   Coxeter relations are correct.
5. The 6,552 serialized mark IDs have a valid ID-level reverse involution.
6. The proposed event-epoch initial weights are strictly positive, normalized
   and frame-exchangeable.
7. The finite iid-versus-persistent history survival calculation is correct
   as a control calculation.
8. The response correctly refrains from claiming rank-three selection or
   exclusion.

These are exact statements about registered finite ingredients.  They do not
by themselves define a complete stochastic process.

## Claims not adopted

### 1. The event kernel covers only one frame template

The artifact lists 504 frames, 6,552 marks and 21,168 event states, but
`event_kernel` is generated once from `frames[0] = f012`.  Its 13 rows use the
absolute templates

```text
central, axis_3_plus/minus, ..., axis_8_plus/minus.
```

Only 6 of the 504 frames have that same normal-axis template set.  Of the
19,656 absent states, 6,048 have no corresponding reverse row.  For example,

```text
f013:A:none:axis_2_plus
```

is a serialized products state whose forward mark is valid for `f013`, but no
`axis_2_plus` reverse row exists.  Conversely, the generic table refers to
`axis_3_plus/minus` even though axis 3 belongs to frame `f013` and is not one
of its normal impact axes.

There is therefore no populated row for every serialized source state, no
closed destination-ID table and no proof that every positive forward atom has
a reverse atom.

### 2. The `S9` certificate is only a frame-map certificate

The verifier checks that each adjacent swap maps one ordered frame to the
correct ordered frame and that the action is nontrivial.  It does not check
the action on states, marks, schedules, channels, histories, resets, cemetery
states or event atoms.  The missing `f013:axis_2_plus` row is already an
explicit failure of the claimed event-table covariance.

Frame-level Coxeter relations are retained; exact covariance of the complete
process is false as a certified claim.

### 3. Reverse, ledger, age and cemetery tests do not read the claimed rows

The energy test evaluates the constants

```text
(2 + 0) == (0 + 2)
(0 + 2) == (2 + 0)
```

rather than traversing event atoms.  The cemetery and age augmentation are
metadata, not populated transition rows.  Independent mutations of each of
the following left all 15 reported tests green:

- an annihilation destination energy changed to `999`;
- a destination mark changed to a nonexistent ID;
- a mark impact axis or `b2` changed arbitrarily;
- one schedule row removed;
- the age rule changed;
- the state/mark action replaced by meaningless text;
- all cemetery states and rules removed;
- a source-limit metric changed without regenerating its summary.

The displayed ratio `p_ann = 4 p_create` is also not a detailed-balance replay
of the complete marked transition flux.  With the serialized initial weights,
one audited present/absent pair has one-step flux ratio 6, not 1.  A different
reference measure may be proposed, but it must be serialized and checked on
the actual marked atoms.

### 4. The dependency gate rejects only the prepared adversary

`register_graph` checks a short list of field and operation strings.  It does
not require every input to be a whitelisted leaf or an earlier node, inspect
lookup-table contents, interpret rule semantics or bind the declared graph to
the code that produced the kernel.  For example, the accepted operation

```text
fraction_arithmetic(metric_radii)
```

can carry the rule `special value iff exactly three radii exceed the
boundary`, and the gate accepts it.  Alias counts and a hidden-three source
lookup are accepted as well.  Adding such a node to the artifact leaves every
reported test green.

The absence of an explicit field named `rank` is adopted only as a syntactic
observation, not as a semantic non-encoding theorem.

### 5. The three/four controls are summaries, not two full-kernel replays

The main builder has no metric argument and fixes all nine radii to two.
`source_case()` separately emits valid-frame and mark-count summaries for the
three- and four-large inputs.  It does not instantiate their complete state,
event, reverse, ledger, cemetery and age kernels.  The reported combinatorial
counts are correct, but same-law full-kernel reuse has not been executed.

### 6. The GKM source-limit language is too strong

The scheduled form `t_r approximately r/vbar` and the redraw at scheduled
returns are source-grounded.  The sparse central-plus-axis mark law,
`p0 = 1/4`, `Delta^2 = 1`, `r = R_v/2`, reservoir degeneracies and initial law
are proposed closure choices.  The artifact itself leaves continuum impact
cubature unresolved and has no executable source-validity exits.  The safe
description is a GKM-clock-inspired proposed sparse closure, not a faithful
full GKM source limit.

### 7. Raw file hashes are not checkout-stable

On the current Windows checkout, the documented verify command exits with
status 1 because CRLF conversion changes the raw script and ASCII-armored
artifact hashes.  The decoded canonical payload is unchanged.  Future replay
must fix LF in repository attributes or compare explicitly normalized source
and canonical decoded payload hashes.

## Canonical status after 0013

- `scheduled_nonpoisson_clock_scaffold = adopted`
- `exact_rational_sparse_mark_registry = adopted_as_proposed_closure`
- `frame_level_S9_action = adopted`
- `deterministic_canonical_serialization = adopted`
- `complete_state_to_state_event_kernel = false`
- `complete_reverse_atom_ledger = false`
- `full_process_S9_covariance = false`
- `executable_cemetery_routing = false`
- `semantic_nonencoding_certificate = false`
- `same_law_d3_d4_full_kernel = false`
- `faithful_GKM_full_source_limit = false`
- `rank_three_margin_identified_or_excluded = false`
- `genuine_3p1_selection = false`

## Next move

Close the table rather than enlarge the prose.  The next artifact must emit a
source-state row and explicit destination IDs for every positive event atom,
then validate the reloaded artifact with an independent hostile verifier.  A
certificate that survives changes to energy, reverse IDs, source-validity
routing or hidden-three dependencies is evidence that the certificate is not
checking the claimed object.

