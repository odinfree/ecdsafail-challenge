# Kimi burn lane state

- Protected source: `bdf4845`, branch `research/kimi-burn-bdf4845`.
- Objective: independent tape/decoder re-descent from the promoted Q1278 baseline.
- 2026-08-23 live availability probe: `kimi-code/k3` returned the provider's billing-cycle usage-limit response before model execution. No tools ran and no source, fleet, submission, or provider state changed.
- The lane is preserved cleanly. Retry K3 after the next quota refresh; do not substitute a different model while claiming Kimi attribution.
- Until Kimi is callable, the independent Claude Fable lane continues the tape/decoder overturn and local lanes continue exact structural work.
