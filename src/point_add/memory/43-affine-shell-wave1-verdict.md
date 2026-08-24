# Affine-shell wave 1 verdict

Verdict: `HARD_NACK_LOW_DEGREE_SHEAR`.

The exceptional-safe shell is a full permutation and matches curve addition
on every exhaustively checked valid input at p=31, p=127, and p=251. Its
nonzero-fiber Jacobian determinant is `-T`, which assumes every nonzero field
value. Any scalable symbolic composition of translations, additive triangular
shears, swaps, constant unit scalings, and zero-only corrections has one
constant nonzero determinant on that region. The grammar therefore cannot
realize the target. This does not claim to close field-specific lookup
permutations, which the campaign excludes as non-scalable.

This does not close the direct two-register affine-shell family. It proves the
next construction must contain a genuinely variable-coefficient reversible
operation. The next grammar is `REGISTER_SHARED_EUCLID`: data-dependent rows
whose branch is recoverable from bounded length/location metadata instead of a
linear history tape.

No production Rust, provider, nonce, push, public, or submission action is
authorized by this receipt.
