# Separable Field-Polynomial Verdict

Verdict: `HARD_NACK_SEPARABLE_FIELD_POLYNOMIAL`

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Complete `pp_mul` traversal: T426844.55.
- Conservative replacement ceiling: T335738.86.
- Exact receipt: `50-separable-field-polynomial-receipt.json`, embedded
  SHA-256
  `8acf0663bb6b78f3e1d26d1ef0a581c831b93870daf3b4be60c8da24eb899246`.

## Result

The exact support graph rules out the field identity

```text
T*lambda = f(T) + g(lambda) mod p
```

at p=31 and p=251 for functions of any polynomial degree. Each support contains
an explicit six-edge bipartite cycle whose product labels have a nonzero
alternating residual: 24 mod 31 and 151 mod 251. Those cycles are compact,
independently rechecked certificates against even unrestricted additive
separability on the finite support.

The neighboring p=61 and p=127 supports are forests, so arbitrary vertex
potentials can fit the edges. Exact GF(p) elimination nevertheless requires
minimum symmetric degrees 29 and 62, with 56 and 123 nonzero coefficients.
Those degrees are approximately p/2: lookup interpolation exponential in the
bit width, not a scalable arithmetic identity. Every returned coefficient
solution was re-evaluated on the complete support with zero failures.

The synthetic `T^2 + lambda^3` control was admitted at degree three on all four
fields, separating a functioning solver from a blanket negative result.

## Scope

This closes additive separation into independent univariate field polynomials.
It does not close mixed rational functions, an algebraic square-root extension,
or an explicit in-place multiplication action.

The next grammar is `ALGEBRAIC_ROOT_OR_DIRECT_UNIT_ACTION`. A curve compactor
must now pay for the algebraic root choice explicitly; another finite-support
feature expansion is banned as autoresearcher rot.

## Authority

Provider, nonce-grind, push, public-note, promotion, and submission authority
remain false.
