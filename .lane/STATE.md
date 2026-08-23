# g1000 peak-cut composition state

Updated: 2026-08-23T03:09:08Z

Status: `TERMINAL_FALSIFIED_17_8_0`

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

1. Applied only the three ownership defaults above: PASS.
2. The g1000 width-table file and nonce-bearing module remain byte-identical to
   `bdf4845`: PASS. This preserves the 696-round default, g1000 table,
   `SUB4_PP_G1000_DISABLE` opt-out, default nonce `135608492183`, and
   `SUB4_PINGPONG_TAIL_NONCE` opt-out.
3. Fixed 64-lane diagnostic: PASS at Q1275, T917331.19, `0/0/0`.
4. Fresh live refresh immediately before full evaluation: unchanged at
   `1170580266`, source `bdf4845`. Q1275 allowed rounded T <= 918102; the
   diagnostic predicted rounded score `1169597025`, a strict 983241 beat.
5. One inherited full 9,024-shot evaluation: FAIL at `17/8/0`.

## Exact composed source and artifact

The complete source diff from `bdf4845`, limited to the two edited files, has
SHA-256 `2532f89b0990269ac6693277d985d8828c000743774a5870888940c56f9922c2`.

| item | SHA-256 |
|---|---|
| `src/point_add/pingpong_div.rs` | `24b3d522fd7db7e25df5ee6f80bcb969d4d543a8d0eb6924261a0a4482729cbf` |
| `src/point_add/trailmix_ludicrous/square/product_register.rs` | `dd8236ac0da2c276d9489e78a58abf1e55d3f21ae410d520eb4dc51b364e4215` |
| unchanged g1000 table | `46945a13b61a48e791a422e16681491fd791f5faf1f811802c44565ae9bf7943` |
| unchanged nonce-bearing `mod.rs` | `163fd35fdd6f1ee14384bed40263446cf5c8fcd7a1b3ffb158ed2f9818720692` |
| candidate `ops.bin` | `059a249a8d2934aa83f508280f508821a92fb0b7ce5de5045d00acd0fa8e5e02` |
| unchanged evaluator source | `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b` |
| unchanged evaluator binary | `6583a6e293782d408bc4614be52a4e4869a7787885440214cd3ef942d4e62543` |

The composed stream contains 12,947,403 operations. The 64-lane peak trace
found four Q1275 co-binders: `pp_div_replay`, `square_product_register`,
`pp_mul_replay`, and `pp_mul_walkback`.

## Causal ablation

All rows use the same fixed 64 lanes and passed classical/phase/ancilla
`0/0/0`:

| geometry | Q | diagnostic T | artifact SHA-256 | conclusion |
|---|---:|---:|---|---|
| bdf defaults: R1 356, peak 1278, ladder 248 | 1278 | 915994.83 | `5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8` | byte-exact control |
| R1 342 only; peak 1278, ladder 248 | 1278 | 916032.23 | `60c9bdcb5a0d982180e8f77a2167178d1c156b2156068672429a15d89e357773` | R1 does not own the qubit cut |
| peak 1275 + ladder 245 only; R1 356 | 1275 | 917548.28 | `87d53888908c2bd7b44a05e91ba25c9c7eebc6b0b58b2588e41816d583918489` | coordinated replay/square cut owns all three qubits |
| composed defaults | 1275 | 917331.19 | `059a249a8d2934aa83f508280f508821a92fb0b7ce5de5045d00acd0fa8e5e02` | R1 recovers 217.09 T inside the narrow geometry |

This isolates the ownership mechanism: the coordinated replay/square pair owns
all three saved qubits, while R1 alone owns none. The co-binder trace explains
why replay and square must move together. R1 changes split placement and
conditional gate cost, but not peak width.

## Full falsifier and verdict

The unchanged evaluator loaded 12,947,403 operations at Q1275 and completed all
9,024 shots:

```text
classical mismatches     17
phase-garbage batches     8
ancilla-garbage batches   0
exact dirty-draw T   917361.243
```

The first classical falsifier is shot 923. If clean, rounded T917361 would
score `1169635275`, 944991 below the refreshed leader, but `17/8/0` closes the
inherited-nonce route. No hunt, provider action, submission, or spend followed.
The g1000 schedule changes the reachable width/fold fault surface, so the clean
`087cafa` nonce cannot establish compatibility and the clean g1000 nonce does
not transfer through the Q1275 ownership cut.

`git diff --check` passes. Repository-wide `cargo fmt --check` is not a usable
gate on this promoted snapshot: it reports extensive pre-existing formatting
drift in untouched files. No bulk formatting rewrite was applied.
