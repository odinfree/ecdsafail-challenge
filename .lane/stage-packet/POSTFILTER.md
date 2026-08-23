# Q1274 finite-list conditional-phase postfilter

This is a source-bound, CPU-only Linux packet for filtering an explicit finite
list produced by an exact classical screen. It contains no range/start/count
mode and initiates no provider, host, scan, hunt, or submission action.

## Exact contract and identity

The modeled mask is only:

`clean_phase_mask = evaluator_phase_mask & ~exact_classical_mask`.

A row is emitted only under the conjunction:

`exact_classical_mask == 0 && clean_phase_mask == 0`.

The executable refuses any listed nonce that is not classically clean; the
wrapper then publishes no partial output or receipt. Raw phase on classically
dirty shots is outside the model. No CUDA phase implementation or parity claim
is included.

The ordinary loader binds evaluation before corpus derivation to:

- source `fe0b7bac6348fb35b7680784d4295899e498d0e3`;
- operation count `12,920,073`;
- `ops.bin` SHA-256
  `4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c`;
- predictor checkpoint/tail digest `d2c95102cb9a277d`;
- exactly `9,024` derived shots per nonce and the sealed source schedule.

## Linux build

Build to an untracked path outside this packet:

```sh
.lane/stage-packet/build_phase_postfilter_linux.sh \
  /tmp/q1274-phasepostfilter
```

The build script requires Linux and `g++`, verifies every manifest row, uses
`-O3 -std=c++17 -pthread`, verifies the compiled identity, and prints the
resulting binary SHA-256. It refuses to overwrite a file or place the binary
inside the tracked packet. No binary is committed.

## Production wrapper

The nonce list must be a non-empty newline-terminated ASCII file with exactly
one canonical decimal value per line, no duplicates, and every value below
`2^48`. No comments, blank rows, sign, surrounding whitespace, or leading zero
are allowed.

```sh
.lane/stage-packet/phase_postfilter.sh \
  --binary /tmp/q1274-phasepostfilter \
  --ops /exact/path/ops.bin \
  --nonces /exact/path/classical-clean.nonces \
  --output /exact/path/phase-clean.nonces \
  --receipt /exact/path/phase-clean.receipt
```

The output contains only canonical decimal nonces, in input order. It is also
written to stdout after atomic publication. The deterministic receipt binds
the input/output row counts and SHA-256 values, binary SHA-256, all source
identities, output schema/order, conditional contract, and explicit raw/CUDA
non-claims. Existing output or receipt paths are never overwritten.

The executable exposes `audit` solely for frozen masked-set verification. It
accepts the same finite-list grammar but reports nonce, exact classical count,
clean-phase count, and complete sorted clean-phase set. Production must use
`filter` through the wrapper.

## Verification

On a locally compiled CPU binary and exact `ops.bin`:

```sh
.lane/stage-packet/verify_phase_postfilter.sh \
  /exact/path/ops.bin /tmp/q1274-phasepostfilter
```

The gate checks:

- frozen23 and blinded disjoint32 complete masked-set equality and every
  per-set SHA-256;
- repeated deterministic wrapper output and receipt;
- exact-classical precondition failure without partial publication;
- empty, unterminated, whitespace, signed, leading-zero, non-decimal, blank,
  duplicate, and out-of-range lists in both executable and wrapper;
- wrong magic, wrong count, and same-count/wrong-SHA streams before output;
- a fresh rerun of the unchanged 22-case, 323-row classical ledger.

The only frozen classically-clean production fixture is nonce
`100000035106674`. It is correctly omitted because its complete clean-phase
set is `{1753,5833}`. No recovered wave result is used as a positive example.
