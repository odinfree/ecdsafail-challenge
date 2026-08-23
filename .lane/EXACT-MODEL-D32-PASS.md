# Q1272 selector eviction: blinded D32 exact-model result

Date: 2026-08-23

## Verdict

`D32_EXACT_32_OF_32`; `745_OF_745_FAULTS`; `CPU_MODEL_EXACT_96_OF_96`;
`GO_PARITY_PREDECLARATION`; `HOLD_CUDA_EXECUTION`; `HOLD_RANGE`;
`HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The private D32 passed complete 9,024-bit classical-fault-mask equality after
its predictor output was sealed at
`fa03d445f1759b462c75b1113fa1d9153358fb54`.  The evaluator saw no D32 nonce
before that commit.  Combined with H64, the exact local CPU model now agrees
on 96/96 nonces and 2,202/2,202 classical faults.

This closes only the local CPU exactness gate.  It does not certify Linux or
CUDA parity, screen the phase channel, authorize a range, or qualify a
submission.

## Source, model, and harness binding

```text
candidate source commit         14608572e84daf89397768c43ac0d812c714c3bd
candidate source tree           d56979a2d5b4ac32bb429dd5858211d3bb7eb196
candidate operation count       12908488
canonical predictor commit      b3f71f75dc3448f0bd8a7693e95d0546414e0e58
predictor source SHA-256        b2a4d44c89b5340c7cc7d2db8a11b8cebc9207537a0f6883445d9dd85799e9b4
local predictor binary SHA-256  f7e16bd373708d90d839105ca7e5bf00b46a202bb1ffa05e850c1ecc7e5551db
builder binary SHA-256          0aecd50563ddf9c25a61b9e8edf8c1539adc7417fa4c0458b5f1d484d7c3bce6
evaluator binary SHA-256        06e56929e9c6ccbc9399682df34bb593e32875f78ddd1ba004b7c195c5cbcc14
D32 evaluation harness SHA-256  7c158ad9038a52666567dbba1e4ffee9c2b94c8af86af2b22e8fb9c2d46b8d0d
comparison script SHA-256       cb123b77808997022b08d8361028e28b39a0ed72614d5639c53348bd1fed6d92
```

Every D32 build used only:

```text
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PINGPONG_TAIL_NONCE=<sealed private value>
```

Every evaluator run used the existing output-only trusted instrumentation with
`EVAL_CLASSICAL_SHOTS=1`, `EVAL_EXACT_TOTALS=1`, and `EVAL_NO_WRITE=1`.
Before and after, tracked `src/bin/eval_circuit.rs` remained at SHA-256
`b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`
and `results.tsv` remained at SHA-256
`eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

## Blinded receipt chain

```text
private D32 nonce-set SHA-256       ae6be39a5193eee86c96485a0bcdc8caec46782f2eb8697bff1d97f9e331bab2
sealed predictor-mask SHA-256       dd1296442729e24ab586b730a266e03141dbf0ed8cfa5ebc38c14c94c40133f3
revealed evaluator-mask SHA-256     1542b90568e1ee048b62dec5b8e4a2d344ead81ecee8a02ec4ef2ee7869c5e21
complete evaluation receipt SHA-256 3b663335d17f0f296c618ca8f85fb07cf977eaf7c71cf7639b2582042dd9f23a
operation manifest SHA-256          0675f719388aaad1ec127aeab6ec013ed6ed39101c493d3c1a73ccf2418b5435
build/evaluator log manifest SHA-256 bb742e473164966e7431dfcb6228be21092d55f64243b04ba8fa33b1ac72f199
```

The nonce list, operation artifacts, per-row receipts, logs, and complete
masks remain outside Git.  Their hashes bind every hidden value and result.

## Complete-mask result

```text
evaluator rows            32
predictor rows            32
evaluator classical       745
predictor classical       745
exact masks               32/32
mask mismatches           0
phase-garbage batches     553
ancilla-garbage batches   0
Q/op/shot/ancilla guards  32/32
trusted evaluator exit 1  32/32
```

Every row loaded 12,908,488 operations, measured Q1272, executed 9,024 shots,
and finished with ancilla zero.  The comparator verified nonce-set equality,
141-word mask shape, declared count against popcount, and every mask bit.

Exact D32 Toffoli totals:

```text
total numerator / shots  264144151473 / 288768
mean T                   914727.918166140292553
minimum row T            914715.764738475
maximum row T            914742.612034575
```

## Promotion boundary

The next permitted action is a separate fail-closed Linux/CUDA full-mask
parity predeclaration bound to this exact source, model, and fixture chain.
CUDA execution, any range, phase-based retention, a provider action, nonce
hunt, submission, and incumbent mutation remain on hold until separately
authorized and qualified.
