---
title: "ComfyUI 里的 LoRA 入门:风格和角色模型怎么用"
description: "什么是 LoRA、文件放哪里、怎么把它接进文生图工作流。包含强度调节、多个 LoRA 叠加、还有最容易让新手踩坑的触发词习惯。"
pubDate: 2026-05-20
lang: zh
category: workflow-extensions
tags: ["lora", "微调", "工作流", "stable-diffusion", "教程"]
---

LoRA(Low-Rank Adaptation,低秩适配)是一个小文件,用来把基础扩散模型往特定的风格、角色或概念方向"推"一下,不需要重新训练整个模型。一个普通的 LoRA 是 50–200 MB,一个完整的 SDXL checkpoint 是 7 GB。这个比例就是 LoRA 满天飞的原因 — 训练成本低、分享方便、还能叠加。

本文假设你已经能跑通一个文生图工作流。还不行的话先看[第一个工作流教程](/zh/blog/your-first-comfyui-workflow/)。能跑通之后,加一个 LoRA 就是多一个节点的事。

## LoRA 到底干什么

扩散模型是一摞权重矩阵。训练 LoRA 会为每一层产生一对小很多的矩阵。推理时这两个小矩阵相乘后加到原权重上,模型表现得像稍微变了一点的另一个模型 — 一个被往 LoRA 训练目标方向拉过的模型。

实际意义:

- **不替换基础模型。**LoRA 是叠加上去的。SD 1.5 上训练的角色 LoRA 需要一个 SD 1.5 的 checkpoint。
- **基础模型很重要。**在 `sd-v1-5` 上训练的 LoRA 套到 `realistic-vision-v6` 上,虽然都是 SD 1.5,效果会怪。基础越接近,效果越好。
- **能叠加。**两个 LoRA 各 0.7 强度很常见。四个全开就开始打架了。

## LoRA 文件放哪

放进:

```
ComfyUI/models/loras/
```

子文件夹随便分。多数人按来源或类型分:

```
ComfyUI/models/loras/
  character/
    aragorn-sdxl.safetensors
    sailor-moon-1.5.safetensors
  style/
    pixel-art-xl.safetensors
    studio-ghibli.safetensors
  concept/
    wide-angle-lens.safetensors
```

加完文件,点 ComfyUI 右上角刷新按钮 — 下拉菜单会重新读目录,不用重启。

## 去哪下载 LoRA

主要两个地方:

- **Civitai** — civitai.com。最大的库。质量参差不齐。按基础模型和下载量筛选。
- **Hugging Face** — huggingface.co。库小但来源更干净。搜 "lora sdxl" 或 "lora sd1.5"。

LoRA 详情页一定会写**基础模型**。SD 1.5、SDXL、FLUX、Pony、Illustrious 这几个互不通用。下载的 LoRA 必须匹配你 `Load Checkpoint` 里加载的 checkpoint。

好的详情页还会包含:

- 几张示例图,以及生成它们用的提示词
- **触发词(trigger word)**— 提示词里必须出现的标记,LoRA 才会被激活
- 推荐强度范围(通常 0.6–1.0)

如果详情页没有触发词、没有示例提示词,这是个差页面,跳过。

## Load LoRA 节点

在节点菜单里搜 `Load LoRA`。这个节点有:

**输入(左侧):**
- `model`(紫色)— 你想修改的 MODEL
- `clip`(黄色)— 你想修改的 CLIP

**输出(右侧):**
- `MODEL` — 修改过的 MODEL
- `CLIP` — 修改过的 CLIP

**控件:**
- `lora_name` — `models/loras/` 下文件的下拉菜单
- `strength_model` — LoRA 对扩散模型本身的影响强度(典型值 0.6–1.0)
- `strength_clip` — LoRA 对文本编码器的影响强度(典型值与 strength_model 相同)

这个节点夹在 `Load Checkpoint` 和后续节点之间,拦截 MODEL 和 CLIP。

## 接线

拿你能跑通的文生图图。看 `Load Checkpoint` 出去的几根线:

- MODEL → KSampler
- CLIP → 两个 `CLIP Text Encode`(正向 + 负向)
- VAE → VAE Decode

VAE 那根别动 — LoRA 不影响 VAE。但要拦截 MODEL 和 CLIP 两根:

1. 加一个 `Load LoRA` 节点夹在 `Load Checkpoint` 和后续之间
2. 断开 `Load Checkpoint` 到 KSampler 的 MODEL 线
3. 连:`Load Checkpoint`.MODEL → `Load LoRA`.model → `Load LoRA`.MODEL → KSampler.model
4. 断开 CLIP 那两根线
5. 连:`Load Checkpoint`.CLIP → `Load LoRA`.clip → `Load LoRA`.CLIP → 两个文本编码器

完事。下拉里选一个 LoRA,强度都设 1.0 起步。

## 触发词的习惯

新手最容易栽在这。很多 LoRA 必须在正向提示词里出现一个特定的标记才会被激活。这个标记是训练时定的,提示词里没有它,LoRA 的效果会很弱甚至看不到。

举例(虚构,但代表性强):

```
LoRA: aragorn-sdxl.safetensors
触发词: aragorn-strider
用法: "portrait of aragorn-strider in a forest, cinematic lighting"
```

```
LoRA: pixel-art-xl.safetensors
触发词: pixel art
用法: "pixel art of a fox sitting on a moss-covered rock"
```

每次都查 LoRA 详情页的触发词。如果 LoRA 强度 1.0 接进去图却一点没变 — 多半是没用触发词。

也有些 LoRA 是"常驻"的,不需要触发词。详情页会说明。

## 强度调节

三种数值组合,三种不同表现:

| strength_model | strength_clip | 行为 |
|----------------|---------------|------|
| 1.0            | 1.0           | 完整效果,默认起点 |
| 0.6            | 0.6           | 微妙融入,适合往基础风格里渗一点 |
| 1.2            | 1.0           | 视觉效果强、提示词响应正常。风险:容易把图烤糊 |
| 1.0            | 0.0           | 视觉风格应用了,但提示词理解保持干净。处理麻烦组合时有用 |
| 0.0            | 0.0           | LoRA 关闭(等于没接节点) |

第一次跑,1.0 / 1.0。结果太强(脸变形、颜色爆炸)就降到 0.7。太弱试 1.1 — 但超过 1.2 通常会破坏生成。

`strength_clip` 比大多数人意识到的更重要。如果一个角色 LoRA 把提示词理解污染了(模型"忘了"蓝色是什么意思),把 `strength_clip` 降到 0.5 左右,`strength_model` 留 1.0。

## 多个 LoRA 叠加

两个 LoRA 同时用,把 `Load LoRA` 节点串起来:

```
Load Checkpoint → Load LoRA(风格) → Load LoRA(角色) → KSampler
```

每个节点修改它收到的 MODEL 和 CLIP 然后传下去。顺序的影响小于总强度的影响。

叠加经验法则:**总强度保持在 1.0–1.5 之间**。两个 LoRA 各 0.7 没问题。三个全 1.0 几乎一定出垃圾图。模型的"余量"有限,多个微调互相抢就开始打架。

风格 LoRA + 角色 LoRA 叠加:
- 提示词里写角色 LoRA 的触发词
- 风格 LoRA 有触发词的话也写上
- 两个都从 0.7 起步,慢慢调

## 常见失败

### 加不加 LoRA 图一样

- 提示词里没写触发词,最常见
- 基础模型不对。SD 1.5 LoRA 套 SDXL = 没效果或噪声
- `strength_model` 是 0.0,检查是否被滑回去了

### 图过饱和、扭曲、烤糊

- 强度太高,降到 0.7 或 0.6
- 叠太多 LoRA。除一个全关掉重测
- 有些 LoRA 训练过头了,试 0.5 看看质量是否反弹

### 你没要求画脸的地方脸都崩了

- 角色 LoRA 在 1.0 强度下污染了所有人脸
- 把 `strength_clip` 降到 0.4–0.5,`strength_model` 留 1.0

### "LoRA not found" / 下拉是空的

- 文件扩展名不对。ComfyUI 接受 `.safetensors` 和 `.ckpt`。其他(`.pt`、`.bin`)要改名或转换
- 文件放错文件夹,必须在 `models/loras/`,不是 `models/checkpoints/`
- 忘了点刷新,UI 右上角

### 颜色/风格对了,但角色不对

- 这个 LoRA 是纯风格的,不带角色。要么再加一个角色 LoRA,要么在提示词里描述角色

## LoRA、checkpoint、embedding 区别

下载内容三种类型的速查表:

| 类型 | 体积 | 放哪 | 干啥 |
|------|------|------|------|
| Checkpoint | 2–24 GB | `models/checkpoints/` | 整个模型。替换扩散大脑 |
| LoRA | 50–500 MB | `models/loras/` | 给模型打补丁,风格/角色/概念 |
| Embedding | 5–500 KB | `models/embeddings/` | 仅文本侧,模型新认识的一个"词" |

LoRA 是中间路线 — 小到能随便下,表达力又足以真改变生成。网上看到的工作流大多用 1-2 个 LoRA 加基础 checkpoint。

## 下一步

你现在能把任何角色或风格 LoRA 套到基础文生图工作流上了。两个自然的下一站:

- **ControlNet** — 用深度图、边缘图、骨架图控制构图。和 LoRA 叠加干净
- **Hires Fix** — 低分辨率出图再放大精修,不烧显存出锐利细节

各有专题教程。
