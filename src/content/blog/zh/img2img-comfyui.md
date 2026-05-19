---
title: "ComfyUI 里的图生图(img2img):风格迁移、照片编辑、草图变成品"
description: "用真实图片当起始 latent 而不是纯噪声。ComfyUI 里完整的 img2img 工作流,denoise 调节、常见用法、和 LoRA / ControlNet 怎么搭。"
pubDate: 2026-05-21
lang: zh
category: workflow-extensions
tags: ["img2img", "图生图", "工作流", "stable-diffusion", "教程"]
---

文生图从随机噪声开始。图生图(img2img)从你的图开始。模型把你输入的图当成"已经部分加噪"的 latent,然后跑同样的去噪流程 — 但去噪目标受你的输入影响。输出保留输入的结构和大致颜色,风格和细节按提示词来。

这是大多数用户想要的三大工作流扩展之一,另外两个是 [LoRA](/zh/blog/lora-basics-comfyui/) 和 [ControlNet](/zh/blog/controlnet-basics-comfyui/)。也是最容易接的 — 就两个新节点。

## img2img 适合干什么

- **风格迁移** — 照片转油画、转动漫、转像素艺术
- **照片编辑** — 改季节、时间、环境
- **草图变成品** — 画个粗糙构图,让模型渲染
- **迭代已有生成** — 拿一张你差不多满意的图,改改提示词重出

它**不**适合什么:对特定区域的像素级精修。那是局部重绘(inpainting)的事,另一种工作流。

## 跟文生图的区别

文生图工作流:

```
Empty Latent Image  →  KSampler  →  VAE Decode  →  Save Image
   (空白画布)        (满去噪)
```

图生图:

```
Load Image  →  VAE Encode  →  KSampler  →  VAE Decode  →  Save Image
                              (部分去噪)
```

两处变化:

1. 空白 latent 换成你编码后的图(Load Image + VAE Encode)
2. KSampler 的 `denoise` 设为低于 1.0 — 通常 0.4 到 0.7 — 保留你输入的一部分

整个套路就这。其它(模型、LoRA、提示词、采样器)用法不变。

## 最少需要的节点

搜并加:

- `Load Image` — 选图片文件或从电脑上传
- `VAE Encode` — 把像素图转 latent

然后把现有 KSampler 的 `latent_image` 输入改成接 VAE Encode,而不是 Empty Latent Image。

VAE Encode 的 `vae` 输入接 Load Checkpoint 的 VAE 输出。

## 接线步骤

从能跑通的文生图图开始:

1. **加 Load Image。**节点拖到画布上,点 `choose file to upload` 选你的输入
2. **加 VAE Encode。**
   - `pixels` ← Load Image 的 IMAGE 输出
   - `vae` ← Load Checkpoint 的 VAE(或单独 Load VAE 时来自 Load VAE)
3. **断开 Empty Latent Image** 到 KSampler 的 `latent_image` 那根线
4. **VAE Encode 的 LATENT** 接到 KSampler 的 `latent_image`
5. (可选)删掉 Empty Latent Image — 不再需要

也可以留着 Empty Latent Image,在文生图和 img2img 间切换时改接线就行。ComfyUI 不在乎悬空节点。

## denoise 控件

img2img 你要学的就这一个旋钮。

KSampler 的 `denoise` 控制你的图有多少被新内容替换。原理:denoise = X 时,采样器把你的图加噪到 X*总步数 对应的水平,然后跑 (X*总步数) 步去噪。

实用范围:

| denoise | 表现 |
|---------|------|
| 0.1 | 几乎不变,输出就是你的图加一点点风格点缀 |
| 0.3 | 轻度风格迁移。照片还像照片,提示词影响微妙 |
| 0.5 | **多数场景的甜点**。可见的风格变化,结构保留 |
| 0.7 | 重度重新诠释。同主体大致同构图,质感很不一样 |
| 0.9 | 非常松散,输出几乎不像输入 |
| 1.0 | 纯文生图,你的输入被忽略 |

风格迁移(照片→油画):0.5 起步,风格不够强爬到 0.7。

"调一下这次生成":0.3–0.4 — 保留图,只挪一下提示词。

草图到成品:0.7–0.8 — 草图给构图,模型补细节精修。

## 分辨率行为

输入图的尺寸就是输出的尺寸。1280×768 的照片喂进 VAE Encode,输出就是 1280×768 — 没有单独的 width/height 控件。

两个后果:

- 图的尺寸要能被 8 整除(SDXL 推荐 64)。多数照片本来就是;不是的话编码会向下取整
- 4K 大图直接喂会爆显存。先 resize 到模型原生范围(SD 1.5 ≈ 512,SDXL ≈ 1024)再处理

自动 resize 的话,在 Load Image 和 VAE Encode 之间加 `Upscale Image` 或 `Image Resize` 节点。SDXL 把长边设到 1024。

## 草图到成品示例

你在画图软件里随手画了个粗草图 — 火柴人风景、涂鸦肖像。存成 PNG 拖进 ComfyUI。

参数:

- `denoise` 0.75 — 草图大部分细节被替换,但构图保留
- 提示词:描述最终图的样子,包括风格和氛围
- 负向:`sketch, line drawing, rough, low quality`
- Steps:20–25
- CFG:7

输出保持草图的空间布局,但渲染成完整画作 / 照片 / 插画。

## 风格迁移示例

白天的照片,你想要月夜版。

参数:

- `denoise` 0.45 — 保留可识别的主体和布局
- 提示词:完整目标描述("moonlit night, cool blue tones, stars in sky")
- Steps:20
- CFG:7

denoise 越高 = 风格变化越戏剧但构图漂移越大。多迭代。

## img2img + LoRA

LoRA 用法一样 — 修改后的 MODEL 喂 KSampler,流程不变。一个 "watercolor painting" LoRA,强度 0.8,denoise 0.5,任何输入照片都能干净水彩化。

## img2img + ControlNet

常见组合:img2img 提供起始内容,ControlNet 锁结构。

例子:你有一张 3D 渲染图,想做成插画风格但**严格保留**边缘。

- img2img:3D 渲染图,denoise 0.7(重度重诠)
- ControlNet Canny:同一张 3D 渲染图的边缘,强度 0.8

img2img 保留颜色和粗略形状,ControlNet 锁住边缘。叠起来既风格化又不丢几何。

## 常见失败

### 输出和输入一模一样

- denoise 太低(0.1–0.2)
- 或者接错了 — 检查 VAE Encode 输出有没有到 KSampler 的 `latent_image`

### 输出完全无视输入

- denoise = 1.0,降到 0.5–0.7
- 或 VAE Encode 没接上,检查那根线

### 输出有颗粒/噪点

- VAE 不匹配。确保 VAE Encode 和 VAE Decode 用的是同一个 VAE(同一个 checkpoint 出来的)
- 有些 checkpoint 自带的 VAE 是坏的,单独 `Load VAE` 加载已知好的 VAE,两边都用它

### 输出无视提示词

- denoise 太低,模型没空间表达提示词
- 试 0.6 替代 0.4

### OOM

- 输入分辨率太高,VAE Encode 前先 resize
- 4K 照片在 SDXL 上 0.7 denoise 多数卡都爆

### 颜色莫名漂移

- VAE 来回有精度损失。0.4 denoise 时可接受;0.1 denoise 时很明显(本来也不该用这么低)
- 在意像素级颜色保留就用模型放大器替代 latent 空间处理

## 什么时候用 img2img,什么时候用文生图加参考

目标纯粹是风格化("把这场景画成 X 风格"):img2img 直接快速。想让模型基于你的图**生成新场景**:文生图加 ControlNet 参考(Canny 或 Depth)更自由。

经验法则:

- "把**这张**图变成另一种样子" → img2img
- "**新生成**一张图,有这张图的某些特征" → 文生图 + ControlNet

## 小结

- img2img = 真实图替代空白 latent,部分去噪替代满去噪
- 加两个节点:Load Image + VAE Encode
- denoise 0.4–0.7 覆盖多数场景
- 保留输入尺寸,大图先 resize
- 和 LoRA、ControlNet 叠加 — 风格迁移锁结构是常见组合

## 下一步

到现在你已经看过四大工作流积木:文生图、LoRA、ControlNet、Hires Fix、img2img。网上找的多数工作流就是这些的组合。值得继续探索的方向:

- **局部重绘(inpainting)** — 只重新生成某个区域(脸、手、背景),其他不动
- **AnimateDiff** — 静态工作流变视频
- **IP-Adapter** — 直接把参考图喂进 conditioning,替代 LoRA
- **采样器和调度器** — `dpmpp_2m_sde + karras` 到底是什么、什么时候用
