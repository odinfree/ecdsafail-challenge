# Live 4eb93cb third-binder re-descent predeclaration

Status: `PREDECLARED / NO SEMANTIC EDIT / NO CANDIDATE RESULT`.

## Frontier and exact base

The live benchmark was reopened immediately before this lane. The promoted
source is `4eb93cb33bbf6a93229fe166b8d511c5e52ee253`, tree
`bb19b4018e418c19b4ac13a16c88a31a9d820299`, at Q1273, rounded T914243,
score `1,163,831,339`.

This lane starts from that exact source. Its `pingpong_div.rs` and
`point_add/mod.rs` SHA-256 values are respectively
`a247d6c7f31fd382b3041e4cb2f21d13d7870551fe68344e22615a02e11c0d20`
and `da681f674c2bd0be2c507eafcc7785e045530d920fa343a52593aecf65619ba9`.

Strict rounded-Toffoli ceilings against the frozen live score are:

- Q1272: T at most 914961;
- Q1271: T at most 915681;
- Q1270: T at most 916402.

## One bounded architectural family

The promoted public evidence says lowering `SUB4_PP_PEAK` and the square
ladder together to 1270/240 remains Q1273 because a third allocation binds.
This lane will identify that binder from source-exact peak/liveset evidence,
then test one minimal default-off lifecycle or rematerialization change that
removes it. The preferred target is Q1271 or lower; Q1272 is acceptable only
if it is structurally distinct from fused-fold selector eviction.

The lane may use the disabled sparse `WIDTH_REPAIR` table as archaeology or
reverse-sell individual entries only when a measured entry releases the third
binder or buys enough Toffoli to compose with the single structural change.
It may not revive the whole repair schedule, change the nonce, import a second
unrelated architecture, or hide a width increase behind a different baseline.

## Evidence ladder

1. Reproduce the promoted control and the 1270/240 probe from a forced clean
   release build; record the exact peak site and complete simultaneous live
   set for every Q1273 binder.
2. Name the one changed invariant before editing source, including why every
   freed/reused wire is proven zero or exactly reconstructible.
3. Add a focused exact falsifier covering values, inverse, phase, and ancilla
   cleanup before accepting an allocation result.
4. Measure exact operation count, artifact SHA-256, Q, exact average T,
   rounded T, and score. Generated binaries, `ops.bin`, profiles, and logs stay
   outside Git.
5. Run the unchanged full 9,024-shot evaluator only after the Q/T gate passes.

Decision rules:

- `KILL` if the claimed binder is wrong, a wire is not proven clean, the
  focused falsifier fails, or Q/T misses the applicable strict ceiling;
- `SCORE_GO / VALIDATION_DIRTY` if Q/T strictly beats but any full channel is
  nonzero; hand the exact source and operation identity to a separate screen
  lane;
- only unchanged classical/phase/ancilla `0/0/0` is submission-eligible.

No provider compute, nonce range, fleet action, submission, public note, or
external message is authorized in this lane. Commit and push durable source
and evidence checkpoints; do not commit generated artifacts.

Worker: Claude Fable 5, high effort, bounded to USD 25 for this session.
