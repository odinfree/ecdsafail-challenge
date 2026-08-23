#!/usr/bin/env bash
# Build the CUDA prefilter.  RTX 4090 = sm_89.
#
# ALL COMPUTE RUNS ON THE GPU BOX.  On Windows this shells out to
# vcvars64.bat first, because nvcc needs MSVC's cl.exe plus its INCLUDE/LIB
# in the environment; a bare `nvcc` from Git Bash fails with
# "Cannot find compiler 'cl.exe' in PATH".
set -e
cd "$(dirname "$0")"
ARCH="${ARCH:-sm_89}"
OUT="${OUT:-pingpong_gpu}"
NVCC_FLAGS="-arch=$ARCH -O3 -lineinfo -Xptxas -v -Xptxas -O3 -allow-unsupported-compiler ${NVCC_EXTRA:-}"

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    VCVARS="${VCVARS:-}"
    if [ -z "$VCVARS" ]; then
      VSWHERE="/c/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe"
      if [ -x "$VSWHERE" ]; then
        VSPATH="$("$VSWHERE" -latest -products '*' -property installationPath | tr -d '\r')"
        [ -n "$VSPATH" ] && VCVARS="$VSPATH\\VC\\Auxiliary\\Build\\vcvars64.bat"
      fi
    fi
    if [ -z "$VCVARS" ]; then
      echo "build.sh: could not locate vcvars64.bat; set VCVARS=<path> and retry" >&2
      exit 1
    fi
    echo "vcvars: $VCVARS"
    echo "nvcc $NVCC_FLAGS -o $OUT.exe pingpong_filter.cu"
    cat > .build.bat <<BAT
@echo off
call "$VCVARS" >nul
if errorlevel 1 exit /b 1
nvcc $NVCC_FLAGS -o $OUT.exe pingpong_filter.cu
BAT
    cmd.exe //c .build.bat
    rm -f .build.bat
    echo "built $OUT.exe"
    ;;
  *)
    echo "nvcc $NVCC_FLAGS -o $OUT pingpong_filter.cu"
    nvcc $NVCC_FLAGS -o "$OUT" pingpong_filter.cu
    echo "built $OUT"
    ;;
esac
