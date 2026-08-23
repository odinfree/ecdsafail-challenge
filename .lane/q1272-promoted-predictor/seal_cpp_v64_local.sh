#!/bin/bash
set -euo pipefail

repo=$(cd "$(dirname "$0")/../.." && pwd)
corpus="$repo/.lane/q1272-promoted-predictor/V64.nonces"
cpp=/private/tmp/ppcpu-q1272-promoted-batch
ops=/private/tmp/q1272-promoted-classical.TluCAa/ops.bin

die() { printf 'FATAL: %s\n' "$*" >&2; exit 2; }
hash() { sha256sum "$1" | awk '{print $1}'; }
assert_hash() { [[ -f $1 && $(hash "$1") == "$2" ]] || die "hash drift: $1"; }

[[ $# == 1 ]] || die 'usage: seal_cpp_v64_local.sh OUT'
out=$1
[[ -f $out/prediction.tsv && -f $out/PREDICTION.seal ]] || \
  die 'corrected Rust prediction is not sealed'
[[ ! -e $out/evaluator ]] || die 'trusted evaluator was opened before C++ seal'
[[ ! -e $out/cpp_prediction.tsv && ! -e $out/CPP_PREDICTION.seal ]] || \
  die 'C++ prediction output already exists'

git -C "$repo" merge-base --is-ancestor 3abf2af HEAD || \
  die 'corrected Rust checkpoint is not an ancestor of HEAD'
assert_hash "$corpus" \
  9db8b3a0fc0f277f8cea77cac181cc6133a667c96d5e73a97397a7116a6ec1bd
assert_hash "$repo/.lane/q1272-promoted-predictor/src/pp_model.h" \
  120979945f82318e9df77014fabea3d2f8a9dea3c433e1ff5636cb3cb654424b
assert_hash "$repo/.lane/q1272-promoted-predictor/src/pp_host.h" \
  b635c95deb5bab2b89ea65de4dafdba22ea4184a647c82d4bb5680450f976435
assert_hash "$repo/.lane/q1272-promoted-predictor/src/ppcpu.cpp" \
  37550fe3d8d1f1130cdc03a746ed5b4ea6bdb619475eebcddaeb087342457352
assert_hash "$cpp" \
  068a266f905ceac6c703ba7bac1695b22ae498818aa67d8daaec263a8be27243
assert_hash "$ops" \
  ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1

tmp=$(mktemp "$out/cpp_prediction.tsv.tmp.XXXXXX")
err=$(mktemp "$out/cpp_prediction.stderr.tmp.XXXXXX")
PPF_OPS="$ops" "$cpp" faultshots-file "$corpus" >"$tmp" 2>"$err"
python3 - "$tmp" <<'PY'
import sys
rows=[]
with open(sys.argv[1], encoding='ascii') as f:
    for line in f:
        fields=line.split()
        assert len(fields)==3, fields[:3]
        nonce,count,mask=int(fields[0]),int(fields[1]),fields[2]
        assert len(mask)==141*16 and all(c in '0123456789abcdef' for c in mask)
        assert sum(int(mask[i:i+16],16).bit_count() for i in range(0,len(mask),16))==count
        rows.append(nonce)
assert len(rows)==64 and rows==sorted(set(rows))
PY
cmp -s "$tmp" "$out/prediction.tsv" || die 'corrected Rust/C++ V64 masks differ'
mv "$tmp" "$out/cpp_prediction.tsv"
mv "$err" "$out/cpp_prediction.stderr"
{
  printf 'status=V64_CPP_PREDICTION_SEALED_EVALUATOR_UNOPENED\n'
  printf 'model_sha256=120979945f82318e9df77014fabea3d2f8a9dea3c433e1ff5636cb3cb654424b\n'
  printf 'host_sha256=b635c95deb5bab2b89ea65de4dafdba22ea4184a647c82d4bb5680450f976435\n'
  printf 'cpp_source_sha256=37550fe3d8d1f1130cdc03a746ed5b4ea6bdb619475eebcddaeb087342457352\n'
  printf 'binary_sha256=068a266f905ceac6c703ba7bac1695b22ae498818aa67d8daaec263a8be27243\n'
  printf 'corpus_sha256=%s\n' "$(hash "$corpus")"
  printf 'prediction_sha256=%s\n' "$(hash "$out/cpp_prediction.tsv")"
  printf 'rust_prediction_sha256=%s\n' "$(hash "$out/prediction.tsv")"
  printf 'stderr_sha256=%s\n' "$(hash "$out/cpp_prediction.stderr")"
  printf 'rows=64\nrust_cpp_complete_masks_equal=1\n'
} >"$out/CPP_PREDICTION.seal.tmp"
mv "$out/CPP_PREDICTION.seal.tmp" "$out/CPP_PREDICTION.seal"
sha256sum "$out/cpp_prediction.tsv" "$out/cpp_prediction.stderr" \
  "$out/CPP_PREDICTION.seal"
