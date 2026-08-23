# Q1274 exact-carry plus replay-compare19 composition

Status: **structurally/economically ready and locally predictor-qualified;
fleet launch remains closed.**  The inherited nonce is dirty.  A source-exact
local predictor matched the inherited control plus five pre-registered full
9024-shot fixtures exactly in classical count and failing-shot set, with zero
ancilla garbage.  Linux CPU/GPU 32-fixture parity and a deterministic pred0
canary remain open.  No hunt, provider action, submission, or promotion was
performed from this lane.

## Frozen input and sole composition

- Created UTC: `2026-08-23T00:26:21Z`
- Worktree: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/q1274-compare19-compose`
- Branch: `research/q1274-compare19-compose`
- Exact parent: `8d261ea9449bcd37c9a6d9a1d981a90761ec7b57`
- Parent tree: `15c6b8a83b4c83104121645a9eb598eb989ab246`
- Live source anchor behind the parent: `087cafaef46a4e339644a6191ff2df2e7031cb80`
- Sole circuit mutation: change the baked default for
  `SUB4_PP_REPLAY_CHUNK_COMPARE` from `20` to `19` in
  `src/point_add/pingpong_div.rs`.
- The compare notch is copied exactly from measured commit
  `4aedb3104d86a1d07fe46a4d20167a2424d44eda`; no other source edit from that
  lane is composed.
- Candidate `pingpong_div.rs` SHA-256 before commit:
  `c30037146bf83dfc56fe59428cedfe62973f2b4ce4e3ef471175b97d45066909`.

The parent supplies the exact, binding-only Q1274 carry package:

```text
SUB4_PP_DIV_WALK_TOP_CARRY_HOST=1
SUB4_PP_MUL_WALK_TOP_CARRY_HOST=1
SUB4_BINDING_SOURCE_CARRY_Q1274=1
```

Its frozen parent measurement was Q1274, seed-zero diagnostic average
T919919.48, and 64-lane `0/0/0`.  The compare20 to compare19 notch measured
-1146.494 average T on the exact live Q1275 source.  Transfer is a hypothesis,
not evidence: this lane must measure the composition directly.

## Pre-registered gates

1. Force a clean, locked, offline release build.  Stale `ops.bin` and target
   artifacts are not evidence.
2. Re-run the source-host Boolean identities: all 8 MAJ/UMA input states and
   all 32 final-carry/output-host states must agree with their reference maps.
3. Run the production ping-pong source-host self-check with the three Q1274
   gates enabled.  Both directions must preserve the ABI, phase must be zero,
   and every non-ABI qubit must be clean.
4. Run a full 64-lane `PP_PROFILE=1` point-add measurement with the three gates
   enabled.  Require `classical_mismatch=0`, `phase=0x0`, and
   `dirty_qubits=0`.
5. Trace every global peak co-binder.  Require Q1274 and prove that no phase
   reaches Q1275.
6. Score gate: rounded diagnostic/full estimate must be at most T919693,
   implying projected score at most `1274 * 919693 = 1171608882`, strictly
   below live score `1171689300`.
7. Only if gates 1-6 pass, run exactly one unchanged inherited-nonce full
   9024-shot diagnostic.  Record classical/phase/ancilla and operation SHA-256.
   A dirty inherited nonce is not a structural rejection because compare19 is
   island-graded; it only establishes that re-qualification is required.
8. Do not scan, touch providers, or submit from this lane.  Hunt readiness also
   requires a source-exact predictor guard and compatibility proof.

## Evidence ledger

### Build and focused exactness gates

- A clean/offline/locked release build was performed twice: once before the
  focused checks and once after removing the temporary self-check entrypoint.
  The final build completed from a zero-target state.
- Exhaustive source-host miter:
  `SOURCE_HOST_MITER PASS maj_uma=8/8 walk_output=32/32`.
- Temporary miter source SHA-256:
  `13c4d769831f673f8cda9a4b19406781f9d226df2d31606c6b4ca9e38c129966`.
  It was kept outside the worktree and is not committed.
- Production component self-check with all three Q1274 gates enabled:
  - divide: Q1274, 450038 emitted / 430178.5 executed Toffoli;
  - multiply: Q1274, 449139 emitted / 429421.5 executed Toffoli;
  - ABI values matched in both directions, phase was zero, and every non-ABI
    qubit was clean;
  - terminal receipt: `SOURCE_HOST_PRODUCTION_SELFCHECK: PASS`.
- The repository-wide `cargo test` target remains non-buildable because of
  unrelated stale archived tests and missing archived symbols.  The focused
  component is intentionally callable without that target; a temporary
  release-bin entrypoint invoked it, then the entrypoint and temporary module
  visibility change were removed.  Final Git diff contains neither.

### Direct composition measurement

The full 64-lane `PP_PROFILE=1` run with all three Q1274 gates enabled passed:

```text
PP_PROFILE peak_qubits=1274 peak_ops_idx=2538535 peak_phase=pp_div_replay
TOTAL ops=12920918 ccx=958594 ccz=28 exec_tof=918677.30
PP_PROFILE lanes=64 classical_mismatch=0 phase=0x0 dirty_qubits=0
```

The 96-op identity tail brings the exact stream to 12921014 operations.  Its
SHA-256 is
`28ed9f5d4e9eccf222aa12a28d6fbf311d6f1c76daa62984c63d42a3f8f63955`.

Every global co-binder is Q1274; the complete phase maxima at the top are:

| phase | peak Q | 64-lane executed T |
|---|---:|---:|
| `pp_div_replay` | 1274 | 263532.52 |
| `square_product_register` | 1274 | 58701.34 |
| `pp_mul_replay` | 1274 | 25066.88 |
| `pp_mul_walkback` | 1274 | 307413.19 |

No phase reaches Q1275.  The diagnostic rounded T is 918677, yielding projected
score `1274 * 918677 = 1170394498`, 1294802 below live score 1171689300 and
1016 T below the Q1274 ceiling.

### One inherited-nonce full diagnostic

Exactly one trusted full 9024-shot evaluation was run on the unchanged baked
nonce `251000962439`:

```text
tested shots            : 9024
classical mismatches    : 15
phase-garbage batches   : 17
ancilla-garbage batches : 0
```

The failed evaluator row still prices average executed T at 918758.806;
rounded T918759 implies clean-island score 1170498966, 1190334 below live and
934 T below the Q1274 ceiling.  The exact evaluated operation hash is the
same `28ed9f5...f63955` above.  Full-evaluator log SHA-256:
`8633b3eea6c93c06ca1d15794e81793c4b40b27ec2431a15137825aaaa3bc549`.

This `15/17/0` is compatible with an island-graded compare19 notch and does
not contradict the exact source-host proofs or clean 64-lane production
self-check.  It does prove that the inherited nonce is not a candidate.
`results.tsv` was restored byte-for-byte after recording the receipt; no
generated result row is committed.

## Predictor qualification and next action

The full local qualification, target state digest, source/binary hashes,
wrong-stream negatives, exact six-nonce fault sets, deterministic future
canary rule, and remaining fleet gates are in `.lane/PREDICTOR.md`.  Local
classical parity is `6/6` by count and complete shot set; all six full runs
have ancilla zero.  The temporary predictor rejected the two neighboring
known streams with exit `2`.

The next allowed action is a production Linux CPU/GPU packet: enforce the
target state digest, prove 32-fixture CPU/GPU8/GPU16 mask parity with all fault
classes covered, then close the pre-registered pred0 canary.  Only a separate
lane that closes both gates may begin a non-overlapping nonce hunt.  This lane
itself remains no-scan and no-submit.
