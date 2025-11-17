# Overview


## Installying PyTorch

on ROC

```shell

uv venv -p 3.12 --seed --clear && \
source .venv/bin/activate && \
uv pip install -U pip setuptools wheel && \
uv pip install -U -r requirements.txt && \
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.4


```