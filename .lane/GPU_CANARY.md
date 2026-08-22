# Q1275 R2=625 bounded GPU canary

Status: **TARGET-HOST CANARY PASS; NO FLEET DEPLOYMENT AUTHORIZED HERE.**

## Target-bound artifacts

| Artifact | SHA-256 |
|---|---|
| `ops.bin` (12,953,930 ops; MD5 `7464046369b46251d49e5ee03af881c5`) | `83b66b7ef8e5080924f96faa0970a625044eb9d1e58fa2f6a75d162a3bb850d8` |
| Semantic state digest | `6403052ff4377d60` |
| Guard patch, `.lane/GPU_PORT_Q1275.patch` | `ce046b898530e0cd60b5c48fb50a8d8be606dca1284d2e47c5a3636872f198f3` |
| Patched `src/pp_host.h` | `e51f1b0cdae88a0543f6c55ab8bc58b839123acd4d4f2f38dae9dd4c9c482cce` |
| Unchanged `src/pp_model.h` | `d47f7c5229d5751d30df2fa7936b87fe0b303ae1ad3c6fb97e2fc4ef44ff223e` |
| Patched `src/ppcpu.cpp` | `8099c1aa614208369120113316c4d520596aa4628afc37095c1ecd140b4b6467` |
| Patched `src/ppgpu.cu` | `04fb37c8640a747219b7bd89a3e6d70aeb40728b32ef8d6305ad4a664af05a73` |
| Unchanged `build.sh` | `86955d6633d7f6e3477df237b42ca7053c89c20099e930bcf045f206fcca37af` |
| Target-host CUDA `ppgpu` | `16950112cfa857272f4f1b6cf67f6d2e30df1b1c44e03ab0f794af173c7f6145` |
| Linux x86-64 oracle `ppfilter-rl2` | `7a0dfbb76a503efcb2f2ced4ac30fcc705a1a16213a5db1aff47e1d7001d69ab` |
| Linux `tail_patch` | `e1c5174ae456ea2ac3aa3b1a6377744c1617b81de4060734adf7dc7d80eee313` |
| Unchanged trusted Linux `eval_circuit` | `8efd5d0723c5a4db8d6b46a2665eeb88405943eacba12a995860c79f6043f958` |

The guard patch applies cleanly to the verified local source tree at
`/Users/olifreuler/ecdsa-ops/gpu-port-cc20`. A from-scratch reproduction in
`/tmp/q1275-gpu-patch-repro.Xwot6h` was byte-identical to the patched source.
The guard refuses before CUDA upload unless both the op count is 12,953,930
and the semantic state digest is `6403052ff4377d60`.

## Verified bounded canary

Independent target-host verification built the CUDA binary above and compared
all 16 fixtures in `.lane/CALIBRATION.md` against the trusted results under
both `--comb-bits 8` and `--comb-bits 16`. Result: `16/16` exact under each
comb width. Four wrong-stream controls were refused. This is a fixture canary,
not authorization for a nonce scan.

## Rollback-safe route

- Stage only at `/workspace/ev-peak1275-canary`; never overwrite
  `/workspace/ev-cc20` or its binaries, ops, logs, assignment, or processes.
- Use fixture-only process labels `peak1275_canary_fixture` and
  `peak1275_canary_eval`.
- Verify every SHA-256 above after transfer and before execution.
- Require startup telemetry to print exactly
  `total_ops=12953930 state_digest=6403052ff4377d60`.
- Run `--faultshots NONCE` for the 16 frozen fixtures under comb8 and comb16;
  diff each output against the oracle before any scan command exists.
- Record exact child PIDs in the canary directory. Rollback may stop only those
  recorded PIDs; broad `pkill`, host-global process matching, and live-route
  replacement are forbidden.
- Preserve the staged directory and logs on rollback for diagnosis. Returning
  to the live route requires no mutation because the canary is side-by-side.

The promoted source nonce remains `176078461220`; no nonce is baked by this
packet. A future bounded scan range, fleet expansion, provider action, spend,
or submission needs separate authority and a fail-closed range ledger.
