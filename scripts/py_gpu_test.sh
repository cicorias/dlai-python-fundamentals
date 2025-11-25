#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${1:-gpu_diag}"
mkdir -p "$OUTDIR"

{
  echo "===== PYTHON / PIP ====="
  if command -v python3 >/dev/null 2>&1; then
    python3 --version
    which python3 || true
  else
    echo "python3 not found"
  fi

  if command -v pip3 >/dev/null 2>&1; then
    pip3 --version
  else
    echo "pip3 not found"
  fi
  echo

  echo "===== GPU-RELATED PYTHON PACKAGES ====="
  if command -v pip3 >/dev/null 2>&1; then
    pip3 show torch 2>/dev/null || echo "torch not installed"
    pip3 show tensorflow-rocm 2>/dev/null || echo "tensorflow-rocm not installed"
    pip3 show tensorflow 2>/dev/null || echo "tensorflow (CPU or CUDA) not installed"
    pip3 show cupy 2>/dev/null || echo "cupy not installed"
  fi
  echo

  echo "===== PYTORCH GPU SMOKE TEST ====="
  if command -v python3 >/dev/null 2>&1; then
    python3 - << 'EOF'
import sys
print("Python:", sys.version)

try:
    import torch
except Exception as e:
    print("import torch FAILED:", e)
    raise SystemExit(0)

print("torch version:", torch.__version__)
print("torch.cuda.is_available():", torch.cuda.is_available())
print("torch.cuda.device_count():", torch.cuda.device_count())
print("torch.version.hip:", getattr(torch.version, "hip", None))

for i in range(torch.cuda.device_count()):
    try:
        name = torch.cuda.get_device_name(i)
    except Exception as e:
        name = f"<error getting name: {e}>"
    print(f"device {i}:", name)

# Quick tensor op on 'cuda' (ROCm build wires this to HIP under the hood)
if torch.cuda.is_available():
    try:
        device = torch.device("cuda:0")
        x = torch.randn(1024, 1024, device=device)
        y = torch.randn(1024, 1024, device=device)
        z = x @ y
        print("matmul ok, z mean:", float(z.mean()))
    except Exception as e:
        print("GPU matmul FAILED:", e)
EOF
  else:
    echo "python3 not found, skipping PyTorch test"
  fi
} | tee "$OUTDIR/python_gpu_test.txt"
