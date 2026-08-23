# Q1273 repaired-classical plus conditional-phase predeclaration

Status: `PREDECLARED / NO RESULTS OPENED`.

This gate composes the terminal repaired classical predictor at commit
`7b339f5` with the exact source-bound conditional-phase screen sealed at commit
`031083cc`.  It does not authorize CUDA, a nonce range, a provider, a hunt, or
a submission.

## Immutable inputs

Classical side:

- source / ops identity:
  `093d85d64de87aa5006a94868172f642daacf136` /
  `12,933,805` /
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- repaired model SHA-256:
  `da56cb95e2c423e67e8d400b423117cc54d007505aa7281e7725bcadd2ea19ab`;
- final classical summary / manifest SHA-256:
  `51d9802bee64c6865b294b1e3ac7f40d6717ce258677ea7b9bbfa4a5841a413d` /
  `fa458ea4af5766df3660380943e3fc83e502d379f2cd9945c3e4c38e2f22d93c`;
- exact classical corpus: inherited + H64 + D16 + blinded D32,
  `113/113` masks and `1,594/1,594` faults.

Phase side, read only from commit `031083cc`:

- conditional contract: `clean_phase_mask = phase_mask & ~classical_mask`;
- final survivor: `classical_mask == 0 && clean_phase_mask == 0`;
- schedule header SHA-256:
  `4249864aca9e2928a33865ea086b99ef8ecccc9eb596ba4c3e57468ba88d25e5`;
- schedule ledger SHA-256:
  `a4043530337b91e97d7a42dde2aff7e5a967a0b820ad1a9a120b3c366d7a5294`;
- fixture ledger SHA-256:
  `e148f24d99ae45b3c6930a33d49173fd31b2c236593d98375956077b3feb4d1b`;
- schedule generator SHA-256:
  `83bfa142f2cf546ea5673de424597bf26ed3a57db0173d2b177a009ad9f8e966`;
- exact phase corpus: inherited + D16, `17/17` complete conditional masks,
  3,983 source events over 1,942,962 R/Hmr words.

The phase donor's old classical walk/replay implementation is explicitly not
an input and must not replace the repaired model.

## One allowed composition family

The only allowed semantic edit is a source-event-preserving phase trace graft
onto the repaired classical state machine:

1. preserve the repaired `pp_model.h` classical path byte-for-byte in behavior;
2. import the phase schedule and fixture ledger byte-for-byte from `031083cc`;
3. add phase-only arithmetic/replay trace helpers at the same four source-event
   families and in the same ordinal order;
4. for a non-overflow walk, use the already-qualified donor trace semantics;
5. for an overflow walk, continue from the repaired finite-width
   terminal-loan/walkback state, while emitting exactly the same replay,
   square, and shell source events with the circuit-equivalent comparator
   inputs and scratch-tail treatment;
6. retain the classical cause/early-return vocabulary exactly.  Phase output
   is claimed only when the repaired classical mask is zero.

No ideal full-output fallback, witness special case, oracle-derived correction,
schedule reorder, raw-phase claim on dirty shots, or looser survivor predicate
is allowed.

## Frozen gates

The combined CPU is `GO` only if all of the following pass:

1. exact source, count, ops SHA, state digest, phase schedule, and fixture
   identity, plus deterministic SHAKE256 known answers;
2. the two sealed overflow witnesses retain their exact repaired classical
   masks: nonce `730140001442`, shot `6329` is clean; nonce
   `730070000721`, shot `2493` is mask `4`;
3. all 113 complete classical masks remain byte-identical to their unchanged
   evaluator oracles, with the same 1,594 faults;
4. all 17 complete conditional-phase masks equal the independent two-pass
   oracle fixture ledger;
5. repeated inherited classical and conditional-phase outputs are byte-identical;
6. wrong magic, wrong operation count, same-count/wrong-SHA, wrong state digest,
   wrong phase schedule, missing stream, malformed/non-canonical/overflowing
   nonce, malformed shot index, unknown selector, and disabled scan mode all
   reject with empty result output;
7. ordinary classical output formatting and ordering remain unchanged.

Any classical mask difference, conditional-phase mask difference, framing
drift, or ambiguous trace count is terminal `HOLD`.  A CPU pass permits only a
separate CUDA handoff; it does not permit scanning.
