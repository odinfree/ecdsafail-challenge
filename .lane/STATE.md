# g1000 peak-cut composition state

Updated: 2026-08-23T03:04:32Z

Status: `BASELINE_BYTE_EXACT_COMPOSITION_PENDING`

## Objective and hard boundary

Compose only the proven Q1275 replay/square ownership defaults introduced by
`087cafaef46a4e339644a6191ff2df2e7031cb80` onto promoted g1000 source
`bdf4845afa4f911192e20b5260b9efbd67655cf9`. Preserve the g1000 width table,
multiply-round default, tail nonce, and all source opt-outs. Do not hunt,
submit, provision, or spend.

The one predeclared candidate delta is:

- `SUB4_PP_R1`: default `356 -> 342`
- `SUB4_PP_PEAK`: default `1278 -> 1275`
- `SQUARE_LADDER`: default `248 -> 245`

The `087cafa` nonce is not part of the ownership change and will not be copied.

## Fresh live gate

`ecdsafail benchmark` and `ecdsafail submissions --all` were reopened before
editing. Current best is submission `792ac70`, source `bdf4845`, Q1278,
rounded T915947, score `1170580266`.

Source identities:

- public commit: `bdf4845afa4f911192e20b5260b9efbd67655cf9`
- public tree: `2642dcda918a0cfca8aa2fad6fa9bdcfc5e690af`
- parent / ownership source: `087cafaef46a4e339644a6191ff2df2e7031cb80`
- parent tree: `4e2c565ef6ec215c444958eb0939b733c464e130`
- ownership diff SHA-256, limited to replay and square source:
  `10bf3455d221421c8a44c3ddb16f4f3808b404228883f6e7e39c289a414b34a1`

## Byte-exact default reproduction

The isolated worktree started clean at exact `bdf4845`. Source hashes matched
the independent shipping validation:

| file | SHA-256 |
|---|---|
| `src/point_add/pingpong_div.rs` | `c89ccb06cddaaccb6e9755302bca96d9e4a88ec1eff7dc51d243db67aa2d174f` |
| `src/point_add/mod.rs` | `163fd35fdd6f1ee14384bed40263446cf5c8fcd7a1b3ffb158ed2f9818720692` |
| `src/point_add/greedy_m1000_width_schedule.rs` | `46945a13b61a48e791a422e16681491fd791f5faf1f811802c44565ae9bf7943` |
| `src/point_add/trailmix_ludicrous/square/product_register.rs` | `897c6143b790421fe1d9abbbf8afff9f1f705859af22c678de5c6d9a67099cfd` |

The release builder was invoked under a clean environment containing only
`PATH` and `TMPDIR`. The result reproduced the promoted artifact byte-for-byte:

```text
emitted operations  12912890
ops.bin SHA-256     5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8
ops.bin bytes       50893170
qubits              1278
full 9024 result    0/0/0
exact average T     915947.392
rounded score       1170580266
```

Local binary hashes for this gate:

- `build_circuit`: `785dc3eca81e151a6fe7ad9f5b1bec9e68c8a3046d6c4389c86f1f29244c4828`
- `eval_circuit`: `6583a6e293782d408bc4614be52a4e4869a7787885440214cd3ef942d4e62543`

Generated `ops.bin`, `score.json`, binaries, and result rows are not committed.

## Candidate gates

1. Apply only the three ownership defaults above.
2. Prove the g1000 width-table file, 696-round default, default nonce, and
   opt-out expressions remain byte-identical to `bdf4845`.
3. Run a fixed 64-lane `PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` diagnostic at
   the inherited g1000 nonce `135608492183` and record every co-binder.
4. Refresh live SOTA. Run one candidate full 9,024-shot evaluation only if the
   measured Q/T bound predicts a strict score beat.
5. Stop on any source, op-stream, model, or hash mismatch.

