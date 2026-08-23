# Activation gate

Current verdict: **TERMINAL SUPERSEDED**. The packet remained local and
range-unclaimed. No compute was activated. Do not create an authorization for
this source; the numbered list below is preserved only as the historical gate
that never opened.

Root may create a separate authorization only after all of these are fresh:

1. Reopen ECDSA.fail and bind the current promoted source and score.
2. Recompute `floor((live_score - 1) / 1272)` and require it to be at least
   914,728. Apply the resulting lower ceiling if it is below 914,961.
3. Confirm source `14608572...` at the exact operation and checkpoint hashes.
4. Pass the parent 96/96 Linux CPU/CUDA/trusted complete-mask packet.
5. Pass `audit_pilot.sh`: 714 files, 100/100 chunks, 5,000,000 rows, zero
   survivors, no extension or submission authorization.
6. Pass `verify_packet.sh` and `selftest_failclosed.sh` from the sealed tree.
7. Refresh Vast and RunPod billing; remain below the $500 rolling-24h cap with
   teardown headroom.
8. Assign exactly one retained host to each reviewed slot in `SHARDS.tsv`.
   Host IDs and rates must live in the separate private authorization, not in
   this packet.
9. On every assigned host, byte-rebuild and re-pass exact parity and negatives
   before the slot can become declared.
10. Checkpoint a chunk only after every classical-zero survivor has a terminal
    unchanged 9,024-shot receipt. Require classical/phase/ancilla `0/0/0` and
    the fresh score ceiling for candidacy.

The authorization must bind the packet manifest, live-frontier receipt, exact
host-slot map, spend receipt, and one fixed wave interval. It must state
`auto_extension=no`, `submission_authorized=no`, and fail closed on any missing
receipt, drift, provider fault, or frontier movement.
