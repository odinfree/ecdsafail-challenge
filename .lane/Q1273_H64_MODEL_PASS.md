# Q1273 classical predictor H64 qualification

Verdict: `H64_MASK_PASS / LATER_DISJOINT_MODEL_HOLD`.

Important later result: after this H64 gate was sealed, an independently
frozen D16 corpus exposed one predictor-only shot. See
`Q1273_MODEL_HOLD.md`. The H64 measurement remains exact, but it is not proof
of a globally exact model and it does not permit a CUDA handoff.

The source-bound Q1273 CPU predictor reproduces the complete classical
mismatch-shot indicator for the inherited stream and all 64 predeclared H64
streams. There are zero evaluator-only shots and zero predictor-only shots.
No model source changed after either corpus was opened.

## Immutable source and corpus boundary

- circuit source: `093d85d64de87aa5006a94868172f642daacf136`;
- predictor predeclaration: `a8f7307f0a93ec78910444b2e4c18a78f70b9ae9`;
- predictor source bind: `9e9678471751993356b9a303dde6281fafd94937`;
- inherited mask checkpoint: `d4abbb6fa1a44d13cb8094601cf71c76435aa520`;
- corrected evaluator-source receipt: `14947704b42c3ead838ecaab6fe3c08c2a801a8d`;
- wrong-state guard checkpoint: `0560655ff2a8b1edde4884e9fe8cf0936572a6bc`;
- H64 nonce range: `444000000000..444000000063`;
- committed nonce-ledger SHA-256:
  `010a0599b98bd6b1ad4a78b6e7f036dcd72aa2043a1d1bb7f5d5dd50ec85374f`;
- operation count per stream: `12,933,805`;
- qubits per stream: `1,273`;
- shots per stream: `9,024`;
- evaluator source / instrumentation patch SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b` /
  `15943baf5815f36188a8406b7a080c8b446f856a9337d8046eafe363752c6e4f`;
- instrumented evaluator binary SHA-256:
  `37081d949bf34f185023098e74393a9014b96853633646288a90f1538663580e`;
- CPU predictor binary SHA-256:
  `93a9d9be4e542388457d802dd0a0832c527bfe3803efd8158a2d66e626ecd63c`;
- circuit-builder binary SHA-256:
  `67c8720188d26fe464c3552bba02a2ec011fe7f5c40b0517c4b1c71a55977995`;
- external qualification runner SHA-256:
  `696ee7d36381b8947046f5cb78c7953a9411aecb4d362f80d0f7176001c4ce38`.

Every H64 operation SHA is unique. Each stream was force-generated with only
`SUB4_PINGPONG_TAIL_NONCE` changed, evaluated through the full 9,024-shot
trusted semantics, and required to report Q1273, exactly 12,933,805 operations,
and zero ancilla-garbage batches. All 64 evaluator calls returned the expected
dirty status 1; no result file was written. `results.tsv` remained byte-exact
at SHA-256
`eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

## Exact result

| gate | result |
|---|---:|
| inherited complete-set equality | `1/1` |
| H64 complete-set equality | `64/64` |
| inherited evaluator / predictor faults | `12 / 12` |
| H64 evaluator / predictor faults | `870 / 870` |
| H64 evaluator-only / predictor-only shots | `0 / 0` |
| H64 classical / phase / ancilla totals | `870 / 696 / 0` |
| H64 per-stream classical min / max | `6 / 26` |
| H64 per-stream phase min / max | `3 / 20` |

The concatenated evaluator and predictor H64 index masks are byte-identical,
870 rows each, SHA-256
`9c1c9cfb0dc7057e8ea1aafbd55c42382e9c4eeabab0d13fe80d18d98c899f46`.
The corresponding CPU cause-mask ledger SHA-256 is
`eb3193ffefa76c5572006878fec23ca83f8d83737db49cd0d4c2cbceeb99a0b6`.

All five source-semantic cause bits are exercised by H64, with no combined-bit
rows:

- walk divide, mask 1: 315;
- replay divide, mask 2: 68;
- walk multiply, mask 4: 432;
- replay multiply, mask 8: 53;
- final result, mask 16: 2.

## External receipt seal

Raw operation artifacts, evaluator logs, shot sets, predictor cause masks, and
binaries remain outside Git under
`/Users/olifreuler/ecdsa-ops/q1273-predictor-093d85d`.

- 64-row fixture ledger SHA-256:
  `7918937a30d562a2dd26cf59374cdb702c11ce0f08d42789f9ef42da8264b5f4`;
- 448-row terminal artifact manifest SHA-256:
  `35e4a583a434821aca0bd9b5f94bc7e241eb32c6fbb769dec1c7f8f03436577a`;
- top-level H64 seal SHA-256:
  `97a4acfef1084d264c20fb13d3673f1a5adcdb284568fd81480f3ceca38704b6`.

This gate qualified the CPU model only on the frozen inherited plus H64 corpus.
It never authorized a range scan, provider action, nonce hunt, submission, or
claim of CUDA parity. The later disjoint counterexample blocks the formerly
planned Linux/CUDA handoff until a separately predeclared exact wrapped-state
model passes a new holdout.
