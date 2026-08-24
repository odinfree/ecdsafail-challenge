# Justin Drake small-width liftability audit

**Decision:** GO, with a strict mechanism-lift gate. Use 32/64-bit circuits to discover integer Pareto steps and exact reversible identities. Do not use a raw 64-bit winner as a predictor of the best 256-bit constants.

**Attribution:** Justin Drake proposed the reduced-width autoresearch direction: search smaller adders/circuits so hidden Pareto steps appear faster, then test whether the mechanism lifts. If this lane produces a shipped win, the submission note and campaign ledger should say: **“Reduced-width autoresearch direction suggested by Justin Drake.”** Implementation attribution must remain attached to the actual author/commit; the research-direction credit does not overwrite it.

**Scope:** read-only audit of the public accepted source/history through `67524171baaf568dc3dc606f38515745f70804ff`. No provider action, nonce hunt, or submission.

## Evidence boundary

- Repository: `https://github.com/Layr-Labs/ecdsafail-challenge`
- Audited source: `67524171baaf568dc3dc606f38515745f70804ff`, accepted submission `eaf2ff5d-54c4-41b5-bcb3-3b97e568d61b`, co-authored by `mochimodev`.
- Trusted campaign receipt supplied for that source: Q1267, average executed T `911390.449`, rounded T `911390`, score `1,154,731,130`, 9,024-shot `0/0/0`.
- Adjacent accepted ancestry inspected: `4eb93cb` (`gnuchev`) -> `51c6c31` (`moscowchill`) -> `d919bc6` (`mochimodev`) -> `6752417` (`mochimodev`). Mechanisms below are attributed by source lineage, not inferred private work.
- The current path is hard-coded to 256 bits at `src/point_add/mod.rs:762` and in the product-register square at `src/point_add/trailmix_ludicrous/square/product_register.rs:11`. A small-width lane therefore needs an isolated parameterized kernel harness; changing only `N` is not a valid experiment.

## The control case: this idea has already worked once

The accepted Q1267 source contains an exact low-two-bit comparator reduction in `signed_add_wrapping_sigma_split`:

- The walk invariant fixes the incoming borrow after the first two bits to `source[1]` (`src/point_add/pingpong_div.rs:1237-1243`).
- The comparator starts at bit 2 and emits the final majority phase with three Clifford `CZ`s (`src/point_add/pingpong_div.rs:1244-1290`).
- The same accepted source includes an exhaustive width-3 through width-10 truth-table test (`src/point_add/pingpong_div.rs:3287-3322`).

I independently replayed that truth table: **699,040 cases passed**. This is a direct positive control for Justin’s thesis: a small-width exhaustive identity exposed a constant-width nonlinear prefix that then lifted into the 256-bit circuit.

One tooling caveat: `cargo test` on the accepted tree is not currently a sound global gate because unrelated bin-test targets fail to compile against stale experimental symbols/APIs. The standalone truth table passes, but the new small-width harness must be its own buildable target with a narrow dependency surface.

## Scaling traps: mechanisms lift; raw constants do not

The largest trap is the field correction. secp256k1 uses

```text
p = 2^256 - f
f = 2^32 + 977
bitlen(f) = 33
```

The source hard-codes `F_SECP256K1 = (1 << 32) + 977`, `F_BITLEN = 33`, `LSBS`, comparator padding, and square guard widths (`trailmix_ludicrous/arith.rs:446-454`; `square/product_register.rs:11-20`). At 64 bits, the literal `f` occupies over half the word instead of about one eighth. That changes fold/carry geometry, NAF regimes, square wrap boundaries, and which phase binds. A literal 64-bit port can therefore invert the ranking of two designs.

Use two layers:

1. **Primary: modulus-independent parameterized kernels.** Adders, comparators, carry cleanup, transcript codecs, liveness schedules, and square product-register dataflow are tested at 8/16/32/64 bits. These experiments search identities and lifetime structures, not field-specific constants.
2. **Secondary: structurally scaled toy pseudo-Mersenne fields.** Use a family `p_n = 2^n - f_n` whose `bitlen(f_n)/n`, signed-digit weight, guard ratio, and fold-window ratio approximate secp256k1. Prefer prime members when the full EC shell is tested. This is a cross-check, never the primary proof.

Do not copy `chunk=16`, `window=7`, `round=170`, or any other 64-bit number into the 256-bit source. Lift the cause: a ratio, algebraic identity, reachability support, lifetime certificate, or scheduler recurrence. Re-optimize the integer constant at 256.

## Promotion gate for every candidate

A small-width result may enter a 256-bit engineering lane only when all of these hold:

1. The same semantic step appears at both 32 and 64 bits, or an exact algebraic/liveness proof covers arbitrary width.
2. The result records normalized terms (`Q/n`, `T/n`, `T/n^2`, transcript bits/round, chunk width/n, and live interval), not only the raw score.
3. A 96- or 128-bit sentinel preserves the sign of the normalized improvement after re-optimizing integer parameters.
4. Value, inverse, phase, and ancilla checks pass. Approximate variants additionally record their full error set; a lucky test vector is not evidence.
5. The 256-bit patch moves the actual `pp_div_replay` owner or lowers T at fixed Q. A local allocation reduction off the global peak is not a qubit win.
6. Score economics clear the current strict bar. At the current frontier:

| Q | maximum rounded T for a strict beat | implication |
|---:|---:|---|
| 1266 | 912109 | one qubit saved can spend up to 719 rounded T |
| 1267 | 911389 | fixed-Q route must save at least one rounded T |
| 1268 | 910671 | one extra qubit requires at least 719 rounded T saved |

The final route still needs a fresh op-stream nonce search and trusted 9,024-shot `0/0/0`, but nonce selection is outside this structural lane and cannot be counted as the mechanism.

## Ranked candidate mechanisms and lift falsifiers

### J1. Carry-in-aware exact boundary erasure with a retained window-entry carry

**Priority:** 1 — best immediate small-width target.

**Source opening.** `add_chunked_measured_with` keeps at most two inter-chunk boundary wires, then erases a consumed boundary using `cmp_lt_phase_conditioned(sum, addend)` (`pingpong_div.rs:2062-2157`). The layout comments explicitly say only chunk 0 has a zero carry-in and therefore an exact full-chunk `sum < addend` identity; later wide boundaries are approximate (`pingpong_div.rs:1522-1532`). The codebase already contains carry-in-aware phase comparators (`arith/compare.rs:341-435`).

**Mechanism.** Retain or host the carry entering the *top comparison slice* of a chunk until its carry-out is HMR-erased. Use that exact window-entry carry with a carry-in-aware comparator. This is more precise than retaining only the chunk’s original carry-in: when the comparison omits low bits, exact top-window repair requires the carry produced by those omitted bits.

The promising form is a three-pebble schedule:

- retain boundary carry-out;
- retain one internal carry at the top-window entry;
- consume the boundary in the next chunk;
- HMR the boundary and repair its phase from the top slice plus retained internal carry;
- clean the retained internal carry in an ordering that restores its generating inputs.

With an exact entry carry, the final carry relation may collapse to a one-bit majority whose phase is quadratic and Clifford-only. This could replace thousands of 22-bit conditional comparisons. Even if it costs +1 peak qubit, the present bar needs only about 719 T saved.

**32/64 experiment.** For chunk widths 4..64 and top windows 1..min(22,w): exhaustively synthesize and simulate the forward add, next-chunk consumption, reverse/HMR cleanup, and all four input-carry/control cases. Search cleanup orders and donor placements. Record peak transient wires and emitted/executed nonlinear gates. Include a phase-sensitive miter, not only value equality.

**Lift evidence.** The same constant-number-of-pebbles schedule works for arbitrary chunk width; the retained wire has a width-parametric provenance; 32/64/128 show T savings proportional to the number of repaired boundaries; at 256 the retained wire is hosted or saves more than 719 T if it raises Q by one.

**Hard falsifier.** Reject if cleaning the window-entry carry requires replaying the entire omitted low-prefix ladder, if a phase obligation survives, if the schedule needs more than one additional live wire at the Q1267 owner, or if 256-bit T savings are <=719 when Q rises to 1268. A whole-chunk carry-in-aware comparison is exact but is a likely T loss; it is only a control.

### J2. Low-prefix comparator automata beyond the accepted two-bit identity

**Priority:** 2 — exact, cheap to search, already has a positive control.

**Source opening.** The Q1267 route removes two nonlinear prefix stages and implements the terminal majority phase with Cliffords (`pingpong_div.rs:1237-1290`).

**Mechanism.** Enumerate reachable low-k states of each comparator site, not all unconstrained bit strings. Synthesize the borrow/carry state after k bits as affine or quadratic ANF over already-live controls. Every affine prefix removes carry wires and Toffoli; every quadratic final phase can be emitted with `CZ`/`Z` under HMR.

**32/64 experiment.** Exhaustively enumerate k=2..12 for forward walk, walk-back, replay flag, chunk-boundary, endpoint fold, and square overflow sites. Partition by site invariants. Use exact Boolean minimization to find the smallest reversible state transition and its algebraic degree.

**Lift evidence.** The simplified state depends on a fixed low-bit invariant (oddness, rotation frame, signed frame), not on n or sampled inputs; the same ANF appears at 32 and 64; a symbolic proof covers arbitrary n.

**Hard falsifier.** Reject an extension when degree or state count grows with k, when it relies on a low-bit relation absent at the 256-bit call site, or when the reduced comparator is off-peak and saves too few gates to cross the fixed-Q bar. The existing two-bit identity may be maximal under the known walk invariant; small-width search should be allowed to prove that quickly.

### J3. Output-hosted terminal carry/borrow synthesis

**Priority:** 3 — exact and demonstrated in the accepted lineage.

**Source opening.** The current walk adder stops retaining the final carry and synthesizes it directly into `target[n-1]` (`pingpong_div.rs:1344-1414`). The split form does the same (`1187-1235`). The replay fold also emits a final carry directly into the top output (`2198-2317`). `mod_halve_pm` hosts the final measured borrow in `target[0]` (`2772-2790`).

**Mechanism.** Search terminal networks of length k=1..8 that use output bits or restored selectors as ephemeral carry/borrow targets. The search objective is lexicographic: fewer retained wires at the owner, then fewer nonlinear gates, with exact inverse and phase cleanup.

**32/64 experiment.** Exhaustively synthesize the last k stages of each current ripple family at n<=12, then instantiate the discovered parametric terminal cell at 32/64. Check all carry-in, control, complement-frame, and inverse cases.

**Lift evidence.** The terminal cell depends only on local ripple equations and a stated output-use invariant; saved wires/gates are constant in n but occur at the Q1267 owner or at a high-multiplicity T site.

**Hard falsifier.** Reject if an output bit is observed before restoration, if the inverse needs an extra retained copy, if HMR phase repair becomes cubic, or if the wire is not live at the 256-bit binder.

### J4. Boolean-control live-range holes and conditionally-clean host assignment

**Priority:** 4 — likely source of several one-to-six-wire steps.

**Source opening.** The accepted source clears and frees `sign_xor_add` and `odd_correction` across binding carry ladders, reuses `parity`/`add_out` as `plus_f`, and reconstructs the controls afterward (`pingpong_div.rs:2321-2405`, `2628-2720`). Terminal `u,v` passengers are loaned across replay (`264-299`). These are explicit live-range holes, not arithmetic changes.

**Mechanism.** Build a phase-aware interval graph for each replay cell. Mark every wire as live-value, idle-clean, idle-dirty-restorable, classical/HMR obligation, or immutable control. Solve host assignment and recompute placement exactly at 32/64, then generalize each match with an invariant certificate.

**32/64 experiment.** Emit allocation/free/reacquire plus use traces for one halving and one doubling cell. Search interval coloring with costs for CX-only recompute, Toffoli recompute, and HMR cleanup. Force negative tests where a donor is read inside the proposed hole.

**Lift evidence.** A donor/borrower pair is identified by role and phase, not by qubit ID; the hole duration and restore proof are width-independent; the saved wire lies on `pp_div_replay` at 256.

**Hard falsifier.** Reject if the donor is not idle over the full window, if it carries an unresolved measurement phase, if restoring it costs more than the score value of the saved qubit, or if another co-binder pins Q1267.

### J5. Reachable-sign transcript block codec and fixed-point tail codec

**Priority:** 5 — highest upside, higher proof burden.

**Source opening.** Ping-pong records one sign qubit per round and holds the tape through coefficient replay (`pingpong_div.rs:3-12`, `323-463`). The tape is still the dominant persistent term. Interleaving changes when signs coexist with replay but does not encode them.

**Mechanism.** Enumerate reachable k-round sign words conditioned on parity, width schedule phase, direction, and converged/non-converged state. If a block support has fewer than `2^k` words, synthesize a fixed reversible codec. Treat the fixed-point tail separately: once `(u,v)` reaches the terminal +/-1 pair, remaining transitions may have a much smaller support or a run descriptor.

**32/64 experiment.** At n=16 exhaust all odd inputs; at 32/64 census large exact populations. For k=2..16 and normalized round position, record support size, entropy, transition automaton, encoder/decoder Toffoli, scratch, and streamed-decode peak. Require held-out support coverage.

**Lift evidence.** Interior bits/round stay below 1 by a non-vanishing margin across 32/64/128; the missing words follow an exact recurrence invariant; decoder scratch does not co-reside with a wider raw block; predicted 256 tape saving clears codec T at the Q/T exchange rate.

**Hard falsifier.** Reject if support approaches `2^k` as n grows, if savings exist only in an O(1) tail, if the codec must materialize raw and packed blocks together at replay, or if exact convergence detection costs more than the tail it removes.

### J6. Direction-specialized replay/interleave/pebble scheduling

**Priority:** 6 — proven architecture, search space still jagged.

**Source opening.** Interleaving was an accepted structural step from Q1300 to Q1279 in the local public notes. The current plan has per-direction `r1`, shared `r2`, separate walk peak, and allowance `peak - tape - 2N - 2*walk_width` (`pingpong_div.rs:1766-1831`). The Q1267 source also separates divide/multiply fold windows and round counts (`13-25`, `161-207`).

**Mechanism.** Replace the two-checkpoint hand schedule with an exact dynamic program over events: walk, replay, walk-back, tape retention, coefficient allocation, passenger loan, chunk layout, and optional block recomputation. Search direction independently, then co-balance the two peak owners.

**32/64 experiment.** Enumerate all legal schedules for scaled round counts with exact liveness and T costs. Plot the full Q/T Pareto staircase, not one scalar optimum. Add block-pebble actions only where their recomputation cost is explicit.

**Lift evidence.** The winning schedule family is described by normalized breakpoint equations or local event rules and persists at 32/64/128. At 256, re-optimize integer checkpoints and observe a new Q/T point rather than copying the 64-bit indices.

**Hard falsifier.** Reject if every 32/64 win is a finite-size checkpoint coincidence, if the normalized breakpoints drift materially by 128, or if recomputation T per saved 256-bit qubit exceeds the current exchange rate. Earlier full-prefix Bennett checkpointing was priced as a loss; only a new local staircase/mechanism reopens it.

### J7. Exact chunk-partition DP, co-optimized with cleanup semantics

**Priority:** 7 — low engineering risk after J1 semantics are fixed.

**Source opening.** `chunk_layout` greedily searches equal splits or one exact leading chunk plus wide chunks, minimizing the number of approximate boundaries (`pingpong_div.rs:1503-1587`). The per-round allowance is elastic, so lowering the nominal peak can simply force more chunks/repairs and leave the measured peak unchanged.

**Mechanism.** Run a dynamic program over arbitrary chunk sizes, final-carry timing, comparison width per boundary, exact/approximate cleanup type, retained entry-carry pebbles, and direction-specific cell extras. Return the entire Pareto set `(ladder Q, emitted T, expected/actual error class)`.

**32/64 experiment.** Exhaust all partitions at n<=32; DP at 64. Validate each layout against a bit-exact adder simulator and phase model. Compare the current greedy result against the true lower envelope.

**Lift evidence.** A repeated nonuniform pattern beats greedy at 32/64/128 and can be expressed as a parametric partition rule. The 256 re-optimization reduces T at Q1267 or opens a lower-Q plan.

**Hard falsifier.** Reject if greedy already lies on the exact Pareto envelope, if improvements disappear when true executed weights are used, or if every lower ladder merely transfers the peak to tape/coefficient state.

### J8. Square recursion, in-register aliasing, and fold-segmentation DP

**Priority:** 8 — strong precedent; secondary while replay binds.

**Source opening.** The accepted source merges the Karatsuba sum into the input high half instead of allocating a separate 129-bit register, concatenates disjoint correction operands into one subtraction, emits shifted full terms by rotation/fold, and uses level-2 Karatsuba branches (`square/product_register.rs:23-57`, `140-189`, `365-500`, `502-565`). Those structural moves created enough liveness slack to restore exact full-width square adders.

**Mechanism.** At each square node, choose split, recursion depth, product-register lifetime, direct-to-accumulator fold, input-half alias, correction concatenation, and carry segmentation. Search the Pareto frontier by dynamic programming rather than fixing half splits and one recursion depth.

**32/64 experiment.** Exhaust split points and depth through 64 bits. Track actual live intervals and fold coefficient regimes. Run both modulus-independent integer-square kernels and the secondary structurally scaled pseudo-Mersenne fields.

**Lift evidence.** A split/alias identity is algebraic and survives arbitrary n; normalized T savings persist at 128; at 256 it lowers T without raising the replay peak, or lowers a square co-binder if replay is reduced by another candidate.

**Hard falsifier.** Reject any conclusion driven by literal `f=2^32+977` at n=64, by a wrap/NAF regime absent at 256, or by local square Q that remains far below `pp_div_replay`. A square-only qubit saving is zero until it becomes a co-binder.

### J9. Certified width envelopes and earlier high-bit loans

**Priority:** 9 — useful only if converted from a fit into an invariant.

**Source opening.** The current route embeds a 700-entry sampled width schedule, sparse one-bit repair set, and sign-extension shrink/grow (`pingpong_div.rs:529-645`, `1624-1643`). The accepted 675 source re-enabled the sparse repair set. Existing comments warn that sampled step-down skips can alter self-healing behavior.

**Mechanism.** At small n, compute the exact reachable magnitude set per round. Search for symbolic envelopes and low/high bits that are deterministically sign copies or zero before the current schedule frees them. Loan only bits with a proof certificate; do not fit a lower quantile.

**32/64 experiment.** Exhaust n<=20 and use a complete symbolic/BDD or interval proof at 32/64. Compare the certified envelope with the sampled schedule. Search for step-index rules, not a new lookup table.

**Lift evidence.** The certificate is inductive under the ping-pong recurrence, its normalized envelope stabilizes, and freed bits provide a real host at the 256 replay owner.

**Hard falsifier.** Reject if the improvement exists only on sampled distributions, if the envelope is not inductive, if 32/64 slopes drift strongly, or if high bits are still controls for convergence/self-healing at 256. This candidate must remain exact; otherwise it collapses back into nonce-island tuning.

### J10. Reachable-state invariant mining inside every walk round

**Priority:** 2 alongside J2 — this generalizes the accepted low-two and terminal-stage wins.

**Source opening.** The signed walk already deletes its first two AND stages because oddness and the sign relation make their carries copies of live wires (`pingpong_div.rs:1298-1347`). It deletes or output-hosts the terminal carry using top-bit relations (`1344-1414`). A proposed top-AND skip based only on a loose width-violation argument was correctly left off because some oversized states self-heal and the skip changes them (`648-683`). The distinction is crucial: mine exact reachable-state invariants, not empirical correlations.

**Mechanism.** Enumerate the reachable `(source,target,sign,round parity,width transition)` states at small n and search every ripple position for predicates of the form `carry_i=0`, `carry_i=1`, `carry_i=x`, `carry_i=x xor y`, `operand_i=operand_j`, or a quadratic phase-only relation. Search both forward and reverse reachable sets. Turn each hit into an inductive recurrence invariant and substitute the live predicate for an allocated AND/carry wire.

**32/64 experiment.** Exhaust all odd denominators at n<=20; use complete bitset/BDD state propagation at 32 where feasible and a proof-guided census at 64. Emit a per-round/per-position invariant ledger with support count and counterexamples. Recheck candidate predicates on an independently generated 64-bit population before attempting proof.

**Lift evidence.** A predicate is proved inductively from the ping-pong recurrence and width transition, appears in both traversal directions where required, and removes at least one nonlinear gate or live wire per qualifying round. The proof is parameterized by width/round class rather than a finite input sample.

**Hard falsifier.** Reject any predicate with one reachable counterexample, any rule that merely tags already-width-violating states, any forward-only relation whose inverse needs the deleted wire, or any schedule-specific rule that fails after re-optimizing the 256-bit width schedule. The disabled `walk_top_skip` is the negative control.

## Recommended first tranche

Run three independent kernel searches before building a full 64-bit EC circuit:

1. **J1 exact boundary cleanup:** highest expected T return and a crisp phase/value falsifier.
2. **J2/J3/J10 invariant and terminal Boolean synthesis:** use the existing low-two test as the positive control and disabled top-skip as the negative control; search comparator prefixes, per-round reachable carry predicates, and final carry/borrow cells together.
3. **J4 liveness solver:** trace one divide and one multiply replay cell and search conditional-clean hosts, including the J1 retained entry carry.

In parallel, collect J5 sign-block supports at 16/32/64. Do not write a codec until the support deficit persists across widths. Then run J6/J7 scheduling against the measured cell catalogue. Defer full-field square work until the modulus-scaling harness exists.

## Result classification

- **Immediate GO:** J1, J2, J3, J4, J10.
- **GO as discovery, build only after support/DP evidence:** J5, J6, J7.
- **Secondary/co-binder lane:** J8.
- **Fail closed unless exact invariant is found:** J9.

The core lesson is not “64-bit scores predict 256-bit scores.” It is: **small widths make exact state spaces, liveness colorings, and discrete scheduler transitions cheap enough to exhaust. The liftable output is the proof-bearing mechanism that creates a Pareto step.**
