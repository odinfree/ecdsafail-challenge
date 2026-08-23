# Experiment ledger

## E001 — promoted-source selector lifecycle port

Status: `STRUCTURAL_PASS / FULL_MEASUREMENT_PENDING`.

The exact donor delta from `14608572e84daf89397768c43ac0d812c714c3bd`
against parent `71a5aae760e612345ffed924cd14381010d98ac1` was
three-way applied to promoted source `4eb93cb33bbf6a93229fe166b8d511c5e52ee253`.
The hash-bound porter is `.lane/tools/port_selector_eviction.py`, SHA-256
`3bc0ed0d7da568065f8e202050358e825875a1f3f2f760cc11f4ecca5b073154`.

Before/after file SHA-256:

| file | promoted input | merged output |
|---|---|---|
| `src/point_add/pingpong_div.rs` | `a247d6c7f31fd382b3041e4cb2f21d13d7870551fe68344e22615a02e11c0d20` | `6e7cce578663d8419c032190a9caa405ca0d84e0512104b766b9c68540f01994` |
| `src/point_add/mod.rs` | `da681f674c2bd0be2c507eafcc7785e045530d920fa343a52593aecf65619ba9` | `0c9e9a920d9078f2390028009895f03d495096fdac9d2b596c7913c064e03e63` |

The normalized added-line SHA-256 is
`42f400c50ae367e83f54521ac9fff2ea6c34b0c1d9e1f020f9ac7443da7b3526`
on both donor delta and rebased delta.  No promoted round, repair, nonce,
peak, square, or other default changed in source.

Forced release build after `cargo clean`:

- `target/release/build_circuit` SHA-256
  `1330fa45385cffbacae379943e1c939d429b3774f8d9ed5cd5b9d0d3c4105544`;
- `target/release/eval_circuit` SHA-256
  `afd84890818db97a93aaf94905e700058d6c963289f5bbd057a35352d53065a7`.

Frozen structural gates:

1. `SUB4_PP_FOLD_SELECTOR_EVICT_SELFTEST=1`: PASS 64/64 values under both
   lifecycles, phase 0, ancilla 0, all eight selector arms, identical
   Toffoli, exactly `+4 CX +1 R`, peak `573 -> 572`.
2. `SUB4_PRODUCT_SQUARE_SELFTEST=1` with the frozen candidate environment:
   PASS, 58,980 emitted / 58,721.141 executed Toffoli, Q1272.
3. `SUB4_PINGPONG_POINT_ADD_SELFTEST=1` with the frozen candidate
   environment: PASS, 956,012 emitted / 914,785.328 executed Toffoli, Q1272.

The sole measurement environment remains exactly:

```text
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
```

All other `SUB4_*` variables are unset.  Full 9,024-shot measurement remained
unopened at structural commit `73422709ed70ba9725b3cb592770bcf197df4cdb`.
Generated binaries and `ops.bin` are excluded.

### Terminal measurement

The exact three-variable candidate rebuilt to 12,904,643 operations, compressed
artifact size 50,846,670 bytes, SHA-256
`ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`.
The unchanged evaluator loaded Q1272 / 957,916 bits and completed all 9,024
shots:

- exact average executed Toffoli: `914783.521`;
- rounded T: `914784`;
- rounded score: `1,163,605,248`;
- strict margin below live score `1,163,831,339`: `226,091`;
- classical / phase / ancilla: `23 / 8 / 0`;
- first failure: classical mismatch at shot 292;
- exact appended evaluator-row SHA-256 before restoration:
  `8723d525d7a4502c921c374d0e675bcca786d58c3b80b85f9de06ea29f036d86`.

A pair of independent unchanged evaluator appends reproduced the same
Q/T/op count, full `23/8/0` channels, and first mismatch.  The first was an
accidental bare `--help` invocation (the evaluator does not consume that flag),
and the second was the explicit named confirmation.  Their row SHA-256 values
are `ec5574ae0dea4739b5189c80532b0a6a28622cbda7b8ecc1e58bc783b39ef1f6`
and `b403c8982fab24b84af564f03fe382fdb279ac72dbac3ad579e8e8ace73f614e`.
No evaluator process remained active at receipt sealing.

The tracked `results.tsv` was restored byte-exact to its pre-evaluation SHA-256
`eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`;
the generated evaluator row is represented only by this durable receipt.

Verdict: `SCORE_GO / VALIDATION_DIRTY`.  The saddle clears the frozen Q1272
score ceiling by 177 rounded Toffoli, but `23/8/0` forbids submission and makes
source-bound predictor qualification the next binder.  No hunt, provider,
range, fleet, or submission action was taken.
