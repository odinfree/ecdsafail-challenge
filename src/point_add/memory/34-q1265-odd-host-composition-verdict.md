# Q1265 odd-passenger plus source-host composition verdict

Verdict: `HARD_NACK_NO_ACTIVATION`

## Exact result

The isolated prototype enabled both
`SUB4_PP_INTERLEAVED_ODD_LOAN=1` and
`SUB4_BINDING_SOURCE_CARRY_Q1265=1` under the source profiler. It produced:

```text
peak Q:                    1266
peak phase:                pp_div_replay
emitted operations:        12596439
emitted CCX:               955130
classical/phase/dirty-64:  0/0/0
ops.bin SHA-256:           5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c
```

The operation count, CCX count, and compressed hash are byte-identical to the
frozen odd-passenger Q1266 artifact. The Q1265 host therefore fired zero times.
The remaining Q1266 allocation occurs after or outside the source-host
predicate's owned-carry boundary, so this composition cannot remove it.

## Gate decision

The first predeclared gate required Q at most 1265. It failed deterministically,
before economics or evaluator validation. A mechanically isolated 64-shot
evaluator was built and hashed but deliberately not run; no finite replay can
repair a count-only failure.

The independent oddness recurrence tests still passed, while its frozen-source
audit correctly rejected the composition's modified Rust source SHA. That is
expected fail-closed behavior and does not weaken the already frozen Q1266
certificate.

No active Q1266 source, operation stream, prefilter, provider worker, nonce
range, trusted replay, queue, public note, or submission gate changed.
