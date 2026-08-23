// ppcpu.cpp — bounded CPU reference for the Q1273 replay-square model.
// Uses the exact same pp_model.h arithmetic the CUDA device code compiles.
// CLI mirrors the ppfilter oracle output formats for diffing:
//   ppcpu faultshots NONCE              -> "IDX MASK" lines (mask != 0)
//   ppcpu shot NONCE IDX                -> corpus dump for one shot
//   ppcpu breakdown NONCE               -> per-cause counts
//   ppcpu statedigest                    -> bound checkpoint/tail digest
// Range and scan modes are deliberately absent from this qualification binary.
// Env PPF_OPS selects the ops stream (default ops.bin).
#include <vector>
#include <cerrno>
#include "pp_host.h"

static const char* ops_path() {
    const char* p = getenv("PPF_OPS");
    return p ? p : "ops.bin";
}

static void limbs_hex(const u64 a[4], char* out) {
    snprintf(out, 80, "%016llx%016llx%016llx%016llx", (unsigned long long)a[3],
             (unsigned long long)a[2], (unsigned long long)a[1],
             (unsigned long long)a[0]);
}

static bool parse_u64_decimal(const char* text, u64* out) {
    if (text == nullptr || *text == '\0') return false;
    for (const char* p = text; *p != '\0'; p++) {
        if (*p < '0' || *p > '9') return false;
    }
    errno = 0;
    char* end = nullptr;
    unsigned long long value = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') return false;
    *out = (u64)value;
    return true;
}

static bool parse_shot_index(const char* text, int* out) {
    u64 value;
    if (!parse_u64_decimal(text, &value) || value >= PP_NUM_TESTS) return false;
    *out = (int)value;
    return true;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: ppcpu shaketest | statedigest | faultshots NONCE | shot NONCE IDX | breakdown NONCE\n");
        return 2;
    }
    std::string mode = argv[1];

    if (mode == "scan") {
        fprintf(stderr, "ppcpu: scan mode disabled in bounded qualification build\n");
        return 2;
    }

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

    PP_Prefix prefix;
    pp_load_prefix(ops_path(), &prefix);
    fprintf(stderr, "ppcpu: prefix loaded, %llu ops\n", (unsigned long long)prefix.total_ops);
    if (mode == "statedigest") {
        printf("%016llx\n", (unsigned long long)pp_state_digest(&prefix));
        return 0;
    }
    std::vector<u64> comb;
    pp_build_comb(comb);
    fprintf(stderr, "ppcpu: comb ready\n");

    if (mode == "faultshots") {
        u64 nonce;
        if (argc != 3 || !parse_u64_decimal(argv[2], &nonce)) {
            fprintf(stderr, "ppcpu: malformed nonce\n");
            return 2;
        }
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
        u64 nonce;
        if (argc != 3 || !parse_u64_decimal(argv[2], &nonce)) {
            fprintf(stderr, "ppcpu: malformed nonce\n");
            return 2;
        }
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
        u64 nonce;
        int idx;
        if (argc != 4 || !parse_u64_decimal(argv[2], &nonce) ||
            !parse_shot_index(argv[3], &idx)) {
            fprintf(stderr, "ppcpu: malformed nonce or shot index\n");
            return 2;
        }
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
    fprintf(stderr, "unknown mode %s\n", mode.c_str());
    return 2;
}
