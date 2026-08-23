# Q1274 conditional-phase postfilter predeclaration

Status: predeclared before implementation.

## Frozen base and scope

- branch base: `8802a5b619dcd309e539e6417ed17abebe5d9ecf`;
- circuit source: `fe0b7bac6348fb35b7680784d4295899e498d0e3`;
- exact operation count: `12,920,073`;
- exact `ops.bin` SHA-256:
  `4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c`;
- predictor state digest: `d2c95102cb9a277d`;
- phase contract: `clean_phase_mask = evaluator_phase_mask & ~exact_classical_mask`;
- final predicate: `exact_classical_mask == 0 && clean_phase_mask == 0`.

This lane packages a CPU-only Linux postfilter for an explicit finite list that
an upstream exact classical screen claims is clean. It does not generate a
nonce, infer a range, accept a start/count pair, contact a host, or submit a
result. Raw phase on already-classically-dirty shots and CUDA phase parity are
out of scope.

## Production input and output contract

The wrapper will require named paths for the executable, exact `ops.bin`, input
list, output file, and receipt. The input grammar is deliberately canonical:

- non-empty, newline-terminated ASCII file;
- exactly one canonical unsigned decimal nonce per line;
- no sign, leading zero (except the value `0`), whitespace, blank, or comment;
- every nonce is in `0 <= nonce < 2^48`;
- duplicate nonces are fatal.

The executable will independently enforce the same grammar and range rather
than trusting the wrapper. It will process the finite list once, in input
order, with one prefix load and one combination-table build. If any listed
nonce has a nonzero exact classical mask, the whole run fails closed and the
wrapper publishes no partial output.

The output is newline-delimited canonical decimal nonces, in stable input
order, and contains a row only when both exact masks are zero. Phase-dirty
classically-clean inputs are omitted. The wrapper writes output and receipt via
temporary files and renames them only after a successful run. It refuses to
overwrite an existing destination. The deterministic receipt binds input and
output row counts and SHA-256 values, executable SHA-256, all frozen identities,
and the literal conditional contract.

## Planned packet

- shared CPU phase evaluator extracted without changing the existing
  `ppcpu phasefaultshots` behavior;
- dedicated finite-list `phasepostfilter` C++ executable;
- Linux `g++` build script that emits only a caller-selected scratch binary;
- fail-closed shell wrapper with atomic publication;
- verifier and immutable fixtures/manifest; generated binaries, logs, output
  rows, receipts, and `ops.bin` remain untracked.

## Frozen gates

1. The current direct CPU build remains compiling, and source identity gates
   operation framing/count/SHA plus predictor digest before evaluation.
2. Existing frozen23 and blinded disjoint32 complete masked sets remain exact,
   including every sorted set and its SHA-256.
3. The unchanged 22-case, 323-row classical ledger remains exact; its prior
   terminal provenance is base commit `8802a5b` and it will be rerun after the
   shared-helper extraction.
4. Wrong magic, wrong count, and same-count/wrong-SHA streams fail before
   evaluation.
5. Empty, missing-final-newline, whitespace, signed, leading-zero, non-decimal,
   duplicate, and `>=2^48` lists fail closed without publishing output.
6. The inherited classically-clean canary `100000035106674` is allowed only as
   a frozen fixture and must be omitted because its exact clean-phase set is
   `{1753,5833}`. No recovered wave result supplies a positive row.
7. Repeated runs over the same sealed binary, stream, and list must produce
   byte-identical output/order/SHA and receipt content.

Any complete-set mismatch, classical regression, partial output on error,
identity bypass, nondeterminism, or unbound final predicate is terminal until
repaired and all gates restart. No provider, remote, range, scan, hunt,
submission, CUDA phase work, or recovered-wave input is authorized.
