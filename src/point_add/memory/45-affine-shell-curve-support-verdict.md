# Affine-Shell Curve-Support Verdict

Verdict: `HOLD_CURVE_SUPPORT_CLEANUP_OPEN`

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Complete `pp_mul` traversal: T426844.55.
- Conservative replacement ceiling: T335738.86.
- Exact receipt: `44-affine-shell-curve-support-receipt.json`.

## Admitted information result

For every enumerated curve-supported state at p=31, 127, and 251,

```text
d*T = 2*b*lambda - 3*a^2
```

holds exactly. Lambda is therefore recoverable from `(d,T)` because the
classical point has nonzero `b`. The exact support census also finds at most
two legal lambda values per `T`, so one conditional bit is sufficient as an
information projection at these reduced widths.

This is `ADMIT_INFORMATION_ONLY`, not a circuit admission. The reformulated
output

```text
Y = (d*T^2 + 3*a^2*T)/(2*b) - b
```

still contains the variable product `d*T^2`, has a variable Jacobian, and has
no demonstrated reversible cleanup schedule within the two-word budget.

## Closed literal route

For secp256k1, literal point decompression by binary exponentiation to
`(p+1)/4` requires 253 squarings and 246 selected multiplies. Pricing only the
253 squarings at the current square cost already gives T13883853.17, or
41.353 times the entire replacement ceiling. This favorable relaxation omits
all selected multiplies, branch extraction, routing, and cleanup.

Verdict for that architecture:
`HARD_NACK_CURRENT_SQUARE_FERMAT_DECOMPRESS`.

This does not claim a universal square-root lower bound. It closes only literal
Fermat decompression using the current square implementation.

## Remaining obligation

The curve-support direction remains open only for a direct in-place compactor /
decompactor, a rational row, or another nonlinear construction that realizes
the complete product and cleanup below Q1100 and T335738.86. Affine support
relations are tested separately.

## Authority

Provider, nonce-grind, push, public-note, promotion, and submission authority
remain false.
