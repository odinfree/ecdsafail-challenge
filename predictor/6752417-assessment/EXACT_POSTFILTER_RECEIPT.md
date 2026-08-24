# Q1266 exact postfilter qualification receipt

Decision: `ADMIT_EXACT_CPU_POSTFILTER`

This decision admits `q1266_exact_postfilter` only as a local, source-exact CPU
correctness filter for rare classical-prefilter survivors. It does not admit a
nonce, score, provider campaign, queue operation, public note, push, or
submission.

## Frozen bindings

- candidate source commit: `57ee207abe9f648dbc443bfb329e051707327d46`
- candidate ops SHA-256: `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- candidate op count / resource shape: `12596439` / Q1266
- postfilter source SHA-256: `9312ae2710eaf0226e733311ab646d23c9c7e78ec6fa85bc037dafe0392d0bdc`
- postfilter binary SHA-256: `e47d8651e026c4292a1ad9e02b1b4756699400c1d11c5570aead0d51e8752136`
- independent source-simulator binary SHA-256: `ed45acf0fcef8ffc8dca8fa9d259da4ac0704b8b47e899f68a4862eaca4f05dc`

The two paths are independently invoked: the postfilter verifies and patches
the frozen base artifact in memory, while the source simulator consumes an
independently patched artifact. Qualification compares complete shot-index
sets, not aggregate counts.

## Results

All seven fixtures have exact classical-index parity, exact raw-phase-index
parity, and zero dirty batches on both paths.

| fixture | nonce | classical indices | raw phase indices |
| --- | ---: | --- | --- |
| calibration | 8107117281543 | 728, 1210, 1776, 3082, 4047, 5502, 5914, 6800, 6839, 7178, 7448, 7864, 8243, 8425, 8789 | 1210, 1776, 2578, 3082, 5914, 6800, 6839, 7448, 8243, 8425, 8881 |
| blind-0 | 265188095765219 | 14, 74, 288, 494, 623, 1031, 1171, 2543, 2733, 2876, 3660, 4291, 4928, 5434, 5529, 6791, 6902, 7860, 8483, 8854, 8924, 8968, 9002 | 14, 74, 288, 1031, 1171, 2543, 2733, 2754, 2876, 4291, 4928, 5434, 5529, 6791, 6902, 8483, 8924, 8968, 9002 |
| blind-1 | 91908727183590 | 316, 579, 1178, 2592, 4332, 5033, 5198, 6684, 6759, 6987, 7208, 7353, 8276 | 316, 579, 3131, 4332, 5033, 5469, 6759, 7353, 8276 |
| blind-2 | 156173832321757 | 382, 1275, 1378, 1507, 1556, 2287, 2675, 3345, 3593, 5514, 6068, 7074, 7200, 7555, 7839, 8056, 8984 | 581, 2675, 7074, 7200, 7839, 8056 |
| blind-3 | 214883755683454 | 194, 1504, 3237, 3905, 3927, 4234, 4485, 5392, 5650, 5793, 6016, 6393, 6487, 6581, 6914, 7008, 7696, 7940 | 194, 3607, 3905, 4234, 4485, 5793, 6016, 6393, 6581, 6914, 7696, 7940 |
| blind-4 | 42208999819505 | 1733, 1899, 1987, 2400, 2411, 2597, 3123, 3663, 3980, 4412, 4561, 5088, 6423, 6493, 7605, 7842, 8377, 8542, 8931, 9002 | 1513, 1987, 2400, 2532, 3123, 3663, 3980, 5088, 7842, 8149, 8377, 8542, 8964, 8971 |
| blind-5 | 106720517445303 | 385, 457, 869, 1323, 1634, 1716, 1878, 2182, 2521, 2653, 2686, 3954, 4140, 4341, 4775, 5363, 5559, 6115, 6499, 7432, 7851, 9004, 9007 | 869, 1716, 1878, 2521, 2653, 3954, 4341, 4775, 5363, 6115, 7125, 7851, 8677, 9004 |

The non-clean postfilter exit is expected for these deliberately ordinary
fixtures; the qualification criterion is the reported complete-set parity and
zero dirty batches. A search survivor is admissible for trusted replay only if
the postfilter reports empty classical and raw-phase sets, zero dirty batches,
and `clean=true`.

## Boundary

The earlier fast phase model is excluded. Its ordered source-family trace
failed its predeclared falsifier even though its aggregate event count matched.
`FAST_PHASE_PORT_FALSIFIER.md` records that rejection. The admitted search
pipeline is therefore classical prefilter followed by this exact CPU
postfilter; no approximate phase screen is part of the evidence chain.
