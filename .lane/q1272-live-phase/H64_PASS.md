# Q1272 H64 combined-mask qualification

Verdict: `PASS_H64_64_OF_64 / MODEL SEALED / D32 UNOPENED`.

The source-bound CPU model reproduces every complete trusted classical and
conditional-phase mask on the frozen H64 corpus.  There were no mismatches,
aborts, geometry failures, or nonzero ancillas.  This is a calibration gate,
not authorization for CUDA, a provider, a range, a hunt, or submission.

## Frozen identities

- model checkpoint / H64 runner commits: `a379cd3` / `61461af`;
- target source / operations:
  `73422709ed70ba9725b3cb592770bcf197df4cdb` /
  `12,904,643` /
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- C++ model / host / CPU source SHA-256:
  `0d4c9a812892b9dac598cb59a8345c443b9e21663ac29743578f4e651b39b92a` /
  `aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2` /
  `dd05545d33911e7e0ab44b0e373f03a759ae8ee4b990f20f2cc40ca6ee2063af`;
- local CPU binary SHA-256:
  `47366b9d7d131639bb0ed9a8abc9cb87bd9c3b9aa5b746d0dcbc464ac9ba435c`;
- H64 runner SHA-256:
  `a67d36f3e03df621626677587e09178e88ea1d603aedd55fb0d88efb76b86980`;
- regenerated phase schedule / R/Hmr words: `3,964` / `1,938,616`,
  ledger SHA-256
  `59c177b5b43bf27eba1ee6758a7c1cea07f0eef5aa9b0c2a27dfe05301c6657d`;
- frozen H64 nonce list: `444000000000..444000000063`, exact LF-list
  SHA-256
  `17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9`.

The independent primary classical lane is sealed at commit
`d190180a3df6e5d6b9d0b56c9f11014e863dedd1`, tree
`833116cc67dba96a83b7fd648b79b490ab614108`.  Its classical H64 gate is also
exact `64/64` with the same `1,144` faults.  This lane's independently composed
phase model agrees with both that model and the trusted oracle on every H64
classical set.

## Exact result

Across 64 unchanged 9,024-shot oracle draws:

- complete classical masks: `64/64`, `1,144/1,144` faults;
- complete conditional clean-phase masks: `64/64`, `293/293` faults;
- raw phase faults: `844` (retained only as trusted context, not claimed by
  the screen on classically dirty shots);
- Q / shots / ancilla on every row: `1272 / 9024 / 0`;
- classical / conditional-phase / joint zero rows: `0 / 1 / 0`;
- compact transitive RESULTS manifest SHA-256:
  `0b05b359ac2f9fc23e81163adcf8047aa28fd514c5ecd581a0416a07ee1b9ccc`;
- external artifact root:
  `/Users/olifreuler/ecdsa-ops/q1272-live-phase-ea19759d/h64/`.

`RESULTS.tsv` binds each row's per-file SHA manifest; all raw oracle masks,
model masks, logs, attribution rows, binaries, operation streams, and generated
tables remain outside Git.

## Fixed-corpus density characterization

Per 9,024-shot draw, the observed means are:

- classical lambda: `1,144 / 64 = 17.875`;
- conditional clean-phase lambda: `293 / 64 = 4.578125`;
- joint disjoint-fault lambda: `1,437 / 64 = 22.453125`.

No H64 nonce is classical-zero, so a direct empirical estimate of
phase-zero conditional on a classical-zero nonce is unavailable.  At the shot
level, `293` phase faults occurred among `576,392` classically clean shots,
which scales to conditional phase lambda `4.587211481075` per 9,024 clean
shots.

Under the explicitly approximate Poisson planning model, the mean joint
lambda gives zero density `1.773093799e-10`: about one zero per `5.640e9`
nonces and `1.690e10` nonces for 95% probability of at least one.  Phase adds
an estimated `97.33x` burden over the classical-only mean.  A conservative
one-sided 95% Chernoff upper mean of `23.934319759` lowers the zero-density
bound to `4.031410297e-11` and raises the 95% planning size to
`74,309,783,751` nonces.  These are sizing diagnostics, not a scan request or
a guarantee of independence.

## Next gate

The model family, schedule, and H64 result are now sealed.  The next allowed
action is to reveal the already committed D32 nonce list with SHA-256
`62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90`,
run the same trusted oracle and unchanged model once, and fail closed on any
complete-mask difference.  No source edit is permitted after reveal.
