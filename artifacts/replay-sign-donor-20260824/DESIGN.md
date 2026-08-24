# C3 active replay-sign donor audit design

Date: 2026-08-24

## Binding and authority

- Source commit: `67524171baaf568dc3dc606f38515745f70804ff`
- Source tree: `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Branch: `research/codex-replay-sign-donor-20260824`
- Worktree: `ecdsafail-replay-sign-donor-codex`
- Execution: local CPU and offline dependencies only
- Forbidden: fetch, push, provider launch, submission, or edits outside this
  worktree

## Mission and decision rule

Audit exactly one conditionally-clean/output-hosted donor family in the actual
promoted 675 replay schedule: the active per-round sign qubit stored in `tape`.
It is a candidate host for one exact top-window entry carry only during the
chunked add interval after it has complemented the replay target and before it
is needed again.

The first falsifier is functional, before any production probe: the sign must
be reconstructible from the live post-`walk_round` `source`/`target` state. If
two source-valid walk inputs with opposite signs reach the same live post-walk
state, the sign is not reconstructible by Clifford operations (or by any
deterministic circuit) before replay. In that case stop with a source- and
trace-backed `HARD_NACK`; do not add probe code.

Only if that falsifier fails may an implementation proceed. The contingency
probe would be strictly gated by one new environment variable, leave default
allocation/order byte-identical, and run actual-width correctness, Q/T, and
default-stream identity gates. `ADMIT` would additionally require lower Q and
a projected score improvement over the bound baseline.

## Donor-family selection

Three families were considered:

1. **Active replay sign/tape (selected).** It is already live at the replay
   peak, controls the pre-add target complement, is idle during the chunked
   add, and is read later in the same fused replay cell. It therefore has the
   correct lifetime if it can be restored from the contemporaneous walk state.
2. **Terminal `u`/`v` passenger wires (rejected).** The terminal loan already
   clears and releases these wires to allocator ownership. They do not remain
   a stable named donor through the interleaved replay cell.
3. **Coefficient/output bits (rejected).** They carry live semantic output and
   are mutated by replay. No conditionally-clean invariant has been established
   for a single bit across the add interval.

## Exact-source invariant test

For ordinary rounds (`round > 1`, excluding only the special fused rounds 0
and 1), `walk_round` computes

```text
sign = target_pre[1] XOR source[1]
```

and the signed wrapped adder implements, modulo the current width,

```text
target_sum = target_pre + (-1)^sign * source.
```

Both operands are odd, so `target_sum` is even. The following swap ladder plus
top-bit CNOT is the reversible halving representation; for small positive
values without overflow it is simply

```text
target_post = target_sum / 2.
```

The candidate collision is:

| source | target_pre | sign | target_sum | target_post |
|---:|---:|---:|---:|---:|
| 1 | 1 | 0 | 2 | 1 |
| 1 | 3 | 1 | 2 | 1 |

Both inputs satisfy oddness and the exact source sign predicate, yet the live
post-walk `(source, target)` state is `(1, 1)` in both cases while the stored
sign differs. This collision must be checked against the exact split/unsplit
adder semantics, width/top-skip constraints, and actual scheduled ordinary
rounds. If it survives, the later inverse relation used by `walk_back_round`
cannot be moved earlier: that relation becomes available only after undoing
the halving permutation and inverse signed add.

The bound tree's own `src/point_add/memory/WAYFINDER.md` states the general
version of this theorem: for every odd post-state and odd source, both candidate
preimages `2*target_post-source` (sign zero) and
`2*target_post+source` (sign one) satisfy the required low-bit predicate. The
audit will rederive and mechanically corroborate that statement rather than
treat the note as proof by assertion.

The audit will also exhaustively enumerate a bounded width using a direct
classical model of the exact source transform, checking all valid odd input
pairs and reporting collision counts. This is corroboration; the concrete
collision is the proof witness.

## Actual-width trace binding

Build the exact source offline, then run the 64-lane profiler with:

- `PP_PROFILE=1` for actual Q/T and phase peak
- `TRACE_OP_SITES=1` for operation-site provenance
- `TRACE_ALLOC_NEAR_PEAK=<bounded threshold>` for peak allocation sites
- a narrow `B0_WIN_LO`/`B0_WIN_HI` window around the measured replay peak and
  `B0_PHASE=pp_div_replay` (and, if necessary, the multiply replay/walkback
  peak) for live-owner census

The trace must bind:

1. sign allocation to `walk_round` and retention in `tape`;
2. its use in the fused replay cell immediately before and after the chunked
   add;
3. concurrent liveness of the interleaved `u`/`v` registers;
4. its eventual clearing/free only in `walk_back_round` after the inverse walk;
5. the exact baseline Q/T and correctness counters.

Raw stdout/stderr, command receipts, hashes, and a concise report will live
under `artifacts/replay-sign-donor-20260824/`. Large generated circuit outputs
remain untracked.

## Acceptance and stop conditions

- **HARD_NACK:** the post-walk collision is valid under exact source
  invariants, or the trace disproves the required donor lifetime.
- **ADMIT:** only after a reconstructibility proof, strict env-gated
  implementation, default byte identity, exact correctness, `Q < 1267`, and a
  projected score below the bound promoted result.
- **No classification by projection alone.** A probe that is incorrect or
  fails stream identity is rejected regardless of nominal Q/T.

This lane does not attempt width-2 Boolean synthesis, checkpoint replay, prefix
replay, or a second donor family.
