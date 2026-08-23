# Live 087cafa tape architecture state

Updated: 2026-08-23T02:12:00Z

Status: `ACTIVE_ONE_PRIMITIVE_FALSIFIER`; exact source preserved, no worker or
scan is running from this worktree.

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

The separate current-source carry composition reached Q1274 but was 242 T over
its score budget before a full run. It is comparison evidence, not a tape
result and not a reason to duplicate that lane.

## Next falsifiable experiment

Test one production carry cell in which the already-live sign wire hosts one
otherwise clean ladder carrier while its logical sign is preserved and then
restored. First produce a source-indexed proof that the sign has no concurrent
read during the host interval. Then exhaust the complete Boolean cell domain
and require value equality, restored sign/source/carry-in, and phase/ancilla
zero. KILL immediately on a concurrent sign read or any measurement-phase
debt.

Only if the cell passes may an environment-gated source-exact prototype be
placed at all three ping-pong Q1275 owners. The global composition gate then
requires the independent square wall to fall as well, Q1274, diagnostic T
below the 919693 ceiling, and finally an unchanged full 9,024-shot `0/0/0`.
No nonce hunt, provider work, or submission is authorized from this lane.
