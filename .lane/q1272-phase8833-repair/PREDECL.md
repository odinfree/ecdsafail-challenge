# Q1272 omitted phase-cleanup repair predeclaration

Date: 2026-08-23

Status: `PREDECLARED / NO REPAIR MODEL OUTPUT / R64 SEALED`.

This is an ordinary offline regression repair for the terminal HOLD at commit
`12c4a723ae5a06e056f152b8bca33abe848f265d`. It permits only the two
source-bound conditional-phase predicates identified below, followed by local
complete-mask regression tests. It provides no CUDA, range, search, provider,
network, account, deployment, or submission authority.

## Frozen diagnosis

The failing D32 fixture is nonce `154123680082395`. The unchanged local
evaluator emits clean conditional-phase shots `{304, 4238, 7668, 8833}`;
the combined model emits `{304, 4238, 7668}`. Evaluator attribution binds shot
8833 to operation `12,901,960`, R/Hmr ordinal `1,938,318`, at
`src/point_add/trailmix_ludicrous/arith.rs:1471`.

The exact operation-site trace contains two R/Hmr events at that source line:

- op `6,005,361`, R/Hmr ordinal `907,730`;
- op `12,901,960`, R/Hmr ordinal `1,938,318`.

The frozen phase extractor admits 3,964 sites but omits this source line. The
exact local `PP_PROFILE=1` phase table places the first event inside
`tlm_coord_add3x` and the second inside `tlm_coord_rsub_final`. The profile
stderr SHA-256 is
`6c1b297f88ebf122f3c87b216577885012903b680e6dba01a1b126b429145dad`.
It reports Q1272, 12,904,547 profiled operations before the 96-operation
declared tail, classical mismatch zero, phase zero, and dirty qubits zero.

## Predeclared correction

No classical arithmetic function may change. The only permitted model change
is to admit the two `arith.rs:1471` sites and emit their source predicates in
operation order:

1. `tlm_coord_add3x`: preserve `anc`, the carry of the original 256-bit
   `three_x + denominator` addition; after its controlled low-window repair,
   emit `anc != (result < three_x)` over all 256 bits, matching the call to
   `controlled_lt_msbs_conditional(..., k=256, anc)` in `mod_add_exact`.
2. `tlm_coord_rsub_final`: preserve `anc`, the carry of the original
   `(~reg) + (coord + 1)` addition; after its controlled low-window repair,
   emit `anc != (result_top19 < (coord + 1)_top19)`, matching the call to
   `controlled_lt_msbs_conditional(..., k=19, anc)` in
   `mod_rsub_vented_loaded`.

The extractor must require exactly two line-1471 sites, retain the prior four
source-family counts exactly, and regenerate a 3,966-site schedule containing
the same 1,938,616 R/Hmr operations. Any different count, location, predicate,
classical output, or schedule shape is terminal HOLD.

## Immutable inputs

- repair branch base: `12c4a723ae5a06e056f152b8bca33abe848f265d`;
- structural source: `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- operation stream SHA-256:
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- operation-site trace SHA-256:
  `f2f0f99d096027299460d9a82c16d3714c9684564d10f13f6dcbbac2b3e92833`;
- prior phase metadata / header SHA-256:
  `59c177b5b43bf27eba1ee6758a7c1cea07f0eef5aa9b0c2a27dfe05301c6657d` /
  `de37d6004427082c345004d1225d0f877abfe9597ac969df228b77eb915fe42f`;
- unchanged local evaluator source / binary SHA-256:
  `26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98` /
  `90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`.

## Frozen corpora and terminal gate

All prior corpora remain frozen: inherited singleton, H64, D32, V64, and F32.
The fresh R64 SHA-256 is
`c0253a53113952659308bdc32c0245160b30093fc3ef4e7925cfbd02332a186b`.
It was deterministically derived before any repair output from the low 48 bits
of `SHA256("q1272-phase8833-repair-fresh-r64-v1\\n" || u32be(i) ||
u32be(counter))`, for `i=0..63`, incrementing `counter` only on collision,
then sorted. It is unique, canonical, below 2^48, and disjoint from inherited,
H64, D32, V64, W64, and F32.

Terminal PASS requires byte-complete classical equality between the qualified
classical model, repaired combined model, and unchanged evaluator, plus
byte-complete `raw_phase & ~classical` equality between repaired model and
evaluator, on all 257 frozen rows. It also requires Q1272, 9,024 shots,
ancilla zero, deterministic repeats, immutable-input checks, schedule-failure
rejection, malformed-input rejection, and no silent skips. Any mismatch is
terminal HOLD. Generated binaries, schedules, masks, logs, attribution, and
evaluator outputs remain outside Git.
