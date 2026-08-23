// Fixed-corpus CUDA parity unit for the repaired Q1272 model.
//
// This binary accepts no arguments and evaluates only FIXED8. It is a
// regression executable, not a nonce searcher. Corpus derivation and phase
// aggregation remain on the host; every per-shot classical result and every
// source-bound phase predicate is produced by device execution of the exact
// shared pp_model.h.
#include <cuda_runtime.h>

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include "pp_host.h"
#include "pp_phase_schedule.h"

static const u64 FIXED8[] = {
    3306946714859ULL,
    37754156253796ULL,
    51170368051453ULL,
    65700024945645ULL,
    147428349223424ULL,
    154123680082395ULL,
    202374768790705ULL,
    279811539530441ULL,
};

static void cuda_check(cudaError_t rc, const char* what) {
    if (rc != cudaSuccess) {
        std::fprintf(stderr, "ppcuda-fixed: FATAL: %s: %s\n", what,
                     cudaGetErrorString(rc));
        std::exit(2);
    }
}

__global__ void evaluate_fixed_kernel(const PP_Shot* shots, u32* faults,
                                      u8* phase_values, int* phase_counts,
                                      u8* phase_invalid, const u8* families) {
    int shot = blockIdx.x * blockDim.x + threadIdx.x;
    if (shot >= PP_NUM_TESTS) return;
    u8* values = phase_values + (size_t)shot * PP_PHASE_SITE_COUNT;
    PP_PhaseTrace tr{values, families, PP_PHASE_SITE_COUNT, 0, false};
    const PP_Shot& s = shots[shot];
    faults[shot] = pp_shot_fault_phase_trace(s.tx, s.ty, s.ox, s.oy, s.lam, &tr);
    phase_counts[shot] = tr.count;
    phase_invalid[shot] = tr.invalid ? 1u : 0u;
}

static void emit_nonce(const PP_Prefix* prefix, const u64* comb, u64 nonce,
                       PP_Shot* d_shots, u32* d_faults, u8* d_phase_values,
                       int* d_phase_counts, u8* d_phase_invalid,
                       const u8* d_families) {
    PP_Shake shake;
    pp_nonce_shake(prefix, nonce, &shake);
    std::vector<PP_Shot> shots;
    pp_derive_corpus_batch(&shake, PP_NUM_TESTS, comb, shots);
    if (shots.size() != PP_NUM_TESTS || shots.size() % 64 != 0) {
        std::fprintf(stderr,
                     "ppcuda-fixed: FATAL: nonce %llu derived %zu shots, expected %d\n",
                     (unsigned long long)nonce, shots.size(), PP_NUM_TESTS);
        std::exit(2);
    }

    const size_t trace_bytes =
        (size_t)PP_NUM_TESTS * (size_t)PP_PHASE_SITE_COUNT * sizeof(u8);
    cuda_check(cudaMemcpy(d_shots, shots.data(), shots.size() * sizeof(PP_Shot),
                          cudaMemcpyHostToDevice),
               "copy shots to device");
    cuda_check(cudaMemset(d_phase_values, 0, trace_bytes), "clear phase values");
    cuda_check(cudaMemset(d_phase_counts, 0, PP_NUM_TESTS * sizeof(int)),
               "clear phase counts");
    cuda_check(cudaMemset(d_phase_invalid, 0, PP_NUM_TESTS * sizeof(u8)),
               "clear phase invalid flags");

    const int threads = 64;
    const int blocks = (PP_NUM_TESTS + threads - 1) / threads;
    evaluate_fixed_kernel<<<blocks, threads>>>(
        d_shots, d_faults, d_phase_values, d_phase_counts, d_phase_invalid,
        d_families);
    cuda_check(cudaGetLastError(), "launch fixed evaluator");
    cuda_check(cudaDeviceSynchronize(), "synchronize fixed evaluator");

    std::vector<u32> faults(PP_NUM_TESTS);
    std::vector<u8> phase_values(trace_bytes);
    std::vector<int> phase_counts(PP_NUM_TESTS);
    std::vector<u8> phase_invalid(PP_NUM_TESTS);
    cuda_check(cudaMemcpy(faults.data(), d_faults,
                          PP_NUM_TESTS * sizeof(u32), cudaMemcpyDeviceToHost),
               "copy fault masks from device");
    cuda_check(cudaMemcpy(phase_values.data(), d_phase_values, trace_bytes,
                          cudaMemcpyDeviceToHost),
               "copy phase predicates from device");
    cuda_check(cudaMemcpy(phase_counts.data(), d_phase_counts,
                          PP_NUM_TESTS * sizeof(int), cudaMemcpyDeviceToHost),
               "copy phase counts from device");
    cuda_check(cudaMemcpy(phase_invalid.data(), d_phase_invalid,
                          PP_NUM_TESTS * sizeof(u8), cudaMemcpyDeviceToHost),
               "copy phase flags from device");

    u64 classical_total = 0;
    u64 clean_phase_total = 0;
    for (int shot = 0; shot < PP_NUM_TESTS; ++shot) {
        if (faults[shot] != 0) {
            ++classical_total;
        } else if (phase_invalid[shot] ||
                   phase_counts[shot] != PP_PHASE_SITE_COUNT) {
            std::fprintf(stderr,
                         "ppcuda-fixed: FATAL: phase schedule mismatch nonce=%llu "
                         "shot=%d count=%d expected=%d invalid=%u\n",
                         (unsigned long long)nonce, shot, phase_counts[shot],
                         PP_PHASE_SITE_COUNT, (unsigned)phase_invalid[shot]);
            std::exit(2);
        }
    }
    for (int shot = 0; shot < PP_NUM_TESTS; ++shot) {
        if (faults[shot] != 0) {
            std::printf("C\t%llu\t%d\t%u\n", (unsigned long long)nonce, shot,
                        faults[shot]);
        }
    }

    const size_t batches = shots.size() / 64;
    const size_t rng_words_per_block = 8192;
    std::vector<u8> rng_block(rng_words_per_block * 8);
    std::vector<u64> predicates(PP_PHASE_SITE_COUNT);
    for (size_t batch = 0; batch < batches; ++batch) {
        std::fill(predicates.begin(), predicates.end(), 0);
        u64 classical_mask = 0;
        for (int lane = 0; lane < 64; ++lane) {
            size_t shot = batch * 64 + (size_t)lane;
            if (faults[shot] != 0) {
                classical_mask |= 1ULL << lane;
                continue;
            }
            const u8* values =
                phase_values.data() + shot * (size_t)PP_PHASE_SITE_COUNT;
            for (int site = 0; site < PP_PHASE_SITE_COUNT; ++site) {
                if (values[site]) predicates[site] |= 1ULL << lane;
            }
        }

        u64 phase_mask = 0;
        int next_site = 0;
        for (u32 base = 0; base < PP_PHASE_RHMR_COUNT;
             base += (u32)rng_words_per_block) {
            u32 words = PP_PHASE_RHMR_COUNT - base;
            if (words > rng_words_per_block) words = (u32)rng_words_per_block;
            pp_shake_read(&shake, rng_block.data(), (size_t)words * 8);
            while (next_site < PP_PHASE_SITE_COUNT &&
                   PP_PHASE_ORDINALS[next_site] < base + words) {
                u32 ordinal = PP_PHASE_ORDINALS[next_site];
                if (ordinal < base) {
                    std::fprintf(stderr,
                                 "ppcuda-fixed: FATAL: non-monotone phase schedule\n");
                    std::exit(2);
                }
                u64 rng;
                std::memcpy(&rng,
                            rng_block.data() + (size_t)(ordinal - base) * 8, 8);
                phase_mask ^= predicates[next_site] & rng;
                ++next_site;
            }
        }
        if (next_site != PP_PHASE_SITE_COUNT) {
            std::fprintf(stderr,
                         "ppcuda-fixed: FATAL: phase schedule exceeds R/Hmr stream\n");
            std::exit(2);
        }
        u64 clean = phase_mask & ~classical_mask;
        while (clean != 0) {
            int lane = __builtin_ctzll(clean);
            std::printf("P\t%llu\t%zu\n", (unsigned long long)nonce,
                        batch * 64 + (size_t)lane);
            ++clean_phase_total;
            clean &= clean - 1;
        }
    }

    std::fprintf(stderr,
                 "ppcuda-fixed: nonce=%llu shots=%d classical=%llu clean_phase=%llu\n",
                 (unsigned long long)nonce, PP_NUM_TESTS,
                 (unsigned long long)classical_total,
                 (unsigned long long)clean_phase_total);
}

int main(int argc, char**) {
    if (argc != 1) {
        std::fprintf(stderr,
                     "ppcuda-fixed: this regression binary accepts no arguments\n");
        return 2;
    }

    PP_Prefix prefix;
    pp_load_prefix("ops.bin", &prefix);
    if (prefix.total_ops != PP_EXPECTED_OPS ||
        pp_state_digest(&prefix) != PP_EXPECTED_STATE_DIGEST) {
        std::fprintf(stderr, "ppcuda-fixed: FATAL: checkpoint identity mismatch\n");
        return 2;
    }

    int device_count = 0;
    cuda_check(cudaGetDeviceCount(&device_count), "query visible CUDA devices");
    if (device_count != 1) {
        std::fprintf(stderr,
                     "ppcuda-fixed: FATAL: exactly one visible CUDA device required; got %d\n",
                     device_count);
        return 2;
    }
    cuda_check(cudaSetDevice(0), "select sole visible CUDA device");
    cuda_check(cudaMemcpyToSymbol(PP_WIDTH_SCHEDULE_D, PP_WIDTH_SCHEDULE,
                                 sizeof(PP_WIDTH_SCHEDULE)),
               "bind width schedule");

    std::vector<u8> families(PP_PHASE_FAMILIES,
                             PP_PHASE_FAMILIES + PP_PHASE_SITE_COUNT);
#ifdef PP_FIXED_FORCE_BAD_FAMILY
    families[0] ^= 1u;
#endif
    std::vector<u64> comb;
    pp_build_comb(comb);

    PP_Shot* d_shots = nullptr;
    u32* d_faults = nullptr;
    u8* d_phase_values = nullptr;
    int* d_phase_counts = nullptr;
    u8* d_phase_invalid = nullptr;
    u8* d_families = nullptr;
    const size_t trace_bytes =
        (size_t)PP_NUM_TESTS * (size_t)PP_PHASE_SITE_COUNT * sizeof(u8);
    cuda_check(cudaMalloc(&d_shots, PP_NUM_TESTS * sizeof(PP_Shot)),
               "allocate shots");
    cuda_check(cudaMalloc(&d_faults, PP_NUM_TESTS * sizeof(u32)),
               "allocate fault masks");
    cuda_check(cudaMalloc(&d_phase_values, trace_bytes),
               "allocate phase values");
    cuda_check(cudaMalloc(&d_phase_counts, PP_NUM_TESTS * sizeof(int)),
               "allocate phase counts");
    cuda_check(cudaMalloc(&d_phase_invalid, PP_NUM_TESTS * sizeof(u8)),
               "allocate phase flags");
    cuda_check(cudaMalloc(&d_families, PP_PHASE_SITE_COUNT * sizeof(u8)),
               "allocate phase families");
    cuda_check(cudaMemcpy(d_families, families.data(),
                          PP_PHASE_SITE_COUNT * sizeof(u8),
                          cudaMemcpyHostToDevice),
               "copy phase families");

    for (u64 nonce : FIXED8) {
        emit_nonce(&prefix, comb.data(), nonce, d_shots, d_faults,
                   d_phase_values, d_phase_counts, d_phase_invalid, d_families);
    }

    cuda_check(cudaFree(d_families), "free phase families");
    cuda_check(cudaFree(d_phase_invalid), "free phase flags");
    cuda_check(cudaFree(d_phase_counts), "free phase counts");
    cuda_check(cudaFree(d_phase_values), "free phase values");
    cuda_check(cudaFree(d_faults), "free fault masks");
    cuda_check(cudaFree(d_shots), "free shots");
    cuda_check(cudaDeviceSynchronize(), "final device synchronization");
    std::fprintf(stderr,
                 "ppcuda-fixed: PASS fixtures=8 shots=72192 source=%s "
                 "model_sha256=9eab10bd8cf1c3510f4dcada4f08f8eb93d2efb749cc8496a88b7f68401bb90b\n",
                 PP_SOURCE_COMMIT);
    return 0;
}
