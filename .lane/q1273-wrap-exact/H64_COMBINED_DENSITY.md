# Q1273 fixed-H64 combined-density receipt

Verdict: `COMPLETE / SCORE-DEAD AFTER LIVE PROMOTION`.

The predeclared fixed set `444000000000..444000000063` completed before the
stop signal reached the process.  It did not touch an additional nonce.  The
result is useful only as a sealed density prior: live SOTA moved to
Q1273/T914243, so this Q1273 stream must not receive scan work.

## Result

- rows: `64/64`;
- trusted classical faults: `870`, mean lambda `13.59375`;
- model-predicted conditional-phase faults: `305`, mean lambda `4.765625`;
- joint faults: `1,175`, mean lambda `18.359375`;
- classical-zero / phase-zero among classical-zero / joint-zero rows:
  `0 / 0 / 0`;
- joint row sample standard deviation: `5.186573592934032`;
- predeclared two-standard-error upper mean: `19.656018398233506`;
- Poisson lower `p0`: `2.907365773424635e-09`;
- predeclared N95 / next power of two: `1,030,394,009 / 1,073,741,824`.

The conditional-phase H64 values are qualified-model predictions, not new
trusted-evaluator phase truth.  No provider, range, hunt, CUDA run, or
submission was used.

## Receipts

- rows SHA-256:
  `3153ffb30dd9f006d1745c03bb794e900d132609b0579eb7a7b8c42dcccfce3f`;
- summary SHA-256:
  `dfe64724e15a76f89571520378323ef7e30e6320d5ed19a8686036c790e43a7a`;
- manifest SHA-256:
  `986d1c97376590450cca3c6856598ef045fff7cff67f563f2aa868ba3ea443f4`;
- artifact root:
  `/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/h64-combined-density/`.
