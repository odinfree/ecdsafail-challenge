# Q1270 inherited trusted-mask receipt

Decision: `PASS / H64 AUTHORIZED / MODEL UNOPENED`.

The pushed freeze gate at `426af750d14212cc0ee08ff6560917282cee3ece`
ran only the inherited nonce `65700024945645`. The current-source oracle
executes two independent complete simulations internally; the calibration
runner then invoked it a second time. The complete first and repeated stdout
files are byte-identical at SHA-256
`53c9d456626644c105a7d9419199683b535137e42e21ac6e4689754b6dee9b94`.
Both stderr files are empty and hash to the standard empty-file digest.

## Exact trusted result

- geometry: Q1270 / 961,070 bits / 12,953,636 operations / 9,024 shots;
- exact total Toffoli: `8,269,295,555`, average
  `916366.971963652526`, displayed `916366.972`;
- exact total Clifford: `96,841,086,218`, average
  `10731503.348625887185`, displayed `10731503.349`;
- classical failures: `23`, first shot `373`;
- raw conditional-phase failures: `15` shots in `14` batches;
- clean conditional-phase failures after excluding classical failures: `4`;
- ancilla failures: `0` shots / `0` batches.

The classical mask is set at shots:

```text
373,776,1032,1491,1905,1934,2829,2977,4082,4766,4876,5074,5302,5366,
5834,6170,6475,7619,7963,8572,8586,8915,8958
```

The raw phase mask is set at shots:

```text
373,776,1032,1905,1934,3373,4450,4766,4876,5302,5834,7200,8656,8915,8958
```

The clean phase mask is therefore exactly `3373,4450,7200,8656`.

## Complete-mask and corpus identities

The canonical `row.bin` is 4,892 bytes and hashes to
`a2515e8989d873b721c59e9c58354f6b61d9754d0fb3291dd046ff9b6cc8f004`.
It contains the frozen source, full receipt, operation, nonce-transform,
checkpoint, schedule, evaluator, oracle source, and oracle binary identities,
followed by four complete 141-word little-endian masks. The mask slices hash
to:

- classical:
  `38eef3e8ef39a27f6bf870837c362b62c5a82c39baa908b7c0836962fdefe31f`;
- raw phase:
  `dccf69ee17c206a477e85dfbc9b88919ea1cb13868d40999a1f3259388187d98`;
- clean phase:
  `d4faa8308f5820b4af1ad8e237f741ed1f486f71da070dbec57f213b8c9eef98`;
- ancilla:
  `3731b0a75ab19d96b774da62d37eccacd517c6593af20aa66525dc0b951cdba9`.

The complete corpus-level `RESULTS.tsv`, `SHA256SUMS`, and `COMPLETE` hashes
are respectively:

```text
f72dcee3e5be405845d37d9a38acf3ac1432b50721ae7f30460945ca29bc3245
5e8122213783374b260995e65a99b702fe057fdc41e1b3a2cd8853278a936674
fc8fa24fd12e0727173ea5fc0fde0f00247adcd6c9eb56854dc3d7b5e398a835
```

An independent digest check passed for every artifact in the sealed manifest.
Tracked `results.tsv`, `ops.bin`, evaluator, simulator, and circuit hashes remain
exact. No donor source/model/binary/table/output and no D32 value was opened.
The mandatory inherited gate therefore passes and authorizes only the already
frozen H64 oracle run.
