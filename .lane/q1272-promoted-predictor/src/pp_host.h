// pp_host.h — host-only helpers: ops.bin prefix loader (zstd via popen),
// comb table build, corpus derivation for the CPU reference. Shares all
// arithmetic with the device code through pp_model.h.
#pragma once

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include "pp_model.h"

#define PP_OP_BYTES 56
#define PP_NUM_TESTS 9024

// Hard op-count fingerprint guard: the only stream this build serves.
static const u64 PP_EXPECTED_OPS_Q1272 = 12904643ULL; // exact 73422709 promoted Q1272 stream
static const u64 PP_EXPECTED_STATE_DIGEST_Q1272 = 0xe9b2d20ecd1169a8ULL;

struct PP_Prefix {
    PP_Shake checkpoint;
    u8 tail[96][PP_OP_BYTES];
    u64 total_ops;
};

// FNV-1a digest over the checkpoint state + tail + op count. This is the
// compact runtime identity used to cross-check a loaded stream against the
// SHA-256 and fixture ledger without retaining the generated ops artifact.
inline u64 pp_state_digest(const PP_Prefix* p) {
    u64 h = 1469598103934665603ULL;
    auto mix = [&](const u8* d, size_t n) {
        for (size_t i = 0; i < n; i++) {
            h ^= d[i];
            h *= 1099511628211ULL;
        }
    };
    mix((const u8*)p->checkpoint.st, 200);
    mix((const u8*)&p->checkpoint.n, 4);
    mix((const u8*)p->tail, 96 * PP_OP_BYTES);
    mix((const u8*)&p->total_ops, 8);
    return h;
}

// Decompress ops.bin through the zstd CLI (no libzstd-dev needed) and absorb
// the Fiat-Shamir image of all but the last 96 ops, keeping the tail records.
// Image per op = [kind u8] ++ rec[8..56]. Hard-exits on any inconsistency.
inline void pp_load_prefix(const char* path, PP_Prefix* out) {
    FILE* f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "ppgpu: cannot open ops file %s\n", path);
        exit(1);
    }
    u8 header[16];
    if (fread(header, 1, 16, f) != 16 || memcmp(header, "QECCOPSZ", 8) != 0) {
        fprintf(stderr, "ppgpu: bad ops magic in %s\n", path);
        exit(1);
    }
    u64 n;
    memcpy(&n, header + 8, 8);
    fclose(f);
    if (n != PP_EXPECTED_OPS_Q1272) {
        fprintf(stderr,
                "ppgpu: FATAL: ops stream op count %llu != expected %llu (q1272-promoted); "
                "refusing to run on an unknown stream\n",
                (unsigned long long)n, (unsigned long long)PP_EXPECTED_OPS_Q1272);
        exit(2);
    }
    if (n < 96) {
        fprintf(stderr, "ppgpu: ops stream too short\n");
        exit(2);
    }

    // The zstd frame starts after the 16-byte header; stream from offset 16.
    std::string cmd = std::string("tail -c +17 -- '") + path + "' | zstd -dc";
    FILE* pipe = popen(cmd.c_str(), "r");
    if (!pipe) {
        fprintf(stderr, "ppgpu: cannot spawn zstd -dc\n");
        exit(1);
    }

    PP_Shake shake;
    pp_shake_new(&shake);
    pp_shake_absorb(&shake, (const u8*)"quantum_ecc-fiat-shamir-v2", 26);
    {
        u8 nb[8];
        memcpy(nb, &n, 8);
        pp_shake_absorb(&shake, nb, 8);
    }

    u64 body_len = n * PP_OP_BYTES;
    u64 tail_start = body_len - 96 * PP_OP_BYTES;
    u64 consumed = 0;
    u8 rec_pending[PP_OP_BYTES];
    int rec_pending_len = 0;
    std::vector<u8> img_buf;
    img_buf.reserve(1 << 22);
    std::vector<u8> chunk(1 << 20);

    auto push_image = [&](const u8* rec) {
        img_buf.push_back(rec[0]);
        img_buf.insert(img_buf.end(), rec + 8, rec + 56);
        if (img_buf.size() >= (1 << 22)) {
            pp_shake_absorb(&shake, img_buf.data(), img_buf.size());
            img_buf.clear();
        }
    };

    while (consumed < body_len) {
        size_t got = fread(chunk.data(), 1, chunk.size(), pipe);
        if (got == 0) break;
        size_t off = 0;
        while (off < got) {
            u64 abs = consumed + off;
            int need = PP_OP_BYTES - rec_pending_len;
            size_t take = (size_t)need < (got - off) ? (size_t)need : (got - off);
            memcpy(rec_pending + rec_pending_len, chunk.data() + off, take);
            rec_pending_len += (int)take;
            off += take;
            if (rec_pending_len == PP_OP_BYTES) {
                if (abs >= tail_start) {
                    int idx = (int)(abs / PP_OP_BYTES) - (int)(n - 96);
                    memcpy(out->tail[idx], rec_pending, PP_OP_BYTES);
                } else {
                    push_image(rec_pending);
                }
                rec_pending_len = 0;
            }
        }
        consumed += got;
    }
    int rc = pclose(pipe);
    if (rc != 0) {
        fprintf(stderr, "ppgpu: zstd -dc failed (rc=%d)\n", rc);
        exit(1);
    }
    if (consumed != body_len) {
        fprintf(stderr, "ppgpu: short ops body: %llu != %llu\n",
                (unsigned long long)consumed, (unsigned long long)body_len);
        exit(1);
    }
    if (!img_buf.empty()) pp_shake_absorb(&shake, img_buf.data(), img_buf.size());
    out->checkpoint = shake;
    out->total_ops = n;
    u64 digest = pp_state_digest(out);
    if (digest != PP_EXPECTED_STATE_DIGEST_Q1272) {
        fprintf(stderr,
                "ppgpu: FATAL: ops stream state digest %016llx != expected %016llx "
                "(q1272-promoted-73422709); refusing same-count unknown stream\n",
                (unsigned long long)digest,
                (unsigned long long)PP_EXPECTED_STATE_DIGEST_Q1272);
        exit(2);
    }
}

// Resume the checkpointed XOF and absorb the parameterized nonce tail.
inline void pp_nonce_shake(const PP_Prefix* prefix, u64 nonce, PP_Shake* out) {
    *out = prefix->checkpoint;
    u8 img[49];
    for (int b = 0; b < 48; b++) {
        u64 bit = (nonce >> b) & 1;
        for (int r = 0; r < 2; r++) {
            u8 rec[PP_OP_BYTES];
            memcpy(rec, prefix->tail[2 * b + r], PP_OP_BYTES);
            memcpy(rec + 24, &bit, 8);
            img[0] = rec[0];
            memcpy(img + 1, rec + 8, 48);
            pp_shake_absorb(out, img, 49);
        }
    }
    pp_shake_finalize(out);
}

// ─── host comb build (port of ppfilter build_comb) ─────────────────────────

struct PP_F4 {
    u64 v[4];
};

inline void pp_batch_affine(std::vector<PP_Jac>& pts) {
    size_t n = pts.size();
    std::vector<PP_F4> acc(n);
    u64 running[4] = {1, 0, 0, 0};
    for (size_t i = 0; i < n; i++) {
        memcpy(acc[i].v, running, 32);
        if (!pp_jac_is_inf(&pts[i])) {
            u64 t[4];
            pp_fmul(running, pts[i].z, t);
            memcpy(running, t, 32);
        }
    }
    u64 inv[4] = {0, 0, 0, 0};
    if (!pp_is_zero(running)) pp_finv(running, inv);
    for (size_t i = n; i-- > 0;) {
        if (!pp_jac_is_inf(&pts[i])) {
            u64 zinv[4], t[4], z2[4], z3[4];
            pp_fmul(inv, acc[i].v, zinv);
            pp_fmul(inv, pts[i].z, t);
            memcpy(inv, t, 32);
            pp_fsq(zinv, z2);
            pp_fmul(z2, zinv, z3);
            pp_fmul(pts[i].x, z2, t);
            memcpy(pts[i].x, t, 32);
            pp_fmul(pts[i].y, z3, t);
            memcpy(pts[i].y, t, 32);
            pts[i].z[0] = 1;
            pts[i].z[1] = pts[i].z[2] = pts[i].z[3] = 0;
        }
    }
}

// Flat table: (j*255 + d-1) * 8 u64 = x[4], y[4].
inline void pp_build_comb(std::vector<u64>& table) {
    table.resize((size_t)PP_COMB_WINDOWS * 255 * 8);
    PP_Jac base;
    for (int i = 0; i < 4; i++) {
        base.x[i] = PP_GX[i];
        base.y[i] = PP_GY[i];
        base.z[i] = (i == 0);
    }
    std::vector<PP_Jac> slice((size_t)PP_COMB_WINDOWS * 255);
    for (int j = 0; j < PP_COMB_WINDOWS; j++) {
        std::vector<PP_Jac> bj(1, base);
        pp_batch_affine(bj);
        u64 bx[4], by[4];
        memcpy(bx, bj[0].x, 32);
        memcpy(by, bj[0].y, 32);
        PP_Jac acc;
        pp_jac_inf(&acc);
        for (int d = 1; d <= 255; d++) {
            PP_Jac r;
            pp_jadd_mixed(&acc, bx, by, &r);
            acc = r;
            slice[(size_t)j * 255 + (d - 1)] = acc;
        }
        for (int k = 0; k < PP_COMB_W; k++) {
            PP_Jac r;
            pp_jdbl(&base, &r);
            base = r;
        }
    }
    pp_batch_affine(slice);
    for (size_t i = 0; i < slice.size(); i++) {
        if (pp_jac_is_inf(&slice[i])) {
            fprintf(stderr, "ppgpu: comb entry %zu is infinity\n", i);
            exit(1);
        }
        memcpy(&table[i * 8], slice[i].x, 32);
        memcpy(&table[i * 8 + 4], slice[i].y, 32);
    }
}

// ─── host corpus derivation (ppfilter derive_corpus_batch semantics) ───────

struct PP_Shot {
    u64 tx[4], ty[4], ox[4], oy[4], lam[4];
};

inline void pp_derive_corpus_batch(PP_Shake* shake, int count, const u64* comb,
                                   std::vector<PP_Shot>& shots_out) {
    std::vector<PP_Jac> pts;
    pts.reserve((size_t)count * 2);
    u8 kb[64];
    for (int i = 0; i < count; i++) {
        pp_shake_read(shake, kb, 64);
        PP_Jac t, o;
        pp_comb_mul(comb, kb, &t);
        pp_comb_mul(comb, kb + 32, &o);
        pts.push_back(t);
        pts.push_back(o);
    }
    pp_batch_affine(pts);

    std::vector<PP_Shot> shots;
    shots.reserve(count);
    for (int i = 0; i < count; i++) {
        PP_Jac& t = pts[2 * i];
        PP_Jac& o = pts[2 * i + 1];
        if (pp_jac_is_inf(&t) || pp_jac_is_inf(&o)) continue;
        if (pp_eq(t.x, o.x)) continue;
        PP_Shot s;
        memcpy(s.tx, t.x, 32);
        memcpy(s.ty, t.y, 32);
        memcpy(s.ox, o.x, 32);
        memcpy(s.oy, o.y, 32);
        memset(s.lam, 0, 32);
        shots.push_back(s);
    }
    // Batch inversion of all dx = tx - ox (Montgomery trick).
    size_t n = shots.size();
    if (n > 0) {
        std::vector<PP_F4> acc(n);
        u64 running[4] = {1, 0, 0, 0};
        for (size_t i = 0; i < n; i++) {
            memcpy(acc[i].v, running, 32);
            u64 dx[4], t[4];
            pp_fsub(shots[i].tx, shots[i].ox, dx);
            pp_fmul(running, dx, t);
            memcpy(running, t, 32);
        }
        u64 inv[4];
        pp_finv(running, inv);
        for (size_t i = n; i-- > 0;) {
            u64 dx[4], dxinv[4], t[4], dy[4];
            pp_fsub(shots[i].tx, shots[i].ox, dx);
            pp_fmul(inv, acc[i].v, dxinv);
            pp_fmul(inv, dx, t);
            memcpy(inv, t, 32);
            pp_fsub(shots[i].ty, shots[i].oy, dy);
            pp_fmul(dy, dxinv, shots[i].lam);
        }
    }
    shots_out.swap(shots);
}

inline void pp_derive_corpus(const PP_Prefix* prefix, u64 nonce, const u64* comb,
                             std::vector<PP_Shot>& shots) {
    PP_Shake shake;
    pp_nonce_shake(prefix, nonce, &shake);
    pp_derive_corpus_batch(&shake, PP_NUM_TESTS, comb, shots);
}
