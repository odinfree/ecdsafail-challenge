# Q1274 CPU model: blinded disjoint32 qualification

Date: 2026-08-23

## Verdict

`MODEL_DISJOINT32_PASS`; `CPU_MODEL_EXACT_96_OF_96`; `GO_PARITY_PACKET`;
`HOLD_PHASE_SCREEN`; `HOLD_SCAN`; `HOLD_HUNT`; `HOLD_PROVIDER`;
`HOLD_SUBMIT`.

The circuit-exact model source and original H64 pass were committed and pushed
at `b537c63e38d38249de006a6082310a9c803c0c26` before any disjoint32 evaluator
outcome was generated.  The corrected predictor was run first.  The unchanged
trusted evaluator was then run over exactly the precommitted corpus, with only
the already-qualified shot-index and no-write flags enabled.

## Source and corpus binding

- worktree:
  `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/b523-q1274-control-predictor`;
- branch: `research/b523-q1274-control-predictor`;
- model source commit: `b537c63e38d38249de006a6082310a9c803c0c26`;
- model source SHA-256:
  `3af19302b1d655cc30f89d6ef8e65ac9029d350d71e649b35bf1e2e432a53453`;
- candidate operation count: `12,935,433`;
- canonical inherited operation SHA-256:
  `61a57ce6e167b64663288ade584785b26562f61ff197f6ae0c11c85ea098ee8e`;
- Q1274 control defaults: divide/multiply rounds `700/696`, replay fold `53`,
  B1 `30`, peak `1274`, square ladder `244`;
- disjoint32 corpus SHA-256:
  `2ffcd388696348198f2d86b0ab57dc10e365e20ca45af0c6c8e4e387276be4e1`;
- predictor nonce-list SHA-256:
  `ffeb4674f71589ba6469bb4dc69a4f1ecbe5513980cf5363007bf62ba9db7214`.

## Exact disjoint32 result

- rows: `32`;
- structural guard on every row: Q1274, 12,935,433 operations, 9,024 shots,
  ancilla zero;
- evaluator classical total: `517`;
- predictor classical total: `517`;
- evaluator phase total: `500`;
- per-nonce count equality: `32/32`;
- complete classical shot-set equality: `32/32`;
- evaluator-only shots: `0`;
- predictor-only shots: `0`;
- canonical 517-row `(nonce, shot)` set SHA-256 from both paths:
  `2ee3849fddbaaa809803019a368dba1b1f5391a9e1cd9229b4dec22649ff03f6`;
- predictor counts SHA-256:
  `5cce5c701161d03bea03a280a2c469278fc03e66db886a2c64a7ed12754135b6`;
- predictor verbose receipt SHA-256:
  `ad06371bff4cd52f7a3faa0cf68c173217755a9ff4043ee7185073da7a0c341b`;
- raw compact evaluator row receipt SHA-256:
  `ae3287fc0d1240a64eea1399c136f6c1388541283c764bef95aed2847014de98`;
- evaluator-log manifest SHA-256:
  `28dded8f2f995f2add7c46c8aad1e23f76fab221549dfb50846af4f7ede5b791`;
- per-nonce operation manifest SHA-256:
  `a42c807a9861e59f31ed2a4edbdcd0bc62ecf485d73c31b5ad39cb5a361eda6d`;
- committed 32-fixture ledger SHA-256:
  `5f9ff437e1ed05bedbb5ffff67300e39b8c11e787f7ad17bc753d969f8927c46`.

Together with the original H64 closure, the CPU model has exact complete-set
equality across 96/96 nonces and 1,549/1,549 classical mismatch shots.

## Trusted harness boundary

- restored evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- temporary shot-index/no-write evaluator binary SHA-256:
  `5f034f9da5295532114210b93578f62e31cf85701cf3f200919831fcc06c7aa9`;
- builder binary SHA-256:
  `c9dd06d538072e58fb665b1165c32b9829af6e2e8b10298f295ebd38f4ed2084`;
- tracked `results.tsv` SHA-256 before and after:
  `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

The first local evaluator invocation omitted the two instrumentation flags and
therefore exposed no shot indices and appended one self-authored result row.
That row was removed, the tracked file was restored to the exact pre-run SHA,
and the same operation stream was rerun with `EVAL_CLASSICAL_SHOTS=1` and
`EVAL_NO_WRITE=1` before it entered the authoritative receipt.  No evaluator
source edit or semantic change occurred during this corpus.

## Frozen parity packet and negatives

`.lane/prefilter-fixtures.tsv` freezes all 32 disjoint nonces, expected
classical counts, exact per-nonce mask hashes, observed trusted phase counts,
and ancilla zero.  Linux CPU, CUDA comb8, and CUDA comb16 must reproduce every
full 9,024-bit classical mask, not only its popcount.

Fail closed before executing a fixture when any source, operation, checkpoint,
model, or fixture digest differs.  The negative packet must include:

1. wrong-count protected b523: 12,876,472 operations, canonical SHA
   `4cb1787b181417c1e180ddf362fd7e44430ef2d422bb4184d73d7fe1924fdf7e`;
2. same-count/wrong-SHA stream: the first disjoint fixture has 12,935,433
   operations but SHA
   `d7d89317ff9900ea1800a40793c362a9b3e9122198d55edf0b7558711f638a87`,
   which must be rejected wherever the canonical inherited stream SHA is
   required;
3. fixture-ledger digest tamper: one changed mask nibble with unchanged count,
   which must be rejected before CPU/CUDA comparison.

This packet authorizes isolated Linux/CUDA build and parity only.  It does not
authorize a range, scan, hunt, provider action, phase-based rejection,
submission, or incumbent mutation.  Final candidates still require the
unchanged full 9,024-shot evaluator with classical/phase/ancilla `0/0/0`.

