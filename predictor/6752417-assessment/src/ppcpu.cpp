// ppcpu.cpp — CPU bit-exact reference of the ppgpu kernel logic.
// Uses the exact same pp_model.h arithmetic the CUDA device code compiles.
// CLI mirrors the ppfilter oracle output formats for diffing:
//   ppcpu scan FROM COUNT [THREADS]     -> "NONCE pred_cls=0" lines
//   ppcpu faultshots NONCE              -> "IDX MASK" lines (mask != 0)
//   ppcpu shot NONCE IDX                -> corpus dump for one shot
//   ppcpu breakdown NONCE               -> per-cause counts
//   ppcpu statedigest                    -> loaded prefix/tail identity
// Env PPF_OPS selects the ops stream (default ops.bin).
#include <atomic>
#include <thread>
#include <vector>
#include "pp_host.h"
#include "pp_phase_schedule.h"

static const char* ops_path() {
    const char* p = getenv("PPF_OPS");
    return p ? p : "ops.bin";
}

static void limbs_hex(const u64 a[4], char* out) {
    sprintf(out, "%016llx%016llx%016llx%016llx", (unsigned long long)a[3],
            (unsigned long long)a[2], (unsigned long long)a[1],
            (unsigned long long)a[0]);
}

// Hunt-sufficient phase contract. Raw phase on already-classically-dirty
// lanes is intentionally out of scope; a survivor requires both masks zero.
static int phasefaultshots(const PP_Prefix* prefix, const u64* comb, u64 nonce) {
    PP_Shake shake;
    pp_nonce_shake(prefix, nonce, &shake);
    std::vector<PP_Shot> shots;
    pp_derive_corpus_batch(&shake, PP_NUM_TESTS, comb, shots);
    if (shots.size() != PP_NUM_TESTS || shots.size() % 64 != 0) {
        fprintf(stderr,
                "ppcpu: FATAL: phase corpus mismatch: got %zu, expected %d exact shots\n",
                shots.size(), PP_NUM_TESTS);
        return 2;
    }

    std::vector<u64> predicates(PP_PHASE_SITE_COUNT);
    std::vector<u8> values(PP_PHASE_SITE_COUNT);
    std::vector<size_t> clean_phase_shots;
    u64 classical_faults = 0;
    const size_t batches = shots.size() / 64;
    const size_t rng_words_per_block = 8192;
    std::vector<u8> rng_block(rng_words_per_block * 8);

    for (size_t batch = 0; batch < batches; batch++) {
        std::fill(predicates.begin(), predicates.end(), 0);
        u64 classical_mask = 0;
        for (int lane = 0; lane < 64; lane++) {
            size_t shot_index = batch * 64 + (size_t)lane;
            PP_Shot& shot = shots[shot_index];
            PP_PhaseTrace tr{values.data(), PP_PHASE_FAMILIES, PP_PHASE_SITE_COUNT,
                             0, false};
            u32 fault = pp_shot_fault_phase_trace(shot.tx, shot.ty, shot.ox, shot.oy,
                                                  shot.lam, &tr);
            if (fault != 0) {
                classical_mask |= 1ULL << lane;
                classical_faults++;
                continue;
            }
            if (tr.invalid || tr.count != PP_PHASE_SITE_COUNT) {
                fprintf(stderr,
                        "ppcpu: FATAL: phase schedule mismatch at shot %zu: "
                        "count=%d expected=%d invalid=%d at=%d family=%u/%u\n",
                        shot_index, tr.count, PP_PHASE_SITE_COUNT, tr.invalid ? 1 : 0,
                        tr.invalid_at, (unsigned)tr.actual_family,
                        (unsigned)tr.expected_family);
                return 2;
            }
            for (int site = 0; site < PP_PHASE_SITE_COUNT; site++) {
                if (values[site]) predicates[site] |= 1ULL << lane;
            }
        }

        u64 phase_mask = 0;
        int next_site = 0;
        for (u32 base = 0; base < PP_PHASE_RHMR_COUNT; base += (u32)rng_words_per_block) {
            u32 words = PP_PHASE_RHMR_COUNT - base;
            if (words > rng_words_per_block) words = (u32)rng_words_per_block;
            pp_shake_read(&shake, rng_block.data(), (size_t)words * 8);
            while (next_site < PP_PHASE_SITE_COUNT &&
                   PP_PHASE_ORDINALS[next_site] < base + words) {
                u32 ordinal = PP_PHASE_ORDINALS[next_site];
                if (ordinal < base) {
                    fprintf(stderr, "ppcpu: FATAL: non-monotone phase schedule\n");
                    return 2;
                }
                u64 rng;
                memcpy(&rng, rng_block.data() + (size_t)(ordinal - base) * 8, 8);
                phase_mask ^= predicates[next_site] & rng;
                next_site++;
            }
        }
        if (next_site != PP_PHASE_SITE_COUNT) {
            fprintf(stderr,
                    "ppcpu: FATAL: phase schedule exceeds R/Hmr stream: %d/%d sites\n",
                    next_site, PP_PHASE_SITE_COUNT);
            return 2;
        }

        u64 clean_phase_mask = phase_mask & ~classical_mask;
        while (clean_phase_mask != 0) {
            int lane = __builtin_ctzll(clean_phase_mask);
            clean_phase_shots.push_back(batch * 64 + (size_t)lane);
            clean_phase_mask &= clean_phase_mask - 1;
        }
    }

    for (size_t shot : clean_phase_shots) printf("%zu\n", shot);
    fprintf(stderr,
            "ppcpu phasefaultshots: nonce=%llu shots=%zu classical=%llu "
            "clean_phase=%zu survivor=%d contract=phase&~classical\n",
            (unsigned long long)nonce, shots.size(),
            (unsigned long long)classical_faults, clean_phase_shots.size(),
            classical_faults == 0 && clean_phase_shots.empty() ? 1 : 0);
    return 0;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: ppcpu scan FROM COUNT [THREADS] | faultshots NONCE | "
                        "phasefaultshots NONCE | shot NONCE IDX | breakdown NONCE | "
                        "statedigest\n");
        return 2;
    }
    std::string mode = argv[1];

    if (mode == "shaketest") {
        PP_Shake s;
        pp_shake_new(&s);
        pp_shake_finalize(&s);
        u8 out[64];
        pp_shake_read(&s, out, 64);
        fprintf(stderr, "empty: ");
        for (int i = 0; i < 32; i++) fprintf(stderr, "%02x", out[i]);
        fprintf(stderr, "\nref  : 46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f\n");
        PP_Shake s2;
        pp_shake_new(&s2);
        pp_shake_absorb(&s2, (const u8*)"abc", 3);
        pp_shake_finalize(&s2);
        pp_shake_read(&s2, out, 64);
        fprintf(stderr, "abc  : ");
        for (int i = 0; i < 32; i++) fprintf(stderr, "%02x", out[i]);
        fprintf(stderr, "\nref  : 483366601360a8771c6863080cc4114d8db44530f8f1e1ee4f94ea37e78b5739\n");
        return 0;
    }
    if (mode == "probejac") {
        // probejac NONCE: Jacobian result of the two comb muls for shot 0
        PP_Prefix prefix;
        pp_load_prefix(ops_path(), &prefix);
        std::vector<u64> comb;
        pp_build_comb(comb);
        u64 nonce = strtoull(argv[2], 0, 10);
        PP_Shake s;
        pp_nonce_shake(&prefix, nonce, &s);
        u8 kb[64];
        pp_shake_read(&s, kb, 64);
        PP_Jac t, o;
        pp_comb_mul(comb.data(), kb, &t);
        pp_comb_mul(comb.data(), kb + 32, &o);
        char hx[80];
        limbs_hex(t.x, hx); printf("jx=%s\n", hx);
        limbs_hex(t.y, hx); printf("jy=%s\n", hx);
        limbs_hex(t.z, hx); printf("jz=%s\n", hx);
        limbs_hex(o.x, hx); printf("kx=%s\n", hx);
        limbs_hex(o.y, hx); printf("ky=%s\n", hx);
        limbs_hex(o.z, hx); printf("kz=%s\n", hx);
        return 0;
    }
    if (mode == "probebytes") {
        // probebytes NONCE: hex of the first 128 squeezed bytes
        PP_Prefix prefix;
        pp_load_prefix(ops_path(), &prefix);
        u64 nonce = strtoull(argv[2], 0, 10);
        PP_Shake s;
        pp_nonce_shake(&prefix, nonce, &s);
        u8 out[128];
        pp_shake_read(&s, out, 128);
        for (int i = 0; i < 128; i++) printf("%02x", out[i]);
        printf("\n");
        return 0;
    }
    if (mode == "statedigest") {
        PP_Prefix prefix;
        pp_load_prefix(ops_path(), &prefix);
        printf("%016llx\n", (unsigned long long)pp_state_digest(&prefix));
        return 0;
    }

    PP_Prefix prefix;
    pp_load_prefix(ops_path(), &prefix);
    fprintf(stderr, "ppcpu: prefix loaded, %llu ops\n", (unsigned long long)prefix.total_ops);
    std::vector<u64> comb;
    pp_build_comb(comb);
    fprintf(stderr, "ppcpu: comb ready\n");

    if (mode == "phasefaultshots") {
        if (argc != 3) {
            fprintf(stderr, "usage: ppcpu phasefaultshots NONCE\n");
            return 2;
        }
        u64 nonce = strtoull(argv[2], 0, 10);
        return phasefaultshots(&prefix, comb.data(), nonce);
    }

    if (mode == "faultshots") {
        u64 nonce = strtoull(argv[2], 0, 10);
        std::vector<PP_Shot> shots;
        pp_derive_corpus(&prefix, nonce, comb.data(), shots);
        for (size_t i = 0; i < shots.size(); i++) {
            u32 m = pp_shot_fault_mask(shots[i].tx, shots[i].ty, shots[i].ox, shots[i].oy,
                                       shots[i].lam);
            if (m != 0) printf("%zu %u\n", i, m);
        }
        return 0;
    }
    if (mode == "breakdown") {
        u64 nonce = strtoull(argv[2], 0, 10);
        std::vector<PP_Shot> shots;
        pp_derive_corpus(&prefix, nonce, comb.data(), shots);
        u64 br[5] = {0, 0, 0, 0, 0};
        u64 pred = 0;
        long first_idx = -1;
        for (size_t i = 0; i < shots.size(); i++) {
            u32 m = pp_shot_fault_mask(shots[i].tx, shots[i].ty, shots[i].ox, shots[i].oy,
                                       shots[i].lam);
            if (m != 0) {
                if (first_idx < 0) first_idx = (long)i;
                pred++;
                br[0] += (m & PP_F_WALK_DIV) != 0;
                br[1] += (m & PP_F_REPLAY_DIV) != 0;
                br[2] += (m & PP_F_WALK_MUL) != 0;
                br[3] += (m & PP_F_REPLAY_MUL) != 0;
                br[4] += (m & PP_F_RESULT) != 0;
            }
        }
        printf("nonce %llu pred_cls=%llu walk_div=%llu replay_div=%llu walk_mul=%llu "
               "replay_mul=%llu result=%llu shots=%zu first=%ld\n",
               (unsigned long long)nonce, (unsigned long long)pred,
               (unsigned long long)br[0], (unsigned long long)br[1],
               (unsigned long long)br[2], (unsigned long long)br[3],
               (unsigned long long)br[4], shots.size(), first_idx);
        return 0;
    }
    if (mode == "shot") {
        u64 nonce = strtoull(argv[2], 0, 10);
        int idx = atoi(argv[3]);
        std::vector<PP_Shot> shots;
        pp_derive_corpus(&prefix, nonce, comb.data(), shots);
        PP_Shot& s = shots[idx];
        u32 m = pp_shot_fault_mask(s.tx, s.ty, s.ox, s.oy, s.lam);
        char hx[80];
        printf("shot %d mask=%u\n", idx, m);
        limbs_hex(s.tx, hx); printf("tx=%s\n", hx);
        limbs_hex(s.ty, hx); printf("ty=%s\n", hx);
        limbs_hex(s.ox, hx); printf("ox=%s\n", hx);
        limbs_hex(s.oy, hx); printf("oy=%s\n", hx);
        limbs_hex(s.lam, hx); printf("lam=%s\n", hx);
        u64 a_div[4], dy[4];
        pp_fsub(s.tx, s.ox, a_div);
        pp_fsub(s.ty, s.oy, dy);
        limbs_hex(a_div, hx); printf("a_div=%s\n", hx);
        limbs_hex(dy, hx); printf("dy=%s\n", hx);
        PP_WalkOut wd = pp_walk(a_div, PP_ROUNDS_DIV);
        printf("walk div: fault=%d term_ok=%d su=%d sv=%d walkback_fold=%d\n", wd.fault,
               wd.term_ok, wd.u_neg, wd.v_neg, pp_walkback_fold_fault(a_div));
        u64 x2[4], y2[4];
        pp_coord_sub_model(s.tx, s.ox, x2);
        pp_coord_sub_model(s.ty, s.oy, y2);
        u64 xd[4], y2d[4];
        pp_divide_replay(y2, wd.signs, wd.u_neg, wd.v_neg, xd, y2d);
        u64 three[4], x2b[4], x2c[4];
        pp_fadd(s.ox, s.ox, three);
        pp_fadd(three, s.ox, three);
        pp_mod_add_exact_model(three, x2, x2b);
        pp_square_model(y2d, x2b, x2c);
        limbs_hex(x2c, hx); printf("a_mul=%s\n", hx);
        return 0;
    }
    if (mode == "scan") {
        u64 start = strtoull(argv[2], 0, 10);
        u64 count = strtoull(argv[3], 0, 10);
        int threads = argc > 4 ? atoi(argv[4]) : 8;
        std::atomic<u64> next_i(0), done(0), survivors(0);
        std::vector<std::thread> pool;
        for (int t = 0; t < threads; t++) {
            pool.emplace_back([&]() {
                PP_Prefix pfx = prefix; // checkpoint is cheap to clone
                for (;;) {
                    u64 i = next_i.fetch_add(1, std::memory_order_relaxed);
                    if (i >= count) break;
                    u64 nonce = start + i;
                    std::vector<PP_Shot> shots;
                    pp_derive_corpus(&pfx, nonce, comb.data(), shots);
                    bool fault = false;
                    for (auto& s : shots) {
                        if (pp_shot_fault_mask(s.tx, s.ty, s.ox, s.oy, s.lam) != 0) {
                            fault = true;
                            break;
                        }
                    }
                    if (!fault) {
                        survivors.fetch_add(1, std::memory_order_relaxed);
                        printf("%llu pred_cls=0\n", (unsigned long long)nonce);
                        fflush(stdout);
                    }
                    done.fetch_add(1, std::memory_order_relaxed);
                }
            });
        }
        for (auto& t : pool) t.join();
        fprintf(stderr, "ppcpu done: %llu nonces, survivors %llu\n",
                (unsigned long long)count, (unsigned long long)survivors.load());
        return 0;
    }
    fprintf(stderr, "unknown mode %s\n", mode.c_str());
    return 2;
}
