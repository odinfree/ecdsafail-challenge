# Q1266 odd-passenger local nonce canary receipt

Decision: `COMPLETE_LOCAL_CANARY_NO_CLASSICAL_SURVIVOR`

The executable range declared in `LOCAL_CANARY_ORDER.md` was run exactly once.
This is canary exhaustion, not a hard nack of the structural candidate or its
reserved lease.

## Binding

- order commit: `a5ef2302ffe48c995b846bd15dbe83f40a87238d`
- candidate ops SHA-256: `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- scanner SHA-256: `2ad04b1a337af838b3b6836ff2bae7eeb78fae463234613268ed511dcce17dc1`
- range: `[82503797833728, 82503797837824)`
- count: `4096`
- local CPU threads: `16`

## Result

- scanner exit: `0`
- scanner terminal: `ppcpu done: 4096 nonces, survivors 0`
- classical survivors: `0`
- exact postfilter invocations: `0`
- wall time: `32.96 s`
- measured throughput: `124.271845 nonce/s`
- stdout SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- stderr SHA-256: `1abde3710892cb43c47360ff6b2c1e03d89da8cb3376b4a3ac888231464412f0`

The empty stdout is the expected exact record for zero `pred_cls=0` rows. The
stderr binds prefix load to 12,596,439 operations, successful comb build,
complete range exhaustion, and the timing receipt.

## Boundary and next gate

No nonce outside the executable canary was searched. The remainder of the
reserved source-bound lease `[82503797837824, 82503798882304)` is unsearched.
No provider, remote worker, fleet retarget, queue, public note, push, candidate
bake, trusted evaluator, or submission action occurred.

At the measured local rate, source-bound GPU qualification is the next useful
step. It requires a fresh current-candidate route packet, an isolated provider
canary, exact CPU/GPU classical parity on the frozen calibration and blind
fixtures, a bounded slice of the existing reserved lease, durable logs, and a
hard daily combined Vast/RunPod spend ceiling of USD 500. Submission remains
closed.
