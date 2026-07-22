# Brief 0007 — Derive the generator behind rank release and response

Status: active

Baseline commit: `5a72a19ae4a72db6d846c3af763d0065494cd4b7`

## Role

Act as the originating mathematical physicist. Do not review or defend
response 0006. Its best components have been adopted, and its controller has
made the next hard seam explicit. Originate the microscopic or mesoscopic
generator that could replace the prescribed WIRRC drift.

Read, in order:

1. `state/PROJECT_STATE.md`;
2. `decisions/0005_adopt_repaired_uniform_certificate.md`;
3. `responses/0005_repaired_uniform_3plus1_certificate.md`;
4. `responses/0006_operational_3plus1_selection.md`;
5. `decisions/0006_adopt_scale_ledger_wirrc_as_control.md`;
6. this brief.

The project remains one closed loop. Do not discuss journals or split the
work into papers.

## What is already settled

The identity

\[
\delta_p(s)=2p+1-s,
\qquad s_p=2p+1
\]

is a legitimate generic-intersection seam. The six-gate selection ledger is
the correct target. A complete finite two-jet Green control can test the
response reconstruction. None of these facts derives a physical drift toward
\(s_p\), selects \(p=1\), or selects one time and a common cone.

The present WIRRC clock is only a control because it says: if the rank is
below \(s_p\), move up; if it is above \(s_p\), move down. Replacing the
literal numeral three by a formula is not yet a microscopic explanation.

## Required construction

### 1. A real state space and generator

Define a state space containing at least:

- a variable released-rank/projector sector;
- defect species \(p\) with dynamical density or occupation, tension/mass and
  energy constraints;
- the microscopic variables needed to determine collision or annihilation
  rates;
- response/source/readout variables before any invisible directions are
  quotiented away.

Give either an action/Hamiltonian with a controlled kinetic reduction or a
normalized continuous-time Markov generator

\[
\mathcal L f(X)
=\lambda_+(X)[f(J_+X)-f(X)]
+\lambda_-(X)[f(J_-X)-f(X)]
+\mathcal L_{\rm defect}f(X)
+\mathcal L_{\rm response}f(X).
\]

The definitions of \(\lambda_\pm\) may use worldvolume collision geometry,
defect density, impact distribution, tension, energy and expansion variables.
They may not contain a branch equivalent to `if s<s_p move up; if s>s_p move
down`, a potential centered at \(s_p\), a preferred rank-three subset or a
fixed four-dimensional kinetic dictionary.

Prove positivity, normalization/non-explosion and equivariance. Define every
reset/pushforward map for the metric, fields, response records and residuals
when rank changes.

### 2. Let the drift reveal the selected rank

Compute the rank drift or effective potential from the derived generator.
Determine its zeros and stability without assuming them. Establish one of:

- an exact finite-state theorem;
- a controlled asymptotic theorem;
- a reproducible numerical conjecture with explicit error and finite-size
  bounds; or
- a no-go showing that the intersection kernel alone cannot generate the
  required bidirectional drift.

Vary \(p\). The same implementation must reproduce the appropriate
counterfactual behavior. Then make \(p\) a competing dynamical species and
state whether an open parameter region is actually dominated by \(p=1\).
If no current action provides this, prove the obstruction and identify the
minimal additional physical term rather than hiding \(p=1\) as an input.

### 3. Repair the selection theorem

Replace the circular target definition by a nonempty microscopic stratum
\(Z_I(M)\) defined independently of successful certification. Require a
forward tube until arrival, complete hybrid trajectories, piecewise absolute
continuity and the jump condition

\[
V(X^+)\le V(X^-).
\]

Only then compose with the response certificate. Preserve the universal
quantifiers over the full raw microscopic candidate fiber and the strict
`certified / excluded / inconclusive` semantics.

### 4. Derive, do not register, the response coupling

Construct the source/readout map on the pre-quotient microscopic state. Compute
its observability kernel before choosing an event projector. `R=I` may remain
only as a positive unit control.

Derive finite transfer/Green data from the same generator or its linearization.
Show how the neutral two-jet reconstruction obtains the principal biform. Do
not pass \(q\), signature, a cone truth value or a directed time vector to the
reconstructor.

For multiple field sectors, determine whether the same dynamics contracts
off-common-cone components. A subgradient law aimed at a supplied \(q\) is an
ansatz unless it follows from the generator.

### 5. One time and the departure

State exactly whether index-one hyperbolicity and a time component are selected
or remain a viability-sector condition. Do not use the mechanism flow parameter
as physical time without an ordered-response derivation.

Derive the defect excitation threshold, Green pole or leakage channel from the
same spectrum that sets the rank rates. The departure experiment may not
manually inject a response channel. Give at least one relation among attraction
time, impact/radius variables and departure bandwidth that could falsify the
generator.

### 6. Source discipline

Use primary sources. The audited string rate kernel is Greene, Kabat and
Marnerides, `arXiv:0908.0955`; `arXiv:1212.2115` has the same three authors and
the title *On three dimensions as the preferred dimensionality of space via
the Brandenberger--Vafa mechanism*. Do not attribute the latter to
"Brandenberger et al." Cite a specific paper for every CDT, graph, tensor or
matrix-model mechanism actually used.

Separate every result into:

- source-derived exact;
- source-derived conditional/numerical;
- newly proposed law;
- executable control;
- open gate.

## Mandatory adversaries

1. A controller with rates explicitly keyed to \(s_p\); the non-encoding
   audit must reject it.
2. A model with only upward births or only downward deaths; it must not report
   a full-rank basin.
3. A target rank with zero drift but repelling linearization.
4. A \(p=2\) sector that still returns three.
5. A mixed-species state in which \(p=1\) is not dominant.
6. A rank reset that increases the response residual or changes inertia.
7. Complete readout only after quotienting; it must not count as microscopic
   non-hiding.
8. Even transfer data under port reversal; physical time must remain
   unresolved.
9. Two fields with inequivalent cones.
10. A manually injected high-bandwidth channel; it must fail the
    same-generator departure gate.

## Deliverable

Write one complete response to

`responses/0007_source_derived_generator.md`

and commit and push it directly to `main`. Do not create a PR, do not ask for
a download and do not return only a chat summary. In chat, report only the
path, commit hash, the generator/no-go obtained and the remaining hard gate.
