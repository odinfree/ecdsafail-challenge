# Experiments — tape/decoder lane (bdf4845), 2026-08-23

## E1 — Baseline byte-reproduction (full 9024, independent rebuild)
- `./benchmark.sh` in this worktree at bdf4845, clean tree.
- Result: qubits **1278**, avg executed Toffoli **915,947.392**, score **1,170,580,266**;
  9024/9024 shots OK, 0 classical / 0 phase-garbage / 0 ancilla-garbage.
- Emitted ops 12,912,890; forced-rebuild `ops.bin` SHA256
  `5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8` (50,893,170 B).
- Matches promoted submission 792ac70 (live leader) exactly.

## E2 — Live-set composition at the binding instant
- `B0_WIN_LO=2630000 B0_WIN_HI=2642000 build_circuit`:
  best_active=1278 at ops 2,636,142, phase `pp_div_replay` (r1=356 batch replay).
- Owners: 355+1+1 tape signs (`pingpong_div.rs:1094`, `:548`), 256 coefficient (`:263`),
  256 + 139 point registers (`:1991/:1992`), 139 denominator wires (`arith/adder.rs:341`),
  130 chunk-ladder carries (`:782`), 1 misc. Sum = 1278.
- Reading: tape(357) + 2N coefficient/numerator(512) + walk regs at width 139(278) +
  ladder(130) + 1 = 1278, exactly the `allowance()` accounting.

## E3 — Full-stream Q1278 plateau census
- `TRACE_ALLOC_NEAR_PEAK=1278 build_circuit`, aggregate ALLOC_NEAR by phase/caller:
  - `pp_div_replay`   239 touches, ops 2,636,142..4,019,279
  - `pp_mul_walkback` 245 touches, ops 8,594,249..10,269,578
  - `square_product_register` 4 touches, ops 6,762,459..6,790,511
- Reading: the peak is a three-family plateau; all three are allowance-spenders sized
  against SUB4_PP_PEAK=1278. Lowering Q requires simultaneous shed in all three.

## E4 — Falsifier: sign recomputable from post-state? (algebraic, exact)
- Claim tested: walk-back could re-derive sign[r] from the post-round state, making
  the tape removable.
- Round r: u,v odd; sign = u[1]⊕v[1] selects t ± s so the result ≡ 2 (mod 4);
  v′ = result>>1 (odd, invariant preserved). Pre-image candidates from (u, v′):
  v ∈ {2v′+u, 2v′−u}; 2v′ even and u odd ⇒ BOTH odd ⇒ both parity-valid ⇒ the branch
  bit is one full bit of quantum data per round. Entropy check: terminal state (±1,±1)
  holds ~2 bits, so ~254 bits of the 256-bit denominator must reside in the 698-bit
  tape when replay completes. **Killed — tape residency is information-forced.**
- Measurement escapes: computational-basis measure of data-dependent signs collapses
  live-shot batches (caught by the phase-garbage gate); X-basis erasure destroys the
  control value walk-back requires. Both closed.

## E5 — Dirty-ladder pricing (arithmetic, no build)
- Idle already-replayed signs at each binder ≥ ladder width (130/66). Replacing clean
  ladder wires with dirty sign wires: ≥1 extra Toffoli per carry per replay add
  (loses measured uncompute), ×~700 adds ×2 traversals ≈ 1,400–2,800 T per qubit freed.
- Break-even is 716.7 T/qubit ⇒ net-negative ≈2–4×. Killed.

## E6 — A2 falsifier: exact symbolic segment-matrix sweep (`.lane/a2_falsifier.py`)
- Replay semantics from source: halving round r≥2 is target ← (target ± source)/2 mod p
  (`signed_mod_add_pm_halve_fused`); doubling is target ← 2·target ± source
  (`signed_mod_double_add_pm_fused` doc, :1744). Per-round 2×2 matrices over Z[1/2].
- Sweep: ALL 2^k sign patterns, k = 1..14, both directions, both start parities,
  exact Fraction arithmetic (49,140 matrix products per direction/parity). Results:
  - **Injective everywhere**: |{M_seg}| = 2^k in all 56 cells ⇒ any register from which
    the segment action is applicable holds ≥ k qubits. Numerators < 2^(k+1) < p for
    k ≤ 254 ⇒ injectivity survives reduction mod p.
  - **Entry width exactly b(k) = k+1 signed bits** in every cell (halving: entries stay
    in [−1,1] with denominators | 2^k, proved by induction, bound tight; doubling:
    |entry| ≤ 3^k proved, observed 2^k). Materialized matrix ≥ 3(k+1) qubits
    (4 entries, det = ±2^∓k constraint).
- Script asserts injectivity + proved bounds; exits clean.

## E7 — A2/A6 pricing (arithmetic on exact circuit shape + repo-measured costs)
- Zero tape release: `walk_back_round` (:1109–1134) uncomputes tape[r] against round
  r's boundary state (cx target[1]/source[1] after the reverse add) — signs cannot be
  freed at replay time under ANY replay representation. Released bits at r1 binder
  (op 2,636,142) and terminal binder = 0.
- Per-round replay cost bound by circuit shape: one chunked measured adder pass +
  O(fold_window) fold + O(flag_compare) compare ⇒ A_round ∈ [255, ~900] executed T,
  strictly < 8 adder passes.
- Materialized aggregate, segment k: build/unbuild matrix ≈ 2k² T; application
  4 quantum×quantum multiplies ((k+1)×256-bit, schoolbook = (k+1) controlled adds
  each) + inverse-application erasure of the stale pair (measured erasure barred by
  phase-garbage gate) = 8(k+1) adds ≥ 2040(k+1) T vs baseline k·A_round < 900k.
  ΔT > +1140k T for all k. ΔQ ≥ +3(k+1) (released 0). Streamed variant: touches each
  sign once ⇒ circuit-identical to incumbent replay, gain = 0.
- Score: floor case (k-qubit representation, free application — unattainable)
  Δ ≥ +k·915,947; realistic k=2 Δ ≥ +14M (+1.2%). **A2 closed by lower bound.**
- A6 (tape-free escape): repo square ≈ 54k executed T (5.9% of 915,947, WAYFINDER);
  Fermat ladder ≥ ~270 mult/sq ⇒ ≥ 14.6M T, score ≥ 13B at Q=900 (11× target).
  Hybrid stop-early margin: save ≈ 7.3k T-equiv/bit (2.7 tape qubits + ~4 adds/round
  × 2.7 rounds), pay ~2 mults ≈ 108k T/bit ⇒ ≥14× dead everywhere. **A6 closed.**
