# Q1273 fixed-H64 combined-density predeclaration

Status: `PREDECLARED / NO H64 PHASE RESULTS OPENED`.

This is a bounded characterization of the already frozen nonce set
`444000000000..444000000063`, inclusive.  It may not extend, replace, skip, or
adapt a nonce after seeing a result.  It does not authorize a provider, range,
hunt, CUDA execution, or submission.

## Identity

- combined CPU source commit:
  `3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e`;
- combined model / CPU / binary SHA-256:
  `14fc9230b55d2b2a84721e50d860933764a18d1357ad30331e5999280f764261` /
  `1d93d46803670324401443ed9f625ee641c6fa8ef77ba4a920baebff83ea24ce` /
  `2234a6cfc61dfb996fdfe757b506dcc5a4917662477cbcdc7894659ce6c098c7`;
- ops count / SHA-256: `12,933,805` /
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- frozen H64 fixture ledger SHA-256:
  `7918937a30d562a2dd26cf59374cdb702c11ce0f08d42789f9ef42da8264b5f4`;
- terminal combined qualification manifest SHA-256:
  `c1088ca0e3bf0d9215f63b6823bf490d408ba46e2cf3271d35c40b449d5fe847`.

The existing unchanged-evaluator classical masks may be reused only after
their ledger and per-row files pass the committed combined gate.  Conditional
phase on this H64 is a new model prediction, not a trusted-evaluator oracle;
the result must be labeled accordingly.

## Frozen measurements

For each of the 64 nonces record:

- `C_i`: complete classical-fault shot count from qualified `faultshots`;
- `P_i`: complete conditional-phase shot count from qualified
  `phasefaultshots`, already excluding classically dirty shots;
- `J_i = C_i + P_i`;
- exact classical-zero, phase-zero-among-classical-zero, and joint-zero
  indicators;
- stdout/stderr hashes for both selectors.

Require canonical sorted indices, deterministic repeated inherited output,
exact source/ops/state/schedule guards, 64 distinct rows, and no selector or
nonce outside the frozen set.  Any guard failure is terminal `HOLD`.

## Predeclared summaries

Report without tuning:

- aggregate and mean `lambda_C = sum(C_i)/64`;
- aggregate and mean `lambda_P = sum(P_i)/64`;
- aggregate and mean `lambda_J = sum(J_i)/64`;
- empirical counts of classical-zero, phase-zero among classical-zero, and
  joint predicted-zero nonces;
- the row standard deviation of `J_i` and the conservative upper-mean estimate
  `lambda_J_upper = mean(J_i) + 2 * sd(J_i) / sqrt(64)`;
- Poisson planning estimate `p0_lower = exp(-lambda_J_upper)`;
- conservative 95% initial size
  `N95 = ceil(log(20) / p0_lower)`, rounded upward to the next power of two.

The Poisson calculation is a search-sizing heuristic, not a correctness claim
or permission to scan.  If numerical underflow or an implausible model result
occurs, report it and stop instead of substituting a friendlier estimator.
