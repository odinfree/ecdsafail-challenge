# Q1266 bounded GPU search progress

This ledger records source-bound completed slices and exact CPU postfilter
outcomes. It is not a candidate or score receipt.

## Worker 0 slice 1

- range: `[82503798882304,82503807270912)`
- count / wall time / throughput: `8388608` / `400 s` / `21079.8 nonce/s`
- source / ops / runtime SHA-256:
  `dfa7cc860e24a4785ae3ec4da5451e7afaa9685f6ae2d9fe77f23cb185f0fa6a` /
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c` /
  `4ff81a62f3be5333104df9bfd937a967d405656340d0e4656fb5d4d647c53956`
- state digest / comb mode: `bc16e98fdac46783` / `comb_bits=8`
- GPU survivors: `1`
- survivor: `82503803836732 pred_cls=0`
- slice evidence archive SHA-256 / bytes:
  `cf2580c1770ac59f6ef6095e0e5173df1167b0d59308f4c22c9c060d033fee8a` /
  `824`
- slice evidence archive:
  `/tmp/q1266-w0-slice-82503798882304-82503807270912.tar.gz`

Exact CPU postfilter binding:

- binary SHA-256:
  `e47d8651e026c4292a1ad9e02b1b4756699400c1d11c5570aead0d51e8752136`
- classical indices: empty
- raw phase indices: `5090,7598,8103`
- dirty batches: `0`
- result: `clean=false`, expected exit `3`

The survivor is rejected before trusted evaluation. It releases the ball and
the ordered lease may continue. No trusted evaluator, promotion, queue, or
submission action occurred. `submit=CLOSED`, `no_submit_ack=yes`.

## Worker 0 slice 2

- range / count: `[82503807270912,82503815659520)` / `8388608`
- wall / kernel / throughput: `401 s` / `398325.7 ms` / `21059.7 nonce/s`
- state digest / comb mode: `bc16e98fdac46783` / `comb_bits=8`
- survivors: `0`
- evidence archive SHA-256 / bytes:
  `28faedefd249506969c14e9cca95ebcca916bc421f27e45e4cd7e662a167a67a` /
  `804`
- evidence archive:
  `/tmp/q1266-w0-slice-82503807270912-82503815659520.tar.gz`

## Worker 2 bootstrap and slice 1

- distributed runtime: exact SHA-256 `4ff81a62...`, bootstrap PASS
- exhausted canary: 4,096 nonces, zero survivors, exact state telemetry
- range / count: `[82504871575552,82504879964160)` / `8388608`
- wall / kernel / throughput: `394 s` / `389166.6 ms` / `21555.3 nonce/s`
- state digest / comb mode: `bc16e98fdac46783` / `comb_bits=8`
- survivors: `0`
- combined bootstrap, hard-nack, and slice evidence archive SHA-256 / bytes:
  `0ca1dff266fe9a95fbe368a39f590ccd47d2931f74047a56ac03b2f2c3a91040` /
  `3207`
- evidence archive: `/tmp/q1266-w2-bootstrap-and-slice1.tar.gz`

Cumulative new production coverage through these completed records is
`26210304` nonces, including the production canary. Exactly one GPU survivor
has appeared and it was exact-postfiltered non-clean. Search continues under
the existing lease with no trusted replay. `submit=CLOSED`,
`no_submit_ack=yes`.
