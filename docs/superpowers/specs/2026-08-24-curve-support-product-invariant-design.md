# Curve-Support Product-Invariant Census

Status: approved by the autonomous structural-cut mandate; local falsifier
only.

## Invariant under test

On the exact curve-supported states entering the second affine product, a
material family of partial products or output bits may be affine in the live
`T` and `lambda` bits, allowing nonlinear cells to be deleted without sampling
a nonce.

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Exact current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Complete multiply traversal: T426844.55.
- Conservative replacement ceiling for the 10 percent campaign target:
  T335738.86.
- Wave-2 support identity: `d*T = 2*b*lambda - 3*a^2`; at p=31, 127, and
  251 each `T` has at most two legal `lambda` values.

## Exact model

For adjacent prime widths 5 through 14, choose the first deterministic
nonzero-y point `(a,b)` on `y^2=x^3+7`. Enumerate every affine curve point with
`x != a`, then compute the exact shell state:

```text
d = x-a
lambda = (y-b)/d
T = d+3a-lambda^2
product = T*lambda mod p
```

The affine feature space contains constant one and every live bit of `T` and
`lambda`. For every bit pair `(i,j)`, test whether `T_i AND lambda_j` lies in
that exact GF(2) span on the complete support. Separately test every bit of the
modular product. No term-count cutoff, random sample, nonce, width schedule, or
finite-shot evidence is allowed.

Positive controls must prove that live input bits and XORs are affine. A full
Boolean-support control must reject AND.

## Transfer gate

An observation transfers only when its normalized bit-position pattern
survives at least three adjacent widths and its count scales as `Omega(n)`.
Production admission is stricter: a family must remove a material nonlinear
term, publish an arbitrary-width curve-support proof, identify the live source
wires, and include a two-word reversible cleanup schedule below Q1100 and
T335738.86. Reduced-width affinity alone is never a candidate.

## Falsifier

Issue `HARD_NACK_AFFINE_CURVE_PRODUCT_SUPPORT` if the exhaustive census finds
only constant-size, edge-only, or nonpersistent affine relations. This closes
only affine support simplification of the product cells. It does not close
quadratic support relations, a rational transducer, or an explicit nonlinear
in-place construction.

## Authority

Local Python research only. No production Rust edit, provider action, nonce
grind, push, public note, promotion, or submission is authorized.
