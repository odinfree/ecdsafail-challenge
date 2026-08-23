# Q1272 selector eviction: exact CPU model H64 result

Date: 2026-08-23

## Verdict

`H64_EXACT_64_OF_64`; `1457_OF_1457_FAULTS`; `WRONG_STREAM_FAIL_CLOSED`;
`GO_D32_PREDICTION`; `HOLD_D32_EVALUATOR_REVEAL`; `HOLD_CUDA`;
`HOLD_RANGE`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The local run performed after exact-model predeclaration commit
`83d4a64ec1d8e15d05f82363311efdc44df6ad17` reproduces complete classical
fault masks on all 64 public H64 nonces.  It permits only the frozen private
D32 predictor-first step.  It does not certify phase behavior or authorize a
range.

## Bound artifacts

```text
candidate source commit         14608572e84daf89397768c43ac0d812c714c3bd
canonical predictor commit      b3f71f75dc3448f0bd8a7693e95d0546414e0e58
predictor source SHA-256        b2a4d44c89b5340c7cc7d2db8a11b8cebc9207537a0f6883445d9dd85799e9b4
local predictor binary SHA-256  f7e16bd373708d90d839105ca7e5bf00b46a202bb1ffa05e850c1ecc7e5551db
comparison script SHA-256       cb123b77808997022b08d8361028e28b39a0ed72614d5639c53348bd1fed6d92
plain H64 nonce-list SHA-256    17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9
evaluator masks SHA-256         f36d0e85ac70a21f32822b70971fa6ca53ad9cdfe7bf57e90b1c18e8f6d7a6af
predictor masks SHA-256         f5ffc40cdefc69fabccc41cef7466eaeeecad8bcbbe39e003c31613a8c2b367a
predictor stderr SHA-256        e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
tracked results.tsv SHA-256     eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810
```

Before execution, the candidate source files, imported predictor source,
local binary, H64 list, restored evaluator source, and tracked results all
matched the predeclared hashes.  After execution, the worktree and tracked
results remained unchanged.  Raw predictor and evaluator masks remain outside
Git.

## Complete-mask result

```text
evaluator rows       64
predictor rows       64
evaluator faults     1457
predictor faults     1457
exact masks          64/64
mask mismatches      0
```

The comparator validates 141 words and 2,256 lowercase hexadecimal characters
per predictor row, nonce uniqueness and set equality, declared count versus
mask popcount, and every one of the 9,024 bits.  Its independent positive and
negative synthetic controls returned exit 0 and exit 1 respectively before
this run.

## Wrong-stream control

With selector eviction omitted, the same binary built 12,904,991 operations,
refused the stream before scoring, emitted zero stdout bytes, and exited 2.
The refusal log SHA-256 is
`fc919d9c671410993052013049ad308ddeb3489efc948978f091f9b7c81a8c5b`.

## Next gate

Run the predictor on the already-sealed private D32 list, then hash and freeze
its output before any trusted evaluator reveal.  Only after that seal may the
unchanged 9,024-shot evaluator produce D32 classical masks.  Complete 32/32
mask equality is required before Linux/CUDA parity; no range is authorized.
