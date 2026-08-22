# Q1275 peak-cut canary

Updated: 2026-08-23

Status: `VERIFIED_PACKET_READY`

## Frozen scope

- Base source: `940e34acbc9cdc9ac497f67eea40db80551d1f7c`.
- Branch: `research/postwin-q1275-canary-940e34a`.
- Final target defaults: `SUB4_PP_PEAK=1275`,
  `SUB4_SQUARE_LADDER=245`, `SUB4_PP_R1=342`, and
  `SUB4_PP_R2=625`.
- The promoted tail nonce remains unchanged. No nonce is baked by this lane.
- No remote worker, provider, spend, submission, active packet, or other
  worktree is in scope.

## Gates

- Fresh isolated release build and fresh `ops.bin` emission.
- Record exact operation count, SHA-256, MD5, Q, average executed T, total
  executed T, and trusted 9,024-shot classical/phase/ancilla counts.
- Bind the CPU predictor calibration to the exact target stream fingerprint.
- Compare at least 16 nonces, including low-count boundaries, against the
  unchanged trusted evaluator; require zero predictor undercounts and zero
  overcounts.
- Do not push unless every milestone is verified.

## Superseded target

- The R2=620 stream (`ac5f5a80...`, 12,954,520 ops) was calibrated locally,
  but is not deployable. Structural multi-draw evidence selected R2=625.
- No R2=620 deployment artifact or remote route may be used.

## Verified outcome

- Fresh target: 12,953,930 ops, SHA-256
  `83b66b7ef8e5080924f96faa0970a625044eb9d1e58fa2f6a75d162a3bb850d8`,
  MD5 `7464046369b46251d49e5ee03af881c5`, Q1275, 961900 bits.
- Inherited nonce `176078461220`: exact total T `8,292,747,196`, average
  `918,965.779698581551`, rounded T `918,966`; trusted
  classical/phase/ancilla `14/11/0` across all 9,024 shots.
- Current cc20 CPU predictor: inherited classical `14` exact; fresh trusted
  fixture corpus `16/16` exact, spanning counts 2 and 4 through 18, with
  `under=0 over=0`.
- GPU semantic state digest: `6403052ff4377d60`.
- Target-host CUDA binary SHA-256:
  `16950112cfa857272f4f1b6cf67f6d2e30df1b1c44e03ab0f794af173c7f6145`.
  It matched all 16 fixtures under comb8 and comb16 and refused four wrong
  stream controls.
- Durable evidence: `.lane/CALIBRATION.md`, `.lane/GPU_CANARY.md`, and the
  reproducible `.lane/GPU_PORT_Q1275.patch`.
- Generated ops, logs, results, and local binaries remain outside Git.

## Verification notes

- Fresh locked release build: pass.
- Fresh op emission and exact SHA/count/Q check: pass.
- Unchanged trusted evaluator, inherited plus 16 isolated full-shot fixtures:
  pass.
- `git diff --check`: pass.
- The repository-wide `cargo fmt --check` reports extensive formatting drift
  in untouched source.
- The `build_circuit` cfg-test target does not compile because its untouched
  legacy tests reference removed constants, helpers, and simulator methods
  (165 errors). The release binaries used by the challenge compile and ran;
  no unrelated test-suite repair is included in this packet.

No fleet route, active packet, remote worker, provider, spend, submission, or
nonce default was changed by this lane.
