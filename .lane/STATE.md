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
