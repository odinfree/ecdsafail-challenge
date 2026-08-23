# Q1273 repaired-classical plus conditional-phase qualification

Verdict: `GO_CPU_COMBINED / CUDA_HANDOFF_READY`.

The exact conditional-phase trace from phase commit `031083cc` has been
composed with the repaired finite-width Q1273 classical state machine.  The
combined CPU preserves every qualified classical shot set and reproduces every
sealed conditional-phase shot set.

## Source bind

- structural source: `093d85d64de87aa5006a94868172f642daacf136`;
- operation count / SHA-256: `12,933,805` /
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- checkpoint digest: `2148e09f4c4293b2`;
- combined model / host / CPU SHA-256:
  `14fc9230b55d2b2a84721e50d860933764a18d1357ad30331e5999280f764261` /
  `bc2df2182beb8ebcc103a3fc498a8ca65911bf52439566dbfa1284e88407f98a` /
  `1d93d46803670324401443ed9f625ee641c6fa8ef77ba4a920baebff83ea24ce`;
- qualified local binary SHA-256:
  `2234a6cfc61dfb996fdfe757b506dcc5a4917662477cbcdc7894659ce6c098c7`;
- deterministic composition tool SHA-256:
  `2c0710e0d279bbfbd1424f2cd48f57b661686352238697a7552e0c6ad756d01a`;
- terminal qualification script SHA-256:
  `189d4e8d9f1333ff5d89264d6b3080a5a91e91a33ca0f8db4532365149446248`.

The composition tool binds the repaired input, phase donor, merge base, and
automatic-merge hashes before writing.  It imports the exact phase schedule,
header, generator, and fixtures from `031083cc`.  The donor's older classical
walk implementation is excluded.  Overflow shots continue through the
repaired terminal-loan/walkback register state while retaining the donor's
source-event ordering and comparator inputs.

## Terminal gates

Classical complete-set equality after composition:

| corpus | exact rows | classical faults |
| --- | ---: | ---: |
| inherited | 1/1 | 12 |
| H64 | 64/64 | 870 |
| D16 | 16/16 | 232 |
| blinded D32 | 32/32 | 480 |
| total | 113/113 | 1,594 |

Conditional-phase complete-set equality is `17/17`, with 87 clean-phase
faults across inherited plus D16.  The contract remains exactly
`clean_phase_mask = phase_mask & ~classical_mask`; raw phase on classically
dirty shots is not claimed.

Both blinded overflow witnesses retain the repaired result:

- nonce `730140001442`, shot `6329`: classical mask `0`;
- nonce `730070000721`, shot `2493`: classical mask `4`.

Inherited classical and phase outputs repeat byte-for-byte.  All 17 negative
cases reject with empty result output: wrong magic, count, SHA, state, phase
schedule, or missing stream; scan and unknown selectors; seven malformed or
out-of-range nonces; and two bad shot indices.  SHAKE256 known answers and
deterministic schedule regeneration also pass.

## Receipts

- classical rows SHA-256:
  `f9a62209e64784728a6d8e392271f5c9d859af76ca3cb7ee160a5c9c6a0d01ea`;
- phase rows SHA-256:
  `338483aeb5ef23fb052d7cac58be3859f1ce9297b6cd1016d34c46e9a6fa3d91`;
- negative rows SHA-256:
  `8d3f618969a114dc3fc82afdf71a3380cbc5f84f9e62c67b0c377a457e714a82`;
- immutable artifact manifest SHA-256:
  `c1088ca0e3bf0d9215f63b6823bf490d408ba46e2cf3271d35c40b449d5fe847`;
- artifact root:
  `/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/combined-cpu/`.

No CUDA build, GPU, provider, range, hunt, or submission was used.  CPU GO
permits only a separately guarded CUDA transport and fixture-parity gate.
