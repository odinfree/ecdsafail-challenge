#pragma once

// Fail-closed local host for the exact Q1270 PPFSCKP1 and width artifacts.

#include "q1270_pp_model.h"

#include <openssl/ec.h>
#include <openssl/obj_mac.h>
#include <openssl/sha.h>

#include <algorithm>
#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <memory>
#include <new>
#include <sstream>
#include <string>
#include <vector>

namespace q1270 {

inline constexpr char kSourceCommit[] = "90770b10664fc89065b1d05ac792370efed4c629";
inline constexpr char kEvidenceCommit[] = "953acb44fbcbb32ab097a52be31ae365db41bd92";
inline constexpr char kOperationsSha256[] =
    "ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a";
inline constexpr char kCheckpointSha256[] =
    "75deeae0d80122a3ce30a7337b34128af5dc964bc26ba0b77c2d6599abdb937f";
inline constexpr char kWidthsSha256[] =
    "c49b95b00f2c0c33936b1123f847cf7d2d17f17eda3c89a18d3d8e322aea8bf5";
inline constexpr std::uint64_t kExpectedHostStateDigest = 0xe0d66eb521941b4fULL;
inline constexpr std::uint64_t kExpectedOperations = 12'953'636;
inline constexpr std::uint64_t kExpectedCheckpointResidual = 70;
inline constexpr std::size_t kCheckpointBytes = 5'064;
inline constexpr std::size_t kTailRecords = 96;
inline constexpr std::size_t kRecordBytes = 49;
inline constexpr std::size_t kRate = 136;
inline constexpr std::size_t kShots = 9'024;

inline std::vector<unsigned char> read_binary(const std::string& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open frozen input: " + path);
    input.seekg(0, std::ios::end);
    const std::streamoff length = input.tellg();
    if (length < 0) throw std::runtime_error("cannot size frozen input: " + path);
    input.seekg(0, std::ios::beg);
    std::vector<unsigned char> bytes(static_cast<std::size_t>(length));
    if (!bytes.empty()) input.read(reinterpret_cast<char*>(bytes.data()), length);
    if (!input) throw std::runtime_error("short read from frozen input: " + path);
    return bytes;
}

inline std::string hex_bytes(const unsigned char* bytes, std::size_t length) {
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (std::size_t i = 0; i < length; ++i) output << std::setw(2) << unsigned(bytes[i]);
    return output.str();
}

inline std::string sha256_hex(const std::vector<unsigned char>& bytes) {
    std::array<unsigned char, SHA256_DIGEST_LENGTH> digest{};
    if (SHA256(bytes.data(), bytes.size(), digest.data()) == nullptr) {
        throw std::runtime_error("SHA256 failed");
    }
    return hex_bytes(digest.data(), digest.size());
}

inline std::uint64_t load_u64(const unsigned char* bytes) {
    std::uint64_t value = 0;
    for (unsigned i = 0; i < 8; ++i) value |= std::uint64_t(bytes[i]) << (8 * i);
    return value;
}

inline void store_u64(unsigned char* bytes, std::uint64_t value) {
    for (unsigned i = 0; i < 8; ++i) bytes[i] = static_cast<unsigned char>(value >> (8 * i));
}

inline std::uint64_t fnv1a64(const std::vector<unsigned char>& bytes) {
    std::uint64_t digest = 0xcbf29ce484222325ULL;
    for (unsigned char byte : bytes) {
        digest ^= byte;
        digest *= 0x100000001b3ULL;
    }
    return digest;
}

class Shake256 {
  public:
    Shake256() = default;

    void absorb(const unsigned char* data, std::size_t length) {
        std::size_t offset = 0;
        while (offset < length) {
            const std::size_t take = std::min(kRate - length_, length - offset);
            std::memcpy(buffer_.data() + length_, data + offset, take);
            length_ += take;
            offset += take;
            if (length_ == kRate) {
                permute_block();
                length_ = 0;
            }
        }
    }

    void absorb(const std::vector<unsigned char>& data) { absorb(data.data(), data.size()); }

    std::vector<unsigned char> finish(std::size_t output_length) const {
        Shake256 sponge = *this;
        std::fill(sponge.buffer_.begin() + static_cast<std::ptrdiff_t>(sponge.length_),
                  sponge.buffer_.end(), 0);
        sponge.buffer_[sponge.length_] ^= 0x1f;
        sponge.buffer_[kRate - 1] ^= 0x80;
        sponge.permute_block();
        std::vector<unsigned char> output(output_length);
        std::size_t offset = 0;
        while (offset < output.size()) {
            const std::size_t take = std::min(kRate, output.size() - offset);
            for (std::size_t i = 0; i < take; ++i) {
                output[offset + i] = static_cast<unsigned char>(
                    sponge.state_[i / 8] >> (8 * (i % 8)));
            }
            offset += take;
            if (offset < output.size()) keccakf(sponge.state_);
        }
        return output;
    }

    static Shake256 from_checkpoint(const std::array<std::uint64_t, 25>& state,
                                    const std::array<unsigned char, kRate>& buffer,
                                    std::size_t residual) {
        if (residual >= kRate) throw std::runtime_error("checkpoint residual is invalid");
        Shake256 sponge;
        sponge.state_ = state;
        sponge.buffer_ = buffer;
        sponge.length_ = residual;
        return sponge;
    }

    static bool vector_selftest() {
        static constexpr char kEmpty[] =
            "46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f"
            "d75dc4ddd8c0f200cb05019d67b592f6fc821c49479ab48640292eacb3b7c4be";
        static constexpr char kAbc[] =
            "483366601360a8771c6863080cc4114d8db44530f8f1e1ee4f94ea37e78b5739d"
            "5a15bef186a5386c75744c0527e1faa9f8726e462a12a4feb06bd8801e751e4";
        Shake256 empty;
        Shake256 abc;
        const unsigned char text[] = {'a', 'b', 'c'};
        abc.absorb(text, sizeof(text));
        const auto a = empty.finish(64);
        const auto b = abc.finish(64);
        return hex_bytes(a.data(), a.size()) == kEmpty && hex_bytes(b.data(), b.size()) == kAbc;
    }

  private:
    static void keccakf(std::array<std::uint64_t, 25>& state) {
        static constexpr std::array<std::uint64_t, 24> rc = {
            0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808aULL,
            0x8000000080008000ULL, 0x000000000000808bULL, 0x0000000080000001ULL,
            0x8000000080008081ULL, 0x8000000000008009ULL, 0x000000000000008aULL,
            0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000aULL,
            0x000000008000808bULL, 0x800000000000008bULL, 0x8000000000008089ULL,
            0x8000000000008003ULL, 0x8000000000008002ULL, 0x8000000000000080ULL,
            0x000000000000800aULL, 0x800000008000000aULL, 0x8000000080008081ULL,
            0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL,
        };
        static constexpr std::array<unsigned, 24> rho = {
            1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 2, 14,
            27, 41, 56, 8, 25, 43, 62, 18, 39, 61, 20, 44,
        };
        static constexpr std::array<unsigned, 24> pij = {
            10, 7, 11, 17, 18, 3, 5, 16, 8, 21, 24, 4,
            15, 23, 19, 13, 12, 2, 20, 14, 22, 9, 6, 1,
        };
        for (std::uint64_t round_constant : rc) {
            std::array<std::uint64_t, 5> columns{};
            for (unsigned i = 0; i < 5; ++i) {
                columns[i] = state[i] ^ state[i + 5] ^ state[i + 10] ^ state[i + 15] ^
                             state[i + 20];
            }
            for (unsigned i = 0; i < 5; ++i) {
                const std::uint64_t delta = columns[(i + 4) % 5] ^
                                            std::rotl(columns[(i + 1) % 5], 1);
                for (unsigned j = 0; j < 25; j += 5) state[j + i] ^= delta;
            }
            std::uint64_t rotated = state[1];
            for (unsigned i = 0; i < 24; ++i) {
                const unsigned j = pij[i];
                const std::uint64_t previous = state[j];
                state[j] = std::rotl(rotated, static_cast<int>(rho[i]));
                rotated = previous;
            }
            for (unsigned row = 0; row < 25; row += 5) {
                const std::array<std::uint64_t, 5> before = {
                    state[row], state[row + 1], state[row + 2], state[row + 3], state[row + 4]};
                for (unsigned i = 0; i < 5; ++i) {
                    state[row + i] = before[i] ^ ((~before[(i + 1) % 5]) & before[(i + 2) % 5]);
                }
            }
            state[0] ^= round_constant;
        }
    }

    void permute_block() {
        for (std::size_t i = 0; i < kRate / 8; ++i) state_[i] ^= load_u64(&buffer_[i * 8]);
        keccakf(state_);
    }

    std::array<std::uint64_t, 25> state_{};
    std::array<unsigned char, kRate> buffer_{};
    std::size_t length_ = 0;
};

class Checkpoint {
  public:
    static Checkpoint load(const std::string& path) {
        const std::vector<unsigned char> bytes = read_binary(path);
        if (bytes.size() != kCheckpointBytes) throw std::runtime_error("checkpoint size mismatch");
        if (sha256_hex(bytes) != kCheckpointSha256) throw std::runtime_error("checkpoint SHA mismatch");
        if (fnv1a64(bytes) != kExpectedHostStateDigest) {
            throw std::runtime_error("checkpoint host-state digest mismatch");
        }
        if (std::memcmp(bytes.data(), "PPFSCKP1", 8) != 0) {
            throw std::runtime_error("checkpoint magic mismatch");
        }
        if (load_u64(bytes.data() + 8) != kExpectedOperations ||
            load_u64(bytes.data() + 16) != kExpectedCheckpointResidual) {
            throw std::runtime_error("checkpoint operation/residual mismatch");
        }
        Checkpoint out;
        std::size_t offset = 24;
        for (std::uint64_t& lane : out.state_) {
            lane = load_u64(bytes.data() + offset);
            offset += 8;
        }
        std::copy_n(bytes.data() + offset, kRate, out.buffer_.data());
        offset += kRate;
        for (auto& record : out.tail_) {
            std::copy_n(bytes.data() + offset, kRecordBytes, record.data());
            offset += kRecordBytes;
        }
        if (offset != bytes.size()) throw std::runtime_error("checkpoint parser length mismatch");
        out.validate_tail();
        return out;
    }

    std::vector<unsigned char> xof_for(std::uint64_t nonce, std::size_t bytes) const {
        if (nonce >= (1ULL << 48)) throw std::runtime_error("nonce exceeds 48 bits");
        Shake256 sponge = Shake256::from_checkpoint(state_, buffer_, kExpectedCheckpointResidual);
        for (std::size_t index = 0; index < tail_.size(); ++index) {
            auto record = tail_[index];
            store_u64(record.data() + 17, (nonce >> (index / 2)) & 1ULL);
            sponge.absorb(record.data(), record.size());
        }
        return sponge.finish(bytes);
    }

  private:
    void validate_tail() const {
        for (std::size_t bit = 0; bit < 48; ++bit) {
            const auto& left = tail_[2 * bit];
            const auto& right = tail_[2 * bit + 1];
            for (const auto* record : {&left, &right}) {
                if ((*record)[0] != 6 || load_u64(record->data() + 1) != UINT64_MAX ||
                    load_u64(record->data() + 9) != UINT64_MAX ||
                    load_u64(record->data() + 25) != UINT64_MAX ||
                    load_u64(record->data() + 33) != UINT64_MAX ||
                    load_u64(record->data() + 41) != UINT64_MAX) {
                    throw std::runtime_error("checkpoint nonce-tail shape mismatch");
                }
            }
            const std::uint64_t a = load_u64(left.data() + 17);
            const std::uint64_t b = load_u64(right.data() + 17);
            if (a != b || a > 1) throw std::runtime_error("checkpoint nonce-tail pair mismatch");
        }
    }

    std::array<std::uint64_t, 25> state_{};
    std::array<unsigned char, kRate> buffer_{};
    std::array<std::array<unsigned char, kRecordBytes>, kTailRecords> tail_{};
};

inline TargetConfig load_target_config(const std::string& active_widths_path) {
    const std::vector<unsigned char> bytes = read_binary(active_widths_path);
    if (sha256_hex(bytes) != kWidthsSha256) throw std::runtime_error("active-width SHA mismatch");
    std::istringstream input(std::string(reinterpret_cast<const char*>(bytes.data()), bytes.size()));
    std::string line;
    if (!std::getline(input, line) || line != "direction\tround\twidth") {
        throw std::runtime_error("active-width header mismatch");
    }
    TargetConfig config;
    for (const char* direction : {"divide", "multiply"}) {
        for (unsigned round = 0; round < TargetConfig::kRoundsDivide; ++round) {
            if (!std::getline(input, line)) throw std::runtime_error("active-width row missing");
            std::istringstream fields(line);
            std::string got_direction;
            std::string got_round;
            std::string got_width;
            if (!std::getline(fields, got_direction, '\t') || !std::getline(fields, got_round, '\t') ||
                !std::getline(fields, got_width, '\t') || fields.peek() != std::char_traits<char>::eof()) {
                throw std::runtime_error("malformed active-width row");
            }
            if (got_direction != direction || std::stoul(got_round) != round) {
                throw std::runtime_error("active-width order mismatch");
            }
            const unsigned width = static_cast<unsigned>(std::stoul(got_width));
            if (direction == std::string("divide")) config.widths[round] = width;
            else if (config.widths[round] != width) throw std::runtime_error("direction width mismatch");
        }
    }
    if (std::getline(input, line)) throw std::runtime_error("active-width trailing row");
    config.validate_explicit_target();
    return config;
}

struct TestVector {
    Big x;
    Big y;
    Big ox;
    Big oy;
    Big expected_x;
    Big expected_y;
};

class CurveHost {
  public:
    CurveHost()
        : group_(EC_GROUP_new_by_curve_name(NID_secp256k1), EC_GROUP_free),
          context_(BN_CTX_new()) {
        if (!group_ || context_ == nullptr) throw std::runtime_error("cannot initialize secp256k1");
    }

    CurveHost(const CurveHost&) = delete;
    CurveHost& operator=(const CurveHost&) = delete;
    ~CurveHost() { BN_CTX_free(context_); }

    TestVector from_scalars(const unsigned char* k1_le, const unsigned char* k2_le) {
        std::array<unsigned char, 32> k1_be{};
        std::array<unsigned char, 32> k2_be{};
        std::reverse_copy(k1_le, k1_le + 32, k1_be.begin());
        std::reverse_copy(k2_le, k2_le + 32, k2_be.begin());
        Big k1(BN_bin2bn(k1_be.data(), 32, nullptr));
        Big k2(BN_bin2bn(k2_be.data(), 32, nullptr));
        Point target(EC_POINT_new(group_.get()), EC_POINT_free);
        Point offset(EC_POINT_new(group_.get()), EC_POINT_free);
        Point sum(EC_POINT_new(group_.get()), EC_POINT_free);
        if (!target || !offset || !sum) throw std::bad_alloc();
        bn_require(EC_POINT_mul(group_.get(), target.get(), k1.get(), nullptr, nullptr, context_),
                   "EC_POINT_mul target");
        bn_require(EC_POINT_mul(group_.get(), offset.get(), k2.get(), nullptr, nullptr, context_),
                   "EC_POINT_mul offset");
        if (EC_POINT_is_at_infinity(group_.get(), target.get()) == 1 ||
            EC_POINT_is_at_infinity(group_.get(), offset.get()) == 1 ||
            EC_POINT_cmp(group_.get(), target.get(), offset.get(), context_) == 0) {
            throw std::runtime_error("frozen Fiat-Shamir test set contains a rejected point");
        }
        bn_require(EC_POINT_add(group_.get(), sum.get(), target.get(), offset.get(), context_),
                   "EC_POINT_add");
        TestVector output;
        coordinates(target.get(), output.x, output.y);
        coordinates(offset.get(), output.ox, output.oy);
        coordinates(sum.get(), output.expected_x, output.expected_y);
        return output;
    }

  private:
    using Point = std::unique_ptr<EC_POINT, decltype(&EC_POINT_free)>;
    using Group = std::unique_ptr<EC_GROUP, decltype(&EC_GROUP_free)>;

    void coordinates(const EC_POINT* point, Big& x, Big& y) {
        bn_require(EC_POINT_get_affine_coordinates(group_.get(), point, x.get(), y.get(), context_),
                   "EC_POINT_get_affine_coordinates");
    }

    Group group_;
    BN_CTX* context_;
};

}  // namespace q1270
