# Q1272 selector: immutable one-host Linux/CUDA parity packet

Date: 2026-08-23

## Verdict

`PACKET_READY`; `OFFLINE_VERIFIED`; `GO_PACKET_HANDOFF`; `HOLD_HOST`;
`HOLD_CUDA_EXECUTION`; `HOLD_RANGE`; `HOLD_HUNT`; `HOLD_PROVIDER`;
`HOLD_SUBMIT`.

The content-addressed one-host parity packet is assembled and verified.  It
contains the exact CPU and CUDA sources, inherited operation artifact,
deterministic checkpoint, private H64+D32 nonce and mask fixtures, build and
parity runners, byte-mask comparator, and fail-closed negatives.  No host,
provider, GPU, or range was contacted or launched.

## Packet receipt

```text
packet directory
/Users/olifreuler/ecdsa-ops/q1272-selector-parity-packet-72b8a97-v2

archive
/Users/olifreuler/ecdsa-ops/q1272-selector-parity-packet-72b8a97-v2.tar.gz

archive checksum sidecar
/Users/olifreuler/ecdsa-ops/q1272-selector-parity-packet-72b8a97-v2.tar.gz.sha256

archive SHA-256
9551a1c35f77c90445aa559d458245571a9f11590d4c0aea85587b3548450794

internal MANIFEST.sha256 SHA-256
1e28adf2a205fe04e4875e5a42693c4a89fc697fff4483bb220fef7ef5919377

archive bytes
51077126

manifested files
27
```

The packet directory, files, archive, and checksum sidecar are owner-only and
write-protected.  A clean extraction independently passed `verify_packet.sh`
with:

```text
Q1272_SELECTOR_PARITY_PACKET_OK rows=96 cpu_faults=2202 checkpoint=0dbd37238642df839b7672e25a85d2d5183c202102f80388de749feaecf1c361
```

Changing the extracted `PACKET.meta` made manifest verification exit 1.  The
exact GPU wrapper rejected a same-count wrong-state checkpoint at exit 65
before invoking its supplied executable.  The archive itself remained
unchanged after both tests.

## Frozen source and artifact identities

```text
CPU evidence commit          72b8a97a459344300828eb63c3a0d61fa0b6cc2b
CUDA source commit           2246f4c52f35443f84e3bbaeb9a3f40dbb241161
circuit source commit        14608572e84daf89397768c43ac0d812c714c3bd
circuit source tree          d56979a2d5b4ac32bb429dd5858211d3bb7eb196
CPU source archive SHA-256   aae3656040eb665b953c94b8ebe746af9ac3e9d9b8e4b9b258d5d9a61cea2960
CUDA source archive SHA-256  a13ab24661cb1ec1669312c5434f132f6d8d011fc14762ede7f6369babf81e4b
CPU predictor source SHA-256 b2a4d44c89b5340c7cc7d2db8a11b8cebc9207537a0f6883445d9dd85799e9b4
CUDA source SHA-256          9f9f9c24539257a1e517323b2857798a7aedaee5e37aa3eb1c738f9c28d84c45
operation count              12908488
ops.bin SHA-256              678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0
checkpoint bytes             5064
checkpoint residual bytes    130
checkpoint SHA-256           0dbd37238642df839b7672e25a85d2d5183c202102f80388de749feaecf1c361
```

The checkpoint was generated twice locally from the qualified CPU binary and
the exact Q1272 selector environment; both copies were byte-identical.  The
packet verifier parses the binary headers and requires both the operation and
checkpoint counts to equal 12,908,488.

## Private fixture binding

The archive contains the raw fixtures below.  They remain outside Git and
must not be published.

```text
H64 nonce list SHA-256       17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9
H64 expected masks SHA-256   f5ffc40cdefc69fabccc41cef7466eaeeecad8bcbbe39e003c31613a8c2b367a
H64 evaluator masks SHA-256  f36d0e85ac70a21f32822b70971fa6ca53ad9cdfe7bf57e90b1c18e8f6d7a6af
D32 nonce list SHA-256       ae6be39a5193eee86c96485a0bcdc8caec46782f2eb8697bff1d97f9e331bab2
D32 expected masks SHA-256   dd1296442729e24ab586b730a266e03141dbf0ed8cfa5ebc38c14c94c40133f3
D32 evaluator masks SHA-256  1542b90568e1ee048b62dec5b8e4a2d344ead81ecee8a02ec4ef2ee7869c5e21
```

The offline comparator reconfirmed 64/64 H64 masks with 1,457 faults and
32/32 blinded D32 masks with 745 faults.  It rejects malformed rows, duplicate
nonces or shots, count/popcount disagreement, missing rows, and any bit
difference.

## One-host gate encoded in the packet

`run_one_host_parity.sh` requires a new isolated workspace and performs this
fixed sequence:

1. verify every packet file through `MANIFEST.sha256`;
2. extract the exact source archives;
3. compile Linux `build_circuit` and `pingpong_filter` with Cargo `--locked`;
4. byte-reproduce the supplied `ops.bin` and checkpoint;
5. compile the exact CUDA source with
   `nvcc -O3 -std=c++17 -lineinfo -arch=native -Xptxas=-v`;
6. close nine wrong-checkpoint, wrong-count, bad-magic, short-checkpoint,
   unsafe-override, and screen-plus-mask negatives;
7. require an idle GPU, run the CUDA selftest, and compare complete CPU/CUDA
   masks against all 64+32 trusted fixtures; and
8. require the GPU idle again and emit `PARITY.complete` only after byte
   equality and trusted-mask equality.

The exact wrapper pins the checkpoint hash and operation count and rejects
`--allow-op-mismatch` and incomplete `--screen` mode.  All host outputs and
binaries stay in the new workspace, not the packet.

## Activation boundary

This receipt proves only that the packet is complete, immutable, and locally
verifiable.  CUDA source `2246f4c` remains uncompiled and unexecuted.  A parent
decision is required before using even an existing paid host.  Passing future
parity would still leave phase confirmation, scan economics, range ownership,
provider, hunt, submission, and incumbent mutation behind separate gates.
