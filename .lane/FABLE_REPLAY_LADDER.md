# HOLD-HUNT — replay chunk-carry ladder single-wire overturn, Q1273 landed on Q and priced on T

Resolved: 2026-08-23. Lane: `research/fable-2c79-replay-ladder-overturn`.
Binding predeclaration: `.lane/PREDECLARATION-REPLAY-LADDER.md`, commit
`1a9ecd5` (pushed to `odinfree` before any armed measurement).
Frozen parent / promoted source: `2c79d2f4ef1f6fdc6f75024ef4ae50c6506e2208`
(tree `d50e00b6ba06975de822e7184ca930d3542e255e`), Q1274 / rounded T916526 /
score 1,167,654,124. Live board reopened this session: current best is still
1,167,654,124 @ 2c79d2f, so the Q1273 strict ceiling is rounded T ≤ **917,245**
(floor((1,167,654,124−1)/1273); headroom +719 over the parent's 916,526).

## Verdict

**The family fired. Q1273 is real and measured on both trust paths; the T
price is measured at +632…+678 executed (projected official 917,157…917,203
from the control-pinned base 916,525.546, under the 917,245 ceiling by
42…88); the single authorized inherited-nonce
diagnostic is DIRTY (12 classical / 12 phase-batches / 0 ancilla), exactly the
family's unhunted baseline class. HOLD-HUNT**: the candidate needs a GPU nonce
hunt (excluded from this lane) before any submission. No stop rule fired; this
is stop-rule-4's recorded outcome, not a KILL.

Candidate configuration (no source edit; both knobs exist in the frozen
parent): `SUB4_PP_PEAK=1273 SUB4_SQUARE_LADDER=243`.
Streams: default (parent) `ops.bin` md5 `fdbc7f23a1ed45cca413531bed988100`;
armed md5 `5ba8782cd13b79eda79752b9351bc166` (12,933,805 ops, +13,732).
`git diff 2c79d2f -- src/` is empty; opt-out byte identity holds by
construction.

## Census correction (measured, supersedes the inherited three-way claim)

The predecessor lane (`research/fable-2c79-retained-transducer@fb07d5e`)
reported a three-way Q1274 tie. The full-phase profile on the default build
shows **four** binders at exactly 1274 — its census omitted the square:

```text
phase                      peak   exec_tof (default)
pp_div_replay              1274   263,451.39   <- binder (terminal batch ladder 62)
square_product_register    1274    58,703.33   <- binder (SQUARE_LADDER=244, peak=1030+244) MISSED UPSTREAM
pp_mul_replay              1274    23,982.41   <- binder (terminal batch ladder 63 + doubled_out)
pp_mul_walkback            1274   307,827.27   <- binder (interleaved replay + split-walk ladders)
pp_div_walk/walkback, pp_mul_walk  1057
all tlm_* coordinate phases       ≤1026
```

Reproduced parent identity: peak_qubits = num_qubits = 1274, peak binds at
ops_idx 2528381 in `pp_div_replay` (terminal batch; matches predecessor),
shoulder 1271 @ 929878, 64-lane composition `0 / 0x0 / 0`, emitted CCX+CCZ
957,374, 64-lane exec 916,424.62 (profile lanes) / 916,510.47 (selfcheck
lanes). Parent official receipt bound by integer identity
1274 × 916,526 = 1,167,654,124 (live board) and re-verified by the parent
control below. Divide terminal co-binder identity: tape 698 + coefficient 256
+ numerator 256 + 2 loaned signs + ladder 62 = 1274, layout
`chunk_layout(256,62,final)` = `[12,61,61,61,61]`.

Every binder is a budget-filled carry ladder: the three `pp_*` binders derive
from `plan.peak` (`SUB4_PP_PEAK`, `pingpong_div.rs:1263`) through
`pick_chunks → chunk_layout` (batch + interleaved replay) and
`walk_low_chunk` (split-walk); the square binder from `SQUARE_LADDER=244`
(`product_register.rs:28`) through the same `add_chunked_measured_budgeted`.

## Family execution (predeclared search order)

1. **Ladder-endpoint reconstructibility** (dispatch step 1): proven
   reconstructible in principle — the boundary/final carry of chunk j equals
   `[sum_j < addend_j]` modulo the `addend=2^w−1 ∧ cin` edge; the artifact
   already evaluates exactly this in its measured-erasure repairs. Every
   replacement realization was priced statically and killed **before coding**:
   - exact in-place: a ≥w-bit comparator carries its own ≥w−1 ladder — no
     width win at the binding instant;
   - deferred exact recompute: ≥ +256 emitted CCX per replay round ≈ +18k–35k
     executed T ≫ +719 ceiling;
   - truncated recompute feeding the fold: moves approximation into the
     classical data channel — soundness KILL regardless of economics;
   - dirty-borrowed endpoint (idle tape sign / loaned passenger): `t⊕c`
     cannot control the fold-selector ANDs; compensation doubles the fold;
     and `hmr` measured erasure cannot touch a borrowed wire at all. KILL.
2. **Surviving realization — allocation contraction**: remove the top
   simultaneously-live carry/bridge wire of every peak-filling ladder by
   shrinking each budget by one (`SUB4_PP_PEAK=1273`,
   `SUB4_SQUARE_LADDER=243`). Binding layouts stay structurally identical
   (same chunk counts, same approximate-repair counts): divide terminal
   `[12,61,61,61,61] → [16,60,60,60,60]`; multiply terminal
   `[8,62,62,62,62] → [12,61,61,61,61]`; split-walk `low` grows by 1 (its
   boundary repair is exact by construction); square leading chunk shifts
   ~1 bit. Carry values everywhere remain bit-exact over re-partitioned
   ranges; approximation stays confined to the existing phase-channel
   repairs. The walk-split guards hold with ≥50-wire margin at peak−1
   across the whole interleave (checked against the width schedule).

## Measured gates (armed = `SUB4_PP_PEAK=1273 SUB4_SQUARE_LADDER=243`)

| gate | result | verdict |
|---|---|---|
| predeclaration pushed before armed runs | `1a9ecd5` on `odinfree` | PASS |
| armed peak / trusted Q (builder) | peak_qubits = num_qubits = **1273**, binds ops_idx 2528391 `pp_div_replay` | PASS |
| armed trusted Q (trusted evaluator) | `eval_circuit` prints qubits : **1273** (max referenced id + 1) | PASS |
| per-phase maxima, armed | all four former binders exactly 1273; next 1057; nothing new ≥1274 | PASS |
| 64-lane composition, armed (profile) | classical 0, phase 0x0, dirty 0 | PASS |
| square component miter armed | selfcheck PASS, 1273 peak standalone | PASS |
| composition selfcheck armed | 64 affine adds correct, phase 0, ancillas clean, 1273 qubits | PASS |
| emitted T delta | 957,374 → 958,513 CCX+CCZ (**+1,139 emitted**, deterministic) | measured |
| executed T delta, paired lanes | profile lanes +631.86 (916,424.62→917,056.48); selfcheck lanes +677.89 (916,510.47→917,188.36) | measured |
| projected official rounded T | 916,525.546 + (632…678) = **917,157…917,203 ≤ 917,245** | PASS (margin 42…88) |
| opt-out byte identity | no source edit; default md5 `fdbc7f23…` unchanged | PASS |
| full 9,024-shot diagnostic, inherited nonce unchanged (the one allowed) | **12 classical / 12 phase-batches / 0 ancilla** — DIRTY | HOLD (stop rule 4) |
| parent control eval, same environment | 9,024/9,024 OK `0/0/0`, avg executed Toffoli **916,525.546** (rounds to 916,526), qubits 1274 — receipt reproduced to the decimal | PASS |

Projected candidate score if a hunt lands a clean nonce at the measured T:
1273 × (917,157…917,203) = **1,167,540,861…1,167,599,419**, i.e. −54,705…
−113,263 under the live 1,167,654,124 (exact value fixed by the hunted
nonce's own executed-T draw; the ceiling identity guarantees any rounded
T ≤ 917,245 beats the frontier).

## Critique, fix, verify

- **Dirty ≠ regression.** The armed 12/12/0 is the family's *unhunted*
  intrinsic rate, not a new fault mechanism: the adjacent-lane control on
  b523 measured 14/9/0 for an unhunted stream of the same lineage, ancilla
  stays exactly 0 here, and every arithmetic change is provably value-exact
  (chunk re-partitioning only). The parent's 0/0/0 on this nonce is a hunted
  tail event; any stream perturbation re-rolls all ~2.3k measured repairs
  per shot. The candidate's cleanliness question is a hunt question by
  construction, which this lane is forbidden to answer.
- **Thin T margin objection.** Two independent paired 64-lane deltas (+632,
  +678) bracket the projection under the ceiling by 41…87; the emitted delta
  (+1,139, deterministic) matches the static component sum (terminal-batch
  leading compares +~544, split-walk lows +~440, fill-band/cliff shifts and
  square the remainder). The hunted nonce will move executed T by its own
  draw (±~tens); the successor must re-check the rounded value against
  917,245 at hunt time — the gate is recorded, not assumed.
- **Fourth-binder objection to the dispatch.** The dispatch's family clause
  ("no Q1274 tie remains") governs over its three-phase enumeration; the
  measured tie is four-way and all four were dropped simultaneously. A
  three-phase-only cut would have left Q1274 standing on the square and
  failed the N-way-tie law.
- **Knob-vs-structure objection.** The lever is an allocation-schedule
  contraction realized through existing budgets — but it is exactly the
  family's invariant (one fewer simultaneously live carry wire at every
  binding instant, values bit-exact), it moves trusted Q on both the
  builder and the trusted evaluator, and every transducer-shaped
  alternative was priced dead first, per the dispatch's preferred order.
  Nothing retains a referenced high qubit id: max referenced id + 1 = 1273.
- **Why no R1/R2 rebalance ran.** Stop rule 2 triggers only if the projected
  rounded T exceeds 917,245; it never did (917,158…917,204). No unpredeclared
  knob was swept.

## Next binder (for the successor lane)

At Q1273 the co-binder identity becomes tape 698 + 512 ABI + 2 loaned signs +
ladder 61 = 1273. The ladder still has measured slack of the same kind
(each further −1 costs ≈ +630…+680 executed T at default R1/R2 against a
Q1272 headroom of +1,441 from 916,526, i.e. roughly two more wires before
layout cliffs — but each step needs its own hunt). The sign tape (698) and
ABI (512) remain exactly floored by the predecessor's bounds. Immediate
successor actions, in order:
1. GPU nonce hunt on the armed stream (`SUB4_PP_PEAK=1273
   SUB4_SQUARE_LADDER=243`, md5 `5ba8782c…`), target 0/0/0, then re-verify
   rounded T ≤ 917,245 on the hunted nonce and submit at Q1273.
2. If the hunt stalls, one predeclared R1/R2 rebalance at PEAK=1273 to trade
   executed T for repair-count λ before re-hunting.
3. The next structural family after the ladder is exhausted: the 512-wide
   ABI (coefficient+numerator co-residency at the replay), the only
   non-floored term above 62 wires.

## Model receipt

Claude Fable 5 (`claude-fable-5`), single-lane research worktree, autonomous.
No nonce hunt, no provider/cloud compute, no submission, no public note, no
API-key access, no external communication, no edits outside this worktree.
`ops.bin`, `score.*`, `results.tsv` changes, `target/` not committed.
Commits: predeclaration `1a9ecd5`, this account. Spend recorded by the
harness.
