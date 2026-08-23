# KILL — no new production-reachable fused inverse exists

Resolved: 2026-08-23. Lane: `research/b523-fused-reachable-inverse`.
Binding predeclaration: `.lane/TASK.md`, commit `2e98882`.
Frozen parent: `9fb89d3e6d0cf1c26a880dcacd3c560c3970ef7a`.

## Verdict

**Terminal KILL at Gate 5.** On the frozen production-reachable corpus, the
existing `signed_mod_double_add_pm_fused` is already a bit-exact inverse of
`signed_mod_add_pm_halve_fused`: focused target/source/sign/phase/ancilla is
`0/0/0/0/0` over 79,205 unique tuples. There is therefore no new inverse source
to implement or price. The unchanged full circuit measures Q1278/T919785 and
scores 1,175,485,230, which loses the fresh leader 1,169,101,620 by 6,383,610.

No candidate inverse was written. The only source addition is a default-off
trajectory/miter instrument. No second family, window tuning, nonce change,
provider, hunt, or submission was opened.

## Exact characterization

Command:

```text
SUB4_PP_FUSED_TRAJECTORY_TRACE=1 ./target/release/build_circuit
```

Measured receipt:

```text
FUSED_TRAJ op_stream_identity=OK ops=12972689 stream_sha256=048c3a42ab1375dc4c67a222ed3ecefbd2602c8fce0ee8a220886c9b904f3c17
FUSED_TRAJ P64 classical=0 phase=0 ancilla=0
FUSED_TRAJ calls halve|divide=696 double|multiply=694 other=0 rows=88960
FUSED_TRAJ canonicity noncanon_target_before=0 noncanon_target_after=0 noncanon_source=0 (of 88960)
FUSED_TRAJ range max_target_before=0xffffbcf6abac71a721c2594566a34fbb2b65b50eeeaea85c216cbd1628585045 max_noncanon_before_minus_p=0x0 p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
FUSED_TRAJ rows_sha256=798b8c1c2f92b8af4b95a2b2df7ec7a7b7238e8a957614ccda993ccb77d4e63e
FUSED_TRAJ C64 unique_tuples=79205 corpus_sha256=2e3ca70d1879b85ddcaae72fa571424e955a4b92ea3523ac4fa0bc8659ef5126 restore_fail=0 source_fail=0 sign_fail=0 phase_fail=0 ancilla_fail=0 verdict=EXACT_INVERSE_ON_REACHABLE
```

The 12,972,689-operation identity is for `build_pingpong_point_add()` before
the normal build appends its 96 identity-tail X operations. The recorder is
enabled only while the diagnostic constructs that point-add stream, adds no
operation or wire, then rebuilds with tracing disabled and asserts exact stream
identity.

P64 uses the frozen 64 valid affine point pairs and SHAKE domains from
`pingpong_point_add_simulator_selfcheck`. It observes every round-2-or-later
fused call in both live directions:

- 696 forward halve calls in the Divide pass;
- 694 double-add calls in the Multiply pass;
- 88,960 call/shot rows total;
- every source, target-before, and target-after is canonical `< p`.

The row digest hashes, in call/shot order, direction bytes, little-endian u64
call index, little-endian u64 round, sign byte, and little-endian 32-byte
source/target-before/target-after. The C64 digest hashes the lexicographically
deduplicated `(sign, source, target-before)` corpus. Both are SHA-256 as frozen
in the predeclaration.

The cell bodies are round-independent; round and direction remain in the P64
row receipt, while C64 merges value-identical tuples before replay. No failed
row is filtered, and the original multiplicity remains explicit as 88,960 rows
versus 79,205 unique tuples.

## Scope of the result

Both cells are live in one production point-add but in different arithmetic
passes: the halve cell in Divide and the double-add cell in Multiply. The C64
miter deliberately composes them on the union of their frozen production inputs
to answer this lane's inverse question. It does not claim arbitrary `[0,p)`
closure.

The unchanged A16 negative control confirms that boundary:

```text
signed_mod_add_pm_halve_fused|signed_mod_double_add_pm_fused
restore_fail=3 phase_fail=2 ancilla_fail=0 verdict=NOT_INVERSE
```

Thus the old pair remains non-inverse on arbitrary canonical inputs near lazy
reduction/truncation boundaries, while the measured production support stays
canonical and exact. Narrowing A16 or relabelling it was not permitted and did
not occur.

## Gate ledger

| gate | measured outcome | verdict |
|---|---|---|
| 1 — protected default | 12,972,785 ops; 50,798,742 bytes; SHA256 `e33245d491a16192068ef7024a2c82375047c17af3c8f802c81066de0568cb0a` | PASS |
| 2 — P64 trajectory | trace identity exact; 1,390 calls; 88,960 rows; P64 `0/0/0` | PASS |
| 3 — visibility/closure | existing pair needs no added predicate, transcript, or carrier on C64 | PASS for frozen support |
| 4 — focused miter | 79,205 unique tuples; target/source/sign/phase/ancilla `0/0/0/0/0` | PASS |
| 5 — economics | full Q1278/T919785, score 1,175,485,230; leader 1,169,101,620 | **KILL** |
| 6 — full composition | unchanged full 9,024-shot classical/phase/ancilla `0/0/0`; economically losing | clean control, not candidate |

Exact score arithmetic:

```text
1278 * 919785 = 1175485230
1175485230 - 1169101620 = 6383610
strict Q1278 ceiling = floor((1169101620 - 1) / 1278) = 914789

Q1148: T <= 1018381; 1148 * 1018381 = 1169101388
Q1114: T <= 1049462; 1114 * 1049462 = 1169100668
```

An unchanged inverse cannot lower the full score. Making it cheaper would be a
different family (window redesign, new arithmetic, call deletion, or lifetime
composition), all forbidden in this turn. Adding a generic final reduction
would repair A16 but would add cost to a cell already exact on the scoped
support. No rescue tuning is justified.

## Full trusted control

Fresh absent-flag build and evaluation:

```text
loaded/emitted ops       12972785
qubits                   1278
tested shots             9024
classical mismatches     0
phase-garbage batches    0
ancilla-garbage batches  0
avg executed Toffoli     919785.268
rounded Toffoli          919785
```

Generated `ops.bin`, `score.json`, traces, logs, binaries, `target/`, and
`results.tsv` rows are excluded from commits.

## Next architecture recommendation (not opened here)

A separate predeclared lane may reuse the current pair unchanged inside the
retained-word production splice, but only on a fixture proven to stay within
this canonical reachable support. Its first gate must be the nonzero-midpoint
forward/reverse closure that the prior lane could not establish, followed by a
full price at Q1114 against T<=1,049,462. That is an integration architecture,
not an inverse repair, and was not started in this turn.

## Model receipt

Claude Fable 5 high-effort session
`3d8bee9a-89c1-44f8-8d5f-55a82e78b49f`; exact spend `$7.10130975`:
`claude-opus-5` `$1.35698025` plus `claude-opus-4-8` `$5.74432950`.
Spend was appended to `/Users/olifreuler/ecdsa-ops/SPEND.md`. The model had no
shell, network, commit, or push authority; all measurements above are independent
human-side runs.
