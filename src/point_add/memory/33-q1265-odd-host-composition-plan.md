# Q1265 odd-passenger plus source-host composition

Status: `BOUNDED LOCAL FALSIFIER / DEFAULT OFF / SUBMIT CLOSED`

## Changed premise

The source-host route was correct at Q1266 but too expensive when it fired
1,665 times. The admitted odd-passenger loan now removes one peak qubit with
Clifford-only toggles. This composition asks whether the lower live occupancy
reduces the exact source-host activation count enough to buy Q1265 inside its
larger T exchange budget.

## Binding

- official parent source: `67524171baaf568dc3dc606f38515745f70804ff`
- admitted odd-passenger implementation: `61b974c27409d5baf3677da37f38e2f2d84078d7`
- independent oddness certificate: `57ee207abe9f648dbc443bfb329e051707327d46`
- activation requires both `SUB4_PP_INTERLEAVED_ODD_LOAN=1` and
  `SUB4_BINDING_SOURCE_CARRY_Q1265=1`
- fresh score to beat: `1154731130`
- Q1265 rounded-T ceiling: `912830`
- nominal exchange headroom over live T911390: `1440`

## Gates

1. Both switches absent preserve the official source behavior; the new carry
   host remains strict default-off.
2. Odd loan alone reproduces its frozen Q1266 candidate binding.
3. Composition must reach Q at most 1265 in both prior co-binding phases.
4. Source checks and a mechanically isolated 64-shot evaluator must report
   classical/phase/ancilla `0/0/0`.
5. The measured 64-shot T must round at or below 912830. The exact emitted CCX
   delta and activation count are recorded; a Q cut without winning economics
   is a hard nack.

No full 9,024-shot replay, prefilter rebuild, provider retarget, nonce search,
queue, public note, or submission is authorized by this diagnostic. The active
Q1266 operation stream and GPU lease remain frozen and untouched.
