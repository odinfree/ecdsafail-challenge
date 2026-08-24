# Odd-Lift Prefix-Stream Verdict

Verdict: `HARD_NACK_ODD_LIFT_PREFIX_STREAM`

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Conservative complete-multiply replacement ceiling: T335738.86.
- Exact receipt: `54-odd-lift-prefix-stream-receipt.json`, embedded
  SHA-256
  `470e31c119ff554a3e6d25a515a312b07dfdfec5224aacc48b2715d05cd7eb99`.

## Construction tested

For `R=2^n`, replace each nonzero field element `T` by its odd signed
representative

```text
m(T) = T       when T is odd
       T-p     when T is even,
M(T) = m(T) mod R.
```

`M(T)` is odd, so `lambda -> w=M(T)*lambda mod R` is an exact permutation of
the `n`-bit word. The hoped-for cut was a second one-pass overwrite from `w`
to `y=T*lambda mod p`, folding the pseudo-Mersenne high word without retaining
that word.

All oddness, field-equivalence, complete `R`-word bijection, inverse recovery,
and modular-target controls passed with zero failures.

## Exact collision result

The gate enumerated 5,538,816 complete nonzero-field states over primes of
width 5 through 11 bits. At every width:

- low-to-high correction is ambiguous at every bit except the final MSB;
- high-to-low correction is ambiguous at every bit except the final LSB.

The endpoint exception is structural, not a survivor: at that endpoint the
allowed prefix already contains the complete `w` word. Every interior bit has
an independently replayable pair with the same `T`, the same permitted
processed state, and opposite required output bit. Thus the reduction
correction necessarily consults information on the other side of the moving
frontier.

The separate curve diagnostic enumerated 4,026 valid support rows (4,021 with
nonzero `T`) with zero product failures. It also contains collisions in both
directions at every width from 6 through 11. The full-domain result is the
decision evidence because the affine-shell transducer is required to be a
total permutation; the curve result only confirms that the obstruction is not
an off-curve artifact.

## Scope

This closes precisely a strict one-pass low-to-high or high-to-low correction
after odd multiplication modulo `2^n`. It does not establish a lower bound on
arbitrary nonlocal two-register circuits, and it does not show that a third
field word is universally necessary. A circuit that interrogates both sides
of `w`, revisits bits, or carries a rigorously sublinear summary remains open,
but it must price those nonlocal controls and clean them exactly.

The odd-lift factorization is therefore not admitted into production Rust.
The next grammar is `NONLOCAL_DIRECT_UNIT_ACTION`: search for a bounded-state,
multi-pass correction whose state has an explicit sublinear formula and whose
reverse recomputes every decision.

## Authority

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
