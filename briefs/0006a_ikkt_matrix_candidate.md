# Brief 0006a — Critical addendum: Lorentzian IKKT matrix candidate

Status: active addendum to brief 0006

## Why this addendum exists

The mechanism screen found a materially stronger live candidate after brief
0006 was opened.  Do not finalize the mechanism decision without comparing the
Lorentzian type-IIB/IKKT matrix model against the same operational selection
theorem.  This addendum supersedes only the phrase "exactly these three
routes"; compactification, Brandenberger--Vafa and graph dynamics remain
mandatory controls.

Primary sources to inspect are:

1. Kim, Nishimura and Tsuchiya, arXiv:1108.1540, the original Monte Carlo
   report of SO(9) breaking to SO(3);
2. Nishimura and Tsuchiya, arXiv:1904.05919, the complex-Langevin repair of the
   earlier Pauli-matrix artifact;
3. Hirasawa et al., arXiv:2307.01681, the Lorentz-invariant mass-regulated
   Lorentzian phase;
4. Anagnostopoulos et al., arXiv:2604.19836v1 (21 April 2026), the new
   deformed-model simulations up to N=128 reporting a smooth, real expanding
   3+1 phase.

Use the papers themselves, not press summaries.

## Exact facts already checked in the 2026 source

The following are not reviewer conjectures; they are stated in
arXiv:2604.19836v1 and must constrain the verdict.

- The microscopic action has (A_\mu), \(\mu=0,\ldots,9\), and explicitly
  raises indices with \(\eta=\mathrm{diag}(-1,1,\ldots,1)\).  A 9+1
  Lorentz representation is therefore input even if matrix eigenvalues and
  their locality are emergent.
- The authors show a contour-deformation equivalence of the undeformed
  \(\gamma=0\) Lorentzian and Euclidean models and state that this prevents a
  Lorentzian emergent spacetime in that definition.  They introduce
  \(\gamma>0\) and propose the ordered limit (N\to\infty) followed by
  \(\gamma\to0\); persistence of the reported phase along that limit is not
  demonstrated.
- The displayed 3+1 run is at (N=128,\gamma=4,m_f=6,\tilde d=5,\xi=12\).
  The anisotropic bosonic mass term explicitly breaks SO(9,1) to SO(5,1),
  although the further SO(5) to SO(3) breaking is dynamical.
- Its initial configuration is thermalized first in a bosonic
  \(\tilde d=3,\xi=10\) model.  The paper says that a random initial
  configuration instead gives behavior similar to the nonbreaking
  (m_f=10\) case, and that complex Langevin cannot determine the dominant
  saddle point.  This fails the present open-basin/attraction criterion.
- The Lorentz-boost removal used in the analysis is acknowledged not to be
  fully justified because it breaks the holomorphicity needed by complex
  Langevin.  Faddeev--Popov gauge fixing and Lefschetz-thimble dominance are
  left for future work.

Thus the April 2026 result is a serious mechanism lead, but it is not yet
evidence of an untuned attractive 3+1 basin under this project's definition.

## Questions that decide whether it outranks BV

1. Separate what the ten matrix labels and the Lorentzian contraction already
   encode from what the dynamics actually selects.  In particular, does the
   model select three expanding spatial directions only, or a full
   response-visible one-time 3+1 package?
2. State the exact order parameter used for SO(9) to SO(3), and determine
   whether it establishes an open large-N phase or only one finite-N parameter
   point/history.
3. Audit every deformation, regulator, Lorentz-frame post-processing step and
   complex-Langevin validity criterion.  Is there a controlled path toward the
   undeformed supersymmetric model on which the 3+1 phase persists?
4. Determine whether independent fluctuation/probe sectors on the emergent
   blocks have a common Lorentzian principal cone.  A moment-of-inertia tensor
   with three large eigenvalues is not the operational object O_lambda.
5. Give the smallest honest response interface from matrix configurations to
   anonymous source-response records.  If no cited theorem supplies it, label
   it implementation architecture and specify the missing theorem.
6. Identify a scale/deformation/finite-N departure predicted by the same
   mechanism rather than appended after the fact.

## Mandatory kill tests

Kill the present model as the primary route if any one of the following cannot
be repaired:

- SO(3) expansion disappears when the singular-drift deformation/regulator is
  removed along a controlled large-N path;
- the result is not stable on an open parameter and initial-state basin;
- only an extent or spectral order parameter is three-dimensional while the
  response-derived cotangent/common-cone/time package abstains;
- the probe dynamics needs a 3+1 kinetic term inserted by hand;
- different fluctuation sectors have inequivalent characteristic cones;
- no measurable response-level crossover follows from the matrix parameters.

## Requested change to response 0006

Add IKKT as a fourth row in the mechanism evidence table.  Then choose among
BV, IKKT, a genuinely dimension-blind new graph model, or the honest verdict
that none presently passes.  Freshness or prestige is not evidence: the
decision must be made by the same non-encoding, open-basin, common-cone and
departure criteria used everywhere else in the project.
