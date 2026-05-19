---
title: "你的第一个 ComfyUI 工作流:文生图分步搭建"
description: "从空白画布开始,在 ComfyUI 里搭一个完整的文生图工作流。逐个加节点、连线、生成第一张图。包含确切的参数设置和出问题时怎么办。"
pubDate: 2026-05-19
lang: zh
category: getting-started
tags: ["工作流", "教程", "文生图", "入门", "stable-diffusion"]
---

学懂 ComfyUI 最快的方式就是动手搭一个。第一次启动加载的默认工作流是能用,但它是黑盒 — 节点已经摆好了,你看不到为什么这样连。

本文带你从空白画布亲手搭出同一个工作流。看完你会有第一张生成图,而且清楚每个节点为什么连到哪。

还没装 ComfyUI?看[安装教程](/zh/blog/comfyui-installation-guide/)。不知道节点是什么?先看[节点详解](/zh/blog/understanding-comfyui-nodes/) — 那篇讲清楚了我们待会要连的七个核心节点。

## 准备

- ComfyUI 在 http://127.0.0.1:8188 跑着
- `ComfyUI/models/checkpoints/` 里至少有一个 Stable Diffusion checkpoint
- 显存最低 6 GB(SDXL 推荐 8 GB)

第一次玩推荐 **Stable Diffusion 1.5 base** — 体积小、速度快、容错高。SDXL 也行但生成更慢、占显存更多。

## 第一步:清空画布

在浏览器里打开 ComfyUI,会看到默认工作流。

清空:

- 在画布上右键 → `Clear`
- 或者按 `Ctrl+A` 全选 → `Delete`

现在应该是空白的灰色画布。中键拖动平移,滚轮缩放。

## 第二步:加 Load Checkpoint

在空白画布上双击,弹出搜索框。

输入 `Load Checkpoint`,点结果。节点落在光标位置。

这个节点有:

- 一个控件:列出你 checkpoint 的下拉菜单
- 右侧三个输出:MODEL、CLIP、VAE

点下拉选你的 checkpoint。如果是空的,说明 `models/checkpoints/` 里没有模型。

## 第三步:加两个 CLIP Text Encode 节点

双击画布 → 搜 `CLIP Text Encode` → 加上。

把它拖到 `Load Checkpoint` 右边,留出连线空间。

连线:

1. 点 `Load Checkpoint` 右边的 **CLIP** 输出(黄色 socket)
2. 拖一根线到 `CLIP Text Encode` 左边的 **clip** 输入(也是黄色)
3. 松手。一根黄线出现。

点节点里的文字框,输入**正向提示词**:

```
a cinematic photo of a fox sitting on a moss-covered rock in a misty forest, golden hour lighting, sharp focus
```

再用同样方式加第二个 `CLIP Text Encode` 节点。把它的 `clip` 输入连到 `Load Checkpoint` 同一个 `CLIP` 输出(一个输出可以分给多个输入)。

第二个节点的文字框里输入**负向提示词**:

```
blurry, low quality, watermark, text, deformed, extra limbs
```

小贴士:右键节点 → `Rename` 把它们改名为 "Positive" 和 "Negative",免得搞混。

## 第四步:加 Empty Latent Image

双击 → 搜 `Empty Latent Image` → 加。

放到提示词节点下方。

它有三个控件、一个输出(LATENT)。设置控件:

- **width**:512(SD 1.5)或 1024(SDXL)
- **height**:512 或 1024
- **batch_size**:1

这个节点没有输入,只是按你给的尺寸创建空白画布。

## 第五步:加 KSampler

双击 → 搜 `KSampler` → 加。

放到所有节点的右侧。KSampler 是工作流的心脏。

KSampler 有四个输入:

- **model**(紫色)
- **positive**(橙色)— CONDITIONING
- **negative**(橙色)
- **latent_image**(粉色)

连线:

1. `Load Checkpoint` → MODEL → KSampler → model
2. 正向 `CLIP Text Encode` → CONDITIONING → KSampler → positive
3. 负向 `CLIP Text Encode` → CONDITIONING → KSampler → negative
4. `Empty Latent Image` → LATENT → KSampler → latent_image

控件配置:

- **seed**:任意数字,或点 `randomize`
- **control_after_generate**:`randomize`(每次跑出新图)
- **steps**:20
- **cfg**:7.0
- **sampler_name**:`euler`(从简单的开始)
- **scheduler**:`normal`
- **denoise**:1.0(满噪声,纯文生图)

第一次跑别动这些参数。先有一个能用的基线,再开始实验。

## 第六步:加 VAE Decode

双击 → 搜 `VAE Decode` → 加。

放到 KSampler 右边。VAE Decode 把 KSampler 输出的 latent 转成可见图像。

两个输入:

- **samples**(粉色)— LATENT
- **vae**(红色)— VAE

连线:

1. KSampler → LATENT → VAE Decode → samples
2. Load Checkpoint → VAE → VAE Decode → vae

## 第七步:加 Save Image

双击 → 搜 `Save Image` → 加。

放在最右边。VAE Decode → IMAGE → Save Image → images。

`filename_prefix` 控件控制文件名前缀,改成好认的,比如 `forest-fox`。

也可以用 `Preview Image`(只在浏览器显示不存盘)。调提示词时方便。

## 第八步:生成

看一眼画布,你应该有七个节点连成这样:

```
Load Checkpoint ─┬─ MODEL ──────────────┐
                 ├─ CLIP ──┬─ Positive ──┼─ KSampler ─ VAE Decode ─ Save Image
                 │         └─ Negative ──┤
                 └─ VAE ─────────────────│──────────────┘
                                         │
                  Empty Latent Image ────┘
```

按 `Q` 或点 `Queue Prompt`(右上角附近)。

每个节点跑到时变绿。KSampler 显示进度条。

第一次最慢,因为模型要加载进显存。SD 1.5 几秒,SDXL 第一次更长。

跑完图出现在 `Save Image` 节点里。文件在 `ComfyUI/output/`。

## 保存和复用工作流

工作流能用了就保存下来。

- 点菜单里的 `Save` 按钮,或按 `Ctrl+S`
- 把 JSON 文件存到你记得住的地方

恢复工作流:

- 把 JSON 文件拖到 ComfyUI 画布上
- 或点 `Load` 选文件

还可以把 ComfyUI 生成的 **PNG 图片**拖回画布。ComfyUI 把工作流元数据嵌进了 PNG,拖回去就能恢复出原来那张图的完整图。这是 ComfyUI 最贴心的特性之一。

## 调提示词

有了能用的基线,开始尝试改东西:

- **改正向提示词。**重新队列。如果想固定种子对比,把 `control_after_generate` 设为 `fixed`。
- **改种子。**同样的提示词,不同的图。
- **steps 提到 30。**画面更精细,稍慢。
- **换采样器。**`dpmpp_2m` + `karras` 调度器是 SD 1.5 和 SDXL 的常用组合。
- **改分辨率。**768×512 横图,512×768 竖图。贴近原生(SD 1.5 的 512,SDXL 的 1024)。

一次只改一项。一次改五项后图变烂,你不知道是哪项的锅。

## 故障排查

### "Error occurred when executing CLIPTextEncode"

通常是 checkpoint 没加载好或 CLIP 模型缺失。看 ComfyUI 控制台里的 Python 错误细节。

### 显存不足(OOM)

先把分辨率降到 512×512。能跑了再往上爬。

8 GB 卡跑 SDXL,启动 ComfyUI 加 `--lowvram`(改 bat 文件或命令行)。6 GB 卡用 `--medvram`。

### 生成的图全是灰色或纯噪声

通常是 VAE 没接对,或 checkpoint 损坏。检查 VAE 这根线是不是从 `Load Checkpoint` 连到 `VAE Decode`。如果模型本身不带 VAE(罕见),需要单独 `Load VAE` 节点加载。

### 图模糊一团

- 文生图设置里 denoise 低于 1.0,改回 1.0
- cfg 太低(<3)或太高(>14),回到 7
- steps 太低(<10),试 20

### KSampler 跑了但没有图

你忘了把 VAE Decode 接到 Save Image,或者整个 VAE Decode 都没加。KSampler 的输出是 latent,不是图,必须经 VAE Decode 才能变成图。

### 每次都是同一张图

`control_after_generate` 设成了 `fixed`,改成 `randomize`。

## 你学到了什么

你从零搭出了一条完整的文生图流水线,你现在知道:

- 文生图必备的七个核心节点
- 它们怎么连、为什么这样连
- KSampler 各项控件干啥
- 怎么保存和恢复工作流
- 出问题时往哪里看

这条流水线是地基。图生图、局部重绘、ControlNet、LoRA、放大,全是从这张图加节点改出来的。先把这一条玩熟。

## 下一步

从这里可以往几个方向走:

- **图生图。**把 `Empty Latent Image` 替换成 `Load Image` + `VAE Encode`。`denoise` 降到 0.5–0.7,在已有图上变出新图,而不是从噪声生成。
- **LoRA。**在 `Load Checkpoint` 和后续节点之间插一个 `Load LoRA` 节点,套上画风或角色 LoRA。
- **放大。**在 `VAE Decode` 之后加放大节点(`Upscale Image By` 或基于模型的 `UpscaleModelLoader` + `ImageUpscaleWithModel`)把图放大。

每个方向后面会有专题教程。
