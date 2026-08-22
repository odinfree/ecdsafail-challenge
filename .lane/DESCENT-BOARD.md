# Descent board

## Score gate

| Q | strict maximum rounded T |
|---:|---:|
| 1278 | 924650 |
| 1277 | 925375 |
| 1275 | 926826 |
| 1270 | 930475 |
| 1269 | 931208 |
| 1260 | 937860 |

Always verify with the exact product; the table is a routing aid.

## Ancestor ladder

| id | source | role | known public Q/T | use in this lane |
|---|---|---|---|---|
| A0 | `897dda2` | first promoted ping-pong architecture | 1321 / 952707 | active clean ancestor |
| A1 | `8d7051b` | later width/depth/failure-budget descendant | 1278 / 930729 | comparison only |
| A2 | `787eaa8` | later replay-budget descendant | 1278 / 925387 | comparison only |
| A3 | `70d64f5` | protected live leader | 1278 / 924651 | score gate only |

## Explorer portfolio

| lineage | ancestor | structural hypothesis | target direction | current Q/T | correctness | saddle budget | status | next falsifier |
|---|---|---|---|---|---|---|---|---|
| E-001 | A0 | punch lifetime/materialization holes in replay co-residence | lower tied replay peak | 1266 / 1036334 diagnostic | affine clean; trusted 1/1/0 | completed X002-X004 cycle | retained saddle | T economics fail |
| E-002 | A0+E-001 | erase carry boundaries more cheaply or expose enough dead wires for fewer plots | Q<=1270 and T<930475 | 1266 / 1036334 diagnostic | affine clean; trusted 1/1/0 | 2 structural attempts | active | no boundary family or >=16-wire cut |
| E-003 | A0 | replace a uniform replay region with a proof-backed step schedule | lower Q and T without round truncation | pending | untested | deferred until E-002 boundary result | deferred | derive exact width envelope |

## Composition matrix

| ancestor | first lever | second lever | order | Q | T | correctness | verdict | evidence |
|---|---|---|---|---:|---:|---|---|---|
| A0 | terminal passenger loan | `starkWINTER` endpoint tape | lifetime then workspace | 1306 | 954139 diagnostic | affine clean; trusted dirty | retained component | X002/X003 |
| A0 | `starkWINTER` | `clankerFARM` | workspace then split carries | 1266 | 1036334 diagnostic | affine clean; trusted 1/1/0 | retained saddle | X004 |

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
