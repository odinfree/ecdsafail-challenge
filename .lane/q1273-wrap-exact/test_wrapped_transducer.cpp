#include <cstdio>
#include <cstring>

#include "../q1273-predictor/src/pp_model.h"

static u64 next_word(u64* state) {
    u64 x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *state = x;
    return x;
}

static bool equal4(const u64 a[4], const u64 b[4]) {
    return a[0] == b[0] && a[1] == b[1] && a[2] == b[2] && a[3] == b[3];
}

static bool run_direction(const u64 a[4], int rounds, unsigned long long* checked) {
    PP_WalkOut fast = pp_walk(a, rounds);
    if (fast.fault || !fast.term_ok || pp_walkback_fold_fault(a)) return true;

    u64 signs[11], restored[4];
    bool u_neg, v_neg;
    pp_walk_wrapped_restore(a, rounds, signs, &u_neg, &v_neg, restored,
                            PP_WIDTH_SCHEDULE);
    (*checked)++;
    return std::memcmp(signs, fast.signs, sizeof(signs)) == 0 &&
           u_neg == fast.u_neg && v_neg == fast.v_neg && equal4(restored, a);
}

int main() {
    u64 state = 0x514c313237335752ULL;
    unsigned long long checked_div = 0, checked_mul = 0;
    for (int fixture = 0; fixture < 4096; fixture++) {
        u64 raw[4], a[4];
        for (int limb = 0; limb < 4; limb++) raw[limb] = next_word(&state);
        PP_P4(prime);
        if (pp_ge(raw, prime)) {
            u64 borrow;
            pp_sub_limbs(raw, prime, a, &borrow);
        } else {
            std::memcpy(a, raw, sizeof(a));
        }
        if (pp_is_zero(a)) a[0] = 1;
        if (!run_direction(a, PP_ROUNDS_DIV, &checked_div)) {
            std::fprintf(stderr, "divide miter failed at fixture %d\n", fixture);
            return 1;
        }
        if (!run_direction(a, PP_ROUNDS_MUL, &checked_mul)) {
            std::fprintf(stderr, "multiply miter failed at fixture %d\n", fixture);
            return 1;
        }
    }
    if (checked_div < 4000 || checked_mul < 4000) {
        std::fprintf(stderr, "insufficient clean fixtures: div=%llu mul=%llu\n",
                     checked_div, checked_mul);
        return 2;
    }
    std::printf("PASS fixtures=4096 clean_div=%llu clean_mul=%llu\n", checked_div,
                checked_mul);
    return 0;
}
