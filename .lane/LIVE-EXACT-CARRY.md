# Live 087cafa exact-carry experiments

Exact source anchor: `087cafaef46a4e339644a6191ff2df2e7031cb80`

Official receipt: Q1275, average T918972.304, rounded T918972,
score 1171689300, 12,953,930 emitted ops, full evaluator `0/0/0`, operation
SHA-256 `d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124`.

No experiment in this lane authorizes a nonce scan, provider action, fleet
change, or submission.  The inherited nonce may be evaluated once only after
the structural and primitive gates pass.

## L-001: same-Q exact final-carry host

Hypothesis: the final carry of each divide replay walk has one semantic
consumer, the top output bit.  Computing that majority directly into the
output deletes a measured carry erase without changing the integer width,
logical map, or multiply/square schedules.  The live global peak may remain
Q1275; fewer emitted operations and no replacement Toffoli create a plausible
strict same-Q T beat.

Smallest falsifier, registered before source change:

1. Exhaust all 32 `(source, target, carry, source_top, target_top)` states.
   Kill on any mismatch in restored source, lower sum, or top sum/carry.
2. Run the production 64-lane point-add self-check.  Kill on any class, phase,
   or ancilla mismatch.
3. Trace all phases within two qubits of the maximum.  Kill if Q rises above
   1275 or if the transformation has no executed-T headroom.
4. Only if 1-3 pass, run the unchanged full evaluator once at inherited nonce
   `251000962439`.  Promotion threshold is Q at most 1275, `0/0/0`, and rounded
   T at most 918971.  Any failure closes this inherited-nonce route; no scan.

Measured result: the 32-state miter and production 64-lane self-check passed
with zero value, phase, or ancilla residue.  The live phase profile stayed at
Q1275 and showed lower executed T, but the one authorized full evaluation at
the inherited nonce failed `13/17/0`.  L-001 is therefore an exact structural
T cut with no clean inherited corpus, not a candidate.  The nonce route is
closed without search.

## L-002: Q1274 binding-only carry composition

This experiment remained closed until the live peak trace was frozen.
Its potential pieces are the exact L-001 divide cut and a MAJ/UMA source host
applied only when an owned chunk ladder would cross Q1274.

Pre-registered kill conditions:

1. Every changed carry cell must pass its complete Boolean miter and the
   production value/phase/ancilla self-check independently.
2. A source host may run only when the allocation it replaces would make
   `active_qubits + owned > 1274`; applying it to non-binding cells is rejected
   as avoidable T cost.
3. All Q1275 owners must fall and `pp_mul_replay` must remain at most Q1274.
4. Before any full evaluation, the deterministic profile T must remain below
   the strict Q1274 ceiling implied by the live score: rounded T at most
   919693.  Otherwise the width cut cannot beat the live frontier even if
   clean.
5. If and only if 1-4 pass, run one unchanged 9,024-shot evaluation at the
   inherited nonce.  It must be Q1274, rounded T at most 919693, and `0/0/0`.
   Failure closes the route without nonce search.

The first live trace with L-001 applied shows four Q1275 phase owners:
`pp_div_replay`, `square_product_register`, `pp_mul_replay`, and
`pp_mul_walkback`.  The 12,952,064 semantic operations become 12,952,160 after
the identity tail; seed-zero diagnostic T is 918845.81 and its 64 lanes are
`0/0/0`.  Exact owner censuses, not this aggregate row, determine whether one
binding-only source host covers each replay phase.

The owner censuses show that all four Q1275 allocations use the same generic
chunk adder: divide has 127 owned carries plus two boundaries; multiply replay
and walkback each have 62 owned carries plus two boundaries; square has 244
owned carries plus one boundary.  Therefore the smallest composition does not
change `SQUARE_LADDER`: it applies one exact source host only when
`active_qubits + owned > 1274`, in the four named phases.  Its smallest miter
is all eight `(source, acc, incoming_carry)` states through MAJ then UMA; source
and incoming carry must be restored, the hosted intermediate must equal the
majority carry, and the accumulator must equal the exact sum bit.

Measured reveal after the binding-only source host: divide replay, square, and
multiply replay each fall to Q1274, but multiply walkback remains Q1275 at an
unsplit 94-bit walk with 93 clean sigma carries.  This is the same final-carry
single-consumer identity already exhausted in L-001.  Extending that exact
output host to `pp_mul_walkback` under a separate gate is killed by any change
to the 32-state miter, production self-check, or Q1274 phase proof.

PIP refinement before the final profile: walk-output hosting is also limited
to `active_qubits + stock_carries > 1274`.  The broad L-001 gate supplied its
closed inherited-nonce result; L-002 does not alter non-binding walk cells.

## Frozen L-002 result

Both focused algebra gates pass: the MAJ/UMA cell is 8/8 exact and the walk
output host is 32/32 exact.  The production 64-lane point-add self-check with
all three gates reports Q1274, exact ABI outputs, zero phase, and all non-ABI
qubits clean.  The final binding-only configuration is:

```text
SUB4_PP_DIV_WALK_TOP_CARRY_HOST=1
SUB4_PP_MUL_WALK_TOP_CARRY_HOST=1
SUB4_BINDING_SOURCE_CARRY_Q1274=1
```

The final phase profile proves every former co-binder at Q1274:

| phase | peak Q |
|---|---:|
| `pp_div_replay` | 1274 |
| `square_product_register` | 1274 |
| `pp_mul_replay` | 1274 |
| `pp_mul_walkback` | 1274 |

It emits 12,948,706 semantic ops and 12,948,802 ops after the identity tail.
The operation SHA-256 is
`101dde7c97b1b42fd63b8d51514de7e7d025adeb7f2d058ae179b01854d73e46`.
The tested `pingpong_div.rs` SHA-256 is
`b7535fcc55650f436c8f2ff4a39d60266a54cb1d766d1836272d7991c8ed9ce7`.
Seed-zero diagnostic T is 919919.48, rounded 919919, with `0/0/0` across its
64 lanes.  Its projected score is 1171976806, which is 287506 worse than the
live score.

The generic source host fires 963 times and adds exactly one executed Toffoli
per activation.  Q1274 permits only 721 T above the accepted rounded T, so the
exact architecture is structurally 242 T over budget even before a trusted
corpus run.  L-002 fails the pre-registered score gate; no full 9,024-shot
evaluation was run.

The next exact binder is therefore not another peak owner.  At least 242 of
the mandatory source-host activations need a clean live carrier with no UMA
Toffoli, or an orthogonal exact T cut must remove the equivalent cost.  The
known PEAK1274/SQUARE244/R2-620 schedule geometry is narrower in T, but changes
approximate boundary exposure and is outside this no-tolerance lane.
