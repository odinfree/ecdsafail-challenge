# Q1266 comb8-only GPU parity receipt

Decision: `ADMIT_GPU_CLASSICAL_PREFILTER_COMB8`

The fresh comb8-only GPU artifact passed its full predeclared qualification.
This admits only source-bound classical prefiltering. Exact CPU postfiltering,
trusted evaluation, promotion, push, public note, queue action, and submission
remain separate gates.

## Binding and environment

- comb8-only freeze commit: `b0d035ae6223e7eba25789f882d6379319a2935a`
- CPU-truth reveal commit: `61cdd09e160d6b1251a19141d86cc9d59192f358`
- candidate ops SHA-256: `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- CUDA source SHA-256: `dfa7cc860e24a4785ae3ec4da5451e7afaa9685f6ae2d9fe77f23cb185f0fa6a`
- remote CPU binary SHA-256: `175fb72b8e5a9eafbf7393aab319d871b53530a04b3b45b5364604f85c81aba1`
- admitted GPU binary SHA-256: `8f6f0a59f451ca2ddcd71f07772fd855f8078664f66ed9181d7513825fe78edd`
- parity runner SHA-256: `8e9396e6fffbed9358a184e317e77aac02ff2c0776ff153654b53aaf1e0787d0`
- evidence archive SHA-256: `4313098f7b6c1831232e0cdac367c3694bc9814b012cd701a27c3c2a5a07f7fa`
- evidence archive bytes / local path: `11495` /
  `/tmp/q1266-comb8-gpu-parity-pass-logs.tar.gz`
- device/toolchain: one RTX 4090, driver 580.126.09, CUDA compiler 13.0
- build wall time: `109.89 s`
- parity wall time: `447.23 s`

All transferred artifact, source, and truth hashes matched before compile. The
loader reported exactly 12,596,439 operations and prefix-state digest
`bc16e98fdac46783` throughout.

## Exact results

- forbidden architecture: `--comb-bits` rejected with exit 2 and exact unknown
  argument message
- remote CPU selfcheck: 9 fault fixtures / 165 lines and 6 probe groups exact
- batch inversion: 4/4 widths passed at 32, 64, 128, and 256 threads
- fault matrix: 36/36 complete GPU/CPU diff files empty; all 165 exact
  shot-index/mask lines matched at all four widths
- probes: 18/18 complete squeezed-byte/Jacobian diffs empty on calibration,
  blind-0, and blind-7 at 32/128/256 threads
- CPU diff files: 15/15 empty
- exhausted-canary replay at 128 threads: 4096 nonces, zero survivors, exact
  digest, `15741.0 nonce/s`
- exhausted-canary replay at 256 threads: 4096 nonces, zero survivors, exact
  digest, `14568.9 nonce/s`
- best qualified production width: 128 threads

No nonempty diff exists in the harvested archive. Unlike the hard-nacked
comb16 binary, every tested intermediate and final output in this artifact is
source-exact on the frozen truth set.

## Provider closeout and authority boundary

The uniquely labeled experiment-owned parity canary was destroyed after
evidence harvest; a filtered provider query reported zero active instances
under its label. Runtime was under one hour at less than USD 0.300/hour; exact
provider billing was not claimed. Combined maximum exposure of both parity
canaries was below USD 0.5875, far below the USD 500 Europe/Zurich daily cap.
Unrelated provider instances were untouched.

No new nonce range was searched. Only the previously exhausted 4096-nonce local
canary was replayed. GPU search remains closed until a separate source-bound,
disjoint range order is committed. Every GPU classical survivor must be
exact-postfiltered on CPU; only the first exact `clean=true` survivor may enter
one trusted evaluator replay. `submit=CLOSED`, `no_submit_ack=yes`.
