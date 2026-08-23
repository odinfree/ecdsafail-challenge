# Composition matrix

Frozen before new measurement on 2026-08-23.

| component | base | E-001 | future saddle constraint |
|---|---:|---:|---|
| divide/multiply depth | 696/696 | unchanged | terminal tail changes require tape/replay composition |
| rescaled width schedule | on | unchanged | widening is a separate Fable lane and is not imported |
| replay fold window | 54 | 55 | base opt-out `=54` |
| replay peak / square ladder | 1272 / 242 | unchanged | all co-binders must remain Q1272 |
| replay hard channel | measured on corpus H | predicted lower | primary decision signal |
| phase density | measured on corpus P | measured on corpus P | secondary signal; no independence assumption |
| full rounded T | 914793 | must be <=921139 | hard gate |

E-001 is not composed with width-repair tables, terminal selectors, endpoint
changes, square changes, or new nonces. That isolation makes its causal price
and density effect falsifiable.
