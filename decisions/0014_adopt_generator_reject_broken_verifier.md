---
brief: 0014
response_commit: d23e68de88f27a6896feb6631ea0293a5cdf90f3
status: conditionally_adopted_as_generator_level_scheduled_kernel
supersedes: none
---

# Decision 0014 — adopt the generator-level kernel; reject the broken verifier certificate

## Verdict

Response 0014 repairs the main combinatorial defect in Response 0013.  Its
generator now expands each source state's actual frame, supplies one exact
stochastic row and schedule per state, closes every positive non-null atom
against an explicit reverse atom, and produces complete three- and four-large
control kernels through the same internal expansion path.

Those generator-level facts are independently replayed and conditionally
adopted as a proposed scheduled finite closure.  Brief 0014 outcome 1 is not
adopted.  The verifier committed at `d23e68d` cannot start, the compact
artifact contains hashes and rules rather than expanded rows, and the
registered dependency graph does not yet cover the entire constitutive
construction.  The hostile-mutation report is therefore a historical record,
not a replayable certificate for the committed tree.

No visible response rank is evaluated here.  Nothing in this decision
identifies, selects or excludes three dimensions.

## Generator-level facts independently replayed

Two clean temporary runs of

```text
python artifacts/0014/generate_0014.py
  --output <temporary-kernel>
  --verifier artifacts/0014/verify_0014.py
```

returned zero and produced the same canonical identities:

```text
LF file SHA-256       f899fe6d7ca03df843353c875421f56bb310c347f2d64ffcd4f8dc89f08b2be9
payload SHA-256       5f0bc6aff4857282fd290f25aac63c42a9db5b64fb67c9b0fdee9abd2f31dad0
program SHA-256       a979ba2d545b9333ac9178a0e786763f28f119f43f3ea57c8a344f3a06403f6c
```

Independent expansion, without trusting the report booleans, established:

1. full `T9`: 21,172 states, 6,556 marks including four cemetery marks,
   78,628 atoms and 39,312 positive non-null atoms;
2. three-large control: 1,534 states, 1,570 atoms and 36 positive non-null
   atoms;
3. four-large control: 1,732 states, 2,308 atoms and 432 positive non-null
   atoms;
4. every state has exactly one row and one schedule, and every row sums
   exactly to one;
5. `f013` uses its own normal axes, including `axis_2_plus/minus` and excluding
   axes 0, 1 and 3;
6. every positive non-null atom has a real reverse ID with swapped endpoints,
   reverse mark, compatible channel and opposite energy/charge ledger;
7. all eight adjacent `S9` actions are covariant on the full model's states,
   marks, schedules and atoms;
8. complete three/four controls are produced from their nine-component metric
   inputs without passing or computing a large-direction count; and
9. the deterministic calibration produces event times `2,4,6,8,10`.

The generator source contains no explicit response rank, visible-count or
`count_if == 3` branch.  This is adopted as a useful syntactic and
generator-path fact, not as the final semantic non-encoding theorem.

## Claims not adopted

### 1. The committed independent verifier does not execute

The declared baseline, CRLF and mutation commands all fail before argument
parsing:

```text
ValueError: base85 overflow in hunk starting at byte 19275
```

The same failure occurs on the pure-LF Git blobs, so it is not a Windows
checkout artifact.  `py_compile` succeeds only because it compiles the
915-byte launcher without decoding the verifier implementation.

The response lists shard hashes beginning `86f5e90b` and `c916efff`, while the
actual LF Git-content SHA-256 values begin `157b43cb` and `d78ed1a4`.  The
kernel and report bind the launcher hash but not the two executable source
shards.  Consequently a broken verifier can still leave the generator payload
hash unchanged.  The submitted mutation report describes substantive intended
checks, but none of them is currently replayable from the committed tree.

### 2. The compact artifact is not independently expandable as committed

`framewise_scheduled_kernel.json` serializes the dependency graph, instance
inputs, counts and expanded hashes.  It does not serialize the 21,172 state
rows and 78,628 atoms.  Brief 0014 explicitly allowed such compaction only
when a separately implemented verifier expands the same object exactly.
Because that verifier is unavailable, the current evidence reduces to the
generator checking its own expansion.

### 3. The registered program does not cover the whole constructor

The hash `a979...` covers schedule, validity, mark and destination nodes, but
important constitutive rules remain in unregistered Python or globals:

- the nine directions, three histories and cemetery cases;
- ordered frame enumeration and its fixed arity;
- state, schedule and atom schemas;
- multiplication of mark and channel probabilities;
- channel kinds, acceptance flags and reverse pairing;
- energy/charge ledgers;
- the initial law and countdown rule; and
- the predefined control-instance table.

A clean graph beside free construction code is not the complete dependency
closure required by Brief 0014.  The next artifact must serialize and hash the
entire constructor specification, while allowing the generator and verifier
to implement independent interpreters for that specification.

### 4. Semantic non-encoding remains conditional

The ordinary code is target-rank-free, but it fixes an ordered three-role
frame `(w,v,s)`.  Geometry validity requires all three frame radii to exceed
the boundary, so a first valid sector appears when three large directions are
available.  This may be a legitimate physical collision-role closure, but its
arity must be derived from the source model or declared as a proposed
microscopic prior.  It cannot silently serve as evidence that three visible
directions were dynamically selected.

The names `three_large_valid` and `four_large_valid` also enter state and event
IDs.  They do not alter the current transition law, but opaque instance IDs
are required before a semantic certificate is signed.

### 5. Cemetery routing changes physical payload while claiming otherwise

For every invalid present state, the generated atom changes

```text
pair_present -> cemetery
delta_system_energy = -2
delta_reservoir_energy = +2
physical_projection_changed = false
```

The destination projection and energies differ from the source, contradicting
the flag and making an epistemic source-validity exit look like an
annihilation.  A killed-state lift must preserve the source physical payload,
or the artifact must give and verify an explicit epistemic exemption.  The
former is preferred.

### 6. The reverse label is stronger than the implemented law

`proposed_microcanonical_reverse` currently means a proposed reverse
probability ratio of `1/4`.  Under the serialized uniform initial law it is not
a demonstrated detailed-balance or microcanonical relation.  It must be
renamed unless an explicit density-of-states measure and flux identity are
serialized and verified.

## Canonical status after 0014

- `frame_local_generator_expansion = adopted`
- `exact_stochastic_rows_and_schedules = adopted_at_generator_level`
- `complete_positive_reverse_id_closure = adopted_at_generator_level`
- `deterministic_countdown_clock = adopted_at_generator_level`
- `full_T9_S9_covariance = independently_replayed`
- `same_path_d3_d4_complete_expansions = independently_replayed`
- `target_rank_field_absent = true`
- `executable_independent_verifier = false`
- `replayable_hostile_mutation_certificate = false`
- `cross_platform_raw_file_identity = false`
- `full_constructor_dependency_hash = false`
- `semantic_nonencoding_certificate = false`
- `projection_preserving_cemetery = false`
- `microcanonical_reverse_law = false`
- `rank_three_margin_identified_or_excluded = false`
- `genuine_3p1_selection = false`

## Next move

Do not enlarge the physical model.  Repair the evidence chain and constructor
boundary: publish readable executable verifier code, bind every executable
dependency, serialize the complete constructor specification, repair cemetery
semantics, expose opaque arbitrary-metric inputs, and test the fixed frame
arity as an explicit microscopic prior.  Only then may the scheduled kernel be
connected to the local exact first-entry consumer.
