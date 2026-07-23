# Brief 0018 exact microcanonical source control

This directory is an independent standard-library reference implementation of
the zero-level-matched source theorem in Brief 0018.  It samples the single
ambient delta--Liouville measure of two finite-mode quadratic transverse
strings.  It does not implement the event schema or an encounter solver.

Run from the repository root:

```text
python artifacts/0018/microcanonical_source.py
python artifacts/0018/microcanonical_source.py --check
python -m unittest discover -s artifacts/0018 -p "test_*.py" -v
```

The frozen audit cell is `source_registry.json`.  The winding label and the
ordered complement of transverse target axes are both serialized.  Its
source-draw identity is deliberately smaller than the total audit registry.
Event thresholds, rank tolerances, normal-dimension hints, reaction settings
and source-validity thresholds cannot affect the source coefficient stream.

## Registered theorem

Let

\[
M=T_FL_w,\qquad d=16K,\qquad
E_*=E_\perp-\frac{\|P_{\rm tot}\|^2}{4M}.
\]

For each string and chirality define

\[
z_{in}^{L,R}=\sqrt{2M}\,k_nc_{in}^{L,R}.
\]

After eliminating the fixed total momentum, the energy and two global
world-sheet momenta are

\[
H_\perp-\frac{\|P_{\rm tot}\|^2}{4M}
=\|w\|^2+\sum_i(\|z_i^L\|^2+\|z_i^R\|^2),
\]

\[
\mathcal P_{\sigma,i}
=\|z_i^R\|^2-\|z_i^L\|^2.
\]

At \(\mathcal P_{\sigma,1}=\mathcal P_{\sigma,2}=0\), the energy shares obey

\[
\left(\frac{s_0}{E_*},\frac{s_1}{E_*},\frac{s_2}{E_*}\right)
\sim\operatorname{Dirichlet}(4,16K-1,16K-1).
\]

The implementation draws this distribution with independent integer-shape
Gamma variables, draws all five sphere directions independently, reconstructs
the real Fourier coefficients, and draws the relative centre from normalized
Haar measure on the transverse torus.  The global translation representative
is fixed as \(Q_2=0,\ Q_1=Q_{\rm rel}\).

## Validity and retained mass

The audit cell uses a registered analytic, time-uniform upper bound on both
\(\|Y_i'\|\) and \(\|\dot Y_i\|\), together with \(k_{\max}\ell_s\).  This is
a conservative software-and-measure audit predicate.  Every failing sample is
stored as `source_invalid`; no valid replacement is drawn.  Named per-sample
PRNG substreams ensure that changing the validity predicate cannot move later
samples in the stream.

The report stores aggregates and source-state fingerprints, not a conditioned
population.  Its JSON replay is type-strict, rejects duplicate keys and
non-finite numbers, and compares semantic content independently of LF/CRLF
checkout conversion.

## Scope boundary

This package closes only the finite-\(K\), quadratic, graph-sector source
sampler for the frozen zero-\(\pi_i\) audit cell.  It does not establish:

- a unique cosmological or quantum F1 preparation;
- source validity of the quadratic graph approximation;
- exhaustive first-entry root coverage;
- physical regular or exceptional event masses;
- an encounter-rank or singular-value distribution;
- a continuum limit, \(3+1\) selection, cone, signature or time direction.

Nonzero world-sheet momentum has the different radial density

\[
p(s_0,s_1,s_2)\propto
s_0^3\prod_i
\left(\frac{s_i^2-\pi_i^2}{4}\right)^{8K-1}
\delta(s_0+s_1+s_2-E_*),
\]

with \(s_i\ge|\pi_i|\) and strict regular-shell condition
\(E_*>|\pi_1|+|\pi_2|\).  It is recorded as a later source family and is not
implemented here.
