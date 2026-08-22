# Teddy tape representation audit

Updated: 2026-08-22T12:48Z

## Scope and live gate

- Research-only branch: `research/redescent-teddy-tape-checkpoint`.
- Exact X004 base: `0d15561e2c2985f42e7a30a9518863726f77e353`.
- Fresh protected frontier: `7ca0559911b8cd423c4acc74fe152f332fce0c63`, Q=1278, T=921558, score=1177751124.
- No nonce hunt, provider use, spend, submission, push, or public claim.
- Teddy's private doctrine was refreshed from `odinfree/burn-the-house-down` at `b6ad6381029ce4893e368b0ab677a03698eb607c` before this audit.

## Information lower bound

The raw history is 704 signs (703 allocated at `value_walk:551` plus the fused round-zero bit). The tape cannot be treated as 704 independent information bits:

1. the input denominator has fewer than 256 bits of entropy;
2. `value_walk_back` reconstructs the exact denominator from the history and the two terminal signs;
3. therefore the successful denominator map into `(history, terminal pair)` is injective;
4. because the terminal pair has at most four values, a lossless history code still needs at least `ceil(log2((p-1)/4)) = 254` bits.

So a 256-bit denominator code is within two qubits of the information floor. This bound says nothing about decoder scratch or decoder Toffoli; those are separate costs.

## Exact full-history recomputation falsifier

The pre-existing env-gated diagnostic at commit `5fa69cc` runs a complete walk-back plus re-walk before replay:

```text
SUB4_PP_TEDDY_TAPE_RECOMPUTE_CYCLE=1
```

Deterministic 64-lane full-affine measurements:

```text
baseline: Q1266 / T1036334.453 / emitted T1174483 / cls-pha-anc clean
cycle:    Q1266 / T1431657.594 / emitted T1569851 / cls-pha-anc clean
delta:    +395323.141 executed T (+38.1463%), Q unchanged
```

Before that diagnostic was committed, its diff SHA-256 was `5fe74e45828547bdf666c52b28b8a10fbf4b1a906e3bc4beb6093929dd8669bf`; the modified source SHA-256 was `1b83088ffa107674262573b48dccfc27a430e4ffc61a0e695100e93369555d41`.

Verdict: full tape erase followed by rebuilding the full tape is killed. The rebuilt tape recreates the peak and the exact tax is too large.

## Correction to the zero-cost deletion economics

Do not retain Q1266 after hypothetically deleting 703 resident tape qubits. The earlier broader kill in `.lane/TAPE-CHECKPOINT.md` used the old-Q ceiling and is not a valid product comparison.

For each clean replay-plot ablation, replacing the 703 raw tape qubits by a 256-bit code gives the following lower-bound economics before decoder scratch and decoder T:

| replay plot | measured raw Q | measured T | code-only Q (`raw Q - 703 + 256`) | code-only score | max extra decoder Q at fixed T | max extra decoder T at fixed Q |
|---:|---:|---:|---:|---:|---:|---:|
| 48 | 1266 | 1036334.453 | 819 | 848757917 | 317 | 401700.547 |
| 64 | 1286 | 999425.000 | 839 | 838517575 | 339 | 404330.000 |
| 96 | 1306 | 980761.953 | 859 | 842474518 | 341 | 390310.047 |
| 128 | 1348 | 962451.328 | 901 | 867168647 | 322 | 344707.672 |
| 256 | 1475 | 943810.000 | 1028 | 970236680 | 219 | 201862.000 |

This is a strong objective path if a decoder exists. In particular, plot 48 can tolerate at most 317 extra resident decoder qubits and about 401.7k extra executed T; the measured complete recomputation tax is just under the T allowance but rebuilding the 703-bit tape violates the Q allowance.

## Env-gated 256-bit code prototype

`SUB4_PP_TEDDY_DENOMINATOR_CODE=1` copies the exact denominator into 256 persistent qubits before the walk. It leaves the raw tape untouched, then uncomputes the code only after `restore_wire_layout` restores the denominator value and exact ABI wires. It is an information-code measurement, not a decoder claim.

Deterministic 64-lane full-affine result:

```text
Q = 1522 (exactly baseline +256)
T = 1036472.797
emitted T = 1174483 (unchanged)
classical/phase/ancilla assertions = clean
```

The executed-T difference is sampling-path noise from the altered op/allocation stream; the emitted Toffoli stream is unchanged. Default-off baseline reproduces Q1266/T1036334.453 exactly after the edit.

## Smallest joint-representation falsifier

The value walk alone loses one branch bit per round. For odd source `a` and odd post-target `z`, both predecessor candidates

```text
t0 = 2z - a, with s=0
t1 = 2z + a, with s=1
```

satisfy `s = bit1(t) XOR bit1(a)` and map to the same `z` under the corresponding signed add-and-halve. The post value state therefore cannot erase the sign locally.

Simply updating the current modular coefficient pair online does not fix the local ambiguity. If the coefficient update is

```text
C = (B + (-1)^s A) / 2 mod p,
```

then both predecessor candidates

```text
B0 = 2C - A mod p
B1 = 2C + A mod p
```

are valid. The present canonical modular coefficient state does not expose `s` as a local output predicate, so “apply current replay online, then free sign” is not reversible.

Verdict: kill the untagged online-coefficient composition. Continue only with a deliberately bijective tagged/redundant coefficient representation or another codec whose decoder schedule is proven to fit the Q/T allowances above. Code entropy and decoder scratch must remain separate columns in every follow-up measurement.
