# Tape architecture experiment ledger

## E001 - promoted-source peak and owner recovery

Date: 2026-08-23

Source: `087cafaef46a4e339644a6191ff2df2e7031cb80`

Question: did the restart lose an active structural worker or leave the
promoted-source tape owner set unmeasured?

Pre-existing gate from `.lane/KIMI_TASK.md`: force a clean build, measure the
complete peak-owner set, preserve the exact source, and do not scan, spend,
submit, or use provider compute.

Commands:

```text
cargo build --release --bin build_circuit

PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1 TRACE_PHASE_ACTIVE=1 \
  SKIP_ALT_SEED_CHECKS=1 ./target/release/build_circuit

TRACE_ALLOC_NEAR_PEAK=1275 SKIP_ALT_SEED_CHECKS=1 \
  ./target/release/build_circuit

B0_PHASE=<phase> B0_WIN_LO=<first-10> B0_WIN_HI=<first+10> \
  SKIP_ALT_SEED_CHECKS=1 ./target/release/build_circuit
```

All executions ran with a fresh `/tmp/q1274-tape-*` current directory. Exact
B0 windows were centered at operations 2,542,615; 6,784,834; 8,234,520; and
8,622,659.

Result:

- exact promoted operation SHA reproduced;
- Q1275 owners are divide replay, square product register, multiply replay,
  and multiply walkback;
- B0 snapshots sum to 1275 for every owner;
- diagnostic 64-lane classical/phase/ancilla `0/0/0` at average T918995.67;
- no relevant local structural process was running;
- source remained byte-identical and the worktree gained no generated result.

Decision: `HOLD_TAPE_COMPOSITION`. The tape wall is real, but the independent
square wall proves that tape removal alone cannot change global Q. Proceed
only with the sign-host primitive falsifier named in `STATE.md`, then compose
instead of claiming a local width win.

## E002 - sign-host carrier cell

Status: `HOLD_Q1274_FULL_DIRTY`.

Overturn: a live sign is not only a resident transcript bit; during a bounded
adder interval it may serve as reversible storage for one ladder carrier while
its logical value remains recoverable.

Kill gates:

1. any concurrent read needs the original sign while the host encoding is live;
2. the exhaustive cell miter changes sign, source, accumulator, or carry-in;
3. measurement uncompute leaves phase or ancilla debt;
4. the primitive cannot cover divide replay, multiply replay, and multiply
   walkback, or an uncovered Q1275 owner remains after square composition;
5. the exact composition misses the Q1274 T ceiling.

Implementation:

- `SUB4_PP_SIGN_HOST_CARRY=1` enables the exact production sign-host cells at
  the divide-replay, multiply-replay, and multiply-walkback binders;
- `SUB4_REMAINING_SOURCE_CARRY_Q1274=1` enables the residual reversible
  source-host MAJ/UMA cell at divide replay and the independent square wall;
- both flags are opt-in and absent from the promoted default build.

Focused proof receipts:

- complete sign-host domain: two target-zero arms times 64 logical states,
  128/128 pass, inputs restored, phase/ancilla zero;
- complete source-host MAJ/UMA domain: 16/16 pass including the output bit,
  inputs restored, phase/ancilla zero;
- 64-lane full affine-add selfcheck: 960,468 emitted, average T919531.750,
  Q1274, classical/phase/ancilla `0/0/0`;
- standalone product-register square: 58,929 emitted, average T58702.203,
  Q1275 in isolation, selfcheck clean. In the complete point-add schedule this
  phase binds at Q1274.

Exact complete profile:

```text
PP_PROFILE peak_qubits=1274 peak_ops_idx=2542615
PP_PROFILE lanes=64 classical_mismatch=0 phase=0x0 dirty_qubits=0
emitted operations=12954750
average executed Toffoli=919436.27
operation SHA-256=02771ac1d290406e9cd22ad05d611f3bb3ba875094e6dcc8d177b66cac54b208
```

Peak-owner profile:

```text
pp_div_replay             Q1274 T264182.31
square_product_register   Q1274 T 58704.19
pp_mul_replay             Q1274 T 24871.31
pp_mul_walkback           Q1274 T307720.56
```

The rounded diagnostic T919436 clears the strict T919693 ceiling by 257 and
projects to 1,171,361,464, a 327,836 strict beat of the refreshed frontier.
That projection opened the single permitted inherited full evaluation.

Unchanged full 9,024-shot result:

```text
Q=1274
emitted operations=12954750
classical/phase/ancilla=13/13/0
failed-stream average T=919451.893
```

Decision: KILL the hunt and promotion path. Gates 1 through 5 passed through
the exact composed diagnostic, but the mandatory full correctness gate did
not. No second full run, scan, provider use, or submission was attempted.

Provenance:

```text
pingpong_div.rs  5ca77630a8112988c438d5aad8cf66ba24d074d208b2c3ef8510698e89911326
mod.rs           77a55f878008f5ffacb036e31d1fb2da616227d53d41dce1abb354071d80fdd9
build_circuit    1dd1c3decaadb068b84027fc7344ca1e89b53797018fa762ca3f4a85ae1e680d
eval_circuit     94dc4af2a4c021c96a893ff5fb109ddfe456c16abe46f41e3ca2d152df124481
```

With both opt-in flags absent, a fresh default build reproduced 12,953,930
operations and exact promoted operation SHA-256
`d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124`.
