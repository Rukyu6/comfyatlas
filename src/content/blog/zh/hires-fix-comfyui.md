---
title: "ComfyUI 里的 Hires Fix:低分辨率出图 + 高分辨率精修"
description: "怎么先在低分辨率生成,然后放大并精修到高分辨率最终图,还不烧显存。ComfyUI 里替代 A1111 那个一键 Hires Fix 的双阶段工作流。"
pubDate: 2026-05-21
lang: zh
category: workflow-extensions
heroImage: ../_assets/cover-hires-fix.png
workflow:
  file: hires-fix.json
  title: 双阶段 Hires Fix 工作流
  note: 第一遍 512×512,Latent Upscale 1.5x,第二遍高分辨率 denoise 0.5。同种子锁构图。
tags: ["hires-fix", "放大", "工作流", "stable-diffusion", "教程"]
---

用过 Automatic1111 的话肯定见过 Hires fix 那个勾选框 — 在 512 或 1024 生成,然后自动 2 倍放大跑第二遍。ComfyUI 没这个勾选框,但同样的能力拆成几个节点。自己接一下花一分钟,而且每一阶段你都能控制。

本文假设你已经能跑通文生图工作流([第一个工作流](/zh/blog/your-first-comfyui-workflow/))。

## Hires Fix 为什么存在

扩散模型有一个训练时的"原生"分辨率 — SD 1.5 是 512×512,SDXL 是 1024×1024。生成尺寸远大于原生就会出现拼接伪影(同一张图里同一张脸出现两次)、小显存卡爆显存,有时候还会构图错乱。

但你又想要更锐利的细节、更细的纹理、更大的文件。窍门是两遍:

1. 用原生分辨率生成,模型出干净的构图
2. 把结果放大到目标分辨率,跑**第二次更短的去噪**,只够加细节,不改画面

显存占用低(原生分辨率全跑一遍 + 目标分辨率短跑一遍),构图干净,细节上去。

## 需要的东西

基础图上加三样:

- **Latent Upscale** — 在第一个采样器和第二个之间放大 latent
- **第二个 KSampler** — 在更高分辨率上跑精修
- **末尾的 VAE Decode**(已有)— 把最终 latent 转像素

多数人跳过"Upscale Image" + "VAE Encode",因为在 latent 空间放大更快,也省了一次像素 ↔ latent 的来回。

## 双阶段工作流接线

从能跑通的文生图图开始。原本第一个 KSampler 输出的 LATENT 直接进 VAE Decode,现在改成:

```
KSampler(第一遍)─→ Latent Upscale ─→ KSampler(第二遍)─→ VAE Decode ─→ Save Image
```

具体步骤:

1. **加 Latent Upscale。**搜 `Upscale Latent By`(或 `Upscale Latent`)。把第一个 KSampler 的 LATENT 接它的输入。设:
   - `upscale_method` — `nearest-exact` 锐利,`bilinear` 略柔。先试 `nearest-exact`
   - `scale_by` — 1.5 到 2.0。一遍超过 2 倍画面会丢一致性

2. **加第二个 KSampler。**和第一个同款节点。连:
   - `model` ← 来自 Load Checkpoint(或 Load LoRA 链)
   - `positive` / `negative` ← 和第一个 KSampler 同样的 conditioning
   - `latent_image` ← Latent Upscale 输出

3. **VAE Decode** 现在接到第二个 KSampler 的输出(不是第一个)

4. **Save Image** 跟之前一样

## 第二个采样器的参数

这里跟第一遍不同。

| 控件 | 第一遍 | 第二遍(精修) |
|------|--------|----------------|
| seed | 随机或固定 | **和第一遍同种子**,保持一致 |
| steps | 20 | **8–15**(短点通常更好) |
| cfg | 7 | 5–7 |
| sampler_name | euler / dpmpp_2m | 跟第一遍一致 |
| scheduler | normal / karras | 同上 |
| denoise | 1.0 | **0.4–0.6** ← 关键 |

最关键的是 `denoise`。1.0 第二遍会把 latent 全部重新加噪,生成全新的图,把你刚做好的构图毁掉。0.4–0.6 保留构图但注入细节。

- **0.4** — 保守。同图,稍锐利
- **0.5** — 平衡默认
- **0.6** — 更有创造性的精修。脸和纹理细节更多,但可能微微变化
- **0.7+** — 危险。图开始偏离第一遍

第一次试:同种子,10 步,denoise 0.5。

## 同种子为什么重要

第二个采样器的 seed 和第一个设成同样的值,会锁定噪声模式。配合低 denoise,得到同样的构图但更多细节。不同种子会产生不同细节,有时候会导致构图漂移。

想让第二遍在第一遍基础上确定性出图,两个 seed 都设成同一个固定值(或者 UI 支持的话把第一遍的 seed 接到第二遍)。

## 用模型放大器的双阶段(更锐利但更慢)

上面那种 latent 空间放大快、干净。想要更锐利的输出,换成真正的放大模型(RealESRGAN、4x-UltraSharp 等):

```
KSampler #1 ─→ VAE Decode ─→ Upscale Image (Using Model) ─→ VAE Encode ─→ KSampler #2 ─→ VAE Decode ─→ Save Image
```

需要加:
- `Load Upscale Model` — 从 `models/upscale_models/` 加载 `.pth` 文件
- `Upscale Image (Using Model)` — 跑放大模型
- `VAE Encode` — 转回 latent 给第二个 KSampler

更慢(多一次 VAE 来回 + 放大模型本身)但出图边缘更锐、纹理更细。

推荐放大模型:

- **4x-UltraSharp** — 通用,边缘锐利
- **4x_NMKD-Siax** — 柔和、自然
- **4x-AnimeSharp** — 动漫/插画专用

下载来源 openmodeldb.info,放进 `ComfyUI/models/upscale_models/`。

## 显存计算

第二遍跑在放大后的分辨率,小显存卡可能爆。算一下:

- SD 1.5 在 512×512 → 2 倍 → 1024×1024 — 大多数卡能跑
- SDXL 在 1024×1024 → 2 倍 → 2048×2048 — 需要 ~16 GB
- SDXL 在 1024×1024 → 1.5 倍 → 1536×1536 — 12 GB 能跑

爆显存先降 `scale_by`。1.5 倍 + 高质量放大器经常比裸 2 倍 latent 效果好。

## 常见失败

### 第二遍出了完全不同的图

- `denoise` 太高,降到 0.5 或更低
- 种子和第一遍不同,改成一致

### 第二遍跟第一遍一模一样,看不出改善

- `denoise` 太低(低于 0.3),采样器几乎不工作
- `steps` 太低(低于 5),同样效果

### 第二遍脸/细节崩了

- SDXL 放到 2048+ 常出。模型没在那么高的分辨率训过。降到 1.5 倍
- 试模型放大器替代 latent 放大

### 出现重复主体/拼接

- 分辨率超原生太多。SDXL 超过 2048 就开始拼接。用 ControlNet Tile 或 1.5 倍

### 第二遍 OOM

- 第二遍要的显存等于第一遍在放大后分辨率上的开销。加 `--lowvram` 或降倍数

### 工作流跑了,但 Save Image 存的是小图

- Save Image 接到了第一遍的 VAE Decode,改接到第二遍的输出

## Hires Fix + LoRA + ControlNet

叠加没问题。两遍如果接对了,LoRA 和 ControlNet 都生效:

- LoRA 修改 MODEL/CLIP — 两个 KSampler 用同一个修改后的 MODEL,LoRA 自动延续
- ControlNet 修改 CONDITIONING — 同一个 `Apply ControlNet` 输出接到两个采样器的 positive

如果第二遍想忽略 ControlNet(只想第一遍有结构),那把原始文本编码输出接到第二遍的 positive 就行。

## 小结

- Hires Fix = 第一遍原生分辨率 + 第二遍高分辨率低 denoise
- Latent Upscale 快,Upscale Image (Using Model) 锐利
- 第二遍参数:同种子、8–15 步、denoise 0.4–0.6
- 一遍内放大保持在原生 1.5–2 倍
- LoRA 自动延续,ControlNet 你选要不要延续

## 下一步

第三大工作流扩展是**图生图** — 用真实图当起始 latent,而不是空白的。风格迁移、照片编辑、草图到成品。设置不同,但用的还是你已经熟悉的 KSampler。
