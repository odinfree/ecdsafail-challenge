# Q1271 live-source combined predictor predeclaration

Decision boundary: `FROZEN / NO MODEL OUTPUT YET`.

This lane qualifies a source-bound classical plus conditional-phase CPU screen
for the exact Q1271 doubled-out-lifecycle stream.  It does not modify the
circuit or evaluator and grants no CUDA, provider, range, hunt, submission, or
public-note authority.

## Structural and score binding

- source commit / tree:
  `b69c17e16e0b9140d14f15c7d87314352ecaf7be` /
  `8749e54dd9c3d801cd79edb5ff22b43c87fac0b9`;
- terminal structural packet commit:
  `1d2726698ebeb298852ce8b5c23d3d54a700cdd9`;
- terminal frozen-eight evidence SHA-256:
  `600eb93cd8d6b16cd0afac30007f9fe36561d24bb30e1b53ec9a96d022b56aec`;
- `src/point_add/pingpong_div.rs` SHA-256:
  `0b95700c5c977e9128ce609840da5996928e873313195fcd44935b06ed7df15a`;
- `src/point_add/mod.rs` SHA-256:
  `c4aa38c73e79e3d5860616b31e3f507c888667390c857b319bb912dae1fd538d`;
- exact environment:
  `SUB4_PP_EVICT_DOUBLED_OUT=1 SUB4_PP_PEAK=1271 SUB4_SQUARE_LADDER=241`;
- calibration tail nonce: `65700024945647`;
- expected operation count / SHA-256:
  `12,926,780` /
  `a13de41544a81672b07674acabecec0bb054201b8d1634ed79745bbc4be2f23e`;
- measured stream result: Q `1271`, exact T `915675.850`, rounded T
  `915676`, rounded score `1,163,824,196`, channels `13 / 17 / 0`.

The artifact must be rebuilt with a forced build under exactly the frozen
environment and calibration nonce.  Count, full compressed SHA, Q, exact T,
and the inherited channel counts must all reproduce before model work starts.

## Single declared model family

Port the terminal combined CPU recurrence from commit
`83ad631e1a99db3db1c3886b4d61ff9ded94b0f5`, but transfer semantics only:

1. preserve the exact 256-bit field, finite-width walk, wrap, replay,
   terminal-loan, round-zero sparse reverse, fold, and add3x recurrences;
2. retarget only source-bound constants for peak `1271`, square ladder `241`,
   and the doubled-out lifecycle;
3. derive the operation checkpoint, nonce tail, R/Hmr count, phase-site
   ordering, family table, and phase ordinals anew from this exact source;
4. model the doubled-out eviction as the proven CX-only loan/rematerialization
   lifecycle, never as a new arithmetic approximation;
5. claim only `clean_phase_mask = raw_phase_mask & ~classical_mask` and only
   after complete classical-mask equality.

No fixture, operation, phase-table, checkpoint, digest, or artifact hash from
Q1272 transfers.  If this one family cannot be made source-exact, stop and
localize the first semantic divergence; do not tune against blind rows.

## Frozen fixture order

- inherited list SHA-256:
  `697dfcab8f33ab39c2f5ad706834c18d0440d4c76046b58f1df42fafe955111e`;
- H64 list SHA-256:
  `17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9`.

1. Rebuild and bind the exact calibration artifact.
2. Build a current-source two-pass trusted oracle and reproduce the eight
   inherited rows in `INHERITED.nonces`, including the packet's per-row
   classical/raw-phase counts and Q1271/9,024/ancilla-zero guards.
3. Before any predictor output, generate and seal trusted complete masks for
   the 64 nonces in `H64.nonces`.
4. Adapt the declared model using source geometry and inherited rows only.
5. Require exact complete classical and conditional-phase masks on all eight
   inherited rows, then reveal model output on H64 once.  Any H64 mask mismatch
   is terminal `HOLD` for this family.
6. Only after an H64 `64/64` evidence commit is pushed, reveal the disjoint D32
   object `3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e:.lane/q1273-wrap-exact/D32.nonces`,
   whose required byte SHA-256 is
   `62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90`.
   Run it once without any post-reveal model edit.
7. Repeat the calibration row and final D32 row deterministically, then run
   fail-closed loader/state/command negatives.

The D32 runner must prove uniqueness, canonical decimal framing,
less-than-2^48 range, and disjointness from both earlier corpora before opening
any mask.

## Exact gates

- every trusted row: Q `1271`, shots `9024`, ancilla `0`;
- exact operation magic, count, compressed SHA, checkpoint digest, tail shape,
  source hashes, phase schedule, and predictor source/binary hashes;
- complete 9,024-bit classical-mask equality;
- complete conditional-phase-mask equality on classically clean shots;
- canonical sorted unique shot indices in `[0, 9024)`;
- no abort, partial row, approximate count-only comparison, or silent fallback;
- deterministic byte-identical repeats;
- scan/range mode absent or hard-disabled.

All raw operation streams, binaries, traces, tables, masks, evaluator output,
and logs remain outside Git.  Commits contain only durable source, runners,
hash manifests, and evidence summaries.
