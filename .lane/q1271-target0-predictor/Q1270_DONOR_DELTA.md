# Q1271 terminal donor to future Q1270 routed predictor delta

Decision: `READ_ONLY_MANIFEST / IMPORT_FORBIDDEN / Q1270_H64_ORACLE_SEAL_REQUIRED`.

This file records the exact terminal Q1271 CPU donor and every source-derived
identity that a later Q1270 port must replace. It is not an importer and does
not authorize a Q1270 edit, model build, model output, private-fixture reveal,
provider, CUDA, scan, range, hunt, fleet, submission, or public note.

At inspection, the Q1270 predictor worktree was clean and pushed at
`b6c8b52f3b84eddb8b967be0520459dc3e5e8b2f`, tree
`79328578de985fd54b9426dcd6312b995cc5d571`. Its inherited complete-mask
receipt was sealed, H64 was only authorized, and H64 was not yet sealed. No
Q1270 file was changed or imported while preparing this manifest. A later port
must reopen that lane and require a newer pushed H64 trusted-oracle seal; this
snapshot never satisfies the import gate by itself.

## Frozen terminal donor

- terminal Q1271 commit / tree:
  `f852dee3ce4fec2c17235491944314c38d0393bb` /
  `b8ce92b74019eccc7be0498b9b602af0d9b9ce9f`;
- `src/pp_model.h` SHA-256:
  `46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390`;
- `src/pp_host.h` SHA-256:
  `7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b`;
- `src/ppcpu.cpp` SHA-256:
  `0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba`;
- independently rebuilt CPU binary SHA-256:
  `5c2dc3f4c2be8df9a88d60448e17b65ae3073c285e68f41feaccec96f6f74021`;
- terminal local qualification: inherited + H64 + D32 + fresh F16 exact
  `113/113`, complete-mask FN/FP `0/0`, ancilla `0`, guards `23/23`.

Only the finite-width arithmetic recurrence, bounded CLI framing, phase-trace
composition, and fail-closed loading method are candidate donor semantics. The
three source files above are the complete possible source payload. They become
unqualified target inputs if copied; none of their identities or evidence
transfers.

Do not transfer the Q1271 import tool, operation stream, checkpoint, trace,
phase metadata, generated schedule, binary, oracle, corpus, mask, result,
negative receipt, fresh-fixture receipt, path, branch, or evidence commit.

## Source delta that drives the port

Q1270 source `90770b10664fc89065b1d05ac792370efed4c629`
adds the routed `sign XOR add_out` eviction to the Q1271 target0/sign-alias
source. It checkpoints that derived selector through the clean `routed` AND,
frees it across the correction fold, and reconstructs it for exact uncompute.
The frozen target adds:

```text
SUB4_PP_EVICT_SIGN_XOR_ADD=1
SUB4_PP_PEAK=1270
SUB4_PP_MUL_REPLAY_PEAK=1271
SUB4_SQUARE_LADDER=240
```

The three earlier controls remain enabled:

```text
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_EVICT_DOUBLED_OUT=1
SUB4_PP_ALIAS_TARGET0_SIGN=1
```

Only `SUB4_PINGPONG_TAIL_NONCE=<fixture>` may vary; every other `SUB4_*`
variable is absent. The routed-selector edit adds CX/free lifecycle operations
but no new R/Hmr family. It still changes the exact prefix, ordinals,
checkpoint, operation digest, allocation geometry, and source line bindings.
The lower replay peaks and square ladder also change chunk layouts and phase
site population. Therefore even apparently unchanged arithmetic must be
re-derived and requalified.

## Exact donor-to-target replacements

| binding | Q1271 donor: reject | Q1270 target: bind or derive |
|---|---|---|
| circuit source | `a22090374a957d29a3331d6c876ad12ff45fea31` | `90770b10664fc89065b1d05ac792370efed4c629` |
| source tree | `018eb52de8ab3e6337864338683821c0cbb574a2` | `944593de97d412f8b4c7242f7d0aff98002c0d04` |
| full-run evidence | Q1271 source receipt | `953acb44fbcbb32ab097a52be31ae365db41bd92` plus the future pushed H64 seal |
| `pingpong_div.rs` | `943267f11183a8f028530a0be2cebb68dd39bfbd78b4a7df52d14be50b68efa0` | `9b1e5e8540a01584e1238c27328481ba67db3b167aa199db4113e846f1eb6295` |
| `point_add/mod.rs` | `147d6a8f0ea029b254f97bf7b50d22064114004ad6d96b06fc0fccc159740796` | `3fbe6baa8bb4638217f7416b858f4ddd57906fdaaecc500d860f1ca96f1ed60f` |
| Q / bits | Q1271 / donor geometry | Q1270 / `961,070` |
| operation count | `12,919,161` | `12,953,636` |
| operation SHA-256 | `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa` | `ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a` |
| traced body / tail | `12,919,065 / 96` | `12,953,540 / 96` |
| op-site trace | `56e084c152701707310c6822f7b914652a5d17d2352efd2255fd513492a0b4ce` | raw `766a9b06009560333d3d2790001dfdda18e419123a9c3234732ee045373af36b`, compressed `069ae8682265a831a69bb7861e210fc58e62b7e76422bc66d0ed2f3a81ad4173` |
| R/Hmr words | `1,941,386` | `1,947,720` |
| phase families | `2,579 / 694 / 694 / 3` | `3,267 / 694 / 694 / 3` |
| phase source lines | `1577 / 1846 / 2006 / 1501` | `1585 / 1854 / 2031 / 1501` |
| total phase sites | `3,970` | `4,658` |
| phase metadata SHA-256 | `665e64bb22d87ba629a133f7c67813c284a7fca47d1b6212914c83abe0f5fa1e` | `fba2270e4c4fed53db5625612c72b930dc821bb8c54c4ed43df5855f845bca0b` |
| schedule header SHA-256 | `49f82e4effec2c110fed73974df306cbcae9ac456043cb329bb15a7b5e97f4e8` | `17720a6855002f12f0b90ce8598139bfa4f5d2ec0e1ed72d6579177da9a43d35` |
| host state digest | `a05fe6ce236b1bfc` | derive anew from the exact Q1270 host representation after the H64 oracle seal |
| serialized checkpoint | no transferable artifact | `PPFSCKP1`, 5,064 bytes, SHA-256 `75deeae0d80122a3ce30a7337b34128af5dc964bc26ba0b77c2d6599abdb937f` |
| replay peaks | divide `1271`, multiply `1272` | divide `1270`, multiply `1271` |
| square ladder | `241` | `240` |
| inherited validity aggregate | `11/10/0` | `23/14/0` from the unchanged full evaluator |
| inherited trusted masks | classical `11`, raw phase `10`, clean phase `4` | classical `23`, raw phase shots `15`, clean phase `4`, ancilla `0` |

The target host state digest is deliberately not inferred from the serialized
checkpoint SHA. The port must either load `PPFSCKP1` with a byte-equivalent
state/tail representation or recompute from the exact operation stream, then
seal its own `PP_EXPECTED_STATE_DIGEST_VALUE`. The negative matrix must compile
a one-bit-wrong target digest rather than retain the Q1271 negative constant.

The source currently indicates 696 divide rounds, 696 multiply rounds, the
same 700-entry sampled width table, `floor(r * 703 / 695)`, repair disabled,
and replay compare window 20. Those are semantic observations, not transferable
identities. Re-derive them from `90770b1`, verify the routed-selector lifecycle,
and bind them in the target predeclaration before the first model output.

## File-by-file rewrite manifest

### `src/pp_model.h`

Start only from donor SHA
`46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390`.
Before compiling or running it:

- replace the Q1271 source label and comments with Q1270 source `90770b1`;
- set distinct replay peaks to divide `1270` and multiply `1271`;
- set square ladder `240`;
- re-derive both round counts, the width schedule/map, repair state, chunk
  compare width/order, fold widths, endpoint logic, and round-zero behavior;
- audit the new sign-XOR eviction as a value-neutral lifecycle, including its
  interaction with routed/doubled-out/target0 aliases;
- update phase-family source lines to `1585/1854/2031/1501`;
- require the target schedule to drive exactly 4,658 phase emissions on every
  classically clean shot;
- compute a new target model-source SHA-256. The donor model hash is forbidden
  in any Q1270 identity output.

### `src/pp_host.h`

Start only from donor SHA
`7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b`.
Replace all of:

- `PP_SOURCE_COMMIT`, `PP_EVIDENCE_COMMIT`, operation count/SHA, and lane/error
  labels;
- `PP_EXPECTED_STATE_DIGEST_VALUE`, derived from the exact target state;
- any checkpoint/tail loader assumptions not byte-equivalent to the frozen
  Q1270 `PPFSCKP1` artifact;
- target source comments and the resulting host-source SHA-256.

Retain fail-closed magic/count/full-SHA/state/tail checks. The 96 nonce-tail
records must reproduce the Q1270 checkpoint's 4,096-byte inherited XOF
selfcheck before corpus derivation.

### `src/ppcpu.cpp`

Start only from donor SHA
`0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba`.
Replace:

- the Q1271 description and hard-coded `phasefaultshots` source string;
- the hard-coded classical-model SHA in `identity` with the newly ported
  Q1270 `pp_model.h` SHA;
- all generated schedule bindings by including only the target header;
- any Q1271 path, corpus, expected geometry, or receipt used by a runner.

Keep scan/range absent. Build twice from independent paths and require exact
binary equality plus SHAKE256 empty/`abc` vectors.

### Derivation and qualification tools

Do not port the Q1271 extractor or generator. The already source-bound Q1270
tools are:

- compressed-trace extractor SHA-256:
  `ffc168d817e98508067abaac228cfb5f5c7a97d2efeca737071427c05358acd6`;
- schedule generator SHA-256:
  `b4a2f6be2d1dc36200167a6cb4a2854b1c16f70ea93bf3bf84fffcbdf707dd2c`.

Run them independently against the frozen compressed trace and require exact
metadata/header hashes `fba2270e...bca0b` / `17720a68...43d35` before any
model row. Generated metadata, ledger, header, checkpoint, operations, binary,
masks, and logs remain outside Git.

Every target qualification runner must replace its lane/root paths, branch and
remote ref, source/evidence seals, expected Q/bits/operations, operation and
trace hashes, checkpoint/state digest, phase metadata/header, source/model/
host/CPU hashes, CPU binary, oracle source/binary, corpus hashes, result hashes,
repeat hashes, negative receipts, and freshness domains. No Q1271 fixture
result or receipt can appear in a Q1270 positive gate.

## Target identities already frozen, but nonportable

- inherited list SHA-256:
  `dabc177103443bede607625489337794ac828e25b60e787a67f7789bfa1627f1`;
- Q1270 H64 list SHA-256:
  `87fb300f0f1aa12cb4c6e70c24f0cae7899313c1cc5bd6f92ab70c06848314bd`;
- private unopened Q1270 D32 SHA-256:
  `09941a9174ee19346039a000ceb7f907a13aecaab0a47bf4f0d4b3272508240e`;
- target oracle source / deterministic binary SHA-256:
  `4059969b3cca026a637e7fc735acc8c214d23a5172344d25463dff0ecf128b60` /
  `de84cf864bd80b7acf934259fa5435e4103d9b387167456091d85ca34ce9acfd`;
- target evaluator source / rebuilt binary SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b` /
  `ee52b3968f50e182b356d7253ba580abbb4291264af6ca09a112ff025c746d23`;
- inherited canonical row SHA-256:
  `a2515e8989d873b721c59e9c58354f6b61d9754d0fb3291dd046ff9b6cc8f004`;
- inherited classical / raw phase / clean phase / ancilla mask SHA-256:
  `38eef3e8ef39a27f6bf870837c362b62c5a82c39baa908b7c0836962fdefe31f` /
  `dccf69ee17c206a477e85dfbc9b88919ea1cb13868d40999a1f3259388187d98` /
  `d4faa8308f5820b4af1ad8e237f741ed1f486f71da070dbec57f213b8c9eef98` /
  `3731b0a75ab19d96b774da62d37eccacd517c6593af20aa66525dc0b951cdba9`.

These target identities may be consumed only after reopening their exact files
and commits. They do not authorize donor import while the H64 oracle receipt is
missing, and the private D32 values remain unopened.

## Mandatory later activation sequence

1. Reopen the Q1270 worktree and remote; require clean equality at a pushed
   commit that seals inherited plus all 64 H64 trusted complete masks.
2. Verify the Q1270 operation, trace, checkpoint, phase metadata/schedule,
   oracle, evaluator, corpus, and structural-source identities above again.
3. Predeclare the exact terminal donor `f852dee...` and a hash-bound,
   no-overwrite import of only the three donor source files.
4. Treat copied files as unqualified; complete every replacement in this
   manifest before compiling or producing model output.
5. Independently rebuild and seal the target model/host/CPU/schedule/binary
   identities. Require exact inherited complete classical and clean-phase
   masks first.
6. Run the frozen Q1270 H64 once and require full ordered 9,024-bit classical
   and `raw_phase & ~classical` equality on `64/64`, zero FN/FP, Q1270,
   9,024 shots, and ancilla zero. Any mismatch kills the family.
7. Commit and push that target model/H64 seal. Only then may the private Q1270
   D32 be opened to the frozen predictor under its existing reveal rule.
8. Run target-specific fail-closed negatives and deterministic repeats. No
   later phase grants provider, CUDA, range, hunt, fleet, or submission
   authority without a separate explicit gate.

Until step 1 is satisfied, the only allowed use of this file is read-only port
planning. The terminal Q1271 donor remains sealed and the future Q1270 import
remains `HOLD`.
