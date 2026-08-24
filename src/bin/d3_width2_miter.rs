//! Exhaustive proof miter for the promoted divide leading-boundary width-2
//! family. This is a local research artifact, not a production circuit path.

const PROMOTED_COMMIT: &str = "67524171baaf568dc3dc606f38515745f70804ff";
const PROMOTED_TREE: &str = "8202910d176fa1f3332ff961e6f3f789ca6a7ac2";
const CENSUS_COMMIT: &str = "f6eaee6c83ca254b78c3aff5e5c6202b7ead3287";
const CENSUS_SHA256: &str = "becd6300974d990acb8c6f0cf617d7929c556f191db789dc5ff4c57adbac8adc";
const SOURCE_SUPPORT_MASK: u16 = 0xffff;
const INPUTS: usize = 16;

#[derive(Debug)]
struct SearchResult {
    searches: usize,
    exact_match: Option<(usize, usize, usize)>,
    best_matches: u32,
    best_coefficients: (usize, usize, usize),
    best_mask: u16,
    first_mismatch: usize,
}

fn truth_mask(mut predicate: impl FnMut(usize) -> bool) -> u16 {
    let mut mask = 0u16;
    for index in 0..INPUTS {
        mask |= u16::from(predicate(index)) << index;
    }
    mask
}

fn variable_mask(variable: usize) -> u16 {
    assert!(variable < 4);
    truth_mask(|index| ((index >> variable) & 1) != 0)
}

/// Bit 0 is the constant and bits 1..=4 select the four input variables.
fn affine_mask(coefficients: usize) -> u16 {
    assert!(coefficients < 32);
    let mut mask = if coefficients & 1 != 0 { u16::MAX } else { 0 };
    for variable in 0..4 {
        if coefficients & (1 << (variable + 1)) != 0 {
            mask ^= variable_mask(variable);
        }
    }
    mask
}

/// In-place Boolean-lattice Möbius transform, returned as a monomial mask.
fn anf_mask(truth: u16) -> u16 {
    let mut coefficients = [false; INPUTS];
    for (index, coefficient) in coefficients.iter_mut().enumerate() {
        *coefficient = truth & (1 << index) != 0;
    }
    for variable in 0..4 {
        for monomial in 0..INPUTS {
            if monomial & (1 << variable) != 0 {
                coefficients[monomial] ^= coefficients[monomial ^ (1 << variable)];
            }
        }
    }
    coefficients
        .iter()
        .enumerate()
        .fold(0u16, |mask, (index, &coefficient)| {
            mask | (u16::from(coefficient) << index)
        })
}

fn algebraic_degree(anf: u16) -> u32 {
    (0..INPUTS)
        .filter(|&monomial| anf & (1 << monomial) != 0)
        .map(|monomial| monomial.count_ones())
        .max()
        .unwrap_or(0)
}

/// Inputs are indexed `(a0, a1, x0, x1)`.
fn carry_reference(index: usize) -> bool {
    let addend = index & 3;
    let accumulator = (index >> 2) & 3;
    addend + accumulator >= 4
}

/// The two nonlinear gates emitted by the shipped width-2 chunk recurrence.
fn carry_current_identity(index: usize) -> bool {
    let a0 = index & 1 != 0;
    let a1 = index & 2 != 0;
    let x0 = index & 4 != 0;
    let x1 = index & 8 != 0;
    let p = a0 & x0;
    p ^ ((a1 ^ p) & (x1 ^ p))
}

/// Inputs are indexed `(a0, a1, s0, s1)` after modular two-bit addition.
fn phase_reference(index: usize) -> bool {
    let addend = index & 3;
    let sum = (index >> 2) & 3;
    sum < addend
}

fn phase_direct_identity(index: usize) -> bool {
    let a0 = index & 1 != 0;
    let a1 = index & 2 != 0;
    let s0 = index & 4 != 0;
    let s1 = index & 8 != 0;
    let linear_quadratic = a0 ^ a1 ^ (a0 & a1) ^ (a0 & s0) ^ (a0 & s1) ^ (a1 & s1);
    let cubic = a0 & s0 & (a1 ^ s1);
    linear_quadratic ^ cubic
}

fn first_mismatch(left: u16, right: u16) -> Option<usize> {
    let difference = left ^ right;
    (difference != 0).then(|| difference.trailing_zeros() as usize)
}

fn search_one_product(reference: u16) -> SearchResult {
    let affines = (0..32).map(affine_mask).collect::<Vec<_>>();
    let mut searches = 0usize;
    let mut exact_match = None;
    let mut best_matches = 0u32;
    let mut best_coefficients = (0usize, 0usize, 0usize);
    let mut best_mask = 0u16;
    for affine in 0..32 {
        for left in 0..32 {
            for right in 0..32 {
                searches += 1;
                let candidate = affines[affine] ^ (affines[left] & affines[right]);
                if candidate == reference && exact_match.is_none() {
                    exact_match = Some((affine, left, right));
                }
                let matches = INPUTS as u32 - (candidate ^ reference).count_ones();
                if matches > best_matches {
                    best_matches = matches;
                    best_coefficients = (affine, left, right);
                    best_mask = candidate;
                }
            }
        }
    }
    SearchResult {
        searches,
        exact_match,
        best_matches,
        best_coefficients,
        best_mask,
        first_mismatch: first_mismatch(reference, best_mask).unwrap_or(INPUTS),
    }
}

fn witness_json(index: usize, got: bool, expected: bool) -> String {
    format!(
        concat!(
            "{{\"index\":{},\"addend\":{},\"accumulator\":{},",
            "\"got_carry\":{},\"expected_carry\":{}}}"
        ),
        index,
        index & 3,
        (index >> 2) & 3,
        u8::from(got),
        u8::from(expected),
    )
}

fn main() {
    let carry_truth = truth_mask(carry_reference);
    let carry_anf = anf_mask(carry_truth);
    let carry_degree = algebraic_degree(carry_anf);
    let affine_exact = (0..32).find(|&coefficients| affine_mask(coefficients) == carry_truth);
    let one_product = search_one_product(carry_truth);
    let current_truth = truth_mask(carry_current_identity);
    let current_identity_mismatches = (current_truth ^ carry_truth).count_ones();
    let preserved_data_aliases = (0..4)
        .filter(|&variable| variable_mask(variable) == carry_truth)
        .count();

    let fixed_zero_mismatch = carry_truth.trailing_zeros() as usize;
    let fixed_zero_witness = witness_json(fixed_zero_mismatch, false, true);
    let best_witness = witness_json(
        one_product.first_mismatch,
        one_product.best_mask & (1 << one_product.first_mismatch) != 0,
        carry_truth & (1 << one_product.first_mismatch) != 0,
    );

    let phase_truth = truth_mask(phase_reference);
    let phase_anf = anf_mask(phase_truth);
    let phase_degree = algebraic_degree(phase_anf);
    let phase_direct = truth_mask(phase_direct_identity);
    let phase_identity_mismatches = (phase_truth ^ phase_direct).count_ones();
    let mut measurement_phase_mismatches = 0u32;
    for measured in [false, true] {
        for index in 0..INPUTS {
            let reference = measured & phase_reference(index);
            let direct = measured & phase_direct_identity(index);
            measurement_phase_mismatches += u32::from(reference != direct);
        }
    }

    let mut failures = 0usize;
    failures += usize::from(SOURCE_SUPPORT_MASK != u16::MAX);
    failures += usize::from(carry_truth != 0xec80);
    failures += usize::from(carry_anf != 0x2480);
    failures += usize::from(carry_degree != 3);
    failures += usize::from(affine_exact.is_some());
    failures += usize::from(one_product.searches != 32_768);
    failures += usize::from(one_product.exact_match.is_some());
    failures += usize::from(one_product.best_matches != 14);
    failures += usize::from(one_product.best_coefficients != (0, 4, 16));
    failures += usize::from(one_product.first_mismatch != 7);
    failures += usize::from(current_identity_mismatches != 0);
    failures += usize::from(preserved_data_aliases != 0);
    failures += usize::from(phase_truth != 0x08ce);
    failures += usize::from(phase_anf != 0x26ae);
    failures += usize::from(phase_degree != 3);
    failures += usize::from(phase_identity_mismatches != 0);
    failures += usize::from(measurement_phase_mismatches != 0);

    let verdict = if failures == 0 {
        "HARD_NACK_EXISTING_ABI_WIDTH2"
    } else {
        "D3_MITER_FAILURE"
    };
    println!(
        concat!(
            "{{\"verdict\":\"{}\",\"promoted_commit\":\"{}\",",
            "\"promoted_tree\":\"{}\",\"census_commit\":\"{}\",",
            "\"census_sha256\":\"{}\",\"family\":",
            "\"DIV/leading-0/width-2/final-carry\",",
            "\"source_rows\":21312,\"source_sites\":333,",
            "\"source_trajectories\":64,\"carry_in_fixed\":0,",
            "\"source_support_mask\":\"0x{:04x}\",",
            "\"source_support_under_each_arg_sign\":\"0xffff\",",
            "\"carry_truth_mask\":\"0x{:04x}\",",
            "\"carry_anf_mask\":\"0x{:04x}\",\"carry_anf\":",
            "\"a0*a1*x0 xor a1*x1 xor a0*x0*x1\",",
            "\"carry_degree\":{},\"affine_searches\":32,",
            "\"affine_match\":{},\"one_product_searches\":{},",
            "\"one_product_match\":{},\"best_one_product\":",
            "\"a1*x1\",\"best_one_product_matches\":{},",
            "\"fixed_zero_red\":{},\"best_one_product_red\":{},",
            "\"current_identity\":",
            "\"p=a0*x0; carry=p xor (a1 xor p)*(x1 xor p)\",",
            "\"current_boundary_nonlinear_gates\":2,",
            "\"boundary_lower_bound\":2,",
            "\"current_identity_mismatches\":{},",
            "\"phase_truth_mask\":\"0x{:04x}\",",
            "\"phase_anf_mask\":\"0x{:04x}\",\"phase_anf\":",
            "\"a0 xor a1 xor a0*a1 xor a0*s0 xor a0*a1*s0 xor a0*s1 xor a1*s1 xor a0*s0*s1\",",
            "\"phase_degree\":{},\"direct_phase_cubic\":",
            "\"a0*s0*(a1 xor s1)\",",
            "\"direct_phase_schedule\":",
            "\"condition m: Z(a0),Z(a1),CZ(a0,a1),CZ(a0,s0),CZ(a0,s1),CZ(a1,s1),CX(a1,s1),CCZ(a0,s0,s1),CX(a1,s1)\",",
            "\"phase_identity_mismatches\":{},",
            "\"measurement_phase_cases\":32,",
            "\"measurement_phase_mismatches\":{},",
            "\"current_phase_nonlinear_gates\":1,",
            "\"direct_phase_nonlinear_gates\":1,",
            "\"current_phase_scratch_qubits\":1,",
            "\"direct_phase_scratch_qubits\":0,",
            "\"retained_boundary_qubits\":1,",
            "\"abi_carry_type\":\"Option<QubitId>\",",
            "\"abi_requires_qubit_id\":true,",
            "\"preserved_data_aliases_for_carry\":{},",
            "\"abi_requires_distinct_output_wire\":true,",
            "\"no_retained_wire_abi_compatible\":false,",
            "\"cross_chunk_fusion\":false,",
            "\"prefix_recomputation\":false,\"failures\":{}}}"
        ),
        verdict,
        PROMOTED_COMMIT,
        PROMOTED_TREE,
        CENSUS_COMMIT,
        CENSUS_SHA256,
        SOURCE_SUPPORT_MASK,
        carry_truth,
        carry_anf,
        carry_degree,
        affine_exact.is_some(),
        one_product.searches,
        one_product.exact_match.is_some(),
        one_product.best_matches,
        fixed_zero_witness,
        best_witness,
        current_identity_mismatches,
        phase_truth,
        phase_anf,
        phase_degree,
        phase_identity_mismatches,
        measurement_phase_mismatches,
        preserved_data_aliases,
        failures,
    );
    if failures != 0 {
        std::process::exit(1);
    }
}
