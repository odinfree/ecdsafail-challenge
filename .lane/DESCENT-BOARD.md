# Descent board

## Score gate

| Q | strict maximum rounded T |
|---:|---:|
| 1278 | 921557 |
| 1277 | 922279 |
| 1270 | 927363 |
| 1266 | 930293 |
| 1000 | 1177751 |
| 800 | 1472188 |
| 700 | 1682501 |
| 637 | 1848902 |

Always verify with the exact product; the table is a routing aid.

## Ancestor ladder

| id | source | role | known public Q/T | use in this lane |
|---|---|---|---|---|
| A0 | `897dda2` | first promoted ping-pong architecture | 1321 / 952707 | active clean ancestor |
| A1 | `8d7051b` | later width/depth/failure-budget descendant | 1278 / 930729 | comparison only |
| A2 | `787eaa8` | later replay-budget descendant | 1278 / 925387 | comparison only |
| A3 | `70d64f5` | previous protected leader | 1278 / 924651 | historical score gate |
| A4 | `b5796ce` | protected live leader refreshed 2026-08-22T11:43Z | 1278 / 923463 | current score gate only |
| A5 | `7ca0559` | protected live leader refreshed 2026-08-22T12:16Z | 1278 / 921558 | current score gate and tape-negative evidence |

## Explorer portfolio

| lineage | ancestor | structural hypothesis | target direction | current Q/T | correctness | saddle budget | status | next falsifier |
|---|---|---|---|---|---|---|---|---|
| E-001 | A0 | punch lifetime/materialization holes in replay co-residence | lower tied replay peak | 1266 / 1036334 diagnostic | affine clean; trusted 1/1/0 | completed X002-X004 cycle | retained saddle | T economics fail |
| E-002 | A0+E-001 | erase carry boundaries more cheaply or expose enough dead wires for fewer plots | Q<=1270 and T below live gate | 1270 / 1021815 diagnostic | affine clean; no trusted run | 2 structural attempts complete | deferred | companion T lever required |
| E-003 | A0 | replace a uniform replay region with a proof-backed step schedule | lower Q and T without round truncation | pending | untested | deferred until E-002 boundary result | deferred | derive exact width envelope |
| E-004 | A0 | replace resident sign tape with checkpoint/recompute under a different peak schedule | remove hundreds of persistent Q while spending bounded T | 1266 / 1431658 diagnostic | 64-lane clean | completed exact cycle | killed on current walk | +38.15% T, global Q flat |
| E-005 | A5 | encode signs in a near-minimal coherent denominator code | target 1028-class envelope with bounded decoder cost | primitive Q1533 / emitted T unchanged | 64-lane clean | prefix ladder 1/2/4/8 complete | HOLD | reopen only above256 decisions or without code co-residency |
| E-006 | A5 | replace terminal-orbit tape suffix with one shared sign | immediate same-Q strict T beat | 1278 / 921214 trusted clean-classical draw | full9024 `0/2/0`; zero K0 over394240 scans | bounded pilot complete | HOLD | structural phase change or later K0 selection |
| E-007 | A5 | remove square zero-pad co-binder with sparse structural arithmetic | lower square below future tape/replay composition | standalone 1148 / 59598 diagnostic; whole 1278 / 922501 | deterministic64 `0/0/0` | exact sparse primitive complete | HOLD component | compose only after replay <1148 |
| E-008 | A5 | absorb the sign transcript into replay coefficient state | bypass code/recompute wall | no circuit candidate | lifecycle/capacity falsifier | one bounded audit | KILL current claim | global walkback-live codec or changed cleanup only |

## Composition matrix

| ancestor | first lever | second lever | order | Q | T | correctness | verdict | evidence |
|---|---|---|---|---:|---:|---|---|---|
| A0 | terminal passenger loan | `starkWINTER` endpoint tape | lifetime then workspace | 1306 | 954139 diagnostic | affine clean; trusted dirty | retained component | X002/X003 |
| A0 | `starkWINTER` | `clankerFARM` | workspace then split carries | 1266 | 1036334 diagnostic | affine clean; trusted 1/1/0 | retained saddle | X004 |
| A0+E-001 | staged 144-round tape retirement | 64-bit remaining replay | lifetime then wider replay | 1270 | 1021815 diagnostic | affine clean | deferred; economics fail alone | X005.2 |
| A0+E-001 | staged 320-round tape retirement | exact low-Q walk + 96-bit remaining replay | lifetime then wider replay | 1266 | 1044760 diagnostic | affine clean | killed as dominated | X005.2 |
| A0+E-001 | staged 320-round tape retirement | chunked walk + 96-bit remaining replay | lifetime then wider replay | 1266 | n/a | deterministic phase dirty | killed | X005.2 |
| A5 | lower `SUB4_PP_PEAK` to 1266 | existing live interleaver | replay-budget only | 1278 | 934956 diagnostic | affine clean | killed; global Q flat | X006.0 |
| A0+E-001 | exact walkback/rewalk | erase and reconstruct current tape | recompute then replay | 1266 | 1431658 diagnostic | 64-lane clean | killed; +38.15% T and Q flat | X006.1 |
| A5 | 256-bit denominator code | round-zero tape donation | tagged code then exact restore | 1533 primitive | emitted T unchanged | 64-lane clean | open primitive, not a score candidate | X006.2 |
| A5 | terminal cutoff697 | shared tail sign | tail codec then full coefficient replay | 1278 | 921215 trusted draw | full9024 `4/4/0` | strict economics; hunt gated | X006.3 |
| A5 | sparse square zero pads | existing replay | square first, tape unchanged | 1278 global / 1148 square | 922501 diagnostic | deterministic64 clean | HOLD; replay sole binder | X006.5 |
| A5 | terminal cutoff697 | local HMR repair widening | tail then fitted phase repair | 1278 | 921223 trusted fitted draw | reseeds `15/8/0`, `8/5/0` | KILL overfit | X006.6 |
| A5 | coefficient absorption | one-tag local decoder | replay carrier then walkback extraction | n/a | n/a | capacity contradiction | KILL current semantics | X006.7 |

## Research-to-hunt gate

- [ ] Exact source commit and diff recorded.
- [ ] Fresh build observed; no inherited `ops.bin` reused.
- [ ] Peak owners and movement measured.
- [ ] Q/T economics strictly clear the live score or the route remains explicitly in a bounded saddle.
- [ ] Reference/selftest or equivalent cheap correctness falsifier passes.
- [ ] Target-bound classical filter has zero observed false negatives against trusted fixtures.
- [ ] Phase and ancilla risks are localized.
- [ ] Only then may a bounded nonce pilot begin.

## Shipping gate

This lane cannot submit. A winner must be ported to a fresh shipping tree and separately authorized, then pass a full clean 9024-shot trusted result.
