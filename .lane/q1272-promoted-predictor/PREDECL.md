# Promoted-source Q1272 predictor predeclaration

Status: `PREDECLARED / SOURCE_INTAKE_PENDING / HOLD_RANGE / HOLD_PROVIDER`.

## Exact target

- structural commit: `73422709ed70ba9725b3cb592770bcf197df4cdb`
- structural tree: `fe77bddfb49b426312b1cca3d009b150cd06fd89`
- terminal evidence commit: `41dd0b4508527081b8d24255adf0579389f02453`
- terminal evidence tree: `04fee126fd8fb3112e7422bddb2e458dd38adbc6`
- circuit environment: `SUB4_PP_FOLD_SELECTOR_EVICT=1`,
  `SUB4_PP_PEAK=1272`, `SUB4_SQUARE_LADDER=242`; every other `SUB4_*`
  variable unset
- operations: `12,904,643`
- operation SHA-256:
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`
- target source hashes: `pingpong_div.rs`
  `6e7cce578663d8419c032190a9caa405ca0d84e0512104b766b9c68540f01994`,
  `point_add/mod.rs`
  `0c9e9a920d9078f2390028009895f03d495096fdac9d2b596c7913c064e03e63`,
  product register
  `864d31454c5279632652cf48aeda038d481a504b09e4f7a8c0f266e10a24b81c`
- unchanged full diagnostic: Q1272, T914783.521 (rounded 914784),
  classical/phase/ancilla `23/8/0`, first classical mismatch shot 292
- frozen board: source `4eb93cb`, score `1,163,831,339`; strict Q1272
  rounded-T ceiling `914,961`

## Donor boundary

The earlier Q1272 selector predictor source
`b2a4d44c89b5340c7cc7d2db8a11b8cebc9207537a0f6883445d9dd85799e9b4`
is a mechanical starting point only. It is bound to older source `14608572`
and older operations `678c149f...`; neither its model constants nor its
checkpoint may be reused as evidence.

The existing arm64 partial donor predicts 17 classical faults for target nonce
`65700024945645`, including trusted first shot 292, while the unchanged target
evaluator reports 23. The six-fault undercount is a mandatory negative control:
no port may pass by preserving that output.

Q1273 combined machinery may supply trace schemas, schedule generation, and the
conditional mask contract `clean_phase = phase & ~classical`. Its schedule,
constants, fixtures, checkpoint, and measured rows are Q1273-only and excluded.

## Frozen qualification sequence

1. Integrate only committed target `41dd0b4`; the resulting code files must
   match the exact hashes above.
2. Import the old predictor as a source donor, change its operation guard and
   rederive the target's 696/696 rounds, sampled width schedule, replay folds,
   coordinate/square value channel, and all conditional-phase sites from exact
   target source.
3. Rebuild the target operations and a nonce-independent checkpoint locally;
   require exact count/SHA plus deterministic checkpoint identity.
4. Freeze inherited nonce `65700024945645` and the existing 64-nonce H64 list
   before predictor output. Compare all 9,024 classical bits per nonce, not
   aggregate counts. Require 65/65 exact and require the inherited result to be
   23 faults with first fault shot 292.
5. For every fixture, instrument the unchanged evaluator to emit complete
   classical and phase masks. Compare `phase & ~classical` bit-for-bit in exact
   source-event order. Raw phase on classically dirty shots is diagnostic only.
6. Freeze a disjoint D32 prediction before evaluator reveal. Require 32/32
   classical and conditional-phase mask equality after reveal.
7. Close deterministic-repeat, wrong-operation-count, same-count wrong-SHA,
   wrong-checkpoint-state, truncated-stream, malformed-fixture, and omitted
   conditional-phase-site negatives with empty stdout on rejection.
8. Only after local CPU qualification may a separate scan-disabled Linux/CUDA
   complete-mask packet be sealed. Provider, range, hunt, and submission remain
   forbidden until that later terminal GO.

Every generated operation file, checkpoint, binary, evaluator log, raw mask,
trace, receipt staging tree, and cache stays outside Git.
