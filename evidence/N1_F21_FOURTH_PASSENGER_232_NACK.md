# N1/F21 exact fourth passenger on the 232 binding cells

Date: 2026-08-26

Verdict: `HARD_NACK_Q1263_EXACT_232_FOURTH_PASSENGER`.

The exact fourth passenger is constructible with Clifford-only clear/restore
work and is independently selectable on precisely the admitted 232 cells. Its
exact K2/P1267/W1265/F21 candidate nevertheless remains Q1264 with maximum
referenced qubit id 1263. The predeclared Q1263/max-qid-1262 construction gate
therefore fails. No controlled 141x64 screen, provider work, nonce search,
push, or submission was run for this route.

## Binding and feature contract

- base commit: `bbabca072035d2ed63c285921359a91787fcdc67`
- base tree: `f859d19baeb610c447ae71244cf850264f0ec327`
- constructed `src/point_add/pingpong_div.rs` SHA-256:
  `867a9a4354c521dc88cfce5ad2e90b0778f0c60934bd6ca3edac28fdb033c782`
- selector SHA-256:
  `5e094a77beba68151a008c97b38377f2e1b52676b2d6bc5c95dad4210a1f73ca`
- source-contract test SHA-256:
  `e7a02f8f39b8f3b57767500374342f617b883d3169874adbd9064290e732cfc2`
- structural certificate:
  `/Users/odin/.ecdsafail/evidence/fourth-passenger-support-89ecdce6-20260826T164315Z`

Only exact literal `SUB4_PP_FOURTH_PASSENGER=1` enables the construction. A
selected cell additionally requires exact literal
`SUB4_PP_THIRD_PASSENGER=1`; otherwise construction fails closed. Absent, `0`,
and invalid fourth-passenger values remain dormant.

The exact selected set is the already-admitted third-passenger set: 109 divide
cells plus 123 multiply cells, 232 total. The passenger is the opposite bit-1
wire from the third passenger:

```text
even r: u[1] = 1 XOR tape[1] XOR ... XOR tape[r]
odd  r: v[1] = 1 XOR tape[1] XOR ... XOR tape[r]
```

Clear is one X followed by the complete ascending tape fan-in; restore is the
reversed fan-in followed by X. The fourth passenger is asserted distinct from
both existing odd passengers, the third passenger, and every fan-in control.
It is restored first so the nested release/reacquire order is LIFO.

Across the 232 selected cells, the construction contains exactly 225,990
Clifford operations before stream transforms: 225,526 CX and 464 X, with no
new non-Clifford work.

## TDD and local correctness

The selector suite was first observed RED on the four missing fourth-passenger
symbols, then GREEN at 7/7. It exhaustively checks the full 232-cell selection,
exact-literal and third-feature preconditions, even/odd passenger identity,
nonidentity with the third passenger, complete small-width clear/restore truth
tables, and invalid tape ranges.

The source-contract suite was first observed RED at 5/5 before source wiring,
then GREEN at 5/5. It binds the two flags, stored inverse recipe, parity mapping,
complete fan-in, nonalias assertions, and LIFO restoration. The inherited exact
support/source suite is GREEN at 9/9 after rebinding the expected source digest.

## Exact construction gate

Environment: `SUB4_SQUARE_B_LOCAL_K2=1`, `SUB4_PP_PEAK=1267`,
`SUB4_PP_WALK_PEAK=1265`, `SUB4_PINGPONG_INPUT_AWARE_CONSTPROP=1`,
`TLM_CASCADE_DISABLE=1`, third passenger `1`, fourth passenger as shown, and
straddle absent.

| arm | fourth | Q | max qid | emitted ops | compressed artifact SHA-256 | canonical semantic SHA-256 |
|---|---|---:|---:|---:|---|---|
| parent reproduction | absent | 1264 | 1263 | 12,525,540 | `661cd2277d481677029bb27911b6bd98ee0402bba86469bc6db7a654419df933` | `a332c38fc2b186c8885f60c7f8efc26aeb296d773c36438ca703c62dce9f28fe` |
| dormant control | `0` | 1264 | 1263 | 12,525,540 | `661cd2277d481677029bb27911b6bd98ee0402bba86469bc6db7a654419df933` | `a332c38fc2b186c8885f60c7f8efc26aeb296d773c36438ca703c62dce9f28fe` |
| dormant invalid | `invalid` | 1264 | 1263 | 12,525,540 | `661cd2277d481677029bb27911b6bd98ee0402bba86469bc6db7a654419df933` | `a332c38fc2b186c8885f60c7f8efc26aeb296d773c36438ca703c62dce9f28fe` |
| exact candidate | `1` | **1264** | **1263** | 12,751,513 | `a7197eb470e0c584b74ddcb8d885c32e3dfb0ba56724f84bc084e2f5f43a1256` | `a8bea626a276d59db1bb10c209e7defba07b40bd0ddee841fb2fa35b5b920229` |

The candidate artifact is distinct and its post-F21 emitted delta is +225,973
operations. The construction profile reports zero classical mismatches, zero
phase faults, zero dirty qubits, profile T 906,722.64, and 52 F21 removals for
the deterministic 64-lane build seed. Those profile counters are not the
requested controlled 141x64 screen.

The exact-`1`/third-absent arm exits 101 at the first selected cell with:

```text
SUB4_PP_FOURTH_PASSENGER=1 requires SUB4_PP_THIRD_PASSENGER=1
```

## Terminal audit

- Decision audited: admit only at Q1263/max-qid-1262.
- Evidence: the active candidate is semantically distinct but is Q1264 with
  max qid 1263; the parent and both dormant arms are byte-identical Q1264.
- Cause boundary: the transient fourth loan reduces an interior scratch need,
  but a Q1264 entry/exit/global live-set boundary remains. The exact 232 cells
  cannot cross that boundary by adding another transient passenger.
- Smallest useful next route: change the binding lifetime/order or another
  Q1264 boundary; do not extend this exact 232-cell fourth-passenger family.
- Gate result: `HARD_NACK_Q1263_EXACT_232_FOURTH_PASSENGER`.

The broad repository `cargo test --locked` remains pre-existing red outside
this change because of stale binary-test APIs. Repository-wide
`cargo fmt --check` also remains red; this lane avoided a broad mechanical
rewrite. The bounded selector, source-contract, inherited
support, release build, artifact, and diff gates are the authoritative checks
for this local construction.

Retained local evidence:
`/Users/odin/.ecdsafail/evidence/fourth-passenger-construction-bbabca0-20260826T165607Z`.
