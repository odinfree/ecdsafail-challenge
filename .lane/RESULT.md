# Immediate replay-boundary notch: compare 20 -> 19

Status: **rejected**. The resource reduction is real, but the unchanged inherited nonce is not verifier-clean.

## Target identity and mutation

- Measurement UTC: `2026-08-23T00:14:36Z`
- Exact live base: `087cafaef46a4e339644a6191ff2df2e7031cb80`
- Base tree: `4e2c565ef6ec215c444958eb0939b733c464e130`
- Base parent: `940e34acbc9cdc9ac497f67eea40db80551d1f7c`
- Branch: `research/immediate-compare19-087cafa`
- Sole circuit mutation: `SUB4_PP_REPLAY_CHUNK_COMPARE` default `20 -> 19` in `src/point_add/pingpong_div.rs`
- Base file blob: `17298ab9fe667e1a511d227360c6aee90e9ccf5f`
- Candidate file blob: `8063d22db89c923573534edc5426d375a2f986ce`
- Inherited nonce default remained `251000962439`; no relevant `SUB4_*`, `PPF_*`, or `DIALOG_*` override was present.

The worktree had no `target/`, `ops.bin`, or `score.json` before `./benchmark.sh`. The runner performed a fresh locked/offline release build, emitted a new stream, and ran the unchanged full 9,024-shot evaluator.

## Resource measurement

| metric | live compare 20 | compare 19 | delta |
|---|---:|---:|---:|
| emitted operations | 12,953,930 | 12,926,071 | -27,859 |
| qubits | 1,275 | 1,275 | 0 |
| average executed Toffoli | 918,972.304 | 917,825.810 | -1,146.494 |
| total executed Toffoli over 9,024 shots | 8,292,806,075 | 8,282,460,106 | -10,345,969 |
| rounded Toffoli | 918,972 | 917,826 | -1,146 |
| score if verifier-clean | 1,171,689,300 | 1,170,228,150 | -1,461,150 |

The compare-19 score is counterfactual: the evaluator correctly did not write `score.json` after the validity failure.

Candidate `ops.bin`:

- size: `51,094,533` bytes compressed
- uncompressed artifact bytes reported by the builder: `723,859,992`
- SHA-256: `ae588d6227dddfe5bdb996ae55cd1137d2424fdb3c9ba87dcff30f8e45087ab2`

## Full inherited-nonce diagnostic

- tested shots: `9,024`
- classical mismatches: `9`
- phase-garbage batches: `12`
- ancilla-garbage batches: `0`
- terminal verdict: `FAIL`

The candidate therefore cannot be promoted or submitted with the inherited nonce.

## Exact classical-predictor compatibility

The frozen peak-1275 C++ classical model was compiled locally in a temporary directory with only its diagnostic op-count guard rebound from `12,953,930` to this exact `12,926,071`-operation stream. It loaded the candidate and reported:

```text
nonce 251000962439 pred_cls=9 walk_div=3 replay_div=0 walk_mul=6 replay_mul=0 result=0 shots=9024 first=2550
```

The nine predicted fault-shot indices matched the trusted evaluator's nine classical mismatch indices exactly:

```text
2550  2664  2773  3491  7557  7658  8204  8315  8626
```

Predictor masks were `4,4,1,1,4,4,4,1,4`, consistent with the `3` divide-walk and `6` multiply-walk breakdown. The diagnostic binary rejected the previous 12,953,930-operation target with exit code `2`. This establishes exact inherited-nonce classical compatibility; it does not convert the temporary count-bound diagnostic into a deployable target guard.

Neither `pred<=4` nor `pred0` was exercised: the only evaluated nonce was `pred_cls=9`. No nonce search was run.

## Immediate interpretation beside the Q1274 lane

The independent exact-live Q1274 composition is verifier-clean at diagnostic average T `919919.48`, while the live Q1274 ceiling is rounded T `919693`; that lane needs at least `226` rounded T removed. This compare-19 notch removes `1,146` rounded T, so its reduction is large enough in magnitude, but it remains Q1275 and invalidates the inherited nonce. It is evidence for a coupled replay/square-ladder lever, not a transferable or promotable patch by itself.

## Receipt checksums

Generated logs and helper binaries remain outside Git.

```text
d251ea2cf4ceecd1ec3f1ac02e3b978fa4fb6cf52bc90b93102c5bec7cdfa3de  benchmark log
07eea5f263df8c0b18ae4af6b785a78db43b8ce6dc8a8d32a032741427cb2f0b  trusted index diagnostic log
7bd2418d0ef61346571a7aec0beebeb4821f83ec09d31a4281ebaf7c2abf807a  predictor breakdown log
c3dc697bb196883565ad90b6388f2baee9ebde17da227b5418afb829c78fc511  predictor faultshot receipt
4f4f62e1d57904cc4dca61f93d1389eddc00eebe924b419344003f1d08b56ae1  exact gate-total diagnostic log
11d6c7de68f73eb061bac6f4aa886f5b40df9f9751016d6c018b2e89c7173159  temporary local predictor binary
```

No fleet, provider, hunt, submission, or promotion action was taken.
