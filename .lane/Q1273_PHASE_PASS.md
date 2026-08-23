# Q1273 conditional-phase CPU qualification

Verdict: `PASS_PHASE_17_OF_17 / COMBINED_HUNT_HOLD`.

The source-specific CPU predictor reproduces every complete conditional-phase
shot set in the inherited stream and independently frozen D16 corpus. This is
only the contract `clean_phase_mask = phase_mask & ~classical_mask`. A final
survivor requires `classical_mask == 0 && clean_phase_mask == 0`. Raw phase on
classically dirty shots and CUDA phase parity are not claimed.

The combined classical-plus-phase filter is **not hunt-compatible**. The
original classical model has one predictor-only shot in D16. Such a false
positive can discard a real clean nonce, so the model remains on HOLD despite
the exact phase result.

## Source and identity bind

- structural source commit:
  `093d85d64de87aa5006a94868172f642daacf136`;
- structural tree: `f6fd9d8b151a84fd886835ff3a818d3c1c9ef072`;
- phase predeclaration: `b6911df`;
- operation count / SHA-256: `12,933,805` /
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- predictor checkpoint digest: `2148e09f4c4293b2`;
- geometry: Q1273, 9,024 shots, zero ancilla-garbage batches;
- inherited nonce: `100000045835813`;
- inherited full result: `12 / 12 / 0`;
- inherited receipt:
  `/Users/olifreuler/ecdsa-ops/q1273-redescent-093d85d-full9024/RECEIPT.md`;
- receipt SHA-256:
  `f65aad34d8392d2c273349aa06f50beb8a8cc0a01c04892e801455081840ce17`;
- inherited average T / strict rounded ceiling: `917103.815 / 917245`;
- trusted evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`.

The CPU `identity` mode binds the source commit, exact operation count and
SHA-256, predictor digest, phase schedule digest/counts, 9,024 shots, and the
conditional/non-claim contract in one deterministic row. Its output SHA-256 is
`b47a1e32e75278c76be0380e6c3a9a18aa1e6344e56cb31a36d9ca4f0e1ca78a`.

## Source-derived schedule

An exact source trace contains `1,942,962` R/Hmr stream words. The phase screen
binds 3,983 measured-boundary predicates:

- 2,590 chunk-boundary carries at `pingpong_div.rs:1547`;
- 696 divide replay flags at `pingpong_div.rs:1783`;
- 694 multiply replay flags at `pingpong_div.rs:1898`;
- three arithmetic-shell subtract carries at `arith.rs:1501`.

The complete schedule ledger SHA-256 is
`a4043530337b91e97d7a42dde2aff7e5a967a0b820ad1a9a120b3c366d7a5294`.
The generated C++ header SHA-256 is
`4249864aca9e2928a33865ea086b99ef8ecccc9eb596ba4c3e57468ba88d25e5`.
The committed generator reproduces both byte-for-byte and has SHA-256
`83bfa142f2cf546ea5673de424597bf26ed3a57db0173d2b177a009ad9f8e966`.

## Independent oracle and exact phase result

The two-pass oracle uses the unchanged Simulator for full truth and a separate
operation replay for phase attribution. It patches the final 96-operation
nonce image before both Fiat-Shamir hashing and simulation.

- oracle source / binary SHA-256:
  `26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98` /
  `90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`;
- operation-site trace SHA-256:
  `ddce38817e1fccbf26f1f1ec0d000df28a18b2945b4ffd0a38b3cacbb69de6d5`;
- inherited plus D16 fixture-ledger SHA-256:
  `e148f24d99ae45b3c6930a33d49173fd31b2c236593d98375956077b3feb4d1b`;
- D16 nonce formula: `730000000000 + i * 10000103`, `0 <= i < 16`;
- D16 nonce-list SHA-256:
  `95cdff3d994ed74866e87aff7822d8d8aa8091e74ed5a2842c2fca6732afd3b0`;
- inherited-plus-D16 nonce-list SHA-256:
  `e72d277e87af6c2d01687df89c4254405e98313742e0af51e2004de953db55d2`.

The fixture ledger contains every sorted classical and clean-phase shot set,
not diffs. Across its 17 rows the oracle reports 244 classical, 200 raw-phase,
and 87 conditional clean-phase shots. The CPU result is complete-set exact
`17/17`; inherited clean-phase set `{509,873,1748,3235,4972,5550}` has
SHA-256
`7b4bc204712ca6c7dfde80725f68fd9d3da6036f1bb2d4f4a39bc826a6a2226c`.

The corrected-tail negative is source-bound: using the inherited tail while
labeling nonce `730000000000` reproduces the inherited `12 / 12 / 0` masks,
not the patched D16 fixture. Negative stdout SHA-256:
`55e28dd04b2220d21c017e2510138e747c089dadaa5d499e96a0bf376081970b`.

## Qualification gates

`verify_phase_cpu.sh ops.bin` passed:

- exact source/count/SHA/digest identity;
- deterministic schedule regeneration;
- SHAKE256 known-answer tests;
- every complete inherited-plus-D16 conditional-phase set (`17/17`);
- deterministic inherited stdout/stderr/order/hash;
- wrong magic, wrong operation count, same-count wrong SHA, wrong predictor
  digest, and wrong phase schedule rejection with empty stdout;
- malformed, non-canonical, negative, overflowing, and out-of-range nonce
  rejection;
- disabled scan mode.

The qualified local CPU binary SHA-256 is
`1c42436b1fa3caafe593a4d3ddcc4fa4af4ed94bed997cfb13e3c8c31c61833d`.
Binaries and run logs remain outside Git.

The phase-extended CPU was also compared byte-for-byte against the balanced
classical H64 packet. It preserves all 64 complete classical masks (`64/64`,
870 faults), index-mask SHA-256
`9c1c9cfb0dc7057e8ea1aafbd55c42382e9c4eeabab0d13fe80d18d98c899f46`,
and cause-mask SHA-256
`eb3193ffefa76c5572006878fec23ca83f8d83737db49cd0d4c2cbceeb99a0b6`.
The H64 evidence and terminal HOLD documents have SHA-256
`98203721a0d413d11731af2527da4815fe1fceec4ab459a3bd01fae75769e7bf`
and
`e2e64995c25328881da463e0d4cc8f93b189b274c7840d3934995d2dc7dd8600`.

## Combined-model HOLD

Classical-oracle equality on D16 is `16/17`. At nonce `730140001442`, the
oracle has 19 classical faults while the original predictor adds shot `6329`,
mask 1 (`PP_F_WALK_DIV`). The extra set and cause-ledger SHA-256 values are
`acfa410b8f687b0a3da4a2d3d1c56eeb247d8300f7a49e4457b058fddf58cacf`
and
`b4ab770cc46b111edab12e4c60083354b2449c0720b0498f5c2e5253fdbecb85`.
The first missed circuit wrap is after round 602, sampled at round 607:
scheduled width 44 versus target signed width 45.

A diagnostic Q1272-style wrapped-output fallback fixes shot `6329` and keeps
inherited plus H64 exact `65/65`, but it is invalid. It erases evaluator-real
nonce `730070000721`, shot `2493`, mask 4 (`PP_F_WALK_MUL`), leaving the same
D16 score `15/16` with a false negative instead of a false positive. The
fallback was not committed. Neither the original model nor that fallback may
filter a hunt.

No provider, GPU, CUDA compilation, range, hunt, submission, or recovered-wave
result was used in this qualification.
