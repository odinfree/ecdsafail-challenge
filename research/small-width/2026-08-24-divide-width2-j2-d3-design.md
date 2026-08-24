# D3 divide leading-boundary width-2 miter design

## Scope and source binding

This gate covers one promoted-family interface:

- base commit `67524171baaf568dc3dc606f38515745f70804ff`;
- base tree `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`;
- lane-B census commit `f6eaee6c83ca254b78c3aff5e5c6202b7ead3287`;
- census artifact SHA-256
  `becd6300974d990acb8c6f0cf617d7929c556f191db789dc5ff4c57adbac8adc`;
- family `DIV / leading chunk 0 / width 2 / final_carry=true` in
  `add_chunked_measured_with` and `chunk_add`.

The existing chunk ABI is binding: all four local operand bits remain
preserved as specified by the adder, and chunk 1 receives the identical carry
Boolean through `Option<QubitId>`. Cross-chunk fusion, prefix recomputation,
and repeated on-demand synthesis are outside this gate.

## Reachable-state invariant

Chunk 0 has `carry_in=None`. Because the comparison window covers the entire
two-bit chunk, the carry entering comparator bit 0 is identically zero. Lane B
recorded 21,312 admitted rows across 333 divide sites and 64 EC trajectories.
Their local support contains every one of the 16 `(addend, accumulator)` pairs,
under each argument-sign value, and every site varies in boundary output.

The census is not used to infer a universal arithmetic identity from sampling.
It is used only as a coverage certificate for the finite four-bit local domain:
all 16 assignments occur in source-admitted trajectories. The Boolean miter
then exhausts that complete domain independently.

## Proof artifact

Add one standalone red-team binary, with no production module registration or
production primitive edit. Represent every four-input Boolean function as a
16-bit truth-table mask and perform four checks:

1. Compute the exact carry-out of `addend + accumulator` with carry-in zero.
2. Apply the Möbius transform to obtain its unique algebraic normal form and
   degree.
3. Exhaust every function of the form
   `affine_0 XOR (affine_1 AND affine_2)`. A match would admit a zero/one
   nonlinear-gate boundary implementation; no match is a complete lower-bound
   certificate for that family.
4. GREEN-check the existing two-product identity on all 16 inputs:

   `p = a0 AND x0`

   `carry = p XOR ((a1 XOR p) AND (x1 XOR p))`.

The binary must print the truth mask, ANF monomials, algebraic degree, affine
and one-product search counts, current-identity mismatches, and the first RED
witness for representative zero-gate deletions.

## HMR phase sub-gate

After the value addition, the measured boundary phase must be repaired by the
same carry Boolean expressed over `(addend, sum)`. Derive that post-sum ANF and
miter it over all 16 data assignments and both measurement outcomes. Group its
degree-three part into one product of three affine forms, giving a direct
ancilla-free phase polynomial made from Clifford phases plus one CCZ-class
nonlinear phase gate.

This secondary identity may establish removal of the comparator's one
transient scratch qubit. It does not remove the boundary wire, reduce the
one-nonlinear-gate phase count, or establish a peak-qubit improvement.

## Verdict gates

Return `ADMIT` only if a candidate supplies the identical boundary bit under
the existing ABI with fewer than two nonlinear gates, or eliminates its wire
without fusion/recomputation while preserving all four data bits. Otherwise
return `HARD_NACK_EXISTING_ABI_WIDTH2` if:

- all 16 local assignments are source-covered and exhaustively checked;
- the carry has algebraic degree three;
- the zero/one-product search has no solution;
- the current two-product identity has zero mismatches;
- the phase identity has zero mismatches for all 32 data/measurement cases;
- the source ABI still requires a `QubitId` carry input for chunk 1.

The verdict says nothing about wider chunks, multiply sites, fusion,
recomputation, or alternative chunk interfaces.
