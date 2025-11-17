# Overview

This is for a Beelink SRE8

## 1. Check what GPU you actually have

On this machine (Ryzen 7 5800H, “AMD Radeon Graphics”) it’s almost certainly the **integrated Vega iGPU** inside the CPU, not a discrete Radeon card.

Run:

```bash
lspci | grep -i vga
sudo lshw -C display
```

You’ll likely see something like *“Cezanne / Radeon Vega Graphics”*.

Now compare that to AMD’s official ROCm support list: it mainly includes **Instinct accelerators and a few newer discrete Radeon cards (RX 7900 / 7800 / 7700, etc.)**. Integrated Vega APUs like the 5800H are **not** on the official list. ([Radeon Open Compute Documentation][1])

There *are* some community hacks for 5800H/5800U APUs, but even people who got them running report them as fragile and breaking after a while. ([GitHub][2])

```shell
04:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Cezanne [Radeon Vega Series / Radeon Vega Mobile Series] (rev c5)
  *-display
       description: VGA compatible controller
       product: Cezanne [Radeon Vega Series / Radeon Vega Mobile Series]
       vendor: Advanced Micro Devices, Inc. [AMD/ATI]
       physical id: 0
       bus info: pci@0000:04:00.0
       logical name: /dev/fb0
       version: c5
       width: 64 bits
       clock: 33MHz
       capabilities: pm pciexpress msi msix vga_controller bus_master cap_list fb
       configuration: depth=32 driver=amdgpu latency=0 resolution=1920,1080
       resources: irq:41 memory:d0000000-dfffffff memory:e0000000-e01fffff ioport:e000(size=256) memory:fcc00000-fcc7ffff
```

So:

* **Officially supported / reliable**: No, not with this iGPU.
* **Hacky / experimental**: Maybe, if you’re willing to fight with ROCm.

---

## 2. What “PyTorch with AMD GPU support” actually needs

To get PyTorch using an AMD GPU you need:

1. **ROCm runtime + drivers** working with your GPU.
2. A **PyTorch build compiled for ROCm**, matching your ROCm version.
3. A GPU architecture that PyTorch/ROCm actually recognize (e.g. RDNA2/3 cards or Instinct).

If step 1 fails (common on unsupported APUs), PyTorch will fall back to CPU even if it’s installed “with ROCm”.

---

## 3. If you *add a supported AMD GPU* (recommended path)

If you ever plug in a supported discrete Radeon (e.g. RX 7700 XT, 7800 XT, 7900 XT/XTX or the newer RX 90xx series), then on Ubuntu 24.04.3 you can do roughly this:

### 3.1 Install ROCm on Ubuntu 24.04

Follow AMD’s official Ubuntu 24.04 instructions (ROCm 7.1 example) ([Radeon Open Compute Documentation][3]):

```bash
# 1) Add ROCm key
sudo mkdir --parents --mode=0755 /etc/apt/keyrings
wget https://repo.radeon.com/rocm/rocm.gpg.key -O - | \
    gpg --dearmor | sudo tee /etc/apt/keyrings/rocm.gpg > /dev/null

# 2) Add ROCm + graphics repos
sudo tee /etc/apt/sources.list.d/rocm.list << EOF
deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/7.1 noble main
deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/graphics/7.1/ubuntu noble main
EOF

sudo tee /etc/apt/preferences.d/rocm-pin-600 << EOF
Package: *
Pin: release o=repo.radeon.com
Pin-Priority: 600
EOF

sudo apt update
sudo apt install rocm-dev rocminfo
sudo usermod -a -G render,video "$USER"
```

Log out & back in (or reboot).

Verify ROCm sees the GPU:

```bash
/opt/rocm/bin/rocminfo | grep -i gfx
```

You should see something like `gfx1030` / `gfx1100` (varies by GPU).

### 3.2 Install PyTorch ROCm wheels

>NOTE: at this point take a look at [README](../README.md#installying-pytorch) -- which prefers using [uv](https://docs.astral.sh/uv/) from [Astral](https://astral.sh/)

Go to PyTorch’s *Get Started* page and choose:

* OS: **Linux**
* Package: **pip**
* Compute platform: **ROCm** (pick the version that matches your ROCm) ([PyTorch][4])

For example, if you install ROCm 6.4, they currently recommend something like:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.4
```

(Exact versions/URL may change; always copy from the PyTorch site.)

### 3.3 Test inside Python

```python
import torch

print("CUDA (HIP) available:", torch.cuda.is_available())
print("HIP runtime version:", torch.version.hip)
if torch.cuda.is_available():
    print("Device 0:", torch.cuda.get_device_name(0))
```

On ROCm, PyTorch still uses the `torch.cuda` API; it’s just backed by HIP.

If that prints `True` and your GPU name, you’re good.

---

## 4. Trying this on your **integrated 5800H GPU** (experimental)

If you want to experiment anyway:

1. **Install ROCm** as above.
2. Check whether `rocminfo` lists a GPU (you might see something like `gfx90c` for Vega). If ROCm doesn’t see it, PyTorch won’t either.
3. Install the PyTorch ROCm wheels matching your ROCm version (as in section 3.2).
4. Run the Python test code from 3.3.

Even if you manage to get:

* `torch.cuda.is_available() == True`
* a device name returned

you may still hit issues (crashes, wrong results, apps refusing to run) because this hardware is **not officially supported** for PyTorch/ROCm. ([Radeon Open Compute Documentation][1])

---

## 5. Practical options for you right now

Given this specific mini-PC:

1. **Use PyTorch on CPU only**
   Just install the standard CPU wheel:

   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

   This is 100% supported and stable; just slower for big models.

2. **Add a supported discrete GPU**
   If your box has a PCIe slot and enough power, a mid-range discrete Radeon that’s on the ROCm list (e.g. RX 7700 XT / 7800 XT / 7900 XT/XTX, or one of the newer RX 90xx cards) will make the ROCm + PyTorch route work much more cleanly. ([Radeon Open Compute Documentation][1])

3. **Use a remote GPU**
   Rent a cloud GPU instance (NVIDIA or AMD) and run your PyTorch code there, while developing locally.

---

### If you tell me:

* whether this machine has **only** the integrated GPU or also a discrete GPU, and
* what you’re planning to do (training big models vs. small experiments),

I can suggest a concrete setup (CPU-only, cloud, or “buy this specific card, then run these commands”).

[1]: https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html?utm_source=chatgpt.com "System requirements (Linux)"
[2]: https://github.com/nikelborm/amd-amdgpu-rocm-ollama-gfx90c-ati-radeon-vega-ryzen7-5800H-arch-linux/?utm_source=chatgpt.com "amd-amdgpu-rocm-ollama-gfx90c-ati-radeon-vega-ryzen7- ..."
[3]: https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/install-methods/package-manager/package-manager-ubuntu.html?utm_source=chatgpt.com "Ubuntu native installation"
[4]: https://pytorch.org/get-started/locally/?utm_source=chatgpt.com "Get Started"
