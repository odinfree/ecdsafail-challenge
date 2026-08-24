# Q1266 odd-passenger isolated GPU parity contract

Status: `FROZEN_PRE_REVEAL`

This contract admits at most one isolated, experiment-owned Vast or RunPod GPU
canary. It does not admit a new nonce range, provider scale-out, a candidate,
trusted evaluation, push, public note, queue action, or submission.

## Frozen source binding

- exact challenge source: `67524171baaf568dc3dc606f38515745f70804ff`
- structural candidate source/tree:
  `57ee207abe9f648dbc443bfb329e051707327d46` /
  `b1528c97b2766bd99ea6ee75dcc64d69fbd43360`
- candidate ops SHA-256:
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- candidate operation count / Q: `12596439` / `1266`
- CUDA source SHA-256:
  `687d1df6cd5b853d55e38b3ae066045bdffe3d01e3508b10ffe6704145f9caaf`
- shared model SHA-256:
  `4423f04bb6810993bbe500b3adc147d0a088abb0cb78fc7bf93b973ddef49dc5`
- shared host SHA-256:
  `bccaf9d1be17f131be65d637957cd04f409c3c13a8d5a6904070dab58a2b3c57`
- build script SHA-256:
  `7598ef077ab15573f2f1ed0d216a84ed0788f3c59a33ae7ae00a30051a867094`
- qualified CPU binary SHA-256:
  `2ad04b1a337af838b3b6836ff2bae7eeb78fae463234613268ed511dcce17dc1`
- exact CPU postfilter binary SHA-256:
  `e47d8651e026c4292a1ad9e02b1b4756699400c1d11c5570aead0d51e8752136`

The stale Q1272/696-round prose in the inherited CUDA header was corrected
before this freeze. Executable constants were already supplied by the shared
qualified model: divide 696, multiply 694, exact width repair, candidate op
count, and prefix-state digest `bc16e98fdac46783`.

## Sealed fixtures and falsifiers

The six blind nonces in `gpu-parity-fixtures.tsv` were derived from
`6752417-q1266-odd-passenger-gpu-parity-blind-v1/<index>` and committed with
CPU truth sealed. No CUDA, model, host, or fixture-source change is allowed
after reveal.

Qualification requires all of the following:

1. The remote candidate artifact and all four GPU source/build files match the
   hashes above before compilation. The GPU loader must report exactly
   `12596439` operations and state digest `bc16e98fdac46783`.
2. Record GPU model, CUDA compiler/runtime versions, compile command, compile
   exit, and the resulting GPU binary SHA-256 without exposing provider host,
   account, credential, or payment details.
3. `--probe-batchinv` passes at 128 and 256 threads for both comb8 and comb16.
   `--probe-bytes` and `--probe-jac` exactly match CPU output on calibration and
   blind-0 for both comb widths.
4. Complete `faultshots` output, including every fault mask, exactly equals the
   frozen CPU output for calibration plus all six blind fixtures under all four
   production configurations: comb8/comb16 crossed with 128/256 threads.
   Counts alone are insufficient.
5. Replaying the already exhausted local canary
   `[82503797833728,82503797837824)` produces the same empty survivor stream as
   CPU under comb8 and comb16, reports the exact state digest, and completes
   without overflow or CUDA error.

Any mismatch is `HARD_NACK_GPU_PORT`; tuning against a revealed disagreement is
forbidden. A pass is only `ADMIT_GPU_CLASSICAL_PREFILTER` and still requires a
new bounded search order.

## Provider and spend envelope

- exactly one experiment-owned, uniquely labeled canary instance
- preferred device: one RTX 4090 or another device that can compile/run the
  source without semantic changes
- offer ceiling: `USD 1.00/hour`
- wall-clock lease ceiling: `2 hours`
- maximum canary exposure: `USD 2.00`
- combined Vast plus RunPod ceiling: `USD 500` per Europe/Zurich calendar day
- canary termination: immediately after PASS, falsifier, or operational block
- unrelated or unregistered provider instances are out of scope and untouched
- `submit=CLOSED`, `no_submit_ack=yes`

The canary may receive only the bound source files, candidate artifact, fixture
list, and non-secret runner commands. Provider credentials remain in their
configured clients and must never be placed in commands, logs, Git, or packets.
