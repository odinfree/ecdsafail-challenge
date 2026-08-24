# Q1266 production-worker deterministic runtime receipt

Decision: `ADMIT_CANONICAL_WORKER_RUNTIME`

The raw-binary reproduction clause in the original search order is
`HARD_NACK_RAW_BINARY_REPRODUCIBILITY`. No production nonce ran before that
falsifier. The failure is confined to non-runtime nvcc process-ID text in the
ELF symbol string table; it is not treated as a semantic pass by explanation
alone. A newly frozen canonical artifact and fresh post-freeze parity matrix
passed in full.

## Binding and evidence

- deterministic runtime contract commit:
  `154693c214c8dc13091332a0d303e7830a16f857`
- post-freeze CPU truth reveal commit:
  `4789f90e82bb9381af3e3272362cda3bc5f6d296`
- frozen qualifier commit:
  `50735372a3254e34338b90ae7ea757259dfbf96a`
- qualifier SHA-256:
  `42f68a1fcdabc26c7a159464b947f053ad33e5279704fc8ac9b8b3413c661ec5`
- candidate ops SHA-256:
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- CUDA source SHA-256:
  `dfa7cc860e24a4785ae3ec4da5451e7afaa9685f6ae2d9fe77f23cb185f0fa6a`
- after-freeze raw GPU binary SHA-256:
  `dfc80c9983dc3783a3167cdf0965b6dc9f5e00fdf3c84a633606cef3d9aff1e2`
- after-freeze raw bytes / GNU build ID:
  `3105736` / `bbeef3ef39b7ea9df8710a220b8e29f33ad83c5e`
- canonical stripped runtime SHA-256 / bytes:
  `4ff81a62f3be5333104df9bfd937a967d405656340d0e4656fb5d4d647c53956` /
  `2808400`
- evidence archive SHA-256 / bytes:
  `462ccb1d4c069945e06ea8d0937dbeb6195d42505fa1d0c2c18c283b35289aff` /
  `11202`
- evidence archive: `/tmp/q1266-worker-runtime-qual-pass-logs.tar.gz`
- device/toolchain: RTX 4090, driver 595.71.05, CUDA compiler 13.0
- after-freeze build wall time: `48 s`

## Exact results

- all source, header, model, build, fixture, truth, and ops hashes matched
- raw rebuild retained the expected size and build ID; its raw hash was
  recorded but was not used as a runtime identity
- the frozen strip transform produced the exact canonical SHA and size
- forbidden `--comb-bits` CLI rejected exactly
- state digest remained `bc16e98fdac46783`
- batch inversion: 4/4 widths passed
- fresh fault matrix: 24/24 complete diffs empty across eight blind nonces and
  32/128/256 threads; all 132 index/mask rows matched
- fresh probes: 12/12 complete squeezed-byte/Jacobian diffs empty across three
  blinds and 32/256 threads
- exhausted-canary replay: 4,096 nonces, zero survivors, exact telemetry,
  `15699.9 nonce/s`

This receipt admits only the exact canonical runtime on the qualified current
worker. A separate committed amendment must reopen the production canary and
define the same canonical-hash gate for any additional worker. Exact CPU
postfiltering remains mandatory. Trusted evaluation, promotion, push, public
note, protected queue action, and submission remain closed.
`submit=CLOSED`, `no_submit_ack=yes`.
