# C4 exact-675 width-2 comparator lifetime gate

Date: 2026-08-24

## Verdict

`HARD_NACK_C4_WIDTH2_GLOBAL_Q_LIFT`

The approved D3 secondary synthesis removes the one transient carry from the
`n=2`, no-`c_in` specialization of `cmp_lt_phase_conditioned`, replacing one
conditioned CCX with one conditioned CCZ. Its nonlinear gate count is therefore
T-flat. The removed wire, however, is never live at a promoted Q1267 allocation.
It lowers only the candidate site's local maximum from Q1142 to Q1141; all
global binders survive, so actual-675 Q, T, and projected score do not improve.

No source or production probe was edited. This is a diagnostic-only lifetime
gate.

## Exact binding

- Base commit: `67524171baaf568dc3dc606f38515745f70804ff`
- Base tree: `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Audit branch: `research/codex-replay-sign-donor-20260824`
- Audit source diff from base: empty
- Plain default operations: 12,593,858
- `ops.bin` SHA-256:
  `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e`
- Release `build_circuit` SHA-256:
  `a587c4b22862e3927868ba9bb9d79b3f98070999c52eb8f42286eb14e39896e4`
- Peak allocation log SHA-256:
  `16f0d3102e702942d92b498c9171fd534cd982121be7f35ff46ead110cf5745f`

Relevant source SHA-256:

| Path | SHA-256 |
|---|---|
| `src/point_add/arith/compare.rs` | `0d1cf305c68263cd078ec96c10b2b00135bef21492f81ff4e3d7d45d33e5191e` |
| `src/point_add/pingpong_div.rs` | `953dd851629e4d15a4f56d5061e3c0d61ea83bebab8f7aca5243636d4f240c38` |
| `src/point_add/mod.rs` | `596ed58d4d61fbb087ccf236c728efc09631632a96693d849a71c03bea866a06` |

## Exact candidate and promoted sites

The only candidate is the leading chunk-0 boundary repair in
`add_chunked_measured_with`:

- boundary erase closure and call: `pingpong_div.rs:2116-2122`;
- generic transient carry allocation/lifetime: `compare.rs:447-490`;
- divide replay family: late-carry call `pingpong_div.rs:2333`, invoked from
  `replay_halving_round` at line 1742;
- multiply replay family: late-carry call `pingpong_div.rs:2652`, invoked from
  `replay_doubling_round` at line 1752.

The promoted plan produces layout `[2,127,127]` with ladder budget 128 at
exactly 337 dynamic sites across two source families:

| Family | Rounds | Sites |
|---|---|---:|
| divide | 2 through 334 inclusive | 333 |
| multiply walkback | 325, 323, 321, 319 | 4 |
| **total** | | **337** |

The operation-stream checker matches the exact relational gate pattern, not
only operation kinds, and agrees with the schedule count.

## Lifetime and peak intersection

Each pattern starts with the measured boundary's HMR. The comparator scratch is
allocated one operation later and released immediately after its own reset:

- divide first interval: `[914688,914702)`;
- divide last interval: `[2420640,2420654)`;
- all 333 divide intervals have stride 4,536;
- multiply intervals: `[10227976,10227990)`, `[10241464,10241478)`,
  `[10254914,10254928)`, `[10268414,10268428)`.

B0 at both divide endpoints and at each of the four multiply intervals reports
`best_active=1142` and exactly one owner at `arith/compare.rs:447`. Therefore
every one of the 337 removable scratch lifetimes has local Q1142.

The bound peak trace has 1,665 distinct Q1267 allocation indices:

| Phase | Count | First op | Last op |
|---|---:|---:|---:|
| `pp_div_replay` | 993 | 913421 | 4268648 |
| `pp_mul_walkback` | 672 | 8322690 | 11712170 |
| **total** | **1,665** | | |

Exact half-open interval intersection between all 337 scratch lifetimes and all
1,665 peak indices is zero.

The closest witness is stronger than a coarse phase-level disjointness claim:
the first scratch dies at op 914702, and Q1267 is reached only five operation
positions later at op 914706. B0 at 914706 has 126 current chunk carries owned
by `pingpong_div.rs:1992` and no `compare.rs:447` owner. The four multiply
analogues reach Q1267 at 10227994, 10241482, 10254932, and 10268432, likewise
five positions after their candidate scratches die, with the same 126-carry
binder and no comparator scratch.

This is the declared falsifier: removal would have to hit at least one global
Q1267 allocation. It hits zero, and the immediately adjacent surviving peak
identifies the independent owner that still binds.

## Q/T economics

The D3 premise is one conditioned CCX to one conditioned CCZ under the same
outer phase predicate, so nonlinear T does not increase. The lifetime result
prevents converting that T-flat synthesis into a global-Q lift:

```text
baseline Q = 1267
baseline T = 911220.65625
baseline score = 1154516571.46875
candidate global Q = 1267
candidate structural nonlinear T delta = 0
projected score delta = 0
local-only maximum = 1142 -> 1141
```

## Reproduction commands

Run from the audit worktree root.

```sh
git diff --exit-code 67524171baaf568dc3dc606f38515745f70804ff -- \
  src/point_add/arith/compare.rs src/point_add/pingpong_div.rs src/point_add/mod.rs

shasum -a 256 \
  src/point_add/arith/compare.rs \
  src/point_add/pingpong_div.rs \
  src/point_add/mod.rs \
  ops.bin \
  artifacts/replay-sign-donor-20260824/b0-replay-peak.log \
  target/release/build_circuit

python3 artifacts/replay-sign-donor-20260824/check_c4_width2_lifetime.py --repo .
```

The exact B0 windows used for the six candidate representatives:

```sh
for spec in \
  914688:914702 2420640:2420654 \
  10227976:10227990 10241464:10241478 \
  10254914:10254928 10268414:10268428
do
  lo=${spec%%:*}
  hi=${spec##*:}
  env B0_WIN_LO=$lo B0_WIN_HI=$hi ./target/release/build_circuit 2>&1 \
    | rg 'B0_CENSUS|B0_OWN|emitted ops'
done
```

The immediately adjacent surviving binders:

```sh
for spec in 914706:914706 10227994:10227994
do
  lo=${spec%%:*}
  hi=${spec##*:}
  env B0_WIN_LO=$lo B0_WIN_HI=$hi ./target/release/build_circuit 2>&1 \
    | rg 'B0_CENSUS|B0_OWN|emitted ops'
done
```

No fetch, network, provider, push, submission, or production edit occurred.
