# Q1273 predictor wrong-state negative

Verdict: `WRONG_STATE_REJECTED / H64_1_OF_64`.

This closes the remaining predeclared loader negative before the remaining 63
H64 fixtures are opened. The first fixed H64 nonce, `444000000000`, was used
as an independently generated, valid same-count stream whose changed nonce tail
must not be accepted as the predictor base image.

## Fixture and temporary loader

- candidate operation count: `12,933,805`;
- candidate operation SHA-256:
  `6d7f35a288b2392766e2b87d4727eac08ed031f51182dcfc2260bdafb75670e6`;
- candidate evaluator geometry: Q1273 / 9,024 shots / zero ancilla-garbage
  batches;
- candidate complete evaluator/predictor classical masks were equal, but that
  outcome is not used to alter the frozen model.

An external negative-test build changed only the loader's expected whole-file
SHA from the inherited stream SHA to the fixture SHA above. The expected
checkpoint/tail-state digest remained frozen at `2148e09f4c4293b2`; model
arithmetic, geometry, and the CPU driver remained byte-identical.

- temporary `pp_host.h` SHA-256:
  `328436fe47ac46d4426668dbba149053cc8dacfc2ec8b6d6be437d7774f45a0f`;
- unchanged `pp_model.h` SHA-256:
  `8e97b9b94d313e05bbe7fb844a53381b17c9c3fbd027a744feb41edaa993976d`;
- unchanged `ppcpu.cpp` SHA-256:
  `0fde4f34365e352b272e138d450d9321fff9a1366d38fbd7213dda35b58fa4a8`;
- temporary binary SHA-256:
  `757380f0f84fa3c1688d4381911d490f03ded0e484f6b7e85da96a1cd97e74ea`.

The temporary binary accepted the exact count and full-file SHA, derived state
digest `e789219d19b46092`, rejected it against expected digest
`2148e09f4c4293b2`, and exited 2 before model execution. Stderr SHA-256:
`bd706e4279358b73931cdff990647505a433d9cf4295adcd5eda6427eab2db74`.
Stdout was empty, SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

All four loader/authority negatives are now closed: wrong count, wrong SHA,
wrong state, and unavailable scan mode. Proceed with the remaining frozen H64
fixtures without any model edit.
