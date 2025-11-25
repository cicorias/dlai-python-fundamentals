#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${1:-gpu_diag}"
mkdir -p "$OUTDIR"

{
  echo "===== ROCm / HIP PACKAGES ====="
  dpkg -l | grep -i rocm || echo "no rocm* packages found via dpkg"
  echo

  echo "===== hipconfig -a ====="
  if command -v hipconfig >/dev/null 2>&1; then
    hipconfig -a 2>&1
  else
    echo "hipconfig not in PATH"
  fi
  echo

  echo "===== rocminfo ====="
  if command -v rocminfo >/dev/null 2>&1; then
    rocminfo 2>&1
  else
    echo "rocminfo not in PATH"
  fi
} | tee "$OUTDIR/rocm_status.txt"
