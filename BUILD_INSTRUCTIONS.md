# PyTorch ROCm Build Instructions for AMD gfx90c

## Build Environment

### System Information
- **OS**: Linux (Ubuntu/Debian-based)
- **GPU**: AMD Radeon (gfx90c architecture)
- **ROCm Version**: 7.1.0
- **Python Version**: 3.11.14

### Build Prerequisites

```bash
# Install ROCm development libraries
sudo apt-get install rocrand-dev hiprand-dev rocblas-dev rocsparse-dev \
  hipsparse-dev rocfft-dev hipfft-dev rocthrust-dev hipcub-dev rocm-dev rocm-libs

# Verify ROCm installation
rocminfo | grep gfx
# Should show: gfx90c
```

## Building PyTorch from Source

### 1. Clone PyTorch Repository

```bash
cd ~/
git clone --recursive https://github.com/pytorch/pytorch
cd pytorch
git checkout v2.9.1
git submodule sync
git submodule update --init --recursive
```

### 2. Run HIPIFY Script

This converts CUDA code to HIP for AMD GPUs:

```bash
python tools/amd_build/build_amd.py
```

### 3. Set Up Python Virtual Environment

```bash
# Using uv (recommended)
cd pytorch
uv venv .venv
source .venv/bin/activate

# Install build dependencies
uv pip install cmake ninja setuptools wheel
```

### 4. Set Build Environment Variables

```bash
# Required environment variables
export PYTORCH_ROCM_ARCH=gfx90c
export CMAKE_PREFIX_PATH=/opt/rocm:$CMAKE_PREFIX_PATH

# Disable unsupported features for gfx90c
export USE_FLASH_ATTENTION=OFF
export USE_MEM_EFF_ATTENTION=OFF
export USE_ROCM_CK_GEMM=OFF
```

### 5. Build the Wheel

```bash
python setup.py bdist_wheel 2>&1 | tee build.log
```

**Build time**: Approximately 30-60 minutes depending on CPU

### 6. Verify Build

```bash
ls -lh dist/*.whl
```

You should see a file like:
```
dist/torch-2.9.1a0+gitd38164a-cp311-cp311-linux_x86_64.whl
```

## Complete Build Script

```bash
#!/bin/bash
set -e

# Navigate to pytorch directory
cd ~/pytorch

# Activate virtual environment
source .venv/bin/activate

# Clean previous build (optional)
# python setup.py clean
# rm -rf build

# Set environment variables
export PYTORCH_ROCM_ARCH=gfx90c
export CMAKE_PREFIX_PATH=/opt/rocm:$CMAKE_PREFIX_PATH
export USE_FLASH_ATTENTION=OFF
export USE_MEM_EFF_ATTENTION=OFF
export USE_ROCM_CK_GEMM=OFF

# Build wheel
python setup.py bdist_wheel 2>&1 | tee build_$(date +%Y%m%d_%H%M%S).log

echo "Build complete! Wheel file:"
ls -lh dist/*.whl
```

## Installing the Built Wheel

### Option 1: Install in a Different Virtual Environment

```bash
# Create and activate target virtual environment
cd /path/to/your/project
python -m venv myenv
source myenv/bin/activate

# Install the built wheel
pip install ~/pytorch/dist/torch-2.9.1a0+gitd38164a-cp311-cp311-linux_x86_64.whl

# Install additional packages if needed
pip install torchvision torchaudio
```

### Option 2: Install Using uv

```bash
# In your project directory
cd /path/to/your/project
uv venv
source .venv/bin/activate

# Install the wheel
uv pip install ~/pytorch/dist/torch-2.9.1a0+gitd38164a-cp311-cp311-linux_x86_64.whl
```

### Option 3: Install in Specific Environment by Path

```bash
# Install directly without activating venv
/path/to/your/venv/bin/pip install ~/pytorch/dist/torch-2.9.1a0+gitd38164a-cp311-cp311-linux_x86_64.whl
```

## Verification After Installation

Create a test script `test_gpu.py`:

```python
#!/usr/bin/env python3
import torch
import sys

print("=" * 60)
print("PyTorch AMD ROCm Verification")
print("=" * 60)

print(f"\nPyTorch version: {torch.__version__}")
print(f"ROCm version: {torch.version.hip if hasattr(torch.version, 'hip') else torch.version.cuda}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Architectures: {torch._C._cuda_getArchFlags()}")
    
    # Test simple GPU operation
    try:
        device = torch.device('cuda')
        a = torch.ones(10, 10, device=device)
        b = torch.ones(10, 10, device=device)
        c = a + b
        print("\n✅ GPU operations working!")
    except Exception as e:
        print(f"\n❌ GPU test failed: {e}")
        sys.exit(1)
else:
    print("\n❌ No GPU detected")
    sys.exit(1)
```

Run the test:

```bash
python test_gpu.py
```

Expected output:
```
============================================================
PyTorch AMD ROCm Verification
============================================================

PyTorch version: 2.9.1a0+gitd38164a
ROCm version: 7.1.25424
CUDA/ROCm available: True
GPU: AMD Radeon Graphics
Architectures: gfx90c

✅ GPU operations working!
```

## Troubleshooting

### Issue: "invalid device function" Error

If you still see this error, verify environment variables were set correctly during build:

```bash
grep "Building PyTorch for GPU arch:" ~/pytorch/build.log
# Should show: Building PyTorch for GPU arch: gfx90c
```

### Issue: GPU Not Detected After Installation

Check ROCm visibility:

```bash
rocm-smi
echo $HIP_VISIBLE_DEVICES
```

### Issue: Build Fails with AOTriton Errors

Ensure you set the environment variables to disable flash attention:

```bash
export USE_FLASH_ATTENTION=OFF
export USE_MEM_EFF_ATTENTION=OFF
```

### Issue: Build Fails with Composable Kernel Errors

Ensure CK GEMM is disabled:

```bash
export USE_ROCM_CK_GEMM=OFF
```

## Notes

- **gfx90c Limitations**: This is an older AMD GPU architecture (Vega). PyTorch 2.9+ has limited support, requiring several features to be disabled:
  - Flash Attention
  - Memory Efficient Attention
  - Composable Kernel GEMM optimizations

- **Performance**: The built wheel will work correctly but without some advanced GPU optimizations available on newer AMD GPUs (gfx10xx, gfx11xx).

- **Compatibility**: The wheel is specific to:
  - Python 3.11
  - Linux x86_64
  - ROCm 7.1

## Alternative: Pre-built PyTorch ROCm Wheels

If building from source continues to be problematic, consider using official PyTorch ROCm wheels (though they may not fully support gfx90c):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.0
```

Then use the HSA override workaround:

```bash
export HSA_OVERRIDE_GFX_VERSION=9.0.0
```
