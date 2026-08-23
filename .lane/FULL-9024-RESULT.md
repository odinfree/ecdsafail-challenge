# Q1270 routed checkpoint: full 9,024-shot receipt

Date: 2026-08-23. Verdict: `SCORE_GO / VALIDATION_DIRTY`.

## Frozen identities

- source commit:
  `90770b10664fc89065b1d05ac792370efed4c629`;
- source tree:
  `944593de97d412f8b4c7242f7d0aff98002c0d04`;
- `src/point_add/pingpong_div.rs` SHA-256:
  `9b1e5e8540a01584e1238c27328481ba67db3b167aa199db4113e846f1eb6295`;
- `src/point_add/mod.rs` SHA-256:
  `3fbe6baa8bb4638217f7416b858f4ddd57906fdaaecc500d860f1ca96f1ed60f`;
- unchanged evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- clean rebuild `build_circuit` binary SHA-256:
  `279db7d5849cba75ac23a68839fcebe540ca06bfc8c434a7fddee96a1d7f279d`;
- clean rebuild `eval_circuit` binary SHA-256:
  `1228ba592ce13474eb44e44c1e45e83ca6072cb849f26d5ff4f71f8e0c3b80e0`.

The release binaries were rebuilt with `--locked --offline` from an empty
target directory. The candidate environment was exactly:

```text
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_EVICT_DOUBLED_OUT=1
SUB4_PP_ALIAS_TARGET0_SIGN=1
SUB4_PP_EVICT_SIGN_XOR_ADD=1
SUB4_PP_PEAK=1270
SUB4_PP_MUL_REPLAY_PEAK=1271
SUB4_SQUARE_LADDER=240
SUB4_PINGPONG_TAIL_NONCE=65700024945645
```

No other `SUB4_*` variable was present.

## Fixed operation stream

- emitted operations: `12,953,636`;
- compressed bytes: `49,316,215`;
- `ops.bin` SHA-256:
  `ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a`;
- qubits / classical bits: `1270 / 961,070`.

This reproduces the artifact frozen by the structural GO exactly.

## Unchanged trusted evaluator: one run

The unchanged evaluator was invoked exactly once against the artifact above
and completed all 9,024 shots.

- harness-displayed exact average T: `916366.972`;
- rounded T: `916367`;
- average executed Clifford: `10731503.349`;
- rounded score: `1,163,786,090`;
- frozen comparison score: `1,163,831,339`;
- strict score margin: `45,249`;
- classical mismatches: `23`;
- conditional-phase-garbage batches: `14`;
- ancilla-garbage batches: `0`.

The first overall failure was the first classical mismatch at shot 373:

```text
X got = expected
0x475d6ba08a4d29e6f1df0d4a12146768bc94d168fedfb2acb97018f0cdc50406

Y got
0x769c259ac50506ba26ce9543c267436b1c18e9b45743f45834315e174359baaf

Y expected
0xba63dd9f96cf7505c2bc5efba126d28c08300fed1c69b173b8ab6a260780a575
```

There was no ancilla mismatch. The unchanged evaluator retains only the first
overall failure reason. Because classical shot 373 was encountered first, it
does not expose the first conditional-phase batch; the totals prove 14 such
batches, and batches 0 through 4 were clean. No second evaluator run was made
to manufacture an unavailable phase index.

The appended evaluator row SHA-256, including its newline, was
`f3129ffaa2140d0a31951ee9ccd57aada32a7cf15454f09060015afcd4bfc0f7`.
The tracked `results.tsv` was then restored from 9 rows to its exact 8-row
pre-run SHA-256
`eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.
No `score.json` was emitted because the unchanged evaluator exits on a dirty
validity result; the rounded score above follows its documented integer
rounding rule.

## Decision and exact handoff

The product gate passes, but validity does not. The candidate is therefore
`SCORE_GO / VALIDATION_DIRTY / NO HUNT` and cannot be submitted.

The only authorized successor is a source-bound combined predictor lane rooted
at commit `90770b1` and artifact `ec4fadc0...eb63a`. It must bind the exact
source trace, correction checkpoints, and conditional-phase schedule; freeze
the inherited nonce plus deterministic disjoint H64 and unopened D32 corpora;
and obtain complete classical and conditional-phase masks for the inherited
and H64 sets before importing any donor model. A model for classical failures
alone is insufficient because this receipt has both `23` classical failures
and `14` conditional-phase batches. No nonce search is authorized until the
source-bound predictor clears its sealed validation gates.

No provider, GPU/CUDA worker, range, search, submission, or public note was
used in this gate.
