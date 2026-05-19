---
title: "LoRA Basics for ComfyUI: Style and Character Loaders Explained"
description: "What LoRAs are, how to install them, how to wire the Load LoRA node into your text-to-image workflow, and how to stack multiple LoRAs without breaking your image. Includes the strength settings that actually matter."
pubDate: 2026-05-19
lang: en
tags: ["lora", "stable-diffusion", "workflow", "tutorial", "fine-tuning"]
---

A LoRA (Low-Rank Adaptation) is a small file — typically 50–300 MB — that teaches a base model a specific style, character, or concept without retraining the whole thing. You apply it on top of any compatible checkpoint at generation time. One LoRA can turn SDXL into "anime in the style of artist X" or "always draws this specific character."

This guide covers what LoRAs are, where to get them, where they go, and how to wire the `Load LoRA` node into the workflow you built in [Your First ComfyUI Workflow](/blog/your-first-comfyui-workflow/).

## What a LoRA actually is

When someone fine-tunes a Stable Diffusion checkpoint normally, they retrain the entire ~2-7 GB U-Net. A LoRA is a much cheaper alternative: instead of changing the original weights, it adds small "delta" matrices to specific layers. These deltas are what gets saved.

This has three useful consequences:

- LoRAs are small (50-300 MB vs 2-7 GB)
- They stack — you can apply multiple at once
- They're checkpoint-compatible — a LoRA trained on one SD 1.5 checkpoint usually works on most SD 1.5 checkpoints

A LoRA trained for SD 1.5 will not work on SDXL or FLUX. Always match the LoRA to the base model architecture. The model's page on Civitai or Hugging Face says which it's for.

### LoRA vs LyCORIS vs LoCon vs LoHA

You'll see these terms in the wild. Practically:

- **LoRA** — the standard. Works in every UI.
- **LyCORIS** — an umbrella for variants (LoCon, LoHA, LoKr) that train more layers or use different math. Often produces stronger style transfer but the file format is slightly different.
- **LoCon, LoHA, LoKr** — specific LyCORIS variants.

For ComfyUI, LoRA loading is built in. LyCORIS variants need either a recent ComfyUI build (which now handles most of them) or the **ComfyUI-LyCORIS-Loader** custom node. If a LoRA loads but produces no visible effect, suspect a LyCORIS variant being silently ignored.

## Where LoRAs come from

Two main sources:

- **Civitai** — https://civitai.com — the largest LoRA library. Filter by base model (SD 1.5, SDXL, FLUX) and category (style, character, concept).
- **Hugging Face** — https://huggingface.co — more research-oriented LoRAs, less curated.

When you download, look for:
- **Base model** match (SD 1.5 / SDXL / FLUX)
- **Trigger words** — specific phrases the LoRA was trained against. The model only activates fully when you include them in the prompt.
- **Recommended weight** — usually 0.6–1.0. The LoRA author has tested what works.
- **Sample images and their prompts** — the fastest sanity check. Try replicating one before doing your own.

The file extension is `.safetensors` (preferred) or `.ckpt` (older, less safe). Always pick `.safetensors` if both are offered.

## Where to put the file

ComfyUI looks for LoRAs in:

```
ComfyUI/models/loras/
```

Drop the `.safetensors` file there. You can use subfolders to organize (`models/loras/sdxl/character/`, etc.) — ComfyUI scans recursively and shows the relative path in the dropdown.

After adding a new LoRA, click the refresh icon at the top right of ComfyUI. The `Load LoRA` node's dropdown will pick it up.

## Wiring the Load LoRA node

The `Load LoRA` node sits **between** `Load Checkpoint` and the rest of the graph. It modifies both the MODEL and the CLIP outputs of the checkpoint, so two of its three connection points need rewiring.

### Adding the node

Double-click empty canvas → search `Load LoRA` → add it.

Place it just to the right of `Load Checkpoint`.

### Connections

Inputs:
- **model** ← MODEL output of `Load Checkpoint`
- **clip** ← CLIP output of `Load Checkpoint`

Outputs:
- **MODEL** → goes to KSampler's `model` input (instead of the checkpoint's MODEL going there directly)
- **CLIP** → goes to both `CLIP Text Encode` nodes' `clip` input (instead of the checkpoint's CLIP)

In other words: the wires that used to go from `Load Checkpoint` straight to KSampler and to the prompt encoders now route through `Load LoRA` first.

The checkpoint's **VAE** output stays untouched — it still goes directly to `VAE Decode`. LoRAs don't modify the VAE.

### Widgets

- **lora_name** — dropdown of LoRAs in `models/loras/`. Pick yours.
- **strength_model** — how much the LoRA affects the U-Net. Default 1.0.
- **strength_clip** — how much it affects text understanding. Default 1.0.

These are independent. Keeping them equal is the safe default. Some users tune them separately to get more visual influence with less prompt-rewiring (high model_strength, low clip_strength).

## Trigger words

Most LoRAs require **trigger words** in the prompt to fully activate. The LoRA's Civitai page lists them.

Example: a "vintage film photography" style LoRA might list trigger words like `vintagefilm, kodachrome, film grain`. Your prompt becomes:

```
vintagefilm, a cinematic photo of a fox in a misty forest, kodachrome, golden hour, film grain
```

Without the trigger words, the LoRA still influences generation slightly but doesn't deliver the trained effect. With them, you get the full transformation.

For character LoRAs, the trigger word is usually the character's tagged name from training: `ohwx man`, `arknights amiya`, etc. — verbatim. Don't paraphrase.

## Strength tuning: what each value does

Default is 1.0 for both `strength_model` and `strength_clip`. Real-world useful range:

| Strength | Effect |
|----------|--------|
| 0.0 | LoRA disabled (same as not loading it) |
| 0.4–0.6 | Style hints; subtle influence |
| 0.7–0.9 | Strong but not dominant; useful for stacking |
| 1.0 | Full effect as trained |
| 1.1–1.3 | Pushed harder; risk of artifacts and "burned" colors |
| 1.5+ | Almost always breaks the image |

Negative values (`-0.5`, `-1.0`) are valid and produce the inverse — useful for "remove this style" kind of effects when paired with a LoRA you'd normally use positively.

When stacking LoRAs (next section), lowering each one's strength is essential.

## Stacking LoRAs

You apply multiple LoRAs by chaining `Load LoRA` nodes:

```
Load Checkpoint → Load LoRA #1 → Load LoRA #2 → Load LoRA #3 → KSampler / CLIP Text Encode
```

Each subsequent `Load LoRA` takes its `model` and `clip` inputs from the previous `Load LoRA`'s outputs.

When stacking, sum of strengths matters. Two LoRAs at 1.0 each is often too much — the model's output gets pushed beyond the natural distribution and you get muddy results, color shifts, or anatomy errors. Practical rule: keep the **sum of model_strengths around 1.0–1.5**. So for two LoRAs, 0.7 + 0.6 is safer than 1.0 + 1.0.

There's also a `Load LoRA Stack` node from the **rgthree-comfy** custom node pack that combines all your LoRAs into one node with strength sliders for each — much cleaner than chaining when you have three or more.

## Practical workflow patterns

### Style LoRA

```
Load Checkpoint (SDXL base)
   ↓ (model, clip)
Load LoRA (a style LoRA, strength 0.8/0.8)
   ↓
[rest of the workflow]
```

Trigger words at the start of the positive prompt. Subject in the middle. Quality boosters at the end:

```
[trigger words], a photo of [subject], [details], [quality keywords]
```

### Character + style stack

```
Load Checkpoint
   ↓
Load LoRA (character, strength 0.9/1.0)   ← character needs strong CLIP for the trigger word
   ↓
Load LoRA (style, strength 0.6/0.6)
   ↓
[rest]
```

Character LoRAs benefit from full clip_strength so the trigger word lands hard. Style LoRAs work fine with reduced strength.

### Detail enhancers (LoRAs trained on extra fine detail)

These often work at lower model_strength (`0.4–0.6`) since their job is augmenting rather than transforming. Stack them last in the chain.

## Troubleshooting

### LoRA seems to do nothing

- The LoRA is for a different base model (SDXL LoRA on SD 1.5 checkpoint, etc.). Check the model card.
- It's a LyCORIS variant your ComfyUI version doesn't support natively. Update ComfyUI or install ComfyUI-LyCORIS-Loader.
- You forgot the trigger words.
- strength is set to 0.

### Image is "burned" — oversaturated, blown-out colors

- Total strength sum is too high. Drop each LoRA's strength.
- cfg in KSampler is too high in combination with a strong LoRA. Try cfg 5 instead of 7.

### Faces look melted with character LoRA

- The base checkpoint and the LoRA's training base are too different. Character LoRAs trained on SD 1.5 base sometimes break on heavily-merged anime checkpoints. Try the LoRA on the original base checkpoint to confirm it works, then switch.
- model_strength is too high for that checkpoint. Drop to 0.7.

### Out of memory after adding LoRA

LoRAs add to memory usage during inference. If you were already close to the edge, two stacked LoRAs can OOM. Restart ComfyUI to clear allocator fragmentation, then try with `--lowvram`.

### LoRA file is in the folder but not in the dropdown

Click the refresh icon at the top right of ComfyUI. If still missing, the file extension is `.pt` or something exotic — rename to `.safetensors`. If it's actually broken, ComfyUI logs a load error in the console.

## Saving LoRA-aware workflows

The workflow JSON saves the LoRA file path along with the strength values. When you (or someone else) loads the workflow later, ComfyUI looks up the LoRA by filename. If the file isn't there, you'll see an "Invalid LoRA" warning at load time — install the missing LoRA and refresh.

This makes ComfyUI workflows naturally portable but means your `models/loras/` folder is part of the deal. Sharing workflow JSONs with others requires also sharing (or pointing to) the LoRAs they reference.

## What's next

LoRAs cover style and character control. The next layer of control is **structure** — making the model produce a specific composition, pose, or layout. That's ControlNet, and it's the next guide.
