# Q1270 square-boundary predictor regression

Date: 2026-08-23. Decision:
`PASS / 17 SOURCE-BOUND EVENTS / INTEGER RESIDUAL ZERO / PREDICTOR ONLY`.

This offline gate adds no circuit edit, operation build, nonce processing,
provider action, hunt, submission, or large artifact. It turns the sealed
square-boundary review into a deterministic native predictor regression.

## Frozen source binding

- circuit source commit: `90770b10664fc89065b1d05ac792370efed4c629`;
- Q1270 evidence base commit: `ba8612480e0cf66522c95d81810189fdd486975e`;
- square source SHA-256:
  `864d31454c5279632652cf48aeda038d481a504b09e4f7a8c0f266e10a24b81c`;
- chunk-layout source SHA-256:
  `9b1e5e8540a01584e1238c27328481ba67db3b167aa199db4113e846f1eb6295`;
- sealed review SHA-256:
  `8c0d8359b33ce6fefa45cb409028c9a7764348c536fc4f40f93b9b50f105a6e8`.

The new `src/q1270_square_boundary.h` is SHA-256
`5cda36dffc29fd8a19881214900e580d3a9c7cbed729dab8f4b6a731565aca52`.
The updated CLI source is SHA-256
`10c388c45da4cb064adae86d53227eb3980904ca9cf3dafe7f48e41561f89717`.

## Regression contract

`q1270_ppcpu square-boundary-selftest` enumerates the exact 17 source-order
events. Ladder 240 and compare window 20 derive only these two-chunk layouts:

```text
247 -> 7+240
251 -> 11+240
253 -> 13+240
256 -> 16+240
257 -> 17+240
258 -> 18+240
```

It separately rejects boundary creation for the sealed one-chunk widths
`129/154/225/241`. The event ledger includes six complemented `sub_full`
frames and explicitly requires the B full-shift-6 frame to have `sign=0`.

For every leading width and every `b` in `[0,2^l)`, the regression checks both
integer intervals around the sole transition `a=2^l-b`:

```text
floor((a+b)/2^l) == ((a+b mod 2^l) < b)
```

For complemented frames it also enumerates every possible low chunk and
requires `~x mod 2^l = 2^l-1-x`. Thus `sub_full`'s pre-add X layer spans the
same complete integer domain; its outer identity is
`~(~x+y) = x-y (mod 2^W)`. Every event reports `residual=0`.

## Independent builds and tests

Apple clang C++20 `-O3 -DNDEBUG -Wall -Wextra -Werror` built the updated native
unit twice from separate output directories, once through relative paths and
once through absolute paths. The binaries were byte-identical:

- build A/B binary SHA-256:
  `f7ce2e97e2f0ce11dccb55bdc3db4d35ab45a6cf336a25b5ff6486889c0596ad`;
- byte-identical square-regression output SHA-256:
  `a62ccdfd55715401653484081814b0aefbd9c13978970f505abad1430ed1af77`;
- terminal result:
  `SQUARE_BOUNDARY_SELFTEST PASS events=17 residuals=0 sub_full=6 shift6_sign0=1 ladder=240 compare=20`.

Both binaries also reran the prior native tests without drift:

- identity output SHA-256:
  `c7107e205415146c6ed9cda0bd3d4b0c1858bf067acd11c9eb2ba13c6334ef99`;
- recurrence self-test output SHA-256:
  `10497c962e4ca914ae3e5cb1fa0b2127bde9e59c0a769fc5bd0b2673b91dfdeb`.

The build directories remain small temporary local artifacts outside Git.
This receipt qualifies only the square-boundary simplification inside the
predictor. It is not a circuit qualification or authorization to hunt.
