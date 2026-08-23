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
