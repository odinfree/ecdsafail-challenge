# Q1266 odd-passenger local nonce canary order

Decision: `ADMIT_BOUNDED_LOCAL_CPU_CANARY`

Issued: `2026-08-24T12:12:50Z`

This order opens only the declared local CPU canary below. Provider rental,
provider spend, remote workers, fleet retargeting, protected queues, public
notes, pushes, candidate baking, and submission remain closed.

## Binding and gates

- exact challenge source: `67524171baaf568dc3dc606f38515745f70804ff`
- structural candidate source: `57ee207abe9f648dbc443bfb329e051707327d46`
- structural candidate tree: `b1528c97b2766bd99ea6ee75dcc64d69fbd43360`
- candidate ops SHA-256: `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- candidate resource shape: Q1266, 12,596,439 operations
- classical parity receipt commit: `5a2314b`
- exact postfilter receipt commit: `115876715b1502fff105e2b662cb63c116c17ca6`
- campaign authorization: the user explicitly ordered autonomous structural-cut
  leadership and a live winning result; this order narrows that authorization
  to a no-spend local canary
- ball owner: `codex_q1266_odd_passenger_nonce_owner`

At issuance, the named fleet wrappers reported compute `OPEN`, route `OPEN`,
submission `CLOSED`, zero active ledger rows, and GPU/Rust readiness blocked on
an unset current-source route binding. That state admits no remote action. It
does establish that the following source-bound local lease does not overlap an
active worker range.

## Source-bound lease

The lease is derived before search from the first 48 bits of the SHA-256 of:

`ecdsa.fail/6752417/q1266-odd-passenger/local-lease-v1/2026-08-24/codex-structural-owner`

Derivation SHA-256:
`4b09699c98e7a0f2dcfc9599784280f6972cd84d1bbc84d586b5c8d4c7b6ee5d`

- reserved source-bound lease: `[82503797833728, 82503798882304)`
- executable canary: `[82503797833728, 82503797837824)` (4096 nonces)
- scanner concurrency ceiling: 16 local CPU threads
- no second range and no expansion beyond the executable canary in this order

An exact-number search across the project and fleet workspaces found no prior
reference to any boundary of this lease before issuance. Nonce identity is
meaningful only with the bound operation stream; source or stream drift ends
the lease as `SUPERSEDED`.

## Tool chain and stop conditions

- classical scanner SHA-256: `2ad04b1a337af838b3b6836ff2bae7eeb78fae463234613268ed511dcce17dc1`
- classical model SHA-256: `4423f04bb6810993bbe500b3adc147d0a088abb0cb78fc7bf93b973ddef49dc5`
- scanner host SHA-256: `bccaf9d1be17f131be65d637957cd04f409c3c13a8d5a6904070dab58a2b3c57`
- exact postfilter binary SHA-256: `e47d8651e026c4292a1ad9e02b1b4756699400c1d11c5570aead0d51e8752136`

Run the canary once. Preserve its exact start/count/thread tuple, exit status,
elapsed time, and every `pred_cls=0` row. Apply the exact CPU postfilter once to
every classical survivor in ascending nonce order. Stop on source drift,
artifact mismatch, any tool error, any dirty batch, canary exhaustion, or the
first exact `clean=true` survivor. Do not choose among clean nonces by measured
T count: the first exact-clean nonce owns the one trusted evaluator replay.

A full evaluator replay, if reached, remains a separate gate. It must report
all 9024 shots, classical/phase/ancilla `0/0/0`, Q1266, the exact artifact and
nonce binding, and a rounded T count at most 912109 before any promotion can be
considered. Submission remains closed regardless of local outcome.
