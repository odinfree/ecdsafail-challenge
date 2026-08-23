# Q1271 target0/sign-alias pre-D32 model seal

Verdict: `SEALED_AND_PUSHED / D32_REVEAL_AUTHORIZED_LOCALLY`.

- terminal model/H64 commit:
  `08a9da2093bd5fececbaebc7569de55b12243d9f`;
- terminal model/H64 tree:
  `d6d790781bb094d0f6280c498adbc1f9cb67d80e`;
- branch: `research/q1271-target0-sign-alias`;
- remote: `odinfree/research/q1271-target0-sign-alias`;
- worktree after push: clean;
- model / host / CPU SHA-256:
  `46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390` /
  `7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b` /
  `0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba`;
- exact H64 parity: inherited `1/1`, H64 `64/64`, mismatches `0`;
- H64 results SHA-256:
  `3819de96a6d5351a53a8bd6b45371467cc2fa8f5ee7b5162fc34239391e2e6d7`.

This seal permits opening only the already-precommitted D32 synthetic fixture
list and running the unchanged local oracle/model comparison.  It grants no
provider, CUDA, scan, range, hunt, fleet, submission, or public action.  A
post-reveal semantic source edit invalidates D32 qualification.
