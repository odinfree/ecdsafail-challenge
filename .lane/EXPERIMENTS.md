# Balanced saddle experiment ledger

| id | exact route | artifact | fixed64 | full9024 | verdict |
|---|---|---|---|---|---|
| B0 | promoted `bdf4845`, all saddle env unset | 12,912,890 ops; SHA `5b60d0a...`; Q1278 | T915994.83, 0/0/0 | T915947.392, 0/0/0 | protected anchor |
| S77 | R1/R2 356/625, peak1277, ladder247 | 12,919,073 ops; SHA `a6a79c5a...`; Q1277 | T916234.28, 0/0/0 | T916186.355, 21/12/0, first cls124 | measured prior; dominated |
| S76 | R1/R2 356/625, peak1276, ladder246 | 12,929,346 ops; SHA `d1461959...`; Q1276 | T916718.89, 0/0/0 | T916628.572, 15/5/0, first cls32 | leading hunt geometry |
| S75 | R1/R2 342/625, peak1275, ladder245 | 12,947,403 ops; SHA `059a249a...`; Q1275 | T917331.19, 0/0/0 | T917361.243, 17/8/0, first cls923 | product loses to S76 |

## Exact falsifiers

| assumption | cheapest exact test | result |
|---|---|---|
| The one-notch pair does not lower global Q | forced Q1277 pair plus active timeline | overturned: three independent Q1277 owners |
| Q1277 is the best product saddle because it adds fewer repairs | unchanged full-shot product comparison | overturned: Q1276 is 350,918 lower |
| A milder cut should inherit a cleaner nonce | unchanged 9,024-shot channel comparison | overturned at this nonce: Q1277 is 21/12/0 versus Q1276 15/5/0 |
| Q1277 deserves a parallel fleet stream | require product or calibrated-density compensation | not established; product and observed fingerprint both lose |
| Q1274 should be sampled automatically | require a cheap dominance signal after Q1275 | rejected: Q1275 already crosses the one-qubit exchange rate |

## Reproduction knobs

Use a forced fresh output directory for every row.  The candidate switches are
runtime opt-ins already present in `bdf4845`; source defaults stay protected.

```text
S77: SUB4_PP_R1=356 SUB4_PP_R2=625 SUB4_PP_PEAK=1277 SUB4_SQUARE_LADDER=247
S76: SUB4_PP_R1=356 SUB4_PP_R2=625 SUB4_PP_PEAK=1276 SUB4_SQUARE_LADDER=246
S75: SUB4_PP_R1=342 SUB4_PP_R2=625 SUB4_PP_PEAK=1275 SUB4_SQUARE_LADDER=245
profile: PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1 PP_PROFILE_SEED=0
```

Final acceptance remains the unchanged trusted evaluator over all 9,024 shots
with classical, phase, and ancilla exactly `0/0/0`.
