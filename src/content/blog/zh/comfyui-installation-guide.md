---
title: "ComfyUI 安装教程:Windows、macOS 和 Linux 完整指南"
description: "干净准确的 ComfyUI 安装走读,涵盖 Windows 便携版、手动安装、系统要求、以及如何验证安装是否成功。已对照 ComfyUI 最新版本核对。"
pubDate: 2026-05-19
lang: zh
category: getting-started
heroImage: ../_assets/cover-installation.png
tags: ["安装", "入门", "windows", "macos", "linux"]
---

ComfyUI 是当下最灵活的 Stable Diffusion 等扩散模型运行界面。它把推理流程暴露成一张节点图,你可以构建、保存并分享完整的生成工作流。

本教程走通三条安装路径,以及实际操作中会出问题的地方。所有内容已对照 GitHub 上的 ComfyUI 最新版本核对。

## 系统要求

装之前先确认你的机器能跑动。

| 组件 | 最低 | 推荐 |
|------|------|------|
| 显卡 | NVIDIA 6 GB 显存,或 Apple Silicon,或 Linux 上的 AMD | NVIDIA 12 GB+ 显存 |
| 内存 | 16 GB | 32 GB |
| 硬盘 | 20 GB 可用 | 100 GB+ (模型很占地方) |
| 系统 | Windows 10/11、macOS 12+、Linux | 同上 |

技术上可以纯 CPU 跑,但每张图要几分钟。准备一块显卡。

几个要点:

- NVIDIA 显卡最稳,CUDA 支持成熟。
- Apple Silicon (M1/M2/M3/M4) 通过 PyTorch 的 MPS 后端跑得不错。
- AMD 显卡在 Linux 下通过 ROCm 工作。Windows 下走 DirectML 也能跑,但更慢、更脆弱。

## 方案一:Windows 便携版(最简单)

便携版是一个自包含的压缩包。不用装 Python、不用折腾依赖。如果你只想跑起来,选这条路。

1. 打开 ComfyUI 的 GitHub releases 页:<https://github.com/comfyanonymous/ComfyUI/releases>
2. 下载最新的 `ComfyUI_windows_portable_nvidia.7z`(没显卡就下 CPU 版)。
3. 用 [7-Zip](https://www.7-zip.org/) 解压。不要用 Windows 自带解压 — 偶尔会损坏长路径文件。
4. 进入解压后的文件夹,会看到两个批处理文件:
   - `run_nvidia_gpu.bat` — 在 NVIDIA 显卡上启动 ComfyUI
   - `run_cpu.bat` — CPU 模式启动
5. 双击 `run_nvidia_gpu.bat`。控制台窗口打开。等待这一行出现:`To see the GUI go to: http://127.0.0.1:8188`。
6. 浏览器打开 <http://127.0.0.1:8188>,会看到默认工作流。

关闭控制台窗口即可停止 ComfyUI。

### 常见问题

- **"CUDA is not available."** 把 NVIDIA 驱动升到最新的 Game Ready 或 Studio Driver。重启。重新运行 bat 文件。
- **6 GB 显卡爆显存。** 编辑 `run_nvidia_gpu.bat`,在启动行末尾加上 ` --lowvram`。4 GB 或更小用 ` --novram`。
- **解压时报长路径错误。** 把 7z 文件移到短路径下再解压,例如 `C:\Comfy\`。

## 方案二:Windows / Linux 手动安装

如果你想用系统 Python、打算开发自定义节点、或者你的发行版不适合便携版,选这条。

需要:

- Python 3.10、3.11 或 3.12(3.13 还没被所有自定义节点完全支持)
- Git
- NVIDIA 用户:最新驱动。**不需要**单独装 CUDA Toolkit — PyTorch 自带它需要的 CUDA 库。

### 步骤

```bash
# 1. 克隆仓库
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 2. 创建虚拟环境(强烈建议)
python -m venv venv

# 3. 激活
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# 4. 安装 PyTorch
# NVIDIA (Windows / Linux):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# AMD (仅 Linux):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1

# 纯 CPU:
pip install torch torchvision torchaudio

# 5. 安装其余依赖
pip install -r requirements.txt

# 6. 启动
python main.py
```

控制台输出 `To see the GUI go to: http://127.0.0.1:8188` 时,打开这个地址。

### 为什么必须用虚拟环境

自定义节点经常会锁定特定版本的 `transformers`、`diffusers` 或 `numpy`。不用 venv,这些安装会和系统其它环境冲突。一个坏节点能毁掉你的全局 Python。

## 方案三:macOS 安装

ComfyUI 在 Apple Silicon 上通过 MPS 后端运行。Intel Mac 官方不支持,会回退到 CPU。

```bash
# 1. 装 Homebrew(如果没有): https://brew.sh
# 2. 装 Python 和 Git
brew install python@3.11 git

# 3. 克隆并设置
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python3.11 -m venv venv
source venv/bin/activate

# 4. 安装带 MPS 支持的 PyTorch
pip install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu

# 5. 装其余依赖
pip install -r requirements.txt

# 6. 启动
python main.py --force-fp16
```

Apple Silicon 推荐加 `--force-fp16` 节省显存。

### macOS 注意事项

- 第一次启动后第一张图较慢,因为 PyTorch 会即时编译 MPS 内核。
- 8 GB 统一内存很紧 — SD 1.5 还能跑,大多数 SDXL 模型基本无法使用。
- 16 GB 起步才能舒服跑 SDXL。

## 添加第一个模型

ComfyUI 默认不带任何模型,必须下载至少一个 checkpoint 才能生成。

1. 选一个模型。第一次跑用 [Stable Diffusion 1.5](https://huggingface.co/runwayml/stable-diffusion-v1-5) 体积小、速度快。SDXL base 显存要求更高,但出图质量更好。
2. 下载 `.safetensors` 或 `.ckpt` 文件。
3. 放到 `ComfyUI/models/checkpoints/` 里。
4. 在浏览器里刷新 ComfyUI 页面。`Load Checkpoint` 节点的下拉框里就能看到这个文件了。

LoRA 放 `ComfyUI/models/loras/`,VAE 放 `ComfyUI/models/vae/`。目录结构按模型类型来分。

## 验证安装

ComfyUI 第一次打开时加载的默认工作流就是一个完整的文生图节点图。验证步骤:

1. 打开 <http://127.0.0.1:8188>。
2. 在 `Load Checkpoint` 节点里选你的模型。
3. 点 `Queue Prompt`(右上角,或叫 "Run",取决于 UI 版本)。
4. 等待。第一次最慢,因为模型要加载进显存。
5. `Save Image` 节点出现一张图。

看到图,说明装好了。

## 更新 ComfyUI

便携版:运行安装目录里的 `update/update_comfyui.bat`。

手动安装:

```bash
cd ComfyUI
git pull
source venv/bin/activate   # 或 Windows 等价命令
pip install -r requirements.txt
```

## 常见问题

### 需要单独装 CUDA Toolkit 吗?

不需要。PyTorch 的 NVIDIA wheel 自带它需要的 CUDA 库。只需要最新的 NVIDIA 驱动。

### 可以同时跑 ComfyUI 和 Automatic1111 吗?

同一个端口跑不了。两者都默认起本地 web 服务。停一个再开另一个,或者用 `--port 8189` 改端口。

### 生成的图存在哪里?

默认 `ComfyUI/output/`。可以用 `--output-directory /你的路径` 改。

### 模型占多少硬盘?

单个 SD 1.5 checkpoint 大约 2 GB。SDXL 大约 7 GB。FLUX.1 dev 大约 24 GB。深度玩家最后会有 50–500 GB 的模型库。

### 用便携版还是手动安装?

第一次玩、随便生成 → 便携版。开始写自定义节点、要锁定特定包版本 → 手动安装。

## 下一步

ComfyUI 已经跑起来了。下一步是搞懂节点图本身 — 每个节点是干什么的、数据怎么在节点之间流动。这是下一篇教程的主题。
