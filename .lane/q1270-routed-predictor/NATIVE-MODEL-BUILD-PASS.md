# Q1270 target-native model build receipt

Date: 2026-08-23. Decision:
`BUILD PASS / DETERMINISTIC UNIT PASS / FULL MASK QUALIFICATION UNRUN`.

This gate implements the three empty target files predeclared for
`q1270_native_recurrence_v1`. It uses only the sealed Q1270 source, target
configuration, checkpoint, and active-width identities. No donor model source,
table, checkpoint, operation stream, schedule, mask, fixture result, or binary
was read or copied.

## Reviewed source identities

- `src/q1270_pp_model.h` SHA-256:
  `2e5e7542dda34d543d855b03a337fd466c5acaa61201bcf242346755c403f2a1`;
- `src/q1270_pp_host.h` SHA-256:
  `65a9f341d4f79c4a1c009a30e7f080cae06c7e6cc9fdb8a00116af7181db69db`;
- `src/q1270_ppcpu.cpp` SHA-256:
  `1c1e9ff51176f5598ecc4df36367cecaf19920eb35abc68147eaa0aa2e8687f4`.

The model implements the target source's 259-bit signed round-zero lift,
696-round alternating finite-width walk, literal rescaled width schedule,
terminal `+1/-1` guard, forward halving replay, reverse doubling replay,
54-bit pseudo-Mersenne folds, 66-bit seed fold, and the exact target source's
double sign-CX cancellation in the round-one inverse seed. The four routed
lifecycle controls are asserted as value-neutral explicit target configuration,
not inferred from source defaults.

The host requires:

- source `90770b10664fc89065b1d05ac792370efed4c629`;
- operation count/SHA `12,953,636` / `ec4fadc0...eb63a`;
- exact `PPFSCKP1` 5,064-byte checkpoint / `75deeae0...b937f`;
- canonical host-state FNV-1a digest `e0d66eb521941b4f` computed over the exact
  parsed checkpoint byte representation;
- exact active-width file / `c49b95b0...a8bf5`;
- explicit replay peaks `1270/1271`, square ladder `240`, and all four enabled
  routed lifecycles.

It rejects missing/drifted paths, SHA or state mismatch, malformed checkpoint
magic/count/residual/tail, a nonce outside 48 bits, width order or direction
drift, target defaults, and malformed Fiat-Shamir inputs.

## Independent builds

Apple clang `17.0.0 (clang-1700.6.3.2)`, C++20, `-O3 -DNDEBUG`, strict
`-Wall -Wextra -Werror`, and OpenSSL `3.6.2` produced two byte-identical arm64
binaries from separate output paths. One build used relative source/include
paths and the other absolute paths.

- build A/B binary SHA-256:
  `38e95b03bcb19079bb0697e890a7a218fc7d278f91f45a0454236dbefedf5b7f`;
- identical `identity` output SHA-256:
  `c7107e205415146c6ed9cda0bd3d4b0c1858bf067acd11c9eb2ba13c6334ef99`;
- identical `selftest` output SHA-256:
  `10497c962e4ca914ae3e5cb1fa0b2127bde9e59c0a769fc5bd0b2673b91dfdeb`.

The binary links the exact local OpenSSL 3 libcrypto plus system libc++ and
libSystem. Binaries and outputs remain under the two explicit `/private/tmp`
build directories and are not tracked.

## Deterministic unit gate

Both builds passed:

1. SHAKE256 empty and `abc` 64-byte standard vectors;
2. checkpoint size, SHA, magic, operation count, residual, canonical host
   digest, and all 96 paired-X tail records;
3. two byte-identical 4,096-byte inherited-nonce XOF derivations, SHA-256
   `f1aa1dfaa85591410290df883b62700eec8f32abb69ec7098f9b5ade669fb67d`;
4. exact 696+696 direction-labelled active-width rows and selected Q1270 width
   anchors;
5. target-native divide and multiply recurrence on inherited Fiat-Shamir shot
   zero, compared independently with exact secp256k1 modular products.

Shot zero is classically clean in the already sealed inherited mask, so this
is a deterministic positive unit without importing a mask into the executable.
A missing-input negative exited `1`, emitted nothing on stdout, and named the
missing frozen path on stderr.

## Boundary of this receipt

This is a build and deterministic unit receipt, not inherited-mask equality.
The CLI intentionally exposes only `identity` and `selftest`; it contains no
scan/range/provider/search/submission surface and has not read D32 or created
F16. The next authorized gate must add bounded complete-mask output and compare
all 141 inherited classical and clean-phase words before H64. Until then the
model is `BUILD GO / QUALIFICATION HOLD`.
