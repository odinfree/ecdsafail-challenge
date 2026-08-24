# Exact Prefix Boundary Erase Design

## Goal

Test whether the promoted ping-pong point-add can erase every consumed chunk
boundary immediately and exactly without extending its existing at-most-two
boundary-wire lifetime.

## Source and authority

- Source commit: `67524171baaf568dc3dc606f38515745f70804ff`
- Source tree: `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Branch: `research/codex-exact-boundary-recompute-20260824`
- Local CPU and offline Cargo only. No fetch, push, provider, or submission.

## Architecture

The production function `add_chunked_measured_with` already allocates at most
two boundary wires. It consumes a predecessor boundary in the next chunk, then
measures and frees that predecessor immediately. Its phase repair currently
replays a comparator on only the upper `replay_chunk_compare()` bits of the
completed local chunk, so it is explicitly approximate and omits carry from the
lower global prefix.

An opt-in environment flag,
`SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE=1`, changes only the comparator operands
used by the existing erase closure. For a boundary after bit `hi`, it compares
`acc[..hi]` with `addend[..hi]`. With implicit carry-in zero, the unsigned
relation between the completed sum prefix and the addend prefix is the exact
carry-out predicate at that boundary. The allocation order, chunk schedule,
erase timing, and boundary lifetime remain unchanged.

When the flag is absent or has any value other than `1`, the existing local
slice `hi - min(replay_chunk_compare(), hi - lo)..hi` remains byte-for-byte the
default construction path.

## Components and data flow

Only `src/point_add/pingpong_div.rs` changes:

1. A small pure range-selection helper chooses the comparator start index.
2. The existing erase closure reads the opt-in once per circuit construction.
3. The closure passes either the full prefix or the unchanged local slice to
   `cmp_lt_phase_conditioned`.

No new persistent qubits, caches, retained carries, or alternate chunk layout
are introduced. The full-prefix comparator may allocate more temporary carry
wires and emit more Toffoli operations; that measured cost is the experiment.

## Error handling and isolation

The env flag is strict: only the string `1` enables the experiment. Invalid or
missing values fall back to the exact baseline byte stream. Existing assertions
inside `cmp_lt_phase_conditioned` continue to guard non-empty equal-width
operands. The change is isolated to a new worktree and branch from the exact
source commit.

## Tests and decision gate

1. Add a focused unit test for local versus exact range selection, including a
   chunk whose lower prefix can create a carry that a local slice cannot see.
2. Compile the repository with Cargo `--offline`.
3. Build once from unmodified source and hash `ops.bin`; after implementation,
   rebuild with the new flag absent and require the same SHA-256 byte hash.
4. Run `PP_PROFILE=1` for the exact 64 deterministic lanes with the flag absent
   and with `SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE=1`. Record classical mismatch,
   phase, dirty qubits, peak qubits, and average executed Toffoli.
5. Return `ADMIT` only if the flag-on result has zero classical mismatch, zero
   phase, zero dirty qubits, peak qubits below 1267, and a projected `Q*T` score
   below the current exact-675 baseline. Otherwise return `HARD_NACK` with
   baseline-to-experiment deltas.

This is a local mechanism/economics result only. It does not open submission or
support a promoted-winner claim.
