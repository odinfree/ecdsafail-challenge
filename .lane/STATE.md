# Live 087cafa tape architecture state

Updated: 2026-08-23T02:36:25Z

Status: `HOLD_Q1274_FULL_DIRTY`; the structural composition is preserved, but
its only unchanged full evaluation failed. No worker or scan is running from
this worktree.

## Exact source and frontier

- Worktree: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/kimi-q1274-tape-087cafa`
- Branch: `research/kimi-q1274-tape-087cafa`
- Source HEAD: `087cafaef46a4e339644a6191ff2df2e7031cb80`
- Live frontier refreshed with `ecdsafail benchmark` on 2026-08-23: source
  `087cafa`, score `1171689300`.
- Promoted receipt: Q1275, average T918972.304, rounded T918972,
  12,953,930 emitted operations, operation SHA-256
  `d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124`,
  unchanged full 9,024-shot classical/phase/ancilla `0/0/0`.
- Strict Q1274 ceiling against that score: rounded T at most 919693.

Before restart recovery, tracked source was clean and `.lane/KIMI_TASK.md` was
the only untracked lane material. No source edit or generated benchmark
artifact was recovered here.

## E001: exact-source four-owner census

A forced release build and environment-only profile were run from HEAD. The
binary wrote `ops.bin` only inside fresh `/tmp/q1274-tape-*` directories. The
worktree received no `ops.bin`, log, score, or result change.

The profile reproduced the promoted stream byte-for-byte:

- emitted operations after the identity tail: 12,953,930;
- operation SHA-256: `d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124`;
- diagnostic 64-lane average T: 918995.67;
- diagnostic classical/phase/ancilla: `0/0/0`;
- peak: Q1275.

The complete Q1275 owner set is:

| phase | first Q1275 op | binding ownership |
|---|---:|---|
| `pp_div_replay` | 2,542,615 | 341 walk signs, 256 caller numerator, 256 replay coefficient, two 145-wire walk slices, 129 replay carries, three singletons |
| `square_product_register` | 6,784,834 | independent square wall; 258 product, 244 ladder, two 129-wire square groups, 138 restored divide wires, 106 residual walkback wires, and small boundaries |
| `pp_mul_replay` | 8,234,520 | 695 walk signs, 256 caller numerator, 256 replay coefficient, 62 replay carries, six boundaries/singletons |
| `pp_mul_walkback` | 8,622,659 | 625 remaining walk signs, 256 caller numerator, 256 replay coefficient, 62 carries, two 28-wire growing walk slices, 14 reacquired replay wires, six boundaries/singletons |

Every row is an exact B0 owner snapshot whose group counts sum to 1275. The
source hashes used for this receipt are:

- `src/point_add/pingpong_div.rs`:
  `51bd4fb2ec793fc024bc8b8bdd3417519bf3b00742063f41f4939e2c6bead242`;
- `src/point_add/mod.rs`:
  `c91ae102b8a0e8d97aa40a6ed06355ef3e188fe2a3e71edb4e2ebf96f7c46947`;
- local macOS release `build_circuit`:
  `8dacd2a899ab66f9a93d90236a33e9da437443e89355c21bf021c9a33a711a67`.

This experiment did not rerun the full evaluator. Its `0/0/0` is the local
64-lane profile; the full `0/0/0` above belongs to the unchanged promoted
receipt.

## E002: sign-host plus residual square composition

The predeclared sign-host carrier cell was implemented behind exact opt-in
flags; the promoted default path remains byte-identical:

- `SUB4_PP_SIGN_HOST_CARRY=1` reuses the already-live logical sign while a
  binding ping-pong carry allocation is active;
- `SUB4_REMAINING_SOURCE_CARRY_Q1274=1` uses the reversible source-host
  MAJ/UMA cell at the remaining divide-replay and independent-square walls;
- `SUB4_PP_SIGN_HOST_CELL_SELFTEST=1` runs the focused cell miters without
  building the full circuit.

The complete reachable sign-host domain passed for both target-zero arms
(128 states). The source-host MAJ/UMA domain passed for all 16 states. Both
miters restored every logical input and reported phase/ancilla zero. The
64-lane point-add selfcheck then passed at Q1274 with 960,468 emitted and
919,531.750 executed Toffoli. The standalone product-register-square
selfcheck also passed with 58,929 emitted and 58,702.203 executed Toffoli.

The exact composed 64-lane profile was classically and reversibly clean and
measured:

| phase | executed Toffoli | peak Q |
|---|---:|---:|
| `pp_div_replay` | 264182.31 | 1274 |
| `square_product_register` | 58704.19 | 1274 |
| `pp_mul_replay` | 24871.31 | 1274 |
| `pp_mul_walkback` | 307720.56 | 1274 |
| complete circuit | 919436.27 | 1274 |

All other measured phase owners were below Q1274. The composed stream emitted
12,954,750 operations with SHA-256
`02771ac1d290406e9cd22ad05d611f3bb3ba875094e6dcc8d177b66cac54b208`.
Rounded diagnostic T919436 is 257 below the strict Q1274 ceiling and projects
to score 1,171,361,464, 327,836 below the refreshed frontier. This is only a
diagnostic projection, not a valid benchmark score.

The score and structural gates allowed exactly one unchanged inherited
9,024-shot evaluation. It failed with classical/phase/ancilla `13/13/0`.
The evaluator recorded average T919451.893 and Q1274 on the failed stream, but
the dirty result is not scoreable and is not eligible for a nonce hunt.

Exact provenance:

- candidate `src/point_add/pingpong_div.rs` SHA-256:
  `5ca77630a8112988c438d5aad8cf66ba24d074d208b2c3ef8510698e89911326`;
- candidate `src/point_add/mod.rs` SHA-256:
  `77a55f878008f5ffacb036e31d1fb2da616227d53d41dce1abb354071d80fdd9`;
- local macOS release `build_circuit` SHA-256:
  `1dd1c3decaadb068b84027fc7344ca1e89b53797018fa762ca3f4a85ae1e680d`;
- unchanged local `eval_circuit` SHA-256:
  `94dc4af2a4c021c96a893ff5fb109ddfe456c16abe46f41e3ca2d152df124481`.

A fresh default build with both composition flags absent reproduced exactly
12,953,930 operations and the promoted operation SHA-256 `d9737f...b124`.
The source-host cells add 472 emitted Toffoli relative to the promoted stream;
the sign-host path adds only Clifford/reset work.

## Recovered structural verdict

Tape replacement remains open, but a tape-only cut cannot lower global Q:
the independent square phase is also Q1275. Any successful tape primitive
must lower all three ping-pong owners and then compose with an already exact
square cut. The current source has two distinct histories: 341 signs at the
divide binder and 695 signs at multiply replay, falling to 625 by the first
multiply-walkback binder.

Closed premises remain closed:

- ordinary full-history Bennett erase/rebuild adds about 395k executed T and
  leaves the old peak flat;
- an untagged O(1) local decoder cannot recover transition-zone signs from the
  post-walk pair;
- a literal raw checkpoint approaches the information floor only by paying an
  unwalk/rewalk tax above the priced saddle;
- the 256-wire replay coefficient remains a live operand at the multiply
  binding interval.

The sign-host composition overturns the width premise: the logical sign can
host one binding carrier without a local correctness or phase debt, and all
four peak owners compose at Q1274 under the opt-in flags. The inherited nonce
nevertheless fails full evaluation at `13/13/0`, so the exact stream is frozen
as structural evidence rather than promoted or hunted.

## Next falsifiable experiment

Do not spend another full evaluation or start a nonce grind on this stream.
If this architecture is resumed, first reduce the 472 paid source-host
Toffolis or port the proven sign-host primitive into the strongest independently
validated Q1274 stream. Any hunt would additionally require a source-bound
exact predictor qualification and a pred0 canary. No nonce hunt, provider
work, or submission is authorized from this lane.
