# Stage A — unmodified Q1271 co-binder receipt

Measured: 2026-08-23, before Claude launch and before any operandless source
edit or output.

## Identity and decision

`BASE_Q1272 / DIV_REPLAY_BINDS / OPERAND_PRESENT / CANDIDATE_UNMEASURED`

- branch predeclaration: `a24c50ba673375f46c9de05f81040c1b85ed16bb`;
- exact protected source parent: `14608572e84daf89397768c43ac0d812c714c3bd`;
- protected `pingpong_div.rs` SHA-256:
  `de5e347383a9bab4d76a2776b3bcee4bebda4fecb65beb3dd1ad4c1cbf4c1095`;
- unchanged evaluator SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- exact geometry:
  `SUB4_PP_PEAK=1271 SUB4_SQUARE_LADDER=241
  SUB4_PP_FOLD_SELECTOR_EVICT=1`;
- clean release build hashes in this isolated worktree:
  `build_circuit`
  `c7287d9c29618e269472813bdd2a66bb6de6a57b729cee31a6afa21c515278f6`,
  `eval_circuit`
  `0c98954b433639ea2d88a4182bc61a7bc358c152fb38a7b9df470a000c694b47`.

The unchanged source emitted 12,921,215 operations. Compressed `ops.bin`
SHA-256 was
`c79db2459f5bda92af27b6b3bd0f36a4dde3c3945535703076ff9602fde5c2cb`
(51,699,811 bytes compressed; 723,588,056 bytes uncompressed).

The unchanged full 9,024-shot evaluator measured Q1272,
T915262.302 (rounded 915262), and classical/phase/ancilla `18/16/0`.
The first reported failure was phase mask
`0x8000000000000000`. This is a dirty architecture receipt only and cannot
authorize a hunt or submission. Rounded T is 4,566 below the dispatched
Q1271 ceiling of 919,828, but the requested Q row does not yet land.

## Complete owner profile

`PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` on the identical operation stream
reported Q1272 at operation index 4,264,413 in `pp_div_replay`. The profile
composition passed 64/64 exact values with phase zero and zero dirty
non-register qubits. Every relevant owner peak was:

| owner | peak Q |
|---|---:|
| `pp_div_replay` | 1272 |
| `square_product_register` | 1271 |
| `pp_mul_replay` | 1271 |
| `pp_mul_walkback` | 1271 |

For completeness, `pp_div_walk` and `pp_div_walkback` each peaked at 1050,
and `pp_mul_walk` peaked at 1050. The 64-lane profile executed T915214.44;
the unchanged full evaluator above is the scoring receipt.

## Exact binding live set

A bounded source-owner census over `[4264350,4264480]`, filtered to
`pp_div_replay`, reproduced the same best instant at operation 4,264,413.
The 13 groups sum exactly to 1,272:

| live | allocation owner | allocation phase / role |
|---:|---|---|
| 402 | `pingpong_div.rs:1067` | `pp_div_replay`, interleaved walk signs |
| 297 | `pingpong_div.rs:1067` | `pp_div_walk`, pre-replay walk signs |
| 256 | `pingpong_div.rs:2005` | `init`, caller numerator register |
| 256 | `pingpong_div.rs:261` | `pp_div_replay`, replay coefficient register |
| 51 | `pingpong_div.rs:1585` | `pp_div_replay`, fused-fold carry chain |
| 3 | `pingpong_div.rs:1311` | `pp_div_replay`, clean AND outputs |
| 1 | `pingpong_div.rs:2004` | `init`, terminal walk register |
| 1 | `pingpong_div.rs:1490` | `pp_div_replay`, late overflow |
| 1 | `pingpong_div.rs:1584` | `pp_div_replay`, fused-fold roving operand |
| 1 | `pingpong_div.rs:1667` | `pp_div_replay`, parity |
| 1 | `pingpong_div.rs:1689` | `pp_div_replay`, plus-f selector |
| 1 | `pingpong_div.rs:519` | `pp_div_walk`, fused round-zero sign |
| 1 | `arith/adder.rs:341` | `tlm_inverse`, terminal/base wire |

This freezes the co-binders before the candidate: only division replay is one
qubit above Q1271, and its binding snapshot includes exactly one materialized
roving operand. No candidate edit, selftest, owner remeasurement, price
measurement, rescue tuning, predictor, hunt, network/provider action, or
submission occurred in Stage A.
