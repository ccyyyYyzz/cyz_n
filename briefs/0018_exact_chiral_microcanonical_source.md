# Brief 0018 — exact chiral microcanonical source and total event contract

Status: active

Baseline commit: `7b3e1ed700f8e9b5de017c85b23a30e111df8419`.

## Role

Act as the originating mathematical physicist and computational co-theorist.
Close the source-measure gate that remained open in Brief 0017.  Do not act as
a referee, optimize a paper, or infer visible \(3+1\) from a source sampler.

Read, in order:

1. `state/PROJECT_STATE.md`;
2. `briefs/0017_rank_blind_worldsheet_near_encounter_law.md`;
3. `responses/0017_rank_blind_worldsheet_near_encounter_law.md`;
4. `artifacts/0017/README.md`;
5. this brief.

Use only primary sources for physical claims.  Label every result as one of:

- `exact theorem of the registered finite-K source`;
- `exact analytic control`;
- `controlled numerical verification`;
- `new measurable contract`;
- `open physical gate`;
- `no-go/underdetermination`.

## Governing correction

The principal preparation in Brief 0017 is one normalized ambient
delta--Liouville measure.  It is not an arbitrary mixture of normalized
constraint branches.  If regular branches are ever separated, their weights
are fixed by their coarea masses:

\[
\omega_r=
\frac{\nu_r(\Sigma_r)}
{\sum_s\nu_s(\Sigma_s)}.
\]

Any other branch mixture is a separately named preparation control.

For the zero level-matching cell

\[
\pi_1=\pi_2=0,\qquad K\ge1,\qquad E_*>0,
\]

the regular constrained shell is connected up to zero-measure singular
boundaries.  It admits a direct exact sampler.  No MCMC, tolerance
conditioning, rejection-to-level-match, or rank filtering is needed.

This round must also freeze a total event-record contract before the certified
root solver is implemented.  A source sample must have exactly one mutually
exclusive primary outcome, while simultaneous exceptional properties are
stored as orthogonal flags and complete clusters.

## Goal

Derive, implement and independently audit:

1. the exact chiral-coordinate reduction of the principal finite-\(K\)
   microcanonical source;
2. a direct normalized sampler at \(\pi_1=\pi_2=0\);
3. a frozen computational audit cell, explicitly not promoted to a unique
   early-universe preparation;
4. a versioned, total, rank-blind event-record schema;
5. the precise handoff contract for a certified exhaustive hysteretic
   first-entry solver.

The decisive source theorem is

\[
\boxed{
\left(\frac{s_0}{E_*},\frac{s_1}{E_*},\frac{s_2}{E_*}\right)
\sim\operatorname{Dirichlet}(4,16K-1,16K-1).
}
\]

The response must derive this law from the registered ambient Liouville
measure.  Merely programming the stated distribution does not prove the
theorem.

## Non-goals

This round does not compute the physical first-entry masses, the
event-conditioned rank mixture, the physical \(\sigma_3\) tail, annihilation
rates, a \(3+1\) basin, a cone, a signature, or a time direction.

The audit cell is not asserted to be the cosmological F1 preparation.
Agreement of source constraints is not evidence that the graph-sector,
quadratic, finite-\(K\) model is a continuum or quantum string ensemble.

Source-validity predicates are outcome labels.  They may not be turned into a
rejection sampler unless the removed mass is printed and the conditioned
preparation is given a different name.

## 1. Registered source and conventions

Use the physical-length convention of Brief 0017:

\[
M=T_FL_w,\qquad k_n=\frac{2\pi n}{L_w},\qquad d=16K .
\]

Keep the transverse centre exactly once:

\[
X_i^\perp=Q_i+Y_i,
\]

\[
Y_i(0,\sigma)=
\sum_{n=1}^{K}
\left(x_{in}\cos k_n\sigma+y_{in}\sin k_n\sigma\right).
\]

The implementation must reject any convention in which \(Q_i\) is also
inserted into \(Y_i\).

The frozen audit registry must include at least:

\[
\left(
L_A,T_F,\ell_s,w,K,E_\perp,P_{\rm tot},
\pi_1,\pi_2,\epsilon_{\rm graph}^*,\kappa_{\rm UV}^*,
r_{\rm in},r_{\rm out},[t_0,t_1),
\text{initial history}
\right).
\]

It must satisfy

\[
0<r_{\rm in}<r_{\rm out}<\operatorname{inj}(T^9),
\qquad
\pi_1=\pi_2=0.
\]

Choose one low-\(K\), exactly serialized audit cell whose units and numerical
values make all transformations reproducible.  State next to it that the
choice is a software-and-measure audit cell, not a physical selection result.

Inside the audit registry, define a separate `source_draw_registry` containing
only

\[
\left(
L_A,T_F,L_w,K,E_\perp,P_{\rm tot},\pi_1,\pi_2,
\text{PRNG and seed convention}
\right).
\]

Only this subregistry may enter source-substream seed derivation.  Event
thresholds, validity thresholds, initial history, solver budgets, rank
tolerances and reaction data belong to other subregistries and must not change
the coefficient stream.

Freeze the ambient Liouville reference measure before changing coordinates:

\[
\frac{dQ_{\rm rel}}{\operatorname{Vol}(T_\perp^8)}
d^8P_1\,d^8P_2
\prod_{i,n,A}
dx\,dy\,d\Pi_x\,d\Pi_y,
\]

multiplied by the energy, eight target-momentum and two world-sheet-momentum
delta constraints.  Do not replace this ambient delta measure by the
unweighted geometric surface area of the constraint shell.

## 2. Chiral whitening theorem

For every \(i,n,A\), use

\[
c^L=\frac14\left[
x+\frac qk+i\left(\frac pk-y\right)
\right],
\]

\[
c^R=\frac14\left[
x-\frac qk-i\left(y+\frac pk\right)
\right].
\]

Publish and test the exact inverse:

\[
\begin{aligned}
x&=2(\Re c^L+\Re c^R),\\
y&=-2(\Im c^L+\Im c^R),\\
p&=2k(\Im c^L-\Im c^R),\\
q&=2k(\Re c^L-\Re c^R).
\end{aligned}
\]

Define

\[
z_{in}^{L,R}=\sqrt{2M}\,k_n c_{in}^{L,R}.
\]

After flattening the \(8K\) complex coefficients of each chirality into
\(\mathbb R^d\), prove

\[
H_{{\rm osc},i}
=\|z_i^L\|^2+\|z_i^R\|^2,
\]

\[
\mathcal P_{\sigma,i}
=\|z_i^R\|^2-\|z_i^L\|^2.
\]

The pure-left and pure-right controls must give

\[
\mathcal P_\sigma=-H_{\rm osc},
\qquad
\mathcal P_\sigma=+H_{\rm osc},
\]

respectively.

With canonical real momenta

\[
\Pi_x=\frac M2p,\qquad \Pi_y=\frac M2q,
\]

derive the constant per-mode, per-real-transverse-component Jacobian

\[
dx\,dy\,d\Pi_x\,d\Pi_y
=\frac4{k_n^2}\,d^2z^L\,d^2z^R.
\]

No state-dependent density correction may be introduced by this linear
change of variables.

## 3. Eliminate total target momentum

Let

\[
P_i=MV_i,\qquad
P_\pm=\frac{P_1\pm P_2}{\sqrt2},
\qquad
w=\frac{P_-}{\sqrt{2M}}.
\]

The total target momentum fixes

\[
P_+=\frac{P_{\rm tot}}{\sqrt2}.
\]

Prove

\[
H_\perp
=\frac{\|P_{\rm tot}\|^2}{4M}
+\|w\|^2
+\sum_{i=1}^{2}
\left(
\|z_i^L\|^2+\|z_i^R\|^2
\right).
\]

Register

\[
\boxed{
E_*=E_\perp-\frac{\|P_{\rm tot}\|^2}{4M}.
}
\]

The regular source exists only for \(E_*>0\):

- \(E_*<0\): the constraint shell is empty;
- \(E_*=0\): the shell is singular and is not silently normalized;
- a straight-string atom at \(E_*=0\), if desired later, is a different
  singular source family.

The inverse zero-mode map is

\[
V_1=\frac{P_{\rm tot}}{2M}+\frac w{\sqrt M},
\qquad
V_2=\frac{P_{\rm tot}}{2M}-\frac w{\sqrt M}.
\]

## 4. Derive and normalize the radial law

Write

\[
s_0=\|w\|^2,\qquad
l_i=\|z_i^L\|^2,\qquad
r_i=\|z_i^R\|^2.
\]

Starting from the single ambient delta measure, reduce

\[
\delta(s_0+l_1+r_1+l_2+r_2-E_*)
\prod_{i=1}^{2}\delta(r_i-l_i)
\,dw\,dz_1^Ldz_1^Rdz_2^Ldz_2^R .
\]

Show explicitly that

\[
dw\propto s_0^3\,ds_0\,d\omega_0
\]

and, after setting \(s_i=l_i+r_i\),

\[
l_i^{d/2-1}r_i^{d/2-1}
\delta(r_i-l_i)\,dl_i\,dr_i
=2^{-(d-1)}s_i^{d-2}\,ds_i .
\]

Therefore the radial density is proportional to

\[
s_0^3s_1^{d-2}s_2^{d-2}
\delta(s_0+s_1+s_2-E_*).
\]

Publish the normalized Dirichlet density, its normalization constant, and an
independent derivation through a hierarchical Beta factorization.  Explain
why using surface area without the delta/coarea factor would give the wrong
shape parameter.

Distinguish the normalized radial density from the complete shell partition
function.  In the canonical convention above, the reduced factor is

\[
Z_{\rm red}(E_*)=
\frac{
2^{2-2d}\pi^{2d+4}\Gamma(d-1)^2
}{
\Gamma(d/2)^4\Gamma(2d+2)
}
E_*^{2d+1},
\]

and the constant from the linear canonical transformation is

\[
J_{\rm lin}
=M^4\prod_{n=1}^{K}
\left(\frac4{k_n^2}\right)^{16}.
\]

If the response reports only the normalized radial law, it must say explicitly
that it is not reporting the convention-dependent complete \(Z_h\).

For scope only, record the nonzero-\(\pi_i\) radial density:

\[
p(s_0,s_1,s_2)\propto
s_0^3
\prod_{i=1}^{2}
\left(
\frac{s_i^2-\pi_i^2}{4}
\right)^{8K-1}
\delta(s_0+s_1+s_2-E_*),
\]

\[
s_i\ge|\pi_i|,
\qquad
E_*>|\pi_1|+|\pi_2|.
\]

Here

\[
l_i=\frac{s_i-\pi_i}{2},
\qquad
r_i=\frac{s_i+\pi_i}{2}.
\]

The equality \(E_*=|\pi_1|+|\pi_2|\) is a singular minimal shell, not a
regular normalizable boundary.  The mutation
\(\pi_i\mapsto-\pi_i\) must exchange the left and right chiral factors.

Do not implement this extension by pretending it is still Dirichlet.

## 5. Exact direct sampler

The authoritative sampler is:

1. draw independently
   \[
   G_0\sim\Gamma(4,1),\qquad
   G_1,G_2\sim\Gamma(d-1,1);
   \]
2. set
   \[
   s_j=E_*\frac{G_j}{G_0+G_1+G_2};
   \]
3. draw independent uniform directions
   \[
   u_0\in S^7,\qquad
   u_i^{L,R}\in S^{d-1};
   \]
4. set
   \[
   w=\sqrt{s_0}u_0,\qquad
   z_i^{L,R}=\sqrt{s_i/2}\,u_i^{L,R};
   \]
5. reconstruct \(V_i,c^{L,R},x,y,p,q\);
6. draw \(Q_{\rm rel}\) uniformly on \(T^8_\perp\), independently of all
   oscillator variables.

For trajectory evaluation, fix the global-translation gauge representative

\[
Q_2=0,\qquad Q_1=Q_{\rm rel}.
\]

Do not use a globally ambiguous division-by-two construction on the torus.
An alternative source may instead add an independent common-centre Haar
factor, but it must be registered separately.

Use a declared reproducible PRNG and serialize the seed and algorithm
version.  Numerical pseudorandomness is a controlled implementation of the
ideal random variables, not a proof of their mathematical distribution.

The implementation must never set \(z_i^R=z_i^L\).  Level matching fixes only
their norms; the four chiral directions are independent.

The source coefficient stream may depend only on the `source_draw_registry`.
Changing \(r_{\rm in}\), \(r_{\rm out}\), rank tolerance,
normal dimension, response winner, source-validity threshold, or reaction
parameters must not change the sampled coefficients.

## 6. Source validity without redraw

Evaluate the registered graph and ultraviolet predicates on every sample.
Store at least

\[
\max_i\{\|Y_i'\|_\infty,\|\dot Y_i\|_\infty\},
\qquad
k_{\max}\ell_s.
\]

If the source predicate fails, emit `source_invalid`.  Preserve the
coefficients, seed and violation reasons.  Do not draw a replacement.  Retain
the invalid sample and continue to the next pre-indexed sample; every sample
index consumes exactly one declared draw bundle.

If a validity-conditioned source is reported as a sensitivity control, give
it a distinct preparation name and print both its normalizing mass and the
mass removed from the principal source.

## 7. Total event-record contract

The registered event map may not read encounter rank, singular values, normal
dimension, \(P_N\), impact coordinates, response outputs, or reaction
outcomes when choosing the first-entry section.

### 7.1 Registry failure is not sample mass

An invalid run registry, including

\[
r_{\rm out}\ge\operatorname{inj}(T^9),\qquad
G\not\succ0,\qquad H\not\succ0,\qquad
M\le0,\qquad K<1,\qquad E_*\le0,
\]

prevents construction of the event map.  It is not serialized as
`source_invalid` probability mass.

For the schema version in this round, \(\pi_i\ne0\) is also a registry-level
unsupported-source error.  A later nonzero-\(\pi\) or singular source family
must use its own declared sampler and schema version.

### 7.2 Observation and outer exit

Use a half-open observation window

\[
[t_0,t_1).
\]

For an active episode, a contact with the outer boundary does not re-arm the
process unless the solver verifies that the path actually moves beyond it:

\[
T_{\rm out}
=\inf\{t>T_{\rm in}:\rho(t)>r_{\rm out}\}.
\]

This is the boundary infimum of the open overshoot set.  Record its outward-
rounded boundary interval at \(\rho=r_{\rm out}\), the state immediately after
the boundary, and a post-boundary certificate for \(\rho>r_{\rm out}\).  A
tangent outer touch followed by return remains active.  Re-arm exactly once
only after certified strict overshoot.

A root whose exact time is \(t_1\) belongs to the next continuation window.
After `right_censored_no_entry`, the continuation state remains `armed`.
After `right_censored_active_episode`, it remains `active` and carries the
certified entry record and partial episode history.

While active, every new outer-tube component and every additional inner
contact belongs to the same pair-level episode.  Merges, splits and secondary
inner contacts are marks only.  No new \(T_{\rm in}\) is eligible until strict
outer exit and re-arming.  Component-lineage records must store birth, merge,
split and disappearance intervals together with their certificate
references.

### 7.3 Mutually exclusive primary outcomes

Use the following deterministic precedence:

1. `source_invalid`;
2. `left_censored_active_episode`;
3. `torus_branch_ambiguous`;
4. `ambiguous_tie`, only when root coverage is complete, every candidate is
   isolated, and the only remaining uncertainty is exact equality versus
   ordering within the earliest cluster;
5. `numerically_unresolved`, for every other missing mandatory certificate;
6. if no entry:
   - `no_entry_proved`, only with a complete period or global lower bound;
   - otherwise `right_censored_no_entry`, after complete finite-window
     exclusion;
7. if entry occurred, the trajectory through \(t_1\) was completely
   certified, but no verified outer exit occurred before \(t_1\):
   `right_censored_active_episode`;
8. after a completed episode:
   - `tie_cluster` for a non-singleton complete earliest cluster;
   - `degenerate_spatial_minimum` for a certified global singleton minimum
     with
     \[
     H_{\sigma\sigma}\succeq0,\qquad
     \det H_{\sigma\sigma}=0;
     \]
   - `grazing_entry` for a singleton Morse contact with an exact symbolic,
     algebraic or interval-multiplicity certificate for
     \(\partial_tF=0\);
   - `regular_first_entry` for a singleton Morse inward contact with
     \(\partial_tF<0\).

Failure to prove positive definiteness is not a degeneracy certificate, and
an interval merely containing zero is not a grazing certificate.  A purported
first hit with \(\partial_tF>0\), or a purported global minimum with
indefinite spatial Hessian, is a logical/certificate failure and therefore
`numerically_unresolved`.

This primary outcome is exactly one value.  Simultaneous properties do not
create multiple probability rows.

### 7.4 Orthogonal flags and clusters

Define a versioned flag schema containing at least:

- source/history validity;
- initial armed/active state;
- left and right censoring;
- root-coverage, global-minimum and no-earlier-entry certificates;
- torus-log uniqueness;
- entry observed, tied, positive-dimensional, regular, grazing and
  spatial-degenerate flags;
- outer exit, outer grazing, episode completion and re-arming;
- closest-episode versus window-only status;
- component merger, split and topology-unresolved flags;
- rank and normal-mark completeness;
- finite-window versus complete-time-domain no-entry certification.

The authoritative tie output is the complete unordered minimizer cluster.
Do not choose a lexicographic world-sheet representative.  JSON ordering is
serialization only and has no physical meaning.

Finite clusters may enumerate all certified members.  A
positive-dimensional cluster must instead serialize either a certified finite
union of interval/set components or a replayable implicit-set certificate.  If
neither representation is available, the primary outcome is
`numerically_unresolved`, with the positive-dimensional candidate flag and
all surviving boxes retained.

Each finite-cluster representative must store:

- interval boxes for \((\sigma_1,\sigma_2,t)\);
- torus image and logarithm certificate;
- \(s,F,\nabla_\sigma F,\partial_tF,H_{\sigma\sigma}\);
- \(J,G,H\);
- raw interval singular values and exact/numerical rank status;
- \(P_N\) and an optional gauge-dependent normal frame when rank is certified;
- \(b=P_Ns\) and \(\ell=s-b\) when the authoritative projector is certified;
- all solver-certificate references.

For a finite tie cluster, every member keeps its own jet, rank and normal
object.  A positive-dimensional or implicit cluster instead stores defining
equations, a certified compact enclosure, dimension/cardinality status and a
certified jet-field enclosure.  There is no scalar cluster representative or
rank unless a separate measurable equivariant kernel is registered.

If rank is unresolved, store raw singular-value intervals and
`possible_ranks`.  Do not serialize an authoritative scalar normal dimension,
normal frame, \(P_N,b\), or \(\ell\) unless the schema explicitly supplies a
certified set-valued enclosure.  Every certified normal record must declare
its coordinate basis and units and verify

\[
P_N^2=P_N,\qquad
P_N^\top G=GP_N,\qquad
P_N=NN^\top G,\qquad
N^\top GN=I,
\]

\[
J^\top Gb=0,\qquad
s=b+\ell.
\]

The projector or subspace is authoritative under symmetry tests; raw entries
of a gauge-dependent normal frame are not.

### 7.5 Total measurable map

Let \(\mathfrak E_h^\star\) be the ideal geometric and censoring outcome
space.  Distinguish:

\[
\Psi_h^\star:\Omega_h\to\mathfrak E_h^\star
\]

for the ideal mathematical event map, and

\[
\Psi_{h,B}^{\rm cert}:
\Omega_h\to
\mathfrak E_h^\star
\sqcup
\{\texttt{ambiguous_tie},\texttt{numerically_unresolved}\}
\]

for a deterministic solver with preregistered operation, precision,
subdivision and memory budgets \(B\).

Do not use a wall-clock timeout as event semantics.

Prove Borel measurability assuming:

- \(\Omega_h\) is standard Borel;
- source-validity and history predicates are Borel;
- below the injectivity radius, each of finitely many logarithm/image branches
  has continuous \(F\);
- the label torus and finite observation window are compact;
- the argmin correspondence is compact valued with Borel graph;
- entry is a Borel closed-set hitting time and outer exit is a Borel open-set
  hitting time;
- the certified algorithm has a deterministic finite operation budget.

Use the compact hyperspace for cluster-valued outputs; do not assume a
symmetry-breaking scalar selector.  Finite-horizon measurability alone does
not establish the all-time `no_entry_proved` branch; exact recurrence and
global-bound certificates require their own measurable predicates.

## 8. Certified-root handoff

Fix one smooth torus-image branch \(n\), write its separation as

\[
s_n=d-\Lambda n,
\qquad
F_n=\frac12s_n^\top Gs_n,
\]

and order variables as \((\sigma_1,\sigma_2,t)\).  For
\(r\in\{r_{\rm in},r_{\rm out}\}\), define

\[
g_{r,n}
=
\left(
F_{n,\sigma_1},
F_{n,\sigma_2},
F_n-r^2/2
\right).
\]

At a root of \(g_{r,n}\),

\[
Dg_{r,n}
=
\begin{pmatrix}
F_{11}&F_{12}&F_{1t}\\
F_{21}&F_{22}&F_{2t}\\
0&0&F_t
\end{pmatrix},
\]

\[
\boxed{
\det Dg_{r,n}
=
F_t\det H_{\sigma\sigma}.
}
\]

Thus spatial Morse regularity with nonzero flux makes the branchwise root
simple.  Simple-root regularity guarantees that sufficiently small boxes
admit a uniqueness certificate in principle.  A finite solver may emit
`unique_root` only after verifying

\[
K(B)\subset\operatorname{int}B
\]

for its Krawczyk operator, or an equivalent interval-Newton inclusion.
Failure inside the preregistered deterministic budget remains `unresolved`.

The identity does not directly classify the nonsmooth envelope
\(\min_nF_n\), an unresolved image switch, or a positive-dimensional
minimizer set.  A unique branchwise root is also not yet a first-entry event.
It still requires:

- \(H_{\sigma\sigma}\succ0\);
- global spatial minimality over every compatible image;
- an armed/history certificate;
- direct sublevel exclusion proving no earlier entry;
- flux and one-sided crossing behavior.

For a grazing classification, \(F_t=0\) must be accompanied by global
first-contact and one-sided touch/plateau evidence.

### 8.1 Complete image and box coverage

For every compact search box \(B\), enumerate every image \(n\) satisfying

\[
\left(d(B)-\Lambda n\right)
\cap
\{s:s^\top Gs\le r_{\rm out}^2\}
\ne\varnothing.
\]

For rectangular \(\Lambda=\operatorname{diag}(L_A)\), a coordinate superset
is

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

The shortcut \(c_A=r_{\rm out}\) is valid only for the corresponding unit
metric convention.  Store image-label transformations across world-sheet and
time seams.  Quotient duplicates that are proven to represent the same
physical root, but never merge different roots merely because image
enclosures overlap.

A coverage-tree hash is only an integrity checksum.  The replayable
certificate must also contain:

- an exact rational or dyadic initial box cover;
- a gap-free leaf partition on every branch domain;
- an interval-exclusion witness for every `excluded` leaf;
- a Krawczyk or interval-Newton inclusion for every `unique_root` leaf;
- every `certified_singular_cluster` and its set certificate;
- every `unresolved` leaf and reason code;
- exact inputs, tree topology and input hashes.

Root-time handling must distinguish:

- quotient-equivalent uniqueness neighborhoods: one physical root;
- distinct roots with certified equal time: one complete `tie_cluster`;
- overlapping time intervals without equality/order proof: refine, otherwise
  `ambiguous_tie`.

Any unresolved leaf that can alter the earliest root, a tie, outer exit or
re-arm order promotes the whole sample to `numerically_unresolved` and enters
the population mass ledger.

### 8.2 Episode and closest-approach certificates

An outer-boundary root is not an exit merely because one image branch has
\(F_t>0\).  Prove that the selected contact is the global spatial minimum and
that a right neighborhood satisfies

\[
\rho(t)>r_{\rm out}.
\]

If another simultaneous minimizer remains inside, the pair-level episode has
not exited.

The boundary system \(g_{r,n}=0\) does not produce the episode closest mark.
For a completed episode, exhaustively cover internal roots of

\[
\left(
F_{\sigma_1},F_{\sigma_2},F_t
\right)=0,
\]

check both time endpoints and all image branches, prove globality, and retain
all closest ties.  For a right-censored active episode, report only a
provisional window minimum.

The handoff schema must therefore include:

- nonsmooth envelope and image-switch coverage;
- positive-dimensional and singular-root-set coverage;
- global-minimum and no-earlier-entry certificates;
- root ordering and complete tie clusters;
- outer-exit, component-lineage and re-arm certificates;
- completed-episode closest coverage and censored window minima;
- a dependency audit proving that root selection never reads rank, normal or
  reaction data.

### 8.3 No-entry semantics and backends

In the current wave-speed convention, \(L_w\) is a common oscillator period.
A complete separation recurrence requires exact integers with

\[
P=mL_w,\qquad
(V_1-V_2)P\in\Lambda_\perp,
\qquad m\in\mathbb N.
\]

Store \(m\), the transverse torus-lattice translation vector and the
time-seam cover.  A certified search may prove absence of entry on a finite
window, but its primary outcome remains `right_censored_no_entry`.  The
all-time `no_entry_proved` outcome requires either exhaustive coverage of an
exact recurrence time circle, together with an armed initial state and
\(\rho(t_0)>r_{\rm in}\), or a strict global-in-time bound
\(\rho(t)>r_{\rm in}\).  Floating intervals that merely contain a rational
number do not prove exact recurrence.

SciPy and NumPy may generate candidates only.  `mpmath.iv.findroot` may not
generate an `excluded` or `unique_root` conclusion.  Arb/python-flint supplies
strict ball operations but not the complete proof automatically: the project
must still implement Krawczyk, directed enclosure of preconditioners, gap-free
box coverage and certificate replay.  Fourier coefficients, lattice,
thresholds and metrics enter the backend as exact values or outward-rounded
enclosures.

Until an independent proof backend replays the certificate, label the result
`controlled numerical verification`, not an exact physical event theorem.

Freeze the following next-round numerical fixture matrix in the handoff
artifact:

- unique regular root, excluded box and singular-root Krawczyk controls;
- separate \(F_t=0\) and \(\det H_{\sigma\sigma}=0\) determinant controls;
- a narrow high-\(K\) root lying between candidate-grid nodes;
- torus, world-sheet and time-seam duplicates counted once;
- complete image enumeration for non-unit \(G\);
- local non-global Morse roots, saddles and outward roots rejected as entry;
- simultaneous, strictly ordered-nearby and unresolved-order root pairs;
- repeated inner contacts before outer exit versus a second episode after
  certified re-arming;
- exact recurrent no-entry versus incommensurate finite-window no-entry;
- positive-dimensional roots and resource-budget exhaustion retained as
  unresolved;
- interior, endpoint and tied episode-closest controls.

## 9. Required artifacts

Commit:

1. `responses/0018_exact_chiral_microcanonical_source.md`;
2. `artifacts/0018/microcanonical_source.py`;
3. `artifacts/0018/test_microcanonical_source.py`;
4. `artifacts/0018/source_registry.json`;
5. `artifacts/0018/source_report.json`;
6. `artifacts/0018/event_record.schema.json`;
7. `artifacts/0018/event_schema_controls.json`;
8. `artifacts/0018/README.md`.

All JSON readers must reject duplicate keys, non-finite numbers and
type-changing substitutions such as `true -> 1`.  Semantic replay must be
independent of LF/CRLF line endings.  Every vector and matrix has a strict
declared shape.

The source report must print its canonical SHA-256, code inventory, Python and
dependency versions, seed policy, sample count and every failed gate.

## 10. Mandatory tests

At minimum:

1. chiral forward/inverse round trip for several \(M,k_n,K\);
2. pure-left and pure-right sign controls;
3. analytic and finite-difference Jacobian agreement;
4. per-sample energy, eight target-momentum and two level-matching residuals;
5. hard rejection of \(E_*\le0\);
6. exact Dirichlet moment formulas
   \[
   \mathbb E\prod_jX_j^{r_j}
   =
   \frac{
   (4)_{r_0}(d-1)_{r_1}(d-1)_{r_2}
   }{
   (2d+2)_{r_0+r_1+r_2}
   };
   \]
7. Gamma implementation versus independent hierarchical-Beta implementation;
8. hostile shape mutations \(d\), \(d/2\) and \(d-\tfrac12\), all rejected;
9. uniform-torus Fourier-character controls for \(Q_{\rm rel}\);
10. the \(\sigma\)-average of \(Y_i\) is zero while the average of
    \(X_i^\perp\) is \(Q_i\);
11. source coefficients unchanged under mutations of event thresholds, rank
    tolerance, validity threshold and response data;
12. validity mutation changes only the label, never the sampled coefficients
    or sample count;
13. exact-flow conservation of \(H\) and \(\mathcal P_\sigma\);
14. independent chiral directions, not copied left/right vectors;
15. rejection of tolerance-based level matching;
16. nonzero-\(\pi\) analytic controls for the singular equality boundary and
    the exact left/right exchange under \(\pi\mapsto-\pi\);
17. schema/precedence fixtures cover every primary variant, including
    `torus_branch_ambiguous` and `numerically_unresolved`, without pretending
    that every variant is realized by a valid physical trajectory;
18. a synthetic tied, grazing and degenerate cluster has exactly
    `primary_outcome == "tie_cluster"`, all three flags true, and exactly one
    primary mass row;
19. finite-window no-entry versus complete-time no-entry remain distinct, and
    the latter fixture uses exact commensurate zero-mode drift or a true global
    lower bound rather than the oscillator period alone;
20. an outer grazing touch does not re-arm, certified strict overshoot re-arms
    exactly once, and a second inner contact before overshoot is a secondary
    mark rather than a new episode;
21. a certified exact-rank-two event keeps a seven-dimensional normal fiber
    without changing source sampling or event selection; a tolerance-only rank
    label is not accepted for this test;
22. outcome-conditional schema rules require finite-window exclusion for
    `right_censored_no_entry`, exact recurrence/global bound for
    `no_entry_proved`, cluster completeness for `tie_cluster`, and an
    unresolved-region manifest for `numerically_unresolved`; `source_invalid`
    does not require a root certificate;
23. strict loaders reject wrong shapes, duplicate keys, non-finite values and
    type substitutions; duplicate-key rejection is not delegated to JSON
    Schema;
24. LF/CRLF clean-copy replay;
25. `unique_root` without an inclusion witness, gap-free leaf cover or image
    manifest is rejected;
26. `regular_first_entry` without global minimality, no-earlier-entry,
    \(H_{\sigma\sigma}\succ0\) or \(F_t<0\) certificates is rejected;
27. overlapping time intervals without an equal-time proof cannot be emitted
    as `tie_cluster`;
28. `no_entry_proved` is rejected for a finite window, approximately rational
    drift, or a recurrence claim missing its exact integer/lattice certificate;
29. `outer_exit=true` is rejected without a post-boundary
    \(\rho>r_{\rm out}\) certificate;
30. an event-order-relevant unresolved leaf cannot coexist with a
    non-unresolved primary outcome;
31. seam/image duplicates are quotiented once, while two genuinely distinct
    simultaneous roots remain a complete cluster;
32. deleting a coverage-tree leaf fails replay even if ordinary JSON hashes
    are recomputed;
33. full-directory test discovery exits zero from a clean checkout.

Statistical tests must use preregistered seeds and finite-sample acceptance
intervals with controlled familywise error.  They supplement the analytic
derivation; they do not replace it.

## 11. Acceptance and verdict

This round passes only if:

- the implemented sampler is derived from the single ambient
  delta--Liouville measure;
- every ideal source constraint is satisfied analytically by construction,
  and the floating implementation supplies certified residual enclosures;
- no rank or event quantity enters the source draw;
- every invalid sample is retained;
- the event-record type and precedence schema is total, disjoint and cluster
  preserving;
- all committed files reproduce from a clean checkout;
- all claims remain within the finite-\(K\), quadratic, graph-sector scope.

The correct success statement is:

> The zero-level-matching finite-\(K\) classical source measure and the type,
> precedence and serialization contract for its downstream event records are
> closed within the declared model.

It is not:

> The physical near-encounter law, \(3+1\) selection, or early-universe F1
> preparation has been derived.

The next open gate is the certified exhaustive hysteretic event solver,
followed by the unconditioned population law of
\((T,j,b,\ell,a,\sigma_3)\).

No event-map outcome masses are assigned in this round.  The schema is closed;
the certified event map has not yet been numerically instantiated.
