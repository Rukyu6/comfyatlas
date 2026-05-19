---
title: "ComfyUI 里的 ControlNet 基础:用姿势、深度、边缘控制构图"
description: "ControlNet 怎么把 Stable Diffusion 引向特定姿势、深度布局或线稿。涵盖预处理器、Apply ControlNet 节点、模型选择,以及怎么和 LoRA 一起用。"
pubDate: 2026-05-20
lang: zh
category: workflow-extensions
heroImage: ../_assets/cover-controlnet.png
workflow:
  file: controlnet-openpose.json
  title: ControlNet OpenPose 工作流
  note: 需要 comfyui_controlnet_aux 自定义节点包 + OpenPose ControlNet 模型。把姿势参考图丢进 Load Image。
tags: ["controlnet", "构图", "工作流", "stable-diffusion", "教程"]
---

纯文生图给你"画什么"的控制(主体、风格、氛围),但几乎没有"画在哪里"的控制。人物站在某个位置、建筑朝某个方向、镜头按模型自己想的那样取景。

ControlNet 解决这个问题。你给它一个参考 — 姿势骨架、深度图、Canny 边缘图 — 模型就被引向那个结构,同时还能听你的提示词决定内容和风格。

本文假设你已经能跑通文生图工作流。还不行的话先看[第一个工作流](/zh/blog/your-first-comfyui-workflow/)。懂 LoRA([LoRA 入门](/zh/blog/lora-basics-comfyui/))有帮助但不是必须。

## ControlNet 到底是什么

ControlNet 是和基础扩散模型一起训练出来的另一个神经网络。推理时它接收一张"控制图"(通常是某种结构图)然后向扩散过程注入引导,让输出符合那个结构。

ControlNet 不是单一模型,而是一族,每个针对一种特定控制类型:

| 类型 | 控制什么 | 典型用法 |
|------|----------|----------|
| OpenPose | 人体姿势(骨架) | 精确摆人物姿势 |
| Depth | 深度图(远近) | 保持 3D 布局 |
| Canny | 边缘线 | 沿着已有线稿或照片轮廓 |
| Lineart | 线稿 | 给草图上色、漫画着色 |
| Scribble | 粗略涂鸦 | 大致勾画布局 |
| MLSD | 直线 | 建筑、室内 |
| Tile | 平铺细节注入 | 保持结构的放大 |
| SoftEdge | 软轮廓(HED) | 类 Canny 但更宽松 |

按你想控制什么挑类型。摆人物姿势?OpenPose。复刻参考照片的布局?Depth 或 Canny。

## ControlNet 工作流的样子

在基础文生图图上加三样东西:

1. **控制图** — 定义结构的输入
2. **预处理器节点** — 把你的原始图(照片、草图)转成 ControlNet 期待的格式(姿势骨架、深度图、边缘图)
3. **Apply ControlNet 节点** — 把预处理后的图加上 ControlNet 模型注入到 conditioning 里影响采样

数据流:

```
Load Image ─→ 预处理器 ─→ 控制图
                              │
Load ControlNet Model ────────┤
                              ▼
正向 CONDITIONING ─→ Apply ControlNet ─→ KSampler
```

KSampler 还是收 MODEL、正向 CONDITIONING、负向 CONDITIONING、latent 跟之前一样 — 只不过正向 CONDITIONING 现在被结构控制增强了。

## 模型文件怎么放

ControlNet 模型放:

```
ComfyUI/models/controlnet/
```

每种控制类型一个文件。命名风格不统一,会看到:

```
control_v11p_sd15_openpose.pth
control_v11p_sd15_canny.pth
control_v11p_sd15_depth.pth
diffusers_xl_canny_full.safetensors
diffusers_xl_depth_full.safetensors
```

`sd15` 是 SD 1.5 训的,`xl` 是 SDXL 训的。**不能换着用。**SD 1.5 的 ControlNet 套到 SDXL checkpoint 上完全不工作。

下载来源:

- SD 1.5: Hugging Face 上的 lllyasviel/ControlNet-v1-1 — 最早的,种类最全
- SDXL: Hugging Face 上的 diffusers/controlnet-canny-sdxl-1.0 之类的 repo
- Civitai 也有社区重训版本

还需要预处理器模型。最常用的安装方式是 **ComfyUI-Manager** — 它有一个 ControlNet 辅助预处理器节点包,自动处理预处理器模型。没有这个包就要手动下每个预处理器的权重。

## 最少需要的节点

在 ComfyUI 里搜并加上:

- `Load Image` — 加载参考图
- 一个预处理器节点(`OpenPose Pose`、`Canny Edge`、`Zoe Depth Map` 等)— 来自 ComfyUI-Manager 的辅助预处理器
- `Load ControlNet Model` — 从 `models/controlnet/` 选一个 `.pth` 或 `.safetensors`
- `Apply ControlNet`(或 `Apply ControlNet (Advanced)`)

## OpenPose 接线示例

你有一张某人摆特定姿势的照片,想让 AI 生成相同姿势的奇幻角色。

1. **Load Image** — 把参考照片拖到画布上,或用文件选择器
2. **预处理器** — 加 `OpenPose Pose`。把 Load Image 的 IMAGE → 预处理器 image 输入。预处理器输出的是姿势骨架(黑底彩色火柴人)
3. **Load ControlNet Model** — 选匹配你 base 的 OpenPose 模型(SD 1.5 → openpose-sd15,SDXL → openpose-sdxl)
4. **Apply ControlNet** — 三个输入:
   - `positive` ← 来自文本编码节点的正向 CONDITIONING
   - `control_net` ← 来自 Load ControlNet Model
   - `image` ← 预处理器输出
5. Apply ControlNet 输出新的正向 CONDITIONING。接到 KSampler 的 `positive` 输入

负向 CONDITIONING 绕过 ControlNet — 直接从文本编码连到 KSampler。

## 强度调节

Apply ControlNet 有一个 `strength` 控件(0.0–2.0),作用:

- **0.0** — ControlNet 等于关闭
- **0.5** — 松散遵循,适合"暗示"姿势
- **1.0** — 默认,严格遵循结构
- **1.5+** — 跟提示词冲突时,有时候会完全压过提示词

OpenPose 用 1.0 就够。Canny 套精细线稿时,0.7 通常更好 — 满强度有时候会太死板地跟线,图发僵。

Advanced 节点还暴露 `start_percent` 和 `end_percent` — 控制在扩散时间步的哪个区间生效。默认 0–1(全程)。把 `end_percent` 设 0.5 表示 ControlNet 只引导前半段,后半段模型自由发挥。这能在保留结构的同时,让细节更松。

## 选哪种控制类型

简易决策树:

- 参考是人,要**相同身体姿势**?→ OpenPose
- 参考是 3D 场景或照片,要**相同深度布局**?→ Depth(Zoe 或 MiDaS)
- 参考是草图/线稿?→ Lineart 或 Scribble
- 参考是完成图,要**像素级重画但换风格**?→ Canny,强度 0.7
- 参考是建筑/室内,有**很多直线**?→ MLSD
- 想保留原图配色和大轮廓?→ Tile(配低 denoise 用)

混用两个 ControlNet 很常见。OpenPose + Depth 串起来,姿势和 3D 布局都有。在第一个之后再加一个 `Apply ControlNet`,把上一步的 CONDITIONING 喂进去。

## ControlNet + LoRA 一起用

ControlNet 作用在 conditioning 上,LoRA 作用在 model + clip 上,不打架。常见叠法:

```
Load Checkpoint ─→ Load LoRA ─→ KSampler.model
                  └─→ Load LoRA.CLIP ─→ Text Encode(正向) ─→ Apply ControlNet ─→ KSampler.positive
```

角色 LoRA + OpenPose 让特定角色摆特定姿势。风格 LoRA + Depth 用特定画风渲染 3D 场景。

强度预算还是要管:ControlNet 1.0 + 两个 LoRA 各 0.7 大约就是上限了。三个全开几乎一定崩。

## 常见失败

### 输出无视控制图

- 基础模型不对(SD 1.5 ControlNet 套 SDXL 或反过来)
- 强度是 0
- Apply ControlNet 接错了 — 它的输出必须接到 KSampler 的 positive,不能悬空

### 输出死板地照抄控制图

- 强度太高,降到 0.7
- 或者把 `end_percent` 设到 0.5,中段以后让控制淡出

### 菜单里没有预处理器节点

- 没装 ComfyUI-Manager,或者没通过 Manager 装辅助预处理器包。打开 Manager → Install Custom Nodes → 搜 "controlnet aux" → 安装
- 装完重启 ComfyUI

### 预处理器输出黑图

- 参考图格式不对,转成标准 RGB
- OpenPose:输入图里检测不到人,骨架就空着

### 加 ControlNet 后爆显存

- ControlNet 多吃 1–4 GB 显存。SDXL + ControlNet 在 8 GB 显卡上很紧
- 先把分辨率降到 768,能跑了再爬
- 加 `--lowvram` 启动参数

## 什么时候不用 ControlNet

ControlNet 增加复杂度,这些情况跳过:

- 你只想**靠提示词**生成,没有结构参考。ControlNet 是杀鸡用牛刀
- 你从描述出发,不是参考图出发。ControlNet 需要"某样东西"来控制
- 你只想要模糊的构图引导。提示词工程("low angle shot"、"medium close-up")能搞定 70%,不需要这套搭建

ControlNet 适合提示词语言传达不了你意思的场景。"人盘腿坐双手举过头顶"打字打半天,姿势参考图两秒。

## 小结

- ControlNet 控制结构(姿势、深度、边缘),提示词控制内容(主体、风格)
- 按你想锁定什么选控制类型
- 需要:预处理器 + 匹配 base 的 ControlNet 模型文件 + Apply ControlNet 节点
- 强度 1.0 默认,精细参考用 0.7,`end_percent: 0.5` 让控制后段淡出
- 和 LoRA 叠加干净,但总强度预算要守住

## 下一步

ControlNet 是三大工作流扩展之一,另外两个:

- **Hires Fix** — 低分辨率出图,高分辨率精修。不烧显存出锐利细节
- **图生图** — 拿真实图当起始 latent。风格迁移、照片编辑、草图到成品

各有专题教程。
