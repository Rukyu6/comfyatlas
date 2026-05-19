---
title: "ComfyUI Installation Guide for Windows, macOS, and Linux"
description: "A clean, accurate walkthrough for installing ComfyUI on Windows, macOS, and Linux — including the portable build, manual install, system requirements, and how to verify the install works."
pubDate: 2026-05-19
lang: en
tags: ["installation", "getting-started", "windows", "macos", "linux"]
---

ComfyUI is the most flexible interface for running Stable Diffusion and other diffusion models. It exposes the inference pipeline as a node graph, so you can build, save, and share complete generation workflows.

This guide walks through three install paths and the things that actually break in practice. It is verified against the current ComfyUI release on GitHub.

## System requirements

Before you install anything, check that your machine can run it.

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU       | NVIDIA 6 GB VRAM, or Apple Silicon, or AMD on Linux | NVIDIA 12 GB+ VRAM |
| RAM       | 16 GB   | 32 GB |
| Disk      | 20 GB free | 100 GB+ (models add up fast) |
| OS        | Windows 10/11, macOS 12+, Linux | same |

CPU-only is technically possible but generation will take minutes per image. Plan on a GPU.

A few things to know up front:

- NVIDIA GPUs work best because of mature CUDA support.
- Apple Silicon (M1/M2/M3/M4) works well using PyTorch's MPS backend.
- AMD GPUs work on Linux through ROCm. AMD on Windows is possible via DirectML but is slower and more fragile.

## Option 1: Windows portable build (easiest)

The portable build is a self-contained zip. No Python install, no dependency wrangling. This is the path to take if you just want it running.

1. Go to the ComfyUI GitHub releases page: <https://github.com/comfyanonymous/ComfyUI/releases>
2. Download the latest `ComfyUI_windows_portable_nvidia.7z` (or the CPU version if you have no GPU).
3. Extract with [7-Zip](https://www.7-zip.org/). Do not use the built-in Windows extractor — it sometimes corrupts long paths.
4. Open the extracted folder. You will see two batch files:
   - `run_nvidia_gpu.bat` — start ComfyUI on your NVIDIA GPU.
   - `run_cpu.bat` — start in CPU mode.
5. Double-click `run_nvidia_gpu.bat`. A console window opens. Wait for the line `To see the GUI go to: http://127.0.0.1:8188`.
6. Open <http://127.0.0.1:8188> in your browser. You should see the default workflow.

To stop ComfyUI, close the console window.

### What can go wrong

- **"CUDA is not available."** Update your NVIDIA driver to the latest Game Ready or Studio Driver. Reboot. Re-run the bat file.
- **Out of memory on a 6 GB card.** Edit `run_nvidia_gpu.bat` and add ` --lowvram` to the launch line. For 4 GB or less, use ` --novram`.
- **Long path errors when extracting.** Move the 7z file to a short path like `C:\Comfy\` before extracting.

## Option 2: Manual install on Windows / Linux

Use this path if you want a system Python install, plan to develop custom nodes, or your distribution doesn't fit the portable build.

You need:

- Python 3.10, 3.11, or 3.12 (3.13 is not yet fully supported by all custom nodes)
- Git
- For NVIDIA: a current driver. CUDA Toolkit is **not** required — PyTorch ships its own CUDA libraries.

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 2. Create a virtual environment (strongly recommended)
python -m venv venv

# 3. Activate it
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# 4. Install PyTorch
# NVIDIA (Windows / Linux):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# AMD (Linux only):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1

# CPU-only:
pip install torch torchvision torchaudio

# 5. Install the rest
pip install -r requirements.txt

# 6. Launch
python main.py
```

When the console prints `To see the GUI go to: http://127.0.0.1:8188`, open that URL.

### Why a virtual environment

Custom nodes often pin specific versions of `transformers`, `diffusers`, or `numpy`. Without a venv, those installs collide with anything else on your system. One bad node can wreck your global Python.

## Option 3: macOS install

ComfyUI runs on Apple Silicon using the MPS backend. Intel Macs are not officially supported and will fall back to CPU.

```bash
# 1. Install Homebrew if you don't have it: https://brew.sh
# 2. Install Python and Git
brew install python@3.11 git

# 3. Clone and set up
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python3.11 -m venv venv
source venv/bin/activate

# 4. Install PyTorch with MPS support
pip install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu

# 5. Install the rest
pip install -r requirements.txt

# 6. Launch
python main.py --force-fp16
```

`--force-fp16` is recommended on Apple Silicon for memory efficiency.

### macOS gotchas

- The first generation after a fresh launch is slow because PyTorch compiles MPS kernels on the fly.
- 8 GB unified memory is tight — you can run SD 1.5 models but most SDXL models will be unusable.
- 16 GB or more is the practical floor for SDXL.

## Adding your first model

ComfyUI ships with no models. You must download at least one checkpoint to generate anything.

1. Pick a model. For a first run, [Stable Diffusion 1.5](https://huggingface.co/runwayml/stable-diffusion-v1-5) is small and fast. SDXL base needs more VRAM but produces better images.
2. Download the `.safetensors` or `.ckpt` file.
3. Place it in `ComfyUI/models/checkpoints/`.
4. Reload the ComfyUI page in your browser. The `Load Checkpoint` node should now show your file in its dropdown.

For LoRAs, place them in `ComfyUI/models/loras/`. For VAEs, `ComfyUI/models/vae/`. The folder structure mirrors the model type.

## Verifying the install works

The default workflow that loads when you first open ComfyUI is a complete text-to-image graph. To verify everything works:

1. Open <http://127.0.0.1:8188>.
2. In the `Load Checkpoint` node, select your model.
3. Click `Queue Prompt` (top right, or the "Run" button depending on UI version).
4. Wait. The first run is slowest because it loads the model into VRAM.
5. An image appears in the `Save Image` node.

If you see an image, the install is good.

## Updating ComfyUI

For the portable build, run `update/update_comfyui.bat` inside the install folder.

For manual installs:

```bash
cd ComfyUI
git pull
source venv/bin/activate   # or the Windows equivalent
pip install -r requirements.txt
```

## Frequently asked questions

### Do I need to install CUDA Toolkit separately?

No. PyTorch's NVIDIA wheels include the CUDA libraries it needs. You only need a current NVIDIA driver.

### Can I run ComfyUI and Automatic1111 at the same time?

Not on the same port. They both default to a local web server. Stop one before starting the other, or change the port with `--port 8189`.

### Where do my generated images go?

`ComfyUI/output/` by default. You can change this with `--output-directory /your/path`.

### How much disk space do models take?

A single SD 1.5 checkpoint is ~2 GB. SDXL is ~7 GB. FLUX.1 dev is ~24 GB. A serious user ends up with 50–500 GB of models.

### Should I use the portable build or manual install?

Portable for first-time use and casual generation. Manual when you start writing custom nodes or pinning specific package versions.

## Next steps

You have ComfyUI running. The next thing to learn is the node graph itself — what each node does and how data flows between them. That's the focus of the next guide.
