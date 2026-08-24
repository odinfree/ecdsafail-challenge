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
