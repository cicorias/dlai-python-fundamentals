#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${1:-gpu_diag}"
mkdir -p "$OUTDIR"

{
  echo "===== BASIC SYSTEM INFO ====="
  date
  uname -a
  echo

  echo "===== /etc/os-release ====="
  if [ -f /etc/os-release ]; then
    cat /etc/os-release
  else
    echo "/etc/os-release not found"
  fi
  echo

  echo "===== GPU (lspci) ====="
  if command -v lspci >/dev/null 2>&1; then
    lspci -nnk | grep -A3 -E 'VGA|3D'
  else
    echo "lspci not installed"
  fi
  echo

  echo "===== amdgpu kernel module ====="
  lsmod | grep amdgpu || echo "amdgpu not in lsmod"
  echo

  echo "===== last 50 amdgpu dmesg lines ====="
  dmesg | grep -i amdgpu | tail -n 50 || echo "no amdgpu lines in dmesg"
  echo

  echo "===== /dev/dri ====="
  ls -l /dev/dri || echo "/dev/dri missing"
  echo

  echo "===== user id/groups ====="
  id
  echo

  echo "===== lshw -C display ====="
  if command -v lshw >/dev/null 2>&1; then
    sudo lshw -C display || echo "lshw failed (maybe need sudo or package not installed)"
  else
    echo "lshw not installed"
  fi
} | tee "$OUTDIR/sys_gpu_info.txt"
