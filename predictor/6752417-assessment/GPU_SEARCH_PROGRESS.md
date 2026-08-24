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

## Subsequent zero-survivor slices

Every row below has exit 0, exact source/ops/runtime hashes, state digest
`bc16e98fdac46783`, `comb_bits=8`, and a locally harvested archive whose hash
matches the remote hash.

| worker/slice | exact half-open range | survivors | archive SHA-256 | bytes |
| --- | --- | ---: | --- | ---: |
| w0/3 | `[82503815659520,82503824048128)` | 0 | `d6eb75707b46e68269260778e299f480c8bbe5acfd288ff3621dae00eb8480dc` | 804 |
| w0/4 | `[82503824048128,82503832436736)` | 0 | `668b35f2363cc996fa8e39bce346d22b118a8a2f275f24d2c0e9548e6b7fb0fb` | 803 |
| w0/5 | `[82503832436736,82503840825344)` | 0 | `2cb19fa67420a538edbe563cd8f7f23b34a90ff51fea661a3521e0c53592b7a4` | 809 |
| w0/6 | `[82503840825344,82503849213952)` | 0 | `38c21d7ac38e0ff5390b60f3c1224c2010d5ac3c91b3e6c5b0376967386e1a0a` | 809 |
| w1/1 | `[82504334704640,82504343093248)` | 0 | `1a8c9f99feaba5d70609b3ebddd26d7f4623c8314881683464d5bc9638b0b8e2` | 1782 |
| w1/2 | `[82504343093248,82504351481856)` | 0 | `feab91cedbe8cb2dcae5a94f920041e4a295054c3347a5940c75ec32aabdc282` | 810 |
| w2/2 | `[82504879964160,82504888352768)` | 0 | `6ec85f6df6d37ce54eb7f6189e726c37f78d407ff0178a04c684408f40cc89e1` | 811 |
| w2/3 | `[82504888352768,82504896741376)` | 0 | `48cd1ee7c006ff0a27cb5d9b37b86e31c8d4a52b7991da2517c2c4486eea7df4` | 810 |
| w2/4 | `[82504896741376,82504905129984)` | 0 | `af330eb3f998b3fd53b510d2a977f83660c31af34e45aaa76d36477cdb389287` | 811 |
| w2/5 | `[82504905129984,82504913518592)` | 0 | `3b9673d7d1f51c0760600af57d72bb187b162f4b42961c3af1abf5ea69fe970d` | 809 |
| w0/7 | `[82503849213952,82503857602560)` | 0 | `2490d8561f3c29a8b9298acc6d5ac38a0bfc9f9f90675f77a60f9f25a7abf2e4` | 808 |
| w2/6 | `[82504913518592,82504921907200)` | 0 | `6b4846a027161d1d5b7fd0e038906fd9a052d988ef25253a0c7df51c9fe5b70a` | 810 |

Cumulative completed production coverage is now `126873600` nonces: the
1,044,480-nonce production canary plus fifteen full `2^23` slices. Exactly one
GPU survivor has appeared in these rows; exact CPU postfilter rejected it as
phase-dirty.
No trusted evaluator replay has run. `submit=CLOSED`, `no_submit_ack=yes`.

## Worker 1 slice 3 survivor rejection

- range / count: `[82504351481856,82504359870464)` / `8388608`
- wall time / GPU survivors: `398 s` / `1`
- survivor: `82504354325995 pred_cls=0`
- evidence archive SHA-256 / bytes:
  `51813a261a8673aab137600c9155a74e71e71b892553477c115a0ce4d819178d` /
  `824`
- exact CPU postfilter: classical indices empty; raw phase index `3481`;
  dirty batches `0`; `clean=false`, expected exit `3`

The survivor was rejected before trusted evaluation. Across all completed
production coverage, two GPU survivors have appeared and both were exact
phase-dirty rejections. Cumulative coverage including this slice is
`135262208` nonces: the production canary plus sixteen full `2^23` slices.
No trusted evaluator replay has run. `submit=CLOSED`, `no_submit_ack=yes`.

## Further zero-survivor slices

| worker/slice | exact half-open range | survivors | archive SHA-256 | bytes |
| --- | --- | ---: | --- | ---: |
| w0/8 | `[82503857602560,82503865991168)` | 0 | `416b0c517ae841e6063d924a6daea00e978e651aae344921f1849efde6f41d48` | 809 |
| w1/4 | `[82504359870464,82504368259072)` | 0 | `f8361e4d56a67be4e3a2591d13fc7814572049118472685952efc6eb7a7b9bce` | 806 |
| w2/7 | `[82504921907200,82504930295808)` | 0 | `14a1327486ff5e0544c04327d8c92a10af3c5f6a8ed6b3237bc59ba2e52408b9` | 808 |
| w0/9 | `[82503865991168,82503874379776)` | 0 | `b8e60481ed0858b4fff171980fdd8a6372fee71dff6f2525d2533e47065b1690` | 808 |

Cumulative completed production coverage is `168816640` nonces: the
1,044,480-nonce production canary plus twenty full `2^23` slices. Two GPU
survivors have appeared and both were exact phase-dirty rejections. No trusted
evaluator replay has run. `submit=CLOSED`, `no_submit_ack=yes`.
