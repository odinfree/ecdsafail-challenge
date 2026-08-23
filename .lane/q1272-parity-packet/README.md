# Q1272 selector one-host Linux/CUDA parity packet

Status: `PACKET_ONLY / HOLD_HOST / HOLD_CUDA / HOLD_RANGE`

This content-addressed packet binds the Q1272 selector circuit at CPU evidence
commit `72b8a97a459344300828eb63c3a0d61fa0b6cc2b` to the uncompiled CUDA port at
`2246f4c52f35443f84e3bbaeb9a3f40dbb241161`.  It includes the exact inherited
operation artifact and nonce-independent checkpoint, complete trusted H64 and
blinded D32 fixtures, qualified CPU source, CUDA source, build commands,
byte-parity comparator, and fail-closed negatives.

The archive contains private D32 nonce and mask fixtures.  Keep it outside Git
and do not publish it.

Offline verification:

```bash
./verify_packet.sh
```

On one clean, idle Linux/CUDA host, extract the archive and run:

```bash
./run_one_host_parity.sh /workspace/ev-q1272-selector-parity 0
```

The workspace must not already exist.  The runner rebuilds the exact Linux CPU
predictor and circuit, byte-reproduces `ops.bin` and the checkpoint, compiles
the exact CUDA source with the recorded `nvcc` command, closes nine negative
guards, then compares CPU and CUDA complete masks against the trusted 64+32
fixtures.  It refuses a busy GPU before parity and requires it idle afterward.

A `PARITY.complete` receipt permits only later review of the parity result.  It
does not authorize a range, provider action, nonce hunt, phase claim,
submission, or incumbent mutation.  Every eventual candidate still requires
the unchanged full 9,024-shot evaluator with classical/phase/ancilla `0/0/0`.
