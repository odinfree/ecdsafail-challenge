# D1272 `pp_div_replay` overshoot diagnosis

Updated: 2026-08-23

## Decision

`FIXED_FOLD_FLOOR / NO_PEAK1271_FALSIFIER / NO_CANDIDATE_MEASUREMENT`

The fresh bounded task was dispatched before this diagnostic rebuild:

1. explain the D1272 Q1273 peak at operation index 4,257,060;
2. only if it is a one-qubit cap-layout plateau, predeclare one
   `PEAK=1271, LADDER=242, B1=24` Q1272 falsifier;
3. otherwise freeze diagnosis only.

The conditional is false. The extra qubit is not a discrete ladder-layout
plateau that a lower `SUB4_PP_PEAK` can cross. It is the fixed live footprint of
the terminal fused-fold cell, which does not consult the ladder cap. Therefore
the proposed PEAK1271 row has a static lower bound of Q1273 and was not built,
selftested, or evaluated.

No R1/R2 tuning, second row, predictor, provider action, hunt, range, scan,
submission, source edit, or incumbent edit occurred.

## Exact diagnostic identity

- worktree base: `e1cfd3aab6831a92cff00703a8be287e1cb92065`;
- source model: hard-coded B1=24 inherited from `6f6da43`;
- diagnostic settings: `SUB4_PP_PEAK=1272`,
  `SUB4_SQUARE_LADDER=242`;
- emitted operations: 12,904,991;
- operation SHA-256:
  `0ce4aac781957c12b2fb2217cb116a68fe77e74ad810a73cfd1a1f4450fa0e20`;
- `src/point_add/pingpong_div.rs` SHA-256:
  `92ffe2f17886334e9db863e81683ef31911c46b759b7b7acac65017591e6c66d`.

The operation identity exactly reproduces terminal D1272. The diagnostic added
only existing env-gated allocator census output (`B0_*`, `PP_IDMAP`, and
`TRACE_PEAK`); it did not alter the operation stream or source.

## Peak census

The bounded census window `[4257000,4257120]` reproduced:

```text
B0_CENSUS_BEGIN best_active=1273 best_ops=4257060
  best_phase=pp_div_replay n_live=1273 n_groups=14
```

The complete live-set ownership at that instant was:

| live qubits | owner | role |
|---:|---|---|
| 402 | `pingpong_div.rs:1056`, allocated in `pp_div_replay` | interleaved walk signs |
| 297 | `pingpong_div.rs:1056`, allocated in `pp_div_walk` | pre-replay walk signs |
| 1 | `pingpong_div.rs:508` | fused round-zero sign |
| 256 | `pingpong_div.rs:1975` | caller numerator register |
| 256 | `pingpong_div.rs:261` | replay coefficient register |
| 1 | `pingpong_div.rs:1974` | terminal walk wire |
| 1 | `arith/adder.rs:341` | second terminal/base wire |
| 1 | `pingpong_div.rs:1479` | late overflow/carry-out |
| 1 | `pingpong_div.rs:1573` | fused-fold roving operand |
| 51 | `pingpong_div.rs:1574` | fused-fold carry chain |
| 1 | `pingpong_div.rs:1656` | parity |
| 3 | `pingpong_div.rs:1300` | three clean AND outputs |
| 1 | `pingpong_div.rs:1662` | sign/parity selector |
| 1 | `pingpong_div.rs:1669` | plus-f selector |

The rows sum exactly to 1,273.

## Static composition proof

At the terminal division replay:

```text
base = tape + 2*N + 2*walk_width
     = 700  + 512 + 2
     = 1214
```

This is both the formula used by `allowance()` and the census subtotal:
700 signs, two 256-wire coefficient/numerator registers, and two terminal
wires.

With `SUB4_PP_PEAK=1272`, `allowance()` therefore gives 58. That value reaches
the chunked-adder ladder selector through `ladder_for_allowance()` and
`set_ladder()`. It does not reach `fused_fold_maskfree()`.

The peak occurs after the chunked add, inside the fixed 53-bit fused fold:

```text
fold scratch = late overflow             1
             + roving operand            1
             + (53 - 2) carries         51
             + parity                    1
             + clean AND outputs         3
             + sign/parity selector      1
             + plus-f selector           1
             =                           59

realized Q = base 1214 + fold scratch 59 = 1273
```

`replay_fold_window()` is frozen at 53. None of the seven fold allocations
above reads `Plan::peak`, `LADDER_TARGET`, or the chunk layout. Rounds, R1/R2,
the tape length, and coefficient widths are also frozen by the task. Lowering
only PEAK from 1272 to 1271 can reduce the chunked-adder allowance from 58 to
57, but it cannot reduce either the 1,214-wire base or this 59-wire fold cell.
The static lower bound remains Q1273.

This explains the observed shape precisely: at D1272 the product-square and
multiply owners reach Q1272, while the division replay stays at Q1273. The
overshoot is one qubit relative to the requested D1272 cap, but it is not a
one-step cap plateau. A PEAK1271 measurement would be a known-negative third
row, so the conditional authorization does not activate.

## Frozen next action

A future Q1272 attempt must change the `pp_div_replay` composition itself—for
example, remove or loan one wire from the 59-wire fused-fold live set, or
recompose that fold while a selector is dead. Any such change requires a fresh
predeclaration with value/phase/ancilla falsifiers and T pricing against the
then-live frontier. It is outside this diagnosis-only lane.

Generated `ops.bin`, release binaries, caches, and logs are excluded from the
commit. No `results.tsv` or score artifact was produced.
