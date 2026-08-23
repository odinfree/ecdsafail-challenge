# Burn plateau re-descent from 940e34a

## Restart recovery overlay - 2026-08-23

Status: `RECOVERED_UNCOMMITTED_PROTOTYPE`; do not treat the source diff as a
measurement or candidate.

- Branch HEAD remains `464ea805356a`.
- `src/point_add/pingpong_div.rs` has an uncommitted 104-line,
  `pp_mul_walkback`-only source-carry prototype.
- No matching process is running and no durable miter, 64-lane result, full
  9,024-shot result, operation hash, or Q/T receipt was found for this diff.
- The measured Q1277/T917898.890/full `8/13/0` receipt below belongs to HEAD's
  sparse-square composition, not to the recovered uncommitted prototype.

Next falsifier: before building the complete circuit, exhaust the MAJ/UMA
cell's full Boolean domain and prove restoration of the hosted source,
accumulator, and incoming carry with phase/ancilla zero. If it passes, run the
unchanged 64-lane point-add check and complete owner census. KILL if the cut is
multiply-only at a still-tied plateau or if any cleanup channel is dirty. Do
not delete, commit, or continue the recovered source diff until its owner
chooses that gate explicitly.

Updated: 2026-08-23

## Decision

- Preserve `/work/redescent-teddy-1270` at clean commit `3370f66`; it is a
  historical re-descent whose merge-base with the live source is `897dda2`.
  Its large divergent replay rewrite was not rebased onto the leader.
- Work only in the fresh isolated branch `research/burn-plateau-940e34a`,
  created directly from exact live commit
  `940e34acbc9cdc9ac497f67eea40db80551d1f7c`.
- Keep the exact sparse-square component behind an environment gate.
- Do not hunt the composed Q1277 stream. The inherited nonce is dirty at the
  unchanged trusted 9024-shot evaluator, and this lane forbids nonce tolerance.
- No provider, spend, fleet, submission, or live-process action occurred.

## Protected baseline, freshly reproduced

| field | value |
|---|---:|
| source | `940e34acbc9cdc9ac497f67eea40db80551d1f7c` |
| emitted ops | 12,918,089 |
| ops SHA-256 | `38e4d98d2ed7c9d0c3600f631e371de54284832f7cd7657fe25698c46c062a7e` |
| ops MD5 | `2476648bade253b539b41bbc2e230b7b` |
| Q | 1278 |
| trusted average T | 917,480.917 |
| score | 1,172,540,718 |
| trusted channels | 9024 shots, `0/0/0` |

After the gated source port, a no-environment build reproduced the same op
count and both hashes byte-for-byte. The protected path is unchanged.

## Exact component retained

Gate: `SUB4_SQUARE_TEDDY_SPARSE_TRI_CORR=1`.

The square's two materialized 129-wire zero-pad layouts were replaced by
`Option<QubitId>` structural zeroes. Boundary carries are repaired with a
full-prefix comparison. No binary value register was narrowed.

Standalone 64-lane selfchecks:

| route | split | Q | emitted T | executed T | result |
|---|---:|---:|---:|---:|---|
| protected square | n/a | 1278 | 58,879 | 58,678.203 | exact |
| sparse balanced | default | 1148 | 60,693 | 59,597.625 | exact |
| sparse T-biased | 1 | 1158 | 58,787 | 58,627.875 | exact |

The split-1 route spends ten of the component's 129 qubits of global slack to
remove full-prefix comparator work. It is value-, phase-, and ancilla-clean in
the standalone check.

## Smallest measured orthogonal composition

```text
SUB4_SQUARE_TEDDY_SPARSE_TRI_CORR=1
SUB4_SQUARE_TEDDY_SPARSE_SPLIT=1
SUB4_PP_PEAK=1277
SUB4_PP_R1=342
SUB4_PP_R2=625
```

| field | value |
|---|---:|
| Q | 1277 |
| emitted ops | 12,919,618 |
| ops SHA-256 | `c7bd2c82f74e8973d153444acc8201c404a465b48ea39a96bd9afd0be63d0e64` |
| ops MD5 | `7db863eb24c57f7323d43fe87ebb2c1f` |
| deterministic-64 T, seed 0 | 917,832.17 |
| canonical total T, 9024 shots | 8,283,119,579 |
| canonical average T | 917,898.890, rounded 917,899 |
| strict Q1277 rounded-T ceiling | 918,199 |
| score if clean | 1,172,157,023, a 383,695 strict beat |
| deterministic cohorts | 16 x 64 = 1,024 shots, `0/0/0` |
| unchanged trusted evaluator | 9024 shots, `8/13/0`, DIRTY |

The composition is economically live but not valid. It is an architecture
receipt, not a candidate or hunt packet.

## Exact peak-owner plateaus

Baseline `940e34a` is three-way at Q1278:

- `pp_div_replay`: Q1278, first op 2,634,748;
- `square_product_register`: Q1278, op 6,765,206;
- `pp_mul_walkback`: Q1278, op 8,967,950;
- `pp_mul_replay`: Q1276 near-binder.

The composed stream removes the square wall but remains two-way at Q1277.

### Divide replay, op 2,542,595

```text
343  transcript/current sign wires
512  numerator plus replay coefficient
290  two 145-wire walk registers
132  exact split-walk carry and retained boundary
----
1277
```

There is no spare passenger in this equality. The split-walk boundary repair
is already exact over the whole low chunk.

### Multiply walkback, op 9,006,188

```text
556  transcript wires, including fused round-zero sign
512  numerator plus replay coefficient
112  two 56-wire walk registers
 14  reacquired terminal passenger wires required by walkback
 80  replay carry ladder plus two live boundaries
  3  doubled-out, caller remnant, and constant/shell singleton
----
1277
```

The coefficient is live at every binding replay instant and is freed in the
zero-op gap immediately after its final semantic consumer. There is no
post-consumer lifetime hole. If both Q1277 owners move, `pp_mul_replay` at
Q1276 becomes the next wall.

## Value-exact replay-boundary falsifier

Widening every replay chunk repair to its complete producer chunk with
`SUB4_PP_REPLAY_CHUNK_COMPARE=256` was tested on the same composition. It was
64-lane `0/0/0`, but expanded to Q1280, deterministic-64 T996,128.69,
14,790,856 emitted ops, SHA-256
`7115b01929eff2f9dde1df05818b273e5461c1261a3f87e48be77070543190ff`.
It fails both width and score gates and is closed.

## Next structural binder

Any continuation must lower `pp_div_replay` and `pp_mul_walkback` together,
then account for Q1276 `pp_mul_replay`. The smallest credible changed premise
is an exact carry-host transformation on the split walk paired with an exact
replay-boundary or transcript-state deletion on multiply. Releasing the
coefficient after its last use, another square-only cut, and full replay
comparators are already falsified.
