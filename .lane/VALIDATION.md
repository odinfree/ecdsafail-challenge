# g1000 nonce 135608492183 independent shipping validation

Validated: 2026-08-23T02:47:08Z

Status: `READY_CLEAN_NO_SUBMIT`

## Bound source

- Independent worktree:
  `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/validate-g1000-135608492183-x005`
- Branch: `validation/g1000-135608492183-x005`
- Exact parent: `7ca0559911b8cd423c4acc74fe152f332fce0c63`
- Candidate geometry: divide rounds 698, multiply rounds 696, exact
  `greedy_m1000` width table, tail nonce `135608492183`.
- Source width-table CSV SHA-256:
  `dfa4611b3fb5632c7b80b3dcc60f4b7e1ec8bf63cd07c93a9e535ad27266af56`.

The greedy table is baked as source data. The original `7ca0559` table remains
in place and is selected with `SUB4_PP_G1000_DISABLE=1`; multiply depth remains
overridable through `SUB4_PP_ROUNDS_MUL`; the nonce remains overridable through
`SUB4_PINGPONG_TAIL_NONCE`.

## Reconstruction gates

The canonical fleet g1000 artifact was decoded to confirm that its inherited
tail nonce is `48000070891`. Building this source with that nonce reproduced
the frozen artifact byte-for-byte:

```text
emitted operations  12912890
MD5                 f5c22035d9cc60e429d19e29ffeeda28
SHA-256             f8770944b57e1a147ec42fb598eeaf57fa75bf84ec47bb8c048abfa512c2d0a7
byte comparison     exact
```

The full source opt-out was also exercised with the original width table,
multiply rounds 700, and nonce `950027083`. It reproduced the exact `7ca0559`
stream:

```text
emitted operations  13001937
MD5                 2a3d088e0fa743bed3bd4f9cd7fd5a5e
SHA-256             c0e1dc5dcffe957d1aa57e7f4cece0866df6d52d9c691d5aa1614fa031efe25f
```

These two receipts bind the source implementation before using the hunted
nonce.

## Candidate artifact

The default baked candidate build produced:

```text
nonce                135608492183
emitted operations   12912890
qubits                1278
MD5                   599a8c5212e6b17363c2c394c9ad087d
SHA-256               5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8
```

An independent tail patch of the frozen SHA `f8770944...` artifact to nonce
`135608492183` was byte-identical to the from-source candidate above.

## Unchanged trusted evaluator

No evaluator, circuit loader, simulator, or library source was changed. The
checked evaluator provenance is:

```text
src/bin/eval_circuit.rs SHA-256  b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b
eval_circuit binary SHA-256      beda29fdb4c43d8143d7e9c3850ce4196fd7a467f089d04eb0d3c6955d026ac9
eval log SHA-256                 7a6bc805effff733bd44bc0f29d02f79825535091a98957bc98c9fcf53d75818
```

The unchanged full 9,024-shot evaluation returned exit zero:

```text
tested shots             9024
classical mismatches     0
phase-garbage batches    0
ancilla-garbage batches  0
average executed T       915947.392
average Clifford         10719804.752
total executed T         8265509263
emitted operations       12912890
qubits                   1278
```

Rounded T is 915947, so the benchmark score is
`1278 * 915947 = 1170580266`.

The live benchmark was refreshed read-only immediately after validation:
source `087cafa`, score `1171689300`. This candidate is a strict beat by
`1109034`. No submission, provider action, scan, or fleet mutation was made
from this lane.

## Source and binary hashes

```text
src/point_add/pingpong_div.rs             c89ccb06cddaaccb6e9755302bca96d9e4a88ec1eff7dc51d243db67aa2d174f
src/point_add/mod.rs                      163fd35fdd6f1ee14384bed40263446cf5c8fcd7a1b3ffb158ed2f9818720692
src/point_add/greedy_m1000_width_schedule.rs
                                           46945a13b61a48e791a422e16681491fd791f5faf1f811802c44565ae9bf7943
build_circuit binary                       9d6a4b6156f0da98c5214550d492d09f8ad940df3c5507bfef569f2ef7610ae6
```

Decision: the artifact is independently reconstructed and clean, but remains
held for the root campaign lane to decide submission timing and note content.
