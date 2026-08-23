# Operandless fold — implementation and frozen Gates 1–2

Updated: 2026-08-23. This receipt follows the pushed Stage-A baseline
`c982ed7` and stops after frozen Gate 2, before any candidate artifact or
owner measurement.

## Decision

`IMPLEMENTED / GATE_1_PASS / GATE_2_PASS / HOLD_STAGE_3_UNRUN`

Exactly one default-off family was added: `SUB4_PP_FOLD_OPERANDLESS=1`
inside `fused_fold_maskfree`, composing with the already protected selector
eviction. Only `src/point_add/pingpong_div.rs` and the selftest hook in
`src/point_add/mod.rs` changed. No second arithmetic/lifecycle family,
default change, selector lifecycle change, width/round/R1/R2/BREAK/tape/
replay/carry/erasure change, evaluator edit, rescue tuning, provider action,
hunt, or submission occurred.

Stage 3 and later gates remain explicitly unrun: there is no candidate
artifact/owner census, exact candidate T, product-square result, complete
point-add result, or unchanged full 9,024-shot candidate receipt yet.

## Claude implementation provenance and spend

- model: first-party `claude-fable-5`, high effort; Opus fallback configured
  but unused;
- session: `86025481-fc12-4778-ba10-12a20efc6341`;
- 25 turns, 58,764 output tokens including 43,270 thinking tokens;
- exact modeled cost: **$6.266129** under the $20 hard cap;
- web search/fetch: 0/0; permission denials: 0; subagents: 0.

Claude had only Read/Edit/Write/Grep/Glob tools, edited the two bounded files,
and left the change uncommitted. Codex independently reviewed, compiled, and
ran the gates below. The exact spend and provenance were appended at
`2026-08-23T07:40:07Z` to `/Users/olifreuler/ecdsa-ops/SPEND.md`.

## Independent source audit

The flag is read per fold call and is false unless its value is exactly `1`.
With it false, the original operand allocation/body/free path is selected.
The selector-empty branch is source-identical. With it true, only the roving
operand allocation is removed.

For selector-nonempty positions, the forward branch implements the frozen
identity directly:

```text
(S xor p)(a xor p) xor p = S*a xor S*p xor p*a
```

It emits `CCX(c,a,carry)` and `CCX(c,p,carry)` for each selector `c`, then
`CCX(p,a,carry)` and `CX(p,a)`. The reverse branch first restores
`carry ^= p`, measures it, corrects phase with `CZ_if(p,a,m)` plus
`CZ_if(c,a,m)` for each selector, then applies `CX(c,a)` for each selector.
This matches the predeclaration literally; no alternate construction was
introduced.

On the real 53-bit schedule (`P=51` nonempty internal positions,
selector-multiplicity sum `M=58`), the focused assertions attribute the exact
per-call delta:

- `+2M = +116` CCX;
- `-(3M+6P) = -480` CX;
- `+M = +58` conditioned CZ;
- `-1` R;
- unchanged Hmr and CCZ;
- `-307` total emitted operations and `-1` peak qubit.

Thus the net Clifford reduction is 423 per fused call, while the hostile
Toffoli price remains the predeclared +116 per call. The review found no
unpriced tuning knob or second family. `git diff --check` and the release
compiler both passed. A repository-wide `cargo fmt --check` remains noisy on
many untouched, pre-existing files, so no bulk formatting rewrite was made.

Candidate source identities at this gate:

- `src/point_add/pingpong_div.rs`:
  `134a495bc9dea6c3bd1da802cb2f95e5634089a0fe808784696852e5a5918332`;
- `src/point_add/mod.rs`:
  `674b2c6e1ae6adac4c4f71cba0bc7a0c76c7c3e4a44509221c0c164d01089c70`;
- unchanged `src/bin/eval_circuit.rs`:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`.

## Clean build

`cargo build --release --locked --offline --bin build_circuit --bin
eval_circuit` completed successfully after the Stage-A cleanup. Only the
three inherited warnings in `arith/multiply.rs` and `dirtyscan.rs` appeared.
Release binary hashes in this isolated path were:

- `build_circuit`:
  `fd7b223b81f93efbd0e0d33e08ce260439422cb8f39eec3d3883ec52613e78f6`;
- `eval_circuit`:
  `0c98954b433639ea2d88a4182bc61a7bc358c152fb38a7b9df470a000c694b47`.

## Gate 1 — protected opt-out reproduction

With `SUB4_PP_FOLD_OPERANDLESS` and its selftest hook explicitly unset, the
exact protected geometry

```text
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
SUB4_PP_FOLD_SELECTOR_EVICT=1
```

reproduced 12,908,488 operations and compressed `ops.bin` SHA-256
`678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0`
byte-for-byte.

The unchanged full 9,024-shot evaluator reproduced Q1272, T914727.660
(rounded 914728), and classical/phase/ancilla `18/13/0`. Its first reported
failure was phase mask `0x0040000000000000`, exactly matching the protected
receipt. The generated `results.tsv` row was removed after capture; its
protected SHA-256 is restored to
`eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

## Gate 2 — focused exhaustive and real-schedule miter

`SUB4_PP_FOLD_OPERANDLESS_SELFTEST=1 ./target/release/build_circuit` exited
zero and reported:

```text
FOLD_OPERANDLESS_SELFTEST: PASS
```

The miter exhausts widths 1 through 6, every fold constant within each width,
every accumulator value, both first-carry values, and all eight raw selector
wire states. It also runs 256 covering lanes on the real 53-bit schedule.
Both protected and operandless streams match the classical ripple model and
each other lane-for-lane, with phase mask zero and every non-input ancilla
zero. Selector wires and first carry remain intact.

Coverage asserts the selector-empty path, both carry values, all selector
states, and every feasible selector multiplicity 0, 1, and 2. Multiplicity 3
is independently asserted absent across the exhaustive corpus: where `f` and
`-f` can agree at their lowest set bit, the lower `f` bit needed by `2f` is
clear; above it, the two complement. The real schedule independently asserts
51 nonempty positions, multiplicity sum 58, and both multiplicities 1 and 2.

The same gate asserts the exact operation deltas above, unchanged Hmr/CCZ,
byte-identical width-1/2 streams, and standalone peak 109 → 108 for the real
schedule.

Generated `ops.bin`, release products, logs, binaries, score artifacts, and
result rows are excluded from the commit.
