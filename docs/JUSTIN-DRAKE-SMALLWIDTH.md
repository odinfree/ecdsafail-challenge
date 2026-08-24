# Justin Drake reduced-width Pareto experiment

Hypothesis origin: **Justin Drake**. If this lane produces a promoted circuit
win, credit him.

## Scope

The promoted `67524171baaf568dc3dc606f38515745f70804ff` point-add route is not
mechanically width-parametric: it embeds secp256k1 constants, 256-bit types,
fixed round schedules, and absolute peak/window thresholds. The dedicated
probe therefore exercises the exact generic adder and phase-repair primitives
from that source at 32/64/96/128 bits, with 256 bits as the lift check. It does
not use the broken generic test target or claim full-circuit correctness.

The sweep records exact integer resource counts, phase-attributed peak owner,
`Q/n`, `T/n`, `T/n^2`, Pareto adjacency, plateaus, and owner migration. JSONL
rows are separated by semantic comparison scope so approximate repairs cannot
dominate exact repairs.

Boundary repair is an explicit dimension:

- `approximate_no_cin`
- `exact_whole_chunk_with_chunk_cin`
- `topW_with_window_entry_carry`

The last form is locally exact but only transferable if the real replay route
can retain or host the carry entering the top-W slice and clean it reversibly.

## Reproduce

```sh
cd /Users/olifreuler/Documents/Codex/2026-08-24/sol-smallwidth-analysis
scripts/run-smallwidth-pareto.sh artifacts/smallwidth-pareto
```

Override widths or search caps with `SMALLWIDTH_WIDTHS`,
`SMALLWIDTH_MAX_BLOCKS`, and `SMALLWIDTH_MAX_WINDOW`.

## First measured result

The completed 32/64/96/128/256 sweep emitted 1,650 resource rows. The analyzer
found 15 peak-owner migrations and 47 qubit plateaus. Across the measured
width/window grid, `topW_with_window_entry_carry` cost exactly one additional
peak qubit and zero additional emitted Toffolis relative to
`approximate_no_cin`. This is a concrete mechanism candidate, not a benchmark
win.

The two-adder co-binder micro-model exposes discrete owner changes rather than
smooth extrapolation. For example, at 32 bits the peak owner changes between
`clean_top=26` and `27` while Q plateaus; at 64 bits it changes between `56`
and `57`. These finite-width steps are exactly the features the experiment is
intended to surface before a 256-bit port.

## Promotion boundary and unfinished work

No provider, challenge submission, or protected lane was touched. Promotion
still requires:

1. integrate the entry-carry repair into the exact promoted replay path;
2. prove reversible hosting and cleanup of the retained carry;
3. perform a per-round reachable-state invariant census, especially low carry
   prefixes and top-slice equalities;
4. run the trusted full 9,024-shot evaluator and enforce a strict score beat.
