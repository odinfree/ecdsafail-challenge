# Audit — Fable Q1274 width-rescale and Matt's two-round hint

Date: 2026-08-23 (Europe/Zurich)

## Decision

Commit `82a742b19fb28d641e3993c3ef18abd0191544ee` is reproducible and
cleanly pushed. Its source commit `94616482dbde34f8c537f3a6c3e9c388f2b1eea4`
is a real Q1274 composition with
substantial score headroom, but the inherited nonce is not clean: the unchanged
9,024-shot evaluator reproduces `18/10/0`. The route is a candidate for a fresh
nonce only after predictor qualification; it is not submission-ready.

Matt's hint is not fully exhausted by the committed `SQUARE_LADDER 245 -> 244`
change. A separate, bounded composition reaches a balanced Q1272 plateau:

```text
SUB4_PP_WIDTH_RESCALE=1
SUB4_PP_R1=340
SUB4_PP_R2=628
SUB4_PP_ROUNDS=696
SUB4_PP_ROUNDS_MUL=696
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
SUB4_PINGPONG_TAIL_NONCE=251000962439
```

It is not a free exact cut. Shortening the divide walk is a graded convergence
risk, width rescaling narrows the sampled schedule, and the lower replay/square
budgets change measured-boundary exposure. The Q1272 route passes both 64-lane
gates but is `17/16/0` on the inherited full draw. Freeze it as a separate
hunt candidate; do not bake it into this audited Q1274 branch.

## Git and source provenance

- worktree: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/claude-fable-burn-087cafa`
- branch: `research/claude-fable-burn-087cafa`
- upstream: `odinfree/research/claude-fable-burn-087cafa`
- receipt commit: `82a742b19fb28d641e3993c3ef18abd0191544ee`
- source commit: `94616482dbde34f8c537f3a6c3e9c388f2b1eea4`
- exact live base: `087cafaef46a4e339644a6191ff2df2e7031cb80`
- before this audit document: clean, upstream divergence `0/0`
- source diff versus live: 17 insertions, 7 deletions across two source files

The source delta is only:

1. make the existing `width_round_index` rescale default-on, with
   `SUB4_PP_WIDTH_RESCALE=0` as the exact opt-out;
2. replay plan defaults `R1 342 -> 340`, `R2 625 -> 628`, `PEAK 1275 -> 1274`;
3. square carry-ladder budget `245 -> 244`.

No arithmetic primitive was added. The committed cells are the already-shipped
chunk layout, measured carry erasure, and square product-register machinery.

## Exact reproduction receipts

| route | loaded ops | artifact SHA-256 | Q | full result | exact full average T | rounded score if clean |
|---|---:|---|---:|---|---:|---:|
| live opt-out | 12,953,930 | `d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124` | 1275 | `0/0/0` | 918972.304 | 1,171,689,300 |
| committed Q1274 | 12,913,879 | `60b6fe451b0cea31c2deffee907c74a1327e175f1adbe9dd41d6e9d76e6ea933` | 1274 | `18/10/0` | 916091.556 | 1,167,101,208 |
| separate Q1272 hint | 12,901,167 | `ecc3d9f0bb1dd4e68e6d337e39c4cdb66cfbfe83928a81fec28e22797fca4cfd` | 1272 | `17/16/0` | 914792.720 | 1,163,616,696 |

The exact dirty-draw average for Q1274 is 916091.556, not the lane's earlier
915882 estimate based on transplanting the baseline diagnostic offset. The
conditional execution mix changes with the Fiat-Shamir draw. This correction
reduces the projected live margin but leaves a wide score gate: 4,588,092.
The Q1272 route would beat the live score by 8,072,604 if a clean nonce exists.

The Q1274 artifact has 12,913,783 semantic operations plus the 96-op tail. Its
independent 64-lane profile is:

```text
Q=1274, peak op=2,527,796, phase=pp_div_replay
diagnostic T=915905.50
classical=0, phase=0x0, dirty=0
```

All four co-binders reach Q1274, rather than only the first reported owner:
`pp_div_replay`, `square_product_register`, `pp_mul_replay`, and
`pp_mul_walkback`.

The Q1274 peak-owner census is:

```text
339 prior walk-tape wires
256 input/numerator wires
256 replay coefficient wires
145 u wires
145 v wires
130 replay-ladder wires
  3 one-wire controls/signs
----
1274
```

## Self-tests and build gates

The following were run from the exact source commit:

- `cargo build --release --bin build_circuit --bin eval_circuit`: PASS.
- Q1274 `PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1`: PASS, `0/0/0`,
  diagnostic T915905.50, four Q1274 co-binders.
- Q1274 `SUB4_PINGPONG_POINT_ADD_SELFTEST=1`: PASS, 64 affine additions,
  916063.359 executed T, Q1274, phase and ancilla clean.
- Q1274 `SUB4_PRODUCT_SQUARE_SELFTEST=1`: PASS, 64 square inputs,
  58709.125 executed T, Q1274, phase and ancilla clean.
- trusted unchanged Q1274 evaluator: exact `18/10/0` over 9,024 shots.
- live opt-out build with `WIDTH_RESCALE=0`, `R1=342`, `R2=625`,
  `PEAK=1275`, and `SQUARE_LADDER=245`: byte-identical baseline artifact.
- trusted unchanged live evaluator: exact `0/0/0`, T918972.304, Q1275.
- `git diff --check 087cafa..82a742b`: PASS.

Repository-wide test-only compilation is not a usable gate on this snapshot:
`cargo test --release --bin build_circuit -- --list` fails in unrelated stale
test-only code (missing legacy constants/helpers and obsolete simulator APIs;
165 compiler errors). `cargo test --release --lib point_add` runs zero tests.
The callable production selftests and trusted evaluator above are the usable
source gates; this audit did not edit the stale test modules.

## Matt hint: bounded history and ablation

`087cafa~8` is `b5796ce`, the baseline Matt described. Its relevant defaults
were divide rounds 700, multiply rounds 702, R1/R2 356/625, replay peak 1278,
and square ladder 248. The live base had already moved to 698/696, 342/625,
Q1275, and square ladder 245 before Fable started. Fable then moved to
340/628, Q1274, and square ladder 244.

Direct ablations on `82a742b` show why the ladder is only half the move:

| delta from committed Q1274 | measured Q | diagnostic T | 64-lane gate |
|---|---:|---:|---|
| square ladder 243 only | 1274 | 915895.55 | `0/0/0` |
| square ladder 242 only | 1274 | 915926.67 | `0/0/0` |
| replay peak 1273 + square 243 | 1273 | 916625.48 | `0/0/0` |
| replay peak 1272 + square 242 | 1272 | 917341.19 | `0/0/0` |
| rounds 696/696, replay peak 1274, square 244 | 1274 | 913814.58 | `0/0/0` |
| rounds 696/696, replay peak 1273, square 243 | 1273 | 914270.08 | `0/0/0` |
| rounds 696/696, replay peak 1272, square 242 | 1272 | 914748.17 | `0/0/0` |

Square tightening alone is off-peak because replay still binds. Lowering replay
and square together moves the plateau. At Q1272 the four co-binders again tie:
`pp_div_replay`, square, multiply replay, and multiply walkback all reach 1272.

The Q1272 peak census at op 2,527,023 is:

```text
339 prior walk-tape wires
256 input/numerator wires
256 replay coefficient wires
145 u wires
145 v wires
128 replay-ladder wires
  3 one-wire controls/signs
----
1272
```

This is the key correction to the casual "two tape qubits are free" reading:
R1 stays 340, so the binding snapshot still has 339 prior tape wires. The two
fewer divide rounds save gates and alter convergence exposure; the actual two
peak qubits come from the replay ladder 130 -> 128 plus the coordinated square
ladder 244 -> 242. The lower depth makes that Q1272 score attractive, but does
not make it exact.

Q1272 focused gates:

- product-register square selftest at ladder 242: PASS, 58721.141 executed T,
  Q1272, phase and ancilla clean;
- full affine 64-lane selftest: PASS, 914661.344 executed T, Q1272;
- independent profile: `0/0/0`, diagnostic T914748.17;
- unchanged 9,024-shot inherited evaluation: `17/16/0`, ancilla clean,
  exact average T914792.720.

Verdict: there is a real, balanced Q1272 structural candidate, but no newly
proven exact-clean cut. Its primitive-level structure passes focused tests; its
graded convergence and boundary risks still require a separately qualified
predictor and a fresh clean nonce.

## Safe next lane and gate

Keep this branch unchanged. A separate lane can start safely from the pushed
base `82a742b`:

```text
worktree: /Users/olifreuler/Documents/Codex/2026-08-21/par/work/q1272-round696-ladder242
branch:   research/q1272-round696-ladder242
base:     82a742b19fb28d641e3993c3ef18abd0191544ee
```

First action in that lane: bake the frozen config, reproduce
`ecc3d9f0...`, then qualify the exact classical predictor against unchanged
full 9,024-shot fixtures and CPU/GPU parity. Do not start a nonce hunt until
that gate passes. No provider state, scan, submission, or unrelated worktree
was changed by this audit.
