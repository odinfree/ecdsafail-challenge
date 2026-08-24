# Coupled Transposed Seed Verdict

Identity verdict: `ADMIT_IDEAL_COUPLED_SEED_IDENTITY_ONLY`

Generator verdict: `HARD_NACK_BOUNDED_DEGREE_COUPLED_SEED`

## Exact identity

Fixing the online Euclid matrix orientation gives

```text
B_T = [[-r_T,T],[k_T,-p]],  k_T*T-r_T*p=1.
```

For a coupled seed `(lambda,s(T)*lambda+h(T))`, collision-free fixed-`T`
families must have one common direction `c`, forcing

```text
s(T) = T*r_T+c*T^2 mod p.
```

At `c=0`, choosing `h(T)=T^2` makes the output exactly
`(T,T*lambda mod p)`. The oracle exhausted 83,342 pairs over fields 31, 61,
127, and 251 with zero orientation, output, or interpolation failures.

## Closed generator

The unique degree-below-`p` polynomial for `T*r_T`, totalized to zero at
`T=0`, has degree exactly `p-1` at all four widths: 30, 60, 126, and 250. Its
nonzero coefficient counts are 15, 32, 65, and 127. Adding arbitrary
`c*T^2` changes only the quadratic coefficient; the full degree and every
higher coefficient remain.

This closes literal bounded-degree field-polynomial generation of the coupled
seed. It is not a circuit lower bound for every way to generate the Euclidean
cofactor.

## Next obligation

The only live version of this route is an `ONLINE_COFACTOR_PRODUCT_RECURRENCE`
that creates the exact `r_T*lambda` cancellation while Euclid generates
`r_T`. It must publish a reversible state recurrence, fit Q1100, return every
auxiliary word to zero, and avoid both a linear quotient transcript and a
separate variable multiplication. Supplying the ideal seed as an oracle is not
implementation progress.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
