# Protected reference

Frozen before new measurement on 2026-08-23 (Europe/Zurich).

## Exact Q1272 base

| field | frozen value |
|---|---:|
| source | `091abce0c0ac73f5e1965034fa976fa14c855594` |
| ops | `12,901,167` |
| ops SHA-256 | `ecc3d9f0bb1dd4e68e6d337e39c4cdb66cfbfe83928a81fec28e22797fca4cfd` |
| peak Q | `1272` |
| 64-lane diagnostic T | `914748.17` |
| inherited full result | `17/16/0`, exact average T `914792.720` |
| rounded-T ceiling | `921139` |

The base reproduction switches for a replay-fold/selector experiment are
`SUB4_PP_REPLAY_FOLD_WINDOW=54 SUB4_PP_MUL_PLUS2F_ALIAS=0`. A changed default
is invalid unless this vector reproduces the exact base ops count and SHA
above.

## Promoted-route reproduction fixture

This is a local byte-identity fixture from the audited source history, not a
claim that the public leaderboard was refreshed in this local-only lane.

```text
SUB4_PP_ROUNDS=698
SUB4_PP_ROUNDS_MUL=696
SUB4_PP_WIDTH_RESCALE=0
SUB4_PP_R1=342
SUB4_PP_R2=625
SUB4_PP_PEAK=1275
SUB4_SQUARE_LADDER=245
SUB4_PP_REPLAY_FOLD_WINDOW=54
SUB4_PP_MUL_PLUS2F_ALIAS=0
```

Expected ops SHA-256:
`d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124`.

No experiment may overwrite either protected reference.

## Held structural component

`SUB4_PP_REPLAY_FOLD_WINDOW=55 SUB4_PP_MUL_PLUS2F_ALIAS=1` reconstructs
12,939,336 operations at SHA-256
`d4ecab6dd80d044d0a28ae456a9106992d2b3aae070d80cfa0dde3d24400f920`,
Q1272, same-seed diagnostic T916117.12, and `0/0/0`. It is not the leader or a
hunt stream: the exact H64 gate contains one new result fault and the inherited
nonce is `14/14/0`.
