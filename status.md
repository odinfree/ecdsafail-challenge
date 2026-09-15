# lane_t_reduce status — 2026-09-15

## Findings
1. **INV16 table bug (correctness)**: q793_exit_low::INV16 had 5->5, 13->11
   instead of true inverses 5->13, 13->5. U16_TERMS match the TRUE map exactly
   on the reachable domain (0 mismatches); inverse_16() (used by the exhaustive
   cycle_swap selftest) agrees with the true map. Fixed table:
   [0,1,9,11,13,13,3,7,0,9,13,3,5,5,7,15].
   Effect: -90,816 structural T per block per traversal (uniform, all 202
   blocks) = ~73.4M at Q792; whole-count 1,369,818,684 -> 1,296,419,964 ops,
   structural_T 820,699,472 -> 747,320,144.
2. **A24-analog cargo prune** (flag Q793_CARGO_A_SUPPORT, default OFF):
   prune at(252)/at(253) when block A-support hi<=252/253; at(254) kept
   (sentinel). -14,122 T per block-124 t-census (~7M total).
3. **Stream failures**: the four-hole artifact FAILS whole-stream 64/64 with
   nonzero phase for every terminal-home variant tried so far:
   - w2[257] home: phase 0xbdc9cb0a280c5f49 (buggy and INV16-fixed runs).
   - w1[254] home: phase 0xbcad2abde7a3ca04.
   INV16 is necessary but not sufficient; probes in flight (w2[258], borrow OFF).

## Artifacts
- lanes/laneT-reduce @ 37dff749 (INV16 + prune; plus post-commit home probes).
- runtime/build_circuit-treduce-fixed.bin: INV16 + w2[257] + borrow ON.
- runtime/build_circuit-treduce-w1254.bin / -w2258.bin / -noborrow.bin.
- runtime/treduce-inv16-fix.patch: INV16-only patch for lane_refreeze's tree.

## Gate chain state
- whole-count fixed: peak=792, ops=1,296,419,964, structural_T=747,320,144.
- whole-stream: NOT CLEAN (64/64 classical, phase != 0) — do not submit.
