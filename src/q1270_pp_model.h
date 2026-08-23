#pragma once

// Target-native finite-width recurrence for circuit source 90770b1.
//
// This file is derived from src/point_add/pingpong_div.rs in the same tree.
// It contains no transferred predictor source, table, fixture, or output.

#include <openssl/bn.h>

#include <array>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <utility>

namespace q1270 {

inline void bn_require(int ok, const char* operation) {
    if (ok != 1) {
        throw std::runtime_error(std::string("OpenSSL BN failure: ") + operation);
    }
}

class Big {
  public:
    Big() : value_(BN_new()) {
        if (value_ == nullptr) throw std::bad_alloc();
        BN_zero(value_);
    }

    explicit Big(BIGNUM* value) : value_(value) {
        if (value_ == nullptr) throw std::bad_alloc();
    }

    Big(const Big& other) : Big(BN_dup(other.value_)) {}

    Big(Big&& other) noexcept : value_(std::exchange(other.value_, nullptr)) {}

    Big& operator=(Big other) noexcept {
        swap(other);
        return *this;
    }

    ~Big() { BN_free(value_); }

    void swap(Big& other) noexcept { std::swap(value_, other.value_); }
    BIGNUM* get() { return value_; }
    const BIGNUM* get() const { return value_; }

    static Big word(std::uint64_t value) {
        Big out;
        bn_require(BN_set_word(out.get(), static_cast<BN_ULONG>(value)), "BN_set_word");
        return out;
    }

    static Big hex(const char* text) {
        BIGNUM* raw = nullptr;
        if (BN_hex2bn(&raw, text) == 0 || raw == nullptr) {
            BN_free(raw);
            throw std::runtime_error("invalid frozen hexadecimal integer");
        }
        return Big(raw);
    }

    static Big power_of_two(unsigned bits) {
        Big out;
        bn_require(BN_set_bit(out.get(), static_cast<int>(bits)), "BN_set_bit power");
        return out;
    }

  private:
    BIGNUM* value_;
};

inline Big add(const Big& left, const Big& right) {
    Big out;
    bn_require(BN_add(out.get(), left.get(), right.get()), "BN_add");
    return out;
}

inline Big sub(const Big& left, const Big& right) {
    Big out;
    bn_require(BN_sub(out.get(), left.get(), right.get()), "BN_sub");
    return out;
}

inline Big shift_left(const Big& value, unsigned bits) {
    Big out;
    bn_require(BN_lshift(out.get(), value.get(), static_cast<int>(bits)), "BN_lshift");
    return out;
}

inline Big shift_right_exact(const Big& value, unsigned bits) {
    Big out;
    bn_require(BN_rshift(out.get(), value.get(), static_cast<int>(bits)), "BN_rshift");
    return out;
}

inline Big nonnegative_mod(const Big& value, const Big& modulus, BN_CTX* context) {
    Big out;
    bn_require(BN_nnmod(out.get(), value.get(), modulus.get(), context), "BN_nnmod");
    return out;
}

inline Big modulo_power(const Big& value, unsigned bits, BN_CTX* context) {
    return nonnegative_mod(value, Big::power_of_two(bits), context);
}

inline bool equal(const Big& left, const Big& right) {
    return BN_cmp(left.get(), right.get()) == 0;
}

inline bool is_zero(const Big& value) { return BN_is_zero(value.get()) == 1; }
inline bool is_negative(const Big& value) { return BN_is_negative(value.get()) == 1; }

inline bool unsigned_bit(const Big& value, unsigned bit) {
    if (is_negative(value)) throw std::runtime_error("unsigned_bit received a negative value");
    return BN_is_bit_set(value.get(), static_cast<int>(bit)) == 1;
}

inline bool signed_fits(const Big& value, unsigned width) {
    if (width == 0) return false;
    const Big limit = Big::power_of_two(width - 1);
    if (!is_negative(value)) return BN_cmp(value.get(), limit.get()) < 0;
    Big magnitude(value);
    BN_set_negative(magnitude.get(), 0);
    return BN_cmp(magnitude.get(), limit.get()) <= 0;
}

inline Big signed_twos(const Big& value, unsigned width, BN_CTX* context) {
    return modulo_power(value, width, context);
}

inline bool signed_bit(const Big& value, unsigned bit, unsigned width, BN_CTX* context) {
    return unsigned_bit(signed_twos(value, width, context), bit);
}

inline Big xor_width(const Big& left, const Big& right, unsigned width, BN_CTX* context) {
    if (width % 8 != 0) throw std::runtime_error("xor_width requires a byte width");
    const std::size_t bytes = width / 8;
    if (bytes > 64) throw std::runtime_error("xor_width exceeds fixed local buffer");
    std::array<unsigned char, 64> a{};
    std::array<unsigned char, 64> b{};
    Big la = modulo_power(left, width, context);
    Big lb = modulo_power(right, width, context);
    if (BN_bn2binpad(la.get(), a.data(), static_cast<int>(bytes)) != static_cast<int>(bytes) ||
        BN_bn2binpad(lb.get(), b.data(), static_cast<int>(bytes)) != static_cast<int>(bytes)) {
        throw std::runtime_error("BN_bn2binpad failed");
    }
    for (std::size_t i = 0; i < bytes; ++i) a[i] ^= b[i];
    return Big(BN_bin2bn(a.data(), static_cast<int>(bytes), nullptr));
}

inline Big complement_256(const Big& value, BN_CTX* context) {
    Big mask = sub(Big::power_of_two(256), Big::word(1));
    return sub(mask, modulo_power(value, 256, context));
}

inline Big low_fold_delta(const Big& value, const Big& delta, unsigned bits, BN_CTX* context) {
    const Big modulus = Big::power_of_two(bits);
    Big low = nonnegative_mod(value, modulus, context);
    Big high = sub(value, low);
    Big next = nonnegative_mod(add(low, delta), modulus, context);
    return modulo_power(add(high, next), 256, context);
}

inline Big negate_word(const Big& value) {
    Big zero;
    return sub(zero, value);
}

struct TargetConfig {
    static constexpr unsigned kRoundsDivide = 696;
    static constexpr unsigned kRoundsMultiply = 696;
    static constexpr unsigned kReplayPeakDivide = 1270;
    static constexpr unsigned kReplayPeakMultiply = 1271;
    static constexpr unsigned kSquareLadder = 240;
    static constexpr unsigned kReplayChunk = 96;
    static constexpr unsigned kReplayCompare = 20;
    static constexpr unsigned kReplayFold = 54;
    static constexpr unsigned kEndpointFold = 20;
    static constexpr unsigned kReplayFlagCompare = 22;
    static constexpr unsigned kPlanR1 = 340;
    static constexpr unsigned kPlanR2 = 628;
    static constexpr bool kFoldSelectorEvict = true;
    static constexpr bool kDoubledOutEvict = true;
    static constexpr bool kTarget0SignAlias = true;
    static constexpr bool kSignXorAddEvict = true;

    std::array<unsigned, kRoundsDivide> widths{};

    void validate_explicit_target() const {
        if (widths[0] != 259 || widths[1] != 258 || widths[339] != 145 ||
            widths[340] != 145 || widths[627] != 34 || widths[628] != 33 ||
            widths[695] != 8) {
            throw std::runtime_error("Q1270 width identity mismatch");
        }
        for (std::size_t i = 1; i < widths.size(); ++i) {
            if (widths[i] > widths[i - 1] || widths[i] < 8 || widths[i] > 259) {
                throw std::runtime_error("Q1270 width schedule is malformed");
            }
        }
        static_assert(kReplayPeakDivide == 1270 && kReplayPeakMultiply == 1271);
        static_assert(kSquareLadder == 240 && kFoldSelectorEvict && kDoubledOutEvict &&
                      kTarget0SignAlias && kSignXorAddEvict);
    }
};

struct RecurrenceResult {
    Big value;
    bool dirty = false;
    const char* first_fault = "clean";
};

class NativeRecurrence {
  public:
    explicit NativeRecurrence(TargetConfig config)
        : config_(std::move(config)), context_(BN_CTX_new()),
          p_(Big::hex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F")),
          f_(Big::hex("1000003D1")), f_minus_one_(sub(f_, Big::word(1))) {
        if (context_ == nullptr) throw std::bad_alloc();
        config_.validate_explicit_target();
    }

    NativeRecurrence(const NativeRecurrence&) = delete;
    NativeRecurrence& operator=(const NativeRecurrence&) = delete;
    ~NativeRecurrence() { BN_CTX_free(context_); }

    const Big& modulus() const { return p_; }

    RecurrenceResult divide(const Big& denominator, const Big& numerator) {
        return run(denominator, numerator, false);
    }

    RecurrenceResult multiply(const Big& denominator, const Big& numerator) {
        return run(denominator, numerator, true);
    }

    Big mod_p(const Big& value) { return nonnegative_mod(value, p_, context_); }

    Big square_mod_p(const Big& value) {
        Big out;
        bn_require(BN_mod_sqr(out.get(), value.get(), p_.get(), context_), "BN_mod_sqr");
        return out;
    }

  private:
    struct Walk {
        Big u;
        Big v;
        std::array<bool, TargetConfig::kRoundsDivide> tape{};
        bool dirty = false;
        const char* first_fault = "clean";
    };

    static void fault(bool& dirty, const char*& first, const char* reason) {
        if (!dirty) first = reason;
        dirty = true;
    }

    Walk walk(const Big& denominator) {
        Walk out{p_, mod_p(denominator)};
        const bool a0 = unsigned_bit(out.v, 0);
        const bool a1 = unsigned_bit(out.v, 1);
        Big q = shift_right_exact(out.v, 1);
        Big w = sub(q, p_);
        if (a1) w = add(w, p_);
        if (a0) w = add(w, shift_right_exact(add(p_, Big::word(1)), 1));
        out.v = std::move(w);
        out.tape[0] = a0;

        for (unsigned round = 1; round < TargetConfig::kRoundsDivide; ++round) {
            const unsigned width = config_.widths[round];
            if (!signed_fits(out.u, width) || !signed_fits(out.v, width)) {
                fault(out.dirty, out.first_fault, "walk-width");
                return out;
            }
            Big* source = (round % 2 == 0) ? &out.u : &out.v;
            Big* target = (round % 2 == 0) ? &out.v : &out.u;
            const bool sign = signed_bit(*target, 1, width, context_) ^
                              signed_bit(*source, 1, width, context_);
            Big combined = sign ? sub(*target, *source) : add(*target, *source);
            if (signed_bit(combined, 0, width + 1, context_)) {
                fault(out.dirty, out.first_fault, "walk-parity");
                return out;
            }
            *target = shift_right_exact(combined, 1);
            out.tape[round] = sign;
        }

        const Big one = Big::word(1);
        Big minus_one = negate_word(one);
        if ((!equal(out.u, one) && !equal(out.u, minus_one)) ||
            (!equal(out.v, one) && !equal(out.v, minus_one))) {
            fault(out.dirty, out.first_fault, "walk-terminal");
        }
        return out;
    }

    Big low_add(const Big& value, const Big& delta, unsigned bits) {
        return low_fold_delta(value, delta, bits, context_);
    }

    Big mod_halve(Big target, bool& dirty, const char*& first) {
        const bool parity = unsigned_bit(target, 0);
        if (parity) target = low_add(target, negate_word(f_), 54);
        const bool post_low = unsigned_bit(target, 0);
        target = shift_right_exact(target, 1);
        if (parity) bn_require(BN_set_bit(target.get(), 255), "BN_set_bit halve");
        if (post_low) fault(dirty, first, "halve-cleanup");
        return modulo_power(target, 256, context_);
    }

    Big mod_double(Big target, bool& dirty, const char*& first) {
        const bool overflow = unsigned_bit(target, 255);
        target = modulo_power(shift_left(target, 1), 256, context_);
        if (overflow) target = low_add(target, f_, 54);
        if (unsigned_bit(target, 0) != overflow) fault(dirty, first, "double-cleanup");
        return target;
    }

    Big conditional_negate(Big value, bool control) {
        if (!control) return value;
        value = complement_256(value, context_);
        return low_add(value, negate_word(f_minus_one_), 54);
    }

    Big fused_halve(bool sign, const Big& source, Big target, bool& dirty, const char*& first) {
        if (sign) target = complement_256(target, context_);
        Big sum = add(target, source);
        const bool overflow = unsigned_bit(sum, 256);
        target = modulo_power(sum, 256, context_);
        const bool parity = unsigned_bit(target, 0);
        const bool not_sign_and_parity = (!sign) && parity;
        const bool sign_and_parity = sign && parity;
        const bool minus_f = (!overflow) && not_sign_and_parity;
        const bool plus_2f = overflow && sign_and_parity;
        const bool plus_f = minus_f ^ sign ^ parity;
        Big delta;
        if (minus_f) delta = negate_word(f_);
        if (plus_f) delta = add(delta, f_);
        if (plus_2f) delta = add(delta, shift_left(f_, 1));
        target = low_add(target, delta, 54);
        const bool shift_top = parity ^ overflow ^ sign;
        if (sign) target = complement_256(target, context_);
        const bool post_low = unsigned_bit(target, 0);
        target = shift_right_exact(target, 1);
        if (shift_top) bn_require(BN_set_bit(target.get(), 255), "BN_set_bit fused halve");
        if (post_low) fault(dirty, first, "fused-halve-cleanup");
        return modulo_power(target, 256, context_);
    }

    Big fused_double(bool sign, const Big& source, Big target) {
        const bool doubled_out = unsigned_bit(target, 255);
        target = modulo_power(shift_left(target, 1), 256, context_);
        if (sign) target = complement_256(target, context_);
        Big sum = add(target, source);
        const bool add_out = unsigned_bit(sum, 256);
        target = modulo_power(sum, 256, context_);
        const bool routed = doubled_out && (sign ^ add_out);
        const bool minus_f = routed && sign;
        const bool plus_2f = routed ^ minus_f;
        const bool plus_f = doubled_out ^ add_out ^ minus_f;
        Big delta;
        if (minus_f) delta = negate_word(f_);
        if (plus_f) delta = add(delta, f_);
        if (plus_2f) delta = add(delta, shift_left(f_, 1));
        target = low_add(target, delta, 54);
        if (sign) target = complement_256(target, context_);
        return target;
    }

    Big seed_forward(bool sign, const Big& source, Big target) {
        target = xor_width(target, source, 256, context_);
        if (sign) target = complement_256(target, context_);
        if (sign) target = low_add(target, negate_word(f_minus_one_), 66);
        return target;
    }

    Big seed_inverse(bool sign, const Big& source, Big target) {
        if (sign) target = low_add(target, f_minus_one_, 66);
        // The exact target source emits two identical sign CXs here; they cancel.
        return xor_width(target, source, 256, context_);
    }

    RecurrenceResult run(const Big& denominator, const Big& numerator, bool multiply_mode) {
        Walk state = walk(denominator);
        RecurrenceResult result;
        result.dirty = state.dirty;
        result.first_fault = state.first_fault;
        if (state.dirty) return result;

        Big x = multiply_mode ? mod_p(numerator) : Big{};
        Big y = mod_p(numerator);
        x = conditional_negate(std::move(x), is_negative(state.u));
        y = conditional_negate(std::move(y), is_negative(state.v));

        if (!multiply_mode) {
            // Divide replay is forward and applies terminal sign corrections last.
            x = Big{};
            y = mod_p(numerator);
            for (unsigned round = 0; round < TargetConfig::kRoundsDivide; ++round) {
                Big* source = (round % 2 == 0) ? &x : &y;
                Big* target = (round % 2 == 0) ? &y : &x;
                if (round == 0) {
                    *target = mod_halve(std::move(*target), result.dirty, result.first_fault);
                } else if (round == 1) {
                    *target = seed_forward(state.tape[round], *source, std::move(*target));
                    *target = mod_halve(std::move(*target), result.dirty, result.first_fault);
                } else {
                    *target = fused_halve(state.tape[round], *source, std::move(*target),
                                          result.dirty, result.first_fault);
                }
                if (result.dirty) return result;
            }
            x = conditional_negate(std::move(x), is_negative(state.u));
            y = conditional_negate(std::move(y), is_negative(state.v));
            if (!equal(x, y)) fault(result.dirty, result.first_fault, "divide-coefficient-clear");
            result.value = std::move(y);
            return result;
        }

        for (int round = static_cast<int>(TargetConfig::kRoundsMultiply) - 1; round >= 0;
             --round) {
            Big* source = (round % 2 == 0) ? &x : &y;
            Big* target = (round % 2 == 0) ? &y : &x;
            if (round > 1) {
                *target = fused_double(!state.tape[static_cast<unsigned>(round)], *source,
                                       std::move(*target));
            } else {
                *target = mod_double(std::move(*target), result.dirty, result.first_fault);
            }
            if (round == 1) {
                *target = seed_inverse(state.tape[1], *source, std::move(*target));
            }
            if (result.dirty) return result;
        }
        if (!is_zero(x)) fault(result.dirty, result.first_fault, "multiply-coefficient-clear");
        result.value = std::move(y);
        return result;
    }

    TargetConfig config_;
    BN_CTX* context_;
    Big p_;
    Big f_;
    Big f_minus_one_;
};

}  // namespace q1270
