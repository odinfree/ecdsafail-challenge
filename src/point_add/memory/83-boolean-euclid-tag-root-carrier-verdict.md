# Boolean Euclid-Tag Root-Carrier Verdict

Verdict:
`HARD_NACK_BOOLEAN_EUCLID_TAG_ROOT_CARRIER_NATURAL_ANF`

## Completion-independent degree

For each bit of `T`, the gate solved exact GF(2) span systems made from every
square-free monomial in the binary bits of `(g,z)`. All output bits first
become representable at degree 2 for fields 31 and 61, then degree 3 for fields
127, 251, and 509.

Every bit hits the same boundary: precisely the first degree where the feature
matrix reaches full support-row rank. At the preceding degree, adjoining each
target raises rank by one. The admitted functions are therefore explained by
unconstrained support interpolation, not a privileged output-bit identity.

## Canonical zero extension

Extending each output bit by zero away from support gives a unique full truth
table. Its exact Möbius transform is both high degree and dense:

```text
p=31:  degree 9,       110..166 coefficients per bit of 1,024
p=61:  degree 11,    1,236..1,904 coefficients per bit of 4,096
p=127: degree 13,    4,112..5,148 coefficients per bit of 16,384
p=251: degree 15..16,19,104..21,416 coefficients per bit of 65,536
p=509: degree 17..18,62,348..70,928 coefficients per bit of 262,144
```

No output bit yields a stable linear family or a sparse natural ANF template.

## Scope and next obligation

This does not prove that every factored Boolean circuit is expensive. ANF
density can hide factoring, and another off-support reversible extension may
be far better than zero extension.

The next grammar is `SUPPORT_TRACE_ROOT_SELECTOR`: retain one bounded statistic
from the Euclidean quotient trace and test whether it resolves the GLV branch
before `(g,z)` loses that structure. This changes the representation instead
of fitting another decoder to the same collapsed outputs.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
