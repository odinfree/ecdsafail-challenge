# N1 branch-B local Karatsuba report

Date: 2026-08-26

Source: Layr-Labs `64f9aaa510b338041bc15d54b32c97fc2f1f5442`

Branch: `research/codex-n1-independent-k2-20260826`

Status: `CANDIDATE`; submission remains closed

## Construction

The 128-bit branch-B operand is split into 64-bit halves `a` and `b`.  Its
existing 256-bit product register is populated with

```text
x^2 = a^2 + 2^64 ((a + b)^2 - a^2 - b^2) + 2^128 b^2.
```

The two 64-bit triangular squares land directly in the disjoint low/high
halves of the product register.  A 65-bit `a + b` register and a 130-bit cross
register remain live across the two existing branch-B folds.  The cross term
is added through all 192 bits of `product[64..]`, so its carry can propagate
through `b^2`.  After the folds, the construction is reversed in exact reverse
order and all workspace is proved clean by the simulator selfcheck.

`SUB4_SQUARE_B_LOCAL_K2=1` enables the candidate.  The default is off and only
the exact value `1` enables it.  An absent flag and `SUB4_SQUARE_B_LOCAL_K2=0`
produce byte-identical default artifacts (SHA-256
`141c33dfdb94b2835902dae2563dcf04270933604465af1e8423f6f7aa2ecfe5`).

## TDD evidence

The test contract was written and run before implementation.  RED: flag `1`
produced the unchanged baseline metrics, so the required >=2,000-Toffoli
saving assertion exited 1.  GREEN:

```text
baseline  55,111 emitted / 54,882.297 executed T / 1,153 peak qubits
candidate 52,617 emitted / 52,395.047 executed T / 1,222 peak qubits
delta     -2,494 emitted / -2,487.250 executed T / +69 peak qubits
```

Both paths passed 64-lane exact source/output comparison, phase `0`, and clean
ancilla checks.  The test also proves that an invalid flag value stays on the
baseline path.

Reproduction:

```sh
./test_product_square_b_local_k2.sh
```

## Full-circuit controlled profiles

All profiles used the same freshly built release binary and a clean
environment.  These are local 64-lane profile measurements, not official
admission results.

| configuration | qubits | ops | executed T | correctness |
|---|---:|---:|---:|---|
| stock structure | 1,266 | 12,558,662 | 909,027.03 | 0 classical / 0 phase / 0 dirty |
| branch-B K2 | 1,266 | 12,517,407 | 906,499.08 | 0 classical / 0 phase / 0 dirty |
| stock + asymmetric cap | 1,265 | 12,562,146 | 909,224.67 | 0 classical / 0 phase / 0 dirty |
| branch-B K2 + asymmetric cap | 1,265 | 12,520,891 | 906,761.45 | 0 classical / 0 phase / 0 dirty |

At Q1266 the local score proxy improves by about 3.20M.  Stacking the already
measured asymmetric cap gives a Q1265 proxy about 3.82M below the current
official score.  Execution-weighted profile counts vary with the deterministic
simulator stream after any op-stream edit; they are useful projections, not an
official score or a clean-nonce result.

The candidate's full-circuit peak remains in `pp_div_replay`, not in the square.

## Build and test status

- `cargo build --release --locked --bin build_circuit --bin eval_circuit`: PASS.
- `cargo test --locked --lib`: PASS (the library target contains zero tests).
- Candidate selfcheck contract: PASS.
- Three full-circuit PP profiles above the baseline control: PASS at 64 lanes.
- `git diff --check`: PASS.
- `cargo test --locked --bin build_circuit`: source-wide baseline blocker.  The
  pristine `64f9aaa` worktree fails the same target at compile time with the
  same pre-existing missing direct-centered symbols and stale simulator APIs.

## Remaining gates

1. Independent review of the exact patch and test contract.
2. Freeze the candidate source/tree and compressed artifact hashes.
3. CPU/GPU evaluator parity on that exact artifact.
4. Bounded nonce search for this exact op stream; no island transfers from a
   different circuit.
5. Untouched official 9,024-shot `0/0/0` validation at the winning nonce.
6. Independent clean reproduction, strict live score beat, then submission.

Until all six gates close, this is a high-margin structural candidate rather
than a leaderboard win.

## Provenance

The campaign's reduced-width direction was suggested by Justin Drake.  The
algebra, implementation, TDD contract, and measurements in this worktree were
independently derived and executed by Codex.  No provider or submission action
was taken in this lane.
