# b523ecf BREAK_1 counterbeat sweep

The frozen ten-point sweep completed. Every changed stream used the unchanged
9,024-shot evaluator at the promoted nonce. All variants had Q1278 and zero
ancilla faults. Generated `results.tsv` rows were removed after transcribing
the measurements; generated operations, logs, binaries, and temporary build
directories are not tracked.

| BREAK_1 | T average | rounded product | operations | classical/phase/ancilla | operation SHA-256 |
| ---: | ---: | ---: | ---: | ---: | --- |
| 20 | 910902.327 | 1,164,132,756 | 12,817,013 | 36/19/0 | `3edbab0a2c7ecc2bc43f21776a42d70ca995e690cd51ebb852924e9ba7b4a806` |
| 24 | 911310.414 | 1,164,654,180 | 12,822,408 | 17/13/0 | `af28dbc49471651c3e856c62c1fd97cb429469cde4b66fe7fe082a0d23fe1ad7` |
| 26 | 914378.785 | 1,168,576,362 | 12,871,180 | 15/15/0 | `91901d65b4f45f667b8d1c10e1e0e5fc28e2d10653fd58df7ef05fa56a0a44b3` |
| 28 | 917512.843 | 1,172,581,614 | 12,921,133 | 14/17/0 | `1f7dd086f566756698b9195f160e7576272db6e3734c1d8118626505538c7e88` |
| 29 | 917887.162 | 1,173,059,586 | 12,926,106 | 11/10/0 | `f165e8f2ca1428a4bec2cb72f3fbb0f030202c0908c48e6b26d81ad9363d6084` |
| 31 | 917529.931 | 1,172,603,340 | 12,921,341 | 14/12/0 | `c18823e1807f975f24870a033b83ad79534feb2173d9231b784c48c2aa8f8908` |
| 32 | 917907.091 | 1,173,085,146 | 12,926,262 | 21/20/0 | `c14974e766f4863fe6138d7ccfe2be7b2352e56160a4d18bef76e99b1d5dc0be` |
| 34 | 921070.295 | 1,177,127,460 | 12,977,189 | 6/10/0 | `de0324886c4a5b6adfb025d0ccc3a6ae33b91b5bfd7dcf4fb4a79e530588740f` |
| 36 | 918287.664 | 1,173,572,064 | 12,931,444 | 16/10/0 | `261ed366066ad7944b5160c9382a4656680432cb202d2ffb3f69ca3106ec8f0a` |
| 40 | 924640.848 | 1,181,691,198 | 13,034,123 | 12/10/0 | `0972b7a2454e753db7b3778e45439b2f90f9c9fe45496f0e925927971a41e49d` |

## Decision

`BREAK_1=24` is the primary counterbeat stream. Its fixed-nonce diagnostic is
dirty, so the promoted nonce is not transferable, but its projected score is
4,447,440 below live `b523ecf` and its 17/13/0 fault band is close enough to
the live stream to justify a source-bound exact predictor. `BREAK_1=20` is a
cheaper structural reserve with a substantially worse fault rate. `BREAK_1=26`
is the low-headroom reserve. The remaining points do not project a strict beat.

Next action: freeze the full B1=24 operation identity, port the exact classical
and phase screen to that source, prove local CPU and Linux/CUDA per-shot parity,
then authorize only a bounded canary before any fleet retarget. No result from
this sweep is submission-ready.
