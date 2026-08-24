# Q1266 production-worker runtime CPU truth receipt

Decision: `REVEAL_FROZEN_WORKER_RUNTIME_CPU_TRUTH`

The blind fixture set was committed first in `154693c`. This reveal changes no
CUDA, model, host, build, artifact, fixture, or search-range input.

- qualified local CPU binary SHA-256:
  `2ad04b1a337af838b3b6836ff2bae7eeb78fae463234613268ed511dcce17dc1`
- candidate ops SHA-256:
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- observed state digest: `bc16e98fdac46783`
- fault truth SHA-256:
  `13d55255d89015530936020386bf973c06d72feb4602f4154f400f7786333bae`
- probe truth SHA-256:
  `ccc51ee87f5e7ffb2c237c0035c8271cd60dc5594fc3ca7fd5c909338d7aaaaa`
- complete truth volume: 8 nonces, 132 fault index/mask rows, 3 squeezed-byte
  rows, and 18 Jacobian-field rows

This is CPU truth for the frozen host-runtime qualification only. It does not
admit the worker, search, a candidate, trusted evaluation, or submission.
`submit=CLOSED`, `no_submit_ack=yes`.
