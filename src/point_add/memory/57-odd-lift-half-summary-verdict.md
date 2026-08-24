# Odd-Lift Half-Word Summary Verdict

Verdict: `HARD_NACK_ODD_LIFT_HALF_SUMMARY`

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Exact receipt: `56-odd-lift-half-summary-receipt.json`, embedded
  SHA-256
  `9a19205c42a3b69ed610d5b69914345384d24be7e935b673d12af3a96a134a7c`.

## Exact reduced-width result

The census enumerated all 5,538,816 nonzero-field states at widths 5 through
11. At every balanced cut `k=floor(n/2)`, both directions attain the maximum
possible diversity `2^k`:

```text
width     5   6   7   8   9  10  11
cut       2   3   3   4   4   5   5
D_low     4   8   8  16  16  32  32
D_high    4   8   8  16  16  32  32
```

Every maximum has a stored, independently replayable family of inputs with
one visible half fixed and all possible opposite output halves. The identity
control `y=w` requires zero summary bits.

## Exact secp256k1 certificate

The production result is not extrapolated from the toy census. Put

```text
B = 2^128
c = 2^32+977
p = B^2-c
T = B
M = B+c.
```

For the family `lambda=B*h`, all `B` inputs are legal, `w mod B=0`, and
`y mod B=c*h mod B`. Since `c` is odd, this visits every 128-bit low word.
Any high-half prepass that destroys the high half before emitting the low half
therefore needs at least 128 retained bits.

For the reverse direction, choose for each low word `l` the unique
`h=-c^-1*(l+floor(c*l/B)) mod B`. This fixes `floor(w/B)=0` and leaves at least

```text
B-c = 340282366920938463463374607427473243183
```

legal field inputs. A final high word has at most
`c+1=4294968274` compatible `l` values, so the high-output diversity is at
least

```text
79228144473352741572166176013,
```

which requires 96 retained bits. All modulus, range, oddness, single-reduction,
and integer-bound checks pass exactly.

## Scope and next grammar

The proposed two-pass half-word fold did not turn the lost high product into a
bounded or sublinear digest. In either direction its retained state is a
production-width linear owner, violating the transducer fingerprint before
gate pricing.

This is a communication lower bound for a half-word prepass followed by
destructive emission of the other half. It does not reject a circuit that
keeps both halves live, revisits them, or interleaves nonlocal updates without
crossing this cut. The next grammar is `NONLOCAL_INTERLEAVED_UNIT_ACTION`; it
must expose a concrete reversible cell schedule rather than rename a linear
summary.

## Authority

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
