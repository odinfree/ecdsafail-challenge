// ppcpu.cpp — CPU bit-exact reference of the ppgpu kernel logic.
// Uses the exact same pp_model.h arithmetic the CUDA device code compiles.
// CLI mirrors the ppfilter oracle output formats for diffing:
//   ppcpu scan FROM COUNT [THREADS] [--max-faults 0..3]
//                                           -> "NONCE pred_cls=N" lines
//   ppcpu faultshots NONCE              -> "IDX MASK" lines (mask != 0)
//   ppcpu shot NONCE IDX                -> corpus dump for one shot
//   ppcpu breakdown NONCE               -> per-cause counts
//   ppcpu statedigest                    -> loaded prefix/tail identity
// Env PPF_OPS selects the ops stream (default ops.bin).
#include <atomic>
#include <thread>
#include <vector>
#include "pp_host.h"

#ifndef PP_DISABLE_SCAN
#define PP_DISABLE_SCAN 0
#endif

static const char* ops_path() {
    const char* p = getenv("PPF_OPS");
    return p ? p : "ops.bin";
}

static void limbs_hex(const u64 a[4], char* out) {
    sprintf(out, "%016llx%016llx%016llx%016llx", (unsigned long long)a[3],
            (unsigned long long)a[2], (unsigned long long)a[1],
            (unsigned long long)a[0]);
}

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: ppcpu scan FROM COUNT [THREADS] [--max-faults 0..3] | faultshots NONCE | shot NONCE IDX | breakdown NONCE | statedigest\n");
        return 2;
    }
    std::string mode = argv[1];

#if PP_DISABLE_SCAN
    if (mode == "scan") {
        fprintf(stderr, "ppcpu: range scanning is disabled in this parity build\n");
        return 78;
    }
#endif

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
        return 0;
    }
    if (mode == "scan") {
        if (argc < 4) {
            fprintf(stderr, "ppcpu: scan requires FROM and COUNT\n");
            return 2;
        }
        u64 start = strtoull(argv[2], 0, 10);
        u64 count = strtoull(argv[3], 0, 10);
        int threads = 8;
        u32 max_faults = 0;
        int i = 4;
        if (i < argc && argv[i][0] != '-') threads = atoi(argv[i++]);
        while (i < argc) {
            std::string a = argv[i++];
            if (a == "--max-faults" && i < argc) {
                char* end = nullptr;
                unsigned long v = strtoul(argv[i++], &end, 10);
                if (!end || *end != '\0' || v > 3) {
                    fprintf(stderr, "ppcpu: --max-faults must be in 0..3\n");
                    return 2;
                }
                max_faults = (u32)v;
            } else {
                fprintf(stderr, "ppcpu: unknown scan argument %s\n", a.c_str());
                return 2;
            }
        }
        if (threads < 1) {
            fprintf(stderr, "ppcpu: thread count must be positive\n");
            return 2;
        }
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
                    u32 faults = 0;
                    for (auto& s : shots) {
                        if (pp_shot_fault_mask(s.tx, s.ty, s.ox, s.oy, s.lam) != 0) {
                            faults++;
                            if (faults > max_faults) break;
                        }
                    }
                    if (faults <= max_faults) {
                        survivors.fetch_add(1, std::memory_order_relaxed);
                        printf("%llu pred_cls=%u\n", (unsigned long long)nonce, faults);
                        fflush(stdout);
                    }
                    done.fetch_add(1, std::memory_order_relaxed);
                }
            });
        }
        for (auto& t : pool) t.join();
        fprintf(stderr, "ppcpu done: %llu nonces, max_faults %u, survivors %llu\n",
                (unsigned long long)count, max_faults,
                (unsigned long long)survivors.load());
        return 0;
    }
    fprintf(stderr, "unknown mode %s\n", mode.c_str());
    return 2;
}
