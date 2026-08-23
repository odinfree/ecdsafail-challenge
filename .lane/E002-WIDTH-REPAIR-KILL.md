# E002 — fixed-nonce sparse width-repair terminal receipt

Date: 2026-08-23

Verdict: `KILL / FIVE HARD CLASSICAL FAULTS / NO CIRCUIT EDIT / NO FULL EVALUATION`.

## Exact binding

- predeclaration commit: `1c2a4cb`;
- evidence base / structural source:
  `41dd0b4508527081b8d24255adf0579389f02453` /
  `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- structural tree:
  `fe77bddfb49b426312b1cca3d009b150cd06fd89`;
- `pingpong_div.rs` / `mod.rs` SHA-256, unchanged throughout E002:
  `6e7cce578663d8419c032190a9caa405ca0d84e0512104b766b9c68540f01994` /
  `0c9e9a920d9078f2390028009895f03d495096fdac9d2b596c7913c064e03e63`;
- exact operation artifact: 12,904,643 operations, SHA-256
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- inherited nonce fixture: `.lane/E002-INHERITED-NONCE.txt`, SHA-256
  `dabc177103443bede607625489337794ac828e25b60e787a67f7789bfa1627f1`;
- inherited full result: Q1272, T914783.521 (rounded 914784),
  classical/phase/ancilla `23/8/0`;
- strict Q1272 ceiling: rounded T914961, nominal headroom `+177`.

The fixed diagnostic baseline was independently reproduced three times with
`PP_PROFILE=1`, `PP_PROFILE_SEED=0`, and the exact three-variable source
environment.  All three returned Q1272, `TOTAL 914800.77`, 12,904,547 profiled
operations / 12,904,643 emitted operations, and profiler
classical/phase/dirty `0/0/0`.  The rebuilt artifact reproduced the exact
operation SHA above.

## Exact predictor and complete inherited set

The committed exact-Rust checkpoint was imported from
`01e06d605c1de3cea4571b033e1d16dc820bfbdf`, tree
`506ba5874d55dbea6506a43235e1cc4aa7f51305`.  Its unmodified qualification
source SHA-256 is
`2d016070a93a5966c5a163a6242b27ef8264176c76c72448ba50027b70465890`.
Local runs reproduced its byte-identical stdout SHA-256
`e137d9d4f4ec455830a7cada3fe508ca6f302e3ff0982f660a46d1c5d9dee428`
and the trusted complete set exactly `23/23`:

`292, 925, 1601, 1765, 3094, 3415, 4418, 4546, 4897, 5038, 5165, 5246, 6089, 6515, 6606, 6692, 7209, 7370, 7468, 7956, 8561, 8736, 8954`.

The canonical newline-delimited set SHA-256 is
`c46041ff454200ba4d2ab3cffcefb2b118e4afd839f674431762b24da37f8848`.

## Causal classification and hard witness

The source-bound causal checkpoint was imported from
`d190180a3df6e5d6b9d0b56c9f11014e863dedd1`, tree
`833116cc67dba96a83b7fd648b79b490ab614108`.  Its normalized 23-row fixture
`.lane/q1272-promoted-predictor/INHERITED_CAUSAL_DIAGNOSTICS.tsv` has SHA-256
`ab647dc2345fade447d47547037962e399d66142e57519563769cfe3a93d8fcb`.
Shared model / host / CPU source SHA-256 values are:

- `120979945f82318e9df77014fabea3d2f8a9dea3c433e1ff5636cb3cb654424b`;
- `b635c95deb5bab2b89ea65de4dafdba22ea4184a647c82d4bb5680450f976435`;
- `8dbc8687f2bc5dcfae2861d9ab0e8e757785d7eb608d6d2b05296f04f0c1ae4d`.

An independent local `c++ -O3 -std=c++17 -pthread` build produced binary
SHA-256
`70ab050072651d4d1c37a87efc77f25c6837c2e885e0ff38d26f3ed517ca363e`.
Two complete diagnostic repeats were byte-identical, stdout SHA-256
`b35613a083650e3d9c21c7993a778c338e67dd55c1fad0a95dad1a718ba3c1fd`,
and reproduced the committed 18-soft / 5-hard split.

The five hard witnesses are outside the sole sparse-width family:

| shot | mask | source-localized mechanism |
|---:|---:|---|
| 292 | 8 | replay-multiply coefficient failure |
| 3094 | 8 | replay-multiply coefficient failure |
| 4897 | 8 | replay-multiply coefficient failure |
| 6692 | 2 | replay-divide coefficient failure |
| 7956 | 4 | multiply-terminal failure with no scheduled-width violation |

The other 18 failures are first post-add width deficits of exactly one bit.
Their `(shot -> sampled index)` mapping is:

`925->680, 1601->583, 1765->649, 3415->556, 4418->450, 4546->690, 5038->651, 5165->600, 5246->651, 6089->145, 6515->688, 6606->608, 7209->659, 7370->666, 7468->678, 8561->641, 8736->517, 8954->145`.

This is first-deficit attribution only; repairing one boundary can expose a
later deficit.  Chained-cover work stopped as soon as the five hard witnesses
were verified, exactly as predeclared.

## Bounded +1 control and minimum-set verdict

The exact Rust predictor was extended only with a qualification-only,
fail-closed sampled `+1` diagnostic; the emitted circuit source and operation
stream were untouched.  Final diagnostic source / local binary SHA-256 are
`c66d291f4d1f7882f8e7e47a67fcab5ebaf069d38dceede7fab2a2f8024425fa` /
`bae3cf4ce8979f070d64b5990af8236c0717e9b0c99bdafeb161f09be7731f67`.
With no perturbation it retained the exact stdout SHA above.

The complete 700-single-index matrix found only one immediate clearance:
sampled index 450, width `105 -> 106`, clears shot 4418, creates no new
classical fault, and changes the count `23 -> 22`.  The previously cheap-looking
fixed-seed diagnostic indices `661, 628, 536, 533, 377, 400, 671, 659, 530`
each left the inherited predictor count at 23 when tested singly.  Malformed
`01`, duplicate `450,450`, descending `451,450`, and out-of-range `700`
diagnostic inputs all exited 2.

Because five failures have no admissible width-schedule repair, no finite
sparse `+1` set covers the complete 23-shot fixture.  The family is infeasible;
there is no minimum repair set to price against `+177`.  Fixed-seed cost noise
cannot change that semantic lower bound.

## Terminal boundary

The predeclared hard-fault gate fires before a circuit semantic edit, chained
soft-cover search, candidate pricing, or unchanged full 9,024-shot evaluation.
No phase/ancilla claim is made for a candidate because no candidate exists.
No provider, range, hunt, fleet, submission, or public-note action occurred.
