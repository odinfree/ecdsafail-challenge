# Q1266 worker-0 production canary receipt

Decision: `ADMIT_BOUNDED_FOUR_WORKER_SCALE_OUT`

Worker 0 passed the exact production canary declared in
`GPU_SEARCH_ORDER.md`. This receipt opens only the remaining bounded partitions
under that order. It does not open trusted evaluation, promotion, push, public
note, protected queue action, or submission.

## Binding

- amended search-order commit:
  `931af1e9fba63e4d0a8a9a5f970e2c9276905a41`
- deterministic runtime receipt commit:
  `515d88c044affbe53cd56f95f3e1f0d0590f48f0`
- canonical GPU runtime SHA-256:
  `4ff81a62f3be5333104df9bfd937a967d405656340d0e4656fb5d4d647c53956`
- CUDA source SHA-256:
  `dfa7cc860e24a4785ae3ec4da5451e7afaa9685f6ae2d9fe77f23cb185f0fa6a`
- candidate ops SHA-256:
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- exact half-open canary range:
  `[82503797837824,82503798882304)`
- evidence archive SHA-256 / bytes:
  `784edc51af239a4b1c88f572556abfea4f1ceebf8451581d6fd41f84abe14bcf` /
  `636`
- evidence archive: `/tmp/q1266-w0-production-canary-pass.tar.gz`

## Exact result

- exit: `0`
- count: `1044480`
- wall / kernel time: `53 s` / `50362.0 ms`
- throughput: `20739.4 nonce/s`
- complete survivor stdout SHA-256:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- survivors: `0`
- operation count / state digest: `12596439` / `bc16e98fdac46783`
- fixed-base mode: `comb_bits=8`
- no overflow, CUDA, source, artifact, logging, or range error

Workers 1-3 may now launch only after their independent source, canonical
runtime, state, and exhausted-canary gates pass. Worker 0 may continue after
the production canary boundary in slices no larger than `2^23`. Every survivor
still requires the admitted exact CPU postfilter, and the first exact-clean
survivor stops new slices. `submit=CLOSED`, `no_submit_ack=yes`.
