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

Status: predeclared, not started.

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

No source change is authorized before the read-interval map and complete cell
miter exist.
