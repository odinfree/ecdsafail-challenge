# Rational Euclid-Tag Root-Carrier Gate

Status: approved for exact bounded-degree interpolation falsification on
2026-08-25.

## Question

For the exact smallest injective constant seed at the first classical point,
the online Euclid output is `(g,z)` and the desired word is `T`. Does curve
support make `T` a low-degree polynomial or rational function of `(g,z)`?

This is the strongest direct algebraic way for the Euclid tag itself to become
a cube-root carrier. It avoids separately computing a root and then selecting
one GLV branch.

## Polynomial gate

Let `M_d` be all bivariate monomials

```text
g^i*z^j,  i+j <= d.
```

For each exact support, increase `d` until `T` lies in the span of the evaluated
monomial columns. Record both the last rejected degree and the first admitted
degree, column counts, feature rank, and augmented rank.

If the first solution appears only when the monomial count reaches the number
of support rows, classify it as generic interpolation rather than a support
identity.

## Rational gate

A degree-`d` rational relation

```text
T = P_d(g,z)/Q_d(g,z)
```

implies a nonzero null vector of the homogeneous evaluation matrix

```text
[ M_d | -T*M_d ].
```

Record the last degree with full column rank and the first degree with a
nonzero nullspace. A null vector is only a necessary condition: its denominator
may vanish on support. The gate therefore claims a lower bound on relation
degree, never a decoder from nullity alone.

## Exact fields and decision

Use first-point supports at primes 31, 61, 127, 251, and 509. These widths keep
the full modular row reduction exact while spanning five adjacent sizes.

`HARD_NACK_RATIONAL_EUCLID_TAG_ROOT_CARRIER_INTERPOLATION_ONLY` if:

1. polynomial decoding first appears exactly at generic interpolation capacity;
2. rational relations have full column rank until twice the monomial count
   exceeds support size;
3. the first possible degrees and coefficient counts grow with field width and
   do not form a width-bounded family.

This closes total-degree bivariate field polynomials and rational functions for
the selected constant seed. It does not close Boolean circuits, higher-arity
representations, a different nonlinear seed, or rational functions exploiting
an independently computed branch/root bit.

The next grammar is `BOOLEAN_EUCLID_TAG_ROOT_CARRIER`: measure exact bitwise
decoder degree/density and look for a width-stable non-field representation.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
