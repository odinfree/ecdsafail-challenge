# Separable-Quadratic Curve-Support Verdict

Verdict: `HARD_NACK_SEPARABLE_QUADRATIC_SUPPORT`

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Complete `pp_mul` traversal: T426844.55.
- Conservative replacement ceiling: T335738.86.
- Exact receipt: `48-separable-quadratic-support-receipt.json`, embedded
  SHA-256
  `c869d080a278d9e6b2353767ace02ceca53a5bd0b8f609f016f084506d7c51b4`.

## Result

The exact census enumerated 32,750 curve-supported states over adjacent prime
widths 5 through 14. At each width it tested all mixed partial products and all
modular product bits against the complete GF(2) span of affine features plus
every quadratic internal to `T` and every quadratic internal to `lambda`.

Width 5 admitted three mixed partial products and one output bit. Widths 6
through 14 admitted exactly zero mixed partial products and zero output bits.
Consequently no normalized relation survives even two adjacent widths, and
the material-family gate is false.

All self-span and synthetic separable-quadratic positive controls passed. A
full Boolean-support degree-three control was rejected at every width. The
shared-denominator curve identity held on every support row.

The isolated width-5 expressions are finite-support interpolation artifacts;
they are retained in the receipt and receive no transfer credit.

## Scope

This closes expressions of degree at most two whose right-hand side contains
no mixed `T/lambda` feature. It does not close cubic curve relations, rational
rows, higher-degree support compactors, or explicit nonlinear reversible
constructions.

The next grammar is `CUBIC_OR_RATIONAL_SUPPORT_COMPACTOR`. It must exploit the
actual field identity structurally; increasing the Boolean feature degree
without a circuit-cost hypothesis would saturate the finite support and cause
autoresearcher rot.

## Authority

Provider, nonce-grind, push, public-note, promotion, and submission authority
remain false.
