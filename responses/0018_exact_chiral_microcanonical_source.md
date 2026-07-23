---
brief: 0018
branch: brief-0018
status: source_and_event_record_contract_closed_physical_pushforward_open
captured: 2026-07-23
artifacts:
  - artifacts/0018/source_registry.json
  - artifacts/0018/microcanonical_source.py
  - artifacts/0018/source_report.json
  - artifacts/0018/stat_audit_registry.json
  - artifacts/0018/statistical_audit.py
  - artifacts/0018/stat_audit_report.json
  - artifacts/0018/event_record.schema.json
  - artifacts/0018/coverage_proof.py
  - artifacts/0018/event_contract.py
  - artifacts/0018/event_schema_controls.json
---

# Response 0018 — exact chiral microcanonical source and replayable event-record contract

## Verdict

```text
registered zero-level-matched finite-K source: closed
cross-platform source and statistical audit: closed
total disjoint rank-blind event-record contract: closed
physical 9D exhaustive root search: not computed
physical first-entry masses and joint law: not computed
unconditioned finite-K population law: not computed
3+1 selection dynamics: not derived
```

Within the registered quadratic graph-sector model, Brief 0018 closes the
zero-level-matched finite-\(K\) classical source measure and its exact direct
sampler. It also closes the type, precedence, serialization and replay
contract for all downstream event records.

This is a source-and-interface theorem. It is not a physical first-entry
calculation. In particular, no event outcome has yet been assigned a physical
mass.

## Exact source theorem

The starting object is one normalized ambient delta--Liouville measure. It is
not an arbitrary mixture of constraint branches and not a geometric surface
measure inserted after the constraints have been solved.

For

\[
M=T_FL_w,\qquad d=16K,\qquad
E_*=E_\perp-\frac{\|P_{\rm tot}\|^2}{4M},
\]

the total target-momentum constraint removes \(P_+\). The remaining
zero-mode and chiral coordinates obey

\[
H_\perp
=\frac{\|P_{\rm tot}\|^2}{4M}
+\|w\|^2
+\sum_{i=1}^{2}
\left(\|z_i^L\|^2+\|z_i^R\|^2\right),
\]

\[
\mathcal P_{\sigma,i}
=\|z_i^R\|^2-\|z_i^L\|^2.
\]

The chiral transformation has the constant per-mode, per-transverse-component
Jacobian

\[
dx\,dy\,d\Pi_x\,d\Pi_y
=\frac{4}{k_n^2}\,d^2z^L\,d^2z^R.
\]

It therefore introduces no state-dependent reweighting.

Set

\[
s_0=\|w\|^2,\qquad
l_i=\|z_i^L\|^2,\qquad
r_i=\|z_i^R\|^2,\qquad
s_i=l_i+r_i.
\]

The eight-dimensional relative momentum gives

\[
dw\propto s_0^3\,ds_0\,d\omega_0.
\]

At zero world-sheet momentum, the two chiral constraints give

\[
l_i^{d/2-1}r_i^{d/2-1}
\delta(r_i-l_i)\,dl_i\,dr_i
=2^{-(d-1)}s_i^{d-2}\,ds_i.
\]

Consequently, the reduced radial density is

\[
s_0^3s_1^{d-2}s_2^{d-2}
\delta(s_0+s_1+s_2-E_*).
\]

After division by \(E_*\), the exact normalized law is

\[
\boxed{
\left(\frac{s_0}{E_*},\frac{s_1}{E_*},\frac{s_2}{E_*}\right)
\sim\operatorname{Dirichlet}(4,d-1,d-1)
}
\]

with density

\[
\frac{\Gamma(2d+2)}
{\Gamma(4)\Gamma(d-1)^2}
x_0^3x_1^{d-2}x_2^{d-2}
\]

on \(x_j\ge0\) and \(x_0+x_1+x_2=1\). Since \(d=16K\), the claimed law is
\(\operatorname{Dirichlet}(4,16K-1,16K-1)\).

The canonical audit cell fixes

\[
\ell_s=1,\quad T_F=\frac1{2\pi},\quad L_w=16\pi,\quad M=8,\quad
K=1,\quad E_\perp=2,
\]

\[
P_{\rm tot}=(4,4,0,\ldots,0),
\]

so \(E_*=1\), \(d=16\), and the registered law is
\(\operatorname{Dirichlet}(4,15,15)\). The transverse periods are eight,
the winding period is \(16\pi\), and the two winding orientations are
\(+1\) and \(-1\).

The direct sampler draws independent Gamma variables of shapes
\((4,d-1,d-1)\), five independent sphere directions, and an independent Haar
relative centre on \(T_\perp^8\). It then reconstructs the zero modes and
chiral coefficients. A hierarchical-Beta construction supplies an
algorithmically independent radial control.

The translation gauge is \(Q_2=0,\ Q_1=Q_{\rm rel}\). The oscillator field
contains no centre, so \(X_i^\perp=Q_i+Y_i\) includes \(Q_i\) exactly once.
The implementation rejects the former double-centre convention.

## Source audit closure

There is one canonical source registry. The production sampler and the
independent statistical audit bind to it by canonical hashes:

```text
source registry:
35d31a64e45d9a3ea9cc346e19d8bc5d8d40d1f9eac68eb07385fb291aed8cdb

source-draw registry:
4bc0d8eadef9ad8aea8752f25e105127311b83edebc99ebe1b1b7561999e1bd4

full statistical report semantic payload:
dcbd68d124df5bc2a1dbd74fcf6e190e32102d337261abca2d459cd08ac7056e
```

The source-draw identity excludes event thresholds, rank tolerances, reaction
data, validity thresholds and response data. Mutating those downstream
quantities leaves every sampled coefficient unchanged.

The registered open-uniform map uses 52-bit midpoints strictly inside
\((0,1)\). Named substreams and a deterministic Decimal-90 math layer make
the 512-sample source payload replayable across the tested Windows and Linux
runtimes.

All 512 draws are retained. The registered validity predicate labels 283
draws valid and 229 draws `source_invalid`. These counts describe this audit
cell only. They are not physical probabilities, and the 229 invalid samples
are neither redrawn nor removed.

The independent full statistical profile executes 514 preregistered scalar
gates with zero failures. It checks the source implementation through a
production-output bridge, rather than auditing a second source cell. The
analytic derivation remains the proof of the radial law; the statistical
audit checks the implementation.

## Total replayable event-record contract

The event layer now has one closed-object schema and one deterministic
precedence rule. Every record has exactly one primary outcome:

```text
source_invalid
left_censored_active_episode
torus_branch_ambiguous
ambiguous_tie
numerically_unresolved
no_entry_proved
right_censored_no_entry
right_censored_active_episode
tie_cluster
degenerate_spatial_minimum
grazing_entry
regular_first_entry
```

Simultaneous properties remain orthogonal flags. They do not create multiple
mass rows. Complete ties retain their full unordered cluster, while JSON
ordering is serialization only.

`ambiguous_tie` is reserved for complete root coverage with unresolved
equality or ordering among isolated earliest candidates. Any missing root or
order-relevant unresolved region is `numerically_unresolved`.

Finite-window exclusion yields `right_censored_no_entry`. The stronger
`no_entry_proved` label requires an exact recurrence certificate or a global
strict lower bound. An outer tangent touch does not re-arm an episode.
Re-arming requires a certified strict outer overshoot and its right
neighborhood.

The problem commitment separately binds the source registry, source-draw
registry, realized source state, source-validity record, solver registry,
metric, lattice, thresholds, observation window, root functions and proof
models. The proof-model registry covers:

1. source predicates and event headers;
2. gap-free domain and image coverage;
3. exclusion, unique-root and singular-cluster leaves;
4. seam and image quotient classes;
5. complete candidate clusters;
6. geometry, derivative, rank and normal jets;
7. implicit positive-dimensional sets; and
8. episode, outer-exit, closest-approach and re-arm ledgers.

Rank, normal dimension, \(P_N\), \(b\), \(\ell\), singular values and reaction
data are downstream marks. They cannot enter the source draw or event
selection. If rank is unresolved, the record cannot fabricate a scalar normal
dimension or authoritative projector.

The synthetic fixtures have pinned problem and proof-model anchors. A
coordinated rewrite of roots, geometry, rank, source validity, recurrence,
closest time or outer-exit time fails independent replay even when local JSON
hashes are refreshed.

## Physical-envelope boundary

The schema accepts a future physical solver payload only as a formal
interchange envelope. Brief 0018 requires

```text
authoritative_physical_certificate = false
independent_replayer = brief-0019-independent-event-replayer
```

The envelope becomes physical evidence only after Brief 0019 independently
reconstructs the registered functions, interval witnesses, box/image cover,
root ordering, episode history and provenance. The current synthetic controls
therefore close the certificate interface, not a physical event certificate.

## Reproducibility

From a clean repository root:

```bash
python artifacts/0018/microcanonical_source.py --check
python artifacts/0018/statistical_audit.py --profile full --check
python artifacts/0018/generate_schema.py --check
python artifacts/0018/event_contract.py --check
python -m unittest discover -s artifacts/0018 -p "test_*.py" -v
```

The integrated suite replays on Windows and WSL Linux with 150 discovered
tests, one designed skip and no failures. Source generation, all 514
statistical gates, schema generation and event-contract replay pass on both
platforms.

## Closure ledger

The following objects are closed within the declared finite-\(K\), quadratic,
graph-sector audit model:

1. the ambient delta--Liouville reduction at
   \(\mathcal P_{\sigma,1}=\mathcal P_{\sigma,2}=0\);
2. the exact \(\operatorname{Dirichlet}(4,16K-1,16K-1)\) source theorem;
3. the normalized direct sampler and the canonical \(K=1\) audit cell;
4. source retention without validity redraw or rank conditioning;
5. cross-platform deterministic and statistical implementation audits; and
6. the total, disjoint, cluster-preserving, rank-blind event-record contract.

The following objects remain open:

1. an independently replayed exhaustive physical 9D interval root solver;
2. physical first-entry and episode-closest outcome masses;
3. the joint law of \((T,j,b,\ell,a,\sigma_3)\);
4. the unconditioned finite-\(K\) population pushforward;
5. a continuum or quantum-string preparation theorem; and
6. dimension-selection dynamics producing a stable visible \(3+1\) basin.

The next gate is therefore not another source model. It is the source-separated
Brief 0019 proof backend and its gap-free 9D box/image coverage. Only after
that backend closes may the project compute first-entry masses and the
unconditioned population law.
