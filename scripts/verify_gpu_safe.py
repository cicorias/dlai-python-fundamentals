#!/usr/bin/env python3
import torch, sys

print("=" * 60)
print("PyTorch AMD ROCm Minimal Test")
print("=" * 60)

print(f"torch version      : {torch.__version__}")
print(f"torch.version.hip  : {getattr(torch.version, 'hip', None)}")
print(f"torch.version.cuda : {getattr(torch.version, 'cuda', None)}")

if not torch.cuda.is_available():
    print("\n✗ torch.cuda.is_available() = False (no ROCm-visible GPU)")
    sys.exit(1)

print("\n✓ torch.cuda.is_available() = True")
n = torch.cuda.device_count()
print(f"✓ device count: {n}")

for i in range(n):
    props = torch.cuda.get_device_properties(i)
    print(f"  [GPU {i}] name={props.name}, total_mem={props.total_memory/1024**3:.2f} GB")

device = torch.device("cuda:0")
torch.cuda.set_device(device)

print("\n--- Step 1: tiny tensor roundtrip ---")
x = torch.tensor([1.0, 2.0, 3.0], device=device)
torch.cuda.synchronize()
print("✓ x on device:", x)

print("\n--- Step 2: small matmul ---")
a = torch.randn(128, 128, device=device)
b = torch.randn(128, 128, device=device)
c = a @ b
torch.cuda.synchronize()
print("✓ matmul(128x128) done, mean:", float(c.mean()))

print("\n--- Step 3: small backward ---")
u = torch.randn(16, 16, device=device, requires_grad=True)
v = (u * u).sum()
v.backward()
torch.cuda.synchronize()
print("✓ backward done, grad norm:", float(u.grad.norm()))

print("\n✅ Minimal ROCm test finished without crash.")
