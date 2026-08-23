// ppgpu.cu — CUDA port/harness for the exact promoted Q1272 sampled and
// default-rescaled stream at structural source 73422709. Range mode is
// compile-disabled in the qualification build. RTX 4090 target (sm_89).
//
// Bit-exactness contract: per-shot fault masks and per-nonce survivor
// verdicts must equal the unchanged trusted evaluator (see FIXTURES.md). All
// arithmetic lives in pp_model.h, shared line-for-line with the CPU
// reference (ppcpu.cpp).
//
// Kernel architecture (adapted from ecdsa-gpu-v2 cuda/gpu_island2.cu):
//   one block per nonce, WAVE threads = WAVE shots per wave, thread 0
//   advances the checkpointed SHAKE256 sponge in shared memory, all lanes
//   run the two fixed-base comb muls, ONE 256-wide block batch inversion
//   yields both affine points and lambda per shot, then the pingpong fault
//   model runs per lane with the sign tapes in shared memory.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <cuda_runtime.h>

#include "pp_model.h"
#include "pp_host.h"

#define MAX_WAVE 256
// atomicAdd for uint64_t (unsigned long on LP64) via the ULL overload.
__device__ __forceinline__ void pp_atomic_add_u64(u64* p, u64 v) {
    atomicAdd((unsigned long long*)p, (unsigned long long)v);
}

// ─── device constants ───────────────────────────────────────────────────────
__device__ __constant__ u64 d_base_st[25];
__device__ __constant__ int d_base_n;
__device__ __constant__ u8 d_tail[96 * PP_OP_BYTES];
__device__ u64* d_comb;   // comb8: 32*255 entries * 8 u64
__device__ u64* d_comb16; // comb16: 16*65535 entries * 8 u64 (optional)
__device__ __constant__ int d_comb_bits;

// ─── comb16 construction (device): entry (j,d) = comb8[2j][lo] + comb8[2j+1][hi]
__global__ void build_comb16_kernel(const u64* comb8, u64* comb16) {
    u64 idx = blockIdx.x * (u64)blockDim.x + threadIdx.x;
    u64 total = 16ull * 65535ull;
    for (u64 i = idx; i < total; i += gridDim.x * (u64)blockDim.x) {
        int j = (int)(i / 65535ull);
        u32 d = (u32)(i % 65535ull) + 1;
        u32 lo = d & 0xff, hi = d >> 8;
        u64 ax[4], ay[4];
        const u64* e;
        if (lo) {
            e = comb8 + ((size_t)(2 * j) * 255 + lo - 1) * 8;
            for (int k = 0; k < 4; k++) { ax[k] = e[k]; ay[k] = e[4 + k]; }
        }
        if (hi) {
            e = comb8 + ((size_t)(2 * j + 1) * 255 + hi - 1) * 8;
            if (lo) {
                // Jacobian add of the two affine entries, then to affine
                PP_Jac a, r;
                for (int k = 0; k < 4; k++) { a.x[k] = ax[k]; a.y[k] = ay[k]; a.z[k] = (k == 0); }
                pp_jadd_mixed(&a, e, e + 4, &r);
                u64 zi[4], zi2[4], zi3[4];
                pp_finv(r.z, zi);
                pp_fsq(zi, zi2);
                pp_fmul(zi2, zi, zi3);
                pp_fmul(r.x, zi2, ax);
                pp_fmul(r.y, zi3, ay);
            } else {
                for (int k = 0; k < 4; k++) { ax[k] = e[k]; ay[k] = e[4 + k]; }
            }
        }
        u64* out = comb16 + i * 8;
        for (int k = 0; k < 4; k++) { out[k] = ax[k]; out[4 + k] = ay[k]; }
    }
}

// Scalar mul with the comb16 table: 16 windows of 16 bits.
__device__ __forceinline__ void pp_comb_mul16(const u64* table, const u8 k[32],
                                              PP_Jac* acc) {
    pp_jac_inf(acc);
    for (int j = 0; j < 16; j++) {
        u32 d = (u32)k[2 * j] | ((u32)k[2 * j + 1] << 8);
        if (d != 0) {
            const u64* e = table + ((size_t)j * 65535 + d - 1) * 8;
            PP_Jac r;
            pp_jadd_mixed(acc, e, e + 4, &r);
            *acc = r;
        }
    }
}

__device__ __forceinline__ void dev_comb_mul(const u8 k[32], PP_Jac* acc) {
    if (d_comb_bits == 16 && d_comb16) {
        pp_comb_mul16(d_comb16, k, acc);
    } else {
        pp_comb_mul(d_comb, k, acc);
    }
}

// ─── per-nonce SHAKE tail absorb + wave squeeze (thread 0 only) ────────────
// sq lives in shared memory. Exact same byte stream as the oracle's
// nonce_shake + Shake::read.

__device__ void dev_nonce_absorb(PP_Shake* sq, u64 nonce) {
    for (int i = 0; i < 25; i++) sq->st[i] = d_base_st[i];
    sq->n = d_base_n;
    sq->squeezing = false;
    sq->pos = 0;
    u8 img[49];
    for (int b = 0; b < 48; b++) {
        u64 bit = (nonce >> b) & 1;
        for (int r = 0; r < 2; r++) {
            const u8* rec = &d_tail[(2 * b + r) * PP_OP_BYTES];
            // image = rec[0] ++ rec[8..56], with rec[24..32] = bit (LE)
            img[0] = rec[0];
            for (int i = 0; i < 16; i++) img[1 + i] = rec[8 + i];          // rec[8..24]
            for (int i = 0; i < 8; i++) img[17 + i] = (u8)(bit >> (8 * i)); // rec[24..32]
            for (int i = 0; i < 24; i++) img[25 + i] = rec[32 + i];        // rec[32..56]
            pp_shake_absorb(sq, img, 49);
        }
    }
    pp_shake_finalize(sq);
}

// Squeeze into shared wbytes, u64-wise (valid: wave sizes are multiples of
// 64 and the rate is a multiple of 8, so the position stays 8-aligned).
__device__ void dev_squeeze_wave(PP_Shake* sq, u8* wbytes, int nbytes) {
    u64* w64 = (u64*)wbytes;
    int nwords = nbytes / 8;
    for (int i = 0; i < nwords; i++) {
        if (sq->pos == PP_RATE) {
            pp_keccak_f(sq->st);
            sq->pos = 0;
        }
        w64[i] = sq->st[sq->pos / 8];
        sq->pos += 8;
    }
}

// ─── 256-wide block batch inversion (two values per lane) ──────────────────
// Hillis-Steele inclusive scans from both ends + one Fermat inversion.
// Slot layout: slot[2*t] = a_t, slot[2*t+1] = b_t. Every thread must call.
// All contributed values must be nonzero (substitute 1 for inactive lanes).
__device__ __forceinline__ void sh4_store(u64* base, int idx, const u64 v[4]) {
    u64* p = base + (size_t)idx * 4;
    for (int i = 0; i < 4; i++) p[i] = v[i];
}
__device__ __forceinline__ void sh4_load(const u64* base, int idx, u64 v[4]) {
    const u64* p = base + (size_t)idx * 4;
    for (int i = 0; i < 4; i++) v[i] = p[i];
}

__device__ void block_batch_inv2(const u64 va[4], const u64 vb[4], u64 inva[4],
                                 u64 invb[4], u64* scan, u64* rscan,
                                 u64* shared_inv) {
    int t = threadIdx.x;
    int wave = blockDim.x;
    int n2 = 2 * wave;
    sh4_store(scan, 2 * t, va);
    sh4_store(scan, 2 * t + 1, vb);
    sh4_store(rscan, 2 * t, va);
    sh4_store(rscan, 2 * t + 1, vb);
    __syncthreads();
    for (int off = 1; off < n2; off <<= 1) {
        int idx0 = 2 * t, idx1 = 2 * t + 1;
        u64 cur0[4], left0[4], cur1[4], left1[4];
        bool has0 = idx0 >= off, has1 = idx1 >= off;
        sh4_load(scan, idx0, cur0);
        if (has0) sh4_load(scan, idx0 - off, left0);
        sh4_load(scan, idx1, cur1);
        if (has1) sh4_load(scan, idx1 - off, left1);
        __syncthreads();
        if (has0) {
            u64 prod[4];
            pp_fmul(left0, cur0, prod);
            sh4_store(scan, idx0, prod);
        }
        if (has1) {
            u64 prod[4];
            pp_fmul(left1, cur1, prod);
            sh4_store(scan, idx1, prod);
        }
        __syncthreads();
    }
    for (int off = 1; off < n2; off <<= 1) {
        int idx0 = 2 * t, idx1 = 2 * t + 1;
        u64 cur0[4], right0[4], cur1[4], right1[4];
        bool has0 = (idx0 + off) < n2, has1 = (idx1 + off) < n2;
        sh4_load(rscan, idx0, cur0);
        if (has0) sh4_load(rscan, idx0 + off, right0);
        sh4_load(rscan, idx1, cur1);
        if (has1) sh4_load(rscan, idx1 + off, right1);
        __syncthreads();
        if (has0) {
            u64 prod[4];
            pp_fmul(cur0, right0, prod);
            sh4_store(rscan, idx0, prod);
        }
        if (has1) {
            u64 prod[4];
            pp_fmul(cur1, right1, prod);
            sh4_store(rscan, idx1, prod);
        }
        __syncthreads();
    }
    if (t == 0) {
        u64 total[4];
        sh4_load(scan, n2 - 1, total);
        pp_finv(total, shared_inv);
    }
    __syncthreads();
    {
        int idx = 2 * t;
        u64 before[4], after[4], tmp[4], out[4];
        if (idx == 0) {
            before[0] = 1; before[1] = before[2] = before[3] = 0;
        } else {
            sh4_load(scan, idx - 1, before);
        }
        sh4_load(rscan, idx + 1, after);
        pp_fmul(before, after, tmp);
        pp_fmul(tmp, shared_inv, out);
        for (int i = 0; i < 4; i++) inva[i] = out[i];
    }
    {
        int idx = 2 * t + 1;
        u64 before[4], after[4], tmp[4], out[4];
        sh4_load(scan, idx - 1, before);
        if (idx == n2 - 1) {
            after[0] = 1; after[1] = after[2] = after[3] = 0;
        } else {
            sh4_load(rscan, idx + 1, after);
        }
        pp_fmul(before, after, tmp);
        pp_fmul(tmp, shared_inv, out);
        for (int i = 0; i < 4; i++) invb[i] = out[i];
    }
    __syncthreads();
}

// ─── per-lane stage 1: comb muls + Jacobian aggregates ─────────────────────
__device__ __forceinline__ void dev_stage1(const u8* rb, u64 jx[4], u64 jy[4],
                                           u64 jz[4], u64 kx[4], u64 ky[4],
                                           u64 kz[4], u64 num_jac[4], u64 za[4],
                                           u64 den[4], bool* skip_out) {
    PP_Jac tj, oj;
    dev_comb_mul(rb, &tj);
    dev_comb_mul(rb + 32, &oj);

    // den = (tx-ox)*(Zt*Zo)^2 = Xt*Zo^2 - Xo*Zt^2
    // num = (ty-oy)*(Zt*Zo)^3 = Yt*Zo^3 - Yo*Zt^3
    u64 zt2[4], zo2[4], zt3[4], zo3[4], t1[4], t2[4];
    pp_fsq(tj.z, zt2);
    pp_fsq(oj.z, zo2);
    pp_fmul(zt2, tj.z, zt3);
    pp_fmul(zo2, oj.z, zo3);
    pp_fmul(tj.x, zo2, t1);
    pp_fmul(oj.x, zt2, t2);
    pp_fsub(t1, t2, den);
    pp_fmul(tj.y, zo3, t1);
    pp_fmul(oj.y, zt3, t2);
    pp_fsub(t1, t2, num_jac);

    bool skip = pp_jac_is_inf(&tj) || pp_jac_is_inf(&oj) || pp_is_zero(den);
    pp_fmul(tj.z, oj.z, za);
    if (skip) {
        za[0] = 1; za[1] = za[2] = za[3] = 0;
        den[0] = 1; den[1] = den[2] = den[3] = 0;
    }
    for (int i = 0; i < 4; i++) {
        jx[i] = tj.x[i]; jy[i] = tj.y[i]; jz[i] = tj.z[i];
        kx[i] = oj.x[i]; ky[i] = oj.y[i]; kz[i] = oj.z[i];
    }
    *skip_out = skip;
}

// ─── per-lane stage 2 (after batch inversion): affine + lambda + model ─────
__device__ __forceinline__ u32 dev_stage2(const u64 jx[4], const u64 jy[4],
                                          const u64 jz[4], const u64 kx[4],
                                          const u64 ky[4], const u64 kz[4],
                                          const u64 num_jac[4], const u64 za_inv[4],
                                          const u64 den_inv[4], u64* signs_d,
                                          u64* signs_m, const u16* wtab) {
    u64 zt_inv[4], zo_inv[4], t[4];
    pp_fmul(za_inv, kz, zt_inv);
    pp_fmul(za_inv, jz, zo_inv);
    u64 zti2[4], zti3[4], zoi2[4], zoi3[4];
    pp_fsq(zt_inv, zti2);
    pp_fmul(zti2, zt_inv, zti3);
    pp_fsq(zo_inv, zoi2);
    pp_fmul(zoi2, zo_inv, zoi3);
    u64 tx[4], ty[4], ox[4], oy[4], lam[4];
    pp_fmul(jx, zti2, tx);
    pp_fmul(jy, zti3, ty);
    pp_fmul(kx, zoi2, ox);
    pp_fmul(ky, zoi3, oy);
    // lam = num_jac * den_inv * za_inv = (dy/dx)*(ZtZo)^3/(ZtZo)^2 * 1/(ZtZo)
    pp_fmul(num_jac, den_inv, t);
    pp_fmul(t, za_inv, lam);
    return pp_shot_fault_mask_s(tx, ty, ox, oy, lam, signs_d, signs_m, wtab);
}

// Shared-memory budget per block (wave = blockDim.x):
//   wbytes      wave*64
//   scan/rscan  2 * (2*wave*4) u64
//   shared_inv  4 u64
//   signs       2 * wave*11 u64
//   post-skip prefix (harness only): wave ints
static size_t shmem_bytes(int wave) {
    return (size_t)wave * 64 + 2 * (size_t)(2 * wave * 4) * 8 + 32 +
           2 * (size_t)wave * 11 * 8 + (size_t)wave * 4 + 64;
}

// ─── probe kernel: batch inversion self-check ──────────────────────────────
// lane t contributes va = t+2, vb = (t+2)^2 (small field values); writes back
// va*inva and vb*invb (both must be field 1) plus finv(va)*va.
__global__ void probe_batchinv_kernel(u64* out) {
    extern __shared__ unsigned char smem[];
    int t = threadIdx.x;
    int wave = blockDim.x;
    u64* scan = (u64*)smem;
    u64* rscan = scan + 2 * wave * 4;
    u64* shared_inv = rscan + 2 * wave * 4;
    u64 va[4] = {(u64)t + 2, 0, 0, 0};
    u64 vb[4];
    pp_fsq(va, vb);
    u64 inva[4], invb[4];
    block_batch_inv2(va, vb, inva, invb, scan, rscan, shared_inv);
    u64 c1[4], c2[4];
    pp_fmul(va, inva, c1);
    pp_fmul(vb, invb, c2);
    for (int i = 0; i < 4; i++) {
        out[t * 8 + i] = c1[i];
        out[t * 8 + 4 + i] = c2[i];
    }
    // direct finv check: slot 2 of output row = va * finv(va)
    if (t == 0) {
        u64 fi[4], c3[4];
        pp_finv(va, fi);
        pp_fmul(va, fi, c3);
        for (int i = 0; i < 4; i++) out[1024 + i] = c3[i];
    }
}

// ─── production scan kernel ────────────────────────────────────────────────
__global__ void scan_kernel(u64 start, u64 count, u32* out_cnt, u64* out_list,
                            int max_out, u64* waves_done, u64* fault_counter) {
    extern __shared__ unsigned char smem[];
    int t = threadIdx.x;
    int wave = blockDim.x;
    u8* wbytes = smem;
    u64* scan = (u64*)(wbytes + wave * 64);
    u64* rscan = scan + 2 * wave * 4;
    u64* shared_inv = rscan + 2 * wave * 4;
    u64* signs_all = shared_inv + 4;
    u64* signs_d = &signs_all[t * 11];
    u64* signs_m = &signs_all[wave * 11 + t * 11];
    __shared__ PP_Shake sq;
    __shared__ int hard_flag;
    __shared__ u16 ws[700];
    for (int i = t; i < 700; i += wave) ws[i] = PP_WIDTH_SCHEDULE_D[i];
    __syncthreads();

    for (u64 nidx = blockIdx.x; nidx < count; nidx += gridDim.x) {
        u64 nonce = start + nidx;
        if (t == 0) {
            dev_nonce_absorb(&sq, nonce);
            hard_flag = 0;
        }
        __syncthreads();
        u64 my_waves = 0, my_faults = 0;
        for (int base_shot = 0; base_shot < PP_NUM_TESTS; base_shot += wave) {
            if (hard_flag) break;
            int n_this =
                (PP_NUM_TESTS - base_shot < wave) ? (PP_NUM_TESTS - base_shot) : wave;
            if (t == 0) dev_squeeze_wave(&sq, wbytes, n_this * 64);
            __syncthreads();

            bool active = t < n_this;
            u64 jx[4], jy[4], jz[4], kx[4], ky[4], kz[4], num[4], za[4], den[4];
            bool skip = true;
            if (active) {
                dev_stage1(&wbytes[t * 64], jx, jy, jz, kx, ky, kz, num, za, den, &skip);
            } else {
                za[0] = 1; za[1] = za[2] = za[3] = 0;
                den[0] = 1; den[1] = den[2] = den[3] = 0;
            }
            u64 za_inv[4], den_inv[4];
            block_batch_inv2(za, den, za_inv, den_inv, scan, rscan, shared_inv);
            if (active && !skip) {
                u32 mask = dev_stage2(jx, jy, jz, kx, ky, kz, num, za_inv, den_inv,
                                      signs_d, signs_m, ws);
                if (mask != 0) {
                    hard_flag = 1;
                    my_faults++;
                }
            }
            my_waves++;
            __syncthreads();
        }
        if (t == 0) {
            pp_atomic_add_u64(waves_done, my_waves);
            pp_atomic_add_u64(fault_counter, my_faults);
            if (!hard_flag) {
                u32 pos = atomicAdd(out_cnt, 1u);
                if (pos < (u32)max_out) out_list[pos] = nonce;
            }
        }
        __syncthreads();
    }
}

// ─── fixture harness kernel: one nonce, ALL shots, no early exit ───────────
// Writes per-shot masks (post-skip indexed, matching oracle faultshots) and
// optionally corpus values for one shot.
__global__ void harness_kernel(u64 nonce, u32* masks, int* nsaved_out,
                               u64* shot_dump, int dump_idx) {
    extern __shared__ unsigned char smem[];
    int t = threadIdx.x;
    int wave = blockDim.x;
    u8* wbytes = smem;
    u64* scan = (u64*)(wbytes + wave * 64);
    u64* rscan = scan + 2 * wave * 4;
    u64* shared_inv = rscan + 2 * wave * 4;
    u64* signs_all = shared_inv + 4;
    u64* signs_d = &signs_all[t * 11];
    u64* signs_m = &signs_all[wave * 11 + t * 11];
    int* skipflags = (int*)&signs_all[2 * wave * 11];
    __shared__ PP_Shake sq;
    __shared__ int saved_base;
    __shared__ u16 ws[700];
    for (int i = t; i < 700; i += wave) ws[i] = PP_WIDTH_SCHEDULE_D[i];

    if (t == 0) {
        dev_nonce_absorb(&sq, nonce);
        saved_base = 0;
    }
    __syncthreads();
    int dump_lane_target = dump_idx; // post-skip index to dump
    for (int base_shot = 0; base_shot < PP_NUM_TESTS; base_shot += wave) {
        int n_this = (PP_NUM_TESTS - base_shot < wave) ? (PP_NUM_TESTS - base_shot) : wave;
        if (t == 0) dev_squeeze_wave(&sq, wbytes, n_this * 64);
        __syncthreads();

        bool active = t < n_this;
        u64 jx[4], jy[4], jz[4], kx[4], ky[4], kz[4], num[4], za[4], den[4];
        bool skip = true;
        if (active) {
            dev_stage1(&wbytes[t * 64], jx, jy, jz, kx, ky, kz, num, za, den, &skip);
        } else {
            za[0] = 1; za[1] = za[2] = za[3] = 0;
            den[0] = 1; den[1] = den[2] = den[3] = 0;
        }
        u64 za_inv[4], den_inv[4];
        block_batch_inv2(za, den, za_inv, den_inv, scan, rscan, shared_inv);

        // post-skip index of this lane's shot: saved_base + number of
        // non-skipped active lanes with lower thread id
        skipflags[t] = (active && !skip) ? 1 : 0;
        __syncthreads();
        int prefix = 0;
        for (int i = 0; i < t; i++) prefix += skipflags[i];
        int nlive = 0;
        for (int i = 0; i < wave; i++) nlive += skipflags[i];
        __syncthreads();

        if (active && !skip) {
            int corpus_idx = saved_base + prefix;
            u32 mask = dev_stage2(jx, jy, jz, kx, ky, kz, num, za_inv, den_inv,
                                  signs_d, signs_m, ws);
            masks[corpus_idx] = mask;
            if (shot_dump && corpus_idx == dump_lane_target) {
                // recompute affine values for the dump
                u64 zt_inv[4], zo_inv[4], tt[4];
                pp_fmul(za_inv, kz, zt_inv);
                pp_fmul(za_inv, jz, zo_inv);
                u64 zti2[4], zti3[4], zoi2[4], zoi3[4];
                pp_fsq(zt_inv, zti2);
                pp_fmul(zti2, zt_inv, zti3);
                pp_fsq(zo_inv, zoi2);
                pp_fmul(zoi2, zo_inv, zoi3);
                u64* tx = shot_dump;
                u64* ty = shot_dump + 4;
                u64* ox = shot_dump + 8;
                u64* oy = shot_dump + 12;
                u64* lam = shot_dump + 16;
                pp_fmul(jx, zti2, tx);
                pp_fmul(jy, zti3, ty);
                pp_fmul(kx, zoi2, ox);
                pp_fmul(ky, zoi3, oy);
                pp_fmul(num, den_inv, tt);
                pp_fmul(tt, za_inv, lam);
            }
        }
        __syncthreads();
        if (t == 0) saved_base += nlive;
        __syncthreads();
    }
    if (t == 0) *nsaved_out = saved_base;
}

// ─── probe kernel: dump the first 128 squeezed bytes of a nonce ────────────
__global__ void probe_bytes_kernel(u64 nonce, u8* out) {
    __shared__ PP_Shake sq;
    if (threadIdx.x == 0) {
        dev_nonce_absorb(&sq, nonce);
        u8 buf[136];
        int done = 0;
        while (done < 128) {
            if (sq.pos == PP_RATE) {
                pp_keccak_f(sq.st);
                sq.pos = 0;
            }
            buf[done++] = pp_shake_get_byte(&sq, sq.pos);
            sq.pos++;
        }
        for (int i = 0; i < 128; i++) out[i] = buf[i];
    }
}

// ─── probe kernel: Jacobian comb-mul results for shot 0 ────────────────────
__global__ void probe_jac_kernel(u64 nonce, u64* out) {
    __shared__ PP_Shake sq;
    __shared__ u8 kb[64];
    if (threadIdx.x == 0) {
        dev_nonce_absorb(&sq, nonce);
        dev_squeeze_wave(&sq, kb, 64);
    }
    __syncthreads();
    if (threadIdx.x == 0) {
        PP_Jac tj, oj;
        dev_comb_mul(kb, &tj);
        dev_comb_mul(kb + 32, &oj);
        for (int i = 0; i < 4; i++) {
            out[i] = tj.x[i];
            out[4 + i] = tj.y[i];
            out[8 + i] = tj.z[i];
            out[12 + i] = oj.x[i];
            out[16 + i] = oj.y[i];
            out[20 + i] = oj.z[i];
        }
    }
}

// ─── host ───────────────────────────────────────────────────────────────────

static void limbs_hex(const u64 a[4], char* out) {
    sprintf(out, "%016llx%016llx%016llx%016llx", (unsigned long long)a[3],
            (unsigned long long)a[2], (unsigned long long)a[1],
            (unsigned long long)a[0]);
}

int main(int argc, char** argv) {
    const char* ops = nullptr;
    u64 from = 0, to = 0;
    int wave = 128;
    int blocks = 0; // 0 = auto
    int comb_bits = 16;
    u64 faultshots_nonce = ~0ULL;
    u64 shot_nonce = ~0ULL;
    int shot_idx = -1;
    u64 breakdown_nonce = ~0ULL;
    u64 probe_bytes_nonce = ~0ULL;
    u64 probe_jac_nonce = ~0ULL;
    bool probe_batchinv = false;
    bool requested_range = false;

    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        auto next = [&]() -> const char* { return i + 1 < argc ? argv[++i] : nullptr; };
        if (a == "--ops") ops = next();
        else if (a == "--from") { from = strtoull(next(), 0, 10); requested_range = true; }
        else if (a == "--to") { to = strtoull(next(), 0, 10); requested_range = true; }
        else if (a == "--threads-block") wave = atoi(next());
        else if (a == "--blocks") blocks = atoi(next());
        else if (a == "--comb-bits") comb_bits = atoi(next());
        else if (a == "--faultshots") faultshots_nonce = strtoull(next(), 0, 10);
        else if (a == "--shot") {
            shot_nonce = strtoull(next(), 0, 10);
            shot_idx = atoi(next());
        } else if (a == "--breakdown") breakdown_nonce = strtoull(next(), 0, 10);
        else if (a == "--probe-bytes") probe_bytes_nonce = strtoull(next(), 0, 10);
        else if (a == "--probe-jac") probe_jac_nonce = strtoull(next(), 0, 10);
        else if (a == "--probe-batchinv") probe_batchinv = true;
        else {
            fprintf(stderr, "ppgpu: unknown arg %s\n", a.c_str());
            return 2;
        }
    }
    if (!ops) {
        fprintf(stderr,
                "usage: ppgpu --ops OPS.bin (--from A --to B | --faultshots N | "
                "--shot N IDX | --breakdown N) [--threads-block 128] [--blocks N] "
                "[--comb-bits 8|16]\n");
        return 2;
    }
#if !defined(PP_ENABLE_RANGE_SCAN)
    if (requested_range) {
        fprintf(stderr, "ppgpu: range scan disabled in qualification build\n");
        return 2;
    }
#endif
    if (wave < 32) wave = 32;
    if (wave > MAX_WAVE) wave = MAX_WAVE;
    if (wave % 32) wave = ((wave + 31) / 32) * 32;
    if (comb_bits != 8 && comb_bits != 16) comb_bits = 16;

    // host prefix load (includes the op-count fingerprint guard)
    PP_Prefix prefix;
    pp_load_prefix(ops, &prefix);
    fprintf(stderr, "ppgpu: ops=%s total_ops=%llu state_digest=%016llx\n", ops,
            (unsigned long long)prefix.total_ops, (unsigned long long)pp_state_digest(&prefix));

    // comb table on host
    std::vector<u64> comb;
    pp_build_comb(comb);
    fprintf(stderr, "ppgpu: comb8 built\n");

    // upload constants
    cudaMemcpyToSymbol(PP_WIDTH_SCHEDULE_D, PP_WIDTH_SCHEDULE,
                       sizeof(u16) * 700);
    cudaMemcpyToSymbol(d_base_st, prefix.checkpoint.st, 200);
    cudaMemcpyToSymbol(d_base_n, &prefix.checkpoint.n, 4);
    cudaMemcpyToSymbol(d_tail, prefix.tail, 96 * PP_OP_BYTES);
    u64* dc;
    cudaMalloc(&dc, comb.size() * 8);
    cudaMemcpy(dc, comb.data(), comb.size() * 8, cudaMemcpyHostToDevice);
    cudaMemcpyToSymbol(d_comb, &dc, sizeof(dc));

    u64* dc16 = nullptr;
    if (comb_bits == 16) {
        size_t bytes = 16ull * 65535ull * 8 * sizeof(u64);
        cudaError_t ce = cudaMalloc(&dc16, bytes);
        if (ce) {
            fprintf(stderr, "ppgpu: comb16 malloc failed: %s\n", cudaGetErrorString(ce));
            return 1;
        }
        build_comb16_kernel<<<2048, 256>>>(dc, dc16);
        ce = cudaDeviceSynchronize();
        if (ce) {
            fprintf(stderr, "ppgpu: comb16 build failed: %s\n", cudaGetErrorString(ce));
            return 1;
        }
        fprintf(stderr, "ppgpu: comb16 built (%.1f MiB)\n", bytes / 1048576.0);
    }
    cudaMemcpyToSymbol(d_comb16, &dc16, sizeof(dc16));
    cudaMemcpyToSymbol(d_comb_bits, &comb_bits, 4);

    if (probe_bytes_nonce != ~0ULL) {
        u8* dout;
        cudaMalloc(&dout, 128);
        probe_bytes_kernel<<<1, 32>>>(probe_bytes_nonce, dout);
        cudaError_t ce = cudaDeviceSynchronize();
        if (ce) {
            fprintf(stderr, "ppgpu: probe kernel failed: %s\n", cudaGetErrorString(ce));
            return 1;
        }
        u8 h[128];
        cudaMemcpy(h, dout, 128, cudaMemcpyDeviceToHost);
        for (int i = 0; i < 128; i++) printf("%02x", h[i]);
        printf("\n");
        return 0;
    }
    if (probe_jac_nonce != ~0ULL) {
        u64* dout;
        cudaMalloc(&dout, 24 * 8);
        probe_jac_kernel<<<1, 32>>>(probe_jac_nonce, dout);
        cudaError_t ce = cudaDeviceSynchronize();
        if (ce) {
            fprintf(stderr, "ppgpu: probe-jac kernel failed: %s\n", cudaGetErrorString(ce));
            return 1;
        }
        u64 h[24];
        cudaMemcpy(h, dout, 24 * 8, cudaMemcpyDeviceToHost);
        const char* names[6] = {"jx", "jy", "jz", "kx", "ky", "kz"};
        for (int f = 0; f < 6; f++) {
            char hx[80];
            limbs_hex(h + 4 * f, hx);
            printf("%s=%s\n", names[f], hx);
        }
        return 0;
    }

    size_t shmem = shmem_bytes(wave);
    cudaFuncSetAttribute(scan_kernel, cudaFuncAttributeMaxDynamicSharedMemorySize,
                         (int)shmem);
    cudaFuncSetAttribute(harness_kernel, cudaFuncAttributeMaxDynamicSharedMemorySize,
                         (int)shmem);
    if (blocks <= 0) {
        int dev, nsm;
        cudaGetDevice(&dev);
        cudaDeviceGetAttribute(&nsm, cudaDevAttrMultiProcessorCount, dev);
        blocks = nsm * 4;
    }

    if (probe_batchinv) {
        int w = wave;
        u64* dout;
        cudaMalloc(&dout, (size_t)w * 8 * 8 + 64);
        cudaMemset(dout, 0, (size_t)w * 8 * 8 + 64);
        size_t bsh = (size_t)(2 * w * 4) * 8 * 2 + 32;
        probe_batchinv_kernel<<<1, w, bsh>>>(dout);
        cudaError_t ce = cudaDeviceSynchronize();
        if (ce) {
            fprintf(stderr, "ppgpu: probe-batchinv failed: %s\n", cudaGetErrorString(ce));
            return 1;
        }
        std::vector<u64> h((size_t)w * 8 + 8);
        cudaMemcpy(h.data(), dout, (size_t)w * 8 * 8 + 64, cudaMemcpyDeviceToHost);
        {
            char hx[80];
            limbs_hex(&h[1024], hx);
            printf("direct finv check (want 1): %s\n", hx);
        }
        int bad = 0;
        for (int i = 0; i < w; i++) {
            bool ok1 = h[i * 8] == 1 && h[i * 8 + 1] == 0 && h[i * 8 + 2] == 0 &&
                       h[i * 8 + 3] == 0;
            bool ok2 = h[i * 8 + 4] == 1 && h[i * 8 + 5] == 0 && h[i * 8 + 6] == 0 &&
                       h[i * 8 + 7] == 0;
            if (!ok1 || !ok2) {
                if (bad < 5) {
                    char hx[80];
                    limbs_hex(&h[i * 8], hx);
                    printf("lane %d c1=%s\n", i, hx);
                    limbs_hex(&h[i * 8 + 4], hx);
                    printf("lane %d c2=%s\n", i, hx);
                }
                bad++;
            }
        }
        printf("probe-batchinv: %s (%d/%d bad)\n", bad == 0 ? "OK" : "FAIL", bad, w);
        return bad == 0 ? 0 : 1;
    }

    if (faultshots_nonce != ~0ULL || shot_nonce != ~0ULL || breakdown_nonce != ~0ULL) {
        u64 nonce = faultshots_nonce != ~0ULL ? faultshots_nonce
                    : shot_nonce != ~0ULL   ? shot_nonce
                                            : breakdown_nonce;
        u32* dmasks;
        cudaMalloc(&dmasks, PP_NUM_TESTS * 4);
        cudaMemset(dmasks, 0, PP_NUM_TESTS * 4);
        int* dnsaved;
        cudaMalloc(&dnsaved, 4);
        u64* ddump = nullptr;
        u64 hdump[20];
        if (shot_nonce != ~0ULL) {
            cudaMalloc(&ddump, 20 * 8);
            cudaMemset(ddump, 0, 20 * 8);
        }
        harness_kernel<<<1, wave, shmem>>>(nonce, dmasks, dnsaved, ddump, shot_idx);
        cudaError_t ce = cudaDeviceSynchronize();
        if (ce) {
            fprintf(stderr, "ppgpu: harness kernel failed: %s\n", cudaGetErrorString(ce));
            return 1;
        }
        int nsaved = 0;
        cudaMemcpy(&nsaved, dnsaved, 4, cudaMemcpyDeviceToHost);
        if (shot_nonce != ~0ULL) {
            cudaMemcpy(hdump, ddump, 20 * 8, cudaMemcpyDeviceToHost);
            char hx[80];
            u32* hmasks = (u32*)malloc(PP_NUM_TESTS * 4);
            cudaMemcpy(hmasks, dmasks, PP_NUM_TESTS * 4, cudaMemcpyDeviceToHost);
            printf("shot %d mask=%u\n", shot_idx,
                   shot_idx >= 0 && shot_idx < nsaved ? hmasks[shot_idx] : 0);
            limbs_hex(hdump, hx); printf("tx=%s\n", hx);
            limbs_hex(hdump + 4, hx); printf("ty=%s\n", hx);
            limbs_hex(hdump + 8, hx); printf("ox=%s\n", hx);
            limbs_hex(hdump + 12, hx); printf("oy=%s\n", hx);
            limbs_hex(hdump + 16, hx); printf("lam=%s\n", hx);
            free(hmasks);
            return 0;
        }
        if (faultshots_nonce != ~0ULL) {
            u32* hmasks = (u32*)malloc(PP_NUM_TESTS * 4);
            cudaMemcpy(hmasks, dmasks, PP_NUM_TESTS * 4, cudaMemcpyDeviceToHost);
            for (int i = 0; i < nsaved; i++)
                if (hmasks[i] != 0) printf("%d %u\n", i, hmasks[i]);
            free(hmasks);
            return 0;
        }
        // breakdown
        u32* hmasks = (u32*)malloc(PP_NUM_TESTS * 4);
        cudaMemcpy(hmasks, dmasks, PP_NUM_TESTS * 4, cudaMemcpyDeviceToHost);
        u64 br[5] = {0, 0, 0, 0, 0};
        u64 pred = 0;
        long first = -1;
        for (int i = 0; i < nsaved; i++) {
            u32 m = hmasks[i];
            if (m) {
                if (first < 0) first = i;
                pred++;
                br[0] += (m & PP_F_WALK_DIV) != 0;
                br[1] += (m & PP_F_REPLAY_DIV) != 0;
                br[2] += (m & PP_F_WALK_MUL) != 0;
                br[3] += (m & PP_F_REPLAY_MUL) != 0;
                br[4] += (m & PP_F_RESULT) != 0;
            }
        }
        printf("nonce %llu pred_cls=%llu walk_div=%llu replay_div=%llu walk_mul=%llu "
               "replay_mul=%llu result=%llu shots=%d first=%ld\n",
               (unsigned long long)nonce, (unsigned long long)pred,
               (unsigned long long)br[0], (unsigned long long)br[1],
               (unsigned long long)br[2], (unsigned long long)br[3],
               (unsigned long long)br[4], nsaved, first);
        free(hmasks);
        return 0;
    }

    if (to <= from) {
        fprintf(stderr, "ppgpu: --to must exceed --from\n");
        return 2;
    }
    u64 count = to - from;

    u32* dcnt;
    cudaMalloc(&dcnt, 4);
    cudaMemset(dcnt, 0, 4);
    const int MAXOUT = 65536;
    u64* dlist;
    cudaMalloc(&dlist, MAXOUT * 8);
    u64* dwaves;
    cudaMalloc(&dwaves, 8);
    cudaMemset(dwaves, 0, 8);
    u64* dfaults;
    cudaMalloc(&dfaults, 8);
    cudaMemset(dfaults, 0, 8);

    fprintf(stderr, "ppgpu: scan [%llu,%llu) blocks=%d wave=%d shmem=%zu comb_bits=%d\n",
            (unsigned long long)from, (unsigned long long)to, blocks, wave, shmem,
            comb_bits);
    cudaEvent_t t0, t1;
    cudaEventCreate(&t0);
    cudaEventCreate(&t1);
    cudaEventRecord(t0);
    scan_kernel<<<blocks, wave, shmem>>>(from, count, dcnt, dlist, MAXOUT, dwaves,
                                         dfaults);
    cudaError_t ce = cudaDeviceSynchronize();
    cudaEventRecord(t1);
    cudaEventSynchronize(t1);
    if (ce) {
        fprintf(stderr, "ppgpu: scan kernel failed: %s\n", cudaGetErrorString(ce));
        return 1;
    }
    float ms = 0;
    cudaEventElapsedTime(&ms, t0, t1);
    u32 cnt;
    cudaMemcpy(&cnt, dcnt, 4, cudaMemcpyDeviceToHost);
    u64 hwaves, hfaults;
    cudaMemcpy(&hwaves, dwaves, 8, cudaMemcpyDeviceToHost);
    cudaMemcpy(&hfaults, dfaults, 8, cudaMemcpyDeviceToHost);
    if (cnt > (u32)MAXOUT) {
        fprintf(stderr, "ppgpu: FATAL output overflow (%u > %d)\n", cnt, MAXOUT);
        return 3;
    }
    std::vector<u64> hlist(cnt);
    cudaMemcpy(hlist.data(), dlist, cnt * 8, cudaMemcpyDeviceToHost);
    for (u32 i = 0; i < cnt; i++) printf("%llu pred_cls=0\n", (unsigned long long)hlist[i]);
    double secs = ms / 1000.0;
    fprintf(stderr,
            "TELEMETRY {\"from\":%llu,\"to\":%llu,\"count\":%llu,\"blocks\":%d,"
            "\"wave\":%d,\"comb_bits\":%d,\"kernel_ms\":%.1f,\"nonces_per_s\":%.1f,"
            "\"waves\":%llu,\"fault_shots\":%llu,\"survivors\":%u,"
            "\"state_digest\":\"%016llx\"}\n",
            (unsigned long long)from, (unsigned long long)to, (unsigned long long)count,
            blocks, wave, comb_bits, ms, count / secs, (unsigned long long)hwaves,
            (unsigned long long)hfaults, cnt, (unsigned long long)pp_state_digest(&prefix));
    return 0;
}
