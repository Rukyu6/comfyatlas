---
title: "ComfyUI 里的局部重绘(Inpainting):选择性重生成手、脸、背景"
description: "给图像的某个区域画蒙版,让模型只重新生成那个区域,其他像素不动。涵盖 inpainting 工作流、蒙版模糊、denoise 调整、专用 inpainting 模型。"
pubDate: 2026-05-22
lang: zh
category: workflow-extensions
heroImage: ../_assets/cover-inpainting.png
tags: ["inpainting", "蒙版", "工作流", "stable-diffusion", "教程"]
---

你生成了一张挺好的图,但手画得像意大利面。或者脸不错,背景却全是怪伪影。重新生成整张图风险是把好的部分一起毁掉。**局部重绘(Inpainting)** 解决这个 — 给坏的区域画蒙版,模型只重新生成那个区域,其他像素一字不变。

这是继 [LoRA](/zh/blog/lora-basics-comfyui/)、[ControlNet](/zh/blog/controlnet-basics-comfyui/) 和 [图生图](/zh/blog/img2img-comfyui/) 之后第四个主要工作流扩展。也是最难调优的一种,但基本图很小。

## Inpainting 干什么

拿一张已有的图,在你想重做的部分画黑白蒙版,给模型一段提示词描述那里应该画什么,跑采样。模型只改蒙版内的像素,蒙版外的像素**完全保留原样**。

用法:

- **修坏手坏脸**,不用重画整张图
- **去除或替换物体**(把人从风景里去掉、把 logo 从产品图里去掉)
- **改细节**(眼色、发色、衣服颜色)
- **扩展画面**(往蒙版的透明区域往外画 — outpainting)
- **局部迭代**,当 95% 的图都好用,只有一处要改

## 最少需要的节点

基础图上加:

- `Load Image` — 你的输入图
- `Load Image (as Mask)` — 你的蒙版图(或用内置蒙版编辑器)
- `VAE Encode (for Inpainting)` — 把输入和蒙版编码成专用的 inpaint latent
- 第二个 `KSampler`,带蒙版意识

替换文生图图里的空白 latent 和 KSampler。其它(模型、条件、VAE Decode、Save Image)不变。

## 两种画蒙版的方法

### 方法一:ComfyUI 内置蒙版编辑器

右键任何一个加载了图的 `Load Image` 节点 → `Open in MaskEditor`。出来一块画布。用刷子涂你要重新生成的地方。保存。蒙版现在跟那张图绑定。

最快的方式,适合一次性蒙版。边缘不够精细。

### 方法二:外部蒙版文件

在任何画图软件里做一张黑白 PNG。白 = 重新生成,黑 = 保留。单独存,用 `Load Image (as Mask)` 加载。

适合精细蒙版(精确边缘、多个分离区域)。

蒙版颜色规则:
- **白色 / 255**:重新生成这个像素
- **黑色 / 0**:保留原样
- **灰色**:按对应强度混合

## 接线

从能跑通的文生图图开始:

1. **加 Load Image。**选你的输入
2. **画蒙版。**用 MaskEditor(右键 → Open in MaskEditor)快速画,或加载单独的蒙版文件
3. **空白 Latent 替换为 VAE Encode (for Inpainting)。**输入:
   - `pixels` ← Load Image 的 IMAGE
   - `vae` ← Load Checkpoint 的 VAE
   - `mask` ← Load Image 的 MASK(同节点暴露的蒙版通道)
4. **VAE Encode (for Inpainting) 的 LATENT** 接到 KSampler 的 `latent_image`
5. KSampler 设置:
   - `denoise` 1.0(蒙版内满去噪 — 模型从头重建)
   - 其它和文生图一致
6. **VAE Decode** 和 **Save Image** 跟之前一样

基本图就这。当 KSampler 的输入 latent 来自 `VAE Encode (for Inpainting)` 时,蒙版会被自动尊重。

## Inpainting checkpoint 还是普通 checkpoint

模型有两种选择:

| 类型 | 行为 |
|------|------|
| 普通 checkpoint | 能用,但蒙版边缘有时可见。80% 场景够用 |
| **Inpainting checkpoint**(后缀 `-inpainting` 或 `-inpaint`) | 专门带蒙版条件训练过。边缘更干净、融合更好 |

SD 1.5: 下 `realistic-vision-inpainting`、`dreamshaper-inpainting` 这种。是普通 checkpoint 的 inpaint 重训版。放进 `models/checkpoints/`,跟其他模型一样。

SDXL: 专用 inpainting checkpoint 较少 — 多数 SDXL 用普通 checkpoint inpaint 也好。

FLUX: 用 FLUX.1-fill-dev,Black Forest 官方 inpainting 版本。

如果你要大量做 inpainting,下个专用 inpainting checkpoint 值得。一次性修图用现成 checkpoint 也行。

## 蒙版调优

### 蒙版模糊

硬边蒙版会出现可见接缝。修法:编码前模糊蒙版。

在 `Load Image (as Mask)` 和 `VAE Encode (for Inpainting)` 之间加 `MaskBlur`(自定义节点包带的)或 `GaussianBlur`。模糊半径 4-12 像素软化过渡。

圆形蒙版(脸、手):模糊半径 8-15。
直边蒙版(天空区域、墙面):模糊 4-8。

### Denoise(这里角色不一样)

跟图生图不同,蒙版内的 denoise 通常应该停在 **1.0**。蒙版本身已经隔离了改动区域 — 那里要的是完整重新生成。降 denoise 反而会在蒙版内出现原图的鬼影。

例外:做某种**微妙改动**(轻微改色),把 denoise 降到 0.6-0.7。

### 蒙版扩张 / 收缩

有时手画的蒙版略小 — 模型只重新生成了坏手,但腕部边缘还是丑。用 `GrowMask` 扩 4-8 像素。扩出来的余地给模型融合的上下文。

蒙版太大溢出到好区域,`ShrinkMask` 反过来缩。

## 提示词策略

提示词描述**蒙版区域应该是什么**,不是整张图。模型只把蒙版区域当生成目标。

差提示词:`"a portrait of a young woman, smiling, sunlit forest"`(描述整张图,浪费注意力)

好提示词:`"a hand holding an apple, fingers clearly defined, photorealistic"`(只描述要 inpaint 的部分)

负向提示词照常针对失败模式(`deformed, blurry, extra fingers`)。

## Outpainting(扩展画面)

Outpainting 就是 inpainting,蒙版变成画布扩展区。

工作流:
1. 拿你的原图。用 `ImagePadForOutpaint` 在你想要的方向加一圈透明(被蒙版的)边
2. 结果喂给 `VAE Encode (for Inpainting)` — 加的透明边**就是**蒙版
3. 跑 KSampler。模型把新区域填上,和可见原图融合

注意:一遍 outpaint 超过 50% 通常崩。模型丢失上下文。按 25-50% 步进多次跑。

## 常见失败

### 蒙版边缘是硬接缝

- 没加蒙版模糊。加 `MaskBlur` 半径 6-10
- 或换专用 inpainting checkpoint

### 修过的区域跟其他完全不像

- denoise 太高(已经 1.0 — 那是对的,这是特性不是 bug)
- 提示词描述跟周围图不一致。图很暗你提示 "bright daylight",肯定违和
- 用 ControlNet(原图的 Depth 或 Canny)保持结构一致

### 修过的手还是 7 根手指

- 修手是真难。试:
  - 扩大蒙版包含更多腕部/前臂
  - 用修手 LoRA(Civitai 搜 "hand")
  - 多换种子,有时候 5 张才出 1 张好手
  - SDXL 用 Hands-XL LoRA 帮助大

### 输出和原图一模一样(没改)

- 蒙版是空的或全黑。检查蒙版真的有白像素
- 蒙版接错节点。蒙版必须到 `VAE Encode (for Inpainting)` 的 `mask` 输入,不能悬空

### "Mask size doesn't match image size"

- 蒙版尺寸 ≠ 图尺寸。把蒙版 resize 成一样大。ComfyUI 不自动 resize

### Inpaint 时 OOM

- 同尺寸下 inpaint 比文生图多吃显存。降到 1024 或用 `--lowvram`

## Inpainting + ControlNet

常见组合:用 ControlNet OpenPose 的手势参考来 inpaint 一只手。

1. 生成手势参考(一张单独的火柴人或想要的手势真照)
2. 跑 OpenPose 预处理器
3. OpenPose 输出喂给 `Apply ControlNet`,跟 inpainting 提示词一起
4. 蒙版区域被重新生成**且**匹配参考手势

这能大幅提升修手成功率。

## Inpainting + LoRA

LoRA 用法一样。角色 LoRA + 脸部 inpaint = 把特定角色的脸放到现有身体上。"完美双手" LoRA + 手部 inpaint = 修手成功率高很多。

## 小结

- Inpainting = 给区域画蒙版,只重新生成那个区域
- 接线:Load Image + 蒙版 + VAE Encode (for Inpainting) + KSampler 用 denoise 1.0
- 用专用 inpainting checkpoint 边缘更干净
- 永远蒙版模糊 6-10 像素避免硬接缝
- 提示词描述蒙版内,不是整张图
- 修手修脸,搭配 ControlNet 姿势参考

## 下一步

到此你已看过五种主要工作流模式:文生图、LoRA、ControlNet、Hires Fix、img2img、inpainting。下一类要探索的是**用参考图代替 LoRA 来给模型条件**,那就是 IP-Adapter,值得单独一篇。
