#!/usr/bin/env python3
import torch
import sys
import time

print("=" * 60)
print("Quick GPU Check")
print("=" * 60)

print(f"PyTorch: {torch.__version__}")
print(f"ROCm: {torch.version.hip if hasattr(torch.version, 'hip') else torch.version.cuda}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Architectures: {torch._C._cuda_getArchFlags()}")
    
    print("\n--- Testing small tensor (10 seconds max) ---")
    
    try:
        device = torch.device('cuda')
        
        # Timeout wrapper
        start = time.time()
        print("Creating small tensor on GPU...")
        a = torch.ones(10, 10, device=device)
        elapsed = time.time() - start
        
        print(f"✓ Tensor created in {elapsed:.2f}s")
        
        if elapsed > 5:
            print("⚠️  WARNING: Very slow - likely kernel incompatibility")
        
        # Try simple operation
        start = time.time()
        b = a + a
        elapsed = time.time() - start
        print(f"✓ Addition in {elapsed:.2f}s")
        
        if elapsed > 5:
            print("❌ GPU operations too slow - incompatible kernels")
            sys.exit(1)
        
        print("\n✅ GPU works!")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        sys.exit(1)
else:
    print("❌ No GPU detected")
    sys.exit(1)