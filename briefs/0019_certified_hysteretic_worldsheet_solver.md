# Brief 0019 — certified exhaustive hysteretic world-sheet event solver

Baseline: the final verified Brief 0018 integration commit after source and
event-contract repair.

## Mission

Close the next gate left open by Brief 0018: turn one serialized finite-\(K\)
F1 source state into a replayable, rank-blind event record without silently
missing a torus image, world-sheet root, earlier contact, tie, outer exit or
episode closest point.

This round is an algorithmic and certificate theorem for a declared
finite-\(K\), finite-window model.  It is not yet the population law and may
not report a \(3+1\) selection result.

The authoritative three-state result for each sample is:

1. certified event/censoring record;
2. registry or declared-class exclusion;
3. `numerically_unresolved` with every order-relevant unresolved box retained.

Failure of a numerical candidate search is never `no_entry_proved`.

## 1. Frozen mathematical object

Use the physical-length, opposite-winding convention

\[
X_i^\perp(t,\sigma_i)
=Q_i+V_it+Y_i(t,\sigma_i),
\qquad
X_i^w=o_i\sigma_i,
\qquad (o_1,o_2)=(+1,-1).
\]

For every Fourier mode,

\[
Y_i=x_i(t)\cos(k_n\sigma_i)+y_i(t)\sin(k_n\sigma_i),
\]

\[
\dot x_i=p_i,\quad \dot y_i=q_i,\quad
\dot p_i=-k_n^2x_i,\quad \dot q_i=-k_n^2y_i .
\]

The unwrapped separation and an image branch are

\[
d(t,\sigma_1,\sigma_2)
=X_1-X_2,\qquad
s_n=d-\Lambda n,
\]

\[
F_n=\frac12s_n^\top Gs_n.
\]

All serialized binary64 source coefficients are interpreted as their exact
dyadic rational values.  Transcendental evaluations use outward-rounded Arb
balls.  The solver therefore certifies the frozen numerical finite-\(K\)
model; it does not retroactively turn pseudorandom binary64 draws into exact
continuum random variables.

The solver registry must bind:

- source-state and source-registry semantic hashes;
- the complete serialized source state and its exact-dyadic coefficient
  projection, with both projections recomputed from the pinned source
  registry rather than accepted from the certificate;
- \(G,\Lambda,H,r_{\rm in},r_{\rm out},[t_0,t_1)\);
- initial history and continuation convention;
- precision ladder, subdivision rule, operation/memory budgets;
- image enumeration, seam and duplicate policy;
- candidate backend version and proof backend version;
- every tolerance used only for candidate generation;
- the exact event-record schema and certificate-bundle hashes.

Bundle-internal hashes prove consistency only; they are not a trust anchor.
The accepted solver-registry hash and equation-family version must be pinned by
the replayer code or supplied as an independently authenticated run input.
The replayer reconstructs \(d,F,g,Dg\) from that pinned registry and source
state.  A certificate-supplied polynomial, root location, function registry or
backend name is never allowed to replace the reconstructed physical problem,
even when every ordinary JSON hash and cross-reference is recomputed.

Rank, normal dimension, response rank, requested winner and reaction data are
forbidden solver inputs.

The first physical integration fixtures are selected before inspecting any
event outcome.  Under the canonical Brief 0018 source registry

`35d31a64e45d9a3ea9cc346e19d8bc5d8d40d1f9eac68eb07385fb291aed8cdb`

and source-draw identity

`4bc0d8eadef9ad8aea8752f25e105127311b83edebc99ebe1b1b7561999e1bd4`,

use the least source index with each required validity status:

- index \(0\), state hash
  `bafc85014205bbdbb8156e059606a73a0c899911745f189a4ac4e0c90742670b`,
  is the first `source_invalid` control and must execute no event solver;
- index \(2\), state hash
  `1c671b6bf8e737d238c21de8b0f694a57b8bfab7006ebb1401136176567f118c`,
  is the first `valid` source and is the physical source-to-solver wiring
  control.

This rule does not select on encounter, rank or solver success.  Index \(2\)
is not a population estimate; Brief 0020 must still push forward the complete
pre-registered source ledger, retaining invalid and unresolved mass.

## 2. Rigorous backend boundary

Pin one python-flint/Arb version and record FLINT/Arb runtime metadata.
NumPy, SciPy and ordinary floats may generate candidates or preconditioners
only.

An `excluded`, `unique_root`, positive-sign, negative-sign, positive-definite
or strict-order conclusion must be produced by outward-rounded ball
arithmetic or exact rational algebra.  `mpmath.iv.findroot`, a dense grid and
an optimizer success flag are never proof witnesses.

Implement a second source-separated certificate replayer.  It may share the
typed certificate format and Arb dependency, but it must not import the
solver/generator module, candidate code or cached runtime objects.

The replayer must also close provenance transitively.  Every range,
monotonicity, Krawczyk, singular-set, global-minimum, no-earlier, tie,
outer-exit, closest-point, recurrence and global-lower-bound witness must be
recomputed by the registered proof backend (or by an explicitly registered
exact-algebra primitive).  An outer solver-backend label cannot authorize a
subcertificate carrying another opaque backend label.

## 3. Exact dyadic box tree

The initial domain is a half-open torus/time cover represented by exact
dyadic or rational boxes.  Every internal node has a declared split axis and
split point.  Children must be disjoint and their union must equal the parent
exactly.

Each leaf has exactly one status:

- `excluded_range`;
- `excluded_monotone`;
- `unique_root`;
- `certified_singular_cluster`;
- `seam_duplicate`;
- `unresolved`.

The bundle stores the full tree topology, branch/image ID, exact bounds,
witness payload and child hashes.  Counts and root IDs are derived from the
tree, not trusted input fields.

The replayer must reject:

- an empty complete cover;
- a missing, duplicated or overlapping child;
- a recomputed hash attached to a tree with a deleted leaf;
- a leaf whose witness does not prove its status;
- an unresolved leaf hidden under a complete flag;
- an image manifest not referenced by the initial cover.

Wall-clock time is not event semantics.  Budget exhaustion emits unresolved
leaves under a deterministic operation/precision budget.

## 4. Complete image enumeration

For every search box \(B\), enumerate every \(n\in\mathbb Z^9\) for which

\[
(d(B)-\Lambda n)\cap
\{s:s^\top Gs\le r_{\rm out}^2\}\ne\varnothing .
\]

For rectangular \(\Lambda=\operatorname{diag}(L_A)\), use the rigorous
coordinate superset

\[
c_A=r_{\rm out}\sqrt{(G^{-1})_{AA}},
\]

\[
n_A\in
\left[
\left\lceil\frac{\inf d_A-c_A}{L_A}\right\rceil,
\left\lfloor\frac{\sup d_A+c_A}{L_A}\right\rfloor
\right].
\]

The bounds on \(c_A\), floors and ceilings must be certified.  A subsequent
metric lower-bound test may discard false-positive images; it may not discard
an image from a non-rigorous nearest-image heuristic.

Store world-sheet, target-torus and time-seam transformations.  Quotient two
roots only after an exact physical-equivalence certificate.  Overlapping
enclosures alone do not prove duplication.

## 5. Interval jets

Implement one routine that evaluates, on a box,

\[
d,\quad d_a,\quad d_{ab},
\qquad a,b\in\{\sigma_1,\sigma_2,t\},
\]

then derives

\[
F_a=d_a^\top Gs_n,
\qquad
F_{ab}=d_{ab}^\top Gs_n+d_a^\top Gd_b.
\]

For \(r\in\{r_{\rm in},r_{\rm out}\}\),

\[
g_{r,n}
=
\left(F_{\sigma_1},F_{\sigma_2},F_n-r^2/2\right),
\]

and for completed-episode closest points,

\[
g_{{\rm cl},n}
=
\left(F_{\sigma_1},F_{\sigma_2},F_t\right).
\]

At a boundary root, verify independently that

\[
\det Dg_{r,n}=F_t\det H_{\sigma\sigma}.
\]

Every vector/matrix interval has a strict shape and coordinate/unit label.

## 6. Exclusion and Krawczyk witnesses

A range exclusion records a component of \(g(B)\) whose Arb ball excludes
zero.  A monotonicity exclusion records a derivative sign plus the necessary
face bounds.

For a candidate box \(B\), midpoint \(x_0\) and outward-enclosed point
preconditioner \(C\), compute

\[
K(B)
=x_0-Cg(x_0)
+\bigl(I-CDg(B)\bigr)(B-x_0).
\]

`unique_root` requires

\[
K(B)\subset\operatorname{int}B.
\]

The bundle stores \(x_0,C,g(x_0),Dg(B),K(B)\), precision and inclusion
margins.  The replayer recomputes all balls and the strict inclusion; it does
not trust the stored Boolean.

Disjoint uniqueness boxes can still describe one seam-equivalent physical
root.  Conversely, two distinct uniqueness boxes with equal time require a
complete tie cluster.

If a box continues to contain a singular or positive-dimensional root set,
emit a typed set certificate only when its enclosure and dimension statement
are replayable.  Otherwise retain the box as unresolved.

## 7. From branch roots to first entry

A branchwise root becomes a regular first-entry member only after certifying:

\[
H_{\sigma\sigma}\succ0,\qquad F_t<0,
\]

unique torus logarithm, global spatial minimality over all images, an armed
history, and no earlier sublevel point.

Positive definiteness uses a rigorous Sylvester, Cholesky or eigenvalue
enclosure.  An interval merely containing zero proves neither grazing nor
degeneracy.

`grazing_entry` requires an exact/symbolic zero, interval multiplicity or
equivalent replayable one-sided touch certificate for \(F_t=0\).

`degenerate_spatial_minimum` requires

\[
H_{\sigma\sigma}\succeq0,\qquad
\det H_{\sigma\sigma}=0
\]

by exact or certified set arithmetic, plus global first-contact evidence.

For a putative earliest time interval \(I_*\), directly cover the complete
sublevel domain before \(I_*\) and prove

\[
F_n-r_{\rm in}^2/2>0
\]

on every earlier leaf and image.  Root absence alone is insufficient at an
initially active or unresolved seam.

Root-time handling distinguishes:

- exact physical duplicates;
- distinct equal-time roots, forming one complete unordered tie cluster;
- strictly ordered roots;
- overlapping intervals with unresolved order, producing `ambiguous_tie`
  only when this is the sole remaining uncertainty;
- any possible missing earlier root, producing `numerically_unresolved`.

## 8. Hysteresis, outer exit and closest point

Once an inner entry is selected, process every later inner contact and
outer-tube component in the same pair-level episode until strict overshoot.
Component birth, merge, split and disappearance are marks, not new entries.

An outer-boundary root is an exit only after certifying:

- it is the global spatial minimum;
- every simultaneous minimizer has left the outer tube;
- a right-neighborhood interval satisfies
  \[
  \rho(t)>r_{\rm out};
  \]
- its boundary and post-boundary intervals lie in the observation window.

Re-arm exactly once after that certificate.

For a completed episode, cover all roots of \(g_{\rm cl,n}=0\), all image
branches and both time endpoints.  Retain every tied global closest point.
For a right-censored active episode, serialize only a provisional certified
window minimum.

All episode times must be consistently ordered and agree with the
half-open-window continuation state.

## 9. No-entry semantics

Complete finite-window exclusion gives
`right_censored_no_entry`.

`no_entry_proved` requires either a global lower-bound certificate or exact
recurrence data

\[
P=mL_w,\qquad
(V_1-V_2)P=\Lambda_\perp z,
\qquad m\in\mathbb N,\ z\in\mathbb Z^8.
\]

Store \(m,L_w,P,z\), exact arithmetic witnesses and the complete time-seam
cover.  A floating interval containing a rational number is not an exact
recurrence proof.

## 10. Mandatory fixtures

The generator and independent replayer must cover:

1. a unique regular root, an excluded box and a singular Krawczyk failure;
2. separate \(F_t=0\) and \(\det H_{\sigma\sigma}=0\) controls;
3. a narrow high-\(K\) root between candidate-grid nodes;
4. target-torus, world-sheet and time-seam duplicates counted once;
5. complete image enumeration for non-unit diagonal \(G\);
6. local non-global Morse roots, saddles and outward roots rejected;
7. simultaneous, strictly ordered-nearby and unresolved-order root pairs;
8. repeated inner contacts before outer exit and a new episode after re-arm;
9. exact recurrent no-entry and incommensurate finite-window no-entry;
10. positive-dimensional roots and deterministic budget exhaustion retained;
11. interior, endpoint and tied episode-closest points;
12. source-invalid records that execute no event solver;
13. a certified rank-two event with seven-dimensional normal fiber;
14. a tolerance-only rank label retained as unresolved;
15. hostile deletion of a tree leaf after all ordinary hashes are recomputed;
16. hostile empty coverage, wrong image bound, false Krawczyk inclusion,
    false recurrence, false tie and false outer overshoot;
17. coordinated replacement of a root model, root time and all dependent
    ordinary hashes while leaving the pinned source/problem commitment
    unchanged;
18. a globally self-consistent no-entry or lower-bound certificate produced
    by a backend that differs from the registered proof-backend closure.

Every hostile fixture must fail at its intended semantic gate, not merely
raise an unrelated exception.

## 11. Required artifacts

Commit:

1. `responses/0019_certified_hysteretic_worldsheet_solver.md`;
2. `artifacts/0019/interval_event_solver.py`;
3. `artifacts/0019/certificate_replayer.py`;
4. `artifacts/0019/test_interval_event_solver.py`;
5. `artifacts/0019/test_certificate_replayer.py`;
6. `artifacts/0019/solver_registry.json`;
7. `artifacts/0019/certificate_bundle.schema.json`;
8. `artifacts/0019/fixture_manifest.json`;
9. `artifacts/0019/solver_controls.json`;
10. `artifacts/0019/README.md`.

Strict JSON, type-strict semantic replay, duplicate/nonfinite rejection,
normalized-LF code inventory and canonical semantic hashes are mandatory.

## 12. Acceptance and next gate

This round passes only if a clean Windows checkout and an independent Linux
checkout replay the same certificates and all discovered tests, and every
accepted authoritative record is backed by a gap-free proof bundle.

The permitted success statement is:

> For the declared finite-\(K\), finite-window source fixtures, the
> rank-blind hysteretic event solver either emits a replay-certified total
> event record or preserves every order-relevant unresolved region.

It is not:

> The physical F1 first-entry distribution or \(3+1\) selection has been
> computed.

The next gate is to run this solver on the unconditioned preregistered source
population, retain source-invalid and unresolved mass, and estimate the joint
law of

\[
(T,j,b,\ell,a,\sigma_3)
\]

with finite-sample uncertainty and \(K\)-regulator sensitivity.
