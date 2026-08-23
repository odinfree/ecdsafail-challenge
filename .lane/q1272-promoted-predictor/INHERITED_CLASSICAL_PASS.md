# Promoted Q1272 inherited classical-mask gate

Date: 2026-08-23

Verdict: `INHERITED_23_OF_23_EXACT / SCAN_DISABLED / H64_UNOPENED / HOLD_PROVIDER`.

## Bound target

- structural source: `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- source tree: `fe77bddfb49b426312b1cca3d009b150cd06fd89`;
- terminal evidence: `41dd0b4508527081b8d24255adf0579389f02453`;
- exact environment: `SUB4_PP_FOLD_SELECTOR_EVICT=1`,
  `SUB4_PP_PEAK=1272`, `SUB4_SQUARE_LADDER=242`, with every other external
  `SUB4_*` input absent;
- operation count: `12,904,643`;
- operation SHA-256:
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- inherited nonce: `65700024945645`;
- unchanged full result: Q1272 / T914783.521 / classical-phase-ancilla
  `23/8/0`, first classical mismatch shot 292.

The operation artifact used for the comparison was rebuilt in this worktree
from the exact committed source and reproduced both the count and SHA above.
It remains outside Git.

## Source-semantic repair

The old selector predictor was only a mechanical donor. Its linear 700-round
geometry predicted 17 faults on the target stream. The promoted predictor now
uses the exact target's 696/696 depths, replay fold 54, endpoint fold 20, flag
compare 22, chunk compare 20, and default-on rescaling through the target's
700-entry sampled width table. The table is parsed from the exact
`pingpong_div.rs` text compiled into the binary; it is not duplicated as an
independent constant. Rescaled indices 700 through 703 take the same hard
floor of width 8 as the circuit source.

The qualification source SHA-256 is
`2d016070a93a5966c5a163a6242b27ef8264176c76c72448ba50027b70465890`.
The local arm64 release binary SHA-256 is
`1ce7b22c1ed1a4d55620ccf5daeed110cdb7b0f6de3ce85b5de93fcc86cb7ba8`.
The binary refuses every external `SUB4_*` variable except the three exact
settings above and exits 2 on any range request.

## Independent complete-mask comparison

The trusted evaluator source was unchanged except for observability-only
instrumentation that retains and prints every classical mismatch index and
suppresses result-file writes:

- original evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- instrumentation patch SHA-256:
  `15943baf5815f36188a8406b7a080c8b446f856a9337d8046eafe363752c6e4f`;
- instrumented evaluator source SHA-256:
  `4e87d08dc10cb49ea46410c09796239601ba529deac87d0dc45d641337ede9fc`;
- instrumented evaluator binary SHA-256:
  `37081d949bf34f185023098e74393a9014b96853633646288a90f1538663580e`.

The evaluator and predictor were run independently and their sorted complete
9,024-bit classical sets were compared in memory. They are byte-identical and
contain exactly these 23 indices:

`292, 925, 1601, 1765, 3094, 3415, 4418, 4546, 4897, 5038, 5165, 5246, 6089, 6515, 6606, 6692, 7209, 7370, 7468, 7956, 8561, 8736, 8954`.

Canonical newline-delimited index SHA-256:
`c46041ff454200ba4d2ab3cffcefb2b118e4afd839f674431762b24da37f8848`.
The predictor's 141-word little-endian mask-hex SHA-256 is
`063e4042188c87eef79a53275844ee718144e93a89957f5156603e9ab2cf83c1`.
The direct comparison run produced evaluator stdout SHA-256
`35d0e467bc9a1566082985d5b6346d2c6e888f11821ee203cb3cb614b8906f29`
and predictor stdout SHA-256
`e137d9d4f4ec455830a7cada3fe508ca6f302e3ff0982f660a46d1c5d9dee428`.

Two independent predictor repeats were byte-identical; both retained the same
predictor stdout SHA above. The SHAKE256 empty-string KAT, two product-register
square KATs, and a full point-add KAT passed. Missing required environment,
wrong required value, extra `SUB4_*` input, and range invocation each exited 2.

## Gate boundary

This checkpoint proves only the inherited classical mask. It does not claim
H64, D32, conditional phase, CUDA parity, a hunt range, a provider action, or a
submission. Raw phase remains diagnostic on classically dirty shots. The next
classical gate is sealed H64 complete-mask equality, followed by a predeclared
disjoint holdout. Generated operations, binaries, raw logs, and masks remain
outside Git.
