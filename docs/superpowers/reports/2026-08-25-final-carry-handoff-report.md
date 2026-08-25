# Final-Add Carry-to-Fold Handoff — REFUTE Correction

## Current status

`ALIVE_GLOBAL_MIXED_ENCODING_GAP`

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

## Constructive-extension checkpoint

The independent primitive-gate oracle now exists in
`src/point_add/memory/repro/final_carry_gate_oracle.py`. It does not import the
withdrawn arithmetic model. At widths 5 through 9 it executes:

- the `n-2` phase-AND construction on all 992 basis inputs and every independent
  HMR arm, with zero phase or ancilla mismatch;
- a source-shaped delayed-carry forward circuit, actual inverse gates, and HMR
  cleanup on 698,368 cases, with zero value, restore, phase, or ancilla mismatch;
- the four fold digits `-1,0,+1,+2` on 3,968 cases, including the distinct
  negative orientation, with zero value, selector, phase, or ancilla mismatch.

Nine nontrivial mutations independently turn GREEN to RED: dropping the
terminal CCZ, changing a prefix control, skipping a prefix HMR correction,
dropping the carry top restore, changing the carry HMR control, skipping the
delayed inverse, dropping the fold terminal carry, reversing the `-f`
orientation, and skipping a fold HMR correction. These are valid primitive
oracles, not a composed handoff candidate. No exact 54/53 candidate miter or
Rust diff exists, so they cannot support ADMIT.

### Source-bound information and synthesis results

- Every current local selector arm has an exact canonical secp256k1 witness.
  The fold operand functions have rank 3; operand plus first carry has rank 4;
  adding the raw final carry has rank 5. Divide has no affine wire reclaim and
  multiply has at most one. This closes zero-T affine publication only, not a
  nonlinear selector code.
- Exhaustive widths 5 through 9 show that raw and adjacent-difference carry
  banks each add their full width in Boolean-function rank modulo the actual
  live source and finished-sum wires. The exact transfer executes 513
  canonical coordinate-axis witnesses plus zero/all/alternating/every-unit
  carry words: 131 patterns for the 127-bit divide chunk and 132 for the
  128-bit multiply chunk, with zero canonical or recurrence mismatch after
  the multiply cell's actual left shift. These witnesses eliminate the live
  interface coefficients and then each carry coefficient. This is
  information/lifetime rank, not nonlinear cost by itself.
- A single dirty product `xy` cannot become an independent fold product `pa`
  with one affine-conjugated product update: all 4,096 affine control pairs
  fail, while clear-then-create succeeds with two.
- For two dirty and two fold products, the earlier envelope-preserving search
  found no two-gate path. A new search removes the envelope assumption at
  quadratic degree: all 10,795 decomposable quadratic forms on eight variables,
  all six dirty-to-fold graph isomorphisms, and 64,770 three-generator coset
  candidates contain zero three-generator solution. Four pure clear/create
  generators work. This is exact for two quadratic banks, but it is not a
  larger-bank direct-sum or HMR-assisted theorem.

### Economics and unresolved loophole

For the three-saved-CCX route, an intentionally impossible-favorable relaxation
credits 18 remaining phase gates with 43 unretained carry factors and grants one
free selector wire at both sites. Even then 1,170 cells need at least one host
release/reuse. The checked separable/source-shaped dichotomy charges one
depth-one event on each such cell: 585.0 average T added against a 574.5 ceiling,
so this subfamily is capped at 1,489.5 net and is killed.

That is not a whole-family verdict. At four saved CCX, the same one-event-per-
affected-cell argument still leaves more than 1,500 net, and no checked theorem
yet scales the extra cost with every reused rank. Higher-degree, larger-bank,
globally mixed nonlinear codes and HMR-assisted amortization therefore remain a
real loophole. An earlier 82.95-second “no three-gate path” result was restricted
to intermediates inside the dirty-plus-fold envelope and is superseded; it is
not used here.

Current status is consequently `ALIVE_GLOBAL_MIXED_ENCODING_GAP`. There is no
candidate sequence, no Rust modification, no exact candidate census, no ADMIT,
and no defensible whole-family HARD_NACK. The next local gate is either a
larger-bank/HMR direct-sum proof with source transfer and full savings sweep, or
an explicit globally mixed construction that then enters the exact 54/53 miter
and Rust/Q/T gates.
