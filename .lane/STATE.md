# Lane state — Q1272 rounds696 / ladder242 production bake

Date: 2026-08-23 (Europe/Zurich)

## Decision

The audited Q1272 composition is now baked into source defaults on the isolated
branch `research/q1272-round696-ladder242`, starting from exact receipt commit
`82a742b19fb28d641e3993c3ef18abd0191544ee`.

The build is byte-for-byte reproducible and passes the production 64-lane
profile plus both focused self-tests. The inherited 9,024-shot draw remains
dirty at `17/16/0`, so this branch is a frozen hunt candidate, not a submission
candidate. No nonce search, provider action, or submission was started here.

## Frozen source defaults

```text
SUB4_PP_WIDTH_RESCALE=1 (implicit default; =0 is the opt-out)
SUB4_PP_R1=340
SUB4_PP_R2=628
SUB4_PP_ROUNDS=696
SUB4_PP_ROUNDS_MUL=696
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
SUB4_PINGPONG_TAIL_NONCE=251000962439 (unchanged inherited nonce)
```

Only three runtime defaults changed from the audited Q1274 source: divide
rounds `698 -> 696`, replay peak `1274 -> 1272`, and square ladder `244 -> 242`.
Multiply rounds were already 696; width rescaling and R1/R2 were already baked.
No arithmetic primitive or evaluator code changed.

Every tuned value retains its environment override. Two reproduction paths
were exercised after the bake:

- prior Q1274 route: `ROUNDS=698`, `ROUNDS_MUL=696`, `R1=340`, `R2=628`,
  `PEAK=1274`, `SQUARE_LADDER=244`, width rescale on -> artifact
  `60b6fe451b0cea31c2deffee907c74a1327e175f1adbe9dd41d6e9d76e6ea933`;
- promoted live route: the prior vector plus `WIDTH_RESCALE=0`, `R1=342`,
  `R2=625`, `PEAK=1275`, `SQUARE_LADDER=245` -> artifact
  `d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124`.

## Exact production evidence

Clean release build:

```text
cargo clean
cargo build --release --bin build_circuit --bin eval_circuit
```

Final default reconstruction:

| item | exact result |
|---|---|
| loaded/emitted ops | 12,901,167 |
| semantic ops before 96-op tail | 12,901,071 |
| `ops.bin` SHA-256 | `ecc3d9f0bb1dd4e68e6d337e39c4cdb66cfbfe83928a81fec28e22797fca4cfd` |
| peak qubits | 1272 |
| 64-lane diagnostic T | 914748.17 |
| 64-lane gate | classical 0, phase `0x0`, dirty qubits 0 |

The final source state was rebuilt once more after comment cleanup and produced
the same op count and artifact hash.

## Co-binder profile

`PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` shows a balanced Q1272 plateau:

| phase | peak qubits | executed T on 64-lane diagnostic |
|---|---:|---:|
| `pp_div_replay` | 1272 | 262590.31 |
| `square_product_register` | 1272 | 58733.52 |
| `pp_mul_replay` | 1272 | 24218.28 |
| `pp_mul_walkback` | 1272 | 307586.95 |

First peak: op 2,527,023 in `pp_div_replay`. Its live-set census is 339 prior
walk-tape wires, 256 input/numerator wires, 256 replay coefficient wires, 145
`u`, 145 `v`, 128 replay-ladder wires, and three one-wire controls/signs: 1272
total. The two-qubit peak cut comes from replay ladder `130 -> 128`, coordinated
with square ladder `244 -> 242`; R1 remains 340, so the prior tape contributes
339 wires at the binding snapshot.

## Focused source gates

- `SUB4_PRODUCT_SQUARE_SELFTEST=1`: PASS — 58,980 emitted / 58,721.141
  executed Toffoli, Q1272, 64 square inputs, phase and ancilla clean.
- `SUB4_PINGPONG_POINT_ADD_SELFTEST=1`: PASS — 956,012 emitted / 914,661.344
  executed Toffoli, Q1272, 64 affine additions, phase and ancilla clean.
- `git diff --check`: PASS.

Release compilation emits three pre-existing warnings in unrelated arithmetic
and dirty-scan code. No warning originates in this bake. Repository-wide
test-only compilation is not claimed because the audited base has stale legacy
test modules; the callable production self-tests and unchanged trusted
evaluator are the applicable gates.

## Unchanged full 9,024-shot evaluation

The final default artifact was evaluated by the unchanged release
`eval_circuit` binary:

```text
loaded ops:              12,901,167
qubits:                  1272
classical mismatches:    17
phase-garbage batches:   16
ancilla-garbage batches: 0
exact average T:         914792.720
```

Rounded T would be 914793 and the score would be
`1272 * 914793 = 1,163,616,696` if a clean nonce exists, an 8,072,604 reduction
against the audited live score 1,171,689,300. The inherited draw is not clean,
so no submission claim follows from that score.

The full evaluator appends its receipt to `results.tsv`; that generated row was
removed after reading the exact average and is not part of this branch.
`ops.bin`, release binaries, logs, and generated score artifacts remain ignored
and uncommitted.

## Risk and next gate

The square and affine primitives pass their binary correctness gates. The
remaining faults are graded-route risks: two fewer divide rounds change
convergence exposure, width rescaling narrows the sampled schedule, and the
smaller replay/square budgets change measured-boundary exposure.

Before any hunt, qualify an exact classical predictor against unchanged full
9,024-shot fixtures and prove CPU/GPU parity on this exact op hash. Only after
that gate should a bounded first-predicted-clean canary be evaluated. A final
candidate still requires full `0/0/0` on the unchanged evaluator.

---

# Lane continuation — Q1272 density overturn (from checkpoint 091abce)

Date: 2026-08-23 (Europe/Zurich). Objective: minimize expected time to a clean
Q1272 nonce with a strict score beat (clean rounded T <= 921139); re-descend
density on the exact 696/696 stream.

## D0 — baseline reproduced byte-for-byte (clean rebuild)

- `cargo clean` + release rebuild at 091abce; `build_circuit` emitted
  12,901,167 ops, ops.bin sha256
  `ecc3d9f0bb1dd4e68e6d337e39c4cdb66cfbfe83928a81fec28e22797fca4cfd` — exact
  match to the frozen receipt. VERIFIED.
- 64-lane diag (`PP_PROFILE=1`): T914748.17 total, Q1272, peak op 2,527,023 in
  `pp_div_replay`, 0 classical / phase 0x0 / 0 dirty — exact match.

## D1 — tooling ported (route 1), byte-neutral

- Ported the Q1274 lane's `SUB4_DUMP_WSCHED` (schedule dump through the real
  `value_width` path) and `SUB4_PP_WSCHED_FILE` (sampled-table CSV override,
  default-off) into `mod.rs`/`pingpong_div.rs`. No `WIDTH_REPAIR` const
  imported — repairs must be refitted on this stream.
- Byte-neutrality: default rebuild after the port reproduces sha256
  `ecc3d9f0...` exactly. VERIFIED. (Note: a `SUB4_DUMP_WSCHED=1` run clobbers
  `ops.bin` with an empty stream; always rebuild after dumping.)
- Effective 696-map schedule dumped: `round*703/695` compression; effective
  width hits the 8-bit floor from round ~614 (rescale) vs ~692 (base).

## D2 — classical fault oracle validated on THIS stream

- ppfilter binary sha256 `f763f770527117be409123ae23ab8ceeecac1d5b8d7ee4e698d468f375f58128`
  (the exact binary the Q1274 lane cross-checked against its trusted 18/10/0
  and 22/11/0 receipts), source `/Users/olifreuler/ecdsa-ppfilter-rl`.
- `PPF_OPS=<this ops.bin> PPF_ROUNDS_DIV=696 PPF_ROUNDS_MUL=696
  PPF_WSCHED=<effective rescaled schedule>` breakdown @ inherited nonce
  251000962439: **pred_cls=17** == the trusted full-eval receipt (17/16/0).
  Split: walk_div=10 replay_div=0 walk_mul=5 replay_mul=2; causes: width=11
  term=4 walkback=0 shell=0; first faulting shot 889.

## D3 — corpus predeclaration (BEFORE any census observation)

Committed before any fit/census run on these draws:

- Training sample A: nonces 111000000000 .. 111000000319 (320 draws).
- Held-out sample B: nonces 222000000000 .. 222000000319 (320 draws).
- Held-out sample C: nonces 333000000000 .. 333000000319 (320 draws).
- Fitting uses A only (refits may use A+B, then validate on C, mirroring the
  Q1274 protocol). Controls (direct Q1274 r100/r200 index transfer) are
  priced on A and validated on B without refitting.
- The inherited nonce 251000962439 is a fixture only, never a density sample.
