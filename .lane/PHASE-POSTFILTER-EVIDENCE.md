# Q1274 finite-list conditional-phase postfilter evidence

## Frozen identity and scope

- branch base: `8802a5b619dcd309e539e6417ed17abebe5d9ecf`;
- predeclaration commit: `62d574e9d21942622289f6d1d387be481676b249`;
- first compiling packet commit:
  `c50b76e5c77c597ac347191405c4c49a53ac0736`;
- circuit source: `fe0b7bac6348fb35b7680784d4295899e498d0e3`;
- exact operations: `12,920,073`, SHA-256
  `4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c`;
- predictor digest: `d2c95102cb9a277d`;
- exact contract: `clean_phase_mask = phase_mask & ~classical_mask`;
- only final predicate:
  `classical_mask == 0 && clean_phase_mask == 0`.

The executable consumes only an explicit finite canonical nonce list. It has
no range/start/count mode. A nonzero exact classical mask anywhere is fatal for
the complete input, so no partial survivor output is valid. Raw phase on a
classically dirty shot is intentionally outside the contract. No CUDA phase
claim is made.

This packet cannot be rebound to Q1272, Q1273, the later `2c79d2f` leader
source, or any other circuit by changing metadata. A different source requires
a new source schedule, stream and predictor identities, oracle fixtures,
predeclaration, and complete regression run.

## Build qualification

The packet's canonical Linux builder is
`.lane/stage-packet/build_phase_postfilter_linux.sh`. It requires Linux and
`g++`, verifies the sealed manifest, compiles with
`-O3 -std=c++17 -pthread -Wall -Wextra -Werror -Wno-unused-parameter`, checks
the executable identity, refuses packet-local or existing output paths, and
publishes through a same-directory no-clobber hard link. No binary is tracked.

The exact translation unit compiled and executed on the local arm64 Darwin
host with:

```sh
g++ -O3 -std=c++17 -pthread -Wall -Wextra -Werror \
  -Wno-unused-parameter -o /tmp/q1274-phasepostfilter-final \
  .lane/stage-packet/src/phasepostfilter.cpp
```

That local Mach-O binary SHA-256 was
`e5ac0b8d28e836a8c53c5ccf44f4cf593a75016d6634bccce48d41dbd7657b5a`.
The installed Zig `0.15.2` cross-toolchain also compiled the same sealed source
as a statically linked arm64 Linux ELF with the corresponding flags and
`-target aarch64-linux-musl`; its scratch-only SHA-256 was
`4d047f9ac8c9abf4753307f64d6daebb3b8caeab40402ab44c711c9772948298`.
The Linux ELF was format-qualified locally but not executed because this host
has no running Linux runtime. The exact logic and identity were executed by
the Darwin build; deployment must run the canonical Linux builder and verifier
on the target Linux CPU before use.

## Complete phase fixtures

The terminal verifier compared all complete sorted sets and their individual
SHA-256 values, in declared order, against the immutable ledgers:

- frozen23: `23/23`, 89 clean-phase faults; nonce-list SHA-256
  `4b3af025781591862eaf168d9c481e527aab8debf40a7ac3a0ee53960be4d54f`;
  `.lane/stage-packet/PHASE_FIXTURES.tsv` contains every complete sorted set
  and per-set hash and has ledger SHA-256
  `591cc3c5e1f7140dadbe192f5b98b3c971fb4725fd357752b7ef55bb3a03fe22`;
- blinded disjoint32: `32/32`, 146 clean-phase faults, one empty set and
  `288,768` evaluated shots; nonce-list SHA-256
  `6ec35ba16b516b8571c13c26ee503bf7de58af6a7f8d8aff37f3e37076db863a`;
  `.lane/stage-packet/PHASE_D32_FIXTURES.tsv` contains every complete sorted
  set and per-set hash and has ledger SHA-256
  `fee237d38468963ec114bf722467886cd5b97b117211480c0cef9a1ccf9df2de`.

The combined 55-row audit output was deterministic with SHA-256
`41fe001491f80273f6a4c86d92f50174f173f7bddd54bab90cb9ad023ce4d531`.
The inherited classically-clean canary `100000035106674` remained correctly
omitted because its complete clean-phase set is `{1753,5833}`.

## Production wrapper and fail-closed gates

Two wrapper runs on the same sealed binary, exact stream, and canary input
produced byte-identical output and receipts. The canonical one-row input hash
was `ca194eac8d578a7990b5fbea2bd09b6e34c3360cf3b2ca6c639549a85cc7cacb`;
the zero-row output and stdout hash was
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
the local receipt hash was
`68db77b0c4e2536d7948020d6ae7107508d04f5faf54d89732b37f756baa573b`.
The receipt binds binary/input/output hashes and row counts, source/count/stream
and predictor identities, stable input order, output schema, exact conditional
predicate, and raw/CUDA non-claims.

All negative gates passed:

- a dirty two-row input returned `4` with no output, receipt, or stdout;
- empty, unterminated, whitespace, signed, leading-zero, non-decimal,
  blank-line, duplicate, and `>=2^48` inputs were rejected `9/9` by both the
  executable and wrapper without publication;
- pre-existing output and pre-existing receipt paths returned `2`, preserved
  the existing bytes, and created neither peer artifact nor stdout;
- wrong magic stream
  `f0a120ef246eac3c76123dc478522977cbc543a773ba540ae23c9d6adf30ecf1`
  returned `1` before output;
- wrong-count stream
  `afb4eda48b819711710ae1e3f5eaf5fabdac2c1d19c2ffebe6a75d6e7d6abfeb`
  returned `2` before output;
- same-count, wrong-SHA stream
  `4daf97cffbdfd19fdd6df22d0d8861af49d6b11e0d87f43cb50aafbc85a04e38`
  returned `2` before output.

## Classical regression and terminal verdict

The verifier rebuilt the source stream from the frozen source, reproduced the
exact operation count and stream hash, rebuilt the current CPU predictor, and
reran the unchanged 22-case classical corpus. All `323/323` rows were set-equal
to `.lane/stage-packet/fixtures.local.tsv`, ledger SHA-256
`4889313f27a6f1daabd71f6b0c171459da8bf702424174923ec045e2990161e6`.
The mask histogram stayed `{1:136, 2:18, 4:148, 8:21}` with mask 16 absent.

Terminal command:

```sh
/usr/bin/time -p .lane/stage-packet/verify_phase_postfilter.sh \
  /tmp/fpsc/ops.bin /tmp/q1274-phasepostfilter-final
```

Result: PASS in `347.31s` wall (`371.58s` user, `5.67s` sys). No provider,
remote host, recovered-wave result, range scan, hunt, submission, or CUDA phase
work was used.
