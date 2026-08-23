# Compare-19 local hunt packet

Readiness verdict: **local calibration ready; scan launch blocked**.

The packet binds the rejected compare-19 experiment to exact source commit `4aedb3104d86a1d07fe46a4d20167a2424d44eda`, emitted stream SHA-256 `ae588d6227dddfe5bdb996ae55cd1137d2424fdb3c9ba87dcff30f8e45087ab2`, 12,926,071 operations, and predictor state digest `0c0c07b906775f4f`.

Five SHA-derived nonces were fixed in `FIXTURE_NONCES.tsv` before prediction. The unchanged full 9,024-shot evaluator then matched the predictor's classical fault count exactly on all five (`18`, `10`, `11`, `16`, `17`). The inherited control also matches `9`, including all nine fault-shot indices. Every fixture was phase-dirty and ancilla-clean; none is a candidate.

`FIXTURE_FAULT_SETS.tsv` closes the stronger local gate: predictor fault-shot indices equal evaluator classical-mismatch indices exactly on all five fresh fixtures. Indices were exposed by adding only one diagnostic `eprintln!` to the unchanged evaluator logic; its binary SHA-256 was `2c0db5b3d74430ed138833b3785fc6b3bffdea7b192847040177c13e01c689d9`. The line was then removed, the ordinary evaluator rebuilt to its frozen hash `a8c2a26ee8992df76408e0484a18e14ba81b5eb21657f156b50d836099edd2a3`, and `results.tsv` restored. The breakdown exercises every modeled non-result class across the set: divide walk, divide replay, multiply walk, and multiply replay. Predictor masks `2` and `8` prove both replay classes fired.

The committed deterministic pred0 bound was locally rate-tested over its first 8,192 ascending nonces. It produced no survivor at `77.465721` nonces/second, projecting `56.40` minutes for the full 262,144 bound. Per the predeclared rule, no alternate range was substituted; `PRED0_CANARY_STATUS.md` leaves only that local gate open. CPU/GPU8/GPU16 parity remains a separate fleet gate.

The fixture derivation is SHA-256 of:

```text
compare19-fixture-v1:ae588d6227dddfe5bdb996ae55cd1137d2424fdb3c9ba87dcff30f8e45087ab2
```

Digest: `6744ead7c2070dc187433e2c766858dcb036c4ab50cc15f3bc4f98e3d5db7e3c`. The five nonces are the first five 48-bit chunks interpreted as unsigned integers. This prevents adaptive fixture selection.

The local predictor binary is diagnostic-only: it has the exact operation-count guard and reports the target state digest, but it is not committed and has not been rebuilt or checked on Linux/CUDA. A launch remains blocked until a production predictor is frozen with full stream identity, wrong-stream rejection, Linux CPU/GPU parity, and a separately authorized non-overlapping range ledger. `RANGE_LEDGER_TEMPLATE.tsv` is deliberately empty.

`verify_local.sh OPS.bin PPCPU EVAL_CIRCUIT TAIL_PATCH` fails closed on source identity, the one-line default, stream hashes/header, predictor/evaluator/patcher hashes, state digest, inherited prediction, byte-exact tail roundtrip, fixture count agreement, and an empty range ledger. Success prints `LOCAL_PACKET_OK SCAN_BLOCKED`; it never starts a scan.

No scan, provider action, host mutation, nonce fleet, submission, or promotion was performed.
