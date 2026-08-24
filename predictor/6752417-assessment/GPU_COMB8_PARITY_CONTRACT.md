# Q1266 fresh comb8-only GPU parity contract

Status: `FROZEN_PRE_REVEAL`

This is a new GPU artifact, not a flag-level salvage of the hard-nacked binary.
The invalid optional comb16 construction, device state, CLI selector, upload,
and telemetry parameter were removed from source before this freeze. The sole
fixed-base path is the original source-literal comb8 implementation.

This contract admits at most one isolated provider parity canary. It does not
admit a nonce range, scale-out, candidate, trusted evaluator, push, public note,
queue action, or submission.

## Frozen binding

- exact challenge source: `67524171baaf568dc3dc606f38515745f70804ff`
- structural candidate source/tree:
  `57ee207abe9f648dbc443bfb329e051707327d46` /
  `b1528c97b2766bd99ea6ee75dcc64d69fbd43360`
- candidate ops SHA-256:
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- candidate operation count / Q: `12596439` / `1266`
- fresh comb8-only CUDA source SHA-256:
  `dfa7cc860e24a4785ae3ec4da5451e7afaa9685f6ae2d9fe77f23cb185f0fa6a`
- shared model SHA-256:
  `4423f04bb6810993bbe500b3adc147d0a088abb0cb78fc7bf93b973ddef49dc5`
- shared host SHA-256:
  `bccaf9d1be17f131be65d637957cd04f409c3c13a8d5a6904070dab58a2b3c57`
- build script SHA-256:
  `7598ef077ab15573f2f1ed0d216a84ed0788f3c59a33ae7ae00a30051a867094`
- qualified CPU binary SHA-256:
  `2ad04b1a337af838b3b6836ff2bae7eeb78fae463234613268ed511dcce17dc1`
- expected prefix-state digest: `bc16e98fdac46783`

Source inspection before freeze finds no `d_comb16`, `d_comb_bits`,
`pp_comb_mul16`, `build_comb16`, or `--comb-bits` token. The single surviving
`comb16` text is a historical hard-nack comment and is not executable.

## New sealed fixtures

The eight blind nonces in `gpu-comb8-parity-fixtures.tsv` were derived before
CPU reveal from
`6752417-q1266-odd-passenger-comb8-only-gpu-parity-blind-v2/<index>`.
They are disjoint from every prior CPU and GPU fixture set. No CUDA, model,
host, build, or fixture-source change is allowed after reveal.

## Qualification and falsifiers

1. Transferred artifact and source hashes must match exactly before compile.
   The loader must report `12596439` operations and state digest
   `bc16e98fdac46783`.
2. Record device/toolchain, exact build command and exit, binary hash, and build
   time. The resulting CLI must reject `--comb-bits` with exit 2.
3. Block batch inversion must pass at 32, 64, 128, and 256 threads.
4. Squeezed-byte and all-six-field Jacobian probes on calibration, blind-0,
   and blind-7 must exactly match the post-freeze CPU truth at 32/128/256
   threads. Complete output equality is required.
5. Complete faultshot index/mask output for calibration plus all eight blinds
   must exactly match CPU under 32, 64, 128, and 256 threads: 36 exact diffs.
6. Replaying the already exhausted local canary at 128 and 256 threads must
   reproduce an empty survivor stream, exact state digest, no overflow/error,
   and fixed `comb_bits=8` telemetry.

Any disagreement is `HARD_NACK_COMB8_GPU_ARTIFACT`; no tuning against revealed
truth is allowed. A complete pass is only `ADMIT_GPU_CLASSICAL_PREFILTER` and
still needs a separate bounded search order plus exact CPU postfilter.

## Provider envelope

- exactly one experiment-owned and uniquely labeled RTX 4090 canary
- offer ceiling `USD 1.00/hour`, wall ceiling 2 hours, canary max USD 2.00
- combined Vast plus RunPod ceiling USD 500 per Europe/Zurich calendar day
- terminate immediately after PASS, falsifier, or operational block
- unrelated provider instances remain untouched
- `submit=CLOSED`, `no_submit_ack=yes`
