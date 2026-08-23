#pragma once

// Predictor-only regression for measured carry erasures emitted by the sealed
// Q1270 product-register square. This models no circuit operation and exposes
// no nonce, search, provider, or submission surface.

#include <array>
#include <cstdint>
#include <ostream>
#include <stdexcept>
#include <string>

namespace q1270 {

enum class SquareFrame { AddFull, SubFull, SignSandwich };

struct SquareBoundaryEvent {
    const char* label;
    unsigned width;
    unsigned leading;
    SquareFrame frame;
    int sign;
    int shift;
};

// Exact product_register.rs call order after excluding one-chunk calls.
inline constexpr std::array<SquareBoundaryEvent, 17> kSquareBoundaryEvents{{
    {"A.forward.spread", 256, 16, SquareFrame::AddFull, -1, -1},
    {"A.forward.xext", 256, 16, SquareFrame::SubFull, -1, -1},
    {"A.mod_full.shift0", 257, 17, SquareFrame::SignSandwich, 1, 0},
    {"A.inverse.xext", 256, 16, SquareFrame::AddFull, -1, -1},
    {"A.inverse.spread", 256, 16, SquareFrame::SubFull, -1, -1},
    {"B.forward.spread", 256, 16, SquareFrame::AddFull, -1, -1},
    {"B.forward.xext", 256, 16, SquareFrame::SubFull, -1, -1},
    {"B.full.shift0", 257, 17, SquareFrame::SignSandwich, 1, 0},
    {"B.full.shift4", 253, 13, SquareFrame::SignSandwich, 1, 4},
    {"B.full.shift6", 251, 11, SquareFrame::SignSandwich, 0, 6},
    {"B.full.shift10", 247, 7, SquareFrame::SignSandwich, 1, 10},
    {"B.inverse.xext", 256, 16, SquareFrame::AddFull, -1, -1},
    {"B.inverse.spread", 256, 16, SquareFrame::SubFull, -1, -1},
    {"C.forward.spread", 258, 18, SquareFrame::AddFull, -1, -1},
    {"C.forward.xext", 258, 18, SquareFrame::SubFull, -1, -1},
    {"C.inverse.xext", 258, 18, SquareFrame::AddFull, -1, -1},
    {"C.inverse.spread", 258, 18, SquareFrame::SubFull, -1, -1},
}};

inline constexpr std::array<unsigned, 4> kSquareOneChunkWidths{{129, 154, 225, 241}};

struct SquareLayout { unsigned chunks, leading, trailing, ladder; };

inline SquareLayout q1270_square_layout(unsigned width) {
    constexpr unsigned ladder = 240;
    constexpr unsigned compare = 20;
    if (width == 0) throw std::runtime_error("zero square width");
    if (width - 1 <= ladder) return {1, width, 0, width - 1};
    const unsigned leading = width - ladder;
    if (leading == 0 || leading > compare) throw std::runtime_error("layout escaped sealed branch");
    return {2, leading, ladder, ladder};
}

inline void square_require(bool ok, const std::string& reason) {
    if (!ok) throw std::runtime_error("square-boundary regression: " + reason);
}

inline bool carry(std::uint64_t a, std::uint64_t b, std::uint64_t modulus) {
    return a + b >= modulus;
}

inline bool predicate(std::uint64_t a, std::uint64_t b, std::uint64_t modulus) {
    return ((a + b) % modulus) < b;
}

// For each b, carry and predicate have the same sole transition a=M-b:
// below it r=a+b>=b; at/above it r=a+b-M<b because a<M. Checking both
// interval endpoints for every b proves the integer partition without
// sampling pairs. The complemented pass also enumerates ~x=M-1-x, which is
// the pre-add frame used by sub_full.
inline void prove_leading_chunk(unsigned bits, bool complemented) {
    square_require(bits > 0 && bits < 63, "proof width");
    const std::uint64_t modulus = std::uint64_t{1} << bits;
    const std::uint64_t mask = modulus - 1;
    if (complemented) {
        for (std::uint64_t x = 0; x < modulus; ++x)
            square_require((mask ^ x) == mask - x, "sub_full complement");
    }
    for (std::uint64_t b = 0; b < modulus; ++b) {
        const std::uint64_t transition = modulus - b;
        const std::uint64_t below = transition - 1;
        square_require(!carry(below, b, modulus) && !predicate(below, b, modulus), "below transition");
        square_require(((below + b) % modulus) >= b, "below residue bound");
        if (b != 0) {
            square_require(carry(transition, b, modulus) && predicate(transition, b, modulus), "at transition");
            square_require(carry(mask, b, modulus) && predicate(mask, b, modulus), "upper endpoint");
            square_require(((mask + b) % modulus) < b, "upper residue bound");
        }
    }
}

inline const char* frame_name(SquareFrame frame) {
    if (frame == SquareFrame::AddFull) return "add_full";
    if (frame == SquareFrame::SubFull) return "sub_full_complemented";
    return "sign_sandwich";
}

inline void square_boundary_selftest(std::ostream& out) {
    std::array<bool, 19> plain{}, complemented{};
    unsigned sub_full = 0, shift6_sign0 = 0;
    for (std::size_t i = 0; i < kSquareBoundaryEvents.size(); ++i) {
        const auto& event = kSquareBoundaryEvents[i];
        const auto layout = q1270_square_layout(event.width);
        square_require(layout.chunks == 2 && layout.leading == event.leading &&
                           layout.trailing == 240 && layout.ladder == 240,
                       std::string(event.label) + " layout drift");
        square_require(event.leading <= 20, std::string(event.label) + " truncated compare");
        const bool comp = event.frame == SquareFrame::SubFull ||
                          (event.frame == SquareFrame::SignSandwich && event.sign == 1);
        if (!plain[event.leading]) { prove_leading_chunk(event.leading, false); plain[event.leading] = true; }
        if (comp && !complemented[event.leading]) {
            prove_leading_chunk(event.leading, true); complemented[event.leading] = true;
        }
        sub_full += event.frame == SquareFrame::SubFull;
        shift6_sign0 += event.shift == 6 && event.sign == 0;
        out << i + 1 << '\t' << event.label << "\twidth=" << event.width
            << "\tlayout=" << layout.leading << '+' << layout.trailing
            << "\tcompare=" << event.leading << "\tframe=" << frame_name(event.frame);
        if (event.sign >= 0) out << "\tsign=" << event.sign << "\tshift=" << event.shift;
        out << "\tresidual=0\n";
    }
    square_require(sub_full == 6, "sub_full count");
    square_require(shift6_sign0 == 1, "sign=0 shift-6 count");
    // At full width W, sub_full is ~(~x+y) mod 2^W = x-y mod 2^W.
    // The equality follows directly after substituting ~x=2^W-1-x; the
    // complemented leading-chunk enumeration above binds its measured carry.
    for (unsigned width : kSquareOneChunkWidths) {
        const auto layout = q1270_square_layout(width);
        square_require(layout.chunks == 1, "excluded width became chunked");
        out << "excluded\twidth=" << width << "\tlayout=" << width << "\tboundaries=0\n";
    }
    out << "SQUARE_BOUNDARY_SELFTEST PASS events=17 residuals=0 sub_full=6"
           " shift6_sign0=1 ladder=240 compare=20\n";
}

}  // namespace q1270
