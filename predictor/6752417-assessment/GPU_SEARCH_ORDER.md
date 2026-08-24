# Q1266 odd-passenger bounded GPU search order

Decision: `ADMIT_CANARY_THEN_FOUR_WORKER_GPU_SEARCH`

Issued: `2026-08-24`, Europe/Zurich

This order opens a source-bound classical GPU search only after one production
canary passes. It does not open trusted evaluation, candidate baking, protected
queues, public notes, pushes, or submission.

## Fresh live binding

- official CLI/version: `ecdsafail v2026.08.23-1`
- official benchmark source: `67524171baaf568dc3dc606f38515745f70804ff`
- fresh current best: `1154731130`
- structural candidate source/tree:
  `57ee207abe9f648dbc443bfb329e051707327d46` /
  `b1528c97b2766bd99ea6ee75dcc64d69fbd43360`
- candidate ops SHA-256:
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- candidate resource shape: Q1266 / 12,596,439 operations
- admitted comb8 GPU receipt commit:
  `8da6a28600573512cf300388b14c561e9d13e82b`
- admitted comb8 CUDA source SHA-256:
  `dfa7cc860e24a4785ae3ec4da5451e7afaa9685f6ae2d9fe77f23cb185f0fa6a`
- parity-host raw GPU binary SHA-256 (provenance only):
  `8f6f0a59f451ca2ddcd71f07772fd855f8078664f66ed9181d7513825fe78edd`
- deterministic worker-runtime receipt commit:
  `515d88c044affbe53cd56f95f3e1f0d0590f48f0`
- canonical stripped GPU runtime SHA-256 / bytes:
  `4ff81a62f3be5333104df9bfd937a967d405656340d0e4656fb5d4d647c53956` /
  `2808400`
- exact CPU postfilter receipt commit:
  `115876715b1502fff105e2b662cb63c116c17ca6`
- exact CPU postfilter binary SHA-256:
  `e47d8651e026c4292a1ad9e02b1b4756699400c1d11c5570aead0d51e8752136`
- ball owner: `codex_q1266_odd_passenger_gpu_search_owner`

The official CLI refresh preserved the source and score from the frozen
handoff. Named fleet status reported zero active ledger rows, and exact-number
search found no prior reference to the new partition boundaries below.

## Source-bound lease and partitions

The lease extends the previously declared hash-derived local base without
changing its derivation:

- full lease: `[82503797833728, 82505945317376)`
- total size: `2147483648` (`2^31`) nonces
- already searched: `[82503797833728, 82503797837824)` (4096 nonces)
- production canary: `[82503797837824, 82503798882304)` (1,044,480 nonces)
- worker 0: `[82503797833728, 82504334704640)`
- worker 1: `[82504334704640, 82504871575552)`
- worker 2: `[82504871575552, 82505408446464)`
- worker 3: `[82505408446464, 82505945317376)`

Worker 0 skips the already searched 4096-prefix and owns the production canary.
Workers 1-3 do not launch until worker 0 passes remote source/runtime checks, an
exact replay of the old 4096 canary, and the production canary with no CUDA or
artifact error. All subsequent search is in slices of at most 8,388,608
(`2^23`) nonces. No slice crosses a worker boundary.

## Per-worker gates and evidence

Each uniquely labeled experiment-owned RTX 4090 worker must independently:

1. match all candidate/source hashes and receive the exact frozen runtime from
   the controller artifact bound in `GPU_RUNTIME_DISTRIBUTION_CONTRACT.md`;
2. reproduce canonical runtime SHA-256 `4ff81a62...` and exact size `2808400`
   before execution; host-local production recompilation is forbidden and only
   those transferred canonical bytes may execute a search range;
3. reject `--comb-bits`, report 12,596,439 operations and state digest
   `bc16e98fdac46783`;
4. replay `[82503797833728,82503797837824)` with zero survivors and exact
   telemetry before its first assigned production slice;
5. preserve one durable record per slice: worker, exact half-open range, source,
   ops/binary hashes, exit, telemetry, complete survivor stdout, stderr hash,
   elapsed time, and cumulative coverage.

Any source, hash, binary, state, overlap, overflow, CUDA, or logging error stops
that worker. Other workers continue only if their own bindings remain exact.
Source supersession stops all workers at their next slice boundary.

The original raw-binary reproduction clause was falsified before search: nvcc
places a process-ID-derived temporary name in `.strtab`, so two rebuilds had
different raw hashes. A later cross-host rebuild also failed the stripped hash
gate before any nonce ran. Contract `154693c`, reveal `4789f90`, qualifier
`5073537`, receipt `515d88c`, and the frozen distribution contract replace only
that ill-posed recompile subgate with exact admitted-byte distribution. Fresh
worker-0 semantic parity passed 24 fault diffs, 12 intermediate probe diffs,
four batch widths, and one exhausted-canary replay. All source, state, range,
exact-postfilter, and authority gates are unchanged.

## Survivor and trusted-replay discipline

Every `pred_cls=0` row is transferred after its slice and processed in ascending
nonce order by the admitted exact CPU postfilter against the frozen base
artifact. A postfilter result is admissible only with empty classical and raw
phase sets, zero dirty batches, and `clean=true`.

- non-clean survivors are recorded and search continues;
- the first exact-clean survivor owns the ball and stops new slices;
- in-flight slices may finish only at their already launched boundaries;
- no clean survivor is compared or selected by T count;
- exactly one trusted 9024-shot evaluator replay is allowed for the first
  exact-clean survivor.

Trusted promotion requires classical/phase/ancilla `0/0/0`, Q1266, exact
source/artifact/nonce identity, and rounded T at most `912109`, which strictly
beats the fresh live score. A clean but non-winning trusted result closes this
lease without nonce shopping by measured T.

## Provider and spend envelope

- provider set: Vast and/or RunPod only
- at most 4 simultaneous experiment-owned search workers
- per-worker offer ceiling: USD 1.00/hour
- per-worker wall ceiling: 12 hours
- total search-envelope ceiling: USD 50
- combined Vast plus RunPod hard ceiling: USD 500 per Europe/Zurich calendar day
- stop/destroy on first exact-clean survivor, lease exhaustion, source drift,
  operational falsifier, 12-hour worker ceiling, USD 50 search ceiling, or user
  stop
- unrelated and unregistered provider instances remain untouched

Full lease exhaustion without an exact-clean survivor is
`COMPLETE_SEARCH_NO_CLEAN`, not a structural hard nack. Any extension requires a
new disjoint order. `submit=CLOSED`, `no_submit_ack=yes`.
