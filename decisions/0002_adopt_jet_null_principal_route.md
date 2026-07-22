# Decision 0002 — adopt the jet-null principal route

Date: 2026-07-22

## Decision

The primary finite Green-to-cone theorem will use lower-jet-null response
superpositions, not inversion of a measured Green compression and not the
former common-reducing-space assumption.

At a regular event character, let

\[
0\to K_x\to J_x^2\xrightarrow{\pi_x}J_x^1\to0.
\]

For a measured response two-jet map \(U_x:W\to J_x^2\) and registered source
fiber \(B_x:W\to\mathbb R\), define

\[
Z_x=\ker(\pi_xU_x),\qquad
H_x=U_x|_{Z_x},\qquad
\beta_x=B_x|_{Z_x}.
\]

The unrestricted pointwise inverse-functional fiber

\[
\mathfrak F_x
=
\{\ell\in(J_x^2)^*:\ell U_x=B_x\}
\]

has principal restriction

\[
\boxed{
\operatorname{res}_{K_x}\mathfrak F_x
=
\{q\in K_x^*:qH_x=\beta_x\}.
}
\]

This identity and its proof in response 0001 were independently checked.

## Exact consequences

The fiber is nonempty exactly when

\[
B_x|_{\ker U_x}=0
\quad\Longleftrightarrow\quad
\beta_x|_{\ker H_x}=0.
\]

If \(p=\dim K_x\), then:

- rank \(p\) identifies the principal functional including scale;
- on a nonzero, non-pinning class, \(\beta_x=0\) and rank \(p-1\) identify one
  projective conformal class and leave scale free;
- smaller rank, or rank \(p-1\) with nonzero \(\beta_x\), leaves exact
  nonconformal ambiguity.

For a regular four-dimensional germ \(p=10\). The scale-free design therefore
requires rank nine and \(B_x|_{Z_x}=0\) on the entire lower-jet-null space. A
tenth probe fixes scale only when it adds a new quadratic direction and has a
nonzero source fiber.

The old reachability condition is the absolute branch because

\[
\operatorname{im}H_x=\operatorname{im}U_x\cap K_x.
\]

## Scope corrections to response 0001

The theorem is a necessary-and-sufficient statement for pointwise second-jet
inverse functionals. It is not by itself a criterion for existence of a
global differential generator, a retarded Green inverse or a member of the
full bounded generator class. Actual generator symbols form a subset of the
displayed affine fiber unless a separate jet-realizability result is proved.

The dimension formula

\[
K_x\simeq\operatorname{Sym}^2(\mathfrak m_x/\mathfrak m_x^2)
\]

requires the degree-two multiplication map to be an isomorphism. A regular
Noetherian local real algebra essentially of finite type, or the ordinary
smooth-germ jet theorem, is a sufficient setting. Singular characters are
reported separately.

Exact ranks and the recovered projective class are basis invariant.
Numerical singular gaps require fixed calibrated inner products. In the 2D
toy, the raw basis \((t^2/2,tx,x^2/2)\) and the matrix-coefficient convention
\((Q_{tt},Q_{tx},Q_{xx})\), where \(q([tx])=2Q_{tx}\), give different
numerical gaps. Neither number is an unqualified geometric invariant.

## Multi-field boundary

For a general two-field principal symbol, a strong common cone means

\[
\mathsf P(\xi)=q(\xi)K,\qquad K\in\operatorname{GL}(F),
\]

throughout the feasible fiber. A squared determinant alone is insufficient:
a Jordan symbol can obey \(\det\mathsf P=q^2\) while having only one generic
kernel polarization on the cone. Complete field polarization, entrywise
factorization and field-factor invertibility remain mandatory.

## Next bottleneck

The adopted theorem assumes \(J_x^2\), \(U_x\) and \(B_x\) have been
operationally reconstructed. Brief 0002 asks whether finite opaque contextual
responses can certify that raw-data-to-two-jet step, or which minimal
independent completeness promise/localizer is unavoidable.

Response 0001 remains stored as a proposed co-theorist record. This decision,
the local proof notes and the passing executable tests are the adopted source
of truth.
