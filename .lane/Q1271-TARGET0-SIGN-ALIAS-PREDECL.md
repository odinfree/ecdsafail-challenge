# Q1271 target0/sign alias predeclaration

## Frozen frontier and parent

- Live frontier: `1,163,831,339`, Q1273 / rounded T914243 at source
  `4eb93cb`.
- Strict Q1271 ceiling: rounded `T <= 915681`.
- Parent `e4f602e` proves the selector + doubled-output + full multiply-replay
  split is exact on component gates and fast enough, but Q rises to 1272
  because the wider main add allocates before the post-add loan begins.

## Single lifecycle identity

Immediately before the fused doubling cell's main add, rotation has made
`target[0]=0`, and conditional complementation has made
`target[0]=sign`.  The two wires are redundant during the add.

This lane tests one exact pre-add alias:

1. clear the duplicate `target[0]` with `CX(sign,target[0])` and lend its slot;
2. use the `sign` wire as the add's accumulator bit zero;
3. after the add, reacquire `target[0]` and copy the sum bit from `sign`;
4. restore the original sign with `CX(source[0],sign)`, since bit-zero addition
   has no incoming carry and the temporary sign wire equals
   `old_sign XOR source[0]`.

Default-off control: `SUB4_PP_ALIAS_TARGET0_SIGN=1`.

Frozen composition:

```text
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_EVICT_DOUBLED_OUT=1
SUB4_PP_ALIAS_TARGET0_SIGN=1
SUB4_PP_PEAK=1271
SUB4_PP_MUL_REPLAY_PEAK=1272
SUB4_SQUARE_LADDER=241
```

No arithmetic window, width schedule, round count, nonce, evaluator, or phase
check may change.

## Gates

1. Alias absent: parent operation stream stays byte-identical.
2. A standalone protected-versus-aliased doubling-cell miter must cover every
   sign/source-low/doubled-out/add-carry arm and match values, source, sign,
   relative phase, and clean ancillas on 64 lanes.  Toffoli count must be
   unchanged.
3. Existing selector lifecycle, full affine 64-lane, and square component
   checks must pass.
4. Profile and allocation trace must prove Q1271 and rounded diagnostic
   `T <= 915681`.
5. Only after gates 1–4, run one unchanged 9,024-shot inherited-nonce result.
   Dirty channels are a predictor handoff, not validity or hunt authority.

## Bounds

No provider spend, range, fleet, hunt, submission, or public note.  Commit and
push source and compact evidence; exclude generated binaries, `ops.bin`, logs,
and result artifacts.
