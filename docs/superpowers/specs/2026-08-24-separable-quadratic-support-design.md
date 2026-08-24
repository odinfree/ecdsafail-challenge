# Separable-Quadratic Curve-Support Census

Status: approved by the autonomous structural-cut mandate; exact local
falsifier only.

## Invariant under test

On the exact curve-supported shell states, a material family of mixed partial
products `T_i AND lambda_j`, or modular output bits of `T*lambda mod p`, may lie
in the GF(2) span of:

- constant one;
- every live bit of `T` and `lambda`;
- every within-`T` quadratic `T_i AND T_j` for `i < j`;
- every within-`lambda` quadratic `lambda_i AND lambda_j` for `i < j`.

Such a relation would separate the two live registers at algebraic degree two.
It would not by itself be a circuit, but it could justify replacing a general
mixed-register multiply with two independently structured nonlinear maps plus
linear recombination.

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Exact current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Complete `pp_mul` traversal: T426844.55.
- Conservative replacement ceiling: T335738.86.
- Prior exact affine census: zero hits across widths 5 through 14.

## Exact path

Reuse the deterministic complete curve-support rows and adjacent prime widths
5 through 14 from `curve_support_product_invariants.py`. Build every feature as
an integer bit-vector over the entire enumerated support and use exact GF(2)
elimination. No random samples, fitting tolerance, nonce, or width schedule is
allowed.

For each width:

1. Prove every feature is recoverable from its own span.
2. Prove a positive synthetic separable quadratic is admitted.
3. Prove full-support three-variable AND is rejected by degree-two features.
4. Test all `n^2` mixed partial products.
5. Test all `n` modular output bits.

## Count and transfer gate

Report the exact number and normalized locations of admitted mixed partial
products at every width. A family transfers only if at least `n` normalized
relations persist across the largest three adjacent widths. A production
admission additionally requires an arbitrary-width proof, exact live-wire
mapping, and a complete reversible schedule below Q1100/T335738.86.

## Falsifier

Issue `HARD_NACK_SEPARABLE_QUADRATIC_SUPPORT` if the census finds only
constant-size, edge-only, or nonpersistent relations. Zero hits at every width
is a strict special case.

This verdict closes only degree-two expressions with no mixed-register feature
on their right-hand side. It does not close cubic curve relations, rational
rows, higher-degree support compactors, or explicit nonlinear reversible
constructions.

## Residual gate

No admitted relation earns circuit credit until an exact reversible residual
probe proves value, phase, and ancilla cleanup on the full support. The census
itself is information evidence only.

## Authority

Local Python research only. Provider, nonce-grind, fleet, queue, push,
public-note, promotion, and submission authority remain false.
