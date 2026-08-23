// phasepostfilter.cpp — finite-list CPU postfilter for the Q1274 repair-r100
// conditional phase contract. It has no range/start/count mode.
#include <fstream>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

#include "pp_phase_cpu.h"

static constexpr u64 PP_MAX_NONCE = (1ULL << 48) - 1;

struct PP_AuditRow {
    u64 nonce;
    PP_PhaseResult result;
};

static int usage() {
    fprintf(stderr,
            "usage:\n"
            "  phasepostfilter identity\n"
            "  phasepostfilter filter --ops OPS_BIN --nonces NONCE_LIST\n"
            "  phasepostfilter audit  --ops OPS_BIN --nonces NONCE_LIST\n");
    return 2;
}
static void print_identity() {
    printf("source_commit=%s\tops_count=%llu\tops_sha256=%s\t"
           "predictor_digest=%016llx\tshots=%d\tcontract=%s\tfinal=%s\t"
           "raw_phase=not-claimed\tcuda_phase=not-claimed\n",
           PP_SOURCE_COMMIT,
           (unsigned long long)PP_EXPECTED_OPS_Q1274_REPAIR_R100,
           PP_EXPECTED_OPS_SHA256,
           (unsigned long long)PP_EXPECTED_STATE_DIGEST_Q1274_REPAIR_R100,
           PP_NUM_TESTS, PP_PHASE_CONTRACT, PP_PHASE_FINAL_PREDICATE);
}

static bool safe_ops_path(const char* path) {
    if (path == nullptr || path[0] == 0) return false;
    for (const char* p = path; *p != 0; p++) {
        // pp_load_prefix invokes the zstd CLI through a single-quoted command.
        if (*p == '\'' || *p == '\n' || *p == '\r') return false;
    }
    return true;
}

static bool parse_nonce(const std::string& line, u64* nonce) {
    if (line.empty() || (line.size() > 1 && line[0] == '0')) return false;
    u64 value = 0;
    for (unsigned char c : line) {
        if (c < '0' || c > '9') return false;
        u64 digit = (u64)(c - '0');
        if (value > (PP_MAX_NONCE - digit) / 10) return false;
        value = value * 10 + digit;
    }
    *nonce = value;
    return true;
}

static int load_nonce_list(const char* path, std::vector<u64>* nonces) {
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        fprintf(stderr, "phasepostfilter: cannot open nonce list %s\n", path);
        return 3;
    }
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    if (size <= 0) {
        fprintf(stderr, "phasepostfilter: nonce list must be non-empty\n");
        return 3;
    }
    in.seekg(-1, std::ios::end);
    char last = 0;
    in.get(last);
    if (last != '\n') {
        fprintf(stderr,
                "phasepostfilter: nonce list must end in exactly one line feed\n");
        return 3;
    }
    in.clear();
    in.seekg(0, std::ios::beg);

    std::unordered_set<u64> seen;
    std::string line;
    size_t line_number = 0;
    while (std::getline(in, line)) {
        line_number++;
        u64 nonce = 0;
        if (!parse_nonce(line, &nonce)) {
            fprintf(stderr,
                    "phasepostfilter: malformed or out-of-range nonce at line %zu\n",
                    line_number);
            return 3;
        }
        if (!seen.insert(nonce).second) {
            fprintf(stderr, "phasepostfilter: duplicate nonce at line %zu\n",
                    line_number);
            return 3;
        }
        nonces->push_back(nonce);
    }
    if (!in.eof()) {
        fprintf(stderr, "phasepostfilter: nonce list read failure\n");
        return 3;
    }
    return 0;
}

static int run_list(bool audit, const char* ops_path, const char* nonce_path) {
    if (!safe_ops_path(ops_path)) {
        fprintf(stderr, "phasepostfilter: unsafe ops path\n");
        return 3;
    }
    std::vector<u64> nonces;
    int rc = load_nonce_list(nonce_path, &nonces);
    if (rc != 0) return rc;

    PP_Prefix prefix;
    pp_load_prefix(ops_path, &prefix);
    std::vector<u64> comb;
    pp_build_comb(comb);

    std::vector<PP_AuditRow> rows;
    rows.reserve(nonces.size());
    size_t phase_dirty_nonces = 0;
    size_t phase_faults = 0;
    for (u64 nonce : nonces) {
        PP_AuditRow row;
        row.nonce = nonce;
        rc = pp_phase_evaluate(&prefix, comb.data(), nonce, &row.result,
                               "phasepostfilter");
        if (rc != 0) return rc;
        if (!row.result.clean_phase_shots.empty()) phase_dirty_nonces++;
        phase_faults += row.result.clean_phase_shots.size();
        if (!audit && row.result.classical_faults != 0) {
            fprintf(stderr,
                    "phasepostfilter: FATAL: input nonce %llu is not classically "
                    "clean (faults=%llu); no output published\n",
                    (unsigned long long)nonce,
                    (unsigned long long)row.result.classical_faults);
            return 4;
        }
        rows.push_back(std::move(row));
    }

    size_t survivors = 0;
    for (const PP_AuditRow& row : rows) {
        bool survivor = row.result.classical_faults == 0 &&
                        row.result.clean_phase_shots.empty();
        if (survivor) survivors++;
        if (audit) {
            printf("%llu\t%llu\t%zu\t{",
                   (unsigned long long)row.nonce,
                   (unsigned long long)row.result.classical_faults,
                   row.result.clean_phase_shots.size());
            for (size_t i = 0; i < row.result.clean_phase_shots.size(); i++) {
                if (i != 0) putchar(',');
                printf("%zu", row.result.clean_phase_shots[i]);
            }
            printf("}\n");
        } else if (survivor) {
            printf("%llu\n", (unsigned long long)row.nonce);
        }
    }

    fprintf(stderr,
            "phasepostfilter: source=%s ops_count=%llu ops_sha256=%s "
            "predictor_digest=%016llx inputs=%zu survivors=%zu "
            "phase_dirty_nonces=%zu clean_phase_faults=%zu shots_per_nonce=%d "
            "contract=%s final=%s raw_phase=not-claimed cuda_phase=not-claimed\n",
            PP_SOURCE_COMMIT,
            (unsigned long long)PP_EXPECTED_OPS_Q1274_REPAIR_R100,
            PP_EXPECTED_OPS_SHA256,
            (unsigned long long)PP_EXPECTED_STATE_DIGEST_Q1274_REPAIR_R100,
            nonces.size(), survivors, phase_dirty_nonces, phase_faults,
            PP_NUM_TESTS, PP_PHASE_CONTRACT, PP_PHASE_FINAL_PREDICATE);
    return 0;
}

int main(int argc, char** argv) {
    if (argc == 2 && std::string(argv[1]) == "identity") {
        print_identity();
        return 0;
    }
    if (argc != 6) return usage();
    std::string mode = argv[1];
    if ((mode != "filter" && mode != "audit") ||
        std::string(argv[2]) != "--ops" ||
        std::string(argv[4]) != "--nonces") {
        return usage();
    }
    return run_list(mode == "audit", argv[3], argv[5]);
}
