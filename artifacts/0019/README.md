# Brief 0019: first verifiable certificate foundation

This directory contains the Brief 0019 certificate foundation and the first
source-bound physical branch.  It closes the exact container mechanics and,
for preregistered source index 2, an exact closed-string finite-window
no-entry certificate.  It does **not** claim that the population
finite-\(K\) hysteretic world-sheet event problem is solved.

The implemented foundation and its independent replay layer consist of:

1. canonical dyadics \(n/2^e\), with reduced serialization and no JSON
   floating tokens;
2. exact intervals carrying endpoint ownership and exact boxes;
3. a forest with one root for every enumerated torus image, whose split
   topology is replayed from the root domain;
4. exact rectangular-lattice image enumeration for a non-unit diagonal
   metric fixture;
5. typed `excluded_range`, `unique_root`, and `unresolved` leaves; and
6. node, root, cover and whole-bundle semantic hashes that are checked only
   after the corresponding mathematical witness is replayed; and
7. a source-separated
   [`certificate_replayer.py`](certificate_replayer.py) that imports none of
   the generator, Arb-jet, or Arb-Krawczyk implementations and independently
   implements strict JSON, dyadics, image enumeration, exact partitions,
   affine ranges, Krawczyk witnesses, and hash replay.

## External problem commitment

The mathematical inputs of the foundation control are stored separately in
[`foundation_problem_registry.json`](foundation_problem_registry.json).  Both
the generator-side verifier and the independent replayer require its
canonical SHA-256 to be exactly

```text
ac2e14bef595c1e152f32bddfcdea7b5ba295fd0c80e62e19e843cc34a01ce66
```

That digest is fixed in each implementation's source.  The bundle's affine
function system and parameter domain must exactly equal the committed
registry, while the complete ordered image manifest is reconstructed from
the registry's image inputs.  Consequently, replacing the affine equation
and root location while also regenerating every node, root, cover, and bundle
hash is rejected at `problem_commitment`; an attacker cannot create a new
self-consistent problem merely by rewriting fields inside the bundle.

The next committed control,
[`arb_interval_jets.py`](arb_interval_jets.py), pins
python-flint 0.9.0 / FLINT 3.6.0 and evaluates a genuine \(K=1\)
trigonometric two-string fixture with outward-rounded Arb balls.  From exact
dyadic coefficients it derives

\[
d,\ d_a,\ d_{ab},\ F_a,\ F_{ab},\ g,\ Dg
\]

on three-variable boxes.  Its exact regular inward root has

\[
H_{\sigma\sigma}=2I_2,\qquad F_t=-\frac12,\qquad
\det Dg=F_t\det H_{\sigma\sigma}=-2.
\]

The control also verifies that an Arb interval evaluation on a nontrivial
box encloses a higher-precision point evaluation.  It imports neither NumPy
nor the platform libm for asserted proof arithmetic.

[`arb_krawczyk_control.py`](arb_krawczyk_control.py) then uses that physical
three-equation jet.  On the exact box

\[
(\sigma_1,\sigma_2,t)\in[-1/32,1/32]^3
\]

and the exact point preconditioner

\[
C=\operatorname{diag}(1/2,1/2,-2),
\]

it recomputes

\[
K(B)=x_0-Cg(x_0)+(I-CDg(B))(B-x_0)
\subset\operatorname{int}B
\]

with a positive Arb margin on all three axes.  The deliberately wider
\([-1/16,1/16]^3\) box fails inclusion, a zero preconditioner fails, and an
outward root can be isolated only as a root—not mislabelled as inward entry.

## Pinned source-to-physical-problem bridge

[`source_state_bridge.py`](source_state_bridge.py) closes the next wiring
layer without claiming that the event search is exhaustive.  On every build
or replay it reads the canonical Brief 0018 `source_registry.json`, validates
it with the canonical source implementation, and recomputes the registry
commitment

```text
35d31a64e45d9a3ea9cc346e19d8bc5d8d40d1f9eac68eb07385fb291aed8cdb
```

and source-draw identity

```text
4bc0d8eadef9ad8aea8752f25e105127311b83edebc99ebe1b1b7561999e1bd4
```

It regenerates source indices 0, 1 and 2 rather than accepting a
certificate-supplied state or validity label.  The resulting status ledger
proves that index 0 is the least `source_invalid` state and index 2 is the
least `valid` state, with the Brief-pinned state hashes

```text
index 0  bafc85014205bbdbb8156e059606a73a0c899911745f189a4ac4e0c90742670b
index 2  1c671b6bf8e737d238c21de8b0f694a57b8bfab7006ebb1401136176567f118c
```

The complete states are retained losslessly with canonical `float.hex()`
binary64 leaves.  A shape-identical second projection replaces every
binary64 leaf by its unique reduced `numerator/2^exponent` dyadic.  Replay
decodes every hex leaf, checks it against regenerated source output, and
checks the corresponding dyadic against `float.as_integer_ratio()`.  The
fixture and report themselves therefore contain no ordinary JSON floating
tokens.

Validity is re-evaluated from the pinned registry before routing.  Index 0
returns a `source_invalid` route before physical-problem construction;
injected event-solver and Arb-evaluator probes remain at zero calls.  Index 2
is projected into a rank-blind exact problem containing:

- a nine-dimensional target and ordered eight-dimensional transverse space;
- winding axis 8 and orientations `(+1,-1)`;
- `Q1`, `Q2`, both transverse velocities, and every \(K=1\)
  \(x,y,p,q,k\) initial datum;
- physical-length world-sheet domains and the registered Fourier ODE;
- \(G=I_9\), diagonal \(\Lambda\), all nine torus periods and image
  convention;
- exact \(r_{\rm in},r_{\rm out}\), the half-open time window, armed initial
  history and right-boundary continuation convention; and
- a typed ingress contract for a later outward-rounded Arb 9D jet.

`Q1` and `Q2` occur once as the two centre data, while each string refers to
its centre by ID.  Replay also checks the one-rounding binary64
\(T_F=1/(2\pi\ell_s^2)\) convention and
\(L_w=|w|L_8\).  Rank, normal, response-winner and reaction fields are
rejected recursively from the physical problem.

The physical-problem semantic SHA-256 is source-code pinned as

```text
1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca
```

Coefficient, state-hash, registry, orientation, wave-number, validity,
source-index and rank-field hostile variants are required to fail.  The
committed files are `source_state_bridge.py`,
`test_source_state_bridge.py`, `source_state_bridge_fixture.json` and
`source_state_bridge_report.json`.

## Independent source-state binding replay

[`source_binding_replayer.py`](source_binding_replayer.py) is the
source-separated trust boundary for that fixture.  It reads only the strict
Brief 0018 `source_registry.json` and the float-free
`source_state_bridge_fixture.json`.  It does not import or dynamically load
the source generator, the bridge, the certified solver, an Arb jet, a
candidate backend, or any cached runtime object, and it contains no
`exec`/`eval` path.

The replayer independently implements the registered SHA-256 counter stream,
open-52 midpoint mapping, Decimal90 logarithm and square root, fixed
sine/cosine polynomial, integer-Gamma radial draw, sphere directions, and
the \(K=1\) real/chiral coefficient map.  It therefore regenerates all three
pre-selection states, including the index 1 state that is not stored in full
in the bridge fixture:

```text
index 0  source_invalid  bafc85014205bbdbb8156e059606a73a0c899911745f189a4ac4e0c90742670b
index 1  source_invalid  5ffab438ce4cefe8ce278aecee6cab6e5939def96469f6327b7509113c0d6c3c
index 2  valid           1c671b6bf8e737d238c21de8b0f694a57b8bfab7006ebb1401136176567f118c
```

For every regenerated state it recomputes the source-core and coefficient
hashes, Q gauge and open torus cell, orientations, wave number, graph bound,
\(k_{\max}\ell_s\), energy, target momentum, and both world-sheet momentum
residuals.  The polynomial residuals are also recomputed as exact dyadics.
The two complete fixture records are checked leaf-by-leaf for the canonical
binary64-hex/exact-dyadic bijection.

The physical problem is then rebuilt solely from the index 2 exact state and
the source registry.  Every primitive field must match the fixture and the
code-pinned problem hash
`1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca`.
Rank, normal, response, and reaction inputs are rejected.  The index 0 route
must contain no solver payload and must show that no event solver or Arb
evaluator executed.  Hostile tests reseal ordinary state, projection, route,
and problem hashes after coefficient changes; the code-pinned registry,
source-draw, state, coefficient, and problem commitments still reject them.

[`source_binding_replayer_report.json`](source_binding_replayer_report.json)
records this replay and a normalized-LF inventory of the two semantic inputs,
the independent replayer and tests, and this README.  The report scope
explicitly leaves the 9D exhaustive solver, unconditioned population
pushforward, and \(3+1\) selection unimplemented.

## Physical index-2 finite-window no-entry v1

The first source-bound physical outcome is now closed for the single
preregistered valid source index 2.  Its precise status is an
**exact-dyadic cut-open rectangular numerical strip lemma**, not a general
first-entry solver and not a physical closed-string certificate.

[`physical_arb_jets.py`](physical_arb_jets.py) accepts only the code-pinned
physical problem

```text
1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca
```

and exact reduced dyadic boxes in
\((\sigma_1,\sigma_2,t)\).  At 192-bit precision with python-flint 0.9.0 /
FLINT 3.6.0 it evaluates, using outward-rounded Arb arithmetic, all nine
components of \(d\), their first and second derivatives, and the derived
\(F,F_a,F_{ab},g_r,Dg_r\).  The implementation separately tests the
single occurrence of \(Q_1-Q_2\), the minus signs of all string-2
contributions, opposite winding, the lattice shift, and enclosure of
higher-precision point evaluations.

[`physical_no_entry_solver.py`](physical_no_entry_solver.py) applies a
strict coordinate-strip exclusion to the registered cut-open half-open
domain

\[
[0,L_w)\times[0,L_w)\times[t_0,t_1).
\]

For every owned leaf it evaluates the closed hull with Arb.  If the
enclosure \(D_A=[\inf D_A,\sup D_A]\) of one target coordinate and its
rectangular period \(L_A\) satisfy

\[
n_{\min}=
\left\lceil\frac{\inf D_A-r_{\rm out}}{L_A}\right\rceil
>
\left\lfloor\frac{\sup D_A+r_{\rm out}}{L_A}\right\rfloor
=n_{\max},
\]

then no integer image in coordinate \(A\) can lie within \(r_{\rm out}\).
Consequently no nine-dimensional rectangular-lattice image can be within
the outer radius on that leaf.  Contact with the radius is deliberately
not excluded.  Normalized widest-axis midpoint bisection, fixed axis tie
orders, half-open endpoint ownership, and bottom-up node hashes make the
rectangular cover deterministic and gap-free.

The committed v1 tree closes with

```text
nodes             179
split nodes        89
excluded leaves    90
maximum depth       9
unresolved leaves   0
outcome             right_censored_no_entry
```

Thus every point of the registered finite cut-open window is excluded for
source index 2, and the armed history reaches the right boundary without an
entry.  The typed result is exactly `right_censored_no_entry`.  It asserts
neither an all-time no-entry result nor anything about the unconditioned
population or dimension selection.

```text
all-time no-entry      false
population law         false
3+1 selection          false
exact seam quotient    false
```

The principal commitments are

```text
physical problem   1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca
solver registry    e0563bd70cd1d9b330d507605b34f0a7f61f8b6abba1f19c556da8462b51d541
root node          dcd47a95924325d32d0be835bff4b04867c36a2abdbd30ea898db673f1a9ce63
certificate        e1bf43d355c2283eebe871af1d58e5aaa330234f106663214af371ea4fcd575c
solver report      a95964ae459d3a6e0f60bb321864fd8f7bc355a0e5a094961357051208860d8b
replayer report    d769090f0399afcf3a7a70a9e59172c5fd83167d0374acdb980a7bb6853ed53e
```

[`physical_no_entry_replayer.py`](physical_no_entry_replayer.py) is the
independent trust boundary for this certificate.  It imports the separately
anchored source-binding replayer only to reconstruct and authenticate the
registered source and physical problem.  Downstream of that gate it
independently reimplements strict float-free JSON, reduced dyadics, the
physical \(K=1\) F1 equations, exact Arb endpoint ingress, all nine
coordinate enclosures, floor/ceiling strip witnesses, the half-open
partition, and bottom-up hashes.  It does not import or dynamically load
`physical_arb_jets.py`, `physical_no_entry_solver.py`,
`source_state_bridge.py`, either foundation jet/solver module, or any
`exec`/`eval`/`__import__` path.  Every one of the 90 stored leaf witnesses
is recomputed from the authenticated problem rather than accepted from the
certificate.

Both solver-side and independent hostile tests reseal all ordinary hashes
after tampering.  They reject deleted or rewired subtrees, overlap or
changed leaf boxes, reordered nodes, forged Arb endpoints, floor/ceiling
bounds, periods, radii, margins or witness axes, replacement by a later
valid axis, changed physical coefficients or torus periods, boundary
contact presented as strict exclusion, a fabricated unresolved leaf, a
rewritten solver registry or problem commitment, and upgrades to
`first_entry`, all-time no-entry, or exact seam equivalence.  Budget
exhaustion remains a typed unresolved result and cannot be relabelled as a
closed cover.

There is one essential analytic boundary.  The registered binary64-derived
values obey

\[
kL_w-2\pi \simeq -2.449\times10^{-16},
\]

with the sign and nonzero enclosure certified by Arb.  Therefore the two
\(\sigma\)-endpoints used here cannot be identified as an exact analytic
seam.  This v1 result is a rigorous numerical strip lemma on a cut-open
rectangle; it must **not** be called a physical closed-string certificate.
A symbolic-\(\pi\) closed-string lift, followed by an exact seam quotient,
is the next gate.

## Symbolic-\(\pi\) closed-string lift

That gate is now closed by
[`symbolic_pi_lift.py`](symbolic_pi_lift.py).  The old source coefficients
and Brief 0018 hashes are retained, but the geometric realization receives
its own version and problem hash.  The exact physical parameters are

\[
L_*=16\pi,\qquad T_F=\frac1{2\pi},\qquad
M=T_FL_*=8,\qquad k_n=\frac n8 .
\]

With \(u_i=\sigma_i/L_*\in\mathbb R/\mathbb Z\) and
\(\xi^w=X^w/L_*\), the target periods and metric are

\[
\Lambda=\operatorname{diag}(8,\ldots,8,1),\qquad
G=\operatorname{diag}(1,\ldots,1,(16\pi)^2).
\]

The registered solver chart is \((u_1,u_2,t)\), with physical domain metric

\[
H=\operatorname{diag}((16\pi)^2,(16\pi)^2,1).
\]

Krawczyk calculations use the coordinate Jacobian in this chart.  Physical
singular values use \(G^{1/2}JH^{-1/2}\).  Integer Fourier harmonics make the
transverse embedding exactly periodic.  Under \(u_1\mapsto u_1+1\) and
\(u_2\mapsto u_2+1\), the separation winding component and image index shift
by \(+1\) and \(+1\), respectively; at the corner the shift is \(+2\).
These are exact lattice reindexings, not numerical endpoint comparisons.

The canonical commitments are

```text
lift registry       c80acb64eeeb3133dff4422fc798f5b75c6feb52cf32502888cac452e2d210a1
closed problem      3bb6599f211c26d98ecba2077051ad9d0339daf96d580a6399cc5a1ba7f030e0
lift fixture        8ab0bf7deca71d4a1d11f7656a2ee45dbe0766e4ca8ce886592559b080d24f9e
```

[`symbolic_pi_lift_replayer.py`](symbolic_pi_lift_replayer.py) independently
rebuilds this registry and problem from the source-separated Brief 0018
replay.  Its only project import is `source_binding_replayer`; it imports
neither the lift generator, any Arb jet implementation nor any solver.
It separately implements strict symbolic \(q\pi^e\) atoms, exact algebra,
metrics, seam actions, time-window transport and coefficient binding.

[`symbolic_source_measure_bridge.py`](symbolic_source_measure_bridge.py)
checks the source-measure consequence rather than assuming it.  In the old
binary64 generator, the rounded products are exactly

\[
\widehat M=8,\qquad \widehat k_1=\frac18,\qquad \widehat E_*=1.
\]

They equal the new exact values.  Therefore the registered radial
Dirichlet factor \((4,15,15)\), the linear chiral Jacobian factor, the
transverse Haar factor and every named random stream are unchanged.  The
coefficient and latent-variable transports are identities with Jacobian one,
so the analytic Brief 0018 unconditioned source law has
Radon--Nikodym derivative one.  All 512 registered source states and their
coefficient payloads are also identical under exact \(q\pi^0\) re-encoding.
This is a source-law statement only: the physical embedding and its event
pushforward are deliberately not asserted to be unchanged.

## Quotient-safe source-2 finite-window no-entry certificate

[`symbolic_physical_arb_jets.py`](symbolic_physical_arb_jets.py) evaluates
the canonical closed problem with outward-rounded Arb arithmetic.  The
public evaluator is fail-closed on the full problem hash, including source
commitment, coefficients, lattice, metric and seam registry.

[`symbolic_no_entry_solver.py`](symbolic_no_entry_solver.py) uses only the
eight transverse components.  If one transverse coordinate is farther than
\(1/2\) from every \(8\mathbb Z\) image on a box, then the full
nine-dimensional target distance is greater than \(1/2\), independently of
the winding image.  Since the target metric is block diagonal and the
transverse block is \(I_8\), this is a rigorous lower-bound projection.
Every owned half-open box is evaluated on its closed hull, and equality with
the outer radius remains unresolved rather than being excluded.

The deterministic quotient cover closes as

```text
nodes              259
split nodes        129
excluded leaves    130
maximum depth        9
unresolved leaves    0
outcome              right_censored_no_entry
```

The axis witness counts are
`[14, 66, 12, 10, 4, 0, 0, 24]`.  The complete registered time window is
therefore outside the outer tube for source index 2 on the exact closed
world-sheet quotient.  This supersedes the cut-open v1 lemma as the
authoritative physical fixture result; the v1 files remain as a documented
serialization-error control.

```text
solver registry    23e404021dcae9b4c75dca810feb404afe6786aa14280f0ae88b0fa4f24fcec5
certificate        d2cd11d1f8fd1b3669d988f590ee619e9a7f5ee6af43b3a0671830abc69f7fe1
solver report      a29941afbecca913f9b7bee6812b2590f8db733b7993053b7bbe05b1cd5a1817
replayer report    48a2a888501cb084af4c3fc2e3277482e59e19c62057253eddb3d399fbebbcd4
```

[`symbolic_no_entry_replayer.py`](symbolic_no_entry_replayer.py) is the
independent semantic verifier.  Its only project import is the independent
symbolic lift replayer; it imports neither the certificate solver, the
production symbolic jet evaluator nor the lift generator.  It reconstructs
the registered source and \(q\pi^e\) problem, implements its own
python-flint transverse evaluator, and re-evaluates every node on the fresh
closed Arb hull.  At 192-bit precision it exactly reproduces every stored
dyadic endpoint, the complete tree, root and certificate hashes.  Twenty-two
resealed hostile mutations are rejected, while exact outer-radius contact is
correctly left unresolved.  The same report hash and exact endpoints replay
on the pinned Windows and WSL backends.

Node budgets reserve every not-yet-created right sibling.  Consequently all
legal odd budgets end in a complete binary partition whose remaining boxes
are typed `unresolved`; budget exhaustion cannot raise an internal error or
be relabelled as no-entry.

## Exact grammar

A dyadic is serialized as

```json
{"exponent": 2, "numerator": 1}
```

meaning \(1/4\).  It must be reduced: zero is `(0, 0)`, and a nonzero
numerator is odd whenever the exponent is positive.  Booleans are not
integers.  Decimal/exponent JSON numbers, `NaN`, infinities and duplicate
object keys are rejected.

Intervals store lower and upper dyadics plus two Boolean endpoint-closure
flags.  A split at \(c\) assigns \(c\) to the right child:

\[
[a,b)=[a,c)\,\dot\cup\,[c,b).
\]

The replayer derives both child boxes from this rule.  It rejects a missing
child, repeated child, multiple parent, orphan, cycle, wrong split point,
overlap, gap, image-branch change, or a root that is absent for an enumerated
image.  Counts and resolution state are derived; there is no trusted
`complete` flag.

## Complete image fixture

The exact two-dimensional control uses

\[
\Lambda=\operatorname{diag}(2,3/2),\qquad
G=\operatorname{diag}(1/4,4),\qquad r_{\rm out}=1/2,
\]

with

\[
d_0\in[1/2,7/2],\qquad d_1\in[-1/4,5/4].
\]

Since

\[
\sqrt{(G^{-1})_{AA}}=(2,1/2),
\]

the exact coordinate radii are \((1,1/4)\).  Certified floor/ceiling replay
therefore gives

\[
n_0\in\{0,1,2\},\qquad n_1\in\{0,1\},
\]

and the manifest must contain all six Cartesian-product images in canonical
order.  Removing one image fails the enumeration gate before cover semantics
are considered.

This is an exact fixture for the required enumeration formula, not yet the
production nine-dimensional image backend or metric lower-bound pruning.

## Leaf witnesses

The `excluded_range` fixture re-evaluates an affine function over its exact
box and verifies that the resulting closed range excludes zero.

The `unique_root` fixture uses

\[
f(u)=2u-1,\qquad B=[1/4,3/4).
\]

From \(u_0=1/2\), \(C=1/2\), \(f(u_0)=0\), and
\(Df(B)=[2,2]\), exact replay obtains

\[
K(B)=u_0-Cf(u_0)+(1-CDf(B))(B-u_0)
     =[1/2,1/2]\subset\operatorname{int}[1/4,3/4].
\]

Both strict margins are \(1/4\).  The bundle stores the operands and result,
but no success Boolean is accepted: the replayer reconstructs the derivative,
point value, Krawczyk image, and margins from the function registry and box.

The remaining leaf is explicitly `unresolved` under a deterministic
operation budget.  Because it remains in the gap-free forest, replay returns
`unresolved_present`; it cannot be hidden by a completeness assertion.

## Run

From the repository root:

```text
python artifacts/0019/certified_solver_core.py --write
python artifacts/0019/certified_solver_core.py --check
python artifacts/0019/certificate_replayer.py --check
python artifacts/0019/arb_interval_jets.py --write
python artifacts/0019/arb_interval_jets.py --check
python artifacts/0019/arb_krawczyk_control.py --write
python artifacts/0019/arb_krawczyk_control.py --check
python artifacts/0019/source_state_bridge.py --write
python artifacts/0019/source_state_bridge.py --check
python artifacts/0019/source_binding_replayer.py --write
python artifacts/0019/source_binding_replayer.py --check
python -m unittest discover -s artifacts/0019 -p "test_physical_arb_jets.py" -v
python artifacts/0019/physical_no_entry_solver.py --write
python artifacts/0019/physical_no_entry_solver.py --check
python artifacts/0019/physical_no_entry_replayer.py --write
python artifacts/0019/physical_no_entry_replayer.py --check
python artifacts/0019/symbolic_pi_lift.py --write
python artifacts/0019/symbolic_pi_lift.py --check
python artifacts/0019/symbolic_pi_lift_replayer.py --write
python artifacts/0019/symbolic_pi_lift_replayer.py --check
python artifacts/0019/symbolic_source_measure_bridge.py --write
python artifacts/0019/symbolic_source_measure_bridge.py --check
python artifacts/0019/symbolic_no_entry_solver.py --write
python artifacts/0019/symbolic_no_entry_solver.py --check
python artifacts/0019/symbolic_no_entry_replayer.py --write
python artifacts/0019/symbolic_no_entry_replayer.py --check
python -m unittest discover -s artifacts/0019 -p "test_*.py" -v
python -m py_compile artifacts/0019/certified_solver_core.py artifacts/0019/certificate_replayer.py artifacts/0019/arb_interval_jets.py artifacts/0019/arb_krawczyk_control.py artifacts/0019/source_state_bridge.py artifacts/0019/source_binding_replayer.py artifacts/0019/physical_arb_jets.py artifacts/0019/physical_no_entry_solver.py artifacts/0019/physical_no_entry_replayer.py artifacts/0019/symbolic_pi_lift.py artifacts/0019/symbolic_pi_lift_replayer.py artifacts/0019/symbolic_source_measure_bridge.py artifacts/0019/symbolic_physical_arb_jets.py artifacts/0019/symbolic_no_entry_solver.py artifacts/0019/symbolic_no_entry_replayer.py artifacts/0019/test_certified_solver_core.py artifacts/0019/test_certificate_replayer.py artifacts/0019/test_arb_interval_jets.py artifacts/0019/test_arb_krawczyk_control.py artifacts/0019/test_source_state_bridge.py artifacts/0019/test_source_binding_replayer.py artifacts/0019/test_physical_arb_jets.py artifacts/0019/test_physical_no_entry_solver.py artifacts/0019/test_physical_no_entry_replayer.py artifacts/0019/test_symbolic_pi_lift.py artifacts/0019/test_symbolic_pi_lift_replayer.py artifacts/0019/test_symbolic_source_measure_bridge.py artifacts/0019/test_symbolic_physical_arb_jets.py artifacts/0019/test_symbolic_no_entry_solver.py artifacts/0019/test_symbolic_no_entry_replayer.py
```

The Arb commands require python-flint 0.9.0 on `PYTHONPATH` or in the active
environment.  Both the Windows and WSL controls replay the same fixture and
report semantic hashes with the pinned wheels used by this project.

`--write` deterministically regenerates
`certified_solver_fixture.json` and `certified_solver_report.json`.
`--check` performs strict JSON loading, type-strict comparison against a fresh
build, semantic replay, hostile-control replay, and normalized-LF inventory
checking.

The same modes on `source_state_bridge.py` regenerate or replay
`source_state_bridge_fixture.json` and `source_state_bridge_report.json`.
This bridge imports the canonical Brief 0018 source only to regenerate the
pinned draw and to validate the regenerated sample.  It is not a
source-separated independent source audit, and it does not import or execute
an event solver.
The separate `source_binding_replayer.py` supplies that independent audit:
it reconstructs the registered source algorithm locally, validates index 1
as well as the two stored controls, and uses only the registry and bridge
fixture as semantic inputs.
The report records `status: passed`, an empty `failed_gates` list, the
complete fixture semantic hash and its own semantic hash (computed with only
that self-hash field omitted); `--check` recomputes both hashes, all
commitments and the normalized-LF inventory.

The hostile controls delete a leaf, alter a split, fabricate a stored
Krawczyk image, replace the affine root system and root location, omit an
enumerated image, and duplicate a node ID.  They refresh all ordinary hashes
that can still be computed, then must fail at their intended semantic gates
rather than at an incidental parser error.  The independent suite additionally
rejects duplicate JSON keys, non-finite and floating JSON tokens, and Boolean
substitution for an integer.

## Deliberately open

The next implementation layers remain:

- exhaustive first-entry subdivision around source-bound physical equations
  for population states not closed by the transverse coordinate-strip lemma,
  using the demonstrated three-equation Arb Krawczyk primitive;
- singular-cluster and seam-aware certificates;
- global spatial minimality, earlier-sublevel exclusion, root ordering and
  tie closure;
- hysteretic outer exit, re-arm and episode closest-point certificates;
- exact recurrence-based `no_entry_proved`;
- execution on the unconditioned Brief 0018 population.

Accordingly, the strongest permitted physical statement for this layer is:

> For preregistered valid source index 2, a symbolic-\(\pi\), quotient-safe,
> outward-rounded Arb cover proves no outer-radius contact anywhere in the
> registered finite half-open time window, with 130 excluded leaves and no
> unresolved leaf; the typed outcome is `right_censored_no_entry`.

This is not an all-time statement, a population law, a first-entry law for
near-threshold states, or a \(3+1\) selection result.
