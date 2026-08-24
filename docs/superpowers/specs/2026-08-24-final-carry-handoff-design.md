# Final-Add Carry-to-Fold Handoff — Resolution Contract

## Status and authority

This is a bounded local research contract. The sole ball owner is the Codex
carry-handoff lane. It grants no provider, network/fetch, push, submission,
official-artifact, or full-evaluator authority. All other worktrees and
unrelated files remain untouched.

## §1 Definitions

- **Exact source** means commit
  `522d00296ab014b0f4d128915b53851516f17f4d` with tree
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac` in this isolated worktree.
- **Candidate environment** means `SUB4_PP_ROUNDS=694` and
  `SUB4_PP_ROUNDS_MUL=693`, with the exact source's other promoted settings:
  canonical-residue frame, table plus repair width schedule, divide fold width
  54, multiply fold width 53, endpoint fold width 26, replay flag compare 22,
  replay chunk compare 22, and no schedule, fold-window, round, or other config
  change.
- **Divide site** means `signed_mod_add_pm_halve_fused`; **multiply site** means
  `signed_mod_double_add_pm_fused`. A result must cover their distinct sign and
  parity orientations independently; success at one does not transfer to the
  other by assertion.
- **Final carry** means the last-chunk output produced by
  `add_chunked_measured_late_carry`, including its exact last-chunk allocation
  time, its use by selector algebra and `fused_fold_maskfree`, and its final HMR
  plus `cmp_lt_phase_conditioned` cleanup.
- **Permitted handoff family** may rewrite only final-chunk carry publication
  and the carry's selector/fold/cleanup interface. It may retain a top-carry
  suffix, publish a reversible selector code, or conjugate dirty carry storage
  into fold storage. It may not change the arithmetic schedule, truncation
  windows, round counts, width table/repair, frame, unrelated cells, or the
  mathematical tail semantics.
- **Correctness** means equality to the exact-source baseline for the complete
  classical map and every measurement-conditioned phase arm, with all temporary
  qubits clean after both forward use and inverse cleanup. Equality is required
  over maximum redundant input ranges admitted by the two cells, not only
  canonical residues or a chosen nonce.
- **Executed Toffoli** means the emitted CCX/CCZ cost weighted by all active
  quantum measurement conditions. In particular, each CCX in the current
  22-bit flag comparator has condition depth one and contributes 1/2 expected
  executed Toffoli. There are 692 divide cells and 691 multiply cells at
  694/693, hence 1,383 cells total.
- **Peak Q** is the builder's maximum simultaneous active-qubit count. Every
  retained carry and dirty host is charged for its full lifetime. Releasing one
  wire and allocating another later is not evidence of coexistence-free reuse;
  the active timeline and owner/site census must prove it.
- **Reduced miter** means exhaustive phase-aware discovery at widths 5 through
  9, across both orientations, every sign/parity/doubled-out/add-out arm, every
  HMR measurement arm, maximum redundant values, and forward plus inverse
  cleanup. It can falsify a route but cannot admit it.
- **Exact miter** means a source-bound phase-aware executable checker at the
  production divide/multiply fold widths 54/53 and flag width 22, exercising
  forward plus inverse cleanup and explicit exact secp256k1 transfer witnesses.

Degenerate cases include zero carry, parity-zero overflow, carry propagation of
length zero or the full retained suffix, empty selector classes, all-zero and
all-one top windows, dropped final carries/borrows, and both HMR outcomes.

## §2 Objective — forced resolution

Resolve the permitted family with exactly one terminal outcome:

- **(A) `ADMIT_CARRY_HANDOFF_TO_FULL_EVAL`:** provide a concrete exact-source
  Rust diff, executable reduced and exact miters including HMR phase and inverse
  cleanup, a locked offline build, a static lifetime/cost census proving
  `Q <= 1266`, and at least 1,500 average executed-Toffoli net reduction at
  694/693 after every added nonlinear operation and cleanup is charged.
- **(B) `HARD_NACK_CARRY_HANDOFF_FAMILY`:** provide a concrete rank,
  information, cost, or lifetime falsifier that covers both exact sites under
  the permitted family. The evidence must independently close the source
  inventory, truth-table/information transfer, and reversible-synthesis or
  lower-bound routes.

No third outcome settles this contract.

## §3 Working posture

Assume for search purposes that a complete resolution exists and is findable.
Keep incompatible routes alive until killed by a predeclared falsifier. This
posture governs effort only; it never licenses an unverified verdict.

## §4 Ban list

None of these settle the contract, alone or together:

- count-only or emitted-only savings without executed-control accounting;
- deleting, weakening, narrowing, or silently moving a flag comparator or HMR
  phase repair;
- a classical-only proof or checker;
- widths 5 through 9 without exact 54/53 and secp/source transfer;
- any construction whose measured peak exceeds 1266;
- nonce, redraw, sampled-only, prefilter, or phase-blind evidence;
- any schedule, fold-window, round, width-table/repair, frame, or config change;
- signed-frame or one-normalizer rebranding;
- a projection without an actual exact-source diff and executable checker;
- savings that omit selector construction, dirty-host conversion, HMR repair,
  inverse cleanup, or changed condition depth;
- a result for only divide or only multiply;
- a collision candidate, informal lower bound, or synthesis sketch without a
  complete source-transfer verification.

## §5 Traps and forbidden moves

- **Parity-zero overflow:** at the divide site the low correction selectors are
  independent of overflow on parity-zero arms. They cannot silently stand in
  for the HMR phase bit.
- **Dirty phase:** a value-correct construction can still leave a relative phase
  on the raw carry, retained suffix, selector ancilla, or fold carry.
- **Orientation asymmetry:** divide uses width 54 and
  `not_sign_and_parity`; multiply uses width 53, `doubled_out`, and
  `odd_correction`. Their cleanup formulae are not interchangeable.
- **Last-chunk lifetime:** the baseline allocates the final carry only when the
  last chunk starts. Retaining predecessor carries can overlap the selector and
  fold peaks even when aggregate allocation counts look neutral.
- **Dropped information:** discarded carry/borrow states, aliasing a dirty host
  as a clean fold target, or assuming the result identifies a selector can make
  a non-injective transformation appear reversible.
- **Phase-blind prefilter:** classical mismatch counts or K ranking do not test
  HMR phase.
- **Truncated-vs-ideal confusion:** preserve the exact source's 22-bit HMR
  repair semantics; do not substitute either no repair or an ideal 256-bit
  comparator.
- **Economics rounding:** saving two depth-one CCX per 1,383 cells is only
  1,383 average T and misses the target. A uniform route must save at least
  three with sufficiently small added cost.

## §6 Route registry and review rules

Only the sole owner performs discovery or implementation. A separate worker is
reserved for a terminal REFUTE audit after the evidence packet exists; it may
not co-own or duplicate discovery. Registry states are `ALIVE`,
`BLOCKED(reason)`, or `KILLED(falsifier)`. A killed route is not restarted
without new evidence.

Initial registry:

| ID | Family | Initial state | Predeclared falsifier |
|---|---|---|---|
| R1 | Retained top-carry suffix conjugated into the fold ladder | ALIVE | No phase/value-clean reversible conjugation at 5..9 that transfers exactly to 54/53; or exact peak/cost misses §2(A) |
| R2 | Local HMR then quotient carry publication into a minimal selector code | ALIVE | Permitted-interface collision with equal published state but different required HMR phase or inverse cleanup, checked separately at both sites |
| R3 | Comparator/lifetime lower bound and dirty-host synthesis | ALIVE | Explicit baseline-width synthesis below the derived nonlinear-cost bound |

R1 is tried constructively; R2 is the cheapest information falsifier; R3 must
either synthesize a surviving dirty-host map or prove why the baseline's
comparison/lifetime cost cannot be cut enough.

## §7 Exit condition

Before `HARD_NACK_CARRY_HANDOFF_FAMILY`, absent an immediate exact falsifier,
all three independent evidence axes must close:

1. exact-source call, operation, lifetime, peak-owner, and gross/net T inventory;
2. exhaustive reduced truth-table/information-rank analysis plus exact secp and
   width-54/53 transfer for both sites;
3. reversible synthesis search or a checked nonlinear-cost/lifetime lower bound.

Before `ADMIT_CARRY_HANDOFF_TO_FULL_EVAL`, all §2(A) artifacts must pass from a
clean state: focused RED/GREEN tests, reduced miter, exact miter, actual Rust
diff, `cargo build --locked --offline`, and static operation/condition-depth and
peak-lifetime census at exactly 694/693. No full evaluator is run in this lane;
ADMIT opens that later gate but does not claim evaluator validation or
promotion.

The terminal packet is then given to an independent worker instructed to
REFUTE it using every §5 trap. One sustained refutation returns the affected
route to `ALIVE-with-gap`; it cannot be ignored. A terminal commit contains only
the bounded allowlist and reports deterministic artifact hashes and exact test
commands/results.

## Architecture and data flow

1. A source-binding/inventory layer extracts the two formulas, widths, call
   counts, condition depths, and active-wire intervals from the exact source.
2. A pure Python miter models baseline and candidate cells as value plus phase
   transformations. It exhausts widths 5..9 first and emits explicit collision
   or synthesis certificates.
3. An exact-width checker reuses the same equations at 54/53 and the exact
   secp256k1 fold constant; exhaustive small width never substitutes for it.
4. Only a surviving construction is translated to an env-gated Rust diff. A
   static builder census measures peak Q and executed-control economics before
   any full evaluator gate.

Failures are fail-closed: a binding mismatch, unhandled arm, dirty ancilla,
phase mismatch, nondeterministic artifact, missing exact transfer, or budget
miss prevents ADMIT and remains in the route registry.
