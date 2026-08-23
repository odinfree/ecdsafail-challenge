// ppcpu.cpp — CPU bit-exact reference of the ppgpu kernel logic.
// Uses the exact same pp_model.h arithmetic the CUDA device code compiles.
// CLI mirrors the ppfilter oracle output formats for diffing:
//   ppcpu scan FROM COUNT [THREADS]     -> "NONCE pred_cls=0" lines
//   ppcpu faultshots NONCE              -> "IDX MASK" lines (mask != 0)
//   ppcpu faultshots-file FILE          -> Rust-compatible full-mask rows
//   ppcpu shot NONCE IDX                -> corpus dump for one shot
//   ppcpu breakdown NONCE               -> per-cause counts
//   ppcpu statedigest                    -> loaded prefix/tail identity
// Env PPF_OPS selects the ops stream (default ops.bin).
#include <atomic>
#include <thread>
#include <vector>
#include "pp_host.h"

static const char* ops_path() {
    const char* p = getenv("PPF_OPS");
    return p ? p : "ops.bin";
}

static void limbs_hex(const u64 a[4], char* out) {
    sprintf(out, "%016llx%016llx%016llx%016llx", (unsigned long long)a[3],
            (unsigned long long)a[2], (unsigned long long)a[1],
            (unsigned long long)a[0]);
}

struct PP_WidthDiag {
    bool width_fault;
    int round;
    int schedule_index;
    int scheduled_width;
    int needed_width;
    int excess;
    const char* site;
    bool terminal_ok;
};

// Host-only observability mirror of pp_walk_sig. It records the first exact
// scheduled-width violation without changing the shared CPU/CUDA verdict
// path. A violation before the round update is tagged "pre"; one after the
// add and before the arithmetic shift is tagged "post_add".
static PP_WidthDiag walk_width_diag(const u64 a[4], int rounds) {
    PP_P4(Pv);
    PP_S320 p320 = pp_s320_from_u256(Pv);
    PP_S320 h = pp_s320_from_u256(Pv);
    {
        u64 onev[4] = {1, 0, 0, 0};
        PP_S320 one = pp_s320_from_u256(onev);
        pp_s320_add(&h, &one);
    }
    pp_s320_shr1(&h);
    u64 a0 = a[0] & 1;
    u64 a1 = (a[0] >> 1) & 1;
    PP_S320 u = p320;
    PP_S320 v = pp_s320_from_u256(a);
    PP_WidthDiag d = {false, -1, -1, -1, -1, 0, "none", false};

    for (int r = 0; r < rounds; r++) {
        int w = pp_value_width(r);
        int need_u = (int)pp_s320_swidth(&u);
        int need_v = (int)pp_s320_swidth(&v);
        int need = need_u > need_v ? need_u : need_v;
        if (need > w) {
            d = {true, r, r == 0 ? 0 : r * 703 / 695, w, need, need - w,
                 "pre", false};
            return d;
        }
        if (r == 0) {
            PP_S320 nv = v;
            pp_s320_shr1(&nv);
            pp_s320_sub(&nv, &p320);
            if (a1 == 1) pp_s320_add(&nv, &p320);
            if (a0 == 1) pp_s320_add(&nv, &h);
            v = nv;
            continue;
        }
        PP_S320* active;
        if (r % 2 == 0) {
            u64 sign = pp_s320_bit1(&v) ^ pp_s320_bit1(&u);
            if (sign == 0) pp_s320_add(&v, &u); else pp_s320_sub(&v, &u);
            active = &v;
        } else {
            u64 sign = pp_s320_bit1(&u) ^ pp_s320_bit1(&v);
            if (sign == 0) pp_s320_add(&u, &v); else pp_s320_sub(&u, &v);
            active = &u;
        }
        need = (int)pp_s320_swidth(active);
        if (need > w) {
            d = {true, r, r * 703 / 695, w, need, need - w, "post_add", false};
            return d;
        }
        pp_s320_shr1(active);
    }
    d.terminal_ok = pp_s320_is_pm1(&u) && pp_s320_is_pm1(&v);
    return d;
}

// Reconstruct the multiply denominator only after the divide path is clean.
// This is the same value-channel prefix used by pp_shot_fault_mask_s.
static bool derive_multiply_den(const PP_Shot& s, u64 x2c[4]) {
    u64 x2[4], y2[4];
    pp_coord_sub_model(s.tx, s.ox, x2);
    pp_coord_sub_model(s.ty, s.oy, y2);
    PP_WalkOut wd = pp_walk(x2, PP_ROUNDS_DIV);
    if (wd.fault || !wd.term_ok || pp_walkback_fold_fault(x2)) return false;
    u64 xd[4], y2d[4];
    pp_divide_replay(y2, wd.signs, wd.u_neg, wd.v_neg, xd, y2d);
    if (!pp_eq(xd, y2d)) return false;
    u64 three[4], x2b[4];
    pp_fadd(s.ox, s.ox, three);
    pp_fadd(three, s.ox, three);
    pp_mod_add_exact_model(three, x2, x2b);
    pp_square_model(y2d, x2b, x2c);
    return true;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: ppcpu scan FROM COUNT [THREADS] | faultshots NONCE | faultshots-file FILE | diagnostics NONCE | shot NONCE IDX | breakdown NONCE | statedigest\n");
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
#if !defined(PP_ENABLE_RANGE_SCAN)
    if (mode == "scan") {
        fprintf(stderr, "ppcpu: range scan disabled in qualification build\n");
        return 2;
    }
#endif

    PP_Prefix prefix;
    pp_load_prefix(ops_path(), &prefix);
    fprintf(stderr, "ppcpu: prefix loaded, %llu ops\n", (unsigned long long)prefix.total_ops);
    std::vector<u64> comb;
    pp_build_comb(comb);
    fprintf(stderr, "ppcpu: comb ready\n");

    if (mode == "faultshots-file") {
        if (argc != 3) {
            fprintf(stderr, "ppcpu: faultshots-file requires one nonce file\n");
            return 2;
        }
        FILE* nonces = fopen(argv[2], "r");
        if (!nonces) {
            fprintf(stderr, "ppcpu: cannot open nonce file %s\n", argv[2]);
            return 2;
        }
        bool have_prev = false;
        u64 prev = 0;
        size_t rows = 0;
        for (;;) {
            unsigned long long parsed = 0;
            int rc = fscanf(nonces, "%llu", &parsed);
            if (rc == EOF) break;
            if (rc != 1) {
                fprintf(stderr, "ppcpu: malformed nonce file\n");
                fclose(nonces);
                return 2;
            }
            u64 nonce = (u64)parsed;
            if (have_prev && nonce <= prev) {
                fprintf(stderr, "ppcpu: nonce file is not strictly increasing\n");
                fclose(nonces);
                return 2;
            }
            have_prev = true;
            prev = nonce;
            std::vector<PP_Shot> shots;
            pp_derive_corpus(&prefix, nonce, comb.data(), shots);
            u64 words[(PP_NUM_TESTS + 63) / 64] = {0};
            size_t faults = 0;
            for (size_t i = 0; i < shots.size(); i++) {
                u32 m = pp_shot_fault_mask(shots[i].tx, shots[i].ty, shots[i].ox,
                                           shots[i].oy, shots[i].lam);
                if (m != 0) {
                    words[i / 64] |= 1ULL << (i % 64);
                    faults++;
                }
            }
            printf("%llu %zu ", (unsigned long long)nonce, faults);
            for (u64 word : words) printf("%016llx", (unsigned long long)word);
            printf("\n");
            rows++;
        }
        fclose(nonces);
        if (rows == 0) {
            fprintf(stderr, "ppcpu: empty nonce file\n");
            return 2;
        }
        return 0;
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
    if (mode == "diagnostics") {
        u64 nonce = strtoull(argv[2], 0, 10);
        std::vector<PP_Shot> shots;
        pp_derive_corpus(&prefix, nonce, comb.data(), shots);
        for (size_t i = 0; i < shots.size(); i++) {
            PP_Shot& s = shots[i];
            u32 m = pp_shot_fault_mask(s.tx, s.ty, s.ox, s.oy, s.lam);
            if (m == 0) continue;
            if (m == PP_F_WALK_DIV) {
                u64 den[4];
                pp_coord_sub_model(s.tx, s.ox, den);
                PP_WidthDiag d = walk_width_diag(den, PP_ROUNDS_DIV);
                if (d.width_fault) {
                    printf("%zu %u soft walk_div round=%d schedule_index=%d site=%s "
                           "width=%d need=%d excess=%d\n", i, m, d.round,
                           d.schedule_index, d.site, d.scheduled_width,
                           d.needed_width, d.excess);
                } else {
                    const char* cause = !d.terminal_ok ? "terminal" :
                        (pp_walkback_fold_fault(den) ? "walkback_fold" : "unknown");
                    printf("%zu %u hard walk_div cause=%s\n", i, m, cause);
                }
            } else if (m == PP_F_WALK_MUL) {
                u64 den[4];
                if (!derive_multiply_den(s, den)) {
                    printf("%zu %u hard walk_mul cause=upstream\n", i, m);
                    continue;
                }
                if (pp_is_zero(den)) {
                    printf("%zu %u hard walk_mul cause=zero_denominator\n", i, m);
                    continue;
                }
                PP_WidthDiag d = walk_width_diag(den, PP_ROUNDS_MUL);
                if (d.width_fault) {
                    printf("%zu %u soft walk_mul round=%d schedule_index=%d site=%s "
                           "width=%d need=%d excess=%d\n", i, m, d.round,
                           d.schedule_index, d.site, d.scheduled_width,
                           d.needed_width, d.excess);
                } else {
                    const char* cause = !d.terminal_ok ? "terminal" :
                        (pp_walkback_fold_fault(den) ? "walkback_fold" : "unknown");
                    printf("%zu %u hard walk_mul cause=%s\n", i, m, cause);
                }
            } else if (m == PP_F_REPLAY_DIV) {
                printf("%zu %u hard replay_div cause=coefficient\n", i, m);
            } else if (m == PP_F_REPLAY_MUL) {
                printf("%zu %u hard replay_mul cause=coefficient\n", i, m);
            } else if (m == PP_F_RESULT) {
                printf("%zu %u hard result cause=final_value\n", i, m);
            } else {
                printf("%zu %u hard unknown cause=mask\n", i, m);
            }
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
        return 0;
    }
    if (mode == "scan") {
#if !defined(PP_ENABLE_RANGE_SCAN)
        fprintf(stderr, "ppcpu: range scan disabled in qualification build\n");
        return 2;
#else
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
#endif
    }
    fprintf(stderr, "unknown mode %s\n", mode.c_str());
    return 2;
}
