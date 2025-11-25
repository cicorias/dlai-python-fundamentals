#!/usr/bin/env bash

docker run -it --rm \
  --device=/dev/kfd \
  --device=/dev/dri \
  --group-add video \
  --ipc=host \
  --shm-size 8g \
  -e HSA_OVERRIDE_GFX_VERSION=11.0.0 \
  -v "$PWD":/workspace \
  -w /workspace \
  rocm/pytorch:rocm7.1_ubuntu24.04_py3.12_pytorch_release_2.8.0 \
  bash