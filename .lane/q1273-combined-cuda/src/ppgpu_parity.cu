// Bounded CUDA parity transport for the committed Q1273 combined predictor.
//
// This binary intentionally has no nonce-range, early-exit, screen, survivor,
// or approximate mode. The exact source-bound host loader derives one explicit
// 9,024-shot corpus. Device code evaluates the same committed PP_HD model and
// returns complete classical or conditional-phase masks for byte comparison.

#include "SEALED_BINDING.h"

#include <algorithm>
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include <cuda_runtime.h>

#include "../../q1273-predictor/src/pp_host.h"
#include "../../q1273-phase/src/pp_phase_schedule.h"

#define CUDA_OK(call)                                                            \
    do {                                                                         \
        cudaError_t q1273_cuda_error = (call);                                   \
        if (q1273_cuda_error != cudaSuccess) {                                   \
            fprintf(stderr, "ppgpu: CUDA failure at %s:%d: %s\n", __FILE__,   \
                    __LINE__, cudaGetErrorString(q1273_cuda_error));              \
            exit(3);                                                             \
        }                                                                        \
    } while (0)

static const char* ops_path() {
    const char* p = getenv("PPF_OPS");
    return p ? p : "ops.bin";
}

static bool parse_nonce(const char* text, u64* out) {
    if (text == nullptr || *text == '\0' || (text[0] == '0' && text[1] != '\0')) {
        return false;
    }
    for (const char* p = text; *p != '\0'; p++) {
        if (*p < '0' || *p > '9') return false;
    }
    errno = 0;
    char* end = nullptr;
    unsigned long long value = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0' || value >= (1ULL << 48)) {
        return false;
    }
    *out = (u64)value;
    return true;
}

static int device_from_env() {
    const char* text = getenv("PP_CUDA_DEVICE");
    if (text == nullptr || *text == '\0') return 0;
    u64 value = 0;
    if (!parse_nonce(text, &value) || value > 63) {
        fprintf(stderr, "ppgpu: PP_CUDA_DEVICE must be a canonical integer in [0,63]\n");
        exit(2);
    }
    return (int)value;
}

__global__ void classical_mask_kernel(const PP_Shot* shots, size_t count, u32* masks) {
    size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count) return;
    const PP_Shot& shot = shots[i];
    masks[i] = pp_shot_fault_mask(shot.tx, shot.ty, shot.ox, shot.oy, shot.lam);
}

__global__ void phase_trace_kernel(const PP_Shot* shots, size_t count,
                                   const u8* families, u32* masks, u8* values,
                                   int* trace_counts, u8* invalid) {
    size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count) return;
    u8* trace_values = values + i * (size_t)PP_PHASE_SITE_COUNT;
    PP_PhaseTrace trace{trace_values, families, PP_PHASE_SITE_COUNT, 0, false};
    const PP_Shot& shot = shots[i];
    masks[i] = pp_shot_fault_phase_trace(shot.tx, shot.ty, shot.ox, shot.oy,
                                         shot.lam, &trace);
    trace_counts[i] = trace.count;
    invalid[i] = trace.invalid ? 1u : 0u;
}

struct DeviceBuffer {
    void* ptr = nullptr;
    DeviceBuffer() = default;
    DeviceBuffer(const DeviceBuffer&) = delete;
    DeviceBuffer& operator=(const DeviceBuffer&) = delete;
    ~DeviceBuffer() {
        if (ptr != nullptr) cudaFree(ptr);
    }
    void allocate(size_t bytes) { CUDA_OK(cudaMalloc(&ptr, bytes)); }
};

static void select_device() {
    int device = device_from_env();
    int count = 0;
    CUDA_OK(cudaGetDeviceCount(&count));
    if (device < 0 || device >= count) {
        fprintf(stderr, "ppgpu: CUDA device %d unavailable (count=%d)\n", device, count);
        exit(2);
    }
    CUDA_OK(cudaSetDevice(device));
}

static int shaketest() {
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

static void derive_exact_corpus(const PP_Prefix* prefix, const u64* comb, u64 nonce,
                                PP_Shake* phase_shake, std::vector<PP_Shot>* shots) {
    pp_nonce_shake(prefix, nonce, phase_shake);
    pp_derive_corpus_batch(phase_shake, PP_NUM_TESTS, comb, *shots);
    if (shots->size() != PP_NUM_TESTS || shots->size() % 64 != 0) {
        fprintf(stderr, "ppgpu: FATAL: corpus size %zu != exact %d\n",
                shots->size(), PP_NUM_TESTS);
        exit(2);
    }
}

static std::vector<u32> device_classical_masks(const std::vector<PP_Shot>& shots) {
    select_device();
    DeviceBuffer dshots;
    DeviceBuffer dmasks;
    dshots.allocate(shots.size() * sizeof(PP_Shot));
    dmasks.allocate(shots.size() * sizeof(u32));
    CUDA_OK(cudaMemcpy(dshots.ptr, shots.data(), shots.size() * sizeof(PP_Shot),
                       cudaMemcpyHostToDevice));
    const int threads = 128;
    const int blocks = (int)((shots.size() + threads - 1) / threads);
    classical_mask_kernel<<<blocks, threads>>>((const PP_Shot*)dshots.ptr, shots.size(),
                                                (u32*)dmasks.ptr);
    CUDA_OK(cudaDeviceSynchronize());
    std::vector<u32> masks(shots.size());
    CUDA_OK(cudaMemcpy(masks.data(), dmasks.ptr, masks.size() * sizeof(u32),
                       cudaMemcpyDeviceToHost));
    return masks;
}

struct PhaseDeviceResult {
    std::vector<u32> masks;
    std::vector<u8> values;
    std::vector<int> counts;
    std::vector<u8> invalid;
};

static PhaseDeviceResult device_phase_traces(const std::vector<PP_Shot>& shots) {
    select_device();
    std::vector<u8> families(PP_PHASE_FAMILIES,
                             PP_PHASE_FAMILIES + PP_PHASE_SITE_COUNT);
#ifdef PP_PHASE_FORCE_BAD_SCHEDULE
    families[0] ^= 1u;
#endif
    size_t values_size = shots.size() * (size_t)PP_PHASE_SITE_COUNT;
    DeviceBuffer dshots;
    DeviceBuffer dfamilies;
    DeviceBuffer dmasks;
    DeviceBuffer dvalues;
    DeviceBuffer dcounts;
    DeviceBuffer dinvalid;
    dshots.allocate(shots.size() * sizeof(PP_Shot));
    dfamilies.allocate(families.size());
    dmasks.allocate(shots.size() * sizeof(u32));
    dvalues.allocate(values_size);
    dcounts.allocate(shots.size() * sizeof(int));
    dinvalid.allocate(shots.size());
    CUDA_OK(cudaMemcpy(dshots.ptr, shots.data(), shots.size() * sizeof(PP_Shot),
                       cudaMemcpyHostToDevice));
    CUDA_OK(cudaMemcpy(dfamilies.ptr, families.data(), families.size(),
                       cudaMemcpyHostToDevice));
    CUDA_OK(cudaMemset(dvalues.ptr, 0, values_size));
    const int threads = 128;
    const int blocks = (int)((shots.size() + threads - 1) / threads);
    phase_trace_kernel<<<blocks, threads>>>(
        (const PP_Shot*)dshots.ptr, shots.size(), (const u8*)dfamilies.ptr,
        (u32*)dmasks.ptr, (u8*)dvalues.ptr, (int*)dcounts.ptr, (u8*)dinvalid.ptr);
    CUDA_OK(cudaDeviceSynchronize());
    PhaseDeviceResult out;
    out.masks.resize(shots.size());
    out.values.resize(values_size);
    out.counts.resize(shots.size());
    out.invalid.resize(shots.size());
    CUDA_OK(cudaMemcpy(out.masks.data(), dmasks.ptr, out.masks.size() * sizeof(u32),
                       cudaMemcpyDeviceToHost));
    CUDA_OK(cudaMemcpy(out.values.data(), dvalues.ptr, out.values.size(),
                       cudaMemcpyDeviceToHost));
    CUDA_OK(cudaMemcpy(out.counts.data(), dcounts.ptr, out.counts.size() * sizeof(int),
                       cudaMemcpyDeviceToHost));
    CUDA_OK(cudaMemcpy(out.invalid.data(), dinvalid.ptr, out.invalid.size(),
                       cudaMemcpyDeviceToHost));
    return out;
}

static int faultshots(const PP_Prefix* prefix, const u64* comb, u64 nonce) {
    PP_Shake shake;
    std::vector<PP_Shot> shots;
    derive_exact_corpus(prefix, comb, nonce, &shake, &shots);
    std::vector<u32> masks = device_classical_masks(shots);
    size_t faults = 0;
    for (size_t i = 0; i < masks.size(); i++) {
        if (masks[i] != 0) {
            printf("%zu %u\n", i, masks[i]);
            faults++;
        }
    }
    fprintf(stderr,
            "ppgpu faultshots: source=%s combined=%s nonce=%llu shots=%zu "
            "classical=%zu range=disabled\n",
            PP_SOURCE_COMMIT, Q1273_COMBINED_CPU_GO_COMMIT,
            (unsigned long long)nonce, shots.size(), faults);
    return 0;
}

static int phasefaultshots(const PP_Prefix* prefix, const u64* comb, u64 nonce) {
    PP_Shake shake;
    std::vector<PP_Shot> shots;
    derive_exact_corpus(prefix, comb, nonce, &shake, &shots);
    PhaseDeviceResult device = device_phase_traces(shots);
    std::vector<u64> predicates(PP_PHASE_SITE_COUNT);
    std::vector<size_t> clean_phase_shots;
    const size_t rng_words_per_block = 8192;
    std::vector<u8> rng_block(rng_words_per_block * 8);
    u64 classical_faults = 0;

    for (size_t batch = 0; batch < shots.size() / 64; batch++) {
        std::fill(predicates.begin(), predicates.end(), 0);
        u64 classical_mask = 0;
        for (int lane = 0; lane < 64; lane++) {
            size_t shot = batch * 64 + (size_t)lane;
            if (device.masks[shot] != 0) {
                classical_mask |= 1ULL << lane;
                classical_faults++;
                continue;
            }
            if (device.invalid[shot] || device.counts[shot] != PP_PHASE_SITE_COUNT) {
                fprintf(stderr,
                        "ppgpu: FATAL: phase schedule mismatch at shot %zu: "
                        "count=%d expected=%d invalid=%u\n",
                        shot, device.counts[shot], PP_PHASE_SITE_COUNT,
                        (unsigned)device.invalid[shot]);
                return 2;
            }
            const u8* values = device.values.data() + shot * (size_t)PP_PHASE_SITE_COUNT;
            for (int site = 0; site < PP_PHASE_SITE_COUNT; site++) {
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
                    fprintf(stderr, "ppgpu: FATAL: non-monotone phase schedule\n");
                    return 2;
                }
                u64 rng;
                memcpy(&rng, rng_block.data() + (size_t)(ordinal - base) * 8, 8);
                phase_mask ^= predicates[next_site] & rng;
                next_site++;
            }
        }
        if (next_site != PP_PHASE_SITE_COUNT) {
            fprintf(stderr, "ppgpu: FATAL: phase schedule exceeds R/Hmr stream: %d/%d\n",
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
            "ppgpu phasefaultshots: source=%s combined=%s nonce=%llu shots=%zu "
            "classical=%llu clean_phase=%zu survivor=%d "
            "contract=phase&~classical raw_phase=not-claimed cuda_phase=parity-only "
            "range=disabled\n",
            PP_SOURCE_COMMIT, Q1273_COMBINED_CPU_GO_COMMIT,
            (unsigned long long)nonce, shots.size(),
            (unsigned long long)classical_faults, clean_phase_shots.size(),
            classical_faults == 0 && clean_phase_shots.empty() ? 1 : 0);
    return 0;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr,
                "usage: ppgpu shaketest | identity | statedigest | "
                "faultshots NONCE | phasefaultshots NONCE\n");
        return 2;
    }
    std::string mode = argv[1];
    if (mode == "scan") {
        fprintf(stderr, "ppgpu: scan mode disabled in bounded parity build\n");
        return 2;
    }
    if (mode == "shaketest") {
        if (argc != 2) {
            fprintf(stderr, "ppgpu: unexpected shaketest arguments\n");
            return 2;
        }
        return shaketest();
    }

    u64 nonce = 0;
    if (mode == "faultshots" || mode == "phasefaultshots") {
        if (argc != 3 || !parse_nonce(argv[2], &nonce)) {
            fprintf(stderr, "ppgpu: expected one canonical 48-bit nonce\n");
            return 2;
        }
    } else if ((mode == "identity" || mode == "statedigest") && argc != 2) {
        fprintf(stderr, "ppgpu: unexpected arguments for %s\n", mode.c_str());
        return 2;
    } else if (mode != "identity" && mode != "statedigest") {
        fprintf(stderr, "ppgpu: unknown bounded selector %s\n", mode.c_str());
        return 2;
    }

    PP_Prefix prefix;
    pp_load_prefix(ops_path(), &prefix);
    if (mode == "identity") {
        printf("source_commit=%s ops_count=%llu ops_sha256=%s predictor_digest=%016llx "
               "combined_cpu_commit=%s combined_host_sha256=%s combined_model_sha256=%s "
               "combined_cpu_sha256=%s phase_meta_sha256=%s phase_sites=%d "
               "phase_rhmr=%d shots=%d scan=disabled range=unauthorized\n",
               PP_SOURCE_COMMIT, (unsigned long long)PP_EXPECTED_OPS,
               PP_EXPECTED_OPS_SHA256, (unsigned long long)pp_state_digest(&prefix),
               Q1273_COMBINED_CPU_GO_COMMIT, Q1273_COMBINED_HOST_SHA256,
               Q1273_COMBINED_MODEL_SHA256, Q1273_COMBINED_CPU_SHA256,
               PP_PHASE_META_SHA256, PP_PHASE_SITE_COUNT, PP_PHASE_RHMR_COUNT,
               PP_NUM_TESTS);
        return 0;
    }
    if (mode == "statedigest") {
        printf("%016llx\n", (unsigned long long)pp_state_digest(&prefix));
        return 0;
    }

    std::vector<u64> comb;
    pp_build_comb(comb);
    if (mode == "faultshots") return faultshots(&prefix, comb.data(), nonce);
    return phasefaultshots(&prefix, comb.data(), nonce);
}
