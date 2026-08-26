# N1 branch-B K2 + F21 input-aware constprop stack

Date: 2026-08-26

Verdict: `ADMIT_TO_HUMAN_REVIEW_F21_STACK` for deterministic composition.
Submission remains `CLOSED`: this is complete-state equivalence and value
evidence, not an untouched clean-nonce evaluation or an official score.

## Binding

- N1 source commit: `bac61e355cd7fe886e100db8a456ebdcb6c986a9`.
- N1 source tree: `7bcd5078553f9c63276747620b0f384dfdaef297`.
- Live-source parent: `64f9aaa510b338041bc15d54b32c97fc2f1f5442`.
- F21 implementation commits: `1414bb6`, `11d64e2`, and checker commit
  `ee2b4cf` (ports of `e57d5e6`, `01772f4`, and `3c6191b`).
- Exact candidate environment:
  `SUB4_SQUARE_B_LOCAL_K2=1 SUB4_PP_PEAK=1267`
  `SUB4_PP_WALK_PEAK=1266 SUB4_PINGPONG_INPUT_AWARE_CONSTPROP=1`
  `TLM_CASCADE_DISABLE=1`, with `TLM_CONSTPROP_STRADDLE` absent.

## TDD and controlled evidence

The inherited F21 contract and composition-checker suites pass `16/16`.
`cargo build --release --locked --bin build_circuit --bin eval_circuit`
also passes (three pre-existing warnings only).

The exact composition checker was run twice: first on 2 x 64 controlled lanes,
then on the full 141 x 64 = 9,024 controlled-lane gate. Both runs returned
`ADMIT_TO_HUMAN_REVIEW_F21` and proved:

- Q remains exactly `1265` (maximum referenced qubit id `1264`).
- Baseline artifact: `12,520,987` operations, compressed SHA-256
  `ccea63b339fa7715199b466d578235a5369f7b4477512a2c83c57e0f41dff610`.
- Stacked artifact: `12,520,960` operations, compressed SHA-256
  `ea7e6f85a74cb2fab138c4f764f84fdc0a9fe2c6b5487944de009a8af28d82d0`.
- F21 removes `27` emitted operations and exactly `51` executed Toffoli per
  lane on this N1 stream.
- All 51 transforms originate from unconditional (`NO_BIT`) CCX operations at
  condition-stack depth zero: 43 constant and 8 affine transforms.
- The second transform iteration removes zero gates, proving the fixpoint.
- Baseline and candidate have the identical full qubit/bit/phase outcome
  digest on all 9,024 controlled lanes:
  `f0860e3b6c995824367fd69de4d8be357a461f4c33fc028eb37c33ed5d1a8b8d`.
- Phase, ancilla, classical, and dirty-free-event fields match exactly.

The N1 Q1265 64-lane profile is `906,761.45` executed Toffoli. Because the 51
removed CCX operations are unconditional on every lane, the paired proxy is
`906,710.45`, giving:

```text
Q1265 proxy score       1,146,988,719.25
live score              1,150,873,758.00
projected lead              3,885,038.75  (0.337573%)
```

This is a stronger local value candidate than N1 alone, but the official
9,024-shot draw changes with the transformed operation stream. Its official
executed-Toffoli value and correctness therefore remain unclaimed until the
candidate has a new source-bound prefilter/checkpoint, a clean nonce, and an
untouched official evaluator run.

## Remaining gates

1. Independent review of this exact stack and its checker evidence.
2. Rebuild the corrected CPU/CUDA model against the stacked operation stream.
3. Device CPU/CUDA parity; local host-only CUDA-model tests are insufficient.
4. Bounded nonce search and an untouched trusted `9,024`-shot `0/0/0` result.
5. Independent reproduction, live-source/score rebind, and submission gate.

## Provenance

The reduced-width direction was suggested by Justin Drake. Codex implemented
and validated the N1 branch-B K2 construction. The F21 input-aware constprop
implementation and checker commits are authored by `welttowelt`; this report
reuses them without claiming independent invention. No provider, protected
fleet, remote repository, or submission was changed by this stack validation.
