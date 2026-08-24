# Rational Euclid-Tag Root-Carrier Verdict

Verdict:
`HARD_NACK_RATIONAL_EUCLID_TAG_ROOT_CARRIER_INTERPOLATION_ONLY`

## Polynomial decoder

The exact gate evaluated every total-degree monomial in `(g,z)` on the
selected constant seed at the first curve point. Across fields 31 through 509,
`T` first enters the polynomial feature span at degrees 5, 10, 15, 21, and 31.

In every field this is precisely the first degree at which the monomial count
reaches the number of support rows. The immediately preceding augmented
system has rank one higher than the feature system. These are generic
interpolants, not a width-stable curve-support identity.

## Rational decoder

A degree-`d` rational decoder requires a nonzero vector in

```text
[M_d(g,z) | -T*M_d(g,z)].
```

The matrix has full column rank through degrees 2, 6, 9, 14, and 21. Its first
nullspace appears only at degrees 3, 7, 10, 15, and 22, exactly when twice the
monomial count exceeds the number of support rows. Thus the first possible
relations are explained completely by dimensional interpolation.

Nullity alone does not certify a decoder: the denominator may vanish on
support. This gate deliberately does not promote any of those null vectors.

## Scope and next obligation

This closes total-degree bivariate field polynomials and rational functions for
the selected injective constant seed. It does not close a bitwise Boolean
decoder, a different nonlinear seed, or a representation carrying an
independently computed root selector.

The next grammar is `BOOLEAN_EUCLID_TAG_ROOT_CARRIER`: exact output-bit ANF
degree and density, tested across widths, to determine whether field-dense
interpolation hides a width-stable Boolean circuit.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
