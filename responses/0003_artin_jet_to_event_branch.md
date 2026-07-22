---
brief: 0003
source: browser-hosted GPT
captured: 2026-07-22
repository_commit: 864e451
status: proposed
---

# Response 0003 — Relation-complete regular branches and the Artin-jet comparison theorem

## Executive result

The contextual Loewy quotient and a positive-dimensional event branch are not
two rival reconstructions.  They are linked by a canonical quotient map.

Let

\[
P=\mathbb R[z_1,\ldots,z_g]
\]

be the polynomial algebra on the anonymous registered scalar response
generators.  Raw contextual substitution supplies a surjection

\[
\eta_D:P\longrightarrow \widehat{\mathcal A}_D,
\qquad
N_D=\ker\eta_D,
\]

and a physical handle supplies a character
\(\widehat x:\widehat{\mathcal A}_D\to\mathbb R\).  Put

\[
\lambda_i=\widehat x(\eta_D(z_i)),
\qquad
\mathfrak q_\lambda=(z_1-\lambda_1,\ldots,z_g-\lambda_g).
\]

Suppose an independently bounded, relation-complete physical-character panel
reconstructs a reduced event-branch presentation

\[
\mathcal A=P/I
\]

whose selected real character \(x\) has the same generator values
\(\lambda\).  Consistency of the event interpretation with every registered
context forces

\[
I\subseteq N_D.
\]

There is then an explicit filtered surjection

\[
\boxed{
\Theta_{x,2}:
J_x^2
=
\mathcal A_{\mathfrak m_x}/\mathfrak m_x^3
\;\simeq\;
\frac{P}{I+\mathfrak q_\lambda^3}
\longrightarrow
\widehat J_{\widehat x}^2
\;\simeq\;
\frac{P}{N_D+\mathfrak q_\lambda^3}
}
\tag{1}
\]

given by the same raw polynomial term on both sides:

\[
\Theta_{x,2}([f]_{I+\mathfrak q_\lambda^3})
=
[f]_{N_D+\mathfrak q_\lambda^3}.
\]

Its kernel is exactly

\[
\boxed{
\ker\Theta_{x,2}
=
\frac{N_D+\mathfrak q_\lambda^3}
     {I+\mathfrak q_\lambda^3}.
}
\tag{2}
\]

Thus the comparison is not an identification by notation.  It is a concrete
quotient induced by the common anonymous response generators.

Let

\[
V_{\lambda,2}=P/\mathfrak q_\lambda^3
\]

and define the local relation spaces

\[
R_{I,x}^{(2)}
=
\frac{I+\mathfrak q_\lambda^3}{\mathfrak q_\lambda^3},
\qquad
R_{D,x}^{(2)}
=
\frac{N_D+\mathfrak q_\lambda^3}{\mathfrak q_\lambda^3}.
\]

Then

\[
R_{I,x}^{(2)}\subseteq R_{D,x}^{(2)}
\]

and

\[
\boxed{
\Theta_{x,2}\text{ is an isomorphism}
\iff
R_{I,x}^{(2)}=R_{D,x}^{(2)}
\iff
\operatorname{rank}M_{I,x}^{(2)}
=
\operatorname{rank}M_{D,x}^{(2)}.
}
\tag{3}
\]

Here \(M_{I,x}^{(2)}\) is the local degree-two Macaulay matrix of the
reconstructed ideal and \(M_{D,x}^{(2)}\) is the kernel matrix of the
contextual Loewy quotient, both written in the same centered monomial space.

If the reconstructed local ring is regular of dimension \(d\), then

\[
\dim J_x^2
=
1+d+\frac{d(d+1)}2
=
\binom{d+2}{2}.
\]

Because (1) is already surjective, the sharp regular-branch dimension squeeze
is

\[
\boxed{
\dim\widehat J_{\widehat x}^2
=
\binom{d+2}{2}
\quad\Longleftrightarrow\quad
\Theta_{x,2}\text{ is an isomorphism}.
}
\tag{4}
\]

This is the bridge required by the brief.

The finite physical-character panel reconstructs \(I\) only under four
independently auditable conditions:

1. the registered generators are complete for the declared branch algebra;
2. \(I\) has a declared generator-degree bound;
3. the physical panel is unisolvent through that degree, or a Hilbert-rank
   squeeze proves the same fact;
4. the reconstructed branch ideal is real radical, and a separate physical
   state-completeness promise ties its selected real branch to realizable event
   handles.

None of these follows from the response realization order \(n_J\).

For the centered conformal source design, every prepared source lies in
\(\mathfrak m_xS\).  Therefore

\[
B_x|_W=0,
\qquad
\beta_x=0
\]

follows directly from the source-module action.  No source-fiber point
amplitude is used in this response.

---

## 1. The smallest auditable branch-presentation class

### 1.1 Anonymous response generators

Let

\[
z_1,\ldots,z_g
\]

be opaque recyclable scalar-response generators.  Their labels carry no
spacetime meaning.  Operational products provide all monomials needed up to a
declared degree \(D\).

A repeatable physical-handle token \(\xi_a\) supplies a multiplicative row

\[
x_a:\mathcal A_{\mathrm{resp}}\to\mathbb R.
\]

Its generator-value vector is

\[
\lambda^{(a)}
=
\bigl(
x_a(z_1),\ldots,x_a(z_g)
\bigr)\in\mathbb R^g.
\]

These numbers are values of response functions.  They are not assumed
spacetime coordinates.

For

\[
P_{\le D}
=
\{f\in P:\deg f\le D\},
\]

choose the monomial column \(\nu_D(z)\).  The physical-character evaluation
matrix is

\[
E_D
=
\begin{pmatrix}
\nu_D(\lambda^{(1)})^\top\\
\vdots\\
\nu_D(\lambda^{(N)})^\top
\end{pmatrix}.
\tag{5}
\]

Every entry of \(E_D\) is an operational product followed by a registered
multiplicative handle evaluation.

### 1.2 Certificate-carrying bounded polynomial class

The first exact class should be polynomial.  A candidate selected branch is
specified by an ideal

\[
I\subset P
\]

satisfying the following independently declared bounds.

1. **Generator completeness.**  
   Every scalar response function used in the event, Green and overlap
   constructions belongs to \(P/I\), generated by the registered
   \(z_1,\ldots,z_g\).

2. **Relation complexity.**  
   \(I\) is generated by at most \(s\) polynomials of degree at most
   \(\delta\), with bounded calibrated coefficient norm.  Computational
   certification may additionally bound Gröbner-basis and real-Nullstellensatz
   certificate degrees.

3. **Reduced real branch.**  
   \(I\) is real radical.  For a single irreducible branch closure one may use
   the stronger real-prime subclass.  Real radicality is proved by a symbolic
   certificate or is an independent class promise; it is never inferred from
   character values alone.

4. **Physical branch selector.**  
   A tagged handle \(x_0\), together with finitely many response polynomials
   \(s_j\) and sign choices, selects a semialgebraically connected component

   \[
   B
   \subset
   V_{\mathbb R}(I)
   \cap
   \{s_1>0,\ldots,s_b>0\}.
   \tag{6}
   \]

   The sign functions are reconstructed response functions, not external
   coordinates.

5. **State completeness.**  
   The registered event-handle class realizes a relatively open neighborhood
   of \(x_0\) in \(B\), or realizes the declared response-open cover used in a
   branch claim.  For relation reconstruction, the finite character panel is
   additionally degree-unisolvent as defined below.

The exact mathematics uses only \(g,\delta\), unisolvence, real radicality and
the branch certificate.  Coefficient, Gröbner and Positivstellensatz bounds
make the adversarial search compact and auditable under noise.

### 1.3 Nash and smooth variants

A bounded Nash presentation reduces to the polynomial class by adjoining
graph generators.  A Nash response \(y=\phi(z)\) is represented by

\[
F(z,y)=0,
\qquad
\partial_yF\ne0
\]

on the selected branch.  The lifted polynomial ideal and the nonvanishing
minor supply the same comparison theorem.

An unrestricted \(C^\infty\) finite-presentation class is not relation
complete from finite character data.  Smooth functions can vanish on every
finite panel and to every prescribed finite jet order without vanishing on a
neighborhood.  A smooth version therefore needs an independent finite
dictionary, quasianalytic class, or finite-determinacy bound.  Without one,
the correct result is the no-go in Section 8.1.

---

## 2. Relation completeness from a physical-character panel

### 2.1 The truncated relation space is not the ideal

For an event ideal \(I\), define only the finite vector space

\[
I_{\le D}=I\cap P_{\le D}.
\]

It is generally not an ideal: multiplying an element of \(I_{\le D}\) by a
generator can leave \(P_{\le D}\).

The generated ideal

\[
\langle I_{\le D}\rangle_P
\]

equals \(I\) only if \(I\) has a generating set of degree at most \(D\).
This degree promise is logically independent of any rank statement about
\(I_{\le D}\).

### Definition 1 — degree-\(D\) unisolvent panel

A physical-character panel
\(\Lambda=\{\lambda^{(a)}\}_{a=1}^N\) is \(D\)-unisolvent for \(P/I\) when

\[
\overline{\operatorname{ev}}_{\Lambda,D}:
P_{\le D}/I_{\le D}
\longrightarrow
\mathbb R^N
\]

is injective.

Equivalently,

\[
\ker E_D=I_{\le D}.
\tag{7}
\]

This is the exact finite state-completeness property required for degree-\(D\)
relations.

### Theorem 1 — finite relation-space theorem

Let \(I\subset P\) be the selected branch ideal and let every registered
physical character lie in \(V_{\mathbb R}(I)\).  Then

\[
I_{\le D}\subseteq\ker E_D.
\tag{8}
\]

The panel determines the complete degree-\(D\) relation space if and only if it
is \(D\)-unisolvent, in which case

\[
I_{\le D}=\ker E_D.
\tag{9}
\]

If \(I\) is generated in degree at most \(\delta\le D\), then

\[
\boxed{
I=\left\langle\ker E_D\right\rangle_P.
}
\tag{10}
\]

#### Proof

Every algebraic relation vanishes under every character, giving (8).
Equality is exactly injectivity of the quotient evaluation map.  If the
generator-degree bound holds, every chosen ideal generator belongs to
\(I_{\le D}=\ker E_D\), so \(I\subseteq\langle\ker E_D\rangle\).  The reverse
inclusion follows because \(\ker E_D=I_{\le D}\subseteq I\).

### Theorem 2 — Hilbert dimension squeeze for unisolvence

Put

\[
r_D=\operatorname{rank}E_D.
\]

For every candidate ideal \(I\) consistent with the physical panel,

\[
r_D
\le
h_I(D),
\qquad
h_I(D)
=
\dim P_{\le D}/I_{\le D}.
\tag{11}
\]

If the independently bounded event class proves

\[
h_I(D)\le r_D
\]

for every candidate consistent with all raw intervals, then

\[
h_I(D)=r_D,
\qquad
I_{\le D}=\ker E_D
\]

for every candidate.  If all candidate ideals are generated in degree at most
\(D\), the entire ideal is common and relation complete.

#### Proof

The evaluation map factors through
\(P_{\le D}/I_{\le D}\), so its rank cannot exceed the dimension of that
quotient.  Equality of dimensions forces the induced map to be injective.

### Exact finite adversary

Within a bounded coefficient and degree class, failure of relation
completeness is witnessed by either

\[
\exists I,I'
\quad
\text{both class-consistent,}
\quad
I_{\le D}\ne I'_{\le D},
\tag{12}
\]

or by a nonzero polynomial class

\[
[f]\in P_{\le D}/I_{\le D},
\qquad
E_Df=0.
\tag{13}
\]

With bounded Gröbner and real-radical certificates, these are finite
semialgebraic feasibility problems.  Emptiness of both witness systems is an
auditable class-relative relation-completeness certificate.

### Branch-relative versus global reconstruction

If every panel handle lies on one selected branch \(B\), Theorem 1 reconstructs

\[
I_B
=
I\!\left(
\overline{B}^{\,\mathrm{Zar}}
\right)
\]

provided the panel is unisolvent for that branch closure.  It does not exclude
an additional physical component disjoint from \(B\).

To reconstruct a global visible algebra containing all declared branches, the
state-completeness promise must quantify over the full physical character
set.  Otherwise the mathematically correct output is a branch-relative
presentation \(P/I_B\) plus an inconclusive global-component claim.

### Why real radicality is separate

A physical-character panel can determine at most the ideal of its real
zero set:

\[
I\bigl(V_{\mathbb R}(I)\bigr)
=
\sqrt[\mathbb R]{I}.
\]

Thus character evaluations cannot distinguish \(I\) from a nonreduced ideal
having the same real radical.  The regular event branch must be reconstructed
from a real-radical presentation, or nilpotent structure must be supplied by a
separate non-character operation.

---

## 3. Selecting and proving a physical regular branch

### 3.1 Dimension is computed, not supplied

After relation completeness, compute

\[
d=\dim_{\mathrm{Krull}} P/I
\tag{14}
\]

from a Gröbner basis or Hilbert polynomial.  No value of \(d\) is inserted
before this step.

Let \(F_1,\ldots,F_s\) generate \(I\), and let

\[
\mathsf J_F(z)
=
\left(
\frac{\partial F_\alpha}{\partial z_i}
\right)_{\alpha,i}
\tag{15}
\]

be the presentation Jacobian.

### Theorem 3 — physical regular-branch theorem

Assume:

1. \(I\) is real radical and equidimensional of Krull dimension \(d\), or is
   the real-prime ideal of the selected branch closure;

2. the tagged physical handle has value
   \(\lambda\in V_{\mathbb R}(I)\);

3. at \(\lambda\),

   \[
   \operatorname{rank}\mathsf J_F(\lambda)=g-d;
   \tag{16}
   \]

4. the selected semialgebraic component \(B\) in (6) contains \(\lambda\), and
   the singular witness set

   \[
   \left\{
   z\in B:
   \operatorname{rank}\mathsf J_F(z)<g-d
   \right\}
   \tag{17}
   \]

   is empty;

5. the branch-state completeness promise realizes the claimed neighborhood or
   cover of \(B\).

Then:

- \(\mathcal A_{\mathfrak m_x}\) is a regular local ring of dimension \(d\);
- \(B\) is a \(d\)-dimensional Nash manifold;
- its local topology and smooth structure are generated by the reconstructed
  response functions;
- \(x\) is a physical event character, rather than an unselected abstract real
  character.

#### Proof skeleton

In characteristic zero, the Jacobian rank \(g-d\) is the Jacobian--Krull
criterion for regularity of the local ring at \(\lambda\).  The same rank on
the selected component makes every point nonsingular.  The real implicit
function theorem then makes the real locus locally a \(d\)-dimensional Nash
manifold.  The branch selector and tagged handle choose the component.  State
completeness is what promotes this mathematical component to a physically
realized event branch.

### 3.2 Auditing the branch and its cover

The emptiness of (17) is a real-algebraic feasibility problem.  It can be
written by adjoining all \((g-d)\)-minors of \(\mathsf J_F\) and asking whether
their simultaneous vanishing is compatible with the branch sign conditions.

Choose finitely many nonzero \((g-d)\)-minors

\[
\Delta_\alpha.
\]

The principal response-open sets

\[
U_\alpha
=
B\cap\{\Delta_\alpha\ne0\}
\tag{18}
\]

cover \(B\) exactly when

\[
B\cap
V(\Delta_1,\ldots,\Delta_L)
=
\varnothing.
\tag{19}
\]

A CAD, roadmap or Positivstellensatz certificate may audit (17) and (19).
Finite sampling of nonsingular points is not a substitute.

There are two different coverage statements.

1. **Algebraic cover:** the \(U_\alpha\) cover the reconstructed branch.
2. **Physical cover:** registered event handles realize every claimed
   \(U_\alpha\), or are dense enough for the declared operational property.

The first follows from the ideal and inequalities.  The second is an
independent state-completeness promise and cannot be proved from a finite panel
alone.

---

## 4. The reconstructed branch jet

Let

\[
x:P/I\to\mathbb R
\]

be the selected physical character with generator values \(\lambda\), and let

\[
\mathfrak m_x=\ker x.
\]

### Proposition 1 — localization-free finite model of the local two-jet

There is a canonical isomorphism

\[
\boxed{
J_x^2
=
(P/I)_{\mathfrak m_x}/\mathfrak m_x^3
\;\simeq\;
P/(I+\mathfrak q_\lambda^3).
}
\tag{20}
\]

#### Proof

The natural map from \(P\) to the localized jet has kernel
\(I+\mathfrak q_\lambda^3\).  Any polynomial \(s\notin\mathfrak q_\lambda\)
has the form

\[
s=c+n,
\qquad
c=s(\lambda)\ne0,
\qquad
n\in\mathfrak q_\lambda.
\]

Modulo \(\mathfrak q_\lambda^3\),

\[
s^{-1}
=
c^{-1}
-c^{-2}n
+c^{-3}n^2.
\]

Thus localization adds no new element to the order-two quotient.

### Local Macaulay construction

Let

\[
y_i=z_i-\lambda_i
\]

and use the centered monomial basis

\[
\mathcal B_{\lambda,2}
=
\{1,\ y_i,\ y_iy_j:1\le i\le j\le g\}.
\tag{21}
\]

Its size is

\[
n_{g,2}
=
1+g+\frac{g(g+1)}2.
\]

Reduce

\[
hF_\alpha
\pmod{\mathfrak q_\lambda^3}
\]

for the finitely many centered monomials \(h\) needed through total local
order two.  The coefficient rows span

\[
R_{I,x}^{(2)}
=
(I+\mathfrak q_\lambda^3)/\mathfrak q_\lambda^3.
\]

Let the resulting matrix be \(M_{I,x}^{(2)}\).  Then

\[
J_x^2
\simeq
V_{\lambda,2}/
\operatorname{row}M_{I,x}^{(2)}
\tag{22}
\]

and

\[
\dim J_x^2
=
n_{g,2}
-
\operatorname{rank}M_{I,x}^{(2)}.
\tag{23}
\]

If the local ring is regular of dimension \(d\), multiplication induces

\[
\operatorname{Sym}^2(
\mathfrak m_x/\mathfrak m_x^2
)
\simeq
\mathfrak m_x^2/\mathfrak m_x^3
\]

and therefore

\[
\dim J_x^2
=
\binom{d+2}{2}.
\tag{24}
\]

---

## 5. Main theorem: comparison with the contextual Loewy jet

Raw contexts give

\[
\eta_D:P\to\widehat{\mathcal A}_D,
\qquad
N_D=\ker\eta_D.
\]

The physical handle satisfies

\[
\widehat x\eta_D(z_i)=\lambda_i.
\]

Hence

\[
\widehat{\mathfrak m}_{\widehat x}
=
(\mathfrak q_\lambda+N_D)/N_D
\]

and

\[
\widehat J_{\widehat x}^2
\simeq
P/(N_D+\mathfrak q_\lambda^3).
\tag{25}
\]

### Theorem 4 — Artin-jet comparison theorem

Let \(I\) be a relation-complete event-branch ideal reconstructed from the same
anonymous response generators.  Assume its event interpretation is consistent
with every saturated raw context.

Then:

1. every algebraic branch relation is contextually null,

   \[
   I\subseteq N_D;
   \tag{26}
   \]

2. there is a canonical filtered surjection

   \[
   \Theta_{x,2}:
   P/(I+\mathfrak q_\lambda^3)
   \twoheadrightarrow
   P/(N_D+\mathfrak q_\lambda^3);
   \tag{27}
   \]

3. its kernel is

   \[
   \ker\Theta_{x,2}
   =
   (N_D+\mathfrak q_\lambda^3)/
   (I+\mathfrak q_\lambda^3);
   \tag{28}
   \]

4. the following are equivalent:

   \[
   \Theta_{x,2}\text{ is an isomorphism};
   \tag{29a}
   \]

   \[
   N_D\subseteq I+\mathfrak q_\lambda^3;
   \tag{29b}
   \]

   \[
   R_{I,x}^{(2)}=R_{D,x}^{(2)};
   \tag{29c}
   \]

   \[
   \operatorname{rank}M_{I,x}^{(2)}
   =
   \operatorname{rank}M_{D,x}^{(2)};
   \tag{29d}
   \]

   \[
   \dim J_x^2
   =
   \dim\widehat J_{\widehat x}^2.
   \tag{29e}
   \]

Here

\[
R_{D,x}^{(2)}
=
(N_D+\mathfrak q_\lambda^3)/
\mathfrak q_\lambda^3
\]

and \(M_{D,x}^{(2)}\) is any row matrix for the kernel of the raw map

\[
V_{\lambda,2}\to\widehat J_{\widehat x}^2.
\]

#### Proof

A polynomial relation in \(I\) is zero as an event response in every candidate
model.  Substitution into any registered context therefore gives zero, proving
(26).

The inclusion \(I\subseteq N_D\) gives the quotient map (27), and the kernel
formula is the third isomorphism theorem.

Modulo \(\mathfrak q_\lambda^3\), the two relation spaces satisfy

\[
R_{I,x}^{(2)}
\subseteq
R_{D,x}^{(2)}.
\]

The quotient map is injective exactly when those subspaces are equal.  Equality
is equivalent to equality of their ranks because one is contained in the
other.  Finally, a surjection between finite-dimensional vector spaces is an
isomorphism exactly when their dimensions agree.

### Corollary 1 — regular-branch dimension squeeze

If the selected branch is regular of dimension \(d\), then

\[
\boxed{
\Theta_{x,2}\text{ is an isomorphism}
\iff
\dim\widehat J_{\widehat x}^2
=
\binom{d+2}{2}.
}
\tag{30}
\]

More finely, the induced maps

\[
\mathfrak m_x/\mathfrak m_x^2
\twoheadrightarrow
\widehat{\mathfrak m}/\widehat{\mathfrak m}^{\,2}
\]

and

\[
\mathfrak m_x^2/\mathfrak m_x^3
\twoheadrightarrow
\widehat{\mathfrak m}^{\,2}/
\widehat{\mathfrak m}^{\,3}
\]

are isomorphisms exactly when their respective dimensions are

\[
d
\qquad\text{and}\qquad
\frac{d(d+1)}2.
\tag{31}
\]

### Corollary 2 — exact trichotomy for a reconstructed dimension

Let

\[
\widehat r_2
=
\dim\widehat J_{\widehat x}^2.
\]

For a regular candidate branch of dimension \(d\):

- if

  \[
  \widehat r_2>
  \binom{d+2}{2},
  \]

  that regular branch is inconsistent with the raw contextual quotient;

- if equality holds, the comparison map is forced to be an isomorphism;

- if

  \[
  \widehat r_2<
  \binom{d+2}{2},
  \]

  the raw apparatus has collapsed at least one genuine event-jet direction.

No inference about spacetime dimension is allowed from the collapsed quotient
alone.

### Corollary 3 — comparison-witness system

Within a bounded presentation class, nonfaithfulness is witnessed by a
candidate satisfying all raw, panel, real-branch and regularity constraints
together with

\[
\operatorname{rank}M_{I,x}^{(2)}
<
\operatorname{rank}M_{D,x}^{(2)}.
\tag{32}
\]

Equivalently, introduce a normalized centered polynomial \(f\) and require

\[
f\in N_D+\mathfrak q_\lambda^3,
\qquad
f\notin I+\mathfrak q_\lambda^3.
\tag{33}
\]

The emptiness of this bounded comparison-witness system is the exact
class-relative certificate that every reconstructed branch jet maps
isomorphically to the contextual Loewy jet.

---

## 6. Regularity is stronger than a free quadratic layer

Even when

\[
\dim\mathfrak m_x/\mathfrak m_x^2=d
\]

and

\[
\operatorname{Sym}^2(
\mathfrak m_x/\mathfrak m_x^2
)
\longrightarrow
\mathfrak m_x^2/\mathfrak m_x^3
\]

is an isomorphism, the germ need not be regular.  A relation can begin in
order three or higher.

The comparison theorem therefore has two logically separate gates.

1. **Branch gate:** relation completeness, real radicality and
   Jacobian--Krull regularity establish a genuine regular event germ.

2. **Measurement gate:** Theorem 4 proves that the contextual Artin object is
   exactly the measured order-two truncation of that germ.

Neither gate implies the other.

---

## 7. Jet bundles and response-derived chart overlaps

### 7.1 The jet bundle comes from one algebra

For the reconstructed algebra \(A=P/I\), let

\[
\mathcal I_\Delta
=
\ker\bigl(
\mu:A\otimes_{\mathbb R}A\to A
\bigr)
\]

be the diagonal ideal.  The sheaf of second principal parts is generated by

\[
\mathcal P^2_{A/\mathbb R}
=
(A\otimes_{\mathbb R}A)/
\mathcal I_\Delta^3,
\tag{34}
\]

viewed as a left \(A\)-module.

At a real character \(x\),

\[
\mathbb R_x
\otimes_A
\mathcal P^2_{A/\mathbb R}
\simeq
A_{\mathfrak m_x}/\mathfrak m_x^3
=
J_x^2.
\tag{35}
\]

On a regular \(d\)-dimensional branch,
\(\mathcal P^2\) is locally free of rank

\[
\binom{d+2}{2}.
\]

Thus the family of event jets is a bundle derived from the single
reconstructed algebra or its structure sheaf.  It is not assembled by
declaring unrelated pointwise vector spaces equal.

### 7.2 Response-generated charts

On a patch where a \((g-d)\)-minor of the relation Jacobian is nonzero, choose
the complementary \(d\) response generators

\[
a_1,\ldots,a_d\in A.
\]

Their differentials form a basis of \(\Omega^1_A\) on that patch.  The map

\[
p\longmapsto
\bigl(
a_1(p),\ldots,a_d(p)
\bigr)
\tag{36}
\]

is a Nash chart.  The chart is selected after relation reconstruction by a
nonzero response-Jacobian minor; it is not an input coordinate system.

If \(a^{(\alpha)}\) and \(a^{(\beta)}\) are two such tuples, their overlap map
is induced by the identities of those same elements in the localized algebra

\[
A_{\Delta_\alpha\Delta_\beta}.
\]

Its Jacobian is the change-of-basis matrix between

\[
da_1^{(\alpha)},\ldots,da_d^{(\alpha)}
\]

and

\[
da_1^{(\beta)},\ldots,da_d^{(\beta)}.
\]

The overlap maps automatically satisfy the cocycle condition because they are
restrictions of one algebra or one sheaf.

There is no canonical map

\[
J_x^2\to J_y^2
\]

for distinct points \(x,y\).  Such a map would be parallel transport and would
require an additional connection.  The reconstructed structure supplies
local trivializations and overlap maps only.

### 7.3 What is needed for a neighborhood claim

A neighborhood-level claim requires:

1. a finite response-open cover \(U_\alpha\);
2. regularity and constant jet rank on each \(U_\alpha\);
3. operationally certified overlap restrictions;
4. physical state coverage on those patches.

Pointwise comparison maps alone do not determine global topology.

---

## 8. Exact countermodels for every essential condition

### 8.1 No relation-degree bound

Fix any finite truncation degree \(D\ge2\).  At the origin compare

\[
A_0=\mathbb R[u,v]
\]

with

\[
A_1
=
\mathbb R[u,v]/
\bigl(
v^{D+1}-u^{D+2}
\bigr).
\tag{37}
\]

The second ideal is a reduced binomial curve ideal, and its first relation has
order \(D+1\).  The two algebras have identical relation spaces through degree
\(D\) and identical two-jets at the origin, but different Krull dimensions and
regularity.  No finite relation search can exclude \(A_1\) without a generator
degree or finite-determinacy bound.

For arbitrary smooth relations the obstruction is stronger: a nonzero smooth
function can be flat on every finitely probed jet.

### 8.2 No real-radical condition

Compare

\[
I_0=(y)
\]

with

\[
I_1=(y^2)
\qquad
\text{in }\mathbb R[x,y].
\tag{38}
\]

They have the same real character set and every physical-character evaluation
matrix is identical.  But the second algebra contains a nilpotent first-order
direction and has a different local Loewy structure.  Character panels recover
only the common real radical \((y)\).

### 8.3 Finite physical sampling without unisolvence

Let the panel on the real line be

\[
a_1,\ldots,a_N
\]

and put

\[
h(t)=\prod_{j=1}^N(t-a_j).
\]

The two real-radical ideals

\[
I_0=(0),
\qquad
I_1=(h)
\tag{39}
\]

fit every panel value exactly.  At each sampled point, \(I_1\) gives a regular
zero-dimensional branch, while \(I_0\) gives a one-dimensional branch.

If \(N\le\delta\), this ambiguity persists even inside a degree-\(\delta\)
class.  The missing condition is precisely injectivity of the quotient
evaluation map, or its Hilbert dimension squeeze.

### 8.4 Missed physical branches

Compare

\[
I_0=(y)
\]

with

\[
I_1=(y(y-1))
\qquad
\text{in }\mathbb R[x,y].
\tag{40}
\]

Both ideals are real radical.  A panel and every registered context supported
on the branch \(y=0\) give identical data.  The second model has an additional
parallel real branch \(y=1\).

The selected local branch can still be certified, but the global event algebra
and topology cannot.  A full global claim requires state completeness over all
declared physical branches.

### 8.5 Singularities between regular samples

The cusp

\[
I=(y^2-x^3)
\tag{41}
\]

has the regular parameterized points

\[
(x,y)=(t^2,t^3),
\qquad
t\ne0,
\]

but is singular at the origin.  A finite panel avoiding the origin passes
every pointwise Jacobian test.

Once the complete ideal is reconstructed, the singular witness is found
symbolically.  If regularity is checked only at sampled handles, it is not a
branch theorem.

### 8.6 Same two-jet, regular versus singular

At the origin compare

\[
A_{\mathrm{reg}}=\mathbb R[u,v]
\]

with

\[
A_{\mathrm{sing}}
=
\mathbb R[u,v]/(v^3-u^4).
\tag{42}
\]

Since the relation lies in \((u,v)^3\),

\[
J_{\mathrm{reg},0}^2
\simeq
J_{\mathrm{sing},0}^2.
\]

The first germ is regular of dimension two.  The second is a singular curve.
This is the exact reason the contextual Artin quotient cannot establish the
regular branch by itself.

### 8.7 No physical branch selector

For

\[
A=\mathbb R[e]/(e^2-e)
\simeq\mathbb R\oplus\mathbb R,
\]

the automorphism \(e\mapsto1-e\) exchanges the two real characters.  If all
registered rows are invariant under that exchange, no physical branch is
selected.  Choosing one abstract character by hand is not operational.

### 8.8 Ambiguous global gluing and topology

A finite collection of regular one-dimensional local jets is compatible with
both

\[
\mathbb R[t]
\]

and

\[
\mathbb R[c,s]/(c^2+s^2-1).
\tag{43}
\]

Every selected regular point has local two-jet
\(\mathbb R[\epsilon]/(\epsilon^3)\), but the real loci are a line and a
circle.

An exact sheaf version uses two copies \(U,V\) of the Nash interval
\((-2,2)\).  Suppose the registered records contain every within-\(U\) and
within-\(V\) product and jet, but no cross-chart context.  The same records
admit all of the following realizations:

1. the disjoint union \(U\sqcup V\);
2. a longer interval obtained by identifying
   \((1,2)\subset U\) with \((-2,-1)\subset V\) by a Nash translation;
3. a circle obtained by also identifying
   \((1,2)\subset V\) with \((-2,-1)\subset U\).

The local sheaves, all pointwise jets and all within-chart response products
are exactly the same.  Only the overlap isomorphisms differ.  Global topology
is determined only after overlap maps, cocycle consistency and cover
completeness have been registered.

---

## 9. Anonymous-generator exact paraboloid toy

### 9.1 Hidden proof presentation

The simulator uses

\[
A
=
\mathbb R[z_1,z_2,z_3]/(F),
\qquad
F=z_3-z_1^2-z_2^2.
\tag{44}
\]

The inference routine receives only anonymous response-generator values,
operational products, contextual matrices and class bounds.

Use the degree-two monomial order

\[
\mathcal M_2
=
(
1,\,
z_1,\,
z_2,\,
z_3,\,
z_1^2,\,
z_1z_2,\,
z_1z_3,\,
z_2^2,\,
z_2z_3,\,
z_3^2
).
\tag{45}
\]

Take the nine physical handles corresponding in the hidden simulator to

\[
(0,0),\,
(1,0),\,
(-1,0),\,
(0,1),\,
(0,-1),\,
(1,1),\,
(1,-1),\,
(-1,1),\,
(-1,-1),
\]

with

\[
z_3=z_1^2+z_2^2.
\]

The operational evaluation matrix is

\[
E_2=
\begin{pmatrix}
1&0&0&0&0&0&0&0&0&0\\
1&1&0&1&1&0&1&0&0&1\\
1&-1&0&1&1&0&-1&0&0&1\\
1&0&1&1&0&0&0&1&1&1\\
1&0&-1&1&0&0&0&1&-1&1\\
1&1&1&2&1&1&2&1&2&4\\
1&1&-1&2&1&-1&2&1&-2&4\\
1&-1&1&2&1&-1&-2&1&2&4\\
1&-1&-1&2&1&1&-2&1&-2&4
\end{pmatrix}.
\tag{46}
\]

It has

\[
\operatorname{rank}E_2=9
\]

and one-dimensional kernel generated by

\[
r_F
=
(0,0,0,-1,1,0,0,1,0,0)^\top,
\tag{47}
\]

which is the anonymous relation

\[
-z_3+z_1^2+z_2^2.
\]

The independent event class promises:

- relation generators have degree at most two;
- \(h_I(2)\le9\);
- the selected branch ideal is real prime.

The Hilbert squeeze gives

\[
I_{\le2}=\ker E_2,
\qquad
I=(F).
\]

### 9.2 Dimension and regularity

Because \(F\) is linear in \(z_3\),

\[
A\simeq\mathbb R[z_1,z_2].
\]

Thus \(I\) is real prime and

\[
d=\dim_{\mathrm{Krull}}A=2.
\]

The Jacobian is

\[
\mathsf J_F
=
\begin{pmatrix}
-2z_1&-2z_2&1
\end{pmatrix},
\tag{48}
\]

which has rank one everywhere.  The entire real paraboloid is a connected
regular two-dimensional branch.

The branch-state promise says that the registered handle class realizes the
claimed response-open region of this graph.  The nine handles are used for
relation unisolvence, not as proof of topological coverage.

### 9.3 Reconstructed local jet

Choose the physical handle

\[
x_0=(0,0,0).
\]

In the monomial order (45), the local Macaulay relation matrix through order
two is

\[
M_{I,x_0}^{(2)}
=
\begin{pmatrix}
0&0&0&1&-1&0&0&-1&0&0\\
0&0&0&0&0&0&1&0&0&0\\
0&0&0&0&0&0&0&0&1&0\\
0&0&0&0&0&0&0&0&0&1
\end{pmatrix}.
\tag{49}
\]

The rows are the truncations of

\[
F,\qquad
z_1F,\qquad
z_2F,\qquad
z_3F
\pmod{\mathfrak q_0^3}.
\]

They have rank four, so

\[
\dim J_{x_0}^2=10-4=6
=
\binom{2+2}{2}.
\]

A convenient jet basis is

\[
(1,u,v,u^2,uv,v^2).
\]

### 9.4 Contextual Loewy quotient and explicit comparison

Let the contextual quotient use the six-dimensional basis above.  Its raw
degree-two quotient matrix is

\[
C_D=
\begin{pmatrix}
1&0&0&0&0&0&0&0&0&0\\
0&1&0&0&0&0&0&0&0&0\\
0&0&1&0&0&0&0&0&0&0\\
0&0&0&1&1&0&0&0&0&0\\
0&0&0&0&0&1&0&0&0&0\\
0&0&0&1&0&0&0&1&0&0
\end{pmatrix}.
\tag{50}
\]

It implements

\[
z_1\mapsto u,
\qquad
z_2\mapsto v,
\qquad
z_3\mapsto u^2+v^2
\]

and kills all products of local order at least three.

The kernel of \(C_D\) is generated by the four rows of (49).  Therefore

\[
M_{D,x_0}^{(2)}
=
M_{I,x_0}^{(2)},
\]

and the comparison map is forced to be an isomorphism:

\[
\Theta_{x_0,2}:
P/(I+\mathfrak q_0^3)
\xrightarrow{\;\sim\;}
\widehat J_{\widehat x_0}^2.
\tag{51}
\]

The comparison is represented explicitly by \(C_D\); it is not inferred from
the fact that both spaces happen to have dimension six.

### 9.5 Contextual multiplication matrices

On the basis
\((1,u,v,u^2,uv,v^2)\), multiplication by the two independent first-order
classes is

\[
T_u=
\begin{pmatrix}
0&0&0&0&0&0\\
1&0&0&0&0&0\\
0&0&0&0&0&0\\
0&1&0&0&0&0\\
0&0&1&0&0&0\\
0&0&0&0&0&0
\end{pmatrix},
\tag{52}
\]

\[
T_v=
\begin{pmatrix}
0&0&0&0&0&0\\
0&0&0&0&0&0\\
1&0&0&0&0&0\\
0&0&0&0&0&0\\
0&1&0&0&0&0\\
0&0&1&0&0&0
\end{pmatrix}.
\tag{53}
\]

The third anonymous generator acts by

\[
T_{z_3}=T_u^2+T_v^2.
\tag{54}
\]

These matrices generate the same contextual kernel as (50).

### 9.6 Generator anonymity

Before every trial apply an arbitrary class-preserving affine generator
change

\[
z'=Az+b,
\qquad
A\in GL_3(\mathbb R),
\tag{55}
\]

together with arbitrary permutations of handles and invertible changes of
the monomial, context and readout bases.

The induced map on \(P_{\le2}\) is invertible.  It sends \(I\), the Jacobian,
the local Macaulay spaces and \(\Theta_{x,2}\) functorially to isomorphic
objects.  All ranks, regularity, branch dimension and the comparison verdict
are unchanged.

---

## 10. Invariance theorem

### Theorem 5 — presentation and basis invariance

The exact claims in Theorems 1--4 are invariant under:

1. permutations of opaque generator and physical-handle tokens;
2. invertible source, context and readout basis changes;
3. residual-state similarities in the contextual realization;
4. any polynomial automorphism

   \[
   \phi:P\to P
   \]

   whose inverse remains inside the declared presentation class.

Under \(\phi\),

\[
I\mapsto\phi(I),
\qquad
N_D\mapsto\phi(N_D),
\qquad
\mathfrak q_\lambda\mapsto\phi(\mathfrak q_\lambda),
\]

and \(\Theta_{x,2}\) is carried to the conjugate quotient map.  Relation
unisolvence, real radicality, Krull dimension, Jacobian regularity, local
Macaulay ranks and comparison-isomorphism status are preserved.

For a filtered local generator change

\[
y_i'
=
A_i{}^jy_j
+
B_i{}^{jk}y_jy_k
\pmod{\mathfrak q_\lambda^3},
\qquad
A\in GL_g,
\tag{56}
\]

the degree-zero, degree-one and degree-two blocks transform by

\[
1,\qquad
A,\qquad
\operatorname{Sym}^2A
\]

on the associated graded.  Hence the filtered comparison theorem is
coordinate free.

Numerical singular values are invariant only relative to calibrated norms
transported with these changes.

---

## 11. Finite-noise three-verdict theorem

Let \(\mathfrak C(D)\) be the compact set of exact, certificate-carrying
models in the declared response and event classes whose predictions lie in all
measured intervals.

Define the target property \(P_{\mathrm{branch},2}\) to mean:

1. the anonymous generators are complete for the selected branch algebra;
2. all candidates have the same relation ideal up to a registered
   class-preserving generator isomorphism;
3. the selected physical handle lies on a state-complete regular real branch;
4. the local dimension \(d\) is common;
5. the comparison map \(\Theta_{x,2}\) is an isomorphism;
6. the claimed response-open cover has no missed singular or uncovered point.

### Theorem 6 — robust branch-and-comparison certificate

Assume every model in \(\mathfrak C(D)\) satisfies the following calibrated
gaps.

1. **Panel rank gap**

   \[
   \sigma_{r_D}(E_D)\ge\gamma_{\mathrm{panel}}>0,
   \]

   with a class-fixed rank \(r_D\).

2. **Relation-completeness gap**  
   The Hilbert dimension squeeze fixes

   \[
   h_I(D)=r_D
   \]

   for every candidate, and the bounded generator-degree condition fixes the
   generated ideal.

3. **Branch regularity gap**

   On every compact response-defined region
   \(B_{\mathrm{obs}}\subset B\) used in a uniform finite-noise claim,

   \[
   \sigma_{g-d}\bigl(\mathsf J_F(z)\bigr)
   \ge
   \gamma_{\mathrm{Jac}}>0
   \qquad
   \text{for all }z\in B_{\mathrm{obs}},
   \tag{57}
   \]

   together with an exact emptiness certificate for the branch singular
   witness on the full claimed branch.  On a noncompact branch, exact
   regularity may hold without a global positive singular-value infimum, so
   the numerical margin is asserted only on certified compact regions.

4. **Comparison rank gap**

   \[
   \sigma_{r_2}\bigl(M_{I,x}^{(2)}\bigr)
   \ge
   \gamma_{\mathrm{loc}}>0,
   \]

   \[
   \sigma_{r_2}\bigl(M_{D,x}^{(2)}\bigr)
   \ge
   \gamma_{\mathrm{ctx}}>0,
   \]

   where both class-fixed ranks equal

   \[
   r_2
   =
   n_{g,2}
   -
   \binom{d+2}{2}.
   \]

5. **Branch-isolation and cover gaps**  
   All selector inequalities and chosen Jacobian minors have declared positive
   margins on the compact certified subregions where numerical continuation is
   used.

Then every consistent model has the same regular branch dimension and an
isomorphic comparison map.  The response-derived cotangent and quadratic
layers are therefore the actual first two graded layers of that regular event
branch.

If a nominal matrix \(\widehat M\) differs from every exact consistent matrix
by at most \(\eta\) in operator norm and

\[
\sigma_r(\widehat M)>\eta,
\]

the class-fixed rank-\(r\) subspace obeys the Wedin bound

\[
\left\|
\sin\Theta(
\operatorname{row}M,
\operatorname{row}\widehat M
)
\right\|_2
\le
\frac{\eta}
{\sigma_r(\widehat M)-\eta}.
\tag{58}
\]

This controls the relation and local-jet subspace tubes.  It does not turn an
unbounded numerical nullspace into an exact ideal; the degree, Hilbert and
rank promises remain essential.

### Three verdicts

- **certified within class**  
  if \(\mathfrak C(D)\ne\varnothing\) and every consistent model satisfies
  \(P_{\mathrm{branch},2}\), with the required rank, regularity, branch and
  comparison gaps;

- **class excluded**  
  if the full declared class is inconsistent with the intervals, or if no
  consistent model has the target regular faithful branch; the report states
  which exclusion occurred;

- **inconclusive**  
  if relation aliases, non-real-radical lifts, alternate dimensions, missed
  branches, singular candidates, nonisomorphic comparison maps or unresolved
  overlap topologies remain.

The procedure may certify a local branch and remain inconclusive about global
topology.  These are separate properties.

---

## 12. Seven-day implementation kill test

### Day 1 — relation-space and ideal generation

Implement the paraboloid evaluation matrix (46).

Verify exactly:

\[
\operatorname{rank}E_2=9,
\qquad
\ker E_2=\operatorname{span}\{r_F\}.
\]

Generate \(I=(F)\) only after imposing the independent degree-two and Hilbert
upper bounds.

Run the finite-panel countermodel (39).  Without the unisolvence/Hilbert
promise, the output must be inconclusive.

### Day 2 — real radicality and regular branch

Certify symbolically that the paraboloid ideal is real prime, compute

\[
d=2,
\]

and verify the global Jacobian rank.

Run the pair (38).  Character data alone must not distinguish the reduced and
nonreduced ideals.

Run the cusp (41).  Sampling only regular points must not certify the whole
branch; reconstructing the ideal must expose the singular witness.

### Day 3 — comparison map

Construct \(M_{I,x_0}^{(2)}\), \(C_D\) and
\(M_{D,x_0}^{(2)}\) from (49)--(50).

Verify:

\[
I\subseteq N_D,
\]

\[
\ker\Theta_{x_0,2}=0,
\]

\[
\operatorname{rank}M_{I,x_0}^{(2)}
=
\operatorname{rank}M_{D,x_0}^{(2)}
=4.
\]

Then delete one contextual quadratic direction.  The comparison must become a
proper surjection and the verdict must cease to be faithful.

### Day 4 — anonymous-generator invariance

Run at least \(10^4\) exact trials with:

- random affine generator changes;
- random monomial and relation bases;
- random handle permutations;
- random contextual-state similarities;
- random source and readout bases.

Recover isomorphic ideals, the same Krull dimension, the same regularity
verdict and conjugate comparison maps.

### Day 5 — branch and topology boundaries

Run the missed-branch pair (40).  Certify only the selected local branch unless
full state completeness is supplied.

Run the line-versus-circle local-jet model (43).  Pointwise jets must not
determine topology.

Add explicit overlap maps and a cover certificate.  Verify the cocycle, but do
not construct any canonical transport between distinct jet fibers.

### Day 6 — high-order and singular aliases

Run (37) and (42).

A free quadratic layer must not certify regularity.  Increasing response
context depth without increasing the relation-degree/state-completeness class
must not resolve the ambiguity.

Check explicitly that changing \(n_J\) leaves all event-presentation bounds
untouched.

### Day 7 — interval adversary and end-to-end composition

Perturb the panel, local Macaulay, contextual kernel and Jacobian matrices in
directions aligned with their smallest nonzero singular vectors.

Compare:

- direct bounded relation-alias search;
- Hilbert dimension squeeze;
- direct comparison-witness search;
- singular-locus feasibility;
- the Wedin subspace tubes.

Required behavior:

1. no false relation-completeness certificate;
2. no false real-regular branch certificate;
3. no false comparison isomorphism;
4. transition from certified to inconclusive when any required gap closes;
5. no direct transition to an incorrect certified dimension.

Finally, use centered source-module gates and verify

\[
B_x|_W=\beta_x=0.
\]

Feed the certified \(U_x\) and the now-proved identification

\[
K_x
\simeq
\widehat K
\]

into the adopted jet-null principal theorem.

### Hard stop conditions

Stop the positive event-branch claim and retain only the no-go/comparison
boundary if any of the following occurs.

1. The ideal is generated from \(\ker E_D\) without a generator-degree bound.
2. A finite panel is called unisolvent without a Hilbert or direct
   relation-separation certificate.
3. Character data distinguish \((y)\) from \((y^2)\) without a non-character
   operation.
4. A two-jet with a free quadratic layer is declared a regular germ.
5. The code constructs \(J_x^2\) and \(\widehat J^2\) but never constructs
   \(\Theta_{x,2}\).
6. Equality of dimensions is used before proving the canonical surjection.
7. A singular point between panel handles is ignored.
8. A selected local branch is promoted to complete global topology without
   state coverage and overlap data.
9. A generator or basis change alters an exact verdict.
10. A numerical nullspace is treated as an exact ideal without calibrated
    gaps and class-fixed ranks.
11. \(n_J\) is used as an event relation, Krull-dimension or regularity bound.
12. A source-fiber point amplitude is introduced in the centered conformal
    branch.

---

## 13. Strongest honest Paper I statement

The strongest theorem that may now precede the pointwise
Green-to-principal result is:

> **Operational regular-branch lift theorem.**  
> Within a separately bounded, certificate-carrying real-radical polynomial
> or polynomialized Nash branch class, a finite panel of multiplicative
> physical handles and operational products reconstructs the complete
> anonymous response ideal when the panel is unisolvent through an independent
> generator-degree bound.  A Jacobian--Krull certificate and a physical
> branch-state promise then produce a genuine \(d\)-dimensional regular real
> event branch, with \(d\) computed from the reconstructed ideal.  The common
> raw response generators induce a canonical filtered surjection
>
> \[
> \Theta_{x,2}:J_x^2\twoheadrightarrow\widehat J_{\widehat x}^2.
> \]
>
> Its kernel is
>
> \[
> (N_D+\mathfrak q_\lambda^3)/
> (I+\mathfrak q_\lambda^3),
> \]
>
> and it is an isomorphism exactly when the local ideal and contextual
> relation spaces have the same degree-two rank.  On a regular
> \(d\)-dimensional branch this is equivalent to
>
> \[
> \dim\widehat J_{\widehat x}^2
> =
> \binom{d+2}{2}.
> \]
>
> Thus the contextual cotangent and quadratic layers are certified as the
> measured two-truncation of a genuine regular event branch, rather than a
> freestanding Artin surrogate.

With centered source-module gates,

\[
\beta_x=0.
\]

The adopted jet-null theorem may therefore act on the now-justified branch
fiber

\[
K_x
=
\mathfrak m_x^2/\mathfrak m_x^3
\simeq
\widehat K
\]

and identify a conformal principal line when its rank condition holds.

A neighborhood spacetime claim additionally requires constant-rank principal
lines, response-derived overlap maps and physical cover completeness.  A
global topology or canonical parallel transport is not claimed at this stage.
