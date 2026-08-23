# Q1271 target0/sign-alias combined CPU predictor predeclaration

Decision boundary: `FROZEN / NO MODEL OUTPUT / HOLD D32`.

This packet qualifies a source-bound CPU classical plus conditional-phase
screen for the exact target0/sign-alias Q1271 stream.  It does not modify the
circuit or evaluator and grants no CUDA, provider, range, hunt, submission,
fleet, or public-note authority.

## Exact target binding

- evidence/source commit: `a22090374a957d29a3331d6c876ad12ff45fea31`;
- source tree: `018eb52de8ab3e6337864338683821c0cbb574a2`;
- source parent predeclaration: `f99997a`;
- `src/point_add/pingpong_div.rs` SHA-256:
  `943267f11183a8f028530a0be2cebb68dd39bfbd78b4a7df52d14be50b68efa0`;
- `src/point_add/mod.rs` SHA-256:
  `147d6a8f0ea029b254f97bf7b50d22064114004ad6d96b06fc0fccc159740796`;
- exact operation count / SHA-256: `12,919,161` /
  `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa`;
- exact build environment:
  `SUB4_PP_FOLD_SELECTOR_EVICT=1`,
  `SUB4_PP_EVICT_DOUBLED_OUT=1`,
  `SUB4_PP_ALIAS_TARGET0_SIGN=1`,
  `SUB4_PP_PEAK=1271`,
  `SUB4_PP_MUL_REPLAY_PEAK=1272`,
  `SUB4_SQUARE_LADDER=241`, and every other `SUB4_*` variable absent;
- inherited nonce/result: `65700024945645`, Q1271 / exact T915142.533 /
  rounded T915143 / `11/10/0`, first classical mismatch shot 384;
- frozen score: `1,163,146,753`, a strict `684,586` improvement over the
  source packet's reopened reference score `1,163,831,339`.

Before any predictor result, a forced source build must reproduce the complete
operation identity and the unchanged full evaluator must reproduce the
inherited aggregate.  Generated operations and evaluator outputs stay outside
Git.

## Donor and portability boundary

The only donor is terminal combined CPU commit
`83ad631e1a99db3db1c3886b4d61ff9ded94b0f5`, tree
`e96c542e73c8b265eadfe3c4bbcb71df1096a024`.  Portable semantics are limited
to the 256-bit finite-width walk/walkback/replay recurrences, source-event
checkpoint method, add3x low-fold behavior, conditional-phase family
composition, canonical mask framing, and the final predicate:

```text
clean_phase_mask = raw_phase_mask & ~classical_mask
survivor = classical_mask == 0 && clean_phase_mask == 0
```

No Q1272 operation, checkpoint, phase ordinal, schedule/table, constant,
fixture result, mask, digest, or binary transfers.  This lane must independently
derive from the exact target source and stream:

- both round counts and width schedules, including separate multiply-replay
  peak behavior;
- selector, doubled-out, and target0/sign alias lifecycles;
- replay/fold/endpoint/flag/chunk widths and round-zero behavior;
- operation-site sequence, R/Hmr family geometry, checkpoint digest, and tail
  binding;
- add3x finite-width carry/drop semantics at every source call site.

No nonce/shot exception, oracle lookup, ideal-output fallback, tolerant mask,
raw-phase claim on classically dirty shots, or alternate survivor predicate is
allowed.  A mismatch must be localized to the first source mechanism and fixed
generically or this family is `HOLD`.

## Frozen corpora and reveal order

- inherited singleton: tracked `INHERITED.nonces` (nonce
  `65700024945645`), SHA-256
  `dabc177103443bede607625489337794ac828e25b60e787a67f7789bfa1627f1`;
- sealed H64: tracked `H64.nonces`, the exact ordered LF list
  `444000000000..444000000063`, SHA-256
  `17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9`;
- genuinely disjoint D32 holdout: Git object
  `3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e:.lane/q1273-wrap-exact/D32.nonces`,
  required byte SHA-256
  `62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90`.

The D32 object remains unopened to model output until a clean H64 exact-parity
commit is pushed.  Its reveal runner must prove 32 unique canonical unsigned
decimals below 2^48 and complete disjointness from inherited and H64 before
opening any mask.

Ordered gates:

1. push this predeclaration and corpus hashes;
2. reproduce target operations and inherited unchanged full aggregate;
3. build a current-source two-pass trusted oracle and seal complete inherited
   and H64 classical/raw-phase/conditional-phase masks with Q1271/9024/ancilla0;
4. only then port and run the predictor, using source-derived geometry and the
   inherited row for semantic calibration;
5. require complete 9,024-bit classical and conditional-phase equality on the
   inherited row, then H64 `64/64`; seal and push the model before D32 reveal;
6. reveal D32 exactly once, without post-reveal semantic edits; any complete
   mask mismatch is terminal `HOLD`;
7. repeat the inherited row and final D32 row byte-identically;
8. run the complete fail-closed negative matrix.

## Terminal CPU handoff gates

`CPU_HANDOFF_GO` requires all of:

- exact source hashes, operation magic/count/SHA, tail shape, checkpoint,
  source-derived schedule, family order/count, predictor source/binary hashes,
  and deterministic SHAKE256 framing;
- complete classical-mask equality on inherited + H64 + D32;
- complete `raw_phase & ~classical` equality on inherited + H64 + D32;
- ancilla zero on every trusted oracle row;
- canonical sorted unique shot indices in `[0,9024)` and byte-identical
  deterministic repeats;
- fail-closed rejection with empty stdout for wrong magic, count, same-count
  wrong SHA, state/checkpoint, schedule, missing stream, malformed/overflowing
  nonce, malformed/out-of-range shot, unknown mode, extra arguments, and any
  scan/range mode.

All binaries, operation streams, raw traces, generated schedules/tables,
oracle masks, logs, and evaluator rows remain outside Git.  Only durable model
source, qualification runners, compact transitive hash receipts, and evidence
summaries may be committed.
