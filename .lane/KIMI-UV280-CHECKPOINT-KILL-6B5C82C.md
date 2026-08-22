# The 280 u/v walk slices at the batch-replay boundary: checkpoint kill on 6b5c82c

Date: 2026-08-22. Lane: `research/kimi-burn-6b5c-passenger`.
Methodology credit: Teddy Pender — cheapest dependency falsifier before any
builder. Sibling context: the r1=356 literal raw checkpoint was killed at
Q1980 (`a313b84`); current-walk Bennett recomputation is listed as killed on
the Fable stream lane (`68bf16c`). This note closes the u/v slice with exact
6b5c82c arithmetic; no circuit prototype was built.

## Target

In the planned divide (`plan = r1:356, r2:625, peak:1278`), walk rounds
0..356 run first; then `shrink_to(value_width(356))` freezes u and v while
the batch replay of rounds 0..356 runs. During that batch — the Q-binding
phase, global peak op 2,643,328 — u/v are idle-but-live.

Exact footprint from `WIDTH_SCHEDULE` (value_width(356) = 140):
**u + v = 280 wires** at the batch boundary. Of these, v's 140 wires are
caller-x ABI wires (x[0..139]); the high x wires were freed by `shrink_to`
and are pool-reused below the plateau.

## Falsifier 1: information floor — max possible saving is 24 wires

The walk map (u0, v0) ↦ (u_r, v_r) is a bijection given the tape signs
(every round is invertible), and u0 = p is a constant. So the 280-wire pair
(u_356, v_356) carries exactly the 256 bits of x's entropy. Any reversible
checkpoint of the walk state needs ≥ 256 wires; the incumbent already holds
it in 280 because `shrink_to` has collapsed the sign-extension wires. 

**Maximum achievable saving at the batch plateau: 280 − 256 = 24 wires.**
That maximum is attained only by fully unwalking the prefix to (p, x) — the
only scheme that reaches the floor.

## Falsifier 2: T economics — 8.3× over budget

Unwalking rounds 355..0 and rewalking 0..355 re-pays the prefix walk twice.

- Measured (PP_PROFILE on the forced default build): `pp_div_walk` phase =
  rounds 0..355 = **71,756 emitted = 71,756 executed Toffoli** (the walk is
  fully unconditioned). Cross-check: the static per-round formula
  width(r)−3 sums to 71,500 over rounds 1..355, leaving exactly 256 for the
  fused round-0 lift — the formula is exact, and the same arithmetic prices
  the unwalk.
- Unwalk + rewalk price: 2 × 71,756 = **143,512 executed T** (+ 714 sign
  copies and the round-0 reverse lift, immaterial at this margin).
- Exact-gate budget for 24 qubits at Q1278/T918358: 1 qubit ⇔ 718.61 T, so
  24 wires ⇔ **17,247 T**.

Realized exchange: 143,512 / 24 = 5,980 T per qubit = **8.3× over
break-even**. Net score impact even in the best case: strongly positive
(worse). T-kill.

## Falsifier 3: the mandatory rewalk RAISES the peak — Q-kill

The rewalk must complete before interleaved round 356 can run, and at that
moment the tape copies (357), the replay coefficient (256), and caller y
(256) are all still live. Rewalk round 0 re-materializes u/v at the full
round-0 envelope 2×259 = 518:

  tape 357 + u/v 518 + coefficient 256 + y 256 = **1,387 ≥ 1,278 + 109**

The checkpoint relocates the peak to the rewalk and inflates it by ≥109
qubits. Partial unwalks dodge nothing: the width schedule is non-increasing,
so unwalking backward GROWS u/v — only the full unwalk frees any wires, and
it is the one priced above. Q-kill, independent of the T-kill.

## Verdict: KILL

The 280 u/v slices are already the shrink_to-compressed value-envelope
representation of x's entropy. Compaction below 280 is bounded by 24 wires,
and reaching even that costs ≥8.3× the T budget or +109 peak qubits. This
closes the last census component of the divide-replay peak that the
y-passenger kill (`KIMI-Y-TRANSFER-KILL-6B5C82C.md`, transferring `e717062`)
left open:

- sign tape (694): information-theoretically irreducible (`ad206c9`, sign
  non-recomputability theorem) — the Fable stream lane owns the remaining
  streaming-representation question.
- carry ladder: allowance cliff killed (`02a5836`).
- 256 numerator (y): active operand, transfer kill (companion note).
- 256 coefficient: second pair line, decoder-at-peak wall (`e717062` closure 2).
- 280 u/v walk slices: this note.

## Saddle accounting

Budget was two dependency/liveness falsifiers + one bounded prototype.
Used: falsifier 1 (caller-y transfer kill), falsifier 2 (this note).
Prototype: not warranted — neither dependency proof survived. Normal path
byte-for-byte untouched (no source diff; leader receipt re-measured clean).
