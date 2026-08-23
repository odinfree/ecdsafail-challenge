// pp_phase_cpu.h — shared source-bound CPU evaluator for the exact conditional
// phase contract. This models only evaluator_phase_mask & ~exact_classical_mask;
// raw phase on classically dirty shots is deliberately not represented.
#pragma once

#include <algorithm>
#include <cstddef>
#include <cstdio>
#include <cstring>
#include <vector>

#include "pp_host.h"
#include "pp_phase_schedule.h"

static const char PP_PHASE_CONTRACT[] = "phase&~classical";
static const char PP_PHASE_FINAL_PREDICATE[] =
    "classical_mask==0&&clean_phase_mask==0";

struct PP_PhaseResult {
    u64 classical_faults = 0;
    std::vector<size_t> clean_phase_shots;
};

// Returns 0 on an exact result and 2 on an internal corpus/schedule mismatch.
// Stream framing, count, SHA, and state digest are checked by pp_load_prefix
// before this function can be reached.
inline int pp_phase_evaluate(const PP_Prefix* prefix, const u64* comb, u64 nonce,
                             PP_PhaseResult* result, const char* program) {
    result->classical_faults = 0;
    result->clean_phase_shots.clear();

    PP_Shake shake;
    pp_nonce_shake(prefix, nonce, &shake);
    std::vector<PP_Shot> shots;
    pp_derive_corpus_batch(&shake, PP_NUM_TESTS, comb, shots);
    if (shots.size() != PP_NUM_TESTS || shots.size() % 64 != 0) {
        fprintf(stderr,
                "%s: FATAL: phase corpus mismatch: got %zu, expected %d exact shots\n",
                program, shots.size(), PP_NUM_TESTS);
        return 2;
    }

    std::vector<u64> predicates(PP_PHASE_SITE_COUNT);
    std::vector<u8> values(PP_PHASE_SITE_COUNT);
    const size_t batches = shots.size() / 64;
    const size_t rng_words_per_block = 8192;
    std::vector<u8> rng_block(rng_words_per_block * 8);

    for (size_t batch = 0; batch < batches; batch++) {
        std::fill(predicates.begin(), predicates.end(), 0);
        u64 classical_mask = 0;
        for (int lane = 0; lane < 64; lane++) {
            size_t shot_index = batch * 64 + (size_t)lane;
            PP_Shot& shot = shots[shot_index];
            PP_PhaseTrace tr{values.data(), PP_PHASE_FAMILIES,
                             PP_PHASE_SITE_COUNT, 0, false};
            u32 fault = pp_shot_fault_phase_trace(shot.tx, shot.ty, shot.ox,
                                                  shot.oy, shot.lam, &tr);
            if (fault != 0) {
                classical_mask |= 1ULL << lane;
                result->classical_faults++;
                continue;
            }
            if (tr.invalid || tr.count != PP_PHASE_SITE_COUNT) {
                fprintf(stderr,
                        "%s: FATAL: phase schedule mismatch at shot %zu: "
                        "count=%d expected=%d invalid=%d\n",
                        program, shot_index, tr.count, PP_PHASE_SITE_COUNT,
                        tr.invalid ? 1 : 0);
                return 2;
            }
            for (int site = 0; site < PP_PHASE_SITE_COUNT; site++) {
                if (values[site]) predicates[site] |= 1ULL << lane;
            }
        }

        // Consume every R/Hmr word in source order. Schedule gaps are squeezed
        // too, so every batch starts at the exact evaluator XOF position.
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
                    fprintf(stderr, "%s: FATAL: non-monotone phase schedule\n",
                            program);
                    return 2;
                }
                u64 rng;
                memcpy(&rng,
                       rng_block.data() + (size_t)(ordinal - base) * 8, 8);
                phase_mask ^= predicates[next_site] & rng;
                next_site++;
            }
        }
        if (next_site != PP_PHASE_SITE_COUNT) {
            fprintf(stderr,
                    "%s: FATAL: phase schedule exceeds R/Hmr stream: %d/%d sites\n",
                    program, next_site, PP_PHASE_SITE_COUNT);
            return 2;
        }

        u64 clean_phase_mask = phase_mask & ~classical_mask;
        while (clean_phase_mask != 0) {
            int lane = __builtin_ctzll(clean_phase_mask);
            result->clean_phase_shots.push_back(batch * 64 + (size_t)lane);
            clean_phase_mask &= clean_phase_mask - 1;
        }
    }
    return 0;
}
