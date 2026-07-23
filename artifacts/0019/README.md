# Brief 0019: first verifiable certificate foundation

This directory is the first implementation layer of Brief 0019.  It closes
the exact certificate-container mechanics that the later physical solver must
use; it does **not** claim that the finite-\(K\) hysteretic world-sheet event
problem is solved.

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
python -m unittest discover -s artifacts/0019 -p "test_*.py" -v
python -m py_compile artifacts/0019/certified_solver_core.py artifacts/0019/certificate_replayer.py artifacts/0019/arb_interval_jets.py artifacts/0019/arb_krawczyk_control.py artifacts/0019/source_state_bridge.py artifacts/0019/source_binding_replayer.py artifacts/0019/test_certified_solver_core.py artifacts/0019/test_certificate_replayer.py artifacts/0019/test_arb_interval_jets.py artifacts/0019/test_arb_krawczyk_control.py artifacts/0019/test_source_state_bridge.py artifacts/0019/test_source_binding_replayer.py
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

- the nine-dimensional production image cover and rigorous metric pruning;
- exhaustive subdivision around the now source-bound physical equations and
  the demonstrated three-equation Arb Krawczyk primitive;
- singular-cluster and exact seam-equivalence certificates;
- global spatial minimality, earlier-sublevel exclusion, root ordering and
  tie closure;
- hysteretic outer exit, re-arm and episode closest-point certificates;
- exact recurrence-based `no_entry_proved`;
- execution on the unconditioned Brief 0018 population.

Accordingly, the permitted statement for this layer is only:

> The exact foundation fixture replays a gap-free image-indexed cover with
> proof-checked excluded and unique leaves while retaining its unresolved
> leaf.

It is not a claim that the physical event solver or the \(3+1\) selection law
is complete.  In particular, this directory still does not implement the 9D
exhaustive solver, the population pushforward, or \(3+1\) selection.
