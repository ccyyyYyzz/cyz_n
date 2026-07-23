# Brief 0018 independent source statistical audit

This directory contains `audit-k1-v1`, a deterministic controlled audit of
one finite-\(K\) source sampler implementation.  It uses Python and NumPy only;
SciPy is neither imported nor required.

The artifact checks that two independently implemented radial samplers and
the rejection-free direction/torus construction behave consistently with
the registered finite-sample consequences of

\[
(X_0,X_1,X_2)\sim\operatorname{Dirichlet}(4,15,15).
\]

It does **not** derive that Dirichlet theorem.  The theorem must come from the
ambient delta--Liouville and coarea calculation in Brief 0018.  Passing this
artifact also does not establish a physical string preparation, an encounter
or first-entry law, a root-coverage certificate, a dimension-selection law,
or any \(3+1\) conclusion.

## Frozen audit cell

The strict registry is
[`stat_audit_registry.json`](stat_audit_registry.json).  It fixes

\[
K=1,\quad d=16,\quad M=8,\quad k_1=\frac18,\quad
E_\perp=2,\quad E_*=1,
\]

with eight transverse torus periods equal to \(8\).  The winding period is
\(L_w=16\pi\), represented by the registered binary64 value.  Nonzero total
momentum \(P_{\rm tot}=(4,4,0,\ldots,0)\) makes omission of the centre-energy
term detectable.

All values that determine the source draw live under
`source_draw_registry`.  Event thresholds, validity thresholds and initial
history are stored separately and cannot enter the source substream hash.

## Random construction

The algorithm version is
`pcg64dxsm-u52mid-exp-boxmuller-v1`.

- PCG64DXSM is accessed through `random_raw`.
- Raw words are mapped to a fixed open 52-bit midpoint grid in \((0,1)\).
- Integer-shape Gamma variables are sums of exponential variables.
- The independent hierarchical-Beta implementation uses order statistics:
  the fourth of 33 uniforms and the fifteenth of 29 uniforms.
- Sphere directions use the explicitly implemented Box--Muller map followed
  by normalization.
- A complete \(K=1\) source sample consumes exactly 114 raw words.  There is
  no tolerance conditioning, MCMC, or replacement draw.

The ideal continuous-uniform construction has the stated mathematical
distributions.  PCG64DXSM and floating-point evaluation are controlled
numerical implementations, not proofs of physical randomness.

## Full preregistered run

From the repository root:

```text
python artifacts/0018/run_stat_audit.py --profile full
python artifacts/0018/run_stat_audit.py --profile full --check
```

The first command writes
`artifacts/0018/stat_audit_report.json`.  The second command regenerates the
complete audit without writing and compares strict parsed semantic JSON.
Seeds, sample sizes and thresholds have no CLI overrides.

The full profile uses:

- \(2^{20}\) Gamma radial samples;
- \(2^{20}\) hierarchical-Beta radial samples;
- \(2^{18}\) complete source samples;
- \(2^{20}\) samples for each hostile radial-shape marginal.

Its 514 scalar acceptance tests are

\[
34+34+34+64+48+216+72+12=514:
\]

- 34 exact Dirichlet moments for each radial implementation;
- 34 Gamma-versus-Beta moment comparisons;
- 64 torus Fourier-character components;
- 48 torus/radial mixed-character components;
- 216 sphere-coordinate moments;
- 72 sphere adjacent-coordinate products;
- 12 pairwise chiral-direction dot controls.

The familywise false-rejection budget is \(10^{-8}\), allocated by
Bonferroni over exactly 514 tests.  Each acceptance band is a two-sided
Bernstein bound using the exact null variance.  Failed samples are never
deleted and failed tests are never retried with another seed.

## Fast deterministic unit profile

```text
python artifacts/0018/run_stat_audit.py --profile fast
```

This checks the strict registry, raw PRNG golden vectors, construction
invariants, semantic manifest and structural hostile mutations.  It does not
execute any of the 514 statistical acceptances, writes no report by default,
and returns `PASS_FAST_NONAUTHORITATIVE`.  It does not change or replace the
full-profile seeds or thresholds.

## Tests

```text
python -m unittest discover -s artifacts/0018 -p "test_*.py" -v
```

To include a fresh full statistical regeneration in the unittest process:

```text
set CYZ_RUN_FULL_0018_AUDIT=1
python -m unittest discover -s artifacts/0018 -p "test_*.py" -v
```

The committed report is always checked for its semantic SHA-256, complete
514-item ledger, hostile-mutation rejection, hard constraints and normalized
code inventory.  The environment variable adds a new \(2^{20}/2^{18}\)
replay; it does not select a new seed or threshold.

## JSON and report semantics

Every reader rejects duplicate keys, `NaN`, infinities, exponent overflow
such as `1e9999`, unknown registry fields and type substitutions such as
`true` for `1`.  Semantic hashing uses sorted, compact UTF-8 JSON and is
independent of indentation and LF/CRLF line endings.  Source-code inventory
hashes normalize line endings before hashing.

The report contains no timestamp, hostname, absolute checkout path, Python
`hash()` value or wall-clock-dependent field.  Its `semantic_sha256` covers
the parsed report payload except for the hash field itself.

## Known limitations

- Finite-sample agreement can falsify an implementation but cannot prove the
  analytic Dirichlet law or pseudorandom independence.
- The audit cell is \(K=1\); larger \(K\), nonzero level matching and other
  source families require separately registered controls.
- NumPy's PCG64DXSM raw stream is frozen by golden words, but transcendental
  functions still depend on the declared Python/NumPy numerical runtime.
- The package audits a source draw only.  It does not implement certified
  torus-image root coverage, hysteresis, tie clustering, closest approach or
  event-conditioned marks.
