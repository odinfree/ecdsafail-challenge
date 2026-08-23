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

The base reproduction switch for any replay-fold experiment is
`SUB4_PP_REPLAY_FOLD_WINDOW=54`. A changed default is invalid unless this
switch reproduces the exact base ops count and SHA above.

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
```

Expected ops SHA-256:
`d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124`.

No experiment may overwrite either protected reference.
