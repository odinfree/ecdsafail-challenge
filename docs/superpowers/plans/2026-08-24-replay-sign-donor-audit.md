# Replay Sign Donor Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove or falsify whether the actual promoted-675 replay sign/tape qubit can host one exact chunk-entry carry and be restored from the live post-walk registers without prefix replay.

**Architecture:** Check the information invariant before touching production code. A standalone bit-exact classical model reproduces the complement-sandwich add and halving wire permutation, exhaustively establishes the two-preimage collision, and checks the concrete actual-width witness. If it passes, bind the theorem to the exact Rust source plus an actual 64-lane profile and narrow B0 owner/op-site census, then issue a durable `HARD_NACK`; no env-gated source probe is created.

**Tech Stack:** Python 3 standard library, Rust/Cargo release build, existing `PP_PROFILE`, B0 census, operation-site and allocator traces, Git, SHA-256.

## Global Constraints

- Source commit is exactly `67524171baaf568dc3dc606f38515745f70804ff`; source tree is exactly `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`.
- Work only in `ecdsafail-replay-sign-donor-codex` on branch `research/codex-replay-sign-donor-20260824`.
- Use local CPU and offline Cargo dependencies only.
- Do not fetch, push, launch providers, submit, or touch another worktree.
- Audit exactly the active replay sign/tape donor family; do not switch to another donor.
- The post-walk-state collision is the first falsifier. If it survives, stop without production probe code.
- Keep generated `ops.bin` untracked.

---

## File map

- Create `artifacts/replay-sign-donor-20260824/check_sign_collision.py`: deterministic mathematical reproducer for the ordinary walk transform and collision theorem.
- Create `artifacts/replay-sign-donor-20260824/sign-collision.log`: captured reproducer output.
- Create `artifacts/replay-sign-donor-20260824/binding.log`: exact commit/tree/source hashes and toolchain receipt.
- Create `artifacts/replay-sign-donor-20260824/pp-profile.log`: actual 64-lane Q/T/correctness and phase-peak trace.
- Create `artifacts/replay-sign-donor-20260824/b0-replay-peak.log`: narrow replay-peak B0 owner and allocation-site census.
- Create `artifacts/replay-sign-donor-20260824/source-sites.log`: exact source excerpts for sign creation, replay use, and reverse clear.
- Create `artifacts/replay-sign-donor-20260824/REPORT.md`: evidence, hashes, commands, counts, deltas, and terminal classification.
- Do not modify `src/point_add/**` if the collision reproducer passes.

### Task 1: Mechanical first falsifier

**Files:**
- Create: `artifacts/replay-sign-donor-20260824/check_sign_collision.py`
- Create: `artifacts/replay-sign-donor-20260824/sign-collision.log`

**Interfaces:**
- Consumes: ordinary `walk_round` invariant `sign = target_pre[1] XOR source[1]`, complement sandwich, and exact halving permutation.
- Produces: exit status zero only when every reachable post-state bucket at widths 4 through 10 has exactly two opposite-sign preimages and the width-259 concrete witness collides.

- [ ] **Step 1: Write the collision checker**

Create the file with this exact implementation:

```python
#!/usr/bin/env python3
from collections import defaultdict


def complement_sandwich_add(width: int, source: int, target: int, sign: int) -> int:
    mask = (1 << width) - 1
    sign_mask = mask if sign else 0
    return (((target ^ sign_mask) + source) & mask) ^ sign_mask


def halving_wire_permutation(width: int, value: int) -> int:
    bits = [(value >> i) & 1 for i in range(width)]
    for i in range(width - 1):
        bits[i], bits[i + 1] = bits[i + 1], bits[i]
    bits[width - 1] ^= bits[width - 2]
    return sum(bit << i for i, bit in enumerate(bits))


def walk(width: int, source: int, target: int) -> tuple[int, int]:
    assert source & 1 and target & 1
    sign = ((target >> 1) ^ (source >> 1)) & 1
    summed = complement_sandwich_add(width, source, target, sign)
    return sign, halving_wire_permutation(width, summed)


def main() -> None:
    witness_width = 259
    witness = [(target, *walk(witness_width, 1, target)) for target in (1, 3)]
    assert witness == [(1, 0, 1), (3, 1, 1)], witness
    print("actual_width=259 witness_source=1 branches=" + repr(witness))

    total_inputs = 0
    total_collision_keys = 0
    for width in range(4, 11):
        buckets: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
        for source in range(1, 1 << width, 2):
            for target in range(1, 1 << width, 2):
                sign, post = walk(width, source, target)
                assert post & 1 == 1
                assert ((post >> (width - 1)) & 1) == ((post >> (width - 2)) & 1)
                buckets[(source, post)].append((target, sign))

        expected_keys = 1 << (2 * width - 3)
        assert len(buckets) == expected_keys
        assert all(len(preimages) == 2 for preimages in buckets.values())
        assert all({sign for _, sign in preimages} == {0, 1} for preimages in buckets.values())
        inputs = 1 << (2 * width - 2)
        total_inputs += inputs
        total_collision_keys += len(buckets)
        print(
            f"width={width} inputs={inputs} post_keys={len(buckets)} "
            f"preimages_per_key=2 signs_per_key=0,1"
        )

    print(
        f"PASS total_inputs={total_inputs} total_collision_keys={total_collision_keys} "
        "sign_is_not_a_function_of_post_walk_state=true"
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the checker and capture its receipt**

Run:

```bash
python3 artifacts/replay-sign-donor-20260824/check_sign_collision.py 2>&1 | tee artifacts/replay-sign-donor-20260824/sign-collision.log
```

Expected final line:

```text
PASS total_inputs=349504 total_collision_keys=174752 sign_is_not_a_function_of_post_walk_state=true
```

Expected actual-width witness:

```text
actual_width=259 witness_source=1 branches=[(1, 0, 1), (3, 1, 1)]
```

- [ ] **Step 3: Enforce the stop branch**

If Step 2 does not exit zero with both exact lines above, stop execution and return to brainstorming; do not improvise a donor implementation. If it exits zero, production probe code is forbidden by the approved falsifier and the remaining tasks collect source/trace evidence only.

- [ ] **Step 4: Commit the mechanical proof artifact**

```bash
git add artifacts/replay-sign-donor-20260824/check_sign_collision.py artifacts/replay-sign-donor-20260824/sign-collision.log
git commit -m "test: reproduce replay sign collision"
```

Expected: one commit containing only the checker and its deterministic log.

### Task 2: Exact-source and actual-width trace binding

**Files:**
- Create: `artifacts/replay-sign-donor-20260824/binding.log`
- Create: `artifacts/replay-sign-donor-20260824/pp-profile.log`
- Create: `artifacts/replay-sign-donor-20260824/b0-replay-peak.log`
- Create: `artifacts/replay-sign-donor-20260824/source-sites.log`

**Interfaces:**
- Consumes: successful Task 1 theorem receipt and exact source commit.
- Produces: exact source hashes, offline binaries, actual 64-lane correctness/Q/T, replay peak index, and B0 owner allocation sites including the retained tape signs.

- [ ] **Step 1: Capture exact source and toolchain binding**

Run:

```bash
{
  git rev-parse 67524171baaf568dc3dc606f38515745f70804ff
  git rev-parse 67524171baaf568dc3dc606f38515745f70804ff^{tree}
  git rev-parse HEAD
  git rev-parse HEAD^{tree}
  git diff --check
  rustc --version
  cargo --version
  shasum -a 256 Cargo.lock src/point_add/mod.rs src/point_add/pingpong_div.rs src/point_add/pp_profile.rs
} 2>&1 | tee artifacts/replay-sign-donor-20260824/binding.log
```

Expected first two lines are `67524171baaf568dc3dc606f38515745f70804ff`
and `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`; the next two bind the current
evidence commit/tree and `git diff --check` emits nothing.

- [ ] **Step 2: Compile the trusted and untrusted local binaries offline**

```bash
cargo build --release --offline --bin build_circuit --bin eval_circuit
```

Expected: `Finished release profile`; no network access.

- [ ] **Step 3: Run the actual 64-lane profile**

```bash
env PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1 TRACE_PHASE_ACTIVE=1 TRACE_PHASE_ACTIVE_TOP=12 TRACE_EACH_PEAK=1 ./target/release/build_circuit 2>&1 | tee artifacts/replay-sign-donor-20260824/pp-profile.log
```

Expected terminal correctness line:

```text
PP_PROFILE lanes=64 classical_mismatch=0 phase=0x0 dirty_qubits=0
```

Expected binding on the promoted source is peak Q 1267 in `pp_div_replay`. Record the exact reported `peak_ops_idx`, total executed Toffoli, emitted ops, and every mismatch.

- [ ] **Step 4: Run a narrow B0 replay-peak owner/op-site census**

Use the profile-reported peak index without guessing:

```bash
profile_peak_idx=$(sed -n 's/.*PP_PROFILE peak_qubits=[0-9]* peak_ops_idx=\([0-9]*\).*/\1/p' artifacts/replay-sign-donor-20260824/pp-profile.log | head -n 1)
profile_win_lo=$((profile_peak_idx - 256))
profile_win_hi=$((profile_peak_idx + 256))
env B0_WIN_LO="$profile_win_lo" B0_WIN_HI="$profile_win_hi" B0_PHASE=pp_div_replay TRACE_OP_SITES=1 TRACE_ALLOC_NEAR_PEAK=1267 ./target/release/build_circuit 2>&1 | tee artifacts/replay-sign-donor-20260824/b0-replay-peak.log
```

Expected: `B0_CENSUS_BEGIN best_active=1267 ... best_phase=pp_div_replay`, plus `B0_OWN` rows whose caller sites account for the retained sign/tape allocation, coefficient/output registers, live interleaved walk registers, and the peak-local replay scratch. Any missing census or different peak is a mismatch to report, not a reason to widen the experiment silently.

- [ ] **Step 5: Capture the exact sign lifecycle and replay op sites**

```bash
{
  nl -ba src/point_add/pingpong_div.rs | sed -n '359,460p'
  nl -ba src/point_add/pingpong_div.rs | sed -n '1645,1764p'
  nl -ba src/point_add/pingpong_div.rs | sed -n '2480,2547p'
  nl -ba src/point_add/pingpong_div.rs | sed -n '2628,2710p'
  nl -ba src/point_add/memory/WAYFINDER.md | sed -n '132,145p'
} > artifacts/replay-sign-donor-20260824/source-sites.log
```

Expected source facts: sign allocation and low-bit predicate at `walk_round`; target complement, chunked add, and second complement inside both fused replay cells; sign clear/free only after inverse permutation/add in `walk_back_round`; and the checked-in general two-preimage theorem.

- [ ] **Step 6: Hash and commit the trace bundle**

```bash
shasum -a 256 artifacts/replay-sign-donor-20260824/binding.log artifacts/replay-sign-donor-20260824/pp-profile.log artifacts/replay-sign-donor-20260824/b0-replay-peak.log artifacts/replay-sign-donor-20260824/source-sites.log
git add artifacts/replay-sign-donor-20260824/binding.log artifacts/replay-sign-donor-20260824/pp-profile.log artifacts/replay-sign-donor-20260824/b0-replay-peak.log artifacts/replay-sign-donor-20260824/source-sites.log
git commit -m "evidence: bind replay sign liveness trace"
```

Expected: one evidence commit; `ops.bin` remains ignored and untracked.

### Task 3: Terminal evidence report

**Files:**
- Create: `artifacts/replay-sign-donor-20260824/REPORT.md`
- Modify: no source files

**Interfaces:**
- Consumes: Task 1 collision receipt and Task 2 exact-source/profile/B0 receipts.
- Produces: one source-and-trace-backed C3 `HARD_NACK` with exact commands, hashes, counts, baseline economics, and any mismatch.

- [ ] **Step 1: Write the report with the exact evidence**

The report must contain:

```markdown
# C3 active replay-sign donor audit

## Classification

`HARD_NACK_ACTIVE_REPLAY_SIGN_DONOR`

## Exact binding

- base commit/tree
- evidence commits/trees
- source and artifact SHA-256 hashes
- Rust/Cargo versions

## Functional counterexample

- the recurrence and complement-sandwich derivation
- the width-259 `(source,target_pre,sign,target_post)` witness pair
- exhaustive widths 4..10 counts and total 349,504 inputs / 174,752 collision keys
- explanation that identical post-walk `u/v` with opposite sign rules out Clifford reconstruction and every deterministic reconstruction

## Actual schedule/liveness

- exact R1/R2/round defaults from source
- actual PP_PROFILE Q/T/peak phase/op index and 0/0/0 correctness
- B0 owner counts and source sites at the peak
- pre-add/idle/post-add sign uses and later reverse-clear dependency

## Economics and decision

- no candidate stream was built because the first approved falsifier fired
- Q/T deltas are therefore zero/not-applicable, not an inferred win
- the donor cannot hold a boundary carry and be restored without retaining equivalent information or replaying the inverse prefix
- no second donor family, provider, submission, fetch, or push was attempted

## Reproduction

- every exact command from Tasks 1 and 2
- artifact hashes and any mismatch/counterexample
```

- [ ] **Step 2: Verify report consistency and repository cleanliness**

Run:

```bash
rg -n "ADMIT|HARD_NACK|349504|174752|1267|classical_mismatch|phase=|dirty_qubits" artifacts/replay-sign-donor-20260824/REPORT.md
git diff --check
git status --short --branch
```

Expected: no placeholders, exactly one terminal `HARD_NACK`, evidence counts match logs, and only `REPORT.md` is untracked before the final commit.

- [ ] **Step 3: Commit and freeze final hashes**

```bash
git add artifacts/replay-sign-donor-20260824/REPORT.md
git commit -m "docs: hard-nack active replay sign donor"
git rev-parse HEAD
git rev-parse HEAD^{tree}
shasum -a 256 artifacts/replay-sign-donor-20260824/REPORT.md
git status --short --branch
```

Expected: clean branch and a final local evidence commit. Do not push or submit.
