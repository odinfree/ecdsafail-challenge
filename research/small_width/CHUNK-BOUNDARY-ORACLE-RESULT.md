# Chunk-boundary oracle result

Source: promoted `67524171baaf568dc3dc606f38515745f70804ff`.
Hypothesis origin: Justin Drake's reduced-width autoresearch proposal.

Command:

```text
python3 research/small_width/chunk_boundary_oracle.py --max-chunk-width 10
```

The exhaustive grid covered 55 `(chunk_width, top_width)` pairs and every
`(addend, accumulator, chunk_cin)` assignment for each pair.

- implicit-zero top-window repair errors across the grid: `1,396,054`;
- repair supplied with the exact window-entry carry: `0` errors;
- at chunk width 10 and top width 4: error rate `1/32`;
- at chunk width 10 and top width 8: error rate `1/512`;
- at chunk width 10 and top width 10: error rate `1/2048`.

The observed implicit-zero error rate is `2^-(top_width+1)`, including when
the comparison spans the whole chunk but omits the chunk input carry. This
confirms the Boolean mechanism and sharply defines the circuit task: retain or
recompute the carry entering the repair window without creating a worse peak
or a new phase obligation.

Status: mechanism identity verified at reduced width; reversible checkpoint
schedule and 256-bit score effect unverified. This is not a submission result.
