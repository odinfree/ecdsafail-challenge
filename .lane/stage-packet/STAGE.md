# Q1274 repair-r100 — sealed Linux CPU/CUDA parity stage packet

This packet is the durable, self-contained sealing of the classical-fault
**search-model** qualification for the Fable Q1274 sparse width-repair stream.
It vendors the exact frozen predictor sources, binds them by hash to the
repaired artifact, and carries the two things this git branch was missing: a
**local fail-closed CPU verification** that runs here, and a **Linux/CUDA
parity stage runner** that reproduces the terminal parity gate.

It launches nothing. No provider, remote host, range scan, nonce hunt,
submission, or public note is invoked by any file here.

## Bound target (single stream)

| identity | value |
|---|---|
| circuit source commit | `fe0b7bac6348fb35b7680784d4295899e498d0e3` |
| evidence commit | `d793aa293823b7541c933fa666dd5fc830ac58ea` |
| worktree HEAD | `4aebb8bdc347761cb9dc3e07dcae82678d181fec` |
| `ops.bin` op count | `12,920,073` |
| `ops.bin` SHA-256 | `4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c` |
| peak qubits | `1,274` |
| predictor state digest | `d2c95102cb9a277d` |
| divide / multiply rounds | `698 / 696` |
| sampled-index map | `floor(r * 703 / 697)` (both traversals) |
| repair | `+1` bit at the 100 source `WIDTH_REPAIR` indices |

The repaired `ops.bin` was reproduced **byte-for-byte from this worktree's HEAD**
by a clean `build_circuit` release build with no env overrides (op count and
SHA above). That reproduction is the root binding for everything below.

## Fail-closed stream binding (three gates, shared CPU/CUDA loader)

`pp_load_prefix` (in `src/pp_host.h`) refuses any stream that is not the
canonical repaired artifact, before any corpus derivation:

1. `QECCOPSZ` framing;
2. exact op count `12,920,073`;
3. full in-process SHA-256 `4c68597468…` (portable implementation, not a shell
   hash);
4. canonical checkpoint/tail **state digest** `d2c95102cb9a277d`.

Any failure exits `2`. Verified locally (see below) on the two frozen negatives.

## What is proven, and where

- **Local CPU (arm64, this machine) — RE-VALIDATED HERE.** `verify_local_cpu.sh`
  reproduces `ops.bin` (`4c68597468…`), seals the vendored payload against
  `MANIFEST.sha256`, builds `ppcpu` from the vendored source, and reproduces the
  frozen **323-row** classical failing-shot ledger EXACTLY over the 22
  regression cases (`fixtures.local.tsv`), mask totals `1:136 2:18 4:148 8:21
  16:0`. Both fail-closed negatives return exit `2` — the wrong-count stream
  (`12,921,096`) and the same-count / byte-16-altered stream whose SHA is
  exactly `4daf97cffbdfd19fdd6df22d0d8861af49d6b11e0d87f43cb50aafbc85a04e38`.
  The local binary hash is deliberately NOT bound (Apple clang ≠ the frozen
  arm64/Linux binaries); the binding is **behavioural** — identical per-shot
  masks.

- **Linux CPU/CUDA parity — ALREADY PASSED upstream; reproducible here.** The
  terminal 32-fixture parity gate ran on a Linux+CUDA host during the original
  qualification and passed: 32/32 fixtures with CPU (comb8) == GPU comb8 ==
  GPU comb16 complete per-shot mask sets, 64/64 CUDA state-digest checks, total
  predicted faults 457, mask totals `1:178 2:34 4:203 8:42 16:0`.
  - Linux CPU SHA-256 `18f170804a2ca40363a0df3a6f5a86ba33ba92d6fdbe372869e30e0950d7d65d`
  - Linux CUDA SHA-256 `e7b33611ef13bdd5fa89421cdd5ee802793ef9c2f60542419b2d19ed4ad79032`
  - parity-results SHA-256 `924e31aee95e360eb742fb3bb3de9122552d8efce2a74828dacd7bac1ef130d1`

  `run_linux_parity.sh` re-runs exactly this gate from the committed packet on
  any Linux+CUDA host (`nvcc` sm_89, `g++`, `zstd`). It rebuilds both binaries
  (no pipeline may mask the compiler exit), records their hashes (gate 1),
  asserts the state digest on both GPU legs (gate 2), and requires exact
  complete mask-set equality — passing `--comb-bits 8` **explicitly** for the
  CPU-matching leg, since `ppgpu` defaults to comb16.

## Limitation carried into the receipt

The **result channel (mask 16 / `PP_F_RESULT`) is unexercised.** It is 0 across
all local regression fixtures (323 rows) and all 32 parity fixtures (457 rows).
CPU/CUDA parity on that channel is therefore NOT proven by this canary,
regardless of a green run. The only mask-16 evidence is the base-port code-path
identity recorded upstream in `MASK16-CODEPATH-AUDIT.md`; that is inheritance
evidence, not a repaired-stream observation. Both runners emit
`mask16_observed=0` explicitly so a pass is not mistaken for full-channel
coverage.

## Provenance of the upstream evidence (read-only, not re-run here)

- predictor sources + 323-row ledger: `~/ecdsa-ops/gpu-port-q1274-repair-r100`
  (`PREDICTOR.md`, `CORE.sha256`); vendored here byte-identical (`MANIFEST.sha256`).
- 32-fixture parity + Linux binaries + canary: `~/ecdsa-ops/q1274-repair-r100-packet`
  (`STATE.md`, `LINUX-PARITY-RECEIPT.md`, `CANARY-SHARD-RECEIPT.md`). The sole
  authorized lane04 canary there is terminal: one survivor `100000035106674`
  evaluated `0/2/0` (phase-dirty), not a clean candidate. No further shard,
  extension, or submission is authorized, and none is initiated from this packet.

## Contents

```
src/pp_host.h  src/pp_model.h  src/ppcpu.cpp  src/ppgpu.cu  src/build.sh
PARITY_FIXTURES.tsv    32 deterministic, self-verifying, <2^48 parity nonces
fixtures.local.tsv     323-row classical failing-shot ledger (22 cases)
MANIFEST.sha256        seals every payload file above
verify_local_cpu.sh    local fail-closed CPU canary (run here)
run_linux_parity.sh    Linux+CUDA 32-fixture parity stage runner
```

Generated artifacts (`ops.bin`, compiled `ppcpu`/`ppgpu`, patched negative
streams, per-fixture mask files) are scratch-only and never committed.
