# Q1266 exact GPU runtime distribution contract

Status: `FROZEN_BEFORE_ADDITIONAL_WORKER_SEARCH`

Two independent hosts running the same CUDA 13.0 compiler, source, build path,
and command produced different stripped GPU artifacts. Worker 2 hard-nacked on
the canonical hash before replaying or searching any nonce. Cross-host CUDA
recompilation is therefore excluded from the production identity chain.

The already qualified worker-0 runtime is now a frozen binary artifact. It is
harvested once, transferred byte-for-byte to additional RTX 4090 workers, and
verified before execution. This is stronger runtime identity than accepting a
host-specific recompile and does not change any model or search predicate.

## Frozen artifact

- runtime qualification receipt commit:
  `515d88c044affbe53cd56f95f3e1f0d0590f48f0`
- production canary receipt commit:
  `540ee1a858396420f47d3bae3e46aeac38fe0112`
- canonical runtime SHA-256:
  `4ff81a62f3be5333104df9bfd937a967d405656340d0e4656fb5d4d647c53956`
- canonical runtime bytes: `2808400`
- controller artifact: `/tmp/q1266-ppgpu-runtime-admitted`
- CUDA source SHA-256:
  `dfa7cc860e24a4785ae3ec4da5451e7afaa9685f6ae2d9fe77f23cb185f0fa6a`
- ops SHA-256:
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- resource/state binding: `12596439` operations / `bc16e98fdac46783`

## Per-worker gate

1. Transfer the frozen runtime, source/model/host files, ops artifact, and
   bounded slice wrapper. Do not compile a production GPU runtime on the host.
2. Require the exact runtime SHA and byte count before every bootstrap and
   slice. Record device and driver without making either the runtime identity.
3. Require forbidden `--comb-bits` rejection, 128-thread block-inversion PASS,
   and exact empty replay of `[82503797833728,82503797837824)` with the frozen
   operation count, state digest, and `comb_bits=8` telemetry.
4. Only then may that worker enter its assigned partition under
   `GPU_SEARCH_ORDER.md`; slices remain at most `2^23` and every survivor still
   enters the admitted exact CPU postfilter.

Any transfer, hash, compatibility, canary, CUDA, state, or telemetry mismatch
is `HARD_NACK_DISTRIBUTED_RUNTIME` for that worker. It authorizes no source
change, model tuning, range extension, trusted evaluation, promotion, push,
public note, queue action, or submission. `submit=CLOSED`,
`no_submit_ack=yes`.
