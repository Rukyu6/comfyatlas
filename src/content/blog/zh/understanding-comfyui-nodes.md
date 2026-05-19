---
title: "理解 ComfyUI 节点:写给新手的可视化指南"
description: "ComfyUI 节点到底是什么、数据怎么在节点之间流动、组成默认文生图工作流的七个核心节点。写给第一次打开 ComfyUI 的人。"
pubDate: 2026-05-19
lang: zh
tags: ["节点", "入门", "基础", "stable-diffusion"]
---

第一次打开 ComfyUI,你会看到一堆方框被彩色线连起来。看着吓人。其实不是。

ComfyUI 工作流就是一串小操作的链条。每个方框(节点)接收输入、做一件事、把输出传给下一个方框。一旦你搞懂七个核心节点干啥,网上任何文生图工作流你都看得懂。

本文按节点拆解默认工作流。前提是你已经装好 ComfyUI 并加载了一个 checkpoint。没装看[安装教程](/zh/blog/comfyui-installation-guide/)。

## 节点是怎么工作的

每个节点有三个部分:

- **输入(Inputs)**在左边。小圆点(socket),线接进来的地方。
- **输出(Outputs)**在右边。线接出去的地方。
- **控件(Widgets)**在中间。直接填的字段:文字、数字、下拉菜单。

线把一个节点的输出 socket 接到另一个节点的输入 socket。数据从左流到右。

你点 `Queue Prompt` 时,ComfyUI 从最右边的节点(`Save Image`)开始,反向追溯它需要什么,按依赖顺序运行每个节点。你不用告诉它顺序。图本身就是顺序。

## 七种数据类型

socket 是有颜色的。颜色告诉你这条线流的是什么数据。只有相同颜色的输出和输入才能连。

| 颜色 | 类型 | 是什么 |
|------|------|--------|
| 紫色 | MODEL | 扩散模型本身(U-Net) |
| 黄色 | CLIP | 文本编码器 |
| 红色 | VAE | 变分自编码器(潜空间 ↔ 像素的转换器) |
| 橙色 | CONDITIONING | 编码后的提示词 — 文字过 CLIP 后的产物 |
| 粉色 | LATENT | 潜空间里的图像(压缩格式,模型实际处理的对象) |
| 蓝色 | IMAGE | 普通的 RGB 图像,你能看的那种 |
| 灰色 | INT / FLOAT / STRING | 普通数字和文字 |

具体颜色在 ComfyUI 不同版本之间可能略有差异,但这些类别是稳定的。

为什么类型这么多?因为扩散过程本身就这么复杂。模型不在像素上做运算,它在压缩表示 — 也就是 **latent** 上做。VAE 把像素压缩成 latent,再把 latent 解压回像素。模型每一步接收一个 latent 加一个 CONDITIONING(编码后的提示词),输出一个噪声更少的 latent,反复多次。

## 默认工作流逐节点拆解

第一次启动 ComfyUI 默认加载的图就是一条完整的文生图流水线。每个节点干啥如下。

### 1. Load Checkpoint(加载模型)

入口节点。读 `models/checkpoints/` 下的 checkpoint 文件,输出三样东西:

- **MODEL** — 真正干活的扩散模型,把噪声 latent 变干净
- **CLIP** — checkpoint 里打包好的文本编码器
- **VAE** — checkpoint 里打包好的自编码器

一个 checkpoint 是单个文件(通常是 `.safetensors`),把这三样打包在一起。SDXL、SD 1.5、FLUX 的 checkpoint 全用同一个 `Load Checkpoint` 节点,模型自己知道自己是什么。

下拉控件列出 `models/checkpoints/` 里的所有 checkpoint。刚加的新模型没出现?点 ComfyUI 右上角的刷新图标即可。

### 2. CLIP Text Encode (Prompt) — 正向提示词

这个节点接收:

- **CLIP** 输入(从 `Load Checkpoint`)
- 一个 **text** 控件,你在里面打提示词

输出 **CONDITIONING** — 提示词被编码成模型能用的格式。

默认连了两个这种节点。一个是**正向提示词**(你想要的),一个是**负向提示词**(你不想要的)。

你打的字会被 CLIP 的分词器和编码器处理。模型从来看不到你的原文,它看到的是向量表示。

### 3. CLIP Text Encode (Prompt) — 负向提示词

同一个节点的第二份,用来填负向提示词。常见起步负向提示词类似 `blurry, low quality, watermark`(模糊、低质量、水印)。一些较新的模型(FLUX、SD3)完全不理负向提示词 — 留空即可。

### 4. Empty Latent Image(空 latent 画布)

创建一张空白的 latent 画布。三个控件:

- **width** — 输出图像宽度(SD 1.5 必须是 8 的倍数,SDXL 推荐 64 的倍数)
- **height** — 输出图像高度
- **batch_size** — 一次生成几张

输出 **LATENT** — 一个全是零、按要求尺寸的张量。KSampler 会往里灌噪声然后逐步去噪。

要记的几个原生分辨率:
- SD 1.5:512×512
- SDXL:1024×1024
- FLUX:1024×1024

比原生大太多会出现拼接伪影,小太多会出现五官扭曲。第一次跑就贴近原生分辨率。

### 5. KSampler(采样器)

主力节点。接收:

- **MODEL** — 来自 `Load Checkpoint`
- **positive** — 正向提示词编码器输出的 CONDITIONING
- **negative** — 负向提示词编码器输出的 CONDITIONING
- **latent_image** — 上一步产出的空 LATENT

控件:

- **seed** — 随机种子。同样的种子+同样的输入=同一张图。点骰子图标(randomize)每次出新图。
- **control_after_generate** — `randomize`、`fixed`、`increment`、`decrement`。每次生成后种子怎么处理。
- **steps** — 去噪迭代次数。大多数采样器 20 步是合理默认。步数越多越慢,但不一定越好。
- **cfg** — 分类器自由引导强度,即对提示词的服从度。7 是合理默认。低于 3 太松,高于 12 开始出伪影。
- **sampler_name** — 采样算法。`euler` 又快又稳。`dpmpp_2m` 出图更锐利。`dpmpp_3m_sde` 慢但质量高。
- **scheduler** — 噪声调度形状。`normal` 够用。`karras` 通常出图略好。
- **denoise** — 输入 latent 中替换为噪声的比例。纯文生图用 `1.0`,小于 1 是图生图场景。

输出 **LATENT** — 你生成的图,但还在 latent 压缩态。

### 6. VAE Decode(VAE 解码)

KSampler 输出的 latent 还看不了。它是 4 通道、最终尺寸的 1/8。这个节点把它转回像素。

输入:
- **samples** — KSampler 输出的 LATENT
- **vae** — `Load Checkpoint` 输出的 VAE

输出:**IMAGE** — 终于能看的普通 RGB 图。

### 7. Save Image(保存图片)

终点节点。接收 IMAGE,写到 `ComfyUI/output/`。`filename_prefix` 控件控制文件名前缀。

还有一个 `Preview Image` 节点,只在浏览器里显示不保存。调提示词时很有用。

## 把数据流当一句话来读

把默认工作流当一个句子读:

`Load Checkpoint` 提供 MODEL、CLIP、VAE。
↓
CLIP 喂给两个 `CLIP Text Encode` 节点(正向和负向),输出两个 CONDITIONING。
↓
`Empty Latent Image` 产出空白画布。
↓
`KSampler` 把 MODEL + 两个 CONDITIONING + LATENT 拼起来,跑去噪。
↓
`VAE Decode` 用 VAE 把结果 latent 转成像素。
↓
`Save Image` 把像素写到磁盘。

脑子里能这样读出来,你就能读任何工作流。

## 怎么往画布上加节点

三种方式:

1. **右键**空白处 → `Add Node` → 按分类菜单往下找
2. **双击**空白处 → 搜索框。开始打 `KSampler`、`CLIP` 等 — 最快的方法
3. **从 socket 拖一根线**到空白处 → 松手。ComfyUI 只列出有匹配类型 socket 的节点

双击搜索是最常用的,记住它。

## 连线和断线

- 点输出 socket 拖到同色输入 socket 即连接
- 点已有的线选中
- 右键线 → `Delete` 删除。或者把线尾拖到空白处
- 一个输入只能接一根线,一个输出可以分叉给多个

类型不匹配,线会弹回去。颜色就是允许范围的提示。

## 自定义节点

上面七个是核心节点,ComfyUI 自带的。社区另外做了上千个自定义节点。ControlNet 预处理器、IP-Adapter、动画、视频、放大、面部修复都有。它们以文件夹形式装在 `custom_nodes/` 里。

最流行的安装器是 **ComfyUI-Manager**。它会在 UI 里加一个 "Manager" 按钮,从那里搜索和安装节点包。网上找到的工作流 JSON 大多依赖特定的自定义节点,ComfyUI-Manager 会检测缺什么并提示安装。

第一周玩 ComfyUI 时,先无视自定义节点。把核心图玩熟再说。

## 新手常见错误

- **不小心把 CLIP 接到 MODEL 上。**某些主题下两者颜色相近。看 socket 旁边的标签,会写 `MODEL` 或 `CLIP`。
- **denoise 留在 1.0 以下做纯文生图。**这时 KSampler 期待一个真实输入 latent,不是空白的,你会得到一半噪声的图。
- **batch_size 设太高。**批次里每张图都占显存。SDXL 上 4 张 1024×1024 一批要 ~16 GB。
- **拿 SD 1.5 提示词风格喂 SDXL。**SDXL 吃自然语言提示词,SD 1.5 那种 danbooru 标签拼接对它效果差。

## 下一步

你已经懂了七个核心节点和它们之间的数据流。下一步是亲手搭一个 — 从空白画布开始,拖入每个节点、连线、生成第一张图。这是下一篇教程的内容。
