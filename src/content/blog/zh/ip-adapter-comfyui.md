---
title: "ComfyUI 里的 IP-Adapter:用参考图代替 LoRA 训练"
description: "IP-Adapter 怎么把参考图直接喂进模型条件,复制风格、主体、人脸 — 完全不用训练。涵盖安装、四种模型变体、权重调整、和 LoRA / ControlNet 怎么叠加。"
pubDate: 2026-05-22
lang: zh
category: workflow-extensions
tags: ["ip-adapter", "参考图", "工作流", "stable-diffusion", "教程"]
---

你想让生成图看起来像某张特定参考图。经典做法是训练 LoRA — 收集数据集、跑训练、等一小时,祈祷它学到了对的特征。IP-Adapter 跳过这一切。把参考图丢进一个节点,模型把它当作视觉条件和你的文本提示词一起用,输出就带上参考图的风格、主体或人脸。不训练、不要数据集、不用等。

本文假设你已经能跑文生图工作流([第一个工作流](/zh/blog/your-first-comfyui-workflow/))并读过 [LoRA 入门](/zh/blog/lora-basics-comfyui/),因为 IP-Adapter 用不同机制解决相似问题。

## IP-Adapter 到底是什么

IP-Adapter(Image Prompt Adapter)是一个附加的小网络,接收一张参考图,过 CLIP 图像编码器,把得到的视觉嵌入注入扩散模型的交叉注意力层。模型于是会"关注"你的参考图,跟关注文本提示词的方式一样。

可以这么理解:文本提示词 = 你想要什么,图像提示词 = 它应该长什么样。

跟 LoRA 的区别:

| 方面 | LoRA | IP-Adapter |
|------|------|------------|
| 设置 | 下载预训练文件 | 预训练 adapter + 参考图 |
| 每次用 | 选文件,设强度 | 选文件,丢参考图,设强度 |
| 捕获什么 | 训练数据里的东西 | 参考图里的东西 |
| 文件大小 | 50-500 MB | 100-300 MB(adapter)一次,参考图任何都能复用 |
| 适合 | 反复出现的角色、招牌风格 | 一次性参考、快速迭代 |

要生成某角色几百张图,LoRA 还是更优。要 10 分钟试 50 张不同参考,IP-Adapter 赢。

## 四个 IP-Adapter 模型变体

不同变体训来干不同活。按目标挑。

| 变体 | 干啥 | 什么时候用 |
|------|------|------------|
| **Base**(`ip-adapter_sd15`) | 通用视觉风格 + 主体 | 默认起点 |
| **Plus**(`ip-adapter-plus_sd15`) | 对参考图保真度更高 | base 觉得太弱时 |
| **FaceID**(`ip-adapter-faceid`) | 人脸身份保留 | 复刻特定人物的脸 |
| **Plus Face**(`ip-adapter-plus-face`) | 人脸结构(身份弱、神似强) | 通用"这种脸" |

SDXL 有对应版:`ip-adapter_sdxl`、`ip-adapter-plus_sdxl` 等。基础模型不要混 — SD 1.5 IP-Adapter 套 SDXL checkpoint 不工作。

## 安装:自定义节点和模型文件

IP-Adapter 以自定义节点形式发布。最常用的包是 cubiq 的 **ComfyUI_IPAdapter_plus**。

### 通过 ComfyUI-Manager 装

1. 打开 ComfyUI-Manager → Install Custom Nodes
2. 搜 "IPAdapter plus" → 装 cubiq 那个
3. 重启 ComfyUI

### 下模型文件

需要三样:

1. **CLIP Vision 编码器** — `models/clip_vision/`
   - `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`(给 SD 1.5 IP-Adapter)
   - `CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors`(给 SDXL IP-Adapter)

2. **IP-Adapter 模型** — `models/ipadapter/`
   - `ip-adapter_sd15.safetensors` 和/或 `ip-adapter-plus_sd15.safetensors`
   - `ip-adapter_sdxl.safetensors` 和/或 `ip-adapter-plus_sdxl.safetensors`

3. **(只有 FaceID 用)** Insightface buffalo_l — 第一次跑时自动装,但需要 `pip install insightface onnxruntime` 才能工作

cubiq 节点包带下载脚本。打开 ComfyUI-Manager → Install Models → 搜 "ipadapter" → 装你想要的变体。

## 最少需要的节点

基础图上加:

- `Load Image` — 你的参考图
- `IPAdapter Unified Loader` — 一个节点同时加载 IP-Adapter 模型和 CLIP Vision
- `IPAdapter`(或 `IPAdapter Advanced`)— 真正应用 adapter 的节点

## IP-Adapter 工作流接线

从能跑通的文生图图开始:

1. **加 Load Image。**选你的参考图
2. **加 IPAdapter Unified Loader。**输入:
   - `model` ← Load Checkpoint 的 MODEL
   输出:修改过的 MODEL + IPADAPTER 流水线
   控件:`preset` — 选变体(`PLUS`、`FACEID` 等)
3. **加 IPAdapter 节点**(应用节点,不是加载器)。输入:
   - `model` ← IPAdapter Unified Loader 的 MODEL
   - `ipadapter` ← IPAdapter Unified Loader 的 IPADAPTER
   - `image` ← Load Image 的 IMAGE
   控件:`weight` — 影响强度(0.0-2.0)
4. **IPAdapter 的 MODEL 输出** 接到 KSampler 的 `model` 输入

结果:扩散模型现在被文本提示词和参考图同时条件化。KSampler 照常跑。

## 权重调节

`weight` 是主钮。

| weight | 表现 |
|--------|------|
| 0.0 | IP-Adapter 关闭,纯文生图 |
| 0.4 | 微妙,参考图风格暗示 |
| 0.7 | **默认**,清晰视觉影响,提示词仍主导内容 |
| 1.0 | 强,输出明显像参考图 |
| 1.3+ | 参考图主导,文本提示词失去话语权 |

0.7 起步。参考图影响太弱往上调,提示词不被尊重往下调。

`weight_type`(Advanced 节点里)改变权重**怎么**应用:
- `linear` — 直接强度
- `ease in-out` — 扩散过程开头结尾软过渡
- `style transfer` — 强调风格不强调内容(适合艺术参考)
- `composition` — 强调布局不强调风格(适合照片参考)

第一次试:`linear`,权重 0.7。

## 用法一:风格迁移

目标:让生成图看起来像某幅名画。

- 参考:扫描或下载的"神奈川冲浪里"
- 变体:`PLUS`
- 权重:0.7
- 权重类型:`style transfer`
- 提示词:正常描述内容 — "a fox sitting on a moss-covered rock"

输出是用葛饰北斋画风的狐狸。模型从参考图取笔触、配色、构图线索。

## 用法二:人脸身份(FaceID)

目标:从一张参考照生成特定人物的肖像。

- 参考:清晰的人脸照,头肩比例,无遮挡
- 变体:`FACEID PLUS V2`
- 权重:0.8-1.0
- 提示词:描述场景 — "a portrait of a man in a dark suit, neutral background"

输出保留人物身份(眼、下颌线、辨识特征),姿势、衣服、背景从提示词来。下颌以下裁掉的参考更好 — 脸占大部分参考。

FaceID 和 ControlNet OpenPose 配合很好:同时锁定人物姿势和身份。

## 用法三:构图参考

目标:保留某图的布局,用不同风格重画。

- 参考:任何有想要构图的照片
- 变体:base `IP-Adapter`
- 权重:0.5-0.7
- 权重类型:`composition`
- 提示词:描述新风格和内容

输出保留粗略布局(主体位置、深度、取景),其它全部重画。

这有时和 ControlNet(Canny 或 Depth)重叠 — IP-Adapter 构图更松,ControlNet 更严。要自由用 IP-Adapter,要精确线条用 ControlNet。

## 和 LoRA、ControlNet 叠加

三者配合得不错。各自修改流水线不同部分:

- LoRA 修改 MODEL/CLIP 权重
- IP-Adapter 注入 MODEL 的交叉注意力
- ControlNet 条件化正向 CONDITIONING

常见叠法:

```
Load Checkpoint → Load LoRA → IPAdapter Unified Loader → IPAdapter → KSampler.model
                                                                       ↑
            Apply ControlNet ──────────────────────────────────────────┘
```

角色 LoRA + IP-Adapter 风格参考 + ControlNet 姿势 = "这个角色,这种风格,这种姿势"。三个独立杠杆。

总影响预算还要管。LoRA 0.7 + IP-Adapter 0.7 + ControlNet 1.0,生成保持连贯。三个全开通常出糊。

## 多张参考图

某些 IP-Adapter 版本接受多张参考。用 `IPAdapter Batch` 一次喂 N 张。模型平均它们的视觉嵌入 — 一张参考不够好但你有多张变时有用。

人脸场景下,同一人不同角度多张参考比单张照片身份更可靠。

## 常见失败

### 参考图影响看不见

- 权重太低,试 1.0
- CLIP Vision 文件错了(和 IP-Adapter 变体不匹配)。Unified Loader 防这个,手动配置容易错

### 输出就是参考图副本,无视提示词

- 权重太高,降到 0.6
- 试 `weight_type: style transfer` 让它取风格不取内容

### "ipadapter not found" / "clip_vision not found"

- 模型文件没在对的文件夹。`models/ipadapter/` 和 `models/clip_vision/`(不是 `models/checkpoints/`)
- 刷新 ComfyUI 重扫文件夹

### FaceID 出来的脸"差点意思"

- 参考脸裁太紧或太远。目标头+肩占画面 ~70%
- 参考有多张脸 — 人脸检测会乱。裁到一个人
- 参考脸光线极端,用中性光照片

### 加 IP-Adapter 后 OOM

- IP-Adapter 增加显存(CLIP Vision 编码器加载 + 额外交叉注意力)。SDXL + IP-Adapter Plus 对 12 GB 卡很紧。降分辨率或 `--lowvram`

### IP-Adapter 改的不是想要的特征

- 切 `weight_type`:`style transfer` 让内容跟提示词,`composition` 让风格跟提示词
- 用 `start_at` 和 `end_at`(Advanced 节点)— IP-Adapter 只在扩散早期或晚期生效。只早期保留构图,只晚期精修风格

## 怎么选 IP-Adapter / LoRA / ControlNet

决策流:

- 我想复刻某幅画的风格 → **IP-Adapter**(风格参考快)
- 我想每张图都像吉卜力风格 → **LoRA**(反复用,每次少设置)
- 我想要特定人物的脸 → **IP-Adapter FaceID**(一张照片)或 **LoRA**(多张照片,身份更稳)
- 我想要特定姿势 → **ControlNet OpenPose**(只有它能干)
- 我想抄精确构图 → **ControlNet Canny**(精确)或 **IP-Adapter composition**(松)

## 小结

- IP-Adapter = 从参考图来的视觉条件,不训练
- 按目标挑变体:base / plus(通用)/ faceid(身份)/ plus-face(神似)
- 权重 0.7 默认,`weight_type`(style / composition)调要转移什么
- 和 LoRA、ControlNet 叠加 — 总预算大约 1.5-2.0
- 适合一次性风格或身份参考,LoRA 更适合反复用

## 下一步

你已看过 6 大工作流扩展。两条值得继续探索:

- **采样器和调度器** — `dpmpp_2m_sde + karras` 之类,每种算法什么时候出彩
- **AnimateDiff** — 加上动作条件,把上面任何工作流变视频
