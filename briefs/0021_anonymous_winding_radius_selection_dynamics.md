# Brief 0021 — anonymous winding/radius dynamics and the strict three-selection gate

Baseline: the final verified Brief 0020 commit.

## Mission

Compose the source-derived, radius-dependent microscopic kernels of Brief
0020 with one permutation-equivariant winding/radius/reservoir dynamics.
Determine, without entering a preferred dimension label, whether an open
family of preparations develops a stable response-visible three-dimensional
spatial plateau.

The round must end in one of three states:

1. `certified three-selection within the declared dynamical class`;
2. `declared class excludes robust three-selection`;
3. `inconclusive`, with the unidentified rate, preparation or response map
   printed explicitly.

The existence of the F1 kinematic ceiling

\[
a\le 2p+1=3
\]

is an upstream theorem, not the result sought here.  This round must establish
or exclude strict selection among all response competitors \(m=0,\ldots,9\),
including \(m=1,2\).

## 1. Ontological boundary

The dynamical model begins with nine spatial target cycles and one Lorentzian
evolution parameter.  Therefore success can explain why three spatial
directions become stably large and response-visible within this model.  It
does not derive the existence or uniqueness of time from a timeless theory.

Keep four notions separate:

1. target-cycle count: fixed at nine in the registered model;
2. number of currently large radii;
3. local encounter rank \(j\le3\);
4. response-visible spatial rank \(m\).

No equality among these is assumed.  Any equality used in a theorem must be
provided by a separately replayed visibility map.

## 2. Anonymous microscopic state

Use a labelled implementation only for serialization.  The physical state is
an \(S_9\)-equivariant object

\[
X=
(\lambda_i,\dot\lambda_i,W_i^+,W_i^-,N_i,\mathcal A_i)_{i=1}^{9}
\oplus(\varphi,\dot\varphi,E_{\rm osc},E_{\rm res},h),
\]

where:

- \(L_i=L_*e^{\lambda_i}\) is the \(i\)-th cycle length;
- \(W_i^\pm\) are positive/negative winding populations;
- \(N_i\) is the registered momentum-mode population;
- \(\mathcal A_i\) stores pair ages or return-clock state;
- \(\varphi\) is the shifted dilaton when the dilaton-gravity realization is
  selected;
- \(E_{\rm osc}\) and \(E_{\rm res}\) close the energy ledger;
- \(h\) stores hysteretic episode and source history.

The state space, initial-law family, transition rules and all boundary
conditions must be closed under every permutation of the nine axes.

An implementation may cache

\[
q_\rho(X)=\#\{i:L_i>\rho\},
\]

but \(q_\rho\) is a derived diagnostic.  It is forbidden as a branch selector
for reaction formulas unless the same formula is proved to be the exact
reduction of the full radius-dependent kernel.

## 3. Radius/stress-energy realization

The primary physical realization should use one declared low-energy
string-frame system.  For the standard shifted-dilaton control, register

\[
\dot\varphi^2-\sum_i\dot\lambda_i^2=e^\varphi E,
\]

\[
\ddot\lambda_i-\dot\varphi\dot\lambda_i
=\frac12e^\varphi P_i,
\]

\[
\ddot\varphi-\sum_i\dot\lambda_i^2
=\frac12e^\varphi E.
\]

Specify the lapse, units, sign convention and constraint-preserving numerical
flow.  Derive \(E\) and every \(P_i\) from the registered winding, momentum,
oscillator and reservoir energies.  At minimum the control ledger includes

\[
E_{W,i}\propto (W_i^++W_i^-)L_i,
\qquad
E_{N,i}\propto N_i/L_i,
\]

with their pressure signs and all constants fixed.

If a different radius dynamics is chosen, it is a separately named model and
must expose the same anonymous ports.  One model's successful plateau may not
be used as evidence for another.

The numerical integrator must either preserve the Hamiltonian constraint by
construction or serialize a rigorous enclosure of its drift.  An ODE solver
success flag is not a physical certificate.

## 4. Source-derived reaction propensities

For each cycle \(i\), obtain the geometric encounter kernel

\[
\mathcal K_i(\cdot\mid X)
\]

from Brief 0020 after binding the full current radius vector and reservoir
state.  Compose it with the separately registered reaction port and pair
clock to form interval propensities

\[
0\le a_i^-(X)\le a_i(X)\le a_i^+(X).
\]

For an opposite-winding annihilation, the state update must:

1. reduce \(W_i^+\) and \(W_i^-\) together;
2. conserve net winding charge;
3. transfer the released winding energy into declared oscillator/reservoir
   channels;
4. update ages and pair histories without an independent impact redraw;
5. retain unresolved rate width.

If winding-pair creation is admitted, its reverse propensity must follow from
a registered reservoir law or detailed-balance relation.  It may not be
chosen solely to make \(m=3\) stationary.

The full piecewise-deterministic or jump generator is

\[
\mathcal L f
=b(X)\cdot\nabla f
+\sum_r a_r(X)\bigl[f(\Psi_rX)-f(X)\bigr],
\]

where every reaction \(r\), deterministic drift \(b\), and update
\(\Psi_r\) is \(S_9\)-equivariant.

## 5. Preparation family

Selection is quantified over a preregistered open family

\[
\mathfrak M_0
\]

of initial probability laws, not one isotropic point.

The family must include:

- small generic anisotropies in all nine radii and velocities;
- exchangeable winding and momentum perturbations;
- a nonzero range of dilaton/coupling and reservoir energies;
- at least one preparation with fewer than three initially large cycles;
- at least one with more than three initially large cycles, unless a proved
  energy constraint excludes it;
- histories that are armed and histories containing an active pair episode.

Exact isotropy may be retained as a symmetry control.  A deterministic
equivariant flow cannot choose a particular three-axis subset from an exactly
symmetric point without a symmetry-breaking perturbation or stochastic
event.  The ensemble result should be exchangeable over the
\(\binom{9}{3}\) possible subsets.

No initial-law parameter may refer to `winner=3`, a preferred three-axis
frame or a response score.

## 6. Anonymous response reconstruction

At registered observation times, apply the already certified response
interface to the dynamical state.  Reconstruct all competitors

\[
Z_0,\ldots,Z_9
\]

from identical anonymous probes and interventions.

For each \(m\), compute:

- first-entry time into \(Z_m\);
- entrant strict-residence probability;
- conditional retention;
- worst leakage to every \(Z_{m'}\);
- response-identifiability and non-hiding margins;
- cone/signature availability when the response layer supports it.

The response layer may use radii, Green functions or calibrated probe data.
It may not read winding-cycle labels, the local encounter rank or the
dynamical target `three`.

If the response map does not prove that a large-radius plateau is visible, the
output is only a radius-selection result.

## 7. Strict selection criterion

Fix a residence horizon \(\tau_{\rm res}\), leakage horizon
\(\tau_{\rm leak}\), and simultaneous error budget before running the model.

For every initial law \(\mu\in\mathfrak M_0\), define

\[
R_m(\mu)
=P_\mu\!\left(
\text{enter }Z_m
\text{ and remain strictly in }Z_m
\text{ for }\tau_{\rm res}
\right),
\]

and

\[
L_m(\mu)
=\sup_{m'\ne m}
P_\mu\!\left(
\text{leak from }Z_m\text{ to }Z_{m'}
\text{ within }\tau_{\rm leak}
\mid \text{entry into }Z_m
\right).
\]

A strict three-selection certificate requires positive uniform margins

\[
\inf_{\mu\in\mathfrak M_0}
\left[
R_3(\mu)-\max_{m\ne3}R_m(\mu)
\right]\ge\eta_R>0,
\]

\[
\sup_{\mu\in\mathfrak M_0}L_3(\mu)
\le
\min_{m\ne3}\inf_{\mu\in\mathfrak M_0}L_m(\mu)-\eta_L
\]

or a predeclared equivalent stability criterion.

All source, solver, reaction and numerical unresolved intervals are assigned
adversarially when lower-bounding \(\eta_R,\eta_L\).  A positive midpoint
with an interval crossing zero is inconclusive.

## 8. Dynamical certificate routes

At least one route below must be completed.

### 8.1 Finite-state exact route

Construct an abstraction whose cells cover the declared physical state
family.  Interval transition rates must enclose every microscopic model in
the cell.  Prove:

1. no missing or overlapping state cells;
2. a common reachability/arrival bound into \(Z_3\);
3. a lower bound on residence in \(Z_3\);
4. an upper bound on leakage;
5. strict comparison to all \(m\ne3\).

Uniformization, interval Markov-chain bounds or exact rational generators are
acceptable when independently replayed.

### 8.2 Lyapunov/minorization route

Provide a permutation-invariant Lyapunov function \(V\), a target
neighbourhood \(B_3\), and certified constants satisfying a drift condition
outside \(B_3\), for example

\[
\mathcal LV\le-c<0.
\]

Combine it with a reachability/minorization condition and a certified
small-leakage bound inside \(B_3\).  The bounds must apply uniformly to every
\(\mu\in\mathfrak M_0\).

### 8.3 Coupled pathwise route

Construct monotone lower/upper processes driven by the same registered random
words.  Prove that every admissible physical trajectory is sandwiched between
them and that both have the same response winner with a positive margin.

Trajectory simulation without one of these or another predeclared
concentration theorem is controlled numerical evidence, not a uniform basin
certificate.

## 9. Necessary time-scale crossing

As a diagnostic, define the integrated certified annihilation hazards along
each radius-history stratum,

\[
H_i^\pm[t_a,t_b]
=\int_{t_a}^{t_b}a_i^\pm(X_t)\,dt.
\]

Efficient unwinding requires a lower hazard large enough that

\[
1-e^{-H_i^-}\ge1-\varepsilon_{\rm hit},
\]

while winding retention requires an upper hazard small enough that

\[
1-e^{-H_i^+}\le\varepsilon_{\rm miss}.
\]

These inequalities are diagnostics of the full anonymous dynamics, not
piecewise formulas indexed by a chosen dimension count.

A viable three-selection route must exhibit both:

1. an upward/release mechanism that prevents one- and two-dimensional
   plateaus from becoming equally absorbing;
2. a post-three suppression/return mechanism that prevents four and higher
   plateaus from persisting.

The F1 codimension ceiling supplies only the second tendency unless the
source/radius dynamics also proves the first.

## 10. Identifiability and no-go tests

The following outcomes force a downgrade.

### 10.1 Free return-clock no-go

If the geometric encounter law is fixed but the absolute pair clock or
post-miss correlation law remains free, construct two admissible clocks with
different response winners.  Then strict selection is not identified by the
encounter law alone.

### 10.2 Free reaction-profile no-go

If supported reaction bounds include profiles whose rate ordering crosses,
propagate both.  Different winners inside the allowed profile class exclude a
profile-independent selection claim.

### 10.3 Lower-side degeneracy

If one- and two-dimensional response regions have the same absorbing or
residence bounds as the three-dimensional region and no independently
derived upward drive separates them, the F1 three-ceiling does not imply
strict three-selection.

### 10.4 Preparation dependence

If an arbitrarily small allowed perturbation of \(\mu_0\) changes the winner
or removes the residence margin, there is no open-basin certificate.

### 10.5 Visibility failure

If states with different radius counts are response-equivalent under the
registered interventions, the model may select radii but not observable
dimension.

### 10.6 Assumed-time boundary

Even a successful spatial certificate remains conditional on the inherited
Lorentzian time direction.  It cannot be advertised as a derivation of all
of \(3+1\).

## 11. Non-encoding controls

The source-separated dynamics replayer must detect:

1. a preferred three-axis subset under opaque axis renaming;
2. any branch on the number of large radii that is not derived from the full
   kernel;
3. a response winner or encounter-rank field entering the generator;
4. different code paths for \(Z_3\) and the other \(Z_m\);
5. an \(m=3\)-specific initial law, threshold or stopping rule;
6. a reverse reaction inserted only on non-three states;
7. hidden dependence through array order, seed labels or cache keys.

Run the same pipeline on registered counterfactual carrier controls.  For a
\(p\)-carrier interaction whose local domain has dimension \(2p+1\), any
shift of the upper suppression boundary must be an output of the recomputed
kernel.  Hard-coded persistence of three fails the non-encoding gate.

## 12. Mandatory sensitivity cells

The final ledger includes:

- all \(K\) values surviving Brief 0020;
- at least three interaction radii relative to \(\ell_s\);
- at least three coupling/reaction-bound cells;
- at least three dilaton or freeze-out histories;
- matched winding-energy and momentum-energy controls;
- initially sub-three, near-three and super-three radius preparations;
- reversible and explicitly irreversible reservoir controls when both are
  physically allowed;
- the straight-string and rank-blind wiggled source controls.

The same seeds may be coupled for variance reduction, but every marginal law
must remain correct.

## 13. Falsifiable plateau-loss boundary

Before reading the result, register one scalar control \(\chi\) that changes a
microscopic time-scale ratio without naming a target dimension.  Candidate
controls include:

- \(r_{\rm in}/\ell_s\);
- the string coupling entering the reaction profile;
- the expansion-to-return time ratio;
- the dilaton freeze-out time;
- the oscillator energy fraction.

Predict an interval \([\chi_-,\chi_+]\) such that:

- below one side, winding fails to clear even the lower competitors;
- in an intermediate interval, a three-dimensional response plateau is
  possible;
- beyond the other side, a fourth-or-higher competitor is no longer
  suppressed, or the plateau loses its residence margin.

The exact ordering depends on the chosen \(\chi\) and must be derived, not
written into the classifier.  Failure to observe the predicted loss of
plateau falsifies the corresponding dynamical closure.

Additional preregistered predictions should include:

1. the correlation between event-conditioned small \(\sigma_3\) mass and
   plateau leakage;
2. the shift under a \(p\)-carrier counterfactual;
3. exchangeability of the selected three-axis subset;
4. regulator drift with \(K\);
5. the frequency of hysteretic repeated-contact episodes near the
   plateau-loss boundary.

## 14. Required artifacts

Commit:

1. `responses/0021_anonymous_winding_radius_selection_dynamics.md`;
2. `artifacts/0021/dynamics_registry.json`;
3. `artifacts/0021/dynamics_generator.py`;
4. `artifacts/0021/dynamics_replayer.py`;
5. `artifacts/0021/visibility_bridge.py`;
6. `artifacts/0021/test_dynamics.py`;
7. `artifacts/0021/test_dynamics_replayer.py`;
8. `artifacts/0021/selection_ledger.json`;
9. `artifacts/0021/plateau_loss_prediction.json`;
10. `artifacts/0021/README.md`.

If full path data are too large for Git, publish content-addressed chunks with
an in-repository strict manifest and complete small fixtures.

## 15. Acceptance statement

If the uniform margins pass, the strongest permitted statement is:

> Within the declared finite-\(K\), Lorentzian string-gas dynamical class and
> its preregistered open preparation family, a permutation-equivariant
> source-derived kernel gives the response-visible three-spatial-dimensional
> state a strictly larger entrant-residence and smaller leakage bound than
> every competitor.

If they do not pass, publish the sharpest exclusion or identifiability result.

Neither outcome by itself derives the one time direction.  The next and final
gate must test whether the spatial plateau, response cone and Lorentzian
signature survive one common intervention class and must state precisely
which part of \(3+1\) is derived versus inherited.
