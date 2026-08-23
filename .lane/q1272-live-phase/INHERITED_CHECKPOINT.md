# Q1272 inherited combined-mask checkpoint

Verdict: `PASS_INHERITED / H64_FROZEN / NO RANGE`.

The exact live-source Q1272 operation stream and independently regenerated
conditional-phase schedule reproduce the trusted inherited classical and
conditional-phase masks completely.  This checkpoint precedes every H64 model
result and does not authorize CUDA, a provider, a range, a hunt, or submission.

## Immutable target and classical cross-check

- structural source / evidence commits:
  `73422709ed70ba9725b3cb592770bcf197df4cdb` /
  `41dd0b4508527081b8d24255adf0579389f02453`;
- operation count / SHA-256: `12,904,643` /
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- predictor checkpoint digest: `e9b2d20ecd1169a8`;
- exact constants: rounds `696/696`, sampled schedule `r*703/695`, sparse
  repair disabled, fold `54`, endpoint `20`, flag `22`, chunk compare `20`,
  peak `1272`, square ladder `242`;
- independently sealed primary classical checkpoint / tree:
  `01e06d605c1de3cea4571b033e1d16dc820bfbdf` /
  `506ba5874d55dbea6506a43235e1cc4aa7f51305`;
- sealed Rust classical source SHA-256:
  `2d016070a93a5966c5a163a6242b27ef8264176c76c72448ba50027b70465890`.

The source-exact C++ adaptation is independent of that Rust implementation.
Both produce the complete inherited 23-shot classical set with canonical
index SHA-256
`c46041ff454200ba4d2ab3cffcefb2b118e4afd839f674431762b24da37f8848`.

## Source-derived conditional-phase schedule

The diagnostic trace adds only `#[track_caller]` to R/Hmr emission while
building and removes it before source sealing.  The uninstrumented target
files retain their exact hashes.  The trace contains `12,904,547` source-site
rows plus the exact untraced 96-operation nonce suffix and `1,938,616` R/Hmr
words.  Its SHA-256 is
`f2f0f99d096027299460d9a82c16d3714c9684564d10f13f6dcbbac2b3e92833`.

The regenerated phase schedule has 3,964 predicates:

- 2,573 replay chunk carries at `pingpong_div.rs:1558`;
- 694 divide flags at `pingpong_div.rs:1813`;
- 694 multiply flags at `pingpong_div.rs:1928`;
- three arithmetic-shell carries at `arith.rs:1501`.

Schedule-ledger / generated-header SHA-256:
`59c177b5b43bf27eba1ee6758a7c1cea07f0eef5aa9b0c2a27dfe05301c6657d` /
`de37d6004427082c345004d1225d0f877abfe9597ac969df228b77eb915fe42f`.
The generated files remain outside Git.

## Trusted oracle and inherited equality

The already-qualified two-pass oracle remains source-exact because the target
and Q1273 donor have byte-identical `circuit.rs`, `sim.rs`, curve source,
`Cargo.toml`, and `Cargo.lock`.  Oracle source / binary SHA-256:
`26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98` /
`90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`.

For nonce `65700024945645`, the oracle reports Q1272, 9,024 shots,
classical/raw-phase/ancilla `23/8/0`, and exactly one conditional clean-phase
shot, `3290`.  The C++ model matches both complete masks:

- classical index-set equality: `23/23`, SHA-256
  `c46041ff454200ba4d2ab3cffcefb2b118e4afd839f674431762b24da37f8848`;
- conditional-phase equality: `1/1`, SHA-256
  `5f9b22d477a0b834d38b916d94025e6b09fb86cd980e49804a4da296b799e5ed`;
- oracle stdout / attribution SHA-256:
  `230ce787840da6838ae7632851d4a7109d4ab1fda4e802c872eed38c91e1c3b2` /
  `58d3ba81bf890f9edfe22067f24b9faf694e72170014b02d0e9c74b9fc6a8f54`.

The lone clean event is attributed to a Gidney measured-uncompute site; there
is no bare-R or deterministic clean residue.  Raw phase on classically dirty
shots is not claimed.  The next gate is the already frozen H64 complete-mask
comparison; D32 remains unopened.
