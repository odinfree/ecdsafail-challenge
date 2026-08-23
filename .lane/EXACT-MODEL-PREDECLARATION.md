# Q1272 selector eviction: exact classical-model qualification

Date: 2026-08-23

## Frozen decision and sequence

`MODEL_PREDECLARED`; `HOLD_H64_MODEL`; `HOLD_DISJOINT_REVEAL`;
`HOLD_CUDA`; `HOLD_RANGE`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The paired H64 density gate passed and was sealed at
`9e50f6e59fb25670b9e50575e2af4a33530fcc3d`.  This protocol qualifies only
the exact CPU predictor against complete 9,024-bit classical-fault masks.  It
does not certify the phase channel or authorize scanning.

The order is fixed:

1. verify all identities below and the unchanged source/results guards;
2. run the predictor only on the frozen public H64 list;
3. require exact 64/64 complete-mask equality and 1,457/1,457 faults;
4. only after H64 passes, run the already-frozen private D32 through the
   predictor and seal its predicted-mask output hash;
5. only after that prediction is sealed, reveal D32 with the unchanged trusted
   9,024-shot evaluator instrumentation and compare complete masks; and
6. require exact 32/32 equality before any Linux/CUDA parity work.

Any missing, duplicate, malformed, count-inconsistent, or bit-different row is
`FAIL_MODEL`.  A failure stops before the next stage.  No correction may be
fit to H64 or D32 inside this protocol.

## Circuit and predictor binding

Exact candidate environment:

```text
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
SUB4_PP_FOLD_SELECTOR_EVICT=1
```

Frozen identities:

```text
candidate source commit       14608572e84daf89397768c43ac0d812c714c3bd
candidate source tree         d56979a2d5b4ac32bb429dd5858211d3bb7eb196
candidate operation count     12908488
inherited operation SHA-256   678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0
canonical predictor commit    b3f71f75dc3448f0bd8a7693e95d0546414e0e58
local imported predictor tip  0a32a6c1447af64c7f08779e427658d1f777c582
predictor source SHA-256      b2a4d44c89b5340c7cc7d2db8a11b8cebc9207537a0f6883445d9dd85799e9b4
local release binary SHA-256  f7e16bd373708d90d839105ca7e5bf00b46a202bb1ffa05e850c1ecc7e5551db
comparison script SHA-256     cb123b77808997022b08d8361028e28b39a0ed72614d5639c53348bd1fed6d92
rustc                         1.93.0 aarch64-apple-darwin
```

The local binary was compiled before this predeclaration but was not executed
on H64 or D32.  Its canonical imported source is byte-identical to `b3f71f7`.
The selector-off wrong stream has 12,904,991 operations and must exit 2 before
emitting a scored row.  A correct operation count does not override any source
or environment hash mismatch: qualification stops on either.

## H64 binding

The tracked corpus is the 64 nonces `444000000000..444000000063`; it was
already public before the predictor port.  Its frozen receipts are:

```text
tracked corpus SHA-256          f8d1cfb4d281c08f69778c7e634ebd4fc9addf2870816cc4ef2bad23800bcf57
plain nonce-list SHA-256        17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9
evaluator-mask manifest SHA-256 f36d0e85ac70a21f32822b70971fa6ca53ad9cdfe7bf57e90b1c18e8f6d7a6af
evaluator-log manifest SHA-256  671f85777ab23261e909ee2c2d656650ebdf812ed10e855344948900e1379330
raw density receipt SHA-256     90a8d5c33fa62413befd337667bbe272f8bc7fe9e6e4f397df0192b2955efe9d
expected rows                   64
expected evaluator faults       1457
```

The evaluator-mask manifest has one canonical row per nonce containing its
declared count and strictly increasing exact mismatch-shot indices.  It is
mode 0600 outside Git.  The predictor must emit exactly 141 fixed-width
little-endian-word mask segments, or 2,256 lowercase hexadecimal characters,
per nonce.  The committed comparator validates shape, uniqueness, popcounts,
nonce-set equality, and every mask bit.

The independently pushed audit at `6d8a9951753ab0bf69b0669c386b161d274fa8b6`
is corroboration only and does not replace this local predeclared run.

## Private disjoint D32 binding

Before any H64 predictor execution, 32 unique 48-bit nonces were sampled from
OS randomness and sorted canonically.  The set excludes H64, the inherited
nonce, and the previously qualified Q1274 D32.  Its values and all later raw
masks remain outside Git.

```text
private D32 nonce-set SHA-256  ae6be39a5193eee86c96485a0bcdc8caec46782f2eb8697bff1d97f9e331bab2
private D32 rows               32
H64 overlap                    0
inherited-nonce overlap        0
prior Q1274 D32 overlap        0
out-of-48-bit-range rows       0
```

If H64 passes, the exact predictor first emits and seals D32 predictions while
the evaluator outcome remains unread.  Only then may the existing output-only
trusted evaluator binary reveal D32.  Every revealed row must have Q1272,
12,908,488 operations, 9,024 shots, and ancilla zero.  The comparison gate is
32/32 complete classical-mask equality; count-only agreement is insufficient.

## Trusted evaluator and mutation guards

```text
temporary output-only evaluator source SHA-256 706a50f5e23aefed04aaeb7a6fbe66a201ec6f0a53ba52026bd19730c2832248
temporary output-only evaluator binary SHA-256 06e56929e9c6ccbc9399682df34bb593e32875f78ddd1ba004b7c195c5cbcc14
restored tracked evaluator source SHA-256        b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b
tracked results.tsv SHA-256 before/after         eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810
```

The temporary evaluator changes output only: it emits classical mismatch-shot
indices and exact integer totals, suppresses result-row writes, and preserves
operation loading, Fiat-Shamir state, inputs, RNG, simulation, comparison,
channel accounting, gate totals, and exit status.  Raw nonces, masks, logs,
operation artifacts, binaries, and generated manifests stay outside Git.

## Promotion boundary

`H64_EXACT` permits the blinded D32 sequence only.  `D32_EXACT` permits a
separately frozen Linux/CUDA full-mask parity packet only.  Neither result
permits a range, provider contact, hunt, submission, or incumbent mutation.
