# Q1272 E007 Linux/CUDA parity-stage packet

Date: 2026-08-23 (Europe/Zurich)

## Status

`EXECUTED_PASS / HOLD_OVERCOUNT_BOUND / NO_SCAN`

This commit prepares a fail-closed Linux/CUDA fixture stage. The stage later
passed exactly as frozen; see `PARITY-RESULT.md` for binary, receipt, negative,
and protected-state hashes. It did not evaluate a range, start a hunt, mutate
a provider, submit, or authorize deployment. The parity build compiles both
CPU and CUDA range entry points with `PP_DISABLE_SCAN=1`; only diagnostic
fixture modes remain reachable.

The packet follows the receipt structure already exercised by the trusted
Q1276 packet and the wrong-stream/state-digest requirements identified by the
Q1274 qualification. Its fixed stage root is:

```text
/workspace/ev-q1272-e007-ea93a131
```

## Frozen identity

- circuit source: `ea93a131e2bc488bff6fa12010d1f3606c7771b0`;
- operations: `12,943,345`;
- inherited operations SHA-256:
  `4618d4af86c23c06cc72fef26f8a8e5986c7a9de5f804891541a8ce6eb189f37`;
- runtime state digest: `963a662d2e392804`;
- `pp_host.h`:
  `ff609173d16d2cb6d3d69f81b22a1361b42772c3d58c8b83ac836222028ccbaa`;
- `pp_model.h`:
  `609d21cab5ad8dd40180f1a20311d1578b2b6d243133a0137951d3f2dddcc81d`;
- `ppcpu.cpp`:
  `47061664fa5365793e01427c0834dcbee9e01daca16981ba980b9c4f22bbc460`;
- `ppgpu.cu`:
  `bc3acb5867a477d8d50b00a997b38fcab78d92267f9e8906bba9ddff5ab28872`;
- scan-disabled `build.sh`:
  `349287129102bc97aec491c2e0fd6cc7470cbc9ebef64fa567770f94547b2cd7`;
- four-row fixture ledger:
  `ff272f7d203a2f8dc56c21b577f0bcc661ab0dde5390477b239c0bdbe52b3057`;
- inherited exact fault-shot ledger:
  `77c521cb00cbd6fcc32bd6f9accb49d26f1c435b0b79091cf09dbfbd0efc9eaf`;
- `stage_common.sh`:
  `94950be99c0bcafc20373c9d29ebc142679cb026151d1d5558a3fea3a2b43bd9`;
- `stage_dedicated.sh`:
  `d75b797172a8c003e34a084f578d8113dbe43d8a0059d85ced0bcaee78c9a3c4`;
- unarmed `stage_borrowed.sh`:
  `6ddfdc504a710d712b4872e854bb33d4deede274f24c5a21592b5ca8188e8788`;
- unarmed `pilot_tolerant.sh`:
  `55fec31176301fe7c2ab2fe66feffe87feb2bb31afa34a232b26ec9cfd068830`.

The stage asserts these hashes before building. Operation count and state
digest are checked inside both binaries; the exact operation SHA is checked
outside them before either executes.

## Frozen positive fixtures

The four rows remain fixed at nonces `251000962439`, `0`, `7`, and
`2500069332`. For every row the stage requires byte-identical breakdown output
from Linux CPU, CUDA comb8, and CUDA comb16. That equality includes total,
first failure, and all five cause counts.

For inherited nonce `251000962439`, the stage additionally compares the full
ordered 11-line `index mask` output against `inherited-faultshots.tsv`:

```text
2582 1
3967 1
4145 1
4670 4
5353 1
5757 1
6422 1
7544 4
8028 4
8239 1
8443 1
```

All ten CUDA diagnostic invocations must print the single frozen state digest
`963a662d2e392804`. The checked-in fixture table preserves the unchanged full
evaluator's `classical/phase/ancilla` totals and first mismatch; parity does
not rerun or replace that evaluator.

## Frozen negative fixtures

The stage constructs two temporary artifacts and requires both CPU and CUDA
loaders to exit `2` before corpus or kernel work:

1. a wrong-count copy with the header changed from `12,943,345` to
   `12,943,344`;
2. a same-count stream with one nonce-independent image byte changed and the
   body recompressed, giving a different exact SHA and state digest while the
   header count stays fixed.

The first must report the operation-count rejection. The second must report
the same-count unknown-stream rejection. Both artifacts and their logs are
runtime-only and ignored by Git.

## Dedicated and borrowed-host gates

`stage_dedicated.sh` requires exactly one supported GPU, zero compute
applications before and after, an available `sm_89` or `sm_120` compiler
target, no prior receipt or binary, and no candidate process. It emits
`FINGERPRINTS`, `PARITY.complete`, and `DEDICATED.complete` only after every
positive and negative check passes.

`stage_borrowed.sh` is deliberately unarmed. A later reviewed commit must
replace its placeholders with the exact incumbent root, executable, operation
artifact, immutable hashes, assignment bounds, chunk size, and telemetry log.
Once armed, it requires exactly one incumbent process and GPU PID, validates
its exact command and contiguous completed coverage before and after parity,
rechecks immutable hashes, sends no signal, and rejects any pre-existing
candidate process. A parity failure cannot produce `BORROW.complete`.

Exactly one host proof—dedicated xor borrowed—may be consumed by any later
pilot.

## Bounded retention and the strict-zero limitation

CPU and CUDA source now implement complete retention thresholds
`--max-faults 0..3`. For a nonce whose model count is at most the selected
threshold, all 9,024 modeled shots are evaluated and the exact predicted count
is emitted. Counts above the threshold may stop early and are not emitted.

Strict `pred_cls=0` is **not globally safe** for this stream. The retained
fold55 walkback branch is fail-closed and a known older fixture contains one
benign wrapped overflow that the model overcounts. A circuit-true zero could
therefore be discarded by a strict model-zero filter.

`pilot_tolerant.sh` is also deliberately unarmed. Before a future commit can
set `max_faults` to 1, 2, or 3, an exact source-bound proof must establish for
every possible nonce that:

```text
0 <= predicted_classical - true_classical <= B <= 3
```

and the pilot threshold must be at least `B`. That inequality is the retention
argument: every true zero then has predicted count at most `B`, so the tolerant
screen cannot drop it. The proof receipt, its hash, the exact pilot interval,
and a separately hashed scan-enabled binary all require a new reviewed commit.
No such proof exists yet, so no tolerant pilot is authorized.

Every retained row would still require the unchanged full 9,024-shot evaluator
to decide classical, phase, and ancilla. A predictor result is never a circuit
result.

## Runtime artifacts excluded from Git

`ops.bin`, compiled binaries, fixture outputs, negative streams, locks,
fingerprints, completion receipts, proof receipts, scan-enabled binaries,
runs, and logs are ignored. Only source, scripts, frozen ledgers, and this
pre-run contract are committed.
