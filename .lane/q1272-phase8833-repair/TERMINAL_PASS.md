# Q1272 omitted phase-cleanup repair terminal report

Date: 2026-08-23

Verdict: `TERMINAL_GO / LOCAL_CPU_REGRESSION_PASS`.

The predeclared two-site repair at commit
`6cdcbedcb201bad289dd1381ae60429f0691d6fd` passed the complete local
regression gate. All work was offline. This receipt authorizes no CUDA,
range, search, provider, network, account, deployment, or submission action.

## Cause and bounded correction

The terminal HOLD at `12c4a723ae5a06e056f152b8bca33abe848f265d`
missed clean-phase shot 8833 for D32 nonce `154123680082395`. The exact
operation-site trace binds that shot to the second of two omitted Hmr events at
`src/point_add/trailmix_ludicrous/arith.rs:1471`:

- op `6,005,361`, R/Hmr ordinal `907,730`, in `tlm_coord_add3x`;
- op `12,901,960`, R/Hmr ordinal `1,938,318`, in
  `tlm_coord_rsub_final`.

The repair admits exactly those two sites. It models the full-width
`mod_add_exact` cleanup predicate and the top-19-bit
`mod_rsub_vented_loaded` cleanup predicate predeclared at commit
`03efb2781913e67fcaf0cf8e770ec296ac304a3c`. No classical arithmetic
function changed.

The regenerated schedule contains 3,966 phase sites and the unchanged
1,938,616 R/Hmr operations. Its family counts are
`(2573, 694, 694, 3, 2)`.

## Bound identities

- structural source:
  `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- operation count / SHA-256: `12,904,643` /
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- operation-site trace SHA-256:
  `f2f0f99d096027299460d9a82c16d3714c9684564d10f13f6dcbbac2b3e92833`;
- state digest: `e9b2d20ecd1169a8`;
- repaired model / host / driver SHA-256:
  `9eab10bd8cf1c3510f4dcada4f08f8eb93d2efb749cc8496a88b7f68401bb90b`,
  `aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2`,
  `71031a56d921056d41c845b4d933d5fcd020c563a98ec1d7f8407ab57c3962e1`;
- extractor / generator SHA-256:
  `6509c592501ff20c5c808512f443b11ae3881225e8f80c35ff6bdbff5241aaea`,
  `4efb39c8cd7da958cc80d719bd41ecbb47050f9c1bfee4c6ad298ca20fdebd18`;
- phase metadata / generated schedule SHA-256:
  `61e28111ff655bed39d5bc7dd8ccf0912274c112a34dfcc11ec01369725010b6`,
  `2135746c16dc4deb4e608cd2e7e1d9907fe167d76854ba2420279f6164efca82`;
- qualification driver SHA-256:
  `acd6246caaca2f1adfdbbb2ba7694287e1ccde991afe7dc858d05a55d54ce7ce`;
- unchanged local evaluator source / binary SHA-256:
  `26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98`,
  `90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`;
- qualified classical / repaired combined / forced-bad-schedule binary
  SHA-256:
  `50d96bebcec9476656b1e0242182a6a7a87c5ab6e38912e1023e7e5cdcba9be6`,
  `68bc5d1f21b6775aab149cd58f2e2c80d070d6d6df629bfd9d6971d8cda11e46`,
  `30e1ebbe22d5b3bf973f7f00e3c1cfde11537f5e4d473e3e635606e3b7e9f5c7`.

## Complete-mask results

The runner evaluated 257 unique fixtures and 2,319,168 shots. For every row:

- the qualified classical model, repaired combined model, and unchanged local
  evaluator produced byte-identical complete classical masks;
- the repaired model and evaluator produced byte-identical complete
  `raw_phase & ~classical` masks;
- evaluator geometry was Q1272 / 9,024 shots / ancilla zero;
- no fixture was missing or silently skipped.

| corpus | rows | classical faults | raw phase shots | clean phase shots |
| --- | ---: | ---: | ---: | ---: |
| inherited | 1 | 23 | 8 | 1 |
| H64 | 64 | 1,144 | 844 | 293 |
| D32 | 32 | 559 | 407 | 140 |
| V64 | 64 | 1,131 | 863 | 309 |
| F32 | 32 | 563 | 441 | 161 |
| fresh R64 | 64 | 1,107 | 865 | 302 |
| total | 257 | 4,527 | 3,428 | 1,206 |

The repaired D32 row now emits exactly `{304, 4238, 7668, 8833}`. Its
classical mask SHA-256 is
`560d30f493806202e2dc720dca85e234e55af27a7b9196fcbae31c6e55618b23`;
its conditional-phase mask SHA-256 is
`7ba3e07840033acc066bf83b88a09bf304642a74bd45c4aee494ce1cc545ce23`.

## Guards and deterministic repeats

All eleven fixed negative cases failed closed with empty stdout: disabled
scan, unknown mode, missing operation stream, six malformed nonce forms,
corrupted operation stream, and forced bad phase schedule. `NEGATIVES.tsv`
SHA-256 is
`10e9485ef31befd7b32d6c0e5e76864ef7cae9c6e7ce3784944cecfe7c476b42`.

Byte-complete deterministic repeats passed for the inherited singleton, the
last F32 row, the repaired D32 row, and the last R64 row. Their manifest
SHA-256 values are, respectively:

- `ccf6e7a10c9b5f2b09d518f686fa25379f583d403e0c5c8e35c2efb8477c02a9`;
- `54dbfc1e6bc241d5fb2830e524317f796d1e39d1d2d4560540ab3a9963572330`;
- `4879b59f065a25de2eb1dc86b2ddbfca41fa115999414b09618da30daef8947b`;
- `7b111a429095bc4b8f2bdb49cbdeffe055638dd239edf4d42eb08c89350bfffb`.

The complete `RESULTS.tsv` SHA-256 is
`90ba8719ba2e082e6646726ac6a15a8ab19659d33de055d0ab5cd2faaa241fb9`.
The generated terminal receipt SHA-256 is
`21d5a7507335069b4b8c0999fe26356d9e449327b4f347390a2a341975248b14`.

Generated binaries, metadata, schedules, masks, logs, attribution, and
evaluator outputs remain outside Git under
`/Users/olifreuler/ecdsa-ops/q1272-phase8833-repair-generated/` and
`/Users/olifreuler/ecdsa-ops/q1272-phase8833-repair-6cdcbed/`.
