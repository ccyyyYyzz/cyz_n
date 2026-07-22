---
brief: 0002
source: browser-hosted GPT
captured: 2026-07-22
repository_commit: d9a3cd328a6134322dbfa8faff962e72776c2fd4
status: proposed
---

# Response 0002 — Contextual Loewy jets, exact alias witnesses, and the minimal completeness operation

## Executive result

Finite raw contextual data do not, by themselves, certify a faithful
two-jet, even when the response realization is known exactly and every
registered context has been closed to arbitrary depth.

There are two independent exact obstructions.

1. A registered gate direction can be nonzero in the event algebra while
   acting as zero in every registered source/readout realization.  Adjoining
   such a regular direction changes both
   \(\mathfrak m_x/\mathfrak m_x^2\) and
   \(\mathfrak m_x^2/\mathfrak m_x^3\) without changing any raw contextual
   tensor or the response realization order.

2. Even for a fixed, known, reduced event algebra, the all-context readout
   kernel can contain a nonzero quadratic germ.  Then two Green outputs have
   identical gated readouts at every depth but different two-jets.

The strongest non-circular positive statement is therefore class-relative.
Raw data first construct a canonical **contextual algebra** and its
second Loewy quotient.  Every bounded event-algebra model consistent with the
data maps onto that raw quotient.  The desired event two-jet is recovered
exactly if and only if either:

- that canonical map is faithful through order two; or
- the independently declared event/response class selects a unique lift of
  every prepared response despite a nonfaithful raw quotient.

Both alternatives have finite algebraic certificates.

The clean nonparametric branch is the following dimension squeeze.  Let

\[
\widehat{\mathcal A}_D
\]

be the saturated scalar contextual quotient, let \(\widehat x\) be a
physically registered character, and put

\[
\widehat J_{\widehat x}^2
=
\widehat{\mathcal A}_D/
\widehat{\mathfrak m}_{\widehat x}^{\,3}.
\]

For every consistent event model \(M\), there is a canonical surjection

\[
\pi_{M,x}^{(2)}:
J_{M,x}^2
\longrightarrow
\widehat J_{\widehat x}^2.
\]

Hence, writing

\[
\widehat r_2=\dim\widehat J_{\widehat x}^2,
\]

the raw quotient is faithful in every consistent model if and only if

\[
\dim J_{M,x}^2=\widehat r_2
\qquad
\text{for every consistent }M.
\]

It is enough for the independent event class to prove the upper bound

\[
\dim J_{M,x}^2\le \widehat r_2,
\]

because surjectivity already gives the reverse inequality.  This is the
**two-jet dimension-squeeze certificate**.

When that upper bound is unavailable, the exact general certificate is the
emptiness of a finite **two-jet alias witness system**.  In a bounded
presentation class it asks whether two class-consistent scalar terms can have
the same complete contextual signature but different algebraically computed
two-jets.  This is a finite semialgebraic feasibility problem; it does not
supply coordinates, derivatives, adjacency, support, or a target-space
localizer.

There is one further independent issue.  A physical event character does not
determine the source-fiber functional on an opaque source module.  For a source
module \(S\),

\[
\operatorname{Hom}_{\mathcal A}(S,\mathbb R_x)
\simeq
(S/\mathfrak m_xS)^*.
\]

Consequently one must calibrate a basis of the prepared source fiber, or
register an \(\mathcal A\)-linear source-to-scalar bypass.  In the cyclic
scalar-source branch one unit calibration is sufficient and minimal.

The resulting bridge is

\[
\boxed{
\begin{aligned}
\text{finite raw contexts}
&\longrightarrow
\text{saturated substitution congruence}\\
&\longrightarrow
(\widehat{\mathcal A}_D,\widehat x)\\
&\longrightarrow
(\widehat J^1,\widehat K,\widehat U)\\
&\xrightarrow{\text{class-relative faithfulness}}
(J_x^1,K_x,U_x)\\
&\xrightarrow{\text{source-fiber calibration}}
B_x\\
&\longrightarrow
\mathcal Q_x(D)
=
\{q:qH_x=\beta_x\}.
\end{aligned}
}
\]

The response realization bound \(n_J\) closes the contextual congruence only.
It does not bound event generators, local dimension, relation order, source
fiber rank, or differential order.

---

## 1. Typed raw contextual data

### 1.1 Raw terms

Fix finite sets of opaque registered tokens:

- scalar gate tokens \(\mathsf G=\{g_1,\ldots,g_q\}\);
- source seeds \(\mathsf S=\{s_1,\ldots,s_m\}\);
- linear readout seeds \(\mathsf R=\{\rho_1,\ldots,\rho_r\}\);
- repeatable physical-handle tokens \(\Xi\).

No token is called a point, coordinate, neighborhood, localized source, or
causal event.

Before any commutativity claim, let

\[
\mathbb F=\mathbb R\langle \mathsf G\rangle
\]

be the free unital associative gate algebra.  Source terms are finite linear
combinations of words acting on source seeds.  Scalar response terms include
registered linear responses of prepared sources.

A scalar response is said to be **recyclable** when the apparatus allows that
response token to occupy every registered scalar gate hole.  Recycling is a
typed operation.  It does not assert that the response is localized anywhere.

### 1.2 One-hole contexts

A one-hole context is any registered typed expression with one scalar or
source slot left open.  A scalar example is

\[
C[-]
=
\rho_i\!\left(
M_{h_L}\,
G\,
M_{h_1}\,
[-]\,
M_{h_2}s_j
\right),
\]

where all \(h\)'s are registered gate words.  Context composition order is
laboratory protocol order only.

For finite context and term sets \(\mathcal C_0,\mathcal T_0\), the exact raw
context matrix is

\[
\mathbf D_{c,t}=D(C_c[t]).
\]

With noise, each entry is an interval.

The complete finite raw object also records:

- the syntactic left and right gate-extension maps on terms and contexts;
- source and readout superposition maps;
- which scalar responses may be recycled as gates;
- physical-handle calibration rows;
- independent class bounds
  \(\mathcal C_R(n_J)\) and \(\mathcal C_X(B_X)\).

### 1.3 Full substitution equivalence

For same-type terms \(u,v\), define

\[
u\equiv_\infty v
\quad\Longleftrightarrow\quad
D(C[u])=D(C[v])
\quad
\text{for every declared one-hole context }C.
\tag{1}
\]

Because plugging a term into a larger registered context again gives a
registered context, \(\equiv_\infty\) is a typed congruence:

\[
u\equiv_\infty v
\Longrightarrow
a\,u\,b\equiv_\infty a\,v\,b
\]

for every registered left and right gate word \(a,b\), and likewise under
source superposition and response recycling.

Equality under a shallow list of readouts is not enough.  The continuation
counterexample in Section 8.1 is minimal.

---

## 2. Finite certification of the substitution congruence

### Theorem 1 — finite residual closure gives the full gating congruence

Form the block Hankel matrix of typed left and right half-contexts,

\[
\mathsf H_{p,s}
=
D(p\circ s).
\]

Assume the project's already established response-flatness theorem has
certified, using the independent bound \(n_J\), that finite prefix and suffix
sets \(P,S\) are rank-saturated:

\[
\operatorname{rank}\mathsf H_{P,S}
=
\operatorname{rank}\mathsf H_{P\mathsf G,S}
=
\operatorname{rank}\mathsf H_{P,S\mathsf G}
=
r,
\tag{2}
\]

and that no model in \(\mathcal C_R(n_J)\) consistent with the raw intervals
can acquire an additional residual row or column direction at a greater
context depth.

Then:

1. the complete signature of every declared gate or response term is
   determined by its finite signatures on \(P\times S\);

2. finite equality of those signatures is equivalent to
   \(\equiv_\infty\);

3. the finite contextual nullspaces are invariant under every registered left
   and right gate extension;

4. the quotient operations are well defined at arbitrary context depth.

#### Proof skeleton

The saturated Hankel row space is invariant under appending any gate token,
because every one-step-extended row lies in the certified row span.  The same
holds for columns.  Appending a word of arbitrary length is therefore an
iteration of finite transition matrices on those two residual spaces.
Equality on the residual bases propagates inductively to every context.
Kernel invariance is the same statement written dually.

The independent \(n_J\) bound is used only to exclude a later residual-rank
jump.  It says nothing about the number of event generators or the dimension
of a local event germ.

### Corollary 1 — finite algebra and module quotients

Let \(N_{\mathrm{sc}}\) be the saturated contextual null ideal of scalar terms.
Then

\[
\widehat{\mathcal A}_D
=
\mathbb F/N_{\mathrm{sc}}
\tag{3}
\]

is a finite represented algebra on the residual space.

The scalar quotient is accepted as commutative only if the finite residual
certificate proves

\[
[g_i,g_j]\in N_{\mathrm{sc}}
\qquad
\text{for all }i,j,
\tag{4}
\]

and accepts a unit only if its unit identities hold in all residual contexts.

Source and output terms give quotient modules
\(\widehat S_D\) and \(\widehat E_D\).  Registered gate actions descend to
those modules.

If scalar responses are recyclable, the scalar response map descends to

\[
\widehat G_{\mathrm{sc}}:
\widehat S_D
\longrightarrow
\widehat{\mathcal A}_D.
\tag{5}
\]

Without recycling, raw data generally give only

\[
\widehat G:
\widehat S_D
\longrightarrow
\widehat E_D,
\]

and there is no canonical map from \(\widehat E_D\) into an event-algebra
two-jet.  A cross-type scalar anchoring operation is then necessary.

---

## 3. Constructing a physical character

A physical character must be tied to a repeatable apparatus handle, not chosen
from the abstract algebraic spectrum.

For \(\xi\in\Xi\), let

\[
\varepsilon_\xi(a)
\]

be the registered scalar calibration response obtained by inserting the scalar
term \(a\) into the handle context \(\xi\).

### Theorem 2 — finite physical-character certificate

Assume the saturated context quotient
\(\widehat{\mathcal A}_D\) has a finite residual basis
\(\{a_1,\ldots,a_N\}\).  If the finite raw data certify

\[
\varepsilon_\xi(1)=1,
\tag{6}
\]

\[
\varepsilon_\xi(a_i a_j)
=
\varepsilon_\xi(a_i)\varepsilon_\xi(a_j)
\qquad
1\le i,j\le N,
\tag{7}
\]

and \(\varepsilon_\xi\) annihilates the saturated contextual null ideal, then

\[
\widehat x_\xi:
\widehat{\mathcal A}_D\to\mathbb R,
\qquad
\widehat x_\xi([a])=\varepsilon_\xi(a),
\tag{8}
\]

is a well-defined algebra character.

Conversely, every character obtained from the declared handle interface must
satisfy (6)--(7), so these conditions are necessary on a complete quotient
basis.

The character is physical because \(\xi\) is a repeatable raw token.  Other
abstract characters of \(\widehat{\mathcal A}_D\) are not automatically
declared realized.

If no handle branch is selected, or if interval data allow two inequivalent
multiplicative handle rows, the base character is inconclusive.

---

## 4. The canonical raw two-jet

Let

\[
\widehat{\mathfrak m}
=
\ker\widehat x.
\]

All products below are computed from the certified contextual multiplication
table.

Define

\[
\widehat J^2
=
\widehat{\mathcal A}_D/
\widehat{\mathfrak m}^{\,3},
\tag{9}
\]

\[
\widehat J^1
=
\widehat{\mathcal A}_D/
\widehat{\mathfrak m}^{\,2},
\tag{10}
\]

and

\[
\widehat K
=
\widehat{\mathfrak m}^{\,2}/
\widehat{\mathfrak m}^{\,3}.
\tag{11}
\]

These are Loewy quotients of the contextual algebra.  No derivative,
coordinate, adjacency relation, metric, or bump function enters their
definition.

If prepared sources are represented by

\[
\widehat S_W:W\to\widehat S_D
\]

and scalar response recycling has produced (5), define the raw response
two-jet map

\[
\widehat U_x
=
q_2\,
\widehat G_{\mathrm{sc}}\,
\widehat S_W:
W\to\widehat J^2,
\tag{12}
\]

where \(q_2\) is the quotient map in (9).

### Theorem 3 — contextual Loewy-jet maximality

The tuple

\[
(\widehat J^1,\widehat K,\widehat U_x)
\]

is canonically determined by the saturated raw contextual data and the
registered physical handle.

Moreover, any order-two algebraic assignment to scalar raw terms that

- is constant on every raw contextual equivalence class;
- respects the registered scalar multiplication;
- sends the selected handle to a character;
- kills the third power of its character kernel,

factors uniquely through \(\widehat J^2\).

Thus \(\widehat J^2\) is the strongest two-jet-shaped object obtainable from
raw contexts alone.  It is not yet a theorem that it equals the declared event
two-jet.

---

## 5. Exact class-relative faithfulness

### 5.1 Candidate event models

Let \(M\) be a model in the bounded event class
\(\mathcal C_X(B_X)\) consistent with the raw data.  Let

\[
\mathcal A_M
\]

be its declared scalar response algebra generated by the registered scalar
terms, and let

\[
x_M:\mathcal A_M\to\mathbb R
\]

be the character realized by the same physical handle.

Let \(\mathbb T_{\mathrm{sc}}\) denote the scalar term algebra before
contextual quotienting.  The candidate interpretation has algebraic relation
ideal

\[
I_M
=
\ker\bigl(
\mathbb T_{\mathrm{sc}}\to\mathcal A_M
\bigr).
\]

Every algebraic zero is contextually invisible, so

\[
I_M\subseteq N_{\mathrm{sc}}.
\tag{13}
\]

Hence there is a canonical surjection

\[
\pi_M:
\mathcal A_M
=
\mathbb T_{\mathrm{sc}}/I_M
\longrightarrow
\widehat{\mathcal A}_D
=
\mathbb T_{\mathrm{sc}}/N_{\mathrm{sc}}.
\tag{14}
\]

Because the physical-handle row is included among the contexts,

\[
x_M=\widehat x\circ\pi_M.
\tag{15}
\]

Writing \(\mathfrak m_M=\ker x_M\), surjectivity gives

\[
\pi_M(\mathfrak m_M^k)
=
\widehat{\mathfrak m}^{\,k}
\qquad
(k\ge1).
\tag{16}
\]

Therefore (14) induces a canonical filtered surjection

\[
\pi_{M,x}^{(2)}:
J_{M,x}^2
=
\mathcal A_M/\mathfrak m_M^3
\longrightarrow
\widehat J^2.
\tag{17}
\]

### Theorem 4 — faithful raw-context-to-two-jet theorem

For a fixed consistent candidate \(M\), the following are equivalent.

1. The contextual quotient is faithful through order two at \(x\):

   \[
   \pi_{M,x}^{(2)}
   \text{ is an isomorphism}.
   \]

2. The complete contextual kernel contains no nonzero event jet:

   \[
   \ker\pi_M\subseteq\mathfrak m_M^3.
   \tag{18}
   \]

3. In the raw term algebra,

   \[
   N_{\mathrm{sc}}
   \subseteq
   I_M+\mathfrak n_x^3,
   \tag{19}
   \]

   where \(\mathfrak n_x\) is the kernel of the physical character on the raw
   term algebra.

4. The true and contextual two-jets have equal finite dimension:

   \[
   \dim J_{M,x}^2
   =
   \dim\widehat J^2.
   \tag{20}
   \]

5. Both filtered excesses vanish:

   \[
   e_1(M)
   =
   \dim J_{M,x}^1-\dim\widehat J^1
   =0,
   \tag{21}
   \]

   \[
   e_K(M)
   =
   \dim K_{M,x}-\dim\widehat K
   =0.
   \tag{22}
   \]

When these conditions hold, (17) identifies

\[
J_{M,x}^1\simeq\widehat J^1,
\qquad
K_{M,x}\simeq\widehat K,
\qquad
U_{M,x}\simeq\widehat U_x.
\tag{23}
\]

#### Proof

The kernel of (17) is

\[
\frac{\ker\pi_M+\mathfrak m_M^3}{\mathfrak m_M^3}.
\]

This proves the equivalence of (1)--(3).  The map is a surjection between
finite-dimensional spaces, so it is an isomorphism exactly when the dimensions
agree, proving (4).

For both the candidate and contextual jets there is a short exact sequence

\[
0\longrightarrow K
\longrightarrow J^2
\longrightarrow J^1
\longrightarrow0.
\]

The maps induced by (17) on \(J^1\) and \(K\) are surjective.  Hence
\(e_1(M)\ge0\), \(e_K(M)\ge0\), and

\[
\dim J_{M,x}^2-\dim\widehat J^2
=
e_1(M)+e_K(M).
\]

The full dimension excess vanishes exactly when both filtered excesses vanish,
proving (5).

### Corollary 2 — the dimension-squeeze certificate

Put

\[
\widehat r_2=\dim\widehat J^2.
\]

Every consistent candidate obeys

\[
\dim J_{M,x}^2\ge\widehat r_2.
\tag{24}
\]

If the independent event class proves

\[
\dim J_{M,x}^2\le\widehat r_2
\quad
\text{for every model consistent with the intervals},
\tag{25}
\]

then every canonical map (17) is an isomorphism and the raw two-jet is
certified within that class.

The upper bound in (25) may come from a bounded presentation and a local
Macaulay-rank certificate.  It may not come from \(n_J\).

### 5.2 Finite Macaulay implementation

Suppose

\[
\mathcal A_M
=
\mathbb R[z_1,\ldots,z_q]/I_M
\]

within the bounded presentation class, and the physical character has
registered values

\[
\lambda_i=x_M(z_i).
\]

Set

\[
y_i=z_i-\lambda_i
\]

and let

\[
V_2
=
\operatorname{span}
\{1,\ y_i,\ y_iy_j:1\le i\le j\le q\}.
\tag{26}
\]

This is a response-generator coefficient space, not a spacetime coordinate
space.  Its dimension is

\[
N_2
=
1+q+\frac{q(q+1)}2.
\]

For bounded generators \(F_\alpha\) of \(I_M\), form the local Macaulay matrix
whose rows are the coefficients in \(V_2\) of

\[
[hF_\alpha]_{\bmod\,\mathfrak n_x^3},
\qquad
h\in V_2.
\tag{27}
\]

Its row space is

\[
R_{M,x}^{(2)}
=
\frac{I_M+\mathfrak n_x^3}{\mathfrak n_x^3}
\subseteq V_2.
\tag{28}
\]

Therefore

\[
J_{M,x}^2
\simeq
V_2/R_{M,x}^{(2)}
\tag{29}
\]

and

\[
\dim J_{M,x}^2
=
N_2-\operatorname{rank}M_{M,x}^{(2)}.
\tag{30}
\]

All entries are polynomial functions of relation coefficients and physical
character values.  Rank alternatives are finite systems of vanishing and
nonvanishing minors.  Consequently the adversarial question

\[
\exists M\text{ consistent with }D:
\dim J_{M,x}^2\ge \widehat r_2+1
\tag{31}
\]

is a finite semialgebraic feasibility problem inside a bounded
\(\mathcal C_X(B_X)\).

Infeasibility of (31) is an auditable class-relative faithfulness certificate.

---

## 5.3 Regularity is a separate class-relative gate

Once a faithful filtered two-jet has been obtained, raw algebra determines the
embedding dimension

\[
d_{\mathrm{emb}}
=
\dim\mathfrak m_x/\mathfrak m_x^2
\]

and the degree-two multiplication map

\[
\mu_2:
\operatorname{Sym}^2(
\mathfrak m_x/\mathfrak m_x^2
)
\longrightarrow
\mathfrak m_x^2/\mathfrak m_x^3.
\tag{31a}
\]

If \(\mu_2\) is not an isomorphism, the regular-germ class is excluded at that
character.

If \(\mu_2\) is an isomorphism, regularity is not yet certified: a defining
relation may begin in order three or higher and therefore be invisible in
\(J_x^2\).  Before the jet-null principal theorem is applied, the independent
event class must additionally prove regularity, for example by a
Jacobian/local-dimension certificate on the bounded presentation.

Section 9.5 gives an exact regular-versus-singular pair with identical
two-jets.

---

## 6. The strongest general certificate: the two-jet alias system

Faithfulness of the whole contextual algebra is sufficient but not necessary.
A restrictive response normal-form class can select unique jet lifts even
when (17) has a kernel.  The exact general criterion is therefore stated on
the class-allowed scalar term space.

Let \(V\) be the finite coefficient space guaranteed by \(B_X\) to contain all
registered gates, prepared scalar sources, recycled Green outputs, and the
products required by the order-two construction.

For each consistent candidate \(\theta\), raw contexts give a finite signature
map

\[
C_\theta:V\to Y,
\]

and its bounded event presentation gives an algebraic two-jet map

\[
J_{\theta,x}:V\to J_{\theta,x}^2.
\]

No target derivative is supplied: \(J_{\theta,x}\) is obtained by the
centered-generator truncation (26)--(29).

### Theorem 5 — uniform class-relative two-jet criterion

Assume all candidate filtered jet algebras have been identified with a common
filtered algebra \(J_*^2\) by isomorphisms that preserve the registered scalar
generator classes.  Then raw contextual signatures determine a unique
two-jet for every class-allowed scalar response if and only if

\[
C_\theta v=C_{\theta'}v'
\Longrightarrow
\Phi_\theta J_{\theta,x}v
=
\Phi_{\theta'}J_{\theta',x'}v'
\tag{32}
\]

for every pair of data-consistent candidates
\(\theta,\theta'\) and every pair of allowed terms \(v,v'\).

Equivalently, the **alias witness set**

\[
\mathfrak A_2(D)
=
\left\{
(\theta,\theta',v,v'):
\begin{array}{l}
\theta,\theta'\text{ satisfy all class and interval constraints},\\
C_\theta v=C_{\theta'}v',\\
\Phi_\theta J_{\theta,x}v
\ne
\Phi_{\theta'}J_{\theta',x'}v'
\end{array}
\right\}
\tag{33}
\]

is empty.

For one fixed exact candidate and one common coefficient space, this reduces
to

\[
\ker C\subseteq\ker J_x,
\tag{34}
\]

or, equivalently,

\[
\operatorname{rank}
\begin{pmatrix}
C\\
J_x
\end{pmatrix}
=
\operatorname{rank}C.
\tag{35}
\]

The apparently circular condition has therefore become a finite internal
certificate: \(J_x\) is not an external oracle but a matrix generated from
the bounded relation variables and the registered character by (26)--(29).

A sharp data-only sufficient condition is

\[
\ker C=0
\tag{36}
\]

on the complete bounded response term space.  Then the raw signatures identify
the term itself before any jet quotient.  This condition is stronger than
necessary but is often the best experimental design target.

### Proof

If (32) holds, assign to a raw signature \(y=C_\theta v\) the common value
\(\Phi_\theta J_{\theta,x}v\).  The implication makes the assignment
independent of the candidate and representative, so it is a well-defined
two-jet reconstruction map.

Conversely, any well-defined reconstruction map must assign the same jet to
equal raw signatures, giving (32).

Because \(B_X\) bounds all coefficients, degrees, ranks, character branches,
and normal-form dimensions, nonemptiness of (33) is a finite semialgebraic
question after replacing the final inequality by a normalized nonzero
witness.

### Interpretation

There are two legitimately different certification routes.

1. **Data-faithful route.**  The complete contextual quotient is faithful
   through order two.  This is Theorem 4 and the dimension squeeze.

2. **Class-pinned route.**  The raw quotient has hidden jet lifts, but every
   class-allowed prepared response has the same lift.  This is Theorem 5.
   The report must label the result class-pinned, not data-faithful.

Without either route, the output is inconclusive.

---

## 7. Scalar anchoring of Green outputs

The adopted principal theorem requires

\[
U_x:W\to J_x^2(\mathcal A),
\]

not merely a jet in an unrelated output module.

### Proposition 1 — scalar anchoring condition

Let \(\widehat E_D\) be the saturated scalar-output module.  A raw response
column has a well-defined class in the event algebra if and only if its
complete contextual signature is substitution-equivalent to a scalar algebra
term.

Operationally, it is sufficient to register response recycling:

\[
u=\mathrm{Resp}(s)
\quad\mapsto\quad
u\text{ may occupy any scalar gate hole}.
\tag{37}
\]

The resulting mixed contexts test equality between \(u\) and ordinary scalar
gate terms and produce the map (5).

If no cross-type operation relates \(\widehat E_D\) to
\(\widehat{\mathcal A}_D\), an independent automorphism of the output module is
a symmetry of all typed raw data.  The statement that an output vector has a
particular event-algebra two-jet is then not operationally defined.

Thus response recycling, or an equivalent jointly separating
\(\mathcal A\)-linear anchoring map, is the minimal generic repair.

---

## 8. Source-fiber functional

Let \(S\) be the declared source module over \(\mathcal A\), and let
\(\mathbb R_x\) be the one-dimensional module on which \(a\in\mathcal A\) acts
as multiplication by \(x(a)\).

### Theorem 6 — source-fiber calibration theorem

There is a canonical isomorphism

\[
\operatorname{Hom}_{\mathcal A}(S,\mathbb R_x)
\simeq
\left(S/\mathfrak m_xS\right)^*.
\tag{38}
\]

Hence gate action and the reconstructed character determine the source fiber

\[
S_x=S/\mathfrak m_xS,
\]

but do not select a particular source-fiber functional.

#### Proof

If \(B:S\to\mathbb R_x\) is \(\mathcal A\)-linear and
\(a\in\mathfrak m_x\), then

\[
B(as)=x(a)B(s)=0.
\]

Thus \(B\) factors through \(S_x\).  Conversely, for
\(b\in S_x^*\), define \(B(s)=b([s])\).  Since

\[
as-x(a)s\in\mathfrak m_xS,
\]

this lift is \(\mathcal A\)-linear.

### Minimal calibration

Let

\[
\overline S_x:W\to S_x
\]

be the prepared source-fiber map, and put

\[
r_W=\dim\operatorname{im}\overline S_x.
\]

To determine

\[
B_x=B\circ S_W:W\to\mathbb R
\]

for an arbitrary source module, exactly \(r_W\) independent scalar
calibrations are necessary and sufficient.

For the conformal principal branch only

\[
\beta_x=B_x|_{Z_x}
\]

is needed.  Then the minimum number is

\[
r_Z
=
\dim\overline S_x(Z_x).
\tag{39}
\]

In the cyclic scalar-source branch

\[
S=\mathcal A s_0,
\qquad
B_x(s_0)=1,
\tag{40}
\]

one unit calibration is sufficient:

\[
B_x(a s_0)=x(a).
\tag{41}
\]

An equivalent operation is an \(\mathcal A\)-linear source bypass

\[
\kappa:S\to\mathcal A
\]

with

\[
B_x=x\circ\kappa.
\tag{42}
\]

This uses the already reconstructed physical character and does not introduce
a stronger hidden target-space localizer.

Without (39)--(42), \(B_x\) is not identifiable from Green readouts alone.

---

## 9. Exact no-go theorems and countermodels

### 9.1 Shallow equivalence is not a gating congruence

Let

\[
s=
\begin{pmatrix}1\\0\end{pmatrix},
\qquad
\rho=
\begin{pmatrix}1&0\end{pmatrix},
\]

and gate matrices

\[
A=
\begin{pmatrix}
0&0\\
0&0
\end{pmatrix},
\qquad
B=
\begin{pmatrix}
0&0\\
1&0
\end{pmatrix},
\qquad
C=
\begin{pmatrix}
0&1\\
0&0
\end{pmatrix}.
\tag{43}
\]

Then

\[
\rho As=\rho Bs=0,
\]

but

\[
\rho CAs=0,
\qquad
\rho CBs=1.
\tag{44}
\]

Thus one-layer equality of \(A\) and \(B\) is not stable under gate
continuation.  The state dimension two is minimal.

### 9.2 Raw-only event-jet no-go with two reduced regular models

Let the registered scalar gate alphabet contain \(t,u\).  Consider

\[
\mathcal A_0
=
\mathbb R[t,u]/(u)
\simeq
\mathbb R[t],
\tag{45}
\]

and

\[
\mathcal A_1
=
\mathbb R[t,u].
\tag{46}
\]

At the physical character \(x(t)=x(u)=0\), both algebras are reduced and
regular.  Their two-jets have dimensions

\[
\dim J_{0,x}^2=3,
\qquad
\dim J_{1,x}^2=6.
\tag{47}
\]

Let every registered source, response and readout representation factor
through the quotient

\[
q:\mathcal A_1\to\mathcal A_0,
\qquad
q(u)=0.
\tag{48}
\]

Then every raw contextual tensor, at every gate depth, is identical in the two
models.  Their response-Hankel realization orders are also identical.

On the ordered jet bases

\[
(1,t,t^2)
\]

and

\[
(1,t,u,t^2,tu,u^2),
\]

the raw quotient map is

\[
P=
\begin{pmatrix}
1&0&0&0&0&0\\
0&1&0&0&0&0\\
0&0&0&1&0&0
\end{pmatrix}.
\tag{49}
\]

Its kernel contains one first-order and two quadratic directions.

Therefore no finite or infinite raw-context procedure can certify the event
two-jet for a class containing both models.  The missing assumption is not
more response depth.  It is local event-algebra completeness.

More generally, for any regular \(d\)-dimensional candidate, adjoining a
regular generator \(u\) that acts trivially in every registered representation
changes

\[
\dim J^1
\quad\text{by }1
\]

and changes

\[
\dim K
\quad\text{by }d+1
\]

without changing any raw data.

### 9.3 A readout kernel can collapse a quadratic response jet

Fix the reduced algebra

\[
\mathcal A=\mathbb R[t],
\qquad
x(t)=0.
\]

Let every output readout annihilate the ideal \((t^2)\).  For example, use the
constant and linear coefficient functionals.  For every polynomial gate
\(p(t)\),

\[
p(t)t^2\in(t^2),
\]

so

\[
\rho\bigl(p(t)t^2\bigr)=0
\]

for every registered gated readout.

Two Green maps that differ on one source seed by

\[
G_1s-G_0s=t^2
\tag{50}
\]

therefore have identical raw contextual data at every depth, but

\[
j_0^2(G_1s)-j_0^2(G_0s)
=
[t^2]\ne0.
\tag{51}
\]

On the jet basis \((1,t,t^2)\), a minimal matrix realization is

\[
T_t=
\begin{pmatrix}
0&0&0\\
1&0&0\\
0&1&0
\end{pmatrix},
\qquad
R_{\mathrm{bad}}
=
\begin{pmatrix}
1&0&0\\
0&1&0
\end{pmatrix},
\qquad
u_{\mathrm{hidden}}
=
\begin{pmatrix}0\\0\\1\end{pmatrix}.
\tag{52}
\]

Every gated readout of \(u_{\mathrm{hidden}}\) is zero.

The smallest repair is one additional independent context row nonzero on the
hidden quadratic direction, for example

\[
\rho_2=
\begin{pmatrix}0&0&1\end{pmatrix}.
\tag{53}
\]

In general the required repair is a rank increase equal to the unresolved
jet-alias dimension.  One hardware readout may supply several such rows
through gate continuation.

### 9.4 A singular character visible at order two

Let

\[
\mathcal A_{\mathrm{node}}
=
\mathbb R[u,v]/(uv),
\qquad
x(u)=x(v)=0.
\tag{54}
\]

Modulo \(\mathfrak m^3\), use the basis

\[
(1,u,v,u^2,v^2).
\]

Then

\[
\dim\mathfrak m/\mathfrak m^2=2,
\qquad
\dim\mathfrak m^2/\mathfrak m^3=2.
\]

The degree-two multiplication map

\[
\mu_2:
\operatorname{Sym}^2(\mathfrak m/\mathfrak m^2)
\to
\mathfrak m^2/\mathfrak m^3
\]

has matrix

\[
M_{\mu_2}
=
\begin{pmatrix}
1&0&0\\
0&0&1
\end{pmatrix}
\tag{55}
\]

on the ordered source basis \((u^2,uv,v^2)\).  Its kernel is generated by
\(uv\), so the character is singular and must not be passed to the regular
principal-biform theorem.

The multiplication matrices through order two are

\[
T_u=
\begin{pmatrix}
0&0&0&0&0\\
1&0&0&0&0\\
0&0&0&0&0\\
0&1&0&0&0\\
0&0&0&0&0
\end{pmatrix},
\qquad
T_v=
\begin{pmatrix}
0&0&0&0&0\\
0&0&0&0&0\\
1&0&0&0&0\\
0&0&0&0&0\\
0&0&1&0&0
\end{pmatrix}.
\tag{56}
\]

### 9.5 Two-jets alone cannot certify regularity

Consider

\[
\mathcal A_{\mathrm{reg}}
=
\mathbb R[u,v]
\]

and

\[
\mathcal A_{\mathrm{cusp}}
=
\mathbb R[u,v]/(v^3-u^4)
\]

at the origin.  Since the defining relation of the second algebra lies in
\(\mathfrak m^3\),

\[
J_{\mathrm{reg},0}^2
\simeq
J_{\mathrm{cusp},0}^2.
\tag{57}
\]

Nevertheless the first local ring is regular of dimension two, while the
second is a singular one-dimensional domain.

Therefore even a faithful two-jet does not, by itself, certify regularity.
Regularity must be supplied by the bounded event presentation, a Jacobian/local
dimension certificate, or an independent promise that all allowed
singularities are detected by order two.

### 9.6 No physical handle means no selected character

Let

\[
\mathcal A
=
\mathbb R[e]/(e^2-e)
\simeq
\mathbb R\oplus\mathbb R.
\]

Suppose all raw readouts are invariant under the algebra automorphism

\[
e\longmapsto1-e.
\]

For example, the trace readout

\[
\tau(a,b)=a+b
\]

and all its gated continuations have this symmetry.  The two characters

\[
x_0(e)=0,
\qquad
x_1(e)=1
\]

are exactly indistinguishable unless a repeatable physical handle breaks the
swap symmetry.  A source term \(e\) has different target evaluation in the two
branches.

The smallest repair is one multiplicative handle calibration row that selects
one branch.  Choosing an abstract character without such a row is prohibited.

### 9.7 Even with \(x\), the source fiber is not determined by \(G\)

Let

\[
\mathcal A=\mathbb R,
\qquad
S=\mathbb R^2,
\qquad
E=\mathbb R,
\]

with

\[
G=
\begin{pmatrix}1&0\end{pmatrix}
\]

and identity output readout.  The raw Green matrix is

\[
Y=
\begin{pmatrix}1&0\end{pmatrix}.
\tag{58}
\]

Both

\[
B_0=
\begin{pmatrix}1&0\end{pmatrix}
\]

and

\[
B_1=
\begin{pmatrix}1&1\end{pmatrix}
\tag{59}
\]

are valid source-fiber functionals and give the same raw Green data.  One
additional calibration of the second source-fiber basis vector is necessary
and sufficient.

---

## 10. Smallest exact positive toy

The smallest nontrivial regular event germ has one visible differential
direction.  Its two-jet has dimension three.

### 10.1 Hidden proof model

Use the local jet algebra

\[
J^2
=
\mathbb R[\tau]/(\tau^3)
\]

only inside the proof simulator.  The inference routine is given one opaque
gate token, anonymous source/readout bases, multiplication records, and a
physical-handle row.  It is not told that the token is called \(\tau\).

On the ordered hidden basis

\[
(1,\tau,\tau^2),
\]

multiplication by the gate is

\[
T=
\begin{pmatrix}
0&0&0\\
1&0&0\\
0&1&0
\end{pmatrix}.
\tag{60}
\]

Use the anonymous readout frame

\[
R=
\begin{pmatrix}
1&1&0\\
0&1&1\\
1&0&1
\end{pmatrix},
\qquad
\det R=2.
\tag{61}
\]

No row is labeled as a value, derivative, or localized probe.

The unit calibration state and physical character are

\[
c_0=
\begin{pmatrix}1\\0\\0\end{pmatrix},
\qquad
x=
\begin{pmatrix}1&0&0\end{pmatrix}.
\tag{62}
\]

The scalar context signature matrix of
\((1,\tau,\tau^2)\) is

\[
R[c_0,Tc_0,T^2c_0]=R,
\]

so it has rank three.  The one-step extension satisfies

\[
T^3c_0=0.
\]

With independent realization bound \(n_J=3\), the residual context quotient is
closed.

### 10.2 Prepared sources and scalar response recycling

Take two prepared source columns

\[
S=
\begin{pmatrix}
1&0\\
0&1\\
0&0
\end{pmatrix}
\]

and let the scalar Green response be the registered operator

\[
G=T.
\]

Then

\[
U=GS
=
\begin{pmatrix}
0&0\\
1&0\\
0&1
\end{pmatrix},
\tag{63}
\]

and the raw readout tensor is

\[
Y=RU
=
\begin{pmatrix}
1&0\\
1&1\\
0&1
\end{pmatrix}.
\tag{64}
\]

The two outputs are recyclable scalar terms, so their contextual classes are
the gate and its square.

Use the cyclic source calibration

\[
B(s_0)=1.
\]

Then

\[
B=xS
=
\begin{pmatrix}1&0\end{pmatrix}.
\tag{65}
\]

The contextual maximal ideal and its powers are

\[
\widehat{\mathfrak m}
=
\operatorname{span}\{\tau,\tau^2\},
\]

\[
\widehat{\mathfrak m}^{\,2}
=
\operatorname{span}\{\tau^2\},
\qquad
\widehat{\mathfrak m}^{\,3}=0.
\]

Thus

\[
\dim\widehat J^1=2,
\qquad
\dim\widehat K=1,
\qquad
\dim\widehat J^2=3.
\tag{66}
\]

### 10.3 Independent event-class promise

The positive certification does not follow from \(n_J=3\).  The toy declares
independently that every consistent event model has:

- one registered generator through first order;
- a regular local ring at the selected handle;
- local two-jet dimension at most three;
- scalar response recycling;
- the cyclic source calibration (40).

The raw quotient already has dimension three.  The dimension squeeze therefore
forces every map (17) to be an isomorphism.

This is a non-circular toy because the inference input contains only:

- opaque gate/source/readout tokens;
- finite matrices (60)--(65);
- a separately declared event-class upper bound.

The hidden name \(\tau\) and the displayed basis are randomized before every
test.

---

## 11. Invariance

### Theorem 7 — basis and generator invariance

All exact verdicts above are invariant under:

1. permutations of opaque source, gate, readout and physical-handle tokens;

2. invertible source-basis changes

   \[
   S_W\mapsto S_WA,
   \qquad
   U_x\mapsto U_xA,
   \qquad
   B_x\mapsto B_xA;
   \]

3. invertible readout-basis changes

   \[
   C\mapsto LC,
   \]

   which leave \(\ker C\), contextual equivalence and alias-witness emptiness
   unchanged;

4. similarity changes of a minimal residual realization;

5. filtered response-generator changes at the selected character.

For the last item, a general order-two centered change has the form

\[
y_i'
=
A_i{}^j y_j
+
B_i{}^{jk}y_jy_k
\pmod{\mathfrak m^3},
\qquad
A\in GL_d.
\tag{67}
\]

On the filtered basis

\[
(1,\ y,\ \operatorname{Sym}^2y)
\]

it induces a block triangular matrix with invertible diagonal blocks

\[
1,\qquad A,\qquad\operatorname{Sym}^2A.
\tag{68}
\]

Hence it preserves:

- the powers of the maximal ideal;
- \(\dim J^1\) and \(\dim K\);
- faithfulness of (17);
- all exact ranks;
- emptiness of the alias witness set;
- the response jet map up to the induced filtered isomorphism.

Numerical singular values are invariant only after calibrated norms are
transformed with the bases.  An unqualified numerical gap is not geometric.

---

## 12. Finite-noise theorem

All finite-noise claims are relative to calibrated coefficient, source and
readout norms.

For a compact interval family of matrices \(\mathbb M\), define

\[
\underline\sigma_k(\mathbb M)
=
\inf_{M\in\mathbb M}\sigma_k(M).
\tag{69}
\]

Let \(\mathfrak M(D)\) be the complete set of exact models in
\(\mathcal C_R(n_J)\times\mathcal C_X(B_X)\) consistent with all measured
intervals.

### Theorem 8 — robust contextual two-jet certificate

Assume:

1. **Residual closure gap.**
   The response class gives a rank upper bound \(r_R\) for the saturated
   Hankel and one-step extension matrices, and

   \[
   \underline\sigma_{r_R}(\mathbb H_{\mathrm{ext}})>0.
   \tag{70}
   \]

2. **Character isolation.**
   Every consistent model assigns the selected physical handle to the same
   character branch, or to a declared character tube of diameter
   \(\delta_x\), separated from all other branches by a positive calibrated
   gap.

3. **Loewy-rank gaps.**
   The matrices generating
   \(\widehat{\mathfrak m}^{\,2}\) and
   \(\widehat{\mathfrak m}^{\,3}\) from the contextual multiplication table
   have fixed ranks over all consistent models, with their smallest nonzero
   singular values bounded below by

   \[
   \gamma_{\mathrm{mult}}>0.
   \tag{71}
   \]

4. **Scalar anchoring gap.**
   Every prepared response has a unique contextual scalar class, or all such
   classes lie in a declared quotient tube of radius \(\delta_U\).

5. **No hidden jet excess.**
   The finite class search proves

   \[
   e_2^{\max}
   =
   \max_{M\in\mathfrak M(D)}
   \left(
   \dim J_{M,x}^2-\dim\widehat J^2
   \right)
   =0,
   \tag{72}
   \]

   or proves the more general alias set (33) empty.

6. **Source calibration gap.**
   The registered calibration functionals have full rank on the required
   prepared source fiber, with smallest singular value at least
   \(\gamma_B>0\).

Then the filtered dimensions

\[
\dim J^1,\qquad
\dim K,\qquad
\dim J^2
\]

are exact and common to every consistent model.  The response and source maps
lie in finite computable tubes

\[
U_x\in\mathbb U_x(D),
\qquad
B_x\in\mathbb B_x(D),
\tag{73}
\]

whose radii tend to zero with the raw interval widths.

If a nominal rank-\(r\) matrix \(\widehat C\) has perturbation bound

\[
\|C-\widehat C\|_2\le\eta
\]

for every consistent \(C\), and

\[
\sigma_r(\widehat C)>\eta,
\]

then, after the class fixes the rank at \(r\), Wedin's bound gives

\[
\left\|
\sin\Theta(
\ker C,\ker\widehat C
)
\right\|_2
\le
\frac{\eta}
{\sigma_r(\widehat C)-\eta}.
\tag{74}
\]

The same bound applies to the maximal-ideal power subspaces and the
jet-null spaces used in response 0001.  All downstream rank and signature
claims must use the propagated tube, not the nominal nullspace.

### Three-state rule

For the target property \(P_2\) that the raw apparatus determines a regular
faithful two-jet, scalar response map and required source fiber:

- **certified within class**
  if \(\mathfrak M(D)\ne\varnothing\) and every consistent model satisfies
  \(P_2\), with all declared rank and separation gaps positive;

- **class excluded**
  if the complete declared class is inconsistent with the intervals, or if
  the class is nonempty but no consistent model satisfies \(P_2\); the report
  must state which exclusion occurred;

- **inconclusive**
  if faithful and nonfaithful candidates both remain, if character branches
  remain unresolved, if scalar anchoring is not unique, if source-fiber
  calibration is incomplete, or if a required singular gap closes.

A rank deficit never proves a different spacetime dimension.  It proves only
that the present apparatus has not separated the missing jet directions.

---

## 13. Seven-day implementation kill test

### Day 1 — typed congruence engine

Implement the raw term/context grammar and the saturated residual quotient.

Run the two-state matrices (43).  Shallow equality of \(A\) and \(B\) must be
reported, but the continuation \(C\) must split them.  The final quotient must
never identify them.

Verify left/right kernel invariance explicitly.

### Day 2 — positive Loewy toy

Implement (60)--(66).

Recover, without hidden labels,

\[
\dim\widehat J^1=2,
\qquad
\dim\widehat K=1,
\qquad
\dim\widehat J^2=3,
\]

together with \(U\) and \(B\).

Run at least \(10^4\) exact trials with:

- random token permutations;
- random invertible source and readout changes;
- random residual-state similarities;
- random filtered generator changes
  \(\tau'\!=a\tau+b\tau^2\), \(a\ne0\).

All verdicts and filtered dimensions must be invariant.

### Day 3 — event-completeness no-go

Implement the pair (45)--(49).  Feed exactly the same all-depth contextual
representation to both candidates.

The procedure must return inconclusive unless the independent event-class
bound excludes one model.

Then impose the local upper bound

\[
\dim J_x^2\le3.
\]

The dimension squeeze must certify the three-dimensional jet.

### Day 4 — response-jet alias and recycling

Implement (50)--(53).  With \(R_{\mathrm{bad}}\), the two Green outputs must be
exactly indistinguishable and the response two-jet verdict must be
inconclusive.

Add only \(\rho_2\).  The hidden quadratic direction must become visible.

Separately disable response recycling.  The program must report that the
output is only an abstract module element and refuse to place it in
\(J_x^2(\mathcal A)\).

### Day 5 — character and regularity

Implement the physical-handle swap model in Section 9.6.  Without a handle
calibration, the character must be inconclusive.  Add one multiplicative row
and verify branch selection.

Implement the node matrices (56).  The multiplication map (55) must report a
singular character.

Then compare the regular plane and high-order cusp in (57).  The program must
not certify regularity from their common two-jet.

### Day 6 — source-fiber calibration

Implement (58)--(59).  Raw Green data must leave \(B\) ambiguous.

Add one calibration on the second source-fiber basis vector and recover \(B\).

For random source modules verify that the number of independent calibrations
needed is exactly

\[
r_W=\dim\operatorname{im}(W\to S_x),
\]

and that only \(r_Z\) are needed when the downstream target is
\(\beta=B|_Z\).

### Day 7 — interval and adversarial audit

Add interval perturbations aligned with the smallest nonzero singular vectors
of:

- the context Hankel;
- the scalar anchoring matrix;
- the maximal-ideal product matrices;
- the source calibration matrix.

Compute the complete bounded candidate set for the minimal toys and compare:

- direct pairwise alias search;
- the dimension-squeeze certificate;
- the singular-subspace bound (74).

Required behavior:

- no false faithful-jet certification;
- transition from certified to inconclusive as a gap closes;
- no transition directly to an incorrect certified dimension;
- no use of \(n_J\) as an event-dimension or relation-degree bound.

### Hard stop conditions

Stop the raw-to-cone paper and retain only the no-go layer if any of the
following occurs.

1. The shallow pair (43) is ever quotient-identified.
2. The two regular models (45)--(46) are distinguished by data that were
   constructed to factor through (48).
3. A faithful two-jet is certified without either an empty alias set or an
   independent local-dimension/completeness bound.
4. The hidden response \(t^2\) in (50) receives a unique jet before the repair
   (53).
5. Disabling response recycling still produces an event-algebra response jet.
6. The high-order cusp is certified regular from its two-jet alone.
7. \(B_x\) is inferred on an uncalibrated source-fiber direction.
8. A token permutation, source/readout basis change, residual similarity, or
   filtered generator change alters an exact verdict.
9. Any numerical nullspace is treated as exact without a class rank bound and
   a calibrated singular gap.

If the exact algebra succeeds but interval tubes are too wide, retain the
theorems and redesign the apparatus to maximize:

\[
\gamma_{\mathrm{ctx}},
\qquad
\gamma_{\mathrm{mult}},
\qquad
\gamma_{\mathrm{anchor}},
\qquad
\gamma_B,
\]

rather than weakening the certification semantics.

---

## 14. Architectural consequence

The raw-to-principal program should not use

\[
\text{finite readout matrix}
\longrightarrow
\text{guessed }j_x^2.
\]

It should use

\[
\boxed{
\begin{aligned}
\text{raw typed contexts}
&\longrightarrow
\text{full substitution congruence}\\
&\longrightarrow
\text{physical contextual algebra and handle}\\
&\longrightarrow
\text{contextual Loewy quotient}\\
&\longrightarrow
\text{alias-exclusion or dimension squeeze}\\
&\longrightarrow
\text{source-fiber calibration}\\
&\longrightarrow
(U_x,B_x).
\end{aligned}
}
\]

The key distinction is:

\[
\boxed{
\text{canonical raw two-jet}
\ne
\text{faithful event two-jet}
}
\]

unless a separate local completeness statement is proved.

The minimal additional registered capabilities are therefore precisely:

1. **full substitutional gating contexts**, closed by
   \(\mathcal C_R(n_J)\);

2. **scalar response recycling**, or an equivalent cross-type
   \(\mathcal A\)-linear anchoring operation;

3. **a physical multiplicative handle row** selecting \(x\);

4. **enough independent jet-separating context rank**, or an independent
   class promise that gives the matching local two-jet upper bound;

5. **a calibrated source-fiber frame**, reduced to one scalar in the cyclic
   unit-source branch.

With these in place, the output of this response feeds the independently
verified theorem from decision 0002 without circularity:

\[
Z_x=\ker(\pi_xU_x),
\qquad
H_x=U_x|_{Z_x},
\qquad
\beta_x=B_x|_{Z_x},
\]

\[
\mathcal Q_x(D)
=
\{q\in K_x^*:qH_x=\beta_x\}.
\]

For a regular four-dimensional scalar germ, the next-stage conformal
principal-ray test remains

\[
\beta_x=0,
\qquad
\operatorname{rank}H_x=9.
\]

The present result establishes exactly what must be certified before those
symbols are allowed to enter that test.
