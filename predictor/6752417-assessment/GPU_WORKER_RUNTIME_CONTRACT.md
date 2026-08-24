# Q1266 production-worker deterministic runtime contract

Status: `FROZEN_PRE_SEMANTIC_REVEAL`

The original search order required every worker to reproduce raw GPU binary
SHA-256 `8f6f0a59...`. Worker 0 falsified that requirement before any production
nonce ran. Two byte-identical-source rebuilds at the original parity path had
the same size and GNU build ID but different raw hashes. Their complete binary
diff was two bytes in `.strtab`, inside nvcc's process-ID-derived
`tmpxft_........-6_ppgpu.cudafe1.cpp` symbol. After `strip --strip-all`, the two
runtime artifacts were byte-identical.

This contract replaces only the impossible raw-symbol-table reproducibility
subgate. It does not weaken source, state, semantic parity, range, spend,
postfilter, trusted-evaluation, or submission gates. It authorizes no search
until a separate PASS receipt amends the search order.

## Frozen binding

- exact challenge source: `67524171baaf568dc3dc606f38515745f70804ff`
- structural candidate source/tree:
  `57ee207abe9f648dbc443bfb329e051707327d46` /
  `b1528c97b2766bd99ea6ee75dcc64d69fbd43360`
- candidate ops SHA-256:
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- candidate operation count / Q: `12596439` / `1266`
- comb8-only CUDA source SHA-256:
  `dfa7cc860e24a4785ae3ec4da5451e7afaa9685f6ae2d9fe77f23cb185f0fa6a`
- shared model SHA-256:
  `4423f04bb6810993bbe500b3adc147d0a088abb0cb78fc7bf93b973ddef49dc5`
- shared host SHA-256:
  `bccaf9d1be17f131be65d637957cd04f409c3c13a8d5a6904070dab58a2b3c57`
- build script SHA-256:
  `7598ef077ab15573f2f1ed0d216a84ed0788f3c59a33ae7ae00a30051a867094`
- expected prefix-state digest: `bc16e98fdac46783`
- exact build path: `/root/q1266-comb8-parity`
- canonical runtime transform: GNU `strip --strip-all`
- canonical runtime bytes: `2808400`
- canonical runtime SHA-256:
  `4ff81a62f3be5333104df9bfd937a967d405656340d0e4656fb5d4d647c53956`

The eight blind nonces in `gpu-worker-runtime-fixtures.tsv` were derived before
semantic reveal from
`q1266-worker0-runtime-v1/<index>/1a6b0f5c0371bfb2b3682e9dd298209f8e26c3ff`.
They are disjoint from all earlier parity fixtures and from the production
lease.

## Qualification and falsifiers

1. Recheck every frozen source/artifact hash, toolchain version, device, and
   state digest. The CLI must reject `--comb-bits` with exit 2.
2. Rebuild once after this freeze at the exact build path. Preserve the raw
   hash, size, build ID, and build log. Copy the binary, apply the frozen strip
   transform, and require the exact canonical runtime size and SHA above. The
   stripped artifact is the only executable admitted for search.
3. Block batch inversion must pass at 32, 64, 128, and 256 threads.
4. Complete faultshot index/mask output for all eight new blinds must exactly
   match post-freeze CPU truth at 32, 128, and 256 threads: 24 exact diffs.
5. Squeezed-byte and all-six-field Jacobian probes on blind 0, 3, and 7 must
   exactly match post-freeze CPU truth at 32 and 256 threads: 12 exact diffs.
6. Replay `[82503797833728,82503797837824)` at 128 threads with an empty
   survivor stream, exact state digest, fixed `comb_bits=8`, and no
   overflow/CUDA/artifact error.

Any mismatch is `HARD_NACK_WORKER_RUNTIME`. A complete pass admits this exact
canonical runtime only. Search remains closed until a receipt commits the
evidence and explicitly amends the raw-binary clause in `GPU_SEARCH_ORDER.md`.

## Authority and spend boundary

- current uniquely labeled worker remains the sole runtime-qualification host
- no unsearched nonce may run during qualification
- worker offer and wall ceilings remain those in `GPU_SEARCH_ORDER.md`
- combined Vast plus RunPod ceiling remains USD 500 per Europe/Zurich day
- unrelated provider instances remain untouched
- trusted evaluation, candidate promotion, push, public note, queue action,
  and submission remain closed
- `submit=CLOSED`, `no_submit_ack=yes`
