# lane_t_reduce handoff — Q792 four-hole value-correctness status (2026-09-15 ~13:45Z)

## Verified wins (keep these)

1. **INV16 table fix** (`q793_exit_low.rs`): the shipped table had 5->5 and
   13->11 instead of the true inverses 5->13, 13->5. Proof of the bug:
   - `U16_TERMS` (hand-factored u-decode) match the TRUE map exactly on the
     reachable domain (0 mismatches over 4096 codes);
   - `q792_mod16::inverse_16` (Newton, used by the exhaustive 65,536-lane
     cycle_swap selftest) gives the true inverses and disagrees with the table.
   - Corrected table: `[0,1,9,11,13,13,3,7,0,9,13,3,5,5,7,15]`.
   - Effect: -90,816 structural T per block per traversal (uniform across all
     202 blocks; t-census block 0/50/100/150/200 all identical delta) =
     ~73.4M at Q792. Whole-count: ops 1,369,818,684 -> 1,296,419,964,
     structural_T 820,699,472 -> 747,320,144, peak stays 792.
   - Patch: `runtime/treduce-inv16-fix.patch`.

2. **A24-analog support-gated cargo prune** (`q793_cargo_r02.rs`, flag
   `Q793_CARGO_A_SUPPORT`, default OFF): prune at(252)/at(253) when the block's
   A-support has hi<=252/253; at(254) is the sentinel (never pruned, mirroring
   A24's never-pruned at(255)). t-census block 124: -14,122 T (both copies).
   ~7M structural at Q792. NOT yet whole-stream-verified (see below).

## NOT ready for submission — port has a value bug

Whole-stream (64-shot, independent seed) fails 64/64 classical with
`dirty_ancillas=0` and NONZERO phase in every configuration tried:

| config | peak | ops | phase | failures |
|---|---|---|---|---|
| buggy INV16, h0=w2[257], borrow ON | 792 | 1,369,818,684 | 0xbdc9cb0a280c5f49 | 64 |
| INV16 fixed, h0=w2[257], borrow ON | 792 | 1,296,419,964 | 0xbdc9cb0a280c5f49 | 64 |
| INV16 fixed, h0=w1[254], borrow ON | 792 | 1,296,419,964 | 0xbcad2abde7a3ca04 | 64 |
| INV16 fixed, h0=w2[258], borrow ON | 792 | 1,296,419,964 | 0x0a0351029c33dc22 | 64 |
| INV16 fixed, h0=w2[257], borrow OFF | 793 | 1,295,882,110 | 0x5d60bef05e2e0278 | 64 |

Conclusions:
- INV16 is necessary but not sufficient.
- The terminal-home choice is NOT the root cause (all three candidates fail;
  lane-0 outputs identical across variants, others vary).
- Q792_QUOTIENT_TOP_BORROW is exonerated (borrow OFF fails the same way at
  peak 793).
- Nonzero phase + clean ancillas points to a STRUCTURAL R/Hmr imbalance in the
  port (value corruption alone cannot unbalance R/R^-1 phase cancellation).
- Prime suspect region: the chart-reader integration — transfer/Aupdate
  `length_xor` protected-helper substitution, `xor_u16`/`xor_r16` call sites
  (`q793_transfer.rs:124`, `q793_Aupdate.rs:98`) — the exact piece the window-1
  PRO closeout flagged as blocked ("Aupdate/transfer/exit_low embedded charts").

## Artifacts
- `lanes/laneT-reduce` branch `lane-treduce` @ 5d916e83 (INV16 fix + prune +
  probe commits; also contains the w2[257] terminal-home fix identical to
  lane_refreeze's and a marker-leak trap in `B::push_op`).
- Binaries in `runtime/`: build_circuit-treduce-{fixed,w1254,w2258,noborrow}.bin.
- Logs in `runtime/`: treduce-q792-{fixed,w1254,w2258,noborrow}-stream.log,
  pro-q792-stream-w2fix.log (PRO's 64/64), refreeze-*.log.
- `runtime/treduce-inv16-fix.patch` (INV16-only, applies to lane_refreeze).

## Recommended next window
1. Rebuild lane_refreeze with the INV16 fix regardless — it is needed for any
   correct four-hole artifact and is worth -73.4M.
2. Debug the R/Hmr structural imbalance: instrument `Simulator::apply_iter` to
   record R/Hmr op positions and the XOF stream position, and compare the
   OFF (phase-clean) vs four-hole R op sequences.
3. Then re-verify the terminal home with a whole-stream (w2[257] is the most
   likely per the port's re-homing conventions).
4. Only then bake + full 9024-shot + submit. Do NOT submit the current
   four-hole artifact: it fails the trusted evaluator's correctness check.
