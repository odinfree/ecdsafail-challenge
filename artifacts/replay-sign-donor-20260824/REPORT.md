# C3 active replay-sign donor audit

Date: 2026-08-24

## Classification

`HARD_NACK_ACTIVE_REPLAY_SIGN_DONOR`

Exact claim rejected: during the fused replay cell, reuse its live per-round
sign/tape qubit as an exact chunk-entry-carry host, then Clifford-reconstruct
the sign from the contemporaneous post-`walk_round` `u`/`v` state before the
sign is next consumed.

The approved first falsifier fired. The post-walk state has two valid ordinary
walk preimages with opposite signs. Therefore the sign is not an affine
function of the post-walk state; more strongly, it is not any deterministic
function of that state. No production/env-gated probe was built.

## Exact binding

- Base commit: `67524171baaf568dc3dc606f38515745f70804ff`
- Base tree: `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Branch: `research/codex-replay-sign-donor-20260824`
- Worktree: `ecdsafail-replay-sign-donor-codex`
- Design commit/tree: `a9a9752a532adf4d643dc2ac0d27830999d102a5` /
  `b9b8a5f0d585ccf04d43c1eb2942b84cdc1976f6`
- Plan commit/tree: `af76f0409fbc3c49081abf27f6eeaa50be0db552` /
  `36f59cf0b5d3c25840e7881227f98aa3f477c33a`
- Collision-evidence commit/tree:
  `4120dc973c4116e8e3ae5f3533c90b0818e512ad` /
  `1d9acfe07fd2198432ab904b24ca04d1849e8e5c`
- Liveness-evidence commit/tree:
  `74962c615fc42bdffbb79c1d2dc8dc53159a0cc3` /
  `049955340da32a9a6a386f71ae98500d69721107`
- Rust: `rustc 1.93.0 (254b59607 2026-01-19)`
- Cargo: `cargo 1.93.0 (083ac5135 2025-12-15)`
- Network/provider/submission actions: none

Source SHA-256:

| Artifact | SHA-256 |
|---|---|
| `Cargo.lock` | `42ff16919e551891ad1b21821329b116d133194245a0e0734a33573dfe598e07` |
| `src/point_add/mod.rs` | `596ed58d4d61fbb087ccf236c728efc09631632a96693d849a71c03bea866a06` |
| `src/point_add/pingpong_div.rs` | `953dd851629e4d15a4f56d5061e3c0d61ea83bebab8f7aca5243636d4f240c38` |
| `src/point_add/pp_profile.rs` | `3eeab2801b88b16b1e9334febf9ae1d3e32a8de64e62ca852625e4ae913bb538` |
| release `build_circuit` | `a587c4b22862e3927868ba9bb9d79b3f98070999c52eb8f42286eb14e39896e4` |
| release `eval_circuit` | `c20f76131fd0de5833254d27805351d71002e4921e0e47438e214930e86c18c6` |
| plain default `ops.bin` | `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e` |

## Functional counterexample

### Exact source transform

For every ordinary round after the special fused rounds 0 and 1,
`walk_round` allocates a sign and computes

```text
s = target_pre[1] XOR source[1].
```

`signed_add_wrapping` and its split form implement the same complement
sandwich on a `w`-bit target:

```text
F_s(T,S) = (((T XOR s*(2^w-1)) + S) mod 2^w)
            XOR s*(2^w-1))
         = T + S mod 2^w, if s=0
         = T - S mod 2^w, if s=1.
```

Both operands are odd, so `F_s` is even. The following swap ladder and final
top CNOT are the source's arithmetic-halving wire permutation. For the small
positive witness below there is no wrap or sign-edge ambiguity, so the live
post-walk target is exactly `F_s/2`.

### Actual-width witness

`VALUE_WIDTH = N + 3 = 259`. Set the unchanged source register to `S=1`:

| width | source | target before walk | required sign | signed sum | target after walk |
|---:|---:|---:|---:|---:|---:|
| 259 | 1 | 1 | 0 | `1+1=2` | 1 |
| 259 | 1 | 3 | 1 | `3-1=2` | 1 |

Both pre-states satisfy the exact ordinary-round preconditions: source and
target are odd, and `s = target_pre[1] XOR source[1]`. Their entire live
post-walk `(source,target)` pair is the same `(1,1)`, while the retained tape
sign differs.

The later inverse relation does not repair this dependency. `walk_back_round`
first undoes the final top CNOT and swap ladder, then runs the inverse signed
add. Only after those operations does it apply `target[1] XOR source[1]` into
the sign and free it. Using that relation before the inverse walk is precisely
what the collision disproves.

### Exhaustive corroboration

`check_sign_collision.py` bit-models the exact complement sandwich and exact
halving wire permutation. It exhaustively enumerated all odd source/target
pairs at widths 4 through 10:

| width | input pairs | distinct `(source,target_post)` keys | preimages per key |
|---:|---:|---:|---:|
| 4 | 64 | 32 | 2, signs `{0,1}` |
| 5 | 256 | 128 | 2, signs `{0,1}` |
| 6 | 1,024 | 512 | 2, signs `{0,1}` |
| 7 | 4,096 | 2,048 | 2, signs `{0,1}` |
| 8 | 16,384 | 8,192 | 2, signs `{0,1}` |
| 9 | 65,536 | 32,768 | 2, signs `{0,1}` |
| 10 | 262,144 | 131,072 | 2, signs `{0,1}` |
| **total** | **349,504** | **174,752** | **2, signs `{0,1}`** |

This independently reproduces the checked-in theorem in
`src/point_add/memory/WAYFINDER.md`: the two inverse candidates are
`2*target_post-source` for sign zero and `2*target_post+source` for sign one,
and their low bits satisfy the respective sign predicates.

## Actual promoted schedule and liveness

### Default resolution

An inner-only reading of `plan()` gives fallback values 341/628/1273. Those
are not the promoted defaults. `src/point_add/mod.rs` sets the actual defaults
before constructing the ping-pong circuit:

```text
SUB4_PP_ROUNDS=696
SUB4_PP_ROUNDS_MUL=694
SUB4_PP_R1=335
SUB4_PP_R1_MUL=315
SUB4_PP_R2=645
SUB4_PP_PEAK=1267
```

This is the only reconciliation mismatch found: the run matches the build-level
defaults exactly, while the inner fallback values are shadowed.

### 64-lane actual profile

The exact source, built offline, reported:

```text
PP_PROFILE peak_qubits=1267 peak_ops_idx=913421
           peak_phase=pp_div_replay num_qubits=1267 ops=12593762
TOTAL      ops=12593762 ccx=955130 ccz=40 exec_tof=911220.66
PP_PROFILE lanes=64 classical_mismatch=0 phase=0x0 dirty_qubits=0
```

The simulator accumulates an integer gate count over 64 lanes. The displayed
two-decimal `911220.66` therefore uniquely identifies
`58,318,122 / 64 = 911,220.65625` executed Toffoli. Baseline economics are:

```text
Q = 1,267
T = 911,220.65625
Q*T = 1,154,516,571.46875
correctness = 0 classical mismatches / zero phase / 0 dirty qubits
```

The plain default builder emitted 12,593,858 post-nonce operations and the same
`ops.bin` SHA-256 recorded above. The profiler reports the 12,593,762 operations
before the 96-op tail nonce. The allocation trace recorded 1,665 distinct
Q1267 allocation op indices: 993 in `pp_div_replay` and 672 in
`pp_mul_walkback`.

### Divide global peak: op 913421

Narrow census window `[913165,913677]`, phase `pp_div_replay`:

| Count | Owner allocation site | Role |
|---:|---|---|
| 333 | `pingpong_div.rs:1668` | ordinary retained tape signs |
| 1 | `pingpong_div.rs:852` | fused round-0 tape sign |
| 1 | `pingpong_div.rs:925` | fused round-1 tape sign |
| 256 | `pingpong_div.rs:2896` | live public/output register |
| 256 | `pingpong_div.rs:373` | live coefficient register |
| 146 | `pingpong_div.rs:2895` | first live walk register |
| 146 | `arith/adder.rs:341` | second live walk register loaded from `p` |
| 126 | `pingpong_div.rs:1992` | current chunk's owned carry ladder |
| 2 | `pingpong_div.rs:2135` | live chunk boundaries |
| **1,267** | | **complete owner sum** |

Thus all 335 tape signs, including the selected active sign family, are live at
the first global peak. The peak allocation itself occurs at op 913421.

### Multiply global peak: op 8322690

The phase profile independently reaches Q1267 in `pp_mul_walkback`. A second
narrow census window `[8322434,8322946]` avoids transferring the divide census
by assumption:

| Count | Owner allocation site | Role |
|---:|---|---|
| 636 | `pingpong_div.rs:1865` | ordinary retained tape signs |
| 1 | `pingpong_div.rs:852` | fused round-0 tape sign |
| 1 | `pingpong_div.rs:925` | fused round-1 tape sign |
| 256 | `pingpong_div.rs:2896` | live public/output register |
| 256 | `pingpong_div.rs:421` | live coefficient register |
| 58 | `pingpong_div.rs:1992` | current chunk's owned carry ladder |
| 20 + 20 | `pingpong_div.rs:1636,1637` | regrown interleaved walk wires |
| 14 | `reacquire:0` | restored terminal passengers |
| 2 | `pingpong_div.rs:2135` | live chunk boundaries |
| 1 | `pingpong_div.rs:2638` | multiply cell `doubled_out` |
| 1 + 1 | `pingpong_div.rs:2895`, `arith/adder.rs:341` | surviving walk endpoints |
| **1,267** | | **complete owner sum** |

Thus 638 tape signs are live at this second global binder as well.

### Exact idle interval and next dependency

In the signed halving cell, sign complements the replay target at source lines
2495-2497, is idle while `add_chunked_measured` runs at line 2498, complements
the target back at 2499-2501, and is read again by `signed_parity_repair` at
2537.

In the fused doubling cell, sign complements the target at 2644-2646, is idle
during the chunked add at 2647-2653, is read again starting at 2658 and 2664,
and finally restores the target frame at 2737-2739.

The lifetime shape was therefore real: the sign wire is already allocated at
both global peaks and has an add-sized idle interval. The blocker is its value,
not its lifetime. Overwriting it with a boundary carry destroys one bit of
branch information that the live post-walk state provably does not contain.

## Economics and decision

No candidate stream was generated because the first approved functional
falsifier fired. Candidate Q/T deltas are therefore **not applicable**, not
`-1 Q` and not a projected win. Reusing the sign wire would require at least
one of:

1. retain an equivalent branch bit elsewhere, which does not remove the live
   information and therefore cannot deliver the claimed one-wire lift by this
   schedule; or
2. undo/replay enough of the walk to recreate the pre-walk low-bit predicate,
   which is the prefix/inverse dependency the claim forbids.

The exact active-sign donor claim is therefore terminally rejected:

```text
reason=opposite_sign_preimages_have_identical_post_walk_state
candidate_q_delta=NA
candidate_t_delta=NA
production_probe=not_built_by_approved_stop_rule
```

This does not claim that every imaginable output-hosting scheme is impossible.
It rejects exactly the selected active replay-sign family restored from the
post-walk `u`/`v` state without prefix replay. No second donor family, width-2
Boolean synthesis, or checkpoint schedule was attempted in this lane.

## Reproduction

All commands ran from the isolated worktree root.

```bash
git rev-parse 67524171baaf568dc3dc606f38515745f70804ff
git rev-parse 67524171baaf568dc3dc606f38515745f70804ff^{tree}
rustc --version
cargo --version
shasum -a 256 Cargo.lock src/point_add/mod.rs src/point_add/pingpong_div.rs src/point_add/pp_profile.rs

python3 artifacts/replay-sign-donor-20260824/check_sign_collision.py \
  2>&1 | tee artifacts/replay-sign-donor-20260824/sign-collision.log

cargo build --release --offline --bin build_circuit --bin eval_circuit

env PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1 TRACE_PHASE_ACTIVE=1 \
  TRACE_PHASE_ACTIVE_TOP=12 TRACE_EACH_PEAK=1 \
  ./target/release/build_circuit \
  2>&1 | tee artifacts/replay-sign-donor-20260824/pp-profile.log

profile_peak_idx=$(sed -n \
  's/.*PP_PROFILE peak_qubits=[0-9]* peak_ops_idx=\([0-9]*\).*/\1/p' \
  artifacts/replay-sign-donor-20260824/pp-profile.log | head -n 1)
profile_win_lo=$((profile_peak_idx - 256))
profile_win_hi=$((profile_peak_idx + 256))
env B0_WIN_LO="$profile_win_lo" B0_WIN_HI="$profile_win_hi" \
  B0_PHASE=pp_div_replay TRACE_OP_SITES=1 TRACE_ALLOC_NEAR_PEAK=1267 \
  ./target/release/build_circuit \
  2>&1 | tee artifacts/replay-sign-donor-20260824/b0-replay-peak.log

mul_peak_idx=8322690
mul_win_lo=$((mul_peak_idx - 256))
mul_win_hi=$((mul_peak_idx + 256))
env B0_WIN_LO="$mul_win_lo" B0_WIN_HI="$mul_win_hi" \
  B0_PHASE=pp_mul_walkback TRACE_OP_SITES=1 \
  ./target/release/build_circuit \
  2>&1 | tee artifacts/replay-sign-donor-20260824/b0-mul-peak.log

./target/release/build_circuit \
  2>&1 | tee artifacts/replay-sign-donor-20260824/default-build.log
shasum -a 256 target/release/build_circuit target/release/eval_circuit ops.bin
```

Evidence artifact SHA-256 before the final report commit:

| Artifact | SHA-256 |
|---|---|
| `DESIGN.md` | `677ca8ef65db8cff5b7ea5a15e007faa99696279ba619f1c478439fe1d573219` |
| implementation plan | `d811d01a246af12fa59c0765e19735baf5466b723e78bf761997ac1455665876` |
| `check_sign_collision.py` | `78ba5f139758a568a6e45ed3f83aabf5f4b027424ede8044681d6bdbdeed312a` |
| `sign-collision.log` | `e18eee2edfbc1baf1025a0b2265a7c93a65af659fc069e265383b308683981f7` |
| `binding.log` | `108e7a12ea63fce1e3e5f319819d39f59533c07777685e18a7d960be52d018f9` |
| `pp-profile.log` | `019d2f8a8443f5446f868c7f5d03495d13fa2ef4b76f359b86dacc881d96a72b` |
| `b0-replay-peak.log` | `16f0d3102e702942d92b498c9171fd534cd982121be7f35ff46ead110cf5745f` |
| `b0-mul-peak.log` | `0ef0c1e8912e0b0181676a3a4d70a9b6154c1c8f5d74db31e99022839ff4ba4a` |
| `source-sites.log` | `d71ae9d55b81acb156cc4aaa757f563738482a1ed0fb91d2ba435b730b6f6cbf` |
| `default-build.log` | `72ea7c2252d89f6073393fea0cff5c2b3b5ac418ea4921ad912c6383c831f666` |
