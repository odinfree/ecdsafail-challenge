# Curve-Support Product-Invariant Verdict

Verdict: `HARD_NACK_AFFINE_CURVE_PRODUCT_SUPPORT`

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Complete `pp_mul` traversal: T426844.55.
- Conservative replacement ceiling: T335738.86.
- Exact receipt: `46-curve-support-product-invariant-receipt.json`, embedded
  SHA-256
  `20fa77e0d8bb351092fda7ead1da40f108b470fad501a184d21f3276abaa813b`.

## Exact census

The falsifier exhaustively enumerated 32,750 curve-supported shell states over
the adjacent prime widths 5 through 14. At every width it tested every mixed
partial product `T_i AND lambda_j` against the exact GF(2) affine span of the
constant and all live `T` and `lambda` bits. It also tested every bit of
`T*lambda mod p`.

Across 985 bit-pair searches and 95 modular-output-bit searches, the number of
affine hits was exactly zero. The shared-denominator identity held on every
support row. Positive affine controls passed at every width, and a full Boolean
support control rejected AND.

This is stronger than a failed persistence threshold: there is no candidate
relation at any tested width to normalize or transfer.

## Scope

This closes affine simplification of mixed product cells and modular product
bits on the exact reduced-width curve support. It does not close:

- quadratic or higher-degree support relations;
- a rational two-register transducer;
- an explicit nonlinear in-place compactor/decompactor;
- an arbitrary-width circuit proof with a different representation.

The next grammar is `NONLINEAR_SUPPORT_COMPACTOR`. Its first falsifier asks
whether mixed `T/lambda` products can be represented by affine terms plus
quadratics internal to either register, which would replace a general mixed
multiply with separate-register nonlinear structure.

## Authority

Provider, nonce-grind, push, public-note, promotion, and submission authority
remain false.
