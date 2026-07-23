# Brief 0011 — sharpen or retract the all-rank no-go

Status: active

Baseline commit: `2555a8190687c1f597d8dba832c0f99377a1e35d`.

## Role

Act as the originating mathematical physicist.  Do not write a referee report
and do not defend the wording of Response 0010.  Preserve its valid mechanism,
then replace the overstrong theorem by the strongest statement that is actually
proved.

Read, in order:

1. `state/PROJECT_STATE.md`;
2. `responses/0010_exchangeable_all_rank_selection_gate.md`;
3. `decisions/0010_adopt_local_underdetermination_not_sharp_winner_nogo.md`;
4. this brief.

The project remains one closed loop.  Do not discuss journals or divide the
program into papers.

## The central fork

End with exactly one of the following.

1. **Sharp global no-go.**  Exhibit at least two explicit completions inside
   one precisely defined source-compatible winding--geometry family, with the
   same fixed rank-unconditioned initial law, ports, band and error model, such
   that the fully replayed three-margin has opposite signs or one completion
   has a certified non-three winner.  Prove a finite parameter path or
   enclosure connecting the relevant cells.
2. **Exact local underdetermination only.**  State a label-stable Duhamel
   theorem showing that one or more scores are not identified, explicitly
   acknowledge that this alone does not prove winner reversal, and retract the
   phrases `sharp all-rank no-go`, `every rank can win`, and `smallest missing
   object`.

Do not choose branch 1 merely by assuming the conclusion in a generic
"entry enhancement / exit suppression" clause.  If those controls are used,
write the finite graph, finite time horizon, initial-support condition,
absolute rate bounds, communicating-class exclusions and response replay that
make the statement true.

## Repair the response-dependent cells

The cells satisfy

\[
Z_k=Z_k(Q,\mathbb Q,I,\text{ports},\text{band},\text{errors}).
\]

For a local derivative theorem, restrict to an explicitly certified
label-stable neighborhood and prove that \(P_k\) is constant there.  For a
global completion comparison, recompute the anonymous relation/Green
classifier for every completion.  Do not differentiate \(e^{tQ}\) while
silently freezing a projector that depends on \(Q\).

## Keep the initial-law family consistent

Choose one of the following and use it throughout:

- one fixed, independently declared product/exchangeable law;
- the factorized family in Response 0010; or
- the full class of exchangeable laws.

An exponential tilt by an arbitrary orbit function generally leaves the
factorized family.  Do not use such a tilt unless the declared family permits
it.  Every claimed change also needs positive support and a nonzero covariance
condition.  Initial-measure bias must be separated from dynamical attraction.

## Close the finite operator or narrow the claim

1. Make the numerical residual state genuinely finite.  Define an exact
   reachable closure with a jump counter, a validated bin/interval transition,
   or a rule sending every unrepresented residual value to the cemetery.
2. Fix the orientation of the augmented operator.  Under the row convention
   for \(Q\), its column probability channel is \(Q^T\).  Define every reset map
   with an unambiguous source and target index.
3. Give finite input matrices and normalization/covariance rules for
   \(A_x,R_{xy},B,C,M\), or explicitly call the construction an architecture
   rather than a complete executable.
4. Define local response neighborhoods independently of the output rank, so
   that the definition of \(Z_m\) is not circular.
5. Return `undefined_empty_cell` for conditional or worst leakage when
   \(Z_m\) is empty.

## Separate continuum and finite probability theorems

Retain the corrected two-stage continuum recollapse lemma.  For the finite
upwind CTMC, compute geometry first-passage from the same finite \(Q\) or add a
validated semigroup-to-event error.  The finite probability bound must include
this geometry-hitting failure.  Define every annihilation buffer count as a
uniform minimum over the whole stopped tube.  A random response-cell survival
event must have its own killed probability rather than appearing as an
unpriced assumption.

## Correct the controls

1. Exchangeability of a law is not pathwise equality.  Treat the EGJK
   all-or-nothing diagonal statement as a deterministic mean-flow control, or
   define a separate synchronized-jump generator.
2. Keep the equal-hazard binomial chain as an abstract symmetry control unless
   you explicitly embed it into the winding--geometry generator and response
   reconstruction.
3. Re-run the same constitutive law for \(m=2,3,4\).  An \(S_9\)-invariant
   orbit parameter may still hide a cardinality-three branch, so static
   non-encoding requires provenance and variables fixed before the classifier.

## The missing physical object

The complete reachable orbit-rate ledger is a sufficient finite specification,
not automatically a minimal one.  Either prove a genuine minimal sufficient
quotient for the winner ordering, or use the words `complete sufficient
specification`.

The continuum completion must include the normalized recollision-time and
impact-mark kernel, absolute frequency, non-Gaussian/history dependence,
reverse channels and the exchangeable initial law.  The Gaussian determinant
formula is a useful special case, but \(\Sigma^\perp\) alone does not close the
generator.

The proposed law is non-target-keyed only if it is derived or measured before
the output ranks and depends exclusively on predeclared local geometric,
worldsheet and impact invariants.  Permutation invariance by itself is not
enough.

## Required delivery

Write the full result to
`responses/0011_sharpen_or_retract_the_all_rank_nogo.md`, commit it, and push
directly to `main`.  Do not open a pull request, offer a download, or leave the
result only in chat.
