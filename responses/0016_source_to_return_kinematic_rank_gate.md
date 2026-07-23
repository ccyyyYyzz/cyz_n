---
brief: 0016
source: browser-hosted GPT
captured: 2026-07-23
branch: brief-0016
brief_commit: 3c4cdf51c22278d26f2e2365d8719a153df4369a
status: proposed
artifacts:
  - artifacts/0016/probe_0016.py
  - artifacts/0016/probe_report.json
---

# Response 0016 — Coordinate-safe encounter jets, the rank-three preparation obstruction, and a conditional source-family ceiling

## Executive result

This round replaces the registered bookkeeping triple by a coordinate-safe
encounter jet and proves that three different integers must remain separate:

\[
\boxed{
p=\text{microscopic carrier dimension},\qquad
a=\text{local encounter kinematic rank},\qquad
m=\text{anonymous response-visible spatial rank}.
}
\]

For an F1 carrier, \(p=1\).  A local encounter may have \(a=1,2,\) or \(3\).
Neither statement determines \(m\).

Let two immersed \(p\)-brane histories in a spatial Riemannian source geometry
\((M^d,G)\) be

\[
X_1:\Sigma_1^p\times I\to M,\qquad
X_2:\Sigma_2^p\times I\to M.
\]

Inside a declared injectivity tube define the logarithmic separation

\[
\Phi_e(\sigma,\sigma',t)
=\operatorname{Log}_{X_2(\sigma',t)}X_1(\sigma,t).
\]

Globally, replace subtraction by the normal differential of
\((X_1,X_2)\) relative to the diagonal \(\Delta_M\subset M\times M\).
At an event jet \(j\), define

\[
a(j)=\operatorname{rank}D\Phi_{e,j}
\le \min(d,2p+1),
\]

and

\[
N_j=(\operatorname{im}D\Phi_{e,j})^{\perp_G},
\qquad
\dim N_j=d-a(j).
\]

Rank is coordinate invariant.  A numerical singular-value margin is not
defined until a physical metric \(H_e\) on encounter-parameter space is also
registered.  The dimensionless whitened jet is

\[
\widehat J_e
=G^{1/2}D\Phi_{e,j}H_e^{-1/2}.
\]

For F1 and \(d\ge3\),

\[
\sigma_3(\widehat J_e)\ge\eta_{\rm kin}>0
\]

is a sufficient open rank-three preparation certificate.  It is not
necessary: a controlled small-\(\sigma_3\) tail together with explicit
lower-rank mixture weights is an equally valid preparation statement.

The mandatory opposite-winding control changes the physical conclusion.  For
two locally straight strings wound oppositely on the same cycle,

\[
\tau_2=-\tau_1,\qquad
D\Phi_e=[\tau_1,\tau_1,v_{\rm rel}],
\]

so

\[
a\le2,\qquad \sigma_3(\widehat J_e)=0.
\]

If \(v_{\rm rel}\) is transverse to the common tangent, \(a=2\); if it lies in
the tangent line, \(a=1\).  A transverse Fourier momentum \(q\), impact vector
\(b\), or arbitrarily named scattering axis cannot supply a missing incoming
column.

This separates two primary-source regimes.

* Jackson--Jones--Polchinski §3.1 describe two locally straight strings wound
  on a two-torus at an angle \(\theta\), with relative motion.  Away from
  parallel and coplanar-velocity degeneracies, the two string tangents and
  relative velocity have rank three.  Their noncompact cross-section then has
  \(D-4=d-3\) dimensions.
* Greene--Kabat--Marnerides later specialize their cosmological rate model to
  strings moving along one direction and wound oppositely along another.  The
  strictly straight same-cycle local stratum is rank two.  The cited source
  does not derive a local tangent-wiggle distribution, a positive
  \(\sigma_3\) margin, or a controlled rank-mixture tail that upgrades this
  stratum to rank three.

The quantum thickness in the GKM impact amplitude describes transverse
spreading about a classical straight string.  It is not, by itself, an
independent incoming tangent.  Therefore the use of a \(d-3\) impact space in
the strictly straight opposite-winding cosmological stratum remains
conditional on an unprovided non-collinear local preparation.

A second correction concerns nonzero impact.  Exact diagonal encounter means
\(\Phi_e=0\), hence \(b=0\).  A nonzero impact vector must be attached to a
preregistered closest-approach or first-entry event jet \(j\).  At an interior
closest approach,

\[
b=\Phi_e(z_*),\qquad
D\Phi_{e,j}^{*}G\,b=0,
\]

so \(b\in N_j\).  The jet determines the normal fiber; it does not determine
the vector in that fiber.  The repaired source law must therefore jointly
output \((j,b)\):

\[
\boxed{
\mathscr P_X
\bigl(
dT,dj,db,d\chi,dh',dX',d\Delta E_R,d\dagger
\mid h
\bigr),
\qquad b\in N_j.
}
\]

Here \(T\) is an absolute first-hit or return time, \(\chi\) is the reaction
channel, and \(\dagger\) is a source-invalid killed outcome.  `frame_arity`,
visible rank, active masks, response bands, and target strata are forbidden
inputs.

The existing fixed-arity constructor has an exact superselection boundary.
If no row changes arity, then the arity observable is pathwise conserved:

\[
A_t=A_0,\qquad
\Pr(A_t=a)=\Pr(A_0=a).
\]

It cannot dynamically select arity three from an arity-neutral open basin.
For \(q\) directions passing its radius predicate, its exact onset count is

\[
N_{\rm valid}(q,a)=
\begin{cases}
q!/(q-a)!,&q\ge a,\\
0,&q<a.
\end{cases}
\]

This is a constructor theorem, not evidence for visible dimension.

For a fixed \(T^9\) event, the impact codimension is

\[
c=9-a,
\]

not \((m-3)_+\).  Only in a separately declared family of effective source
models with spatial carrier dimension \(\ell\) and preparation rule

\[
a_\ell=\min(\ell,3)
\]

does one obtain

\[
c_\ell=(\ell-3)_+.
\]

That remains a source-family statement until the anonymous response program
independently reconstructs \(m\) and proves the required carrier/response
identification and non-hiding conditions.

For two declared, target-neutral impact preparations the averaged Gaussian
profile is

\[
g_c^{\rm ball}(\rho)
=c\int_0^1u^{c-1}e^{-\rho^2u^2}\,du
=\frac c2\rho^{-c}\gamma\!\left(\frac c2,\rho^2\right),
\]

and

\[
g_c^{\rm box}(\rho)
=\left[
\frac{\sqrt\pi}{2\rho}\operatorname{erf}\rho
\right]^c,
\qquad g_0=1.
\]

Both decrease strictly with \(c\) and with \(\rho>0\), and both are bounded by
constants times \(\rho^{-c}\) for large \(\rho\).  Their numerical values are
closure-dependent.  More importantly, GKM derive the displayed Gaussian as a
large-impact asymptotic.  Ball and box supports include \(b=0\).  Extending
that asymptotic through the unresolved core is a declared profile closure
unless a source-valid core amplitude is supplied.

The strongest conclusion is therefore:

```text
verdict = three-ceiling
scope   = conditional source-family theorem under a rank-three event-jet
          preparation and a declared impact-profile closure

strict three-selection = not proved
visible-m ceiling      = not proved
```

The impact mechanism suppresses the upper side of a rank-three prepared source
family, but gives no lower-side advantage among \(\ell=1,2,3\).  The 2012
successive-fluctuation scenario is a conditional numerical candidate for that
lower side, with explicit assumptions about fluctuation statistics, duration,
coupling window, homogeneity, and initial preparation.  It is not an
all-preparation theorem.

The smallest adoption-blocking component is the conditional local event-jet
preparation

\[
\nu_X(dj)
\quad\text{for}\quad
(\tau_1,\tau_2,v_{\rm rel},G,H_e),
\]

including its rank mixture and the distribution or tail of
\(\sigma_3(\widehat J_e)\) given global opposite winding.  The full physical
closure additionally needs the absolute return/impact/history/reverse kernel
\(\mathscr P_X\) and a continuum preparation law \(\mu_0\).

---

# 1. Classification of claims

## `primary-source derived`

1. GKM 2009 use a heavy, dilute winding-string impact representation.  Their
   equation (5) is a Gaussian large-\(b\) asymptotic, and their validity
   discussion requires impact larger than string thickness.  Their numerical
   cosmology estimates a recollision time and redraws an impact parameter.
   This is a numerical return closure, not a first-principles first-return
   theorem.
2. JJP §3.1 formulate a local F--F collision as two infinite straight strings,
   wrap the two long strings on a two-torus with an angle, and include relative
   velocity.  With additional noncompact directions, their result is a
   cross-section of dimension \(D-4\).
3. The normal momentum \(q\) in JJP/GKM and its conjugate impact \(b\) are
   transverse data.  They do not add an incoming tangent direction.
4. GKM's cosmological specialization uses opposite winding along one cycle and
   motion along another.  Global opposite winding does not itself imply
   non-collinear local tangents.
5. Alexander--Brandenberger--Easson and the BV literature use the generic
   \(2p+1\) intersection ceiling as a carrier/encounter argument.
6. GKM 2012 analyze successive fluctuations under a selected model and state
   assumptions; they do not derive the required all-rank preparation law.

## `exact theorem about a declared geometric model`

1. The coordinate-safe encounter-rank theorem.
2. The F1 rank classification and straight opposite-winding obstruction.
3. The \(G,H_e\)-whitened perturbation-margin theorem.
4. The closest-approach orthogonality theorem.
5. Fixed-arity superselection and falling-factorial onset.
6. Ball/box suppression formulas, monotonicity, and large-\(\rho\) bounds.
7. The conditional effective-source identity
   \(a_\ell=\min(\ell,3)\Rightarrow c_\ell=(\ell-3)_+\).

## `derived from a newly proposed measurable closure`

1. A preparation law on event jets with either a uniform
   \(\sigma_3\) margin or a measured small-value tail and explicit lower-rank
   mixture.
2. Uniform-ball and independent-coordinate box impact preparations.
3. Any continuation of the large-impact Gaussian into the small-impact core.
4. The complete bundle-valued source-to-return kernel.

## `controlled numerical probe`

`artifacts/0016/probe_0016.py` evaluates the two suppression controls at
100-decimal-digit working precision, verifies 756 strict monotonicity
inequalities, emits the exact onset table, and replays six F1 controls with
registered \(G\) and \(H_e\).

## `no-go/underdetermination`

1. Straight same-cycle opposite winding cannot generate encounter rank three.
2. A fixed arity sector cannot dynamically select itself.
3. Impact suppression alone cannot distinguish the lower source dimensions
   one, two, and three.
4. The cited sources do not determine the tangent-wiggle preparation, the
   absolute return law, post-miss history, reverse reference measure, or
   continuum initial law.
5. Consequently neither a strict rank-three residence margin nor a
   visible-\(m\) ceiling is currently source-derived.

## `open gate`

1. Measure or derive the event-jet preparation conditional on global winding.
2. Derive or measure the absolute closest-approach/return and impact law,
   including a valid small-impact core.
3. Compile that law into the age-augmented process and run anonymous response
   reconstruction and all-rank strict residence.
4. Keep time orientation and Lorentzian signature separate: this source branch
   starts from a \(9+1\) Lorentzian background.

---

# 2. Coordinate-safe encounter geometry

## 2.1 Diagonal formulation

Define

\[
\Psi_e:
\Sigma_1^p\times\Sigma_2^p\times I\to M\times M,
\qquad
\Psi_e(\sigma,\sigma',t)
=(X_1(\sigma,t),X_2(\sigma',t)).
\]

Exact collision is transversality to the diagonal
\(\Delta_M\subset M\times M\).  At \((x,x)\),

\[
N_{(x,x)}\Delta_M
\simeq
(T_xM\oplus T_xM)/T_{(x,x)}\Delta_M
\simeq T_xM,
\]

with normal class represented by the difference of the two target
velocities.  The normal differential of \(\Psi_e\) is the invariant encounter
jet.

Inside a declared injectivity tube, use the equivalent logarithmic
representative

\[
\Phi_e=\operatorname{Log}_{X_2}X_1.
\]

On a rectangular flat torus this reduces to a unique local lift and ordinary
difference only while the displacement remains inside that tube.  Coordinate
subtraction outside it is not invariant.

At an exact encounter in local normal coordinates,

\[
D\Phi_e
=
\left[
D_\sigma X_1,\,
-D_{\sigma'}X_2,\,
v_{\rm rel}
\right].
\]

### Theorem 1 — coordinate-safe local kinematic rank

For an event jet \(j\), let

\[
a(j)=\operatorname{rank}D\Phi_{e,j}.
\]

Then:

1. \(a(j)\) is invariant under source reparametrizations and target coordinate
   changes;
2. \(a(j)\le r=\min(d,2p+1)\);
3. maximal-rank jets form an open dense subset of the unrestricted linear jet
   bundle;
4. the impact normal fiber
   \[
   N_j=(\operatorname{im}D\Phi_{e,j})^{\perp_G}
   \]
   has dimension \(d-a(j)\).

The rank bound follows from the \(2p+1\)-dimensional domain.  Rank is preserved
by invertible coordinate changes.  Rank below \(r\) is the common zero set of
the \(r\times r\) minors.  Orthogonal decomposition gives the normal
dimension.

The density claim concerns the unrestricted jet bundle.  It says nothing
about a physical preparation supported on a constrained submanifold such as
straight same-cycle opposite winding.

## 2.2 Quantitative metric margin

Register a positive domain metric \(H_e\) on encounter parameters.  It fixes
the relative scale of the two carrier coordinates and source time.  Define

\[
\widehat J_e
=G^{1/2}D\Phi_eH_e^{-1/2}.
\]

The rank is independent of \(H_e\), but the singular values are not.  Under
coordinate changes with the metrics transformed tensorially, the singular
values of the metric-defined operator are invariant.

### Theorem 2 — open rank margin

Suppose

\[
\sigma_r(\widehat J_e)\ge\eta_{\rm kin}>0.
\]

For a perturbed event jet define

\[
\delta_e
=
\left\|
\widetilde G^{1/2}\widetilde D\Phi_e\widetilde H_e^{-1/2}
-G^{1/2}D\Phi_eH_e^{-1/2}
\right\|_2.
\]

If \(\delta_e<\eta_{\rm kin}\), then

\[
\sigma_r(\widetilde{\widehat J}_e)
\ge\eta_{\rm kin}-\delta_e>0,
\]

so maximal rank is preserved.

A directly auditable perturbation bound is

\[
\begin{aligned}
\delta_e\le{}&
\|\widetilde G^{1/2}-G^{1/2}\|
 \|D\Phi_e\|\|H_e^{-1/2}\|\\
&+\|\widetilde G^{1/2}\|
 \|\widetilde D\Phi_e-D\Phi_e\|
 \|H_e^{-1/2}\|\\
&+\|\widetilde G^{1/2}\|
 \|\widetilde D\Phi_e\|
 \|\widetilde H_e^{-1/2}-H_e^{-1/2}\|.
\end{aligned}
\]

For F1 and \(d\ge3\), \(r=3\).

A uniform lower bound is only a sufficient worst-case certificate.  A broader
preparation may instead be written

\[
\nu_X(dj)
=\sum_{k=0}^{r}\pi_k(X)\nu_{X,k}(dj),
\qquad
\nu_{X,k}\{a(j)=k\}=1,
\]

together with a controlled tail such as

\[
\nu_{X,3}
\{\sigma_3(\widehat J_e)<\eta\}
\le\varepsilon_{\rm kin}.
\]

The downstream return process must retain the explicit lower-rank mixture.

---

# 3. F1 rank classification and source audit

For immersed strings, up to the sign of the second tangent,

\[
a
=
\dim\operatorname{span}
\{\tau_1,\tau_2,v_{\rm rel}\}.
\]

### Theorem 3 — complete F1 classification

For \(d\ge3\):

1. \(a=3\) iff \(\tau_1,\tau_2\) are non-collinear and
   \(v_{\rm rel}\notin\operatorname{span}\{\tau_1,\tau_2\}\).
2. \(a=2\) iff either
   * the tangents are non-collinear and \(v_{\rm rel}\) lies in their plane, or
   * the tangents are collinear and \(v_{\rm rel}\) is transverse to their
     line.
3. \(a=1\) iff both tangents and \(v_{\rm rel}\) are collinear.
4. Rank zero is excluded for immersed strings unless the encounter
   parametrization itself is singular.

## 3.1 Opposite same-cycle control

For locally straight opposite winding,

\[
\tau_2=-\tau_1,
\qquad
D\Phi_e=[\tau_1,\tau_1,v_{\rm rel}].
\]

Thus

\[
a\le2,\qquad
\sigma_3(\widehat J_e)=0.
\]

This is independent of ambient dimension.

## 3.2 JJP versus the straight GKM cosmological stratum

JJP §3.1 explicitly uses two long straight strings wrapped on a two-torus with
an angle \(\theta\), one moving toward the other.  For
\(\sin\theta\ne0\) and velocity outside the tangent plane, the encounter rank
is three.  The incoming worldvolume union then has four spacetime directions,
and the noncompact cross-section has dimension

\[
D-4=d-3.
\]

The transverse \(q\) in the amplitude and its Fourier-conjugate \(b\) belong
to the normal space.  Neither is an incoming column.

The GKM cosmological specialization uses strings moving along one direction
and wound oppositely along a second.  In the strictly straight local model,
this gives two independent spatial columns, not three.  There are two honest
continuations:

1. retain this rank-two stratum, so its normal dimension is \(d-2\); or
2. add real local tangent fluctuations or oscillator wiggles to the source
   state and derive their preparation law and rank margin.

GKM distinguish virtual quantum thickness from real oscillator excitations.
Their radiation-regime model does not supply the required non-collinear
tangent preparation.  Therefore \(d-3\) is not yet derived for the straight
same-cycle source population.

## 3.3 General \(p\)-brane statement

Let \(T_1,T_2\subset T_xM\) be the two \(p\)-dimensional tangent images.
Then

\[
a
=
\dim\bigl(T_1+T_2+\operatorname{span}\{v_{\rm rel}\}\bigr)
\le\min(d,2p+1).
\]

On the unrestricted general-position jet set,

\[
a=\min(d,2p+1),
\qquad
c=(d-2p-1)_+.
\]

Shared tangent directions, constrained velocity, symmetry sectors, and
singular embeddings lower the rank.  The familiar \(2p+1\) number is a
carrier/encounter ceiling, not a response-visible dimension.

---

# 4. Closest approach and the bundle-valued impact law

At exact diagonal encounter,

\[
\Phi_e(z)=0,
\]

so an exact encounter cannot simultaneously carry a nonzero impact vector.

Choose instead a preregistered event semantic.  For an interior closest
approach, define

\[
z_*
\in
\operatorname*{argmin}_{z\in U_e}
\frac12\|\Phi_e(z)\|_G^2,
\qquad
b=\Phi_e(z_*).
\]

Use the covariant derivative of the logarithmic separation when the base point
moves.

### Theorem 4 — closest-approach normality

At an interior critical point,

\[
d\!\left(\frac12\|\Phi_e\|_G^2\right)_{z_*}(\delta z)
=
\langle D\Phi_{e,j}\delta z,b\rangle_G
=0
\]

for every \(\delta z\).  Therefore

\[
D\Phi_{e,j}^{*}G\,b=0,
\qquad
b\in N_j.
\]

At a first-entry boundary this equation need not hold.  One must register the
boundary conormal or continue to a closest approach.

The minimal source-to-return law is consequently a kernel on the event-jet
normal bundle:

\[
\mathscr P_X
\bigl(
dT,dj,db,d\chi,dh',dX',d\Delta E_R,d\dagger
\mid h
\bigr),
\qquad
b\in N_j.
\]

It must specify:

* absolute first-hit or return time \(T\);
* the event semantic and jet \(j\), including \(G,H_e,D\Phi_e,a(j)\);
* continuous normal impact/orientation \(b\);
* conditional reaction channel \(\chi\);
* post-miss history \(h'\);
* updated source state \(X'\);
* reservoir transfer and a reference-measure reverse event;
* source-invalid killed output.

GKM's \(t_r\simeq r/\bar v\) recollision schedule and random redraw belong to
a numerical closure of this kernel, not a first-principles derivation of it.

---

# 5. Fixed-arity superselection

Let

\[
\Omega
=
\bigsqcup_{a\in\mathcal A}
\{a\}\times\Omega_a
\]

and suppose the scheduled transition kernel satisfies

\[
K((a,x),\{a\}\times\Omega_a)=1.
\]

### Theorem 5 — arity conservation

The arity observable \(A(a,x)=a\) is pathwise conserved:

\[
A_t=A_0
\quad\text{almost surely}.
\]

Hence

\[
\Pr(A_t=a)=\Pr(A_0=a).
\]

Every event jump remains in its component, and deterministic age evolution
does not alter the component label.  Induction over event times proves the
claim.

The fixed registered process cannot dynamically choose arity three from an
arity-neutral initial mixture.  Arity-three output is conditional on the
chosen constructor or initial sector.

If \(q\) source directions pass the radius predicate and frames are ordered
distinct \(a\)-tuples, the number of frames is the number of injections from
the ordered role set into those directions:

\[
N_{\rm valid}(q,a)
=
\begin{cases}
q(q-1)\cdots(q-a+1)=q!/(q-a)!,&q\ge a,\\
0,&q<a.
\end{cases}
\]

This onset is not automatically malicious encoding, but it is not evidence
for visible dimension.  It becomes source-grounded only after the local
encounter geometry outputs \(a\), and \(m\) must still be reconstructed from
anonymous response.

---

# 6. Impact-codimension suppression

Let

\[
c=\dim N_j=d-a(j),
\qquad
\rho=r/\Delta.
\]

On a source-valid profile domain, write

\[
P(b\mid X,j)
=
P_0(X,j)
\exp\!\left[
-\frac{\|b\|_{G_N}^2}{\Delta^2(X,j)}
\right].
\]

The validity declaration must include the heavy/dilute semiclassical regime,
weak coupling, injectivity tube, and the domain in which the impact profile is
controlled.

## 6.1 Uniform \(c\)-ball closure

For uniform measure in a \(c\)-ball of radius \(r\), the scaled radius
\(u=\|b\|/r\) has density \(cu^{c-1}\).  Therefore

\[
g_c^{\rm ball}(\rho)
=
c\int_0^1u^{c-1}e^{-\rho^2u^2}\,du
=
\frac c2\rho^{-c}
\gamma\!\left(\frac c2,\rho^2\right).
\]

For \(c=0\), define \(g_0=1\).

For \(c>0,\rho>0\),

\[
\frac{\partial g_c^{\rm ball}}{\partial\rho}
=
-2c\rho
\int_0^1u^{c+1}e^{-\rho^2u^2}\,du
<0.
\]

For fixed \(\rho>0\), let \(V\) be uniform on \((0,1)\) and
\(U_c=V^{1/c}\).  Then \(U_{c+1}>U_c\) almost surely and the integrand is
strictly decreasing, so

\[
g_{c+1}^{\rm ball}(\rho)
<
g_c^{\rm ball}(\rho).
\]

For \(\rho\ge1\),

\[
e^{-1}\rho^{-c}
\le
g_c^{\rm ball}(\rho)
\le
\Gamma\!\left(\frac c2+1\right)\rho^{-c}.
\]

## 6.2 Independent-coordinate box closure

For independent coordinates uniform on \([-r,r]\),

\[
g_c^{\rm box}(\rho)
=
h(\rho)^c,
\qquad
h(\rho)
=
\int_0^1e^{-\rho^2u^2}\,du
=
\frac{\sqrt\pi}{2\rho}\operatorname{erf}\rho.
\]

For \(\rho>0\), \(0<h(\rho)<1\), so the factor strictly decreases with
\(c\).  Also

\[
h'(\rho)
=
-2\rho\int_0^1u^2e^{-\rho^2u^2}\,du
<0.
\]

For \(\rho\ge1\),

\[
\left(\frac{e^{-1}}{\rho}\right)^c
\le
g_c^{\rm box}(\rho)
\le
\left(\frac{\sqrt\pi}{2\rho}\right)^c.
\]

## 6.3 What is robust and what is closure-dependent

Robust within both declared controls:

* added nondegenerate normal directions suppress the average profile;
* suppression strengthens with larger \(r/\Delta\);
* large-\(\rho\) decay carries one inverse power per normal direction.

Closure-dependent:

* the exact constants;
* ball versus box ordering;
* correlations and anisotropic tails;
* weight near \(b=0\);
* the continuation of the amplitude into the small-impact core.

GKM equation (5) is stated for \(b^2\gg Y\alpha'\), while the ball and box
controls include \(b=0\).  The full-support integrations are therefore
controlled profile closures, not direct integration of a source-valid formula
over its proved domain.

## 6.4 Fixed \(T^9\) versus effective-source families

For the actual fixed source geometry,

\[
c=9-a.
\]

There is no rank-three jet “inside” a one- or two-dimensional source.  In a
predeclared family with spatial carrier dimension \(\ell\), maximal F1 rank is

\[
a_\ell=\min(\ell,3),
\]

so only that family gives

\[
c_\ell=\ell-a_\ell=(\ell-3)_+.
\]

This is not a visible-\(m\) formula.  It becomes relevant to \(m\) only after
anonymous reconstruction establishes the relationship between the effective
source family and the response-visible branch.

---

# 7. Three-ceiling versus strict three-selection

In the declared effective-source family with rank-three preparation for
\(\ell\ge3\), impact codimension distinguishes the upper side:

\[
\ell>3
\quad\Longrightarrow\quad
c_\ell=\ell-3>0
\quad\Longrightarrow\quad
g_{c_\ell}(\rho)<1.
\]

For \(\ell=1,2,3\),

\[
c_\ell=0,
\qquad
g_{c_\ell}=1.
\]

The impact mechanism therefore gives an upper ceiling but no lower-side
winner.

To state a quantitative sufficient condition, suppose a declared comparison
model factors a finite-horizon score as

\[
S_\ell=L_\ell U_\ell,
\]

where \(L_\ell\) contains lower-side preparation, growth and arrival factors,
and \(U_\ell\) contains impact-codimension suppression.  Suppose interval
bounds satisfy

\[
\underline L_3
-
\max(\overline L_1,\overline L_2)
\ge\delta_{\rm low}>0,
\]

and

\[
\underline L_3
-
\sup_{\ell\ge4}
\overline L_\ell\,
\overline U_\ell
\ge\delta_{\rm high}>0,
\]

with

\[
\overline U_\ell
\le
\overline g_{\ell-3}(\rho)
\quad(\ell\ge4).
\]

Then

\[
S_3-
\sup_{\ell\ne3}S_\ell
\ge
\min(\delta_{\rm low},\delta_{\rm high})>0.
\]

This is a sufficient factorized comparison condition, not a substitute for
the existing entrant strict-residence calculation.  The upper-side
\(g_c\) structure is source-motivated and exact in the declared profile
closures.  The lower-side \(L_\ell\) ordering is not identified by the cited
sources.  Therefore strict three-selection is not proved.

Moreover, the straight opposite-winding stratum is rank two.  For that
stratum the normal codimension is \(\ell-2\), so even the conditional
three-ceiling compiler cannot be applied until a non-collinear preparation
law is supplied.

---

# 8. The preparation law \(\mu_0\)

The source-to-return kernel does not determine its initial preparation.
Specify a reference measure before specifying a density.  In a finite
gauge-fixed regulator one may use schematically

\[
d\lambda_{\rm ref}
=
d\lambda_{\rm bg}\,d\pi_{\rm bg}\,
\prod_s d\lambda_{{\rm ws},s}\,
\prod_s \#(dq_s)\,
\Omega_R(E_R)\,dE_R\,
d\nu_h,
\]

where:

* \(d\lambda_{\rm bg}\,d\pi_{\rm bg}\) is a registered phase-space measure for
  background geometry;
* \(d\lambda_{{\rm ws},s}\) is a gauge-fixed worldsheet Liouville measure;
* \(\#(dq_s)\) is counting measure on discrete charge/winding sectors;
* \(\Omega_R(E_R)dE_R\) is a reservoir reference measure;
* \(d\nu_h\) is a declared history measure.

Then

\[
\mu_0(dX)=f_0(X)\lambda_{\rm ref}(dX),
\qquad
f_0\ge0,
\qquad
\int f_0\,d\lambda_{\rm ref}=1.
\]

Exchangeability must be a symmetry of both the reference measure and \(f_0\).
The regulator must include a convergence or cutoff statement.

Uniformly weighting whatever states a discretizer happens to create is not a
continuum preparation law.  It changes when cells are refined, when different
coordinates are used, or when one physical cell is represented by more
bookkeeping states.

The smallest missing object for the present rank gate is the marginal of
\(\mu_0\) and the return law on local event jets:

\[
\nu_X(dj)
=
\Pr(dj\mid\text{global winding/source state }X).
\]

It must determine the weight of rank-two straight events, rank-three wiggled
events, and the \(\sigma_3\) tail.

---

# 9. Executable probe

The delivered files are:

```text
artifacts/0016/probe_0016.py
artifacts/0016/probe_report.json
```

The probe has no input or branch named `m`, response rank, target rank, active
mask, response cell, or band.

Commands actually run on the generated LF files were:

```text
python3 -m py_compile artifacts/0016/probe_0016.py
python3 artifacts/0016/probe_0016.py --help
python3 artifacts/0016/probe_0016.py \
  --output artifacts/0016/probe_report.json
python3 artifacts/0016/probe_0016.py \
  --check --output artifacts/0016/probe_report.json
```

All exited zero.

A fresh copy of both files was then converted to CRLF and the following were
run:

```text
python3 -m py_compile artifacts/0016/probe_0016.py
python3 artifacts/0016/probe_0016.py --help
python3 artifacts/0016/probe_0016.py \
  --check --output artifacts/0016/probe_report.json
```

All exited zero.  The `--check` path parses JSON in universal-newline mode and
compares canonical semantic JSON, not raw worktree bytes.

The observed probe result was:

```text
status                    PASS
Gram controls             6
strict monotonicity checks 756
canonical report payload  30aac9cd344c1101c5b68cdc79b1c5c83078ae0d9f2349886a8a6e51725e2be3
LF probe source SHA-256    4fff9053d0f641b8f50594b96688a810afcf699c33e1254803617a50b42c1d4e
LF report file SHA-256     ed02cd1373dc1f5898d27229025f25e06c0245cbe235c4d465e2e9e12400d3c8
```

The six controls are:

1. non-collinear rank three;
2. near-opposite rank three with
   \(\sigma_3\approx7.07\times10^{-3}\);
3. straight same-cycle opposite winding, rank two;
4. relative velocity in the tangent plane, rank two;
5. rank-three jet with rescaled \(H_e\), showing unchanged rank but changed
   \(\sigma_3\);
6. fully collinear rank one.

---

# 10. Exact next composition and falsifiable calculation

The next composition remains

\[
(\mu_0,\mathscr P_X)
\longrightarrow
\text{age-augmented scheduled/return process}
\longrightarrow
\text{anonymous }A,R,B,C,M
\longrightarrow
Z_0,\ldots,Z_9
\]

\[
\longrightarrow
\text{entrant strict residence and leakage}
\longrightarrow
\text{visible cone/signature package}.
\]

No source-axis count may be substituted for \(m\).

The next falsifiable calculation is:

1. prepare or infer two source ensembles with the same global opposite winding:
   a straight rank-two ensemble and a locally wiggled ensemble;
2. measure the joint distribution of
   \((\sigma_3(\widehat J_e),T,b,\chi,h')\);
3. test whether the wiggled ensemble has a positive rank-three weight or
   controlled tail stable across source-valid scales;
4. compile both laws into the same age-augmented process;
5. feed only pre-quotient responses to the anonymous reconstruction stack;
6. compute all ten entrant strict-residence and leakage scores;
7. test whether a positive rank-three margin appears and whether it disappears
   when the \(\sigma_3\) preparation weight is reduced.

This distinguishes the rank-two and rank-three source hypotheses without
putting the desired response rank into the kernel.

---

# 11. Required conclusion

1. **Local kinematic-rank theorem:** proved coordinate-freely, with a registered
   \(G,H_e\) margin.  Straight same-cycle opposite winding is rank at most two.
2. **Fixed-arity superselection:** proved exactly.  The present finite
   constructor cannot select arity three.
3. **Impact-codimension suppression:** proved for the two declared profile
   controls, with strict monotonicity and large-\(\rho\) bounds.
4. **Verdict:** `three-ceiling`, conditional on a rank-three event-jet
   preparation and declared profile closure; no strict three-selection and no
   visible-\(m\) ceiling.
5. **Smallest unidentified component:** the conditional event-jet preparation
   \(\nu_X(dj)\), especially rank mixture and
   \(\sigma_3(\widehat J_e)\) tail; the full closure also needs
   \(\mathscr P_X\) and \(\mu_0\).
6. **Next falsifiable calculation:** measure/derive the joint event-jet and
   return law, compile it without rank labels, reconstruct \(Z_0,\ldots,Z_9\),
   and compare entrant strict residence and leakage.

The present F1/\(T^9\) branch assumes a Lorentzian \(9+1\) background.  It does
not derive one time direction or Lorentzian signature.

---

# Primary sources

1. B. Greene, D. Kabat and S. Marnerides, *Dynamical Decompactification and
   Three Large Dimensions*, arXiv:0908.0955,
   DOI:10.1103/PhysRevD.82.043528.
2. B. Greene, D. Kabat and S. Marnerides, *On three dimensions as the
   preferred dimensionality of space via the Brandenberger--Vafa mechanism*,
   arXiv:1212.2115, DOI:10.1103/PhysRevD.88.043527.
3. M. G. Jackson, N. T. Jones and J. Polchinski, *Collisions of Cosmic F- and
   D-strings*, arXiv:hep-th/0405229,
   DOI:10.1088/1126-6708/2005/10/013.
4. R. Easther, B. R. Greene, M. G. Jackson and D. Kabat, *String windings in
   the early universe*, arXiv:hep-th/0409121,
   DOI:10.1088/1475-7516/2005/02/009.
5. R. Danos, A. R. Frey and A. Mazumdar, *Interaction Rates in String Gas
   Cosmology*, arXiv:hep-th/0409162,
   DOI:10.1103/PhysRevD.70.106010.
6. S. Alexander, R. Brandenberger and D. Easson, *Brane Gases in the Early
   Universe*, arXiv:hep-th/0005212,
   DOI:10.1103/PhysRevD.62.103509.
