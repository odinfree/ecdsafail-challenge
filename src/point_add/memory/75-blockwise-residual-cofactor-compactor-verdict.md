# Blockwise Residual Cofactor Compactor Verdict

Identity verdict: `ADMIT_PREFIX_CROSS_DETERMINANT_PRODUCT_IDENTITY_ONLY`

Compiler verdict:
`HARD_NACK_BLOCKWISE_RESIDUAL_COFACTOR_COMPACTOR_NATURAL_CODECS`

## Admitted invariant

For any common Euclid prefix `B`,

```text
(p,T)B = (u,v)
(lambda,h(T))B = (x,y)
u*y-v*x = epsilon*(p*h(T)-T*lambda).
```

Thus `T*lambda mod p` is available from two rectangular products at every
prefix cutoff; the full half-GCD matrix does not have to be retained or applied.
The oracle checked 640,624 legal states over primes 31, 61, 127, and 251 with
zero row or determinant failures.

## Stored-prefix closure

The most optimistic stored-prefix layout keeps the two-word seed row, the exact
residual pair, one output word for `T`, and a boundary-free raw quotient payload.
Across every material cutoff `w=1..255` in the deterministic 10,000-denominator
secp256k1 sample, the minimum worst-case floor is Q1124. That is 24 qubits over
Q1100 before boundaries, parser, quotient arithmetic, carries, determinant, or
cleanup. A decodable Elias-gamma stream bottoms out still higher at Q1282.

## Code-free closure

Applying each adaptive quotient immediately to both rows avoids history only if
the four-word checkpoint map is injective. Exact legal-input enumerations show
collisions at every cutoff deeper than one bit of shrink. At the last colliding
cut (`w=n-2`) all four fields already have six collisions; only the zero-step or
at-most-one-step cuts remain injective and neither is a material compactor.

## Minimum-rank closure

Replacing the prefix by the multiplier's rank inside its residual fiber uses the
minimum natural sidecar. Its zero-extended decoder parity is nevertheless dense
and high degree at every tested width 5 through 12, reaching degree 19/19 and
193,812 of 524,288 ANF monomials at width 12.

This closes literal lookup/ANF/kickmix rank decoding, not every algorithmic
continued-fraction codec. Earlier half-GCD endpoint/DP/rank work remains the
anti-duplication boundary.

## Reopen condition

The only live version is a `CROSS_DETERMINANT_CONTINUANT_RANK_CODEC` with an
explicit phase-clean arithmetic decoder. It must fit Q1100 including carries
and erase its sidecar below the T335738.86 replacement ceiling. An oracle rank,
generic table, or uncharged parser does not qualify.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
