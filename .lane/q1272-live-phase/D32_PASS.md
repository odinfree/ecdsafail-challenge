# Q1272 D32 combined-mask qualification

Verdict: `PASS_D32_32_OF_32 / CPU_COMBINED_EXACT / NEGATIVES PASS`.

The source-bound CPU model reproduces every complete trusted classical and
conditional-phase mask on the frozen, disjoint D32 corpus.  The model and
phase schedule were not edited after the holdout was revealed.  There were no
mismatches, aborts, geometry failures, or nonzero ancillas.  This receipt does
not authorize CUDA, a provider, a range, a hunt, or submission.

## Frozen identities

- target source / operations:
  `73422709ed70ba9725b3cb592770bcf197df4cdb` /
  `12,904,643` /
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- model checkpoint: `e9b2d20ecd1169a8`;
- model / host / CPU source SHA-256:
  `0d4c9a812892b9dac598cb59a8345c443b9e21663ac29743578f4e651b39b92a` /
  `aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2` /
  `dd05545d33911e7e0ab44b0e373f03a759ae8ee4b990f20f2cc40ca6ee2063af`;
- local CPU binary SHA-256:
  `47366b9d7d131639bb0ed9a8abc9cb87bd9c3b9aa5b746d0dcbc464ac9ba435c`;
- pre-reveal runner commit / SHA-256:
  `03a89b7` /
  `dde7f925a1e5271ed3ccf2ae06b61d15e2ea53322a837519447ba8c5e232b809`;
- frozen D32 list source commit / SHA-256:
  `3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e` /
  `62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90`;
- sealed H64 transitive RESULTS SHA-256:
  `0b05b359ac2f9fc23e81163adcf8047aa28fd514c5ecd581a0416a07ee1b9ccc`.

The 32 nonces are unique, canonical unsigned decimals below 2^48 and disjoint
from the inherited stream and frozen H64.  Their order was read directly from
the precommitted Git object.  The runner required a clean worktree and the
sealed H64 commit as an ancestor before opening that object.

## Exact result

Across 32 unchanged 9,024-shot oracle draws:

- complete classical masks: `32/32`, `550/550` faults;
- complete conditional clean-phase masks: `32/32`, `138/138` faults;
- raw phase faults: `407` (trusted context only on classically dirty shots);
- Q / shots / ancilla on every row: `1272 / 9024 / 0`;
- per-row classical range: `7..29` faults;
- per-row conditional-phase range: `2..8` faults;
- model/oracle mismatches and aborts: `0 / 0`;
- compact transitive RESULTS manifest SHA-256:
  `462cc7c43b5f474a7238a702011227992ebed39bd34c0d7d426d1f8e2a2c6576`;
- deterministic inherited plus final-D32 repeat manifest SHA-256:
  `0569a821c82c37bd5d267009664928bbec4aed79df44f5bb34abbbb2f4d4ec5c`;
- external artifact root:
  `/Users/olifreuler/ecdsa-ops/q1272-live-phase-ea19759d/d32/`.

The repeats are byte-identical across oracle attribution/output and both model
mask channels.  `RESULTS.tsv` binds each row's raw-artifact SHA manifest; all
raw masks, logs, attribution, binaries, operations, and generated tables stay
outside Git.

## Independent classical cross-check

The primary classical lane's earlier Rust D32 model missed one add3x
low-53-fold carry-drop shot.  Its already-sealed shared C++ model contains the
finite-width `pp_mod_add_exact_model` recurrence used here.  This lane's
unchanged C++ model is exact on the full D32, independently confirming that
the C++ recurrence covers that boundary.  The Rust repair remains a separate
primary-lane gate and is not inferred from this receipt.

## Next gate

The fixed fail-closed negative matrix passed `23/23` and is sealed in
`NEGATIVES_PASS.md`.  The next allowed action is an exact-source CUDA port and
CPU=CUDA fixture parity under a separate predeclaration.  Range mode remains
disabled.
