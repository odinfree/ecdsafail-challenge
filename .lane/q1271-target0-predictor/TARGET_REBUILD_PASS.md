# Q1271 target0/sign-alias target rebuild receipt

Verdict: `PASS_BYTE_EXACT / TRUSTED_FULL_REPRODUCED / MODEL_UNRUN`.

After predeclaration commit
`9ec3c60f7b40eb85eddef7a2d26e9ba042d00392`, the exact source was rebuilt
under only the six frozen candidate controls plus inherited nonce
`65700024945645`.

## Bound identities

- source/evidence commit / tree:
  `a22090374a957d29a3331d6c876ad12ff45fea31` /
  `018eb52de8ab3e6337864338683821c0cbb574a2`;
- `pingpong_div.rs` / `mod.rs` SHA-256:
  `943267f11183a8f028530a0be2cebb68dd39bfbd78b4a7df52d14be50b68efa0` /
  `147d6a8f0ea029b254f97bf7b50d22064114004ad6d96b06fc0fccc159740796`;
- build binary SHA-256:
  `e2ecc14646bf075a2916cbe53dd481e11311225e89edd6b7522977277c7ed8b2`;
- unchanged trusted evaluator SHA-256:
  `a3685fc54253d6b477369a5fc6cd95760a44d226e50fe380370cf6387e401982`.

## Exact operation artifact

- magic: `QECCOPSZ`;
- declared/emitted operations: `12,919,161 / 12,919,161`;
- compressed bytes: `50,812,097`;
- uncompressed bytes reported by builder: `723,473,032`;
- SHA-256:
  `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa`;
- external immutable working copy:
  `/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d/target/ops.bin`.

## Unchanged full evaluator

The unchanged evaluator consumed all 9,024 shots and reproduced:

- Q / classical bits: `1271 / 958603`;
- exact average T / Clifford: `915142.533 / 10717964.878`;
- classical / raw phase / ancilla: `11 / 10 / 0`;
- first classical mismatch: shot `384`;
- generated result-ledger SHA-256 before restoration:
  `92ccab7b6359a2b68e294c1f65508916e3dffff31651d3c540df389211b69994`.

This expected nonzero result is the inherited dirty-channel witness, not an
abort.  No predictor output was generated.  Next is source-bound trace,
checkpoint, and trusted inherited/H64 complete-mask generation.
