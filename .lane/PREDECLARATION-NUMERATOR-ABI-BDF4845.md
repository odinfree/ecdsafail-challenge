# Predeclaration — nonzero-numerator ABI-closure audit (bdf4845 lane)

Written: 2026-08-23, before any semantic source edit.

## What is being audited

`KILL_LIVE_NUMERATOR_ABI_CLOSURE`, recorded on the `9805dee` line at commit
`34c1b50` (lane parent `90a2175`). On the nonzero-numerator stress corpus the
production-prefix miter reports complete-reverse-cleanup failure for BOTH the
candidate AND the unchanged reference: candidate final classical/phase/ancilla
`1688/2351/0`, reference `1688/2025/0`. Because the *reference* (built as an
independent forward-then-exact-reverse walk) also fails, the recorded verdict
notes the stress "cannot isolate a low-five defect."

## Correct framing (corrects the prior lane note)

A gate-level `G ∘ G⁻¹` circuit restores its input for EVERY input, in-domain or
not: out-of-domain values may produce garbage at the midpoint but must still
close at the end. Therefore "the nonzero corpus is outside the replay's valid
domain" cannot by itself explain a *closure* failure. The failure can only mean
that some forward/reverse cell is **not an exact gate-level inverse**, and the
all-zero seed hides it (zero is a fixed point of the defective cell). The
identical classical count (1688 for candidate and reference) points at a
primitive the two paths SHARE, not at the retained-word decoder.

## Corpus (exact, deterministic)

- Per-pair unit probe: for each forward/inverse primitive pair, seed a single
  N=256 target register (and source register where the cell reads a source) with
  a fixed deterministic set of nonzero values reduced mod p:
  `{1, p-1, 2, (p-1)/2, p>>1, 0x5555…, 0xAAAA…, SHAKE256("numerator-abi-probe")
  mod p}` plus the zero control. Source register (for two-operand cells) seeded
  from the same list rotated by one so source != target.
- Check per pair, per seed: register restored to input, all ancilla = 0, phase
  = 0, forward∘inverse op count balanced.
- Round-3 component retest: reuse the existing 4,096-denominator census
  (512 low nine-bit residues × 8 high prefixes) but seed the replay `x`/`y`
  registers with a nonzero numerator midpoint value the forward walk actually
  produces, then require the forward-then-reverse replay to close.

## Kill gates (any one ⇒ that pair/component is the defect)

1. `mod_halve_pm` (pingpong_div.rs:1876) / `mod_double_pm` (1897) not mutually
   inverse on some [0,p) seed.
2. `seed_round_one` (1917) / `seed_round_one_inverse` (1926) not mutually
   inverse.
3. `signed_mod_add_pm_halve_fused` (1655) / `X;signed_mod_double_add_pm_fused
   (1745);X` not mutually inverse.
4. `retained_normalization_toggle` (2962) not an involution on a general
   (non-`{0,p}`) value.
5. If all four pairs are exact inverses, the defect is in the walk
   (`walk_round`/`walk_back_round`/`finish_bounded_production_walk`) — a larger
   repair to be scoped, not attempted blind.

Sanity anchor: a correct localization should reproduce a per-lane failure
fraction near 1688/4096 ≈ 41% on the stress corpus.

## What counts as a legitimate repair

The smallest gate-level fix to whichever pair is not an exact inverse, verified
by the unit probe returning restored/0/0 on every seed AND the round-3 census
closing at the nonzero midpoint. A repair that merely narrows the corpus to make
the receipt green is FORBIDDEN unless the primitive is shown to be
domain-restricted *by specification*, in which case the receipt must name the
proven domain and state that it is not production closure for arbitrary
numerators.

## Outcome (filled in after the run)

Gate 3 FIRED; gates 1/2/4 clean; gate 5 not reached. The defect is the shared
fused cell pair `signed_mod_add_pm_halve_fused` /
`signed_mod_double_add_pm_fused` (incomplete modular reduction → `value + p`
representative off the production trajectory), not a harness assumption and not a
retained-word cell. The reserved gate-level repair was therefore NOT taken (it
would enlarge a tuned production primitive, not fix "the smallest incorrect
assumption"), and the splice gate does not open. Full receipts and the next
overturn: `FALSIFIER-NUMERATOR-ABI-BDF4845.md`.

## Guardrails

- Env-gated only; the normal `build()` path stays byte-identical (verify a fresh
  `ops.bin` SHA256 against the protected baseline; do not commit `ops.bin`,
  `target/`, logs, or `results.tsv` rows).
- The flagged soft spot in `ROUND3-RETAINED-WORD-BDF4845.md` (the final
  `expected_x` `{0,p}` branch keyed on `denominator.bit(2)` vs the sign-1 oracle
  ANF terms `[0,4]`) is derived for the zero-seed regime and must be re-derived,
  not reused, for any nonzero midpoint.
- Research-only: no providers, hosts, ranges, hunts, submissions, or notes.
