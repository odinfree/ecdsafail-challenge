# One-word replay-coordinate falsifier

**Source binding:** commit `67524171baaf568dc3dc606f38515745f70804ff`,
tree `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`.

## Hypothesis

The live 512-bit replay pair is a walk-conditioned linear image of one
numerator.  Replace it with one 256-bit data word plus a bounded discriminator,
and update that word in place as each tape sign is consumed.  A successful
construction would remove at least 256 live qubits from both current Q1267
binders and would be large enough to reopen Q1000-class pricing.

## Cheapest falsifier

Before editing the Rust circuit, test the two requirements that such a local
coordinate must satisfy:

1. **local closure:** one nonzero linear coordinate must survive both sign
   branches of each replay cell and compose across an even/odd two-round pair;
2. **bounded discriminator:** the reachable replay-pair class conditioned by
   the tape must remain distinguishable with fewer than one field word.

The first requirement is checked algebraically and by exhaustive finite-field
enumeration.  For an even round the branch matrices are

```text
M_s = [[1, 0], [s/2, 1/2]],  s in {-1,+1};
```

the odd-round matrices are their coordinate swap.  A post-coordinate that is
closed for both branches must annihilate `M_+ - M_-`; hence an even cell can
only preserve the untouched `x` coordinate, while an odd cell can only preserve
the untouched `y` coordinate.  Those one-cell coordinates cannot compose
through a two-round pair without retaining the missing word.

The second requirement is tested on every legal denominator for moduli 29, 61,
and 127.  The exact reduced-width walk supplies only reachable tapes.  Replay
starts from `(x,y)=(0,1)`, and the receipt records the number of distinct
reachable coefficient pairs after every prefix.  At termination it also checks
that sign-normalising both pair members gives the field inverse.  Therefore the
terminal class count is exactly `p-1`, requiring a full-width discriminator.

## Gate

- `ADMIT` only if a nontrivial two-round local coordinate exists and the
  discriminator scales strictly below field width.
- `HARD_NACK` if local closure is absent and the reachable terminal classes
  saturate `p-1` at widths 5, 6, and 7.

This verdict is scoped to a sign-local linear one-word replay plus a sub-word
discriminator.  It does not claim a lower bound for an arbitrary nonlinear
in-place division permutation.  Reopening requires an explicit reversible
nonlinear transform with end-to-end Q/T pricing; relabeling the original
division as its own decoder is not progress.
