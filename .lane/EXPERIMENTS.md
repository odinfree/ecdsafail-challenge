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

All other `SUB4_*` variables are unset.  Full 9,024-shot measurement remains
unopened at this commit.  Generated binaries and `ops.bin` are excluded.
