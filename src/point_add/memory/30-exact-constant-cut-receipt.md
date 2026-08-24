# Exact 22-gate constant-state cut: validation receipt

Verdict: `ADMIT_SOURCE_PROOF / HOLD_NONCE / NO_PROMOTION`

## Binding

- official parent commit/tree: `67524171baaf568dc3dc606f38515745f70804ff` / `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- materializer commit/tree: `b206ab747a3ae5a2dcc9dbc105e30c06edda327e` / `bdc8cdc1bf08e102580bbde8a7d7d3db53015618`
- baseline ops: 12,593,858, SHA-256 `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e`
- candidate ops: 12,593,836, SHA-256 `860f33891d1a42f7e1a873b44907462d1ebde6c04a7d65fce2a6a348b274a395`
- candidate source is default-off behind strict `STRUCTURAL_CUT_APPLY=1`
- exact scanner SHA-256: `868d6b4a46e3c5d6ade0723f5018114a3a1ddcbb5cb6fac06eb696d5cccc1d31`
- independent streaming verifier SHA-256: `d8e7205b72a4cb37576e19fce24ebf558feb01ef17d41b58ca0b8bbc977664b5`

## Proof

The source-integrated abstract interpreter starts only the four declared input
registers unknown and all other qubits/bits at zero. It follows every
condition, reset, HMR, swap, quantum write, and classical store using the
fail-closed lattice `{0,1,unknown}`. It proves exactly 22 CCX gates have a
quantum control fixed at zero: 14 at the hybrid-adder vent site and four each
at the constant-add and constant-subtract sites. The set includes and strictly
generalizes the independently frozen q775 witness.

The independent Python implementation replays all 12,593,858 compressed
records, asserts the exact four-register ABI and baseline hash, reproduces all
22 indices/operands, and proves the candidate equals the baseline with only
those records deleted. Its terminal receipt was:

```text
PASS sha256=87371140...d05e ops=12593858 nonlinear_identities=22 q775=true abi=frozen candidate_ops=12593836 candidate_sha256=860f3389...a395 deletion_only=true
```

With the gate disabled after the materializer landed, the rebuilt stream was
byte-identical to the official baseline hash.

## Staged validation

The exact 64-shot evaluator variant was mechanically derived from the pinned
trusted evaluator by changing only `NUM_TESTS: 9024 -> 64`; its binary SHA-256
was `8ea5c6ae7b65627ea45ed428e703b613a71bcf64f918fb20addc7fe5968828c0`.
It reported Q1267, T911312.297, and classical/phase/ancilla `0/0/0`.

The unchanged full evaluator binary SHA-256
`767ecd2975306e6be081ddb1dbae246d6b29c03b2c44ec4e10ed86a264aafe03`
then ran all 9,024 shots on the exact candidate artifact:

- Q: 1267
- average T: 911373.493
- rounded-T product: 1,154,709,591 (nominal 21,539 below the entry frontier)
- classical mismatches: 32
- phase-garbage batches: 17
- ancilla-garbage batches: 0
- first mismatch: shot 249

Correctness precedes score, so the artifact is not a candidate. The source
identity proof remains admitted; the current Fiat-Shamir draw does not.

## Controller decision

Do not spend or grind for this 22-T-only step. Carry the exact proof into the
next structural scan for nonlinear simplifications whose controls are proven
one, equal, or complementary. Provider, nonce-grind, fleet, queue, push,
public-note, and submission authority remain false.
