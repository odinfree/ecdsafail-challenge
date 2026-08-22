# Experiment ledger

## X000 — exact ancestor reproduction

- Status: complete
- Ancestor: `897dda2b0cf267151ecd973252d2a5078cbf1b63`
- Hypothesis: the initial Q=1321 peak contains at least one replay/walk allocation with a removable lifetime interval, and more than one phase may co-bind.
- Change: none.
- Forced-build receipt: local release build from the exact ancestor; no source/config override.
- Measured Q: 1321.
- Measured average T: 952707.477; scorer T=952707.
- Score: 1258525947.
- Emitted operations: 13,586,833.
- Artifact hash: `8d135db0aa0123fd143fc78ee1dbbe5fe6b851af9003352fde0f2fcc90458b34`.
- Peak owners: unresolved. `TRACE_PEAK=1` emitted nothing because the trace summary is wired to the legacy builder, while the active route returns directly from `build_pingpong_point_add()`.
- Correctness: full 9024-shot trusted evaluation; classical/phase/ancilla = 0/0/0.
- Verdict: baseline reproduced exactly; continue with observation-only instrumentation.
- Evidence: `score.json`; trusted evaluator output at 2026-08-22T10:37:19Z.
- Next action: X001 adds a ping-pong-local peak summary without changing emitted operations.

## X001 — active ping-pong peak-owner instrumentation

- Status: complete.
- Ancestor/source identity: X000 baseline plus observation-only diagnostics.
- Hypothesis: the Q=1321 peak is formed by identifiable replay/walk allocations whose phase and caller can be isolated without changing the op stream.
- Smallest source/config change: expose the existing builder peak/near-peak telemetry from `build_pingpong_point_add()` and add finer phase labels only where the first trace is ambiguous.
- Expected invariant movement: emitted operations and artifact hash remain identical to X000; peak-owner evidence becomes explicit.
- Q/T/score: identical to X000 by byte-identical op stream.
- Emitted operations and artifact hash: 13,586,833; `8d135db0aa0123fd143fc78ee1dbbe5fe6b851af9003352fde0f2fcc90458b34`, exactly X000.
- Cheap correctness result: byte-identical artifact; inherits X000's full trusted result.
- Full correctness result: X000 is the same op stream; rerun if instrumentation changes it unexpectedly.
- Peak-owner movement: observation only. Q=1321 binds at `tlm_inverse` op 1,319,752 and `tlm_forward_multiply` op 12,260,628. In both phases the binding batch is an 88-qubit carry/borrow allocation in `borrowed_const_fold_carries` (`const_arith.rs:417`), entered at active=1233. Each phase invokes it twice, sequentially.
- Verdict: continue. This is a coordinated two-phase endpoint-negation target, not a global replay-width mystery.
- Evidence: two traced builds with `TRACE_PEAK=1`, then `TRACE_ALLOC_BATCH_NEAR_PEAK=1321`; both preserved the X000 artifact hash.
- Exact next action: X002 loans reconstructible terminal passengers across both endpoint negations and replay.

## X002 — terminal passenger loan across replay

- Status: retained saddle; not shippable.
- Ancestor/source identity: X000 plus X001 diagnostics.
- Hypothesis: for a converged walk, both terminal registers are signed `+1/-1`; all non-sign wires are reconstructible from the sign plus constant bit zero and are idle until walk-back.
- Smallest source/config change: clear and free those passenger wires after the walk, then reacquire the exact wires in reverse order and restore them before walk-back. An opt-out env switch preserves the X000 route for A/B testing.
- Expected invariant movement: both Q=1321 endpoint-negation peaks fall together; no compare/fold/depth or nonce parameter changes.
- Q/T/score: Q=1307; trusted evaluator stopped before metrics because the unchanged nonce was dirty.
- Emitted operations and artifact hash: 13,586,917; `81074c476ebc482be278cee9db644fdd7285eed38b84f2c881f09a0e372842ae`.
- Cheap correctness result: 64-lane full-affine selfcheck passed; reported Q=1307.
- Full correctness result: failed at unchanged nonce 82 with classical/phase/ancilla = 4/1/0.
- Peak-owner movement: both endpoint peaks moved 1321 -> 1307. The divide replay plateau reaches 1305; multiply replay reaches 1306. Initial terminal width is eight bits per register, so fourteen non-sign wires were loaned, not the sixteen predicted from later 700-round descendants.
- Verdict: retain as an intermediate lifetime cut because the named invariant moved in both phases, but do not hunt or ship. Its convergence-conditioned reset requires requalification only after the architecture clears the research target.
- Evidence: full traced build and trusted 9024-shot failure receipt at 2026-08-22T10:55Z.
- Exact next action: X003 removes the endpoint carry lane with a dirty-ancilla implementation that preserves the tape.

## X003 — `starkWINTER`: vented endpoint subtraction over dirty tape

- Status: retained architectural cut; not yet shippable.
- Ancestor/source identity: X002 plus an endpoint-local arithmetic route; legacy clean-carry behavior remains available with `SUB4_PP_LEGACY_ENDPOINT_CARRIES=1`.
- Hypothesis: each 89-bit truncated endpoint subtract can preserve its 87 dirty tape ancillas and control/phase while recycling two clean qubits, replacing an 88-clean-qubit ladder.
- Smallest source/config change: pass the live tape into `conditional_mod_negate` and call the ancestor's `cisub_dirty_2clean_classical` over the same 89-bit low slice and same `f-1` constant.
- Expected invariant movement: endpoint peak falls below the 1305/1306 replay plateau without changing `ROUNDS`, `ENDPOINT_FOLD_WINDOW`, replay/fold compares, or nonce.
- Q/T/score: Q=1306; no trusted T/score because the unchanged nonce was not clean. The 64-lane affine diagnostic reported 954138.969 executed T.
- Emitted operations and artifact hash: 13,590,929; `fea4bbfdbc685dee6b56d883095b65a0de940233dbbb222777ccd61f96a59879`.
- Cheap correctness result: production release build passed; 64-lane full-affine selfcheck passed with no structural mismatch. The ancestor's broader Rust test target is pre-existing red with 165 unrelated compile errors, so it is not a usable gate.
- Full correctness result: unchanged nonce 82 produced classical/phase/ancilla = 1/0/0.
- Peak-owner movement: the 88-clean-carry endpoint architecture is gone from the ceiling in both directions. Global Q moved 1307 -> 1306 and the binder migrated to multiply replay; divide replay is 1305.
- Verdict: retain and name `starkWINTER`. It is an architectural workspace substitution, not a width knob: live read-only tape carries the dirty workspace and is preserved through phase repair. Compose before requalification.
- Evidence: traced production build, byte fingerprint, affine selfcheck, and full trusted dirty receipt at 2026-08-22T11:01Z.
- Exact next action: X004 (`clankerFARM`) re-chunks the now-exposed replay plateau to cross Q=1270.

## X004 — `clankerFARM`: split replay, square, and virtual fused-fold carry farms

- Status: retained low-Q architecture; not shippable and not a score candidate.
- Ancestor/source identity: X003 `starkWINTER` route plus three coordinated carry-lifetime cuts. The source remains on the isolated `research/redescent-teddy-1270` branch.
- Hypothesis: wide clean-carry ladders can be replaced by independent measured carry plots, while a fused correction operand can be generated one bit at a time instead of materialising a 56-bit register.
- Smallest source/config changes:
  - replay width 96 -> 48, yielding six balanced 42/43-bit plots; `SUB4_PP_LEGACY_REPLAY_CHUNKS=1` preserves the ancestor layout;
  - product-square adds of at least 200 bits use the same plotter; `SUB4_CLANKER_FARM_SQUARE_MIN` preserves an A/B path;
  - the selected `{-f,0,+f,+2f}` correction is generated virtually and split across three plots. Each measured boundary is repaired with the exact incoming-carry comparator. `SUB4_PP_FOLD_CHUNKS` and `SUB4_PP_LEGACY_FUSED_FOLD` preserve ablations.
- Phase-repair finding: the first four-plot version reconstructed only `post_sum < operand` and failed the affine phase gate. The exact relation is `(post_sum < operand) OR (post_sum == operand AND carry_in)`. Reusing `cmp_lt_phase_conditioned_with_cin` with its multiplicative control pinned high closed that hole. Three fold plots then gave the same global Q as four with lower T.
- Measured Q/T: Q=1266. The 64-lane affine diagnostic measured 1,036,334.453 executed T, 1,174,483 emitted Toffoli, and a clean classical/phase/ancilla result. This crosses the Q target by four qubits but misses the Q=1270 T target by about 105,859.
- Production artifact: 15,730,117 operations; SHA-256 `843558da6f504e3f8f2f41cae1edeccdf0cfed9e0dc216f8e880ebc1752e7b75`.
- Full correctness result: unchanged nonce 82 failed the trusted 9024-shot gate with classical/phase/ancilla = 1/1/0. No nonce search was started because the T economics fail the research-to-hunt gate.
- Peak-owner movement: the original 88-clean endpoint ladders, 85/86-live replay ladders, and 257-bit square ladder are all below the ceiling. The new binder is the replay plot allocation at `pingpong_div.rs:737`: active=1225 plus 41 carries in multiply (Q=1266); divide reaches Q=1265.
- Low-Q existence witness: an earlier four-pass dirty-tape correction reached Q=1266 and passed the affine gate, but measured 1,824,616.875 executed T. It is retained only behind `SUB4_PP_VENTED_FUSED_FOLD=1` as proof that operand materialisation is not required.
- Useful A/B surface (all 64-lane affine clean):
  - replay width 48, fold plots 4: Q=1266 / T=1,039,807.969;
  - replay width 48, fold plots 3: Q=1266 / T=1,036,334.453 (retained default);
  - replay width 48, fold plots 2: Q=1280 / T=1,028,231.906;
  - replay width 52: Q=1274 / T=1,021,178.375;
  - replay width 64: Q=1286 / T=1,002,629.375;
  - legacy replay width 96: Q=1306 / T=984,406.859;
  - legacy fused fold: Q=1282 / T=1,010,564.656;
  - unchunked product square: Q=1287 / T=1,038,597.625.
- Verdict: continue from the retained architecture, but do not tune nonce or compare windows. The measured saddle says restoring wider replay alone cannot reach the target; the next cut must also remove at least about 22k T below Teddy's 952,707 baseline.
- Evidence: default production build and hash, exact peak trace, clean 64-lane affine gate, trusted 9024-shot dirty receipt, and the A/B matrix above.
- Exact next action: design one boundary-erasure or replay-cell fusion that reduces T while holding Q<=1270; alternatively find at least sixteen more dead live wires so four replay plots become possible, then pair that with an independent >=22k T cut.

## Experiment template

- Status:
- Ancestor/source identity:
- Hypothesis:
- Smallest source/config change:
- Expected invariant movement:
- Q/T/score:
- Emitted operations and artifact hash:
- Cheap correctness result:
- Full correctness result:
- Peak-owner movement:
- Verdict: continue / repair / kill / defer.
- Evidence:
- Exact next action:
