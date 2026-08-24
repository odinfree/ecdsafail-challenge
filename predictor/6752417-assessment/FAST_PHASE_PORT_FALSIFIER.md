# Fast phase donor port falsifier

Decision: `HARD_NACK_FAST_PHASE_PORT`

The experimental port from
`origin/research/fable-q1274-fast-phase-screen` is not a valid phase predictor
for the Q1266 odd-passenger candidate.

## Frozen evidence

- experiment commit: `302c58e48bf4e4f99c8d6becb4d6c2891269fb9d`
- immediate revert commit: `959ef20`
- tracked candidate op-site trace SHA-256: `c5f2f732577914bee1ad52a446af5edd0c14fd3962c7c29fdf1273d888e9ae9c`
- traced operations: `12596343`
- traced R/Hmr sites: `1919152`
- expected schedule sites: `4405`

On shot 0, the model reached the same aggregate schedule length of 4405 sites,
but the ordered family comparison failed at site 2366: the source trace emitted
family 0 while the donor-derived schedule expected family 2. The candidate has
four chunk events before the first multiply flag; the donor-derived schedule
emitted a fifth. Matching totals therefore concealed source-architecture drift.

This is the predeclared falsifier. No tuning against revealed phase outcomes is
allowed. The port was frozen for audit and reverted immediately so that the
qualified classical predictor returned to its exact source and binary hashes.
Any future fast phase work must begin from a new source-literal model of the
current candidate and a fresh blind qualification contract.
