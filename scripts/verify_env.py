#!/usr/bin/env python3
"""Quick AMD ROCm + PyTorch verification script"""

import torch
import sys

print("=" * 60)
print("PyTorch AMD ROCm Verification")
print("=" * 60)

# 1. PyTorch version and ROCm
print(f"\n✓ PyTorch version: {torch.__version__}")
print(f"✓ ROCm version: {torch.version.hip if hasattr(torch.version, 'hip') else torch.version.cuda}")

# 2. CUDA/ROCm available
cuda_available = torch.cuda.is_available()
print(f"\n{'✓' if cuda_available else '✗'} CUDA/ROCm available: {cuda_available}")

if not cuda_available:
    print("\n❌ No GPU detected. PyTorch is CPU-only.")
    sys.exit(1)

# 3. Device info
device_count = torch.cuda.device_count()
print(f"✓ GPU count: {device_count}")

for i in range(device_count):
    print(f"\n--- GPU {i} ---")
    print(f"  Name: {torch.cuda.get_device_name(i)}")
    print(f"  Capability: {torch.cuda.get_device_capability(i)}")
    props = torch.cuda.get_device_properties(i)
    print(f"  Total Memory: {props.total_memory / 1024**3:.2f} GB")

# 4. Architecture flags
print(f"\n✓ Compiled architectures: {torch._C._cuda_getArchFlags()}")

# 5. Simple tensor test
print("\n--- Testing GPU Operations ---")
try:
    device = torch.device('cuda')
    
    # Create tensors
    a = torch.randn(1000, 1000, device=device)
    b = torch.randn(1000, 1000, device=device)
    
    # Matrix multiplication
    c = torch.matmul(a, b)
    
    # Check result
    assert c.shape == (1000, 1000)
    assert c.device.type == 'cuda'
    
    print("✓ Matrix multiplication: PASSED")
    print("✓ Tensor operations: WORKING")
    
    # Test backward pass
    x = torch.randn(10, 10, device=device, requires_grad=True)
    y = x ** 2
    loss = y.sum()
    loss.backward()
    
    assert x.grad is not None
    print("✓ Backward pass: WORKING")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - GPU is ready for training!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ GPU test FAILED: {e}")
    print("\nThis is the error you'd see during training.")
    sys.exit(1)