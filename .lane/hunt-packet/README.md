# Compare-19 local hunt packet

Readiness verdict: **local calibration ready; scan launch blocked**.

The packet binds the rejected compare-19 experiment to exact source commit `4aedb3104d86a1d07fe46a4d20167a2424d44eda`, emitted stream SHA-256 `ae588d6227dddfe5bdb996ae55cd1137d2424fdb3c9ba87dcff30f8e45087ab2`, 12,926,071 operations, and predictor state digest `0c0c07b906775f4f`.

Five SHA-derived nonces were fixed in `FIXTURE_NONCES.tsv` before prediction. The unchanged full 9,024-shot evaluator then matched the predictor's classical fault count exactly on all five (`18`, `10`, `11`, `16`, `17`). The inherited control also matches `9`, including all nine fault-shot indices. Every fixture was phase-dirty and ancilla-clean; none is a candidate.

The five fresh fixtures establish exact count equality, not per-shot index-set equality. No fresh `pred0` canary was produced because this task authorized no scan. Those two missing gates, plus CPU/GPU8/GPU16 parity, keep the packet below fleet readiness.

The fixture derivation is SHA-256 of:

```text
compare19-fixture-v1:ae588d6227dddfe5bdb996ae55cd1137d2424fdb3c9ba87dcff30f8e45087ab2
```

Digest: `6744ead7c2070dc187433e2c766858dcb036c4ab50cc15f3bc4f98e3d5db7e3c`. The five nonces are the first five 48-bit chunks interpreted as unsigned integers. This prevents adaptive fixture selection.

The local predictor binary is diagnostic-only: it has the exact operation-count guard and reports the target state digest, but it is not committed and has not been rebuilt or checked on Linux/CUDA. A launch remains blocked until a production predictor is frozen with full stream identity, wrong-stream rejection, Linux CPU/GPU parity, and a separately authorized non-overlapping range ledger. `RANGE_LEDGER_TEMPLATE.tsv` is deliberately empty.

`verify_local.sh OPS.bin PPCPU EVAL_CIRCUIT TAIL_PATCH` fails closed on source identity, the one-line default, stream hashes/header, predictor/evaluator/patcher hashes, state digest, inherited prediction, byte-exact tail roundtrip, fixture count agreement, and an empty range ledger. Success prints `LOCAL_PACKET_OK SCAN_BLOCKED`; it never starts a scan.

No scan, provider action, host mutation, nonce fleet, submission, or promotion was performed.
