# Online Cofactor Product Recurrence Verdict

Verdict: `HARD_NACK_ONLINE_COFACTOR_NATURAL_CLEANUPS`

## Coherent dual-row cleanup

Retaining the Euclid value row, the product-coefficient row, and the
`T^2` cancellation row requires six live field words. At 256 bits this is a
Q1536 floor: 436 qubits beyond the component cap Q1100 and 270 beyond the
protected whole-circuit peak Q1266. Quotient extraction, carries, orientation,
zero-fiber logic, and final cleanup are not yet charged.

This closes the literal coherent dual-row realization.

## Measured-cofactor cleanup

If the first product-row word is measured, its repair function in the surviving
frame `(T,z=T*lambda)` is

```text
r_T*z*T^-1 mod p.
```

The exact oracle exhausted 83,342 legal `(T,lambda)` pairs with zero relation
failures. For an alternating-bit output parity, with unsupported bit patterns
totalized to zero, adjacent-width GF(2) ANFs had `(degree,density/table)`:

```text
p=31:  (7, 254/1024)
p=61:  (11, 1896/4096)
p=127: (14, 7394/16384)
p=251: (15, 31966/65536)
```

This closes literal zero-extended ANF/kickmix phase correction and reconnects
the route to the existing generic in-place multiplication cleanup failure. It
is deliberately not stated as a universal reversible-circuit lower bound or as
a minimum-support extension result.

## Next obligation

The next grammar is `BLOCKWISE_RESIDUAL_COFACTOR_COMPACTOR`: stop the online
Euclid walk before collapse and test whether a bounded residual pair carries
enough multiplier information to transfer the cofactor into the required
output without a linear tail transcript or the same dense division phase.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
