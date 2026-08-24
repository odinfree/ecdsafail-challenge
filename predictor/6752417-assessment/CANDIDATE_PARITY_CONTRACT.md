# 6752417 odd-passenger predictor parity contract

This is a source-literal port for the Q1266 odd-passenger candidate, not a
relabel of the older `da61` predictor.

## Frozen bindings

- official parent source commit: `67524171baaf568dc3dc606f38515745f70804ff`
- candidate source commit: `57ee207abe9f648dbc443bfb329e051707327d46`
- candidate source tree: `b1528c97b2766bd99ea6ee75dcc64d69fbd43360`
- candidate ops SHA-256: `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- candidate op count: `12596439`
- candidate prefix state digest: `bc16e98fdac46783`
- model SHA-256 before blind truth: `4423f04bb6810993bbe500b3adc147d0a088abb0cb78fc7bf93b973ddef49dc5`
- host SHA-256 before blind truth: `bccaf9d1be17f131be65d637957cd04f409c3c13a8d5a6904070dab58a2b3c57`

## Source-literal corrections

- executed divide rounds: 696
- executed multiply rounds: 694
- default-active 100-index width-repair set applied after schedule lookup
- canonical divide replay frame: no stale signed-frame transform
- divide replay fold: 54 bits
- multiply replay fold: 53 bits

The inherited baked nonce is calibration only. It must predict exactly the 15
classical mismatch indices emitted by the independent source simulator. The six
blind nonces in `candidate-parity-fixtures.tsv` were derived by SHA-256 from
`6752417-odd-passenger-predictor-blind-v1/<index>` and committed with truth
sealed. No model changes are allowed between this freeze and truth generation.

Qualification requires exact mismatch-index parity on all six blind fixtures;
aggregate counts are insufficient. Failure closes search and provider gates
until a new source-derived model revision and a new blind set are frozen.
