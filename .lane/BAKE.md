# Q1276 source bake receipt

The clean `b523ecf` source received exactly two numeric default changes:

- `SUB4_PP_PEAK`: `1278 -> 1276`;
- `SUB4_SQUARE_LADDER`: `248 -> 246`.

With both variables unset, a forced fresh release build emitted 12,901,678
operations at SHA-256
`d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`,
byte-identical to the predeclared env-only candidate. Compressed size is
51,641,151 bytes.

The generated operation artifact, build binary, target directory, and log
remain outside Git.
