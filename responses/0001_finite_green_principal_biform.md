---
brief: 0001
source: browser-hosted GPT
captured: 2026-07-22
status: proposed
---

# Response 0001 — Jet-null Green tomography and the principal-ray theorem

## Executive result

The bottleneck has an exact finite-dimensional answer.

One should not invert a finite matrix representation of \(G\) and call the
result the generator.  The sufficient statistic for the principal biform at a
regular physical character \(x\) is instead the space of **linear combinations
of measured Green responses whose value and first differential germ vanish at
\(x\)**.

Such combinations are pure second-order jets.  Every lower-order part of a
candidate \(L\in\operatorname{Diff}^{\le 2}\) vanishes on them.  The equation
\(LG=I\) therefore turns them directly into linear constraints on the
principal biform.

This gives a coordinate-free theorem:

\[
\mathcal Q_D
=
\{q\in K_x^*:q\circ H_x=\beta_x\},
\]

where

\[
K_x=\mathfrak m_x^2/\mathfrak m_x^3
\simeq \operatorname{Sym}^2T_x^{*,\mathrm{evt}},
\]

\(H_x\) is the pure-quadratic jet map obtained from lower-jet-null Green
combinations, and \(\beta_x\) is the corresponding source fiber.

For a scalar field in visible event dimension \(d\), put

\[
p_d=\dim K_x=\frac{d(d+1)}2.
\]

Then, before any prior artificially pins coefficients:

- \(\operatorname{rank}H_x=p_d\) identifies \(Q_x\) including scale;
- \(\beta_x=0\) and \(\operatorname{rank}H_x=p_d-1\) identify exactly one
  conformal principal ray, while leaving its scale free;
- any smaller rank leaves non-conformal second-order generators exactly
  data-indistinguishable;
- lower-order coefficients remain nonunique whenever the measured response
  first jets fail to span the complete first-jet space.

Thus a four-dimensional scalar germ requires nine independent homogeneous
jet-null quadratic response directions to identify a conformal principal
biform, and a tenth independent direction to determine its normalization.

The bounded search over candidate generators is still needed to certify
existence, nondegeneracy, differential order and class membership.  It is not
needed to manufacture the principal ray once the jet-null rank condition is
met.

---

## 1. Registered finite Green experiment

### 1.1 Event and field germs already supplied by the previous stage

Fix a regular physical character \(x\) of the protected differential response
algebra \(\mathcal A^\infty\).  Let

\[
\mathcal O_x=(\mathcal A^\infty)_x,
\qquad
\mathfrak m_x=\ker x.
\]

For the scalar case define

\[
J_x^2=\mathcal O_x/\mathfrak m_x^3,
\qquad
J_x^1=\mathcal O_x/\mathfrak m_x^2,
\qquad
K_x=\mathfrak m_x^2/\mathfrak m_x^3.
\]

There is an intrinsic exact sequence

\[
0\longrightarrow K_x
\longrightarrow J_x^2
\xrightarrow{\pi_x}J_x^1
\longrightarrow 0.
\]

Regularity gives the multiplication isomorphism

\[
K_x\simeq
\operatorname{Sym}^2(\mathfrak m_x/\mathfrak m_x^2)
=
\operatorname{Sym}^2T_x^{*,\mathrm{evt}}.
\]

No splitting of this sequence is canonical or required.

An order-\(\le2\) scalar generator germ defines

\[
\ell_{L,x}:J_x^2\longrightarrow\mathbb R,
\qquad
\ell_{L,x}(j_x^2a)=(La)(x).
\]

Its principal functional is the restriction

\[
q_{L,x}=\ell_{L,x}|_{K_x}\in K_x^*.
\]

For \(a,b\in\mathfrak m_x\),

\[
q_{L,x}([ab])
=
( L(ab))(x)
=
2Q_{L,x}(da,db).
\]

Consequently the projective class of \(q_{L,x}\) is exactly the conformal
class of the principal biform \(Q_{L,x}\).

### 1.2 Raw source, gate and readout operations

Let \(S_0\) be a finite list of registered source seeds and let
\(g_\alpha\in\mathcal A^\infty\) be registered scalar response functions.
Source gating is the physical operation

\[
s\longmapsto M_{g_\alpha}s.
\]

Let \(h_\gamma\in\mathcal A^\infty\) be registered output gates and let
\(\rho_i\) be registered linear readouts.  The raw Green data are the finite
tensor

\[
Y_{(i,\gamma),(\alpha,j)}
=
\rho_i\!\left(
M_{h_\gamma}\,
G\,
M_{g_\alpha}s_j
\right).
\]

Arbitrary finite source superpositions and readout pairings are obtained by
right and left multiplication of \(Y\).  The gates are response-algebra
multipliers.  They are not target-space bump functions, and no support,
distance, adjacency or coordinate label is supplied.

Write \(W\) for the finite coefficient space of prepared gated sources and

\[
S:W\longrightarrow E_{\mathrm{src}}
\]

for the registered source map.

### 1.3 Exact criterion for operational recovery of a response 2-jet

Let \(\mathcal V\) be the declared finite response-mode space for this
truncation, and let

\[
\mathcal R:\mathcal V\longrightarrow\mathbb R^M
\]

be the map formed by all registered output-gated readouts.

The response 2-jet is operationally determined from those readouts if and only
if

\[
\ker(\mathcal R|_{\mathcal V})
\subseteq
\ker(j_x^2|_{\mathcal V}).
\tag{1}
\]

Equivalently, there is a unique linear map on the observed range,

\[
T_x:\mathcal R(\mathcal V)\longrightarrow J_x^2,
\qquad
T_x\mathcal R=j_x^2.
\]

Condition (1) is a readout-frame completeness statement.  It does not assume a
manifold coordinate chart.  If it fails for any data-consistent truncated
response model, the principal-symbol result is inconclusive.

When it holds, the measured Green response-jet map is

\[
U_x
=
j_x^2GS
=
T_xY:
W\longrightarrow J_x^2.
\]

The registered source fiber is

\[
B_x
=
x\circ S:
W\longrightarrow\mathbb R.
\]

A candidate local generator germ is Green-consistent at \(x\) precisely when

\[
\ell_{L,x}\circ U_x=B_x.
\tag{2}
\]

Equation (2) is only a finite family of local inverse equations.  It does not
identify a global unbounded \(L\), and no inverse of the finite data matrix
\(Y\) is used.

---

## 2. Main theorem: the jet-null Green quotient

### Theorem 1 — Finite Green principal-observability theorem

Let

\[
U:W\to J^2,\qquad B:W\to\mathbb R
\]

be exact finite response-jet and source-fiber maps at a regular scalar
character.  Let

\[
0\to K\to J^2\xrightarrow{\pi}J^1\to0
\]

be the intrinsic second-jet filtration.  Define the lower-jet-null experiment
space

\[
Z=\ker(\pi U),
\]

the induced pure-quadratic response map

\[
H=U|_Z:Z\to K,
\]

and the corresponding source functional

\[
\beta=B|_Z:Z\to\mathbb R.
\]

Let

\[
\mathfrak F(U,B)
=
\{\ell\in(J^2)^*:\ell U=B\}.
\]

Then the set of principal functionals of all data-consistent second-order
generator germs is exactly

\[
\boxed{
\mathcal Q(U,B)
=
\{\ell|_K:\ell\in\mathfrak F(U,B)\}
=
\{q\in K^*:qH=\beta\}.
}
\tag{3}
\]

In particular:

1. **Generator-class consistency**

   A local order-\(\le2\) germ exists if and only if

   \[
   \beta|_{\ker H}=0,
   \]

   equivalently \(\beta\in\operatorname{im}H^*\).

2. **Exact principal identification**

   If \(p=\dim K\), the principal functional is unique, including scale, if
   and only if

   \[
   \operatorname{rank}H=p.
   \]

3. **Conformal-only identification**

   Suppose the declared class excludes \(q=0\).  The Green data identify one
   and only one projective principal ray while leaving its scale free if and
   only if

   \[
   \boxed{
   \beta=0,
   \qquad
   \operatorname{rank}H=p-1.
   }
   \tag{4}
   \]

   The identified ray is

   \[
   [q]=\mathbb P\bigl((\operatorname{im}H)^\perp\bigr).
   \]

4. **Exact non-identifiability below rank**

   If

   \[
   \operatorname{rank}H\le p-2,
   \]

   then the data-consistent principal set contains at least a
   two-dimensional linear ambiguity when \(\beta=0\), and an affine ambiguity
   of dimension at least two in general.  For any non-pinning coefficient
   class containing a relative neighborhood of its feasible points, there are
   two data-consistent order-\(\le2\) germs with non-proportional principal
   biforms.

   If \(\operatorname{rank}H=p-1\) but \(\beta\ne0\), the feasible principal
   set is an affine line not passing through the origin, and again contains
   non-proportional biforms.

5. **Lower-order nonuniqueness**

   After fixing any feasible principal functional, the remaining lower-order
   ambiguity is an affine space with direction

   \[
   (\operatorname{im}\pi U)^\perp\subseteq(J^1)^*.
   \]

   Hence its dimension is

   \[
   \dim J^1-\operatorname{rank}(\pi U).
   \tag{5}
   \]

   A declared gauge subspace
   \(\mathscr G\subseteq(\operatorname{im}\pi U)^\perp\) may be quotiented
   without altering the principal result.

### Proof

Necessity of (3) is immediate.  If
\(\ell U=B\) and \(z\in Z\), then \(Uz\in K\), so

\[
(\ell|_K)(Hz)=\ell(Uz)=Bz=\beta z.
\]

For sufficiency, take \(q\in K^*\) satisfying \(qH=\beta\), and extend it
arbitrarily to \(\widetilde q\in(J^2)^*\).  Define

\[
r=B-\widetilde q\,U.
\]

For \(z\in\ker(\pi U)\),

\[
r(z)=\beta z-q(Hz)=0.
\]

Therefore \(r\) factors through \(\operatorname{im}(\pi U)\).  Extend the
resulting functional on \(\operatorname{im}(\pi U)\) to some
\(n\in(J^1)^*\), and put

\[
\ell=\widetilde q+n\pi.
\]

Then \(\ell U=B\) and \(\ell|_K=q\), proving (3).

The feasible principal set is either empty or

\[
q_0+(\operatorname{im}H)^\perp.
\]

All rank and projective statements follow from this affine-space formula.
Equation (5) follows because two lower-order lifts differ by a functional on
\(J^1\) annihilating \(\operatorname{im}\pi U\).

### Interpretation

The theorem identifies the exact piece of finite Green data that can see the
principal biform:

\[
\boxed{
\text{principal information}
=
\text{quadratic jets of response superpositions whose lower jets cancel}.
}
\]

The complete finite matrix \(G\) is not the sufficient statistic.  The
jet-null syzygy

\[
Z_x=\ker(\pi_xU_x)
\]

and its image

\[
H_x=U_x(Z_x)\subseteq K_x
\]

are.

For visible event dimension \(d\),

\[
p_d=\frac{d(d+1)}2.
\]

Therefore a data-driven conformal identification requires at least

\[
p_d-1
\]

independent homogeneous pure-quadratic response directions.  In \(d=4\) the
number is nine.

If the current rank is \(r\), the smallest possible number of additional
independent jet-null directions needed to identify a ray is

\[
N_{\mathrm{add}}^{\min}
=
\max\{0,p_d-1-r\}.
\tag{6}
\]

One further independent quadratic equation with nonzero source fiber fixes the
scale.

---

## 3. Matrix form and basis invariance

Choose any basis of \(J^2\) adapted to the filtration and write

\[
U=
\begin{pmatrix}
U_1\\
U_2
\end{pmatrix},
\]

where \(U_1\) represents the \(J^1\) quotient and \(U_2\) represents \(K\).
Let the columns of \(N\) form a basis of

\[
\ker U_1.
\]

Then

\[
H=U_2N,
\qquad
\beta=BN.
\]

Writing a principal functional as a column \(q\), the effective equations are

\[
H^\top q=\beta^\top.
\tag{7}
\]

The conditions of Theorem 1 become:

\[
\operatorname{rank}
\begin{pmatrix}
H\\
\beta
\end{pmatrix}
=
\operatorname{rank}H
\]

for consistency,

\[
\operatorname{rank}H=p
\]

for exact identification, and

\[
\beta=0,\qquad \operatorname{rank}H=p-1
\]

for conformal-only identification.

Equivalently, if a general finite inverse system is written as

\[
C_Nn+C_Qq=b,
\]

with \(n\) denoting lower-order nuisance coefficients, pass to the quotient

\[
\mathcal Y/\operatorname{im}C_N.
\]

The induced map

\[
\overline C_Q:
K^*\longrightarrow
\mathcal Y/\operatorname{im}C_N
\]

is independent of any splitting between lower and principal coefficients.
The principal feasible set is

\[
\overline C_Q^{-1}([b]).
\]

This is the invariant version of nuisance elimination.

### Invariance

1. A change of prepared-source basis
   \(A\in GL(W)\) sends

   \[
   U\mapsto UA,\qquad B\mapsto BA.
   \]

   It only reparametrizes \(Z\); the subspace
   \(\operatorname{im}H\subseteq K\) and the principal ray are unchanged.

2. A change of registered-readout basis left-multiplies the raw matrix \(Y\).
   When the readout-frame condition (1) holds, the reconstructed jet map
   \(U=j_x^2GS\) is unchanged.

3. A response-generator change induces a filtered jet isomorphism

   \[
   \Phi:J^2\to J^2
   \]

   preserving \(K\).  It sends

   \[
   H\mapsto\Phi_KH,
   \qquad
   q\mapsto(\Phi_K^{-1})^*q.
   \]

   Ranks, projective uniqueness and the resulting cone are invariant.

4. An operator-coordinate change merely right-multiplies the coefficient
   matrices by an invertible matrix.  It cannot change the quotient rank.

A bounded class \(B_L\) can intersect a non-identifiable affine principal
fiber in a single point by prior fiat.  Such a result is class-driven rather
than Green-data-driven.  The rank statements above are necessary and
sufficient for data identification when the principal projection of \(B_L\)
is locally non-pinning, apart from declared nonzero, nondegeneracy and
coefficient-size gaps.  For an arbitrary bounded class, the ultimate criterion
remains

\[
\mathbb P\{q_L:L\text{ is data-consistent in }B_L\}
\]

being a singleton.

---

## 4. Smallest exact scalar toy

### 4.1 Why this toy is minimal

For \(d=1\), every nonzero quadratic form is already conformally equivalent, so
the problem is trivial.  The first nontrivial case is therefore

\[
d=2.
\]

A scalar second jet then has dimension

\[
1+d+\frac{d(d+1)}2=1+2+3=6.
\]

The projective principal space has dimension two, so two independent
homogeneous quadratic equations are the minimum needed to identify a ray.

### 4.2 Hidden simulator

Use a proof chart \((t,x)\) only inside the simulator and the response-mode
space

\[
V=\operatorname{span}
\left\{
1,\ t,\ x,\ \frac{t^2}{2},\ tx,\ \frac{x^2}{2}
\right\}.
\]

The inference routine receives a randomly transformed response algebra,
anonymous source gates and anonymous readouts; it is not told that the hidden
generators are \(t,x\).

Let

\[
L_0=I+\partial_t^2-\partial_x^2.
\]

On \(V\), the second-derivative part squares to zero, so

\[
G_0=L_0^{-1}
=
I-\partial_t^2+\partial_x^2.
\]

Use one scalar source seed and two response-function gates

\[
g_1=tx,
\qquad
g_2=\frac{t^2+x^2}{2}.
\]

Prepare

\[
s_1=g_1,
\qquad
s_2=g_2.
\]

Both gates are annihilated by
\(\partial_t^2-\partial_x^2\), hence

\[
G_0s_1=u_1=tx,
\qquad
G_0s_2=u_2=\frac{t^2+x^2}{2}.
\]

At the character \(x_0=(0,0)\),

\[
j_{x_0}^1u_1=j_{x_0}^1u_2=0,
\qquad
s_1(x_0)=s_2(x_0)=0.
\]

Thus both measured response columns are homogeneous jet-null probes.

For a candidate local germ write

\[
\theta=
(c,b_t,b_x,q_{tt},q_{tx},q_{xx}),
\]

with principal matrix

\[
Q=
\begin{pmatrix}
q_{tt}&q_{tx}\\
q_{tx}&q_{xx}
\end{pmatrix}.
\]

The two Green equations at \(x_0\) are

\[
2q_{tx}=0,
\qquad
q_{tt}+q_{xx}=0.
\]

Equivalently,

\[
C_{\mathrm{conf}}\theta=0,
\qquad
C_{\mathrm{conf}}
=
\begin{pmatrix}
0&0&0&0&2&0\\
0&0&0&1&0&1
\end{pmatrix}.
\tag{8}
\]

Therefore

\[
Q=\lambda
\begin{pmatrix}
1&0\\
0&-1
\end{pmatrix}.
\]

All three lower-order coefficients \(c,b_t,b_x\) remain completely
undetermined by these equations.  With the independent class gap

\[
|\lambda|\ge\kappa_Q>0,
\]

the data certify one nondegenerate Lorentzian conformal cone and leave only its
overall scale free.

### 4.3 Registered readout frame

Six anonymous character readouts suffice to reconstruct an unrestricted
quadratic response mode.  In the hidden chart one convenient evaluation matrix
is

\[
R=
\begin{pmatrix}
1&0&0&0&0&0\\
1&1&0&\tfrac12&0&0\\
1&0&1&0&0&\tfrac12\\
1&-1&0&\tfrac12&0&0\\
1&0&-1&0&0&\tfrac12\\
1&1&1&\tfrac12&1&\tfrac12
\end{pmatrix},
\qquad
\det R=-1.
\tag{9}
\]

The corresponding six readout characters are used only by the simulator.
The inference routine receives \(R\) as an anonymous response-algebra
evaluation frame.

The response-jet matrix and raw output matrix are

\[
U=
\begin{pmatrix}
0&0\\
0&0\\
0&0\\
0&1\\
1&0\\
0&1
\end{pmatrix},
\qquad
Y=RU=
\begin{pmatrix}
0&0\\
0&\tfrac12\\
0&\tfrac12\\
0&\tfrac12\\
0&\tfrac12\\
1&1
\end{pmatrix}.
\tag{10}
\]

Before each test, apply:

- a random filtered algebra-generator transformation;
- a random invertible source-basis transformation;
- a random invertible readout-basis transformation;
- a random permutation of all opaque apparatus labels.

The recovered principal ray must transform functorially and the verdict must
not change.

---

## 5. Exact counterexample below the rank condition

Let

\[
L_+
=
I+\partial_t^2+\partial_x^2,
\qquad
L_-
=
I+\partial_t^2-\partial_x^2.
\]

On the same quadratic response space,

\[
G_+
=
I-\partial_t^2-\partial_x^2,
\qquad
G_-
=
I-\partial_t^2+\partial_x^2.
\]

Register only the gated source

\[
s=tx.
\]

Then

\[
G_+s=tx=G_-s.
\]

Consequently every registered source superposition in
\(\operatorname{span}\{s\}\), every output response-function gate and every
linear readout pairing gives identical data for the two models.

Nevertheless,

\[
Q_+
=
\begin{pmatrix}
1&0\\
0&1
\end{pmatrix},
\qquad
Q_-
=
\begin{pmatrix}
1&0\\
0&-1
\end{pmatrix}
\]

are not conformally equivalent.

Here \(H\) has rank one, while \(p_2-1=2\).  Theorem 1 therefore predicts the
failure exactly.

The smallest repair is one additional registered source gate producing an
independent homogeneous jet-null response.  Adding

\[
g_2=\frac{t^2+x^2}{2}
\]

raises \(\operatorname{rank}H\) from one to two and identifies the Lorentzian
ray.  No target-space localization is added; only one more global
response-algebra multiplier is registered.

This counterexample also proves that complete readout tomography of one Green
column is not enough.  The missing object is quadratic response-direction
coverage, not numerical accuracy on the existing column.

---

## 6. Smallest multi-field extension

Let the physical field fiber be

\[
F_x\simeq\mathbb R^2.
\]

For a locally free two-field module,

\[
K_x(E)
\simeq
K_x\otimes F_x.
\]

The principal symbol is a linear map

\[
\Sigma_L:
K_x\longrightarrow\operatorname{End}(F_x),
\]

or equivalently an element

\[
\Sigma_L\in K_x^*\otimes\operatorname{End}(F_x).
\]

Prepare the two scalar jet-null modes \(u_1,u_2\) above in both independent
input polarizations \(e_1,e_2\), and pair the outputs with both independent
readout polarizations \(e_1^*,e_2^*\).  Complete field polarization means

\[
\operatorname{rank}S_F=2,
\qquad
\operatorname{rank}R_F=2.
\tag{11}
\]

The homogeneous Green equations are the matrix equations

\[
\Sigma_L(u_1)=0,
\qquad
\Sigma_L(u_2)=0.
\]

Writing

\[
\Sigma_L
\leftrightarrow
(S_{tt},S_{tx},S_{xx}),
\qquad
S_{\mu\nu}\in M_2(\mathbb R),
\]

they become

\[
2S_{tx}=0,
\qquad
S_{tt}+S_{xx}=0.
\tag{12}
\]

Hence every data-consistent principal tensor has the factorized form

\[
\boxed{
\Sigma_L
=
q_0\otimes K_F,
\qquad
q_0(\xi)=\xi_t^2-\xi_x^2,
}
\tag{13}
\]

for some \(K_F\in\operatorname{End}(F_x)\).

The conformal spacetime factor \([q_0]\) is unique although the field factor
\(K_F\), all lower-order field mixing and any registered lower-order gauge
freedom may remain nonunique.

A universal cone is certified precisely when every data-consistent field
factor obeys

\[
\sigma_{\min}(K_F)\ge\kappa_F>0.
\tag{14}
\]

Then

\[
\det \sigma_L(\xi)
=
\det(K_F)\,q_0(\xi)^2,
\]

so every physical polarization has the same characteristic cone.

Invariantly, a system principal tensor has one universal quadratic cone if and
only if its flattening across

\[
K_x^*
\quad\big|\quad
\operatorname{End}(F_x)
\]

has tensor rank one,

\[
\Sigma_L=q\otimes K_F,
\]

and the field factor is invertible on the declared physical polarization
quotient.  The universal cone is identifiable if this holds for every
data-consistent \(L\) and all their \(q\)-factors determine the same
projective point.

The source/readout completeness in (11) is necessary.  If only the first field
is excited and read out, the two symbols

\[
\begin{pmatrix}
q_0&0\\
0&q_0
\end{pmatrix},
\qquad
\begin{pmatrix}
q_0&0\\
0&q_1
\end{pmatrix},
\]

with \(q_1\not\propto q_0\), are exactly indistinguishable on the registered
channel, while only the first has a universal cone.

For \(r\) fields and a scalar homogeneous response subspace
\(H_0\subset K_x\), complete polarization data give

\[
\operatorname{im}H=H_0\otimes F_x.
\]

If \(\operatorname{codim}H_0=1\), every feasible principal tensor is
automatically

\[
q_0\otimes K_F.
\]

Thus the scalar jet-null design and field-polarization completeness separate
cleanly.

---

## 7. Finite-noise margin

### 7.1 Effective nuisance-quotient matrix

In an adapted numerical basis write the reconstructed response-jet matrix as

\[
U=
\begin{pmatrix}
U_1\\
U_2
\end{pmatrix},
\]

and let

\[
C_N=U_1^\top,
\qquad
C_Q=U_2^\top.
\]

Assume the nonzero singular values of \(C_N\) have the independent gap

\[
\sigma_{\min}^+(C_N)\ge\gamma_1>0.
\]

Let

\[
P_\perp
=
I-C_NC_N^\dagger
\]

be the projector onto the quotient by lower-order data effects.  Define

\[
A=P_\perp C_Q,
\qquad
y=P_\perp b.
\tag{15}
\]

This is a numerical representative of the invariant quotient map
\(\overline C_Q\).  Source and readout basis changes only replace it by
equivalent row and column coordinates.

Suppose interval propagation from the raw Green/readout data gives

\[
\|A-\widehat A\|_2\le\eta_A,
\qquad
\|y-\widehat y\|_2\le\eta_y.
\]

Let the declared principal coefficient bound be

\[
\kappa_Q\le\|q\|_2\le B_Q.
\]

Put

\[
r_{\mathrm{eff}}
=
\eta_y+\|\widehat y\|_2+\eta_AB_Q+\varepsilon_{\mathrm{inv}},
\tag{16}
\]

where \(\varepsilon_{\mathrm{inv}}\) is the allowed residual in the finite
local inverse equations.

Let

\[
\widehat\sigma_1\ge\cdots\ge\widehat\sigma_p
\]

be the singular values of \(\widehat A\), and let \(\widehat v\) be a unit
right singular vector for \(\widehat\sigma_p\).  Every feasible principal
vector satisfies

\[
\boxed{
\sin\angle([q],[\widehat v])
\le
\frac{r_{\mathrm{eff}}}
{\kappa_Q\,\widehat\sigma_{p-1}}.
}
\tag{17}
\]

Thus a certified projective tube of angular radius \(\delta\) is obtained
whenever

\[
r_{\mathrm{eff}}
<
\kappa_Q\,\widehat\sigma_{p-1}\sin\delta.
\tag{18}
\]

The projective diameter of the complete feasible principal set is then at most
\(2\delta\).

For the exact scalar toy,

\[
A=
\begin{pmatrix}
0&2&0\\
1&0&1
\end{pmatrix}
\]

has nonzero singular values

\[
2,\qquad\sqrt2.
\]

The clean conformal direction is therefore separated by the explicit gap
\(\sqrt2\).

### 7.2 Signature margin

Normalize the representative \(\widehat Q\) of the recovered ray.  Propagate
(17) to an operator-norm bound

\[
\|Q-\widehat Q\|_{\mathrm{op}}\le\delta_Q
\]

after the allowed sign or scale normalization.  If

\[
\min_i|\lambda_i(\widehat Q)|>\delta_Q,
\tag{19}
\]

then every feasible \(Q\) has the same inertia by Weyl's inequality.

For a two-field system, also require every feasible field factor to satisfy
the invertibility margin (14).  If interval data permit either a singular
field factor or a second independent spacetime factor, the universal-cone
claim is inconclusive.

### 7.3 Exact versus finite-resolution claim

With nonzero data intervals, exact equality of all latent conformal rays is
usually stronger than the data support.  The operational claim should be
parameterized by a declared tolerance:

\[
P_{\delta,\kappa,\mathcal I}:
\quad
\text{all feasible }Q_L
\text{ lie in one projective tube of radius }\delta,
\quad
\|Q_L\|\ge\kappa,
\quad
\operatorname{Inertia}(Q_L)=\mathcal I.
\]

The exact conformal theorem is the case \(\delta=0\).  No finite-noise
procedure may silently replace a nonzero projective tube by an exact ray.

---

## 8. Three-state decision rule

Let

\[
\mathfrak L_D(B_L)
\]

be the set of bounded order-\(\le2\) generator germs, response jets and source
fibers consistent with all raw intervals and all registered module
operations.

For a declared target property \(P\), such as a unique Lorentzian principal
tube or a universal two-field cone, return exactly one of:

1. **Certified within class**

   if

   \[
   \mathfrak L_D(B_L)\ne\varnothing
   \]

   and every member satisfies \(P\).

2. **Class excluded**

   if either the complete declared generator class is inconsistent,

   \[
   \mathfrak L_D(B_L)=\varnothing,
   \]

   or the consistent set is nonempty but has empty intersection with the
   requested target subclass.  The report must state which of these two
   exclusion reasons occurred.

3. **Inconclusive**

   if some consistent members satisfy \(P\) and others do not, or if their
   principal rays exceed the declared projective tolerance.

A rank deficit is not itself evidence for a different signature.  If it admits
both Lorentzian and non-Lorentzian candidates, the correct output is
inconclusive.

The response realization bound \(n_J\) may certify that the registered Green
columns and context family are complete within \(\mathcal C_R\).  It does not
supply the local generator bound \(B_L\), the jet-readout gap, the rank of
\(H_x\), or the visible event dimension.

---

## 9. Seven-day kill test

### Day 1 — Exact filtered-jet implementation

Implement the six-dimensional scalar jet model and verify symbolically that

\[
L_\pm G_\pm=I
\]

on \(V\), that the two positive Green columns produce (8), and that the
principal feasible set is exactly

\[
\lambda(1,0,-1).
\]

Brute-force the affine solution space and compare it with Theorem 1.

### Day 2 — Coordinate and apparatus anonymity

Run at least \(10^4\) exact trials with:

- random invertible linear changes of \(T_x^*\);
- random quadratic corrections in the response-generator change modulo
  \(\mathfrak m_x^3\);
- random source and readout basis changes;
- random token and channel permutations.

The transformed ray must agree with the functorial pullback of the original
ray, and the verdict must never change.

### Day 3 — Exact no-go and minimal repair

Run the one-source counterexample with \(L_+\) and \(L_-\).  Confirm that every
registered raw datum agrees and that the algorithm returns inconclusive.

Add only the second gate \(g_2\).  Confirm that the rank rises from one to two
and that the Lorentzian ray is then certified.

### Day 4 — Lower-order and class-bound separation

Randomize all lower-order coefficients in a bounded box while preserving the
same two local Green equations.  The principal ray must remain fixed and the
lower-order feasible dimension must equal (5).

Tighten a prior artificially until it pins a principal coefficient.  The
implementation must label the resulting uniqueness as class-driven rather
than data-driven.

### Day 5 — Two-field universal cone

Use

\[
U_F=U\otimes I_2,
\qquad
Y_F=Y\otimes I_2.
\]

With complete input and output polarization frames, verify (12)--(13) for
random invertible \(K_F\) and random field-basis changes.

Then remove one source polarization or one readout polarization and insert an
unobserved non-conformal second-field symbol.  Universal-cone certification
must fail.

### Day 6 — Interval and adversarial noise

Add interval perturbations to \(Y\), the readout frame and source
calibrations.  Compare the true projective error with the bound (17).

Required behavior:

- below the certified gap, no false principal-ray or signature certificate;
- near gap closure, transition to inconclusive;
- never a direct transition from the correct certified signature to an
  incorrect certified signature.

Use adversarial perturbations aligned with the smallest nonzero singular
vector, not only isotropic Gaussian noise.

### Day 7 — Exhaustive finite-model audit

For the scalar \(p=3\) toy, enumerate or optimize over the complete bounded
feasible coefficient polytope.  Directly maximize all projective minors

\[
q_iq'_j-q_jq'_i
\]

over pairs of feasible \(q,q'\).  Compare the result with the rank and
singular-gap certificate.

Repeat for the two-field tensor flattening and search explicitly for a
rank-\(\ge2\) spacetime factor consistent with the data.

### Hard stop conditions

Stop the principal-cone paper and retreat to event-germ reconstruction if any
of the following occurs:

1. the exact positive toy admits a non-proportional feasible principal form;
2. the one-source counterexample is ever certified;
3. a filtered response-generator change alters the verdict;
4. a feasible principal form lies outside the certified interval tube;
5. incomplete field polarization data certify a universal cone;
6. the method requires a hidden distance, support relation, adjacency graph or
   target-coordinate bump;
7. the implementation obtains uniqueness only by inverting the finite Green
   matrix or by using \(n_J\) as a generator-class bound.

If exact algebra succeeds but the interval bound is too weak for useful noise
levels, retain Theorem 1 and pivot the experimental design toward maximizing
the jet-null singular gap rather than abandoning the formalism.

---

## 10. Minimal simulation matrices

Use the ordered response-mode basis

\[
e=
\left(
1,\ t,\ x,\ \frac{t^2}{2},\ tx,\ \frac{x^2}{2}
\right).
\]

The derivative matrices, with columns denoting images of basis vectors, are

\[
D_t=
\begin{pmatrix}
0&1&0&0&0&0\\
0&0&0&1&0&0\\
0&0&0&0&1&0\\
0&0&0&0&0&0\\
0&0&0&0&0&0\\
0&0&0&0&0&0
\end{pmatrix},
\]

\[
D_x=
\begin{pmatrix}
0&0&1&0&0&0\\
0&0&0&0&1&0\\
0&0&0&0&0&1\\
0&0&0&0&0&0\\
0&0&0&0&0&0\\
0&0&0&0&0&0
\end{pmatrix}.
\]

Set

\[
L_\pm=I+D_t^2\pm D_x^2,
\qquad
G_\pm=I-D_t^2\mp D_x^2.
\]

For the positive Lorentzian toy use

\[
U=
\begin{pmatrix}
0&0\\
0&0\\
0&0\\
0&1\\
1&0\\
0&1
\end{pmatrix},
\qquad
S=U,
\qquad
B=(0,0),
\]

together with the readout matrix \(R\) in (9).

For the exact counterexample use the single column

\[
U_{\mathrm{bad}}
=
\begin{pmatrix}
0\\0\\0\\0\\1\\0
\end{pmatrix},
\qquad
S_{\mathrm{bad}}=U_{\mathrm{bad}}.
\]

For two fields use Kronecker products with \(I_2\).

These matrices are sufficient to implement every exact claim in this response.

---

## 11. Proposed architectural change

Replace the primary computational plan

\[
\text{fit all bounded }L
\longrightarrow
\text{compare all }Q_L
\]

by

\[
\boxed{
\text{finite Green/readout tensor}
\longrightarrow
\text{response 2-jets}
\longrightarrow
\text{lower-jet-null syzygy }Z_x
\longrightarrow
H_x
\longrightarrow
\text{principal ray or exact rank no-go}.
}
\]

The bounded \(L\)-search then becomes a verification layer:

- does a local order-\(\le2\) lift exist?
- is the inferred principal form nonzero and nondegenerate?
- does it obey the coefficient and regularity bounds?
- do all field channels factor through one spacetime ray?
- is the finite-noise projective tube narrow enough to preserve inertia?

This removes the most dangerous inversion step, isolates exactly which
registered operations are missing when the answer is inconclusive, and gives a
finite experimental target for the \(3+1\) bridge:

\[
\boxed{
d_{\mathrm{evt}}=4
\quad\text{and}\quad
\operatorname{rank}H_x=9
\quad\Longrightarrow\quad
\text{one data-identified conformal principal biform at }x,
}
\]

subject to the independent nonzero, lift-existence and class bounds.

The theorem is local and finite.  Global cone coherence should be tested by
overlap compatibility of the recovered projective rays on the response-derived
character sheaf, not by inserting a prior metric connection.
