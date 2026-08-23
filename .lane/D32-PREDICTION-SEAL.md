# Q1272 selector eviction: blinded D32 prediction seal

Date: 2026-08-23

## Verdict

`D32_PREDICTION_SEALED`; `EVALUATOR_STILL_BLIND`; `GO_D32_EVALUATOR_REVEAL`;
`HOLD_D32_VERDICT`; `HOLD_CUDA`; `HOLD_RANGE`; `HOLD_HUNT`;
`HOLD_PROVIDER`; `HOLD_SUBMIT`.

After the local H64 exact-mask result was sealed at
`5558fb941d870e6546cb50d01fd43305ceb6b162`, the unchanged predictor scored
the already-frozen private D32.  No D32 operation artifact or trusted
evaluator result existed when this prediction receipt was committed.

## Bound prediction

```text
private D32 nonce-set SHA-256  ae6be39a5193eee86c96485a0bcdc8caec46782f2eb8697bff1d97f9e331bab2
predictor source SHA-256       b2a4d44c89b5340c7cc7d2db8a11b8cebc9207537a0f6883445d9dd85799e9b4
predictor binary SHA-256       f7e16bd373708d90d839105ca7e5bf00b46a202bb1ffa05e850c1ecc7e5551db
prediction output SHA-256      dd1296442729e24ab586b730a266e03141dbf0ed8cfa5ebc38c14c94c40133f3
predictor stderr SHA-256       e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
rows                           32
predicted classical faults     745
minimum row count              11
maximum row count              34
mask words per row             141
mask bits per row              9024
```

The private nonce values and complete masks remain outside Git.  The output
hash commits to every nonce, count, mask bit, and row order before evaluator
reveal.  The tracked worktree and `results.tsv` remained unchanged.

## Next gate

For each sealed D32 nonce, build only the exact Q1272 selector stream and run
the existing output-only trusted evaluator over the unchanged 9,024 shots.
Require Q1272, 12,908,488 operations, 9,024 shots, and ancilla zero per row.
Only after all rows finish may the evaluator-mask manifest be hashed and
compared with the already-sealed prediction.  Any bit mismatch is
`FAIL_MODEL`; no correction, CUDA work, or range may follow a failure.
