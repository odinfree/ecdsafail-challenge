# Q1273 CPU predictor port: bound before calibration

Verdict: `SOURCE_BOUND / UNCALIBRATED`. No predictor outcome has been exposed.

The port copies the sealed Q1274 repair-r100 model payload from
`research/fable-q1274-repair-qualify@a7326a9541623cdca7912bcefe88ca9a4242dd78`.
The donor files were byte-checked against the predeclaration before edits.
The shared arithmetic remains unchanged. Target edits are limited to:

- source/evidence identity, exact operation count/SHA, and checkpoint digest;
- geometry declarations Q1273 / replay peak 1273 / square ladder 243;
- target comments;
- disabling and removing CPU range-scan mode;
- a bounded `statedigest` receipt command;
- replacing deprecated `sprintf` with bounded `snprintf`.

## Exact target binding

- source commit: `093d85d64de87aa5006a94868172f642daacf136`;
- predeclaration commit: `a8f7307f0a93ec78910444b2e4c18a78f70b9ae9`;
- operation count: `12,933,805`;
- operation SHA-256:
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- checkpoint/tail state digest: `2148e09f4c4293b2`;
- divide/multiply rounds: `698/696`;
- replay peak / square ladder: `1273/243`.

The state digest was derived fail-closed from the exact operation artifact.
The first port build intentionally expected zero and exited 2 before corpus
derivation or model execution, printing `2148e09f4c4293b2`. External prebind
receipt:

- prebind binary SHA-256:
  `f3dfb3dce3aa9f5bed01bf34a8f4db3e8622cab9b62c005d4708408e3099636a`;
- stderr SHA-256:
  `08e8757f188d9c73cf8a0410c0df25d0dc9db3ee5057782379ac82bdc7ee670e`;
- stdout SHA-256 (empty):
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Frozen source hashes

- `pp_host.h`:
  `7a7e477082c240278c36eabfca227b8266d638ae5ab30e5ac6ea2a7dd34f42bb`;
- `pp_model.h`:
  `8e97b9b94d313e05bbe7fb844a53381b17c9c3fbd027a744feb41edaa993976d`;
- `ppcpu.cpp`:
  `0fde4f34365e352b272e138d450d9321fff9a1366d38fbd7213dda35b58fa4a8`.

Next gate: commit and push this source before compiling the final binary or
running any inherited/H64 prediction. Then close loader negatives and the
inherited exact-set canary. H64 remains unopened.
