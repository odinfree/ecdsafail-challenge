#include "q1270_pp_host.h"

#include <iostream>

namespace {

constexpr std::uint64_t kInheritedNonce = 65'700'024'945'645ULL;

void print_identity() {
    std::cout << "model=q1270_native_recurrence_v1\n"
              << "source_commit=" << q1270::kSourceCommit << '\n'
              << "evidence_commit=" << q1270::kEvidenceCommit << '\n'
              << "operations=" << q1270::kExpectedOperations << '\n'
              << "operations_sha256=" << q1270::kOperationsSha256 << '\n'
              << "checkpoint_sha256=" << q1270::kCheckpointSha256 << '\n'
              << "active_widths_sha256=" << q1270::kWidthsSha256 << '\n'
              << "host_state_digest=" << std::hex << std::setfill('0') << std::setw(16)
              << q1270::kExpectedHostStateDigest << std::dec << '\n'
              << "rounds=696/696\n"
              << "replay_peaks=1270/1271\n"
              << "square_ladder=240\n"
              << "lifecycles=selector,doubled_out,target0_sign,sign_xor_add\n";
}

void selftest(const std::string& checkpoint_path, const std::string& widths_path) {
    if (!q1270::Shake256::vector_selftest()) {
        throw std::runtime_error("SHAKE256 empty/abc vector mismatch");
    }
    const q1270::Checkpoint checkpoint = q1270::Checkpoint::load(checkpoint_path);
    const q1270::TargetConfig config = q1270::load_target_config(widths_path);
    const auto first = checkpoint.xof_for(kInheritedNonce, 4096);
    const auto second = checkpoint.xof_for(kInheritedNonce, 4096);
    if (first != second) throw std::runtime_error("checkpoint XOF repeat mismatch");

    q1270::NativeRecurrence model(config);
    q1270::CurveHost curve;
    const q1270::TestVector shot0 = curve.from_scalars(first.data(), first.data() + 32);
    const q1270::Big denominator = model.mod_p(q1270::sub(shot0.x, shot0.ox));
    const q1270::Big numerator = model.mod_p(q1270::sub(shot0.y, shot0.oy));
    q1270::RecurrenceResult divided = model.divide(denominator, numerator);
    q1270::RecurrenceResult multiplied = model.multiply(denominator, numerator);

    std::unique_ptr<BN_CTX, decltype(&BN_CTX_free)> context(BN_CTX_new(), BN_CTX_free);
    if (!context) throw std::bad_alloc();
    q1270::Big inverse(BN_mod_inverse(nullptr, denominator.get(), model.modulus().get(),
                                      context.get()));
    q1270::Big expected_divide;
    q1270::bn_require(BN_mod_mul(expected_divide.get(), numerator.get(), inverse.get(),
                                model.modulus().get(), context.get()),
                      "BN_mod_mul divide unit");
    q1270::Big expected_multiply;
    q1270::bn_require(BN_mod_mul(expected_multiply.get(), numerator.get(), denominator.get(),
                                model.modulus().get(), context.get()),
                      "BN_mod_mul multiply unit");
    if (divided.dirty || !q1270::equal(divided.value, expected_divide)) {
        throw std::runtime_error(std::string("shot0 divide recurrence mismatch: ") +
                                 divided.first_fault);
    }
    if (multiplied.dirty || !q1270::equal(multiplied.value, expected_multiply)) {
        throw std::runtime_error(std::string("shot0 multiply recurrence mismatch: ") +
                                 multiplied.first_fault);
    }

    std::cout << "SELFTEST PASS"
              << " shake=empty+abc"
              << " checkpoint_xof4096_sha256=" << q1270::sha256_hex(first)
              << " widths=696+696"
              << " recurrence=inherited-shot0-divide+multiply\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "identity") {
            print_identity();
            return 0;
        }
        if (argc == 4 && std::string(argv[1]) == "selftest") {
            selftest(argv[2], argv[3]);
            return 0;
        }
        std::cerr << "usage: q1270_ppcpu identity | q1270_ppcpu selftest CHECKPOINT ACTIVE_WIDTHS\n";
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "q1270_ppcpu: " << error.what() << '\n';
        return 1;
    }
}
