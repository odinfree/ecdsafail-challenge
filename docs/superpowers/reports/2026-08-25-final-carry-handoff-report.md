# Final-Add Carry-to-Fold Handoff — REFUTE Correction

## Current status

`ALIVE_DIRTY_HOST_CONJUGATION_GAP`

Commit `e885a164fa92b3c33ae5da7fb89327d8b1700e09` claimed
`HARD_NACK_CARRY_HANDOFF_FAMILY`. Independent REFUTE sustained multiple faults,
so that terminal verdict and its constructive-cleanliness claims are withdrawn.
This correction is deliberately nonterminal and is not an admission claim.

The exact binding remains:

- source commit `522d00296ab014b0f4d128915b53851516f17f4d`;
- source tree `eab2326ce33549eceeb5c10aa64eae33f148b0ac`;
- active `src/point_add/pingpong_div.rs` blob
  `f4399563b1fe8c4beee568027ebf52df252e7555`;
- runtime rounds 694 divide / 693 multiply;
- fold widths 54 divide / 53 multiply;
- 692 divide plus 691 multiply cells;
- Q1266 exact-source baseline.

## Sustained findings

1. The former reduced baseline/candidate “miter” had no independent oracle. It
   reused the same arithmetic recurrence on both sides, checked injectivity
   instead of executing a candidate inverse, and reported
   `candidate_final_phase=0` as a literal. Its 1,040,532-case and phase-count
   totals do not certify a construction and have been removed from the evidence
   packet.
2. The global `k=237` suffix bound omitted the already-computed incoming carry
   of the final chunk. Retaining that boundary reduces the unresolved cleanup
   predicate to the unretained portion of the final chunk, not all 256 bits.
3. The claimed 21-CCX optimality was a value-circuit XOR/AND argument, not a
   phase-circuit lower bound. A phase `AND_n` may use a prefix of `n-3` CCX, a
   terminal CCZ, and measurement uncompute; exact emitted and average-T
   accounting must replace the withdrawn bound.
4. The divide/multiply collisions cover the source's current four selector
   wires only. They do not exclude a broader reversible selector code, so R2 is
   reopened.

## Corrected boundary arithmetic

For a final chunk of width `w`, saving three of the source comparator's 21 CCX
leaves an optimistic 18-nonlinear-gate cleanup budget. If the incoming final-
chunk boundary is retained, the unresolved synthesis target needs only
`w-18` top predecessor carries plus that one boundary—not 237 global
predecessors.

Recomputing this relaxation over every exact census row gives:

| Quantity | Corrected value |
|---|---:|
| Cells fitting Q1266 under free fold-host replacement | 1,383 / 1,383 |
| Divide / multiply fitting cells | 692 / 691 |
| Optimistic peak range | Q1221..Q1252 |
| Gross average T if three CCX/cell are realized | 2,074.5 |
| Maximum added average T while retaining a 1,500 net cut | 574.5 |

This is not a construction. Without fold-host replacement, retained suffixes
still overlap the fold ladder and miss Q. The live question is whether the
dirty retained boundary/top-suffix state can be reversibly conjugated into the
clean fold-carry hosts, used by the width-54/53 folds, and restored with exact
classical value, every HMR phase arm, inverse cleanup, and all ancillas clean at
an added average-T cost no greater than 574.5.

## Evidence retained as observations

- The exact operation artifact remains 12,553,305 operations and SHA-256
  `a4995dc4be4b7b314853d379941141b3b5753110412c07e8a2bc5d097d218ed1`.
- The 1,383-cell static census and its literal-retention peaks remain valid for
  the literal all-carry implementation; they do not lower-bound dirty-host
  conjugation.
- Exhaustive 22-bit secp embeddings still demonstrate the current four-wire
  selector collisions and the `AND22` restriction. They are observations, not
  whole-family information or phase-cost lower bounds.

## Reopened routes and next gate

| Route | Corrected state | Required next evidence |
|---|---|---|
| R1 retained suffix / fold conjugation | `ALIVE_WITH_GAP` | Actual dirty-host reversible synthesis and real lifetime/cost accounting |
| R2 broader selector publication | `ALIVE_WITH_GAP` | Search beyond the current four wires with an independent executable oracle |
| R3 former lower-bound closure | `REFUTED` | Replaced by measured phase-gadget alternatives, not repaired by assertion |

The next gate is an independent gate-level forward/inverse simulator with
symbolic measurement-phase tracking and nontrivial mutations that provably turn
GREEN to RED. Only a surviving construction may proceed to an exact Rust diff,
locked offline build, and static proof of Q<=1266 plus at least 1,500 net
average-T reduction. No provider or full evaluator is authorized before that
local admission gate.
