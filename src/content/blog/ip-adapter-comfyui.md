---
title: "IP-Adapter in ComfyUI: Reference an Image Instead of Training a LoRA"
description: "How IP-Adapter feeds a reference image directly into the model's conditioning to copy style, subject, or face — without any training. Includes setup, the four model variants, weight tuning, and how it stacks with LoRAs and ControlNet."
pubDate: 2026-05-22
lang: en
category: workflow-extensions
tags: ["ip-adapter", "reference-image", "workflow", "stable-diffusion", "tutorial"]
---

You want generations to look like a specific reference image. The classic answer is to train a LoRA — collect a dataset, run training, wait an hour, hope it learned the right features. IP-Adapter skips all that. You drop a reference image into a node, the model uses it as visual conditioning alongside your text prompt, and the output picks up the reference's style, subject, or face. No training, no dataset, no waiting.

This guide assumes you have a working text-to-image workflow ([first workflow](/blog/your-first-comfyui-workflow/)) and have read the [LoRA basics](/blog/lora-basics-comfyui/) since IP-Adapter solves a similar problem with a different mechanism.

## What IP-Adapter actually is

IP-Adapter (Image Prompt Adapter) is a small attached network that takes a reference image, runs it through a CLIP image encoder, and injects the resulting visual embedding into the diffusion model's cross-attention layers. The model then "pays attention" to your reference image the same way it pays attention to your text prompt.

You can think of it as: text prompt = what you want, image prompt = how it should look.

What changes vs LoRA:

| Aspect | LoRA | IP-Adapter |
|--------|------|------------|
| Setup | Pre-trained file you download | Pre-trained adapter + reference image |
| Per-use | Pick file, set strength | Pick file, drop reference image, set strength |
| What it captures | Whatever was in training data | Whatever's in the reference image |
| File size | 50-500 MB | 100-300 MB once (the adapter), reusable for any reference |
| Best for | Recurring characters, signature styles | One-off references, fast iteration |

LoRAs are still the better choice when you'll generate hundreds of images of the same character. IP-Adapter wins when you want to try 50 different references in 10 minutes.

## The four IP-Adapter model variants

Different variants are trained for different jobs. Pick the one matching your goal.

| Variant | What it does | When to use |
|---------|--------------|-------------|
| **Base** (`ip-adapter_sd15`) | General visual style + subject | Default starting point |
| **Plus** (`ip-adapter-plus_sd15`) | Stronger fidelity to the reference | When base feels too weak |
| **FaceID** (`ip-adapter-faceid`) | Face identity preservation | Recreating a specific person's face |
| **Plus Face** (`ip-adapter-plus-face`) | Face structure (less identity, more likeness) | Generic "this kind of face" |

For SDXL there are equivalents: `ip-adapter_sdxl`, `ip-adapter-plus_sdxl`, etc. Don't mix base models — SD 1.5 IP-Adapter on SDXL checkpoint won't work.

## Setup: install the custom nodes and the models

IP-Adapter ships as custom nodes. The most common pack is **ComfyUI_IPAdapter_plus** by cubiq.

### Install via ComfyUI-Manager

1. Open ComfyUI-Manager → Install Custom Nodes
2. Search "IPAdapter plus" → Install the cubiq one
3. Restart ComfyUI

### Download the model files

You need three pieces:

1. **CLIP Vision encoder** — `models/clip_vision/`
   - `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` (for SD 1.5 IP-Adapter)
   - `CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors` (for SDXL IP-Adapter)

2. **IP-Adapter model** — `models/ipadapter/`
   - `ip-adapter_sd15.safetensors` and/or `ip-adapter-plus_sd15.safetensors`
   - `ip-adapter_sdxl.safetensors` and/or `ip-adapter-plus_sdxl.safetensors`

3. **(FaceID only)** Insightface buffalo_l — auto-installed on first run, but needs `pip install insightface onnxruntime` to work.

The cubiq node pack includes a download script. Open ComfyUI-Manager → Install Models → search "ipadapter" → install the variants you want.

## The minimum nodes

Add to a basic graph:

- `Load Image` — your reference image
- `IPAdapter Unified Loader` — loads the IP-Adapter model and CLIP Vision in one node
- `IPAdapter` (or `IPAdapter Advanced`) — the actual adapter application

## Wiring an IP-Adapter workflow

Starting from a working text-to-image graph:

1. **Add Load Image.** Pick your reference image.
2. **Add IPAdapter Unified Loader.** Inputs:
   - `model` ← Load Checkpoint's MODEL
   Output: a modified MODEL + the IPADAPTER pipeline.
   Widget: `preset` — pick the variant (`PLUS`, `FACEID`, etc.)
3. **Add IPAdapter** node (the application node, not the loader). Inputs:
   - `model` ← IPAdapter Unified Loader's MODEL
   - `ipadapter` ← IPAdapter Unified Loader's IPADAPTER
   - `image` ← Load Image's IMAGE
   Widget: `weight` — strength of influence (0.0-2.0)
4. **Wire IPAdapter's MODEL output** to KSampler's `model` input.

Result: the diffusion model is now conditioned by both text prompt and reference image. Run KSampler as usual.

## The weight dial

`weight` is the main knob.

| weight | Behavior |
|--------|----------|
| 0.0 | IP-Adapter off. Pure text-to-image. |
| 0.4 | Subtle. Small style hint from reference. |
| 0.7 | **Default.** Clear visual influence, prompt still drives content. |
| 1.0 | Strong. Output looks heavily like the reference. |
| 1.3+ | Reference dominates. The text prompt loses authority. |

Start at 0.7. Move up if reference influence is too weak. Move down if your prompt isn't being respected.

`weight_type` (in the Advanced node) lets you change *how* weight is applied:
- `linear` — straightforward strength
- `ease in-out` — soft start and end across diffusion steps
- `style transfer` — emphasizes style over content (good with art references)
- `composition` — emphasizes layout over style (good with photo references)

For a first try: `linear`, weight 0.7.

## Use case 1: Style transfer

Goal: make a generation look like a famous painting.

- Reference: scan or download of "The Great Wave"
- Variant: `PLUS`
- Weight: 0.7
- Weight type: `style transfer`
- Prompt: describe content as normal — "a fox sitting on a moss-covered rock"

The output is a fox in the painterly style of Hokusai. The model takes brush style, color palette, and composition cues from the reference.

## Use case 2: Face identity (FaceID)

Goal: generate a portrait of a specific person from a single reference photo.

- Reference: clear face photo of the person, head-and-shoulders, no occlusion
- Variant: `FACEID PLUS V2`
- Weight: 0.8-1.0
- Prompt: describe scenario — "a portrait of a man in a dark suit, neutral background"

The output preserves the person's identity (eyes, jawline, distinguishing features) while taking pose, clothing, and setting from the prompt. Crops below the chin help — face occupies most of the reference.

FaceID stacks well with ControlNet OpenPose: lock the person's pose and identity at the same time.

## Use case 3: Composition reference

Goal: keep an image's layout but redraw it in a different style.

- Reference: any photo with the desired composition
- Variant: base `IP-Adapter`
- Weight: 0.5-0.7
- Weight type: `composition`
- Prompt: describe the new style and content

Output keeps the rough layout (subject placement, depth, framing) but redraws everything else.

This sometimes overlaps with ControlNet (Canny or Depth) — IP-Adapter composition is looser, ControlNet is stricter. Use IP-Adapter when you want freedom; ControlNet when you want exact lines.

## Stacking IP-Adapter with LoRAs and ControlNet

All three play nicely together. Each modifies a different part of the pipeline:

- LoRA modifies MODEL/CLIP weights
- IP-Adapter injects into MODEL's cross-attention
- ControlNet conditions the positive CONDITIONING

A common stack:

```
Load Checkpoint → Load LoRA → IPAdapter Unified Loader → IPAdapter → KSampler.model
                                                                       ↑
            Apply ControlNet ──────────────────────────────────────────┘
```

Use a character LoRA + IP-Adapter style reference + ControlNet pose = "this character, in this style, in this pose." Three independent levers.

Total influence budget still applies. With LoRA at 0.7 + IP-Adapter at 0.7 + ControlNet at 1.0, generations stay coherent. Push all three to max and the model often produces mush.

## Multiple reference images

Some IP-Adapter versions accept multiple references. Use `IPAdapter Batch` to feed N images at once. The model averages their visual embedding — useful when one reference isn't quite right but you have several variations.

For face work, multiple references of the same person from different angles produce more reliable identity than a single photo.

## Common failures

### Reference influence is invisible

- Weight too low. Try 1.0.
- Wrong CLIP Vision file (mismatch with IP-Adapter variant). The Unified Loader prevents this; manual setups can mismatch.

### Output is just a copy of the reference, ignoring prompt

- Weight too high. Drop to 0.6.
- Try `weight_type: style transfer` so it takes style not content.

### "ipadapter not found" / "clip_vision not found"

- Model files aren't in the right folder. `models/ipadapter/` and `models/clip_vision/` (not `models/checkpoints/`).
- Refresh ComfyUI to re-scan folders.

### Face is "off" with FaceID

- Reference face crop too tight or too distant. Aim for head + shoulders fill ~70% of frame.
- Multiple faces in the reference — confuses face detection. Crop to one person.
- Lighting on the reference face is extreme. Use a neutral lit photo.

### OOM after adding IP-Adapter

- IP-Adapter adds VRAM cost (CLIP Vision encoder load + extra cross-attention compute). 12 GB cards are tight on SDXL + IP-Adapter Plus. Drop resolution or use `--lowvram`.

### IP-Adapter changes the wrong characteristic

- Switch `weight_type`: `style transfer` to keep content prompt-driven; `composition` to keep style prompt-driven.
- Use `start_at` and `end_at` (in Advanced node) — apply IP-Adapter only in early or late diffusion steps. Early-only preserves composition, late-only refines style.

## When to choose IP-Adapter vs LoRA vs ControlNet

A decision flow:

- I want to recreate a specific painting style → **IP-Adapter** (style reference is fast)
- I want every generation to look like Studio Ghibli → **LoRA** (recurring use, less per-prompt setup)
- I want a specific person's face → **IP-Adapter FaceID** (one photo) or **LoRA** (many photos, better identity)
- I want a specific pose → **ControlNet OpenPose** (only thing that does this)
- I want to copy an exact composition → **ControlNet Canny** (precise) or **IP-Adapter composition** (loose)

## Summary

- IP-Adapter = visual conditioning from a reference image, no training
- Pick variant based on goal: base / plus (general) / faceid (identity) / plus-face (likeness)
- Weight 0.7 default; `weight_type` (style / composition) tunes what gets transferred
- Stacks with LoRAs and ControlNet — total budget around 1.5-2.0 across all
- Best for one-off style or identity references; LoRA wins for recurring use

## What's next

You've now seen six core workflow expansions. Two solid directions to explore from here:

- **Custom samplers and schedulers** — `dpmpp_2m_sde + karras` and friends, when each algorithm shines
- **AnimateDiff** — turn any of the workflows above into video by adding motion conditioning
