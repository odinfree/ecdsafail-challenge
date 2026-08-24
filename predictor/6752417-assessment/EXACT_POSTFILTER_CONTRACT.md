# Q1266 exact postfilter qualification contract

`q1266_exact_postfilter` is the source-exact, CPU correctness postfilter for
rare classical-prefilter survivors. It is not a score receipt, trusted
evaluator replacement, nonce scanner, or submission tool.

## Frozen pre-reveal binding

- candidate source commit: `57ee207abe9f648dbc443bfb329e051707327d46`
- candidate ops SHA-256: `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- candidate op count / resource shape: `12596439` / Q1266
- postfilter source SHA-256: `9312ae2710eaf0226e733311ab646d23c9c7e78ec6fa85bc037dafe0392d0bdc`
- local postfilter binary SHA-256: `e47d8651e026c4292a1ad9e02b1b4756699400c1d11c5570aead0d51e8752136`
- independent source-simulator binary SHA-256: `ed45acf0fcef8ffc8dca8fa9d259da4ac0704b8b47e899f68a4862eaca4f05dc`

The postfilter fails closed on the compressed base artifact SHA, op count,
Q1266 resource shape, four-register shell, 48-bit nonce, and exact paired X/X
tail identity. It patches the tail in memory before Fiat-Shamir hashing and
simulation, then reports complete classical and raw-phase shot-index sets plus
dirty-batch count.

The inherited nonce is calibration only. The six blind nonces in
`exact-postfilter-fixtures.tsv` were derived from
`6752417-odd-passenger-exact-postfilter-blind-v1/<index>` and frozen with truth
sealed. No postfilter source change is allowed before reveal.

Qualification requires complete classical-index and raw-phase-index equality
against the separately built source-simulator binary on all six fixtures, plus
zero dirty batches on both paths. Aggregate-count parity is insufficient.
