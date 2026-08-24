# GLV Trit-Tag Decoder Verdict

Identity verdict: `ADMIT_GLV_TRIT_INTERPRETATION_ONLY`

Decoder verdict: `HARD_NACK_GLV_TRIT_LINEAR_TAG_DECODER`

## Exact trit interpretation

For every tested `p congruent 1 mod 3`, the nontrivial cube root of unity
`beta` partitions each nonzero output-Y fiber into exactly

```text
{X, beta*X, beta^2*X}.
```

All orbit, curve-membership, `z=Y+b`, and `T=a-X` checks passed at widths 5,
6, 7, 10, and 12. The online Euclid garbage word is therefore a tag selecting
one of at most three X roots; it is not itself evidence that a root can be
created cheaply.

## Every linear seed plus affine postdecode

For `h=A*lambda+B*T+C`, any affine decoder would put T in the span of

```text
-r*lambda, k*lambda, k*T, k, z, 1.
```

The gate relaxed all products of seed and decoder coefficients to independent
unknowns. At every width 5 through 12 the feature rank is five and adjoining T
raises it to six. Even the relaxed system is inconsistent, closing every
linear seed with a global affine postdecode.

## Selected seed plus linear-fractional postdecode

For each exact smallest constant seed, the homogeneous Möbius-decoder matrix

```text
(g,z,1,-T*g,-T*z,-T)
```

has rank six and nullity zero at every tested width. No degree-one rational
postdecode exists for those injective support maps.

## Next obligation

The remaining algebraic escape is a `RATIONAL_EUCLID_TAG_ROOT_CARRIER`: a
bounded-degree rational map that turns `(g,z)` into one actual cube root before
the GLV trit selects the required branch. It must persist across widths and
come with reversible cost and cleanup; width-specific interpolation is not a
construction.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
