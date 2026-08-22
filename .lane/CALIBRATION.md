# Q1275 R2=625 predictor calibration

Date: 2026-08-23

Status: **PASS — 16/16 fresh trusted comparisons, zero undercounts, zero
overcounts.**

## Frozen target

| Field | Value |
|---|---|
| Base source | `940e34acbc9cdc9ac497f67eea40db80551d1f7c` |
| Defaults | `PEAK=1275 SQUARE_LADDER=245 R1=342 R2=625` |
| Promoted nonce | `176078461220` (unchanged; no nonce bake) |
| Emitted ops | `12,953,930` |
| `ops.bin` bytes | `51,226,250` |
| `ops.bin` SHA-256 | `83b66b7ef8e5080924f96faa0970a625044eb9d1e58fa2f6a75d162a3bb850d8` |
| `ops.bin` MD5 | `7464046369b46251d49e5ee03af881c5` |
| Qubits | `1275` |
| Bits | `961900` |
| Target semantic state digest | `6403052ff4377d60` |

Fresh release build used an empty target directory:

```text
CARGO_TARGET_DIR=/tmp/q1275-r2625-target.fzkjGY \
  cargo build --release --locked --bin build_circuit --bin eval_circuit
```

The local macOS binaries were SHA-256
`9e4540a358da372d792382ef7b9211d63fd4380d362c1cbd9001b81551f93b97`
(`build_circuit`) and
`d223dc58dc45de996b3a84999ca9ce383b58beccedaa4a5682de48da029fc7a5`
(`eval_circuit`). They are build receipts, not Linux deployment binaries.

At the inherited nonce, the unchanged trusted evaluator ran all 9,024 shots:

| Metric | Exact result |
|---|---|
| Total executed Toffoli | `8,292,747,196` |
| Average executed Toffoli | `918,965.779698581551` (display `918,965.780`) |
| Rounded T | `918,966` |
| Q x rounded T | `1,171,681,650` |
| Classical / phase / ancilla | `14 / 11 / 0` |
| CPU predictor classical | `14` |

The dirty result is expected and is not promotable. Its purpose is exact target
identity and predictor calibration.

## Predictor identity and binding

The current cc20 CPU predictor source SHA-256 is
`93d2853b2047aa8162579eeab1e6cb2abfc0775f680e528e6e14e30e76825314`.
The tested local binary SHA-256 is
`f763f770527117be409123ae23ab8ceeecac1d5b8d7ee4e698d468f375f58128`.
Every predictor invocation used `PPF_ROUNDS_DIV=698`,
`PPF_ROUNDS_MUL=696`, and `PPF_OPS` pointing at the frozen target above.
The op SHA and header count were checked before the comparison run.

## Fresh trusted comparisons

Each nonce below was first predicted from the frozen base stream, then patched
into an isolated copy of that stream and run through the unchanged trusted
evaluator for all 9,024 shots. Every evaluator loaded 12,953,930 ops at Q1275.

| Nonce | Pred cls | Trusted cls | Phase | Anc | Delta |
|---:|---:|---:|---:|---:|---:|
| 111000001147 | 2 | 2 | 2 | 0 | 0 |
| 111000001116 | 4 | 4 | 5 | 0 | 0 |
| 111000001059 | 5 | 5 | 4 | 0 | 0 |
| 111000001027 | 6 | 6 | 7 | 0 | 0 |
| 111000001023 | 7 | 7 | 5 | 0 | 0 |
| 111000001006 | 8 | 8 | 5 | 0 | 0 |
| 111000001013 | 9 | 9 | 8 | 0 | 0 |
| 111000001000 | 10 | 10 | 9 | 0 | 0 |
| 111000001011 | 11 | 11 | 16 | 0 | 0 |
| 111000001005 | 12 | 12 | 11 | 0 | 0 |
| 111000001002 | 13 | 13 | 15 | 0 | 0 |
| 111000001026 | 14 | 14 | 13 | 0 | 0 |
| 111000001049 | 15 | 15 | 16 | 0 | 0 |
| 111000001010 | 16 | 16 | 9 | 0 | 0 |
| 111000001007 | 17 | 17 | 16 | 0 | 0 |
| 111000001074 | 18 | 18 | 9 | 0 | 0 |

Aggregate: `exact=16 under=0 over=0`. The deliberately selected spectrum
includes low-count boundaries 2, 4, 5, and 6 rather than relying only on
ordinary-count fixtures.

Generated fixture ops and logs are intentionally outside Git under
`/tmp/q1275-r2625-calibration.zvH3hc/`. They are disposable evidence; this
table is the durable result.

## Shared CPU/GPU model check

The patched C++ CPU reference accepted only the frozen op count and state
digest. Its per-shot fault-mask output was byte-identical to the Rust oracle
for the inherited nonce and fresh fixtures with counts 2, 9, 14, and 18.
It rejected the cc20 stream, the superseded R2=620 stream, and a one-bit wrong
expected state digest with exit code 2.
