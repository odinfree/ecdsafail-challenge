Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

Execution provenance: Claude Fable 5, max effort. Fable executed this bounded
takeover after the Kimi account reached its cycle limit.

# Multiply-walkback replay allocation: exact lifetime map, falsifier verdict KILL

**Scope:** burn-explorer lane `research/fable-burn-6b5c-mulwalkback` on the protected
leader `6b5c82c` (trusted Q1278 / T918358 / score 1,173,661,524). No stream change was
made or proposed; every run in this note is on the unchanged leader stream,
`ops.bin` md5 `c0eddceaca5a76fc2307a68efc7a2aa1` (12,950,916 emitted ops), verified
before, during (instrumentation env off *and* on), and after the measurements.
Credit: Teddy Pender — for the protected-leader discipline, the bounded saddle, the
falsifier-first ordering, and the grind-last rule this lane ran under.

## The assumption this lane was built to overturn

> The full 256-wire replay allocation must remain live through multiply walkback
> after its last replay consumer, and its storage cannot host any walkback state
> without changing the affine ABI.

Pre-registered cheapest falsifier: map every read/write/free of the replay
allocation across `pp_mul_replay` and `pp_mul_walkback`, find its last semantic
consumer and the first walkback peak, kill if a live dependency crosses the entire
binding interval. **The falsifier killed the lane.** Details below so nobody re-opens
this without new structure.

## 1. Reproduced plateau census (shipped gated knobs only, zero source changes)

`PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` on the leader stream, 64 lanes,
0 classical / 0 phase / 0 dirty, total 64-lane executed Toffoli 918,412.89
(consistent with the trusted 9,024-shot 918,358):

| phase | peak |
|---|---:|
| pp_div_replay | **1278** (first global peak, op 2,643,328) |
| square_product_register | **1278** |
| pp_mul_walkback | **1278** |
| pp_mul_replay | 1276 |
| every other phase | ≤ 1057 |

The Q1278 plateau is exactly three-way: divide replay, square, multiply walkback.
The multiply *tail batch* (`pp_mul_replay`) is NOT a member — it tops at 1276 with 2
wires of slack.

Owner census at the first `pp_mul_walkback` binding instant
(`B0_WIN_LO=0 B0_WIN_HI=13000000 B0_PHASE=pp_mul_walkback`, best_ops=8,976,984,
active=1278): tape signs 563+1, caller `y` (numerator) 256, **replay allocation
(coefficient, alloc site `pingpong_div.rs:302`) 256**, walk registers 2×61
(14 reacquired loan wires + 2 resident signs + 106 `grow_to`), chunk-ladder carries
77 (`chunk_add`, `pingpong_div.rs:1343`), boundary scratch 2, `doubled_out` 1,
residual shell wire 1, working-x remnant 1. Sums to 1278 exactly.

## 2. Exact lifetime map (temporary env-gated census in the multiply plan branch,
reverted after the run; instrumented default build stayed hash-identical)

Geometry at defaults: `ROUNDS_MUL=696`, `R1=356`, `R2=625`, `PEAK=1278`.
All op indices are absolute stream positions.

| event | op index | facts |
|---|---:|---|
| coefficient alloc | 8,218,090 | first action of `pp_mul_replay` |
| seed writes | 8,218,090.. | CX fanout from y, conditional negates (`:304-308`) |
| tail batch replay r=695..626 | [8,219,738, 8,590,388) | tape 696, max_active 1276 |
| walkback phase start | 8,590,402 | |
| tail walkback r=695..626 | [8,590,402, 8,609,417) | max_active 1248 |
| interleaved r=625..356 | [8,609,417, 10,302,012) | 270 rounds, replay-then-walkback |
| lower batch replay r=355..0 | [10,302,012, 11,990,464) | tape 356, walk 2×140, ladder 129 (2-chunk), max_active **1278** |
| **last semantic consumer** | 11,990,464 | final op of the r=0 doubling replay |
| **coefficient free** | 11,990,464 → 11,990,720 | the very next 256 ops (R resets); zero-op gap |
| final walkback r=355..0 | [11,990,720, 12,931,289) | max_active 1057 |

Binding set of `pp_mul_walkback` (allocator events at active=1278): **619 events,
first 8,976,984, last 11,985,135, zero after the free.** Three measured flavors:

* replay chunked adds — binding rounds span r=563 down to r=356 (70 rounds fill to
  exactly 1278; first binder r=563: tape 564 + 512 + walk 122 + ladder 77 + scratch 3);
* walk-back split adds — 99 late interleaved rounds bind at 1278 through the walk
  adder's own budget-filled ladder (e.g. r=400: replay_max 1278 AND wb_max 1278);
* the lower batch — 356+512+280 footprint + 129-wire 2-chunk ladder + 1 = 1278.

## 3. Why each overturn disjunct is dead

**Release:** the storage is already returned at the exact last-consumer op (zero-op
gap measured above; `free_vec` at `pingpong_div.rs:335` precedes the final 356
walk-back rounds). There is no post-consumer liveness to reclaim — the assumption's
premise does not exist in the live stream. Before that point, every binding instant
lies inside the allocation's live span, and at the replay/lower-batch binders the
allocation is an *operand of the binding add itself* (all 256 wires are read/written
every round — chunked add plus fold cover the full register, both parities). At the
walk-back-add binders the coefficient idles but holds an unrecomputable partial
product still needed by every remaining replay round below r; parking 256 wires of
live data needs 256 other wires that do not exist below peak.

**Alias:** the coefficient is seeded as ±y (`:304-308`) but diverges from y at the
first doubling round; the replay evolves a 2-dimensional module state — two
independent registers are algebraically forced from round one.

**Restored scratch (dirty hosting):** every binding allocation is a
measured-cleanup carry ladder — `chunk_add` erases owned carries via `hmr`+`cz_if`
(`:1389-1391`), and the walk `sigma` adders do the same (`:822-871`). The Gidney
measured-uncompute mechanism requires the carry to start clean (|0⟩): a CCX into a
dirty borrowed wire computes carry⊕garbage and the X-basis measurement then leaves
an uncorrectable state/phase on the host. Hosting ladders in idle live wires
(coefficient chunks, tape, y) therefore means abandoning measured cleanup for a
borrowed-bit compute/uncompute discipline — estimated ≥2× the carry Toffoli on the
dominant add surface (estimate, not measured; not worth measuring under the tie
law below).

**Tie law:** `pp_div_replay` (binds first, op 2,643,328) and
`square_product_register` sit at 1278 regardless of anything done to the multiply
side. Any multiply-only width cut buys zero score until both other owners drop —
it is a strictly-positive-T, zero-Q trade single-wall. The pre-registered gate
("build the 4–8-round slice only if the map survives") therefore stays shut; no
slice was built.

## 4. Durable numbers for the composition lanes

The multiply walkback's 1278 membership is a *chosen ladder budget*, not a floor.
Measured footprints excluding ladders/scratch: interleaved maximum 1210 at r=625
(tape 626 + 512 + 2×36), tail batch 1210 (696+512+2), lower batch 1149
(356+512+280). With minimal 8-chunk ladders (~33+3 wires) the multiply side could
ride ≈ 1246 (estimate from measured footprints + `ladder_for_chunks`), i.e. ~28
qubits of slack purchasable only with boundary-repair Toffoli across ~700
rounds/traversal — the known wash regime (note 09 §4 priced the neighborhood; the
economics have not improved at this geometry). A composition that first takes
`pp_div_replay` and the square below 1278 should re-open the multiply side through
`SUB4_PP_PEAK`/plan budgets, not through this lane's lifetime route.

## 5. Reproduction

```bash
./target/release/build_circuit && md5 ops.bin      # c0eddceaca5a76fc2307a68efc7a2aa1
PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1 ./target/release/build_circuit   # §1 table
B0_WIN_LO=0 B0_WIN_HI=13000000 B0_PHASE=pp_mul_walkback \
  ./target/release/build_circuit                    # §1 owner census
```

The §2 per-round table needs the temporary census block (env-gated
`SUB4_PP_MULWB_CENSUS` + `PROFILE_ACTIVE_TIMELINE`) in the multiply plan branch of
`pingpong_mod_mul_div_in_place`: snapshot `b.ops.len()`/`b.active_timeline.len()`
around each replay/walk-back call and print per-round maxima; it was verified
hash-neutral (md5 unchanged with the gate off and with it on) and reverted after
this note's numbers were captured.
