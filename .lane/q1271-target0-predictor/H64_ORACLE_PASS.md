# Q1271 target0/sign-alias H64 trusted-oracle seal

Verdict: `PASS_EXACT_TRUSTED_ORACLE / MODEL_UNRUN / D32_HOLD`.

The trusted two-pass oracle completed the already-frozen H64 corpus before any
predictor source was imported or executed.  No provider, CUDA, scan, range,
hunt, submission, or public action occurred.

## Frozen identities

- source/evidence commit / tree:
  `a22090374a957d29a3331d6c876ad12ff45fea31` /
  `018eb52de8ab3e6337864338683821c0cbb574a2`;
- operations: `12,919,161`, SHA-256
  `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa`;
- trusted oracle source / binary SHA-256:
  `26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98` /
  `90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`;
- H64 ordered nonce-list SHA-256:
  `17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9`;
- corpus: exactly the 64 ordered canonical decimals
  `444000000000..444000000063`, all distinct from the inherited nonce.

## Complete-mask receipt

Every one of the 64 external oracle directories contains non-empty
`oracle.stdout` and `attrib.tsv`, an empty `oracle.stderr`, and a
`SHA256SUMS` file whose three entries revalidated byte-for-byte.  Every row
reports Q1271, 9,024 shots, ancilla zero, zero bare-R mask, zero deterministic
mask, a matching nonce, sorted unique shot indices in `[0,9024)`, and
disjoint classical and conditional-phase masks.

The canonical row framing is one LF-terminated row per nonce in frozen order:

```text
nonce\tq=1271\tshots=9024\tcls=<sorted CSV>\traw_phase_total=<decimal>\tcond_phase=<sorted CSV>\tanc=0
```

- 64-row canonical-mask bytes / SHA-256: `11,282` /
  `4ee3022cac1798c1d50e871db2518c7142750e6bd272e56b08e8b3bf05e1553e`;
- relative file-manifest framing: for each nonce, filename order
  `attrib.tsv`, `oracle.stderr`, `oracle.stdout`, encoded as
  `nonce\tfilename\tsha256\n`;
- 192-row relative manifest bytes / SHA-256: `17,472` /
  `0faa6512fc6240c71fd42c82ef8ddaf6c77f1990f0887604283e838e8b6c1072`.

Aggregate complete-mask statistics are classical `1,093`, raw phase `843`,
conditional phase `298`, ancilla `0`, and attribution rows `304`.  Per-nonce
ranges are classical `6..32`, raw phase `6..23`, conditional phase `1..11`,
and attribution rows `1..12`.  These distributions are descriptive only; the
qualification gate is complete bit-for-bit mask equality on every row.

External oracle artifacts remain under
`/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d/h64-oracle`
and remain excluded from Git.

## Next gate

Import the donor recurrence semantics into target-bound source, derive all
geometry from the frozen target stream, and require complete mask equality on
the inherited row and H64.  Predictor source and exact H64 parity must be
sealed and pushed before the D32 object is revealed.
