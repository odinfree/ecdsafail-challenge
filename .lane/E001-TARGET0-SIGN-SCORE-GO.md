# E001 — target0/sign alias: Q1271 SCORE_GO / VALIDATION_DIRTY

## Source and identity

- Frozen live source: `4eb93cb`; lane predeclaration: `f99997a`.
- `pingpong_div.rs` SHA-256:
  `943267f11183a8f028530a0be2cebb68dd39bfbd78b4a7df52d14be50b68efa0`.
- `mod.rs` SHA-256:
  `147d6a8f0ea029b254f97bf7b50d22064114004ad6d96b06fc0fccc159740796`.
- With the new alias absent, the parent composition remained byte-identical:
  12,916,385 ops, SHA-256
  `2b05882c8b4e301e98fcacf7965a5dbd2cb8d6cf77eb2507f1d337333b667c19`.

## Structural gates

- Target0/sign standalone miter: PASS 64/64, all 16
  sign/source0/doubled-out/add-carry arms, identical values and relative
  phase, ancilla zero, identical Toffoli, `+3 CX +1 R`, peak 575 -> 574.
- Existing fused-selector lifecycle: PASS 64/64, all eight arms, phase and
  ancilla zero, identical Toffoli, peak 573 -> 572.
- Full affine component: PASS, exact values, phase zero, ancilla zero,
  Q1271 / diagnostic T915181.750.
- Product-register square: PASS, Q1271 / T58738.531.
- Full profile: Q1271 / diagnostic T915100.86, with no allocation at 1272.

## Unchanged trusted 9,024-shot result

Configuration:

```text
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_EVICT_DOUBLED_OUT=1
SUB4_PP_ALIAS_TARGET0_SIGN=1
SUB4_PP_PEAK=1271
SUB4_PP_MUL_REPLAY_PEAK=1272
SUB4_SQUARE_LADDER=241
SUB4_PINGPONG_TAIL_NONCE=65700024945645
```

- Operations: `12,919,161`; SHA-256
  `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa`.
- Q: `1271`.
- Exact average T: `915142.533`; rounded T: `915143`.
- Score: `1,163,146,753`, a strict `684,586` below the freshly reopened live
  score `1,163,831,339`.
- Channels: classical/phase/ancilla `11/10/0`; first classical mismatch shot
  384.

## Verdict

`SCORE_GO / VALIDATION_DIRTY`.  The candidate is not valid and cannot be
submitted.  Hand the exact stream to a new combined classical and conditional
phase predictor qualification; no nonce hunt until sealed holdouts pass.  No
provider, range, fleet, submission, or public-note action occurred here.
