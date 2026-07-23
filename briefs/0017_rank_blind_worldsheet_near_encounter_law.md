---
brief: 0017
branch: brief-0017
status: repaired_inconclusive
artifacts:
  - artifacts/0017/probe_0017.py
  - artifacts/0017/test_probe_0017.py
  - artifacts/0017/analytic_controls.json
response: responses/0017_rank_blind_worldsheet_near_encounter_law.md
---

# Brief 0017 — rank-blind finite-K world-sheet near-encounter law

## Verdict and claim boundary

The physical verdict is **inconclusive**. This brief does not claim that the
finite-\(K\) physical first-entry law, the event-conditioned \(\sigma _3\) law, or a
3+1-dimensional selection effect has been computed.

The repaired bundle has four distinct claim classes:

1. **Exact analytic controls:** algebraic identities and declared Gaussian,
   affine, Fourier, and quadratic-flow surrogate facts.
2. **Conditional propositions:** Palm exponent transfer, the curvature-lifted
   local counterexample, and Borel/normalization statements only after their
   hypotheses and total-map contracts are supplied.
3. **Schematic event semantics:** executable hostile registry and synthetic
   geometry probes. Their case counts are not physical probabilities.
4. **Open physical gates:** a frozen source cell, total physical event schema,
   constrained sampler, and exhaustive certified first-entry solver.

No exceptional record may be redrawn, deleted, rank-filtered, or removed before
normalization.

## 1. Parameterized finite-mode source

Let the transverse graph fields be

\[
X_i^\perp(t,\sigma_i)=Q_i+Y_i(t,\sigma_i),
\]

with \(Y_i\) containing only nonzero Fourier modes. Let \(y\) collect velocity
and oscillator coefficients and let \(Q_{\rm rel}=Q_1-Q_2\) be uniform on the
transverse torus. For frozen cell data \(h\), constraints \(C(y)=c_h\), and
normalization \(Z_h\), the principal preparation is the single normalized
constraint law

\[
 d\mu_{E,K,h}=Z_h^{-1}
 \frac{d^8Q_{\rm rel}}{\operatorname{Vol}(T^8_\perp)}
 \delta(C(y)-c_h)\,dy.
\]

On regular coarea branches \(\Gamma_r\), write

\[
 d\nu_r=\frac{d^8Q_{\rm rel}}{\operatorname{Vol}(T^8_\perp)}
 \frac{d\mathcal H^{N-11}(y)}
 {\sqrt{\det(DC(y)DC(y)^T)}}.
\]

The principal branch weights are fixed by coarea volume:

\[
\boxed{\omega_r=\frac{\nu_r(\Gamma_r)}{\sum_s\nu_s(\Gamma_s)}},
\qquad \omega_r\ge0,\qquad \sum_r\omega_r=1.
\]

An arbitrary mixture is not the principal law. It must be separately named as
a preparation control. The executable \((2,3,5)\mapsto(1/5,3/10,1/2)\) example
checks normalization only; it does not estimate physical branch volumes.

No concrete \(h\) is frozen here. This remains a parameterized family and
cannot close the physical gate or be called the preregistered finite-\(K\)
theorem.

### Constraint singularity is not source invalidity

Loss of rank of \(DC\) is not silently relabelled `source_invalid`. Until a
stratified measure is supplied, the distinct primary outcome is
`source_constraint_unresolved`; source-invalid, censoring, tie, and geometry
facts remain flags. `source_invalid` is reserved for a frozen validity contract
such as a registered graph or ultraviolet bound.

## 2. Fourier convention

At \(t=0\),

\[
Y_i^A(0,\sigma_i)=\sum_{n=1}^K
 (x_{in}^A\cos k_n\sigma_i+y_{in}^A\sin k_n\sigma_i),
\]

\[
\dot Y_i^A(0,\sigma_i)=V_i^A+\sum_{n=1}^K
 (p_{in}^A\cos k_n\sigma_i+q_{in}^A\sin k_n\sigma_i).
\]

Thus \(Q_i\) occurs exactly once, in \(X_i^\perp=Q_i+Y_i\). For
\(Y_n=c_n^Le^{ik_n(\sigma-t)}+c_n^Re^{ik_n(\sigma+t)}+\mathrm{c.c.}\), use

\[
c_n^L=\tfrac14[x_n+q_n/k_n+i(p_n/k_n-y_n)],\qquad
c_n^R=\tfrac14[x_n-q_n/k_n-i(y_n+p_n/k_n)].
\]

The probe performs the inverse round trip and rejects a second addition of
\(Q_i\).

## 3. Total event schema

### Hysteretic episodes

For the global torus minimum \(\rho(t)\), an armed history enters when
\(\rho\le r_{\rm in}\), remains active while \(\rho<r_{\rm out}\), and rearms
only after global outer exit. Every component subentry before that exit is
merged into one episode. Initial active mass is left-censored; an unfinished
entered episode is right-censored active; finite-window nonobservation is
right-censored no-entry unless a complete search or lower bound proves no
entry.

### Equivariant tie policy

Emit the complete unordered certified minimizer cluster and no scalar
representative. Canonical sorting is serialization only, not a physical winner.
The same full-cluster rule is used under string exchange, residual world-sheet
reparametrization, and torus relabelling.

### One primary outcome plus orthogonal flags

Use the following deterministic high-to-low precedence:

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

Every record has one primary outcome and retains all lower-priority facts as
flags. This resolves source-invalid/censored overlap and degenerate/grazing/tie
overlap without deleting mass. The synthetic twelve-case coverage ledger is a
registry test, not the false equal-\(1/12\) physical ledger.

A normalized Borel pushforward is only a conditional proposition: it follows
once a normalized source, torus/history/tie/censoring contracts, and a certified
total solver are actually implemented as Borel operations. Those physical
contracts are not yet complete.

## 4. Entry marks, rank strata, and near-degeneracy

At entry, decompose the separation \(s=b+\ell\), with \(b\) in the normal
fiber and \(\ell\) in the derivative span. Therefore \(b=s\) is not assumed at
first entry. At full closest stationarity, \(\ell=0\) and \(b=s\).

For the opposite-winding Jacobian \(J\), the exact control certifies

\[
\det(J^TJ)=|q\wedge u|^2+|p_1\wedge q\wedge u|^2.
\]

Rank is not preregistered. Straight opposite winding, \(q=0\),
\(u\parallel q\), and full-rank examples are all retained. The normal dimension
is \(9-\operatorname{rank}J\), so the fixed-six mutation fails on rank-two
geometry.

The record separates:

- `exact_rank`, certified with exact rational Gram determinants/minors;
- `singular_values_raw`, never thresholded or overwritten;
- `numerical_rank`, using the recorded tolerance
  \(10^{-14}\sigma_1\).

The exact-rank-three hostile sequence includes
\(q=10^{-8}e_1,10^{-12}e_1,10^{-16}e_1\), \(u=e_2\). The first two remain
numerical rank three with positive \(\sigma_3\); the final case is numerical
rank two but keeps its positive raw \(\sigma_3\). The Gram identity is certified
exactly; the floating comparison is reported separately.

## 5. Executed controls versus open controls

The probe genuinely executes:

- strict vector shape/type rejection, including \(\mathbb R^8\) versus length 7;
- duplicate-key and nonfinite JSON rejection and type-strict semantic equality;
- coarea-weight normalization and a separately named mixture control;
- Fourier round trip and double-\(Q\) mutation;
- exact-rank hostile sequences and the fixed-six projector mutation;
- global hysteresis, component merger, outer-exit rearm, and censoring examples;
- full-cluster tie serialization and primary precedence overlaps;
- rank/\(\sigma_3\) dependency mutations; and
- quadratic finite-mode energy and world-sheet momentum invariants.

These remain schematic controls where no constrained source sample and no
exhaustive physical root geometry is supplied. The probe never labels a missing
physical control as executed.

## 6. Analytic surrogate facts

These facts are valid only for their declared controls:

\[
\Pr[s_{\min}(B)\le\varepsilon]
 \sim \frac{\sqrt{\pi/2}}{48}\varepsilon^7,
\qquad B\in\mathbb R^{8\times2}\text{ iid Gaussian},
\]

\[
\Pr[\lambda_{\min}(B^TB)\le x]
 \sim \frac{\sqrt{\pi/2}}{48}x^{7/2},
\]

and, for the pure affine incoming-volume Palm control with no survival tilt,

\[
\Pr_{\rm vol}[s_{\min}\le\varepsilon]
 \sim \frac{1}{105}\varepsilon^8.
\]

The affine control executes \(\delta^2\), \(\delta^{-1}\), and \(\delta\)
scaling. The curvature-lifted model supplies a conditional local
closest-stationary exponent-six counterexample, not a physical first-entry law.

The numerical tail audit uses 70-digit `Decimal`, the relative-scale change
\(y=\varepsilon^2x^2\), composite Simpson refinement from 8192 to 16384
intervals, and Richardson error \(|I_{2N}-I_N|/15\). At \(\varepsilon=0.05\),

```text
fixed-point normalized ratio  0.9987507809245811
volume-Palm normalized ratio  0.9987507809245810
```

with estimates below \(1.3\times10^{-16}\). The inaccurate
`0.9985753405` value is removed.

None of these exponents or coefficients is transferred to the constrained,
hysteretic finite-\(K\) physical preparation without its density, Jacobian,
section, history, survival, and no-earlier-entry calculation.

## 7. Literature boundary and metadata

The source roles are:

- Sakellariadou, *Numerical experiments on string cosmology*, Nucl. Phys. B 468
  (1996) 319–335, arXiv:hep-th/9511075,
  DOI:10.1016/0550-3213(96)00123-X: lattice evolution/reconnection, not a
  continuous first-entry law.
- Mitchell–Turok, *Statistical Properties of Cosmic Strings*, Nucl. Phys. B 294
  (1987) 1138–1163, DOI:10.1016/0550-3213(87)90626-2; Deo–Jain–Tan,
  *String distributions above the Hagedorn energy density*, Phys. Rev. D 40
  (1989) 2626–2635, DOI:10.1103/PhysRevD.40.2626; and Mañes, *String Form
  Factors*, JHEP 01 (2004) 033, DOI:10.1088/1126-6708/2004/01/033, plus
  *Portrait of the String as a Random Walk*, JHEP 03 (2005) 070,
  DOI:10.1088/1126-6708/2005/03/070: distinct statistical,
  microcanonical/state-distribution, and state-average precedents.
- Easther–Greene–Jackson–Kabat, *String Windings in the Early Universe*, JCAP
  02 (2005) 009, DOI:10.1088/1475-7516/2005/02/009: homogeneous
  background/thermodynamic initial-data ensemble, not a loop-embedding prior.
- Greene–Kabat–Marnerides, *Dynamical Decompactification and Three Large
  Dimensions*, Phys. Rev. D 82 (2010) 043528,
  DOI:10.1103/PhysRevD.82.043528: isotropy/even-distribution simulation
  prescription for impact parameters, not a return theorem.
- Jackson–Jones–Polchinski, *Collisions of Cosmic F- and D-strings*, JHEP 10
  (2005) 013, DOI:10.1088/1126-6708/2005/10/013: reaction probabilities
  conditional on an already specified local collision.
- Edelman, *Eigenvalues and Condition Numbers of Random Matrices*, SIAM J.
  Matrix Anal. Appl. 9 (1988) 543–560, DOI:10.1137/0609045, is the primary
  Gaussian/Wishart control source. Kac, *On the Average Number of Real Roots of
  a Random Algebraic Equation*, DOI:10.1090/S0002-9904-1943-07912-8, and Rice,
  *Mathematical Analysis of Random Noise*,
  DOI:10.1002/j.1538-7305.1944.tb00874.x, are primary root/crossing sources.

None supplies the missing normalized constrained source plus total first-entry
law.

## 8. Acceptance commands

Run from the repository root:

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

Acceptance requires five zero exit statuses, `--check` reporting the
canonical semantic match, and `Ran 12 tests` followed by `OK`.

## 9. Earliest open gate

Freeze a valid principal source measure and the total event schema first,
including constraint-singular, invalid, censored, ambiguous, unresolved, tied,
grazing, degenerate, lower-rank, no-entry, and regular mass. Then implement the
constrained sampler and a certified exhaustive hysteretic first-entry root
solver. Until that sequence is completed, the physical finite-\(K\) law and
3+1 selection remain **not computed**.
