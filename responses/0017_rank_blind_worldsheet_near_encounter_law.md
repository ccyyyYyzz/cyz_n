---
brief: 0017
branch: brief-0017
status: repaired_inconclusive
captured: 2026-07-23
artifacts:
  - artifacts/0017/probe_0017.py
  - artifacts/0017/test_probe_0017.py
  - artifacts/0017/analytic_controls.json
---

# Response 0017 — repaired rank-blind finite-K near-encounter bundle

## Physical verdict

```text
verdict: inconclusive
physical finite-K first-entry law: not computed
3+1 selection: not computed
```

The repair makes the committed analytic/schematic bundle executable and narrows
its claims. It does not freeze a physical source cell, run a constrained
microcanonical sampler, certify an exhaustive hysteretic root search, compute a
normalized physical outcome table, or derive a 3+1 selection law.

## Claim classification

**Exact analytic controls** are limited to the opposite-winding identity, the
iid Gaussian \(\mathbb R^{8\times2}\) hard-edge exponent seven and coefficient
\(\sqrt{\pi/2}/48\), the Gram-eigenvalue exponent \(7/2\), the pure affine
incoming-volume Palm exponent eight and coefficient \(1/105\), the affine
\(\delta^2,\delta^{-1},\delta\) scaling identities, the Fourier round trip, and
the declared quadratic flow invariants.

**Conditional propositions** are the Palm power-transfer rule, the
curvature-lifted local closest-stationary counterexample, and Borel
normalization after a frozen normalized source and an implemented total event
map. They are not theorems of the physical finite-\(K\) first-entry law.

**Schematic event semantics** are the hostile executable vector, rank,
projector, dependency, hysteresis, tie, and primary-precedence controls. Their
registry counts are not probabilities.

**Open physical gates** are, in order: freeze a valid principal source and total
event schema; validate a constrained sampler; certify an exhaustive hysteretic
first-entry root solver.

## Repairs implemented

### 1. Packaging and execution

The public API now exposes the current descriptive names and repaired aliases:
`hard_edge`, `entry_controls`, `hysteresis`, `outcome_ledger`, `flow_control`,
`dependency`, `read_json`, `cbytes`, and `OUTCOMES`. The committed test imports
the exact committed probe and contains 12 hostile tests.

Vector arithmetic validates numeric type and exact shape before every paired
operation, Gram matrix, or projection. A length-seven vector cannot be silently
accepted as \(\mathbb R^8\) through `zip` truncation. JSON loading rejects
duplicate keys and nonfinite constants. Semantic equality is recursive and
type-strict, so `1` and `1.0` are not equal.

`analytic_controls.json` is regenerated from the exact probe, and `--check`
compares duplicate-key-rejected, type-strict canonical semantics rather than
line endings.

### 2. Principal source measure

The principal family is the single normalized delta-Liouville law

\[
 d\mu_{E,K,h}=Z_h^{-1}
 \frac{d^8Q_{\rm rel}}{\operatorname{Vol}(T^8_\perp)}
 \delta(C(y)-c_h)\,dy.
\]

For regular coarea branches,

\[
\omega_r=\frac{\nu_r(\Gamma_r)}{\sum_s\nu_s(\Gamma_s)},
\qquad \omega_r\ge0,\qquad \sum_r\omega_r=1.
\]

The executable volume example \((2,3,5)\) produces
\((1/5,3/10,1/2)\). The equal mixture is separately named and marked
nonprincipal. Constraint-singular points retain the distinct primary outcome
`source_constraint_unresolved`; they are not silently called `source_invalid`.

No numerical source cell is frozen, so this remains a parameterized family and
does not close the physical gate.

### 3. Fourier convention

The oscillator field \(Y_i\) contains no \(Q_i\), and
\(X_i^\perp=Q_i+Y_i\) includes \(Q_i\) exactly once. The inverse convention is

\[
c_n^L=\tfrac14[x_n+q_n/k_n+i(p_n/k_n-y_n)],\qquad
c_n^R=\tfrac14[x_n-q_n/k_n-i(y_n+p_n/k_n)].
\]

The probe executes the real/complex round trip and rejects a second-\(Q_i\)
mutation.

### 4. Total disjoint event semantics

One primary outcome is selected by deterministic precedence, while overlapping
facts remain flags:

```text
source_constraint_unresolved
source_invalid
left_censored_active_episode
torus_branch_ambiguous
numerically_unresolved
no_entry_proved
right_censored_no_entry
right_censored_active_episode
degenerate_spatial_minimum
grazing_entry
tie_cluster
regular_first_entry
```

The tie policy emits the complete unordered certified minimizer cluster and no
scalar representative. Canonical ordering is serialization only. The global
hysteresis state machine merges every component subentry until global outer
exit and rearms only at that exit. Initial active, unfinished active, finite
window no-entry, and certified no-entry cases are distinct. Source-invalid and
censoring overlap, and degenerate/grazing/tie overlap, are exercised without
deleting facts or mass.

The former equal \(1/12\) physical ledger is removed. The twelve synthetic cases
only prove registry coverage. A total Borel physical map and
\(\sum_\alpha M_\alpha=1\) remain conditional on the frozen source and certified
solver.

### 5. Near-degeneracy and rank

The probe stores exact rank, raw unthresholded singular values, numerical rank,
and the tolerance \(10^{-14}\sigma_1\) separately. It never overwrites a small
positive singular value.

Exact-rank-three controls include
\(q=10^{-8}e_1,10^{-12}e_1,10^{-16}e_1\), \(u=e_2\). The first two report
numerical rank three and positive \(\sigma_3\); the hostile \(10^{-16}\) case
reports numerical rank two but keeps positive raw \(\sigma_3\). The identity

\[
\det(J^TJ)=|q\wedge u|^2+|p_1\wedge q\wedge u|^2
\]

is checked with exact rational determinants/minors; floating relative error is
only an auxiliary field.

### 6. Controls and analytic surrogates

The fixed-six mutation is rejected by an executed rank-two projector geometry.
The dependency audit executes rank and \(\sigma_3\) conditioning mutations and
rejects both. The hysteresis control executes merger and rearm transitions.
These are honestly labelled synthetic/schematic where they do not perform the
physical calculation.

The exact surrogate facts retained are:

```text
Gaussian singular-value exponent:       7
Gaussian coefficient:                   sqrt(pi/2)/48
Gram minimum-eigenvalue exponent:        7/2
pure volume-Palm exponent:               8
pure volume-Palm coefficient:            1/105
affine scaling:                          delta^2, delta^-1, delta
curvature-lifted conditional example:    local exponent 6
```

The high-precision audit uses 70-digit `Decimal`, the relative-scale transform
\(y=\varepsilon^2x^2\), 8192/16384 composite-Simpson refinement, and a
Richardson estimate. At \(\varepsilon=0.05\):

```text
fixed-point ratio: 0.9987507809245811
volume-Palm ratio: 0.9987507809245810
```

Both reported error estimates are below \(1.3\times10^{-16}\). The inaccurate
`0.9985753405` claim is removed. None of these surrogate exponents is assigned
to the physical constrained first-entry law.

### 7. Literature wording and metadata

The response now distinguishes Sakellariadou's lattice reconnection/evolution
experiment from a continuous first-entry law; Mitchell–Turok,
Deo–Jain–Tan, and Mañes as distinct statistical, microcanonical/state, and
state-average precedents; EGJK as a homogeneous-background thermodynamic
initial-data ensemble; GKM's impact-parameter draw as an isotropy/even-
distribution simulation prescription; and JJP as conditional on an already
specified local collision.

The published titles are corrected to *Numerical experiments on string
cosmology* and *String distributions above the Hagedorn energy density*.
Primary metadata/DOIs are recorded in the brief, together with Edelman for the
Gaussian/Wishart control and Kac/Rice for roots/crossings.

## Exact committed replay

Run from a clean repository root:

```bash
python3 -m py_compile \
  artifacts/0017/probe_0017.py \
  artifacts/0017/test_probe_0017.py
python3 artifacts/0017/probe_0017.py --help
python3 artifacts/0017/probe_0017.py \
  --output artifacts/0017/analytic_controls.json
python3 artifacts/0017/probe_0017.py \
  --check --output artifacts/0017/analytic_controls.json
python3 -m unittest discover \
  -s artifacts/0017 -p 'test_probe_0017.py' -v
```

Recorded results for the exact payloads:

```text
py_compile exit 0
--help exit 0
generation exit 0; status PASS
--check exit 0; duplicate-key-rejected type-strict canonical semantic match
unittest exit 0; Ran 12 tests; OK
```

Clean detached materialization was clean before and after the replay. The
runtime was Python 3.13.5 on Linux 6.12.13 x86_64 with Debian glibc 2.41.

## Artifact hashes

```text
artifacts/0017/probe_0017.py normalized-LF SHA-256
11ff23b2660424efffe01d7daa7c303f9435e85cbd3ad0b4c34beb279759c9e4

artifacts/0017/test_probe_0017.py normalized-LF SHA-256
323f6f4609aaeda39da3de1e0ef5a0177e1c0f3027356714a814953861f7a435

artifacts/0017/analytic_controls.json file SHA-256
a6c69692c77bae1910b58a57021e355f6621db17b17ab1bf5544b3d6667282b3

artifacts/0017/analytic_controls.json canonical-payload SHA-256
54104e9d13333d5eb1b598cd568193d9e1c17dc850bd9d9ecd899a4db14a6d63
```

## Physical ledger

```text
principal source cell: parameterized only; not frozen
total physical event map: not implemented or proved total
normalized regular mass: not computed
normalized exceptional mass: not computed
constraint-singular mass: not computed
encounter-rank mixture: not computed
event-conditioned sigma_3: not computed
joint T,j,b,ell law: not computed
physical finite-K first-entry law: not computed
3+1 selection: not computed
```

The earliest gate is a frozen valid principal source measure and total event
schema. The next implementation is a constrained sampler and certified
exhaustive hysteretic first-entry root solver. Every invalid, unresolved,
ambiguous, censored, tied, grazing, degenerate, lower-rank, no-entry, and regular
record must remain in the output. Until those gates close, the only supportable
physical verdict is **inconclusive**.
