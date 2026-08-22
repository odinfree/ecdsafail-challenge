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
- Measured Q/T: Q=1266. The 64-lane affine diagnostic measured 1,036,334.453 executed T, 1,174,483 emitted Toffoli, and a clean classical/phase/ancilla result. This crosses the Q target by four qubits but exceeds the refreshed live ceiling at Q=1266 by about 104,119 T.
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

## X005.1 — exact dirty-tape replay add

- Status: killed as dominated; observation retained, source probe reverted.
- Ancestor/source identity: exact X004 `clankerFARM` plus one env-gated local probe, `SUB4_PP_DIRTY_TAPE_REPLAY_ADD=1`.
- Hypothesis: extend each 256-bit replay target by its carry-out wire and use the live walk tape as the 255 dirty lanes for `iadd_dirty_2clean_qoffset`, replacing all clean replay carry plots and their retained boundary repairs with one exact full-width add.
- Smallest source/config change: route the three replay-add call sites through the existing two-clean dirty-offset primitive; allocate one high zero wire and two clean wires, preserve the tape, source, target, and carry-out exactly.
- Expected invariant movement: remove the ordinary replay boundary family and 41/42-wire clean ladder; either lower Q or expose the next binder without phase approximation.
- Q/T/score: Q=1266; deterministic 64-lane affine T=1,659,525.266, so no score exists and no trusted full run is justified.
- Emitted operations: 17,829,001 in the selfcheck build; emitted Toffoli=1,706,599.
- Cheap correctness result: deterministic 64-lane full affine add passed classical outputs, phase, and ancilla cleanup.
- Full correctness result: not run; the T gate fails by a wide margin.
- Peak-owner movement: the replay ladder was removed, but the global binder migrated without moving Q. The new forward-multiply peak contains 703 tape wires, 256 caller-y wires, 256 coefficient wires, a 19-wire fused operand, a 19-wire comparator ladder, three selector wires, and ten singletons. The exact peak is fused-fold boundary repair, not replay addition.
- Verdict: kill. Exact tape borrowing pays a second carry computation and raises affine T by 623,190.813 while leaving global Q flat. It proves that dirty-tape substitution alone cannot produce `storm420`.
- Evidence: `TRACE_PEAK=1` peak at op 10,726,587; B0 census over `[10726490,10726650]`; clean deterministic affine selfcheck. The env-gated probe was reverted after measurement.
- Exact next action: X005.2 must break the fused-fold reverse dependency or identify sixteen truly releasable co-resident wires; another full-width dirty replay pass is closed.

## X005.2 — staged tape retirement and non-uniform replay

- Status: structural lever demonstrated, then deferred; two deeper compositions killed.
- Ancestor/source identity: X004 plus an env-gated multiply-only schedule. Replay a tail suffix while the terminal passengers remain loaned, restore the terminal shell, reverse-walk that suffix to free its signs, then replay the remaining prefix at a wider chunk width.
- Hypothesis: replay and reverse walk consume signs in the same reverse order, so staging a completed suffix can expose at least sixteen replay-co-resident wires without weakening the fixed-round arithmetic.
- Smallest source/config change: split reverse multiply replay at a bounded round count; preserve the divide traversal and all trusted ABI behavior. A temporary prefix chunk override prices the released width directly.
- Expected invariant movement: keep the early 48-bit replay peak at or below Q1266, then spend retired tape signs on a wider, lower-T remaining replay.
- Q/T/score: 144 retired rounds plus a 64-bit prefix produced Q1270 / deterministic affine T1,021,814.734. It passes the lifetime invariant but misses the fresh live T ceiling by 94,452.
- Emitted operations: 15,379,600; emitted Toffoli=1,145,467.
- Cheap correctness result: deterministic 64-lane affine classical/phase/ancilla clean.
- Full correctness result: not run; conservative economics fail.
- Deeper compositions: 320 retired rounds plus a 96-bit prefix and exact one-ancilla walk-back gave Q1266 / T1,044,759.922, affine clean, and is dominated. Replacing that exact walk-back with measured 48-bit chunks held Q1266 but failed deterministic phase cleanup; no score was measured.
- Peak-owner movement: the 144/64 composition maps and releases enough persistent tape state to permit four replay plots at Q1270. The initial narrow suffix remains a Q1266 co-binder, so this lever cannot lower global Q by itself.
- Verdict: defer the staged lifetime lever for explicit composition with a genuine tape-removal or independent T architecture. Kill the exact-low-Q and measured-chunked walk variants.
- Evidence: traced 64-lane selfchecks and exact configs above. No nonce, full trusted run, provider, or submission work occurred.
- Exact next action: X006 removes or replaces the tape rather than polishing its allocation schedule.

## X006.0 — live-leader replay-budget falsifier

- Status: killed.
- Ancestor/source identity: clean detached `7ca0559911b8cd423c4acc74fe152f332fce0c63`, the live Q1278/T921558 leader.
- Hypothesis: the leader's existing walk/replay interleaver can directly spend a lower `SUB4_PP_PEAK=1266` allowance and remain under the exact Q1266 ceiling T930293.
- Smallest source/config change: none; one environment override on the exact live source.
- Baseline deterministic affine result: Q1278 / T921584.156, emitted T963845, clean.
- Falsifier result: `SUB4_PP_PEAK=1266` remained Q1278 and rose to T934955.656, emitted T990848, clean.
- Verdict: kill before a full run. Another phase co-binds at Q1278, so rebudgeting replay alone removes no global qubits and adds 13,371.500 deterministic affine T.
- Evidence: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/7ca-tape-1266/TAPE-PEAK1266-FALSIFIER.md`.
- Exact next action: remove persistent tape state across co-binders; do not treat `SUB4_PP_PEAK` as tape removal.

## X006.1 — exact tape recomputation falsifier

- Status: killed for the current walk; tape replacement remains open.
- Ancestor/source identity: `0d15561` re-descent source with the X004 Q1266 architecture.
- Hypothesis: erase the resident history, reconstruct it by an exact walkback/rewalk cycle, and spend T to lower Q.
- Exact result: deterministic 64-lane classical/phase/ancilla `0/0/0`, Q1266, T1431657.594 versus baseline T1036334.453: +395323.141 (+38.15%) with no global Q movement.
- Corrected lower bound: the first audit incorrectly held Q1266 fixed after granting free deletion of 703 tape cells. Honest deletion gives a raw replay-256 bound near Q772/T943810; adding a conservative 256-bit code gives Q1028 and still clears the live score by a wide margin. Only Bennett/current-walk recomputation is killed.
- Evidence: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/redescent-teddy-tape-checkpoint/.lane/TAPE-CHECKPOINT.md` and `TAPE-REPRESENTATION-AUDIT.md`.
- Exact next action: encode the history or absorb it into a deliberately tagged bijection; do not re-run full erase/rebuild.

## X006.2 — denominator-code changed-premise primitive

- Status: continue.
- Ancestor/source identity: clean live `7ca0559`, isolated branch `research/7ca-teddy-pebble`, commits `451497f`, `974b07f`, and `ce76dc6`.
- Hypothesis: a 256-bit coherent denominator code can replace tape cells and later clear exactly, approaching the 254-bit information lower bound.
- Smallest exact prototype: copy the denominator into a 256-bit code, donate `code[0]` to the round-zero tape decision, use it through walk/replay/walkback, then uncopy after exact restoration.
- Cheap correctness result: full four-register deterministic 64-lane classical/phase/ancilla `0/0/0`; emitted Toffoli unchanged at 963845. Prototype Q1533 is exactly +255 relative to the one tape cell it replaces, confirming the accounting rather than a score win.
- Exact prefix census: for k=2,4,8, the denominator low k+1 bits map bijectively to the first k decisions plus the original bit-1 tag; every k-bit prefix has exactly two preimages on the complete domains 8/32/512. The k4 outputs are all affine, so its exact decoder is 3 SWAP + 3 CNOT + 3 X, zero scratch and zero Toffoli. The real k4 circuit passes deterministic `0/0/0`, Q1530, with unchanged emitted Toffoli. The k8 map is bijective but becomes nonlinear at decision 4; synthesis cost is open.
- Corrected optimistic envelope: full-ladder tape deletion plus a 256-bit code is Q1028/T894781.72 before codec cost, rounded ideal score 919835896. It leaves roughly 250890 executed T of live headroom. A Q819 plot-48 envelope leaves 317 decoder qubits and about 401701 executed T.
- Local algebraic wall: naive untagged online coefficient absorption is two-to-one locally; both value and coefficient transitions retain two valid predecessors. A tagged/redundant code or global decoder is required.
- Evidence: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/7ca-teddy-pebble/.lane/TAPE-PEBBLE.md`.
- K8 synthesis: triangular ANF implementation has maximum control degree7, uses at most three scratch qubits, and costs612 emitted Toffoli one way. The strict full four-register prefix8 circuit passes at Q1526 with emitted966293, exactly+2448 emitted T for four codec applications. An exhaustive 4+4 reuse schedule is exact over all512 low-word states; streaming it around all three consumers costs7344 emitted T.
- Binder law: `Q_pingpong(k)=1278+256-k=1534-k`. Prefix8 therefore remains Q1526, and no codec of this family lowers the current ping-pong binder until it covers at least257 decisions; the square independently remains Q1278.
- Exact next action: HOLD. Reopen only with an exact >256-decision family or a schedule that prevents the 256-bit code from co-residing at the r1 binder.

## X006.3 — terminal-tail shared-sign codec

- Status: CLOSED HOLD; no active scan and no candidate.
- Ancestor/source identity: clean live `7ca0559`, isolated branch `research/7ca-tail-tape-teddy`.
- Hypothesis: after the walk reaches the +/-1 terminal orbit, all later signs equal `u_sign XOR v_sign`; one shared sign can replace the remaining tail cells while all coefficient-replay rounds remain intact.
- Cutoff 697: emitted ops12993972, `ops.bin` MD5 `4e8b9dfd4c11560105231d587cd9973c`, Q1278, T921214.956. Rounded score would be1177312770, a strict 438354 beat. The inherited nonce is not a candidate: full9024 classical/phase/ancilla `4/4/0`.
- Cutoff 696: emitted ops12993612, `ops.bin` MD5 `d4694ed975208bd58675e4728b2d1b78`, Q1278, T921206.867, but full9024 is dirtier at `10/3/0`; defer behind cutoff697.
- Peak-owner movement: the first saved tail cell pays for the shared sign and a separate Q1278 binder remains. The current win is same-Q T reduction; deeper cutoffs must move that binder before claiming qubit reduction.
- Verdict: HOLD cutoff697. Exact non-overlapping ranges B-E covered394240 nonces. Two classical-clean predictions were found: nonce4300192188 ranked K4/events4 and trusted at Q1278/T921214.444 with `0/2/0`; nonce4300390193 ranked K1/events1 and was rejected before staging. No K0/events0 candidate exists in the bounded coverage. No submission, provider expansion, or further grind.
- Filter correction: literal +/-1 convergence was too strong. The circuit only requires the cutoff state to shrink cleanly to signed eight-bit values; it then uses `u_sign XOR v_sign` for the omitted tail. The corrected value model reproduces the inherited four classical failures at exactly shots780,802,4467,7691 and reproduces the patched op stream byte-for-byte.
- Exact next action: reopen only after structural lanes, for a frozen-stream K0/events0/unknown0 row that passes trusted `0/0/0` and still strictly beats a freshly reopened board.

## X006.4 — exact global-codec reachability audit

- Status: local tagged blocks and full-walk decoding killed; reachable-set rank decoding remains theoretical.
- Evidence source: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/redescent-teddy-global-codec/.lane/GLOBAL-SIGN-CODEC-AUDIT.md` and its 20k exact-model census.
- Measured distribution: 19998/20000 sampled walks reached the terminal orbit; two hit width faults. Convergence p50=621 and p99=674; mean constant suffix=82.563 rounds. Sixteen-round suffix entropy falls from 6.589 bits at start624 to1.022 bits at start688, but this is distributional compression rather than an exact circuit identity.
- Exact reverse falsifier: from each +/-1 terminal pair, production-schedule blocks of k=2/4/8/16 admit4/16/256/63905 sign words. The poststate and widths therefore still require exactly k tag bits: no exact local block saving.
- Only exact sub-one-bit construction: rank the input among globally reachable predecessors. Toy-field enumeration proves the concept, but the decoder needs a global reachability oracle.
- Conservative live kill: on the Q1266 re-descent, existing exact recomputation raises T to1431657.594, so the live product forces Q<=822 and leaves only three scratch qubits beyond the Q819 code/plot envelope. A direct decoder needs at least a259-bit walk register plus extension even when the code doubles as the other operand.
- Verdict: kill local tagged-block compression as a width claim and kill current-walk global decoding. Reopen only for a rank/reachability decoder that does not materialize the walk state, or a different value/coefficient composition.

## X006.5 — Teddy sparse-square co-binder overturn

- Status: exact component HOLD.
- Ancestor/source identity: clean live `7ca0559`, isolated branch `research/7ca-teddy-square-dilated`, commit `e004e5f`.
- Hypothesis: the square's materialized 129-qubit `spread` and `xext` zero vectors are representation choices, not physical requirements.
- Smallest source/config change: env-gated sparse measured-uncompute add over structural zero positions; default stream remains byte-identical at13001937 ops, MD5 `2a3d088e0fa743bed3bd4f9cd7fd5a5e`, SHA-256 `c0e1dc5dcffe957d1aa57e7f4cece0866df6d52d9c691d5aa1614fa031efe25f`.
- Exact standalone64 result: Q1278 -> Q1148; emitted T58879 ->60693; executed T58678.203 ->59597.625; value/phase/ancilla `0/0/0`.
- Whole-circuit64 result: global Q1278, T922501.06, emitted CCX/CCZ965631/28, `0/0/0`. Replay becomes the sole binder.
- Bounded saddle: compare8 gives whole Q1278/T921574.14 and deterministic64 clean; compare7 and below fail phase and are killed.
- Verdict: HOLD for composition. The component does not score until every tape/replay binder falls below Q1148.
- Evidence: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/7ca-teddy-square-dilated/.lane/TEDDY-SQUARE-DILATED.md`.
- Reopen condition: a measured tape representation below Q1148, or a lower-cost exact sparse correction primitive.

## X006.6 — terminal-tail phase-repair autopsy

- Status: source repair KILL; frozen selection HOLD.
- Ancestor/source identity: clean `7ca0559` plus the exact cutoff697 diff in isolated branch `research/7ca-tail-phase-repair`, commit `96aa36e`.
- Cheapest falsifier: localize every modeled phase residual for classical-clean nonce4300192188 before widening any global window.
- Result: four pre-existing22-bit measured carry repairs own the residuals: multiply r219 requires24 bits, multiply r249 requires23, divide r123 requires26, multiply r572 requires23. The shared terminal sign is not the defect.
- Smallest repair: widen only those eight positions. Q stayed1278; emitted delta was +8CCX/+8Hmr/+7R/+8CZ/+48CX/+16X; T moved921214.444 ->921223.340.
- Generalization gate: the same source edit reseeded the corpus and failed `15/8/0`; the baked nonce failed `8/5/0`. It repairs one frozen draw rather than the architecture.
- Verdict: KILL local source repair; HOLD only zero-gate frozen-stream selection after structural work. No Range F.
- Evidence: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/7ca-tail-phase-repair/.lane/PHASE-REPAIR-OVERTURN.md`.

## X006.7 — tagged coefficient-absorption falsifier

- Status: current claim KILL; changed global codec semantics HOLD.
- Ancestor/source identity: clean `7ca0559`; independent audit committed as `ad206c9` on `research/7ca-teddy-square-dilated`.
- Claim tested: replay coefficient lows plus one tag can absorb the sign transcript and later expose it LIFO without separate tape.
- Cheapest falsifier: audit the decoder-visible state, known-zero coefficient inputs, retained numerator residual, modular high-word dependencies, and terminal cleanup before building a low-word census.
- Result: the proposed `k+2` low window is not closed under modular halving; boundary bits, full-word overflow, parity, high comparison, and terminal u/v signs are omitted. Its fiber key also retains predecessor residuals that are gone when walkback needs the transcript.
- Reachable-slice witness: zero numerator occurs for valid affine inputs. Exact modular replay then leaves each coefficient word in only `{0,p}`; coefficient pair, terminal signs, and one tag expose at most32 states, insufficient for more than32 accepted denominator transcripts.
- Verdict: KILL the memo-specified local census and current one-tag tape-elimination claim. Reopen only with a full-width global codec keyed solely by state actually live at walkback, or changed coefficient/cleanup semantics.
- Evidence: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/7ca-teddy-square-dilated/.lane/TEDDY-COEFFICIENT-ABSORPTION.md`.

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
