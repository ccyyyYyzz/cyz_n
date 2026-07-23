---
brief: 0015
source: browser-hosted GPT package, repaired and independently audited locally
captured: 2026-07-23
base_remote_commit: 251718c59daaa8a205015cade8a68b24b3dcd7c8
status: locally_verified_fixed_registered_certificate
artifacts:
  - artifacts/0015/constructor_spec.json
  - artifacts/0015/control_vector_manifest.json
  - artifacts/0015/generate_0015.py
  - artifacts/0015/generator_core.py
  - artifacts/0015/generator_model.py
  - artifacts/0015/generator_artifact.py
  - artifacts/0015/verify_0015.py
  - artifacts/0015/verifier_core.py
  - artifacts/0015/verifier_model.py
  - artifacts/0015/verifier_semantics.py
  - artifacts/0015/verifier_replay.py
  - artifacts/0015/verifier_replay_runtime.py
  - artifacts/0015/verifier_hostile.py
  - artifacts/0015/scheduled_kernel.json
  - artifacts/0015/baseline_report.json
  - artifacts/0015/portability_report.json
  - artifacts/0015/hostile_observations.json
  - artifacts/0015/verification_report.json
---

# Response 0015 — fixed registered scheduled-kernel certificate

## Executive result

Brief 0015 now has a readable, replayable software certificate for one exact
finite scheduled-kernel construction. The repair does not claim to have built
a general interpreter for the natural-language rules or the serialized
`constructor_program`. Instead, one canonical specification digest selects
two source-separated fixed implementations. Any content change to that
specification is outside the theorem domain and is rejected before expansion.

The verifier imports no generator module. Through its source-separated fixed
implementation it reconstructs every registered control, checks the finite-
process invariants, reruns the external generator, performs real opaque-ID
renaming through the single-instance CLI, executes live `S9` covariance
workers, and runs the hostile suite in fresh subprocesses.

The strongest closed statement is:

> **Fixed-registration replay theorem.** Let \(S_*\) be the canonical
> constructor document with SHA-256
> `5a935b5e0cc415d73a783cb6e6d926a355f2c43d662fa94aed93e0a8f9a5af01`
> and semantic-contract digest
> `38bb37210c33ae56944688607891b3fb99b89e4af48a159f419f9d96beb8c282`,
> and let \(M_*\) be the canonical control manifest with SHA-256
> `14d9162a69137e85369bca24081f07e48df10b33f1bac83c45d9122e629b86bd`.
> The source-hash-bound generator and source-separated verifier accept only
> \((S_*,M_*)\) and reject modified documents before expansion. For the
> eleven registered controls they construct equal canonical expanded
> SHA-256 digests and exact counts. Subject to SHA-256 collision resistance,
> the verifier reconstruction is thereby bound to the generator expansion.
> The verifier checks exact row normalization, projection-preserving
> absorbing killed lifts, endpoint/mark/channel/ledger involution for
> positive accepted non-null atoms, deterministic finite-countdown schedule
> records, and the registered initial law. For five registered controls it
> additionally checks frames, candidate marks and source cases, marks, states
> including killed lifts, schedules, events and the initial law under each of
> the eight adjacent transpositions \(s_0,\ldots,s_7\).

This theorem is conditional on the registered microscopic inputs and closure
choices. It is not a theorem about an arbitrary constructor DSL, not a
fundamental non-encoding theorem, not a derivation of frame arity three, and
not a proof that the observed world is \(3+1\)-dimensional or Lorentzian.

## Registered identity

The three content identities that define the fixed document domain are:

```text
constructor specification
5a935b5e0cc415d73a783cb6e6d926a355f2c43d662fa94aed93e0a8f9a5af01

semantic-contract projection
38bb37210c33ae56944688607891b3fb99b89e4af48a159f419f9d96beb8c282

control manifest
14d9162a69137e85369bca24081f07e48df10b33f1bac83c45d9122e629b86bd
```

Canonical JSON ignores key ordering and insignificant whitespace. The source
inventory uses normalized LF bytes, so LF/CRLF checkout differences do not
change the registered identity. A semantic JSON change, source change other
than line endings, manifest change, extra executable helper or shadowed import
defines a different release and is not certified by this report.

## What is actually registered

`constructor_spec.json` fixes:

- the nine anonymous directions and ordered frame roles;
- arity bounds and the explicit `frame_arity` input;
- the exact microscopic input field set and forbidden response-derived fields;
- source-validity precedence and interval closure;
- frame-local candidate marks and exact rational probability tables;
- state, killed-state, schedule, event, ID and ordering records;
- destination, history, reverse, energy, work and charge ledgers;
- deterministic finite-countdown schedule records and the initial law;
- the eight adjacent `S9` generators; and
- the exact eleven executable Python dependencies.

These fields are registration data for the fixed implementations. Some are
human-auditable descriptions rather than executable syntax. The certificate
therefore does not infer that a modified but well-typed specification would
be interpreted. It rejects every modified specification at the registered
digest boundary.

The generator and verifier are source-separated but intentionally implement
closely corresponding algorithms. Their agreement is differential replay, not
an independent derivation of the constitutive laws. Common-mode algorithmic
errors remain possible; closed record schemas, explicit invariants, source
binding and hostile tests reduce that risk but do not turn the two programs
into independent physical arguments.

The sharp remaining software obstruction to a general-specification theorem
is a typed executable semantics and two genuinely independent dispatchers for
`constructor_program`, `operation_schemas`, `constitutive_rules` and
`parameter_influence`. In the present certificate these objects are
full-digest-bound and structurally audited metadata; they do not drive a
general dispatcher.

## Closed execution boundary

The generator and verifier separately enforce:

1. exact full-specification, semantic-projection and manifest digests;
2. strict JSON input types, canonical rational strings and range conditions;
3. exactly eleven controls with unique opaque IDs, fixed report roles and
   exact obligations;
4. exactly eleven executable `.py` files, canonical POSIX-relative paths and
   no additional helper in `artifacts/0015`;
5. normalized-LF hashes for all executable files;
6. equality between the repository root and the root containing the executing
   launcher;
7. equality between every loaded module's real `__file__` and its registered
   path; and
8. complete dependency inventory in both suite and single-instance artifacts.

The semantic constructor receives only the fixed specification and the full
microscopic input vector. Opaque IDs are attached to the envelope after the
semantic record is built. Report metadata is used only by the evidence layer.

The old `must_consume` and `consumed_spec_paths_sha256` fields were removed.
They were hashes of declared path names, not runtime access traces, and could
not support a consumption claim.

## Finite controls

The compact artifact contains eleven controls:

| opaque id | fixed report role | arity | frames | valid | states | marks | atoms | positive accepted non-null |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `u0` | ordinary full T9 | 3 | 504 | 504 | 21,172 | 6,556 | 78,628 | 39,312 |
| `u1` | three-large metric control | 3 | 504 | 6 | 3,028 | 10 | 3,064 | 36 |
| `u2` | four-large metric control | 3 | 504 | 24 | 3,172 | 76 | 3,748 | 432 |
| `u3` | velocity invalid | 3 | 504 | 0 | 3,028 | 4 | 3,028 | 0 |
| `u4` | coupling/dilution invalid | 3 | 504 | 0 | 3,028 | 4 | 3,028 | 0 |
| `u5` | geometry invalid | 3 | 504 | 0 | 3,028 | 4 | 3,028 | 0 |
| `u6` | unresolved amplitude | 3 | 504 | 0 | 3,028 | 4 | 3,028 | 0 |
| `u7` | arity-two semantic control | 2 | 72 | 2 | 436 | 6 | 448 | 12 |
| `u8` | arity-four semantic control | 4 | 3,024 | 24 | 18,148 | 28 | 18,292 | 144 |
| `u9` | closed lower speed boundary | 3 | 504 | 504 | 21,172 | 6,556 | 78,628 | 39,312 |
| `u10` | precedence probe | 3 | 504 | 0 | 3,028 | 4 | 3,028 | 0 |

The arity-two and arity-four controls show that the registered code consumes
the declared arity rather than always expanding triples. They do not explain
why the physical microscopic closure should have arity three.

## Live evidence

The final report executes its evidence during the current invocation. It does
not accept baseline, portability, hostile-observation or `S9` files as proof
inputs.

The baseline:

- reconstructs all eleven controls through the source-separated verifier;
- compares expanded hashes, counts and calibration times;
- externally regenerates the complete artifact;
- runs the generator twice on the same full input under the source and
  renamed opaque IDs, has the source-separated verifier check both single
  artifacts, removes only the envelope ID and compares every remaining field;
- binds all loaded verifier modules to registered paths; and
- compiles all eleven executable files and checks both CLIs.

For five registered roles, the verifier-side reconstruction is checked under
each of the eight adjacent transpositions. The comparison covers frames,
candidate marks and source cases, registered marks, physical and killed
states, schedules, events and the initial law. It does not claim an explicit
enumeration of all \(9!\) group elements. The five roles are:

```text
ordinary_full_t9
three_large_metric_control
four_large_metric_control
arity_two_semantic_control
arity_four_semantic_control
```

The portability layer copies the registered tree, converts all Python files
and JSON documents to CRLF/pretty form, regenerates the artifact and repeats
semantic replay. The canonical artifact and normalized source hashes remain
unchanged.

The hostile layer contains 94 named mutations covering model rows, schedules,
IDs, destinations, ledgers, killed lifts, arity, specification rebinding,
manifest deletion, input type/range errors, dependency paths and hashes,
shadowed imports, extra helpers, source-level hard-coded triples, a real
opaque-label branch and the single-artifact schema. Each negative test must:

```text
run in a fresh child process
exit exactly 2
emit status ERROR
emit a VerificationError code in its local expected set
```

Exit 1, exit 3, timeout, malformed output or a wrong error code is an
infrastructure/test failure and cannot count as a rejected mutation.

Report publication is generation-safe. At the beginning of a report run, the
four output files become `IN_PROGRESS` sentinels marked
`not_a_certificate`; this phase-zero invalidation occurs before verifier-module
imports and the root, dependency, generator, document or artifact checks. The
three evidence components remain permanently marked `not_a_certificate` and
carry a component role plus the generation digest. They are accepted only when
their canonical hashes are committed by the matching-generation PASS main
report. Only after every live check succeeds, and pre- and post-commit checks
confirm that the artifact, documents and executable-source inventory did not
change during publication, is the PASS main report retained.

The frozen full run on 2026-07-23 produced the following canonical JSON
identities:

```text
artifact payload
ecb34edb6945e499969e76f3a34ae9ec6043fc3c3079c1e5c431fb3155dba0ee

certificate generation
5edd23096cd2030cad8dc4be4aff806d792c7646ca9a8a49d7999e35e6cf6cf7

verification report
82435a4aab83e44ad5552d76ccd962501aa24de7d2fc41479bdcdb74a0dfda29
```

The reverse audit found all eleven artifact source hashes equal to the current
normalized-LF files, all 94 mutation names present once in declared order, all
109 child rejection records at exact exit 2 with structured `ERROR`, and the
five role-selected covariance records carrying exactly \(s_0,\ldots,s_7\).

## Reproduction

From the repository root:

```text
python -I artifacts/0015/generate_0015.py
python -I artifacts/0015/verify_0015.py --baseline
python -I artifacts/0015/verify_0015.py --portability
python -I artifacts/0015/verify_0015.py \
  --report artifacts/0015/verification_report.json
python -I artifacts/0015/verify_0015.py \
  --check-report artifacts/0015/verification_report.json
```

The `--report` command reruns baseline, all live covariance controls,
portability and all 94 hostile mutations. It is intentionally slower than the
final `--check-report` command. Under a trusted-repository/filesystem
assumption, that command recomputes the current generation identity and checks
that all component hashes and generation bindings still match. It is a
freshness and internal-consistency check, not proof that the stored execution
record is authentic and not a substitute for rerunning `--report`.
Certificate publication supports only the direct isolated CLI shown above;
programmatic `import verify_0015; main(...)` is not part of the certificate
entry surface.

## Scientific boundary and next gate

This closes the exact-registration and replay layer for the registered finite
scheduled scaffold. It leaves both the general-interpreter semantic gate and
the physical-closure gate open, and establishes neither physical completeness
nor selection.

Still unproved are:

```text
derivation of the arity-three microscopic role closure
source-grounded sparse impact preparation
return separation and speed law
post-miss history dynamics
reverse-reservoir state counting or detailed balance
physical preparation of the proposed initial law
connection to anonymous response reconstruction
stable rank-three / 3+1 basin selection
Lorentzian signature
loss-of-plateau prediction
full residual-age trajectory replay
```

The next work should therefore leave the certificate code frozen and attack
the physical closure: derive or independently constrain the microscopic
arity, mark, clock, history, reverse and preparation laws, then connect the
resulting scheduled process to the anonymous response-reconstruction layer.
