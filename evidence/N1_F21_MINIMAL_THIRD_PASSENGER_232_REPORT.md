# N1/F21 minimal third-passenger selector

Status: `COMPLETE_LOCAL_CONSTRUCTION`

This change replaces the all-644 third-passenger gate with the exact 232-cell
peak-binding subset for the P1267/W1265 hybrid. The feature remains default
off and requires `SUB4_PP_THIRD_PASSENGER=1` exactly.

## Source binding

- Parent commit: `89ecdce649318df2b42689590ba2345ac2343ad0`
- Parent tree: `9df894758cb2036b624d8bcd2ff0866c5c79e076`
- Parent `pingpong_div.rs` SHA-256:
  `950997f008b472b14c7bf6d42f879014b71db166afd6e8094295e1bef86fb04d`
- Candidate `pingpong_div.rs` SHA-256:
  `a27ad6d4eb8d3840bfbf0c6576946d6ad4e9de5f0812a3ec2d6a4680a080571c`
- Selector SHA-256:
  `62bdab10888892989723f5062599f99bf8107a1c04da397e7a5cf32981bd4172`

The selector was derived from and independently rechecked against the
resource-localization packet
`third-passenger-peak-localization-89ecdce6-20260826T161812Z`. Credit for the
round families and necessity boundary belongs to that evidence phase; its
`SUMMARY.md` SHA-256 is
`a2ca3316fa73105eb3a11e92a54a0de502b9e1e1f2989ff3547c4a10da1ff776`.

## Exact selector

- Divide: `334-370,372,502,504,506,508,510-541,543,545,609,611,613,615-644`
  (109 cells: one prefix cell and 108 interleaved cells).
- Multiply: `318,320,322-367,369,495,497,501-538,540,608-637,639,641,643`
  (123 interleaved cells).
- Total: 232 of the original 644 eligible loan sites.

The selector unit tests enumerate every site in the 314-645 envelope, compare
the complete selected lists, assert the 109/123/232 census, and reject both
gap rounds and out-of-window rounds.

## Resource and dormant-path results

Exact environment: K2=1, P1267, W1265, F21/input-aware constprop enabled,
cascade disabled, straddle absent.

| arm | Q | max qid | emitted ops | compressed artifact SHA-256 |
|---|---:|---:|---:|---|
| full 232 candidate | 1264 | 1263 | 12,525,540 | `661cd2277d481677029bb27911b6bd98ee0402bba86469bc6db7a654419df933` |
| feature absent | 1265 | 1264 | 12,524,600 | `ef2e51614f6631e3ce49ccf8283106b55ee120583b6997ca3418b55cadf6bfdf` |
| feature `0` | 1265 | 1264 | 12,524,600 | `ef2e51614f6631e3ce49ccf8283106b55ee120583b6997ca3418b55cadf6bfdf` |
| feature invalid | 1265 | 1264 | 12,524,600 | `ef2e51614f6631e3ce49ccf8283106b55ee120583b6997ca3418b55cadf6bfdf` |

The three dormant forms are byte-identical to the exact parent hybrid control.

Each distinct binding family also reproduced its predeclared minus-one
resource witness:

| removed cell | Q | max qid | emitted ops | artifact SHA-256 |
|---|---:|---:|---:|---|
| Divide prefix 334 | 1265 | 1264 | 12,525,536 | `85c4b2cfbdc0bf7588d1f6ac77788021c84c05b4c6b9116bb8ce8398c545e0e6` |
| Divide interleaved 335 | 1265 | 1264 | 12,525,536 | `164cce9492c76c39e7dc9ab37c322cc80d1ce97434aceb121bcb94ac8b0a07d9` |
| Multiply interleaved 318 | 1265 | 1264 | 12,525,536 | `14c40d743a1e21b68cc80045932f5763775fafa0df6f835e53dbbe5f856f2135` |

## Controlled 9,024-lane screen

The final restored 232-cell source produced a faithful 141-round x 64-lane
mirror:

- classical faults: 22
- phase-fault shots: 14
- any-fault union: 23
- phase-bad rounds: 14/141
- ancilla-bad rounds: 0/141
- executed Toffoli total: 8,182,865,910
- average T: 906,789.21875000
- evaluator-style rounded T: 906,789
- outcome digest:
  `68f352d33ac07cd2c5129f40584203c805bd18b10adeaeddfd36a1c705c1edb4`

Evidence and retained artifacts:
`/Users/odin/.ecdsafail/evidence/minimal-third-passenger-232-89ecdce6-20260826T163714Z`.

This is a local construction/resource result. It does not overturn the prior
controlled H/C equivalence NACK and does not authorize search, provider use,
promotion, push, or submission.
