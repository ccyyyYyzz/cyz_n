# Brief 0017 analytic tail controls

This directory contains deterministic, standard-library controls for the
fixed-point \(8\times2\) Gaussian pair jet and several local event-geometry
identities used by Brief 0017.

Run from the repository root:

```text
python artifacts/0017/analytic_tail_controls.py
python artifacts/0017/analytic_tail_controls.py --check
python -m unittest discover -s artifacts/0017 -p "test_*.py" -v
```

The first command writes `artifacts/0017/analytic_tail_controls.json`.  The
second regenerates the report and compares parsed JSON objects, rather than
raw bytes, so an LF/CRLF checkout conversion does not change the result.  The
comparison is type-strict, so a hostile `true` to `1` mutation is rejected
even though ordinary Python equality conflates them.  Duplicate JSON object
keys are also rejected rather than silently collapsed.  The reported
SHA-256 is over the canonical UTF-8/LF serialization.

## What is checked

For a fixed material pair and fixed time, with
\(B=[q,u]\in\mathbb R^{8\times2}\) having iid \(N(0,1)\) entries, the
artifact evaluates the ordered two-eigenvalue Wishart integral and verifies

\[
\Pr[\sigma_{\min}(B)\le\varepsilon]
\sim \frac{\sqrt{\pi/2}}{48}\varepsilon^7,
\]

while

\[
\Pr[\lambda_{\min}(B^\top B)\le x]
\sim \frac{\sqrt{\pi/2}}{48}x^{7/2}.
\]

It separately checks the declared volume-biased surrogate

\[
dP_\wedge(B)
=\frac{\sqrt{\det(B^\top B)}}{
  E\sqrt{\det(B^\top B)}}\,dP(B),
\]

for which

\[
\Pr_\wedge[\sigma_{\min}(B)\le\varepsilon]
\sim \frac{1}{105}\varepsilon^8.
\]

The integrals use closed forms for integer and half-integer upper incomplete
gamma functions plus deterministic converged Simpson quadrature.  No
third-party package or random sampling is used.

The geometry controls also verify:

- the affine closest-event scaling
  `Hessian determinant ~ delta^2`,
  `constraint-zero density ~ delta^-1`, and hence complete local
  `Kac-Rice weight ~ delta`;
- a conditional curvature-lifted closest-event counterexample in which the
  Morse determinant has a positive limit and the local effective scale is
  `delta^-1`;
- the opposite-winding identity
  \[
  \det(J^\top J)
  =|q\wedge u|^2+|p_1\wedge q\wedge u|^2;
  \]
- the exact straight \(p_1=p_2=0\) rank-2 control, an excited but
  \(q=p_1+p_2=0\) rank-2 control, and an exact-rank-3 sequence approaching
  the degeneracy with \(\sigma_{\min}\) linear in its perturbation;
- first-entry bundle data with \(b=P_Ns\) and a nonzero longitudinal phase
  \(\ell=s-b\), versus an interior closest approach with \(b=s\) and
  \(\ell=0\);
- a unique curved strict minimum whose first derivative has rank two.

## Event-law boundary

The coefficient \(1/105\) belongs to the explicitly declared pure
volume-biased control.  It corresponds to a local affine, uniform-translation
stationary-root calculation only after the complete Kac-Rice factors have
been included.  A complete event weight must contain, exactly once,

\[
p_g(0),\quad |\det Dg|,\quad
\mathbf 1_{\rm Morse/inward},\quad
A_{\rm no\ earlier},
\]

as well as any impact-window or episode-selection factor.

The curvature control is only a conditional local closest-event
counterexample.  It is not a first-entry theorem and is not a prediction for
a physical world-sheet ensemble.

This artifact does **not** implement or establish:

- a finite-\(K\) Nambu--Goto/world-sheet sampler;
- coverage, uniqueness, or tie handling for all physical event roots;
- a physical first-entry, closest-event, or Palm law;
- no-earlier, hysteresis, or episode-selection dynamics;
- a cutoff-uniform tail theorem;
- a positive physical singular-value margin;
- response-visible rank three or a \(3+1\) signature.
