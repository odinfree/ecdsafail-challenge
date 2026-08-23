# Q1271 target0/sign-alias D32 holdout qualification

Verdict: `PASS_D32_32_OF_32 / NO_POST_REVEAL_SEMANTIC_EDIT / NEGATIVES_NEXT`.

The precommitted, disjoint D32 fixture list was opened only after the exact
model/H64 source commit and pre-reveal seal were pushed.  The unchanged local
model reproduces every complete trusted classical and conditional-phase mask.
There were no mismatches, aborts, geometry failures, or nonzero ancillas.
This receipt grants no CUDA, provider, scan, range, hunt, fleet, submission,
or public-note authority.

## Reveal and identity boundary

- terminal model/H64 commit:
  `08a9da2093bd5fececbaebc7569de55b12243d9f`;
- pre-reveal seal commit:
  `613a2320ef412d9753f0a7add7ae55e32d807fd5`;
- precommitted D32 runner commit / tree:
  `ec2253a685e43b9929e4796786df5e2f2fc37ff8` /
  `b8f73122485aefc05834fef045e09ec5a2e5efc3`;
- runner SHA-256:
  `b816c4a516e876d0acafe73ae0a2deff0fbfeeeb3ec0ddf8b8c2ead705752325`;
- D32 Git object:
  `3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e:.lane/q1273-wrap-exact/D32.nonces`;
- D32 byte SHA-256:
  `62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90`.

The 32 rows are unique canonical unsigned decimals below 2^48 and are
disjoint from inherited nonce `65700024945645` and the frozen H64 corpus.
Before reveal, the runner required a clean worktree, both seals as ancestors,
and exact hashes for source, operations, trace, phase metadata, generated
schedule, trusted oracle, CPU binary, and H64 results.

Model / host / CPU source SHA-256 remained exactly:

- `46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390`;
- `7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b`;
- `0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba`.

The model source directory has a zero Git diff from the terminal H64 commit.

## Exact result

Across 32 unchanged 9,024-shot oracle draws:

- complete classical masks: exact `32/32`, faults `565/565`;
- complete conditional-phase masks: exact `32/32`, faults `155/155`;
- raw phase faults retained as trusted context: `435`;
- per-row classical range: `9..28`;
- per-row raw-phase range: `8..23`;
- per-row conditional-phase range: `1..9`;
- Q / shots / ancilla on every oracle row: `1271 / 9024 / 0`;
- model/oracle mask mismatches: `0`;
- generated `RESULTS.tsv` SHA-256:
  `b95a6aa454329b6f85a37e88859b755c961e3502e981c4dc6aec34fbd652b8d3`.

The inherited fixture and final ordered D32 row were then rebuilt and
evaluated again.  Oracle attribution/output and both model channels were
byte-identical; the transitive repeat-manifest SHA-256 is
`494486e0cda2f106575ce48cdb914af2a89e661e1b841b0543226f6e6cb5b679`.

All revealed fixtures, operations, masks, binaries, attribution, and logs
remain outside Git under
`/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d/d32-v1`.

## Next gate

Run the fixed fail-closed negative matrix against the same source-bound CPU
binary.  Only after the guard matrix is sealed may a genuinely fresh fixture
holdout be frozen and opened.  The model semantics remain immutable.
