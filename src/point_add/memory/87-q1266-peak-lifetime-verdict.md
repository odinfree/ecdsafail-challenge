# Q1266 Peak-Lifetime Verdict

Verdict: `ADMIT_SIGN_TAPE_AS_NEXT_STRUCTURAL_OWNER`

The current diagnostic stream binds at Q1266 during `pp_div_replay`. The exact
owner census is not a flat 696-bit terminal tape: at the binding operation only
333 tape bits have been emitted, while 512 coefficient/data bits, 290 residual
walk bits, a 125-bit split-adder ladder, and six small wires fill the peak.

The harder structural fact appears at terminal replay. Once all 696 division
signs exist, the loaned walk state is small, but the tape and two 256-bit words
already total Q1208 before any control or arithmetic scratch. Consequently:

- another carry-ladder rearrangement cannot reach Q1169;
- lowering `SUB4_PP_PEAK` does not lower the measured Q because the two-chunk
  walk adder falls back when its requested low half is infeasible;
- the measured cap sweep pays between 20.5k and 128k extra executed Toffoli and
  remains at Q1266 for requested caps from 1240 through 1150.

The unique next owner is the division sign tape or its hosting schedule. A
viable Q1169 route must delete at least 40 resident bits plus its own controls,
and a 10% whole-score route must also satisfy the relevant T ceiling recorded
in the ledger.

`.lane` and `./bin/coord-post` are absent from this isolated candidate
worktree. The ledger is therefore committed beside the source-bound research
receipts; no unwrapped coordination write was improvised.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
