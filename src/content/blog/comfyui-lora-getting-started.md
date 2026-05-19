---
title: "ComfyUI LoRA Guide: How to Use LoRAs to Change Style and Subject"
description: "What a LoRA is, how to install it, how to apply it to your ComfyUI workflow, how to stack multiple LoRAs, and how to control their strength. Includes the right strength values to start with and common mistakes."
pubDate: 2026-05-19
lang: en
tags: ["lora", "fine-tuning", "stable-diffusion", "workflow", "tutorial"]
---

LoRA stands for Low-Rank Adaptation. In plain terms: a small file (usually 50–300 MB) you bolt onto a base model to teach it a new style, character, object, or aesthetic without retraining the whole 7+ GB checkpoint.

LoRAs are the single most useful add-on for Stable Diffusion. Want anime style on a realistic checkpoint? LoRA. Want a specific person's face? LoRA. Want a particular art movement, lighting style, or fashion era? LoRA.

This guide covers what they are, how to install them, and how to wire them into the workflow you built in the [first workflow guide](/blog/your-first-comfyui-workflow/).

## What a LoRA actually does

A base checkpoint (SD 1.5, SDXL, FLUX) has billions of parameters. Fine-tuning all of them on a new dataset is expensive — needs a serious GPU and hours of training.

LoRA training freezes the original weights and learns a tiny set of new weights — typically 0.1% the size of the original. At inference time, ComfyUI loads the LoRA and adds those small weight changes on top of the base model. The result is the base model's general knowledge plus the LoRA's narrow expertise.

A few consequences:

- **LoRAs are checkpoint-specific.** A LoRA trained on SD 1.5 won't work on SDXL. A LoRA trained on a realistic SDXL checkpoint might work poorly on an anime SDXL checkpoint, even though both are SDXL.
- **LoRAs stack.** You can apply 2, 3, even 5 LoRAs to one generation. Style + character + lighting LoRAs can all run together.
- **Strength is controllable.** Each LoRA has a `strength` parameter from 0 to 1 (and sometimes higher). 0 = LoRA disabled. 1 = full effect. Most workflows use 0.6–0.9.

## Where to download LoRAs

The two main hubs:

- **Civitai** — civitai.com. Largest selection, includes adult content (filterable). Quality varies wildly. Filter by base model (SD 1.5 / SDXL / FLUX / Pony) before downloading.
- **Hugging Face** — huggingface.co. More technical, fewer "fan-art" LoRAs but generally higher quality and better-documented.

Each LoRA's page tells you:

- **Base model** — must match your checkpoint
- **Trigger words** — specific tokens you put in the prompt to activate the LoRA. Some LoRAs need `<style of XYZ>` or `(masterpiece by ABC:1.2)`. Others activate just by being loaded.
- **Recommended strength** — usually a range like 0.6–1.0
- **Sample images** — what to expect

Read the description before downloading. A LoRA built for a different base model is dead weight.

## Installing a LoRA

Place the `.safetensors` file in `ComfyUI/models/loras/`.

You can organize into subfolders if you want:

```
models/loras/
  style/
    studio-ghibli.safetensors
    cyberpunk-neon.safetensors
  character/
    custom-character-v1.safetensors
  concept/
    detail-tweaker.safetensors
```

ComfyUI traverses subfolders, so the dropdown will show them as `style/studio-ghibli` etc.

After dropping the file in, click the refresh button at the top right of ComfyUI (the circular arrow icon). The new LoRA appears in the dropdown.

## Adding a LoRA to your workflow

Open the workflow from the [first workflow guide](/blog/your-first-comfyui-workflow/). The chain is:

```
Load Checkpoint → MODEL → KSampler
              └─ CLIP → CLIP Text Encode (positive) → KSampler
              └─ CLIP → CLIP Text Encode (negative) → KSampler
              └─ VAE → VAE Decode
```

To add a LoRA, you insert a `Load LoRA` node between `Load Checkpoint` and the consumers. The LoRA node intercepts both MODEL and CLIP, modifies them, and passes through.

### Steps

1. Double-click empty canvas → search `Load LoRA` → add node
2. Drag it onto the wire between `Load Checkpoint` and your prompt encoders. ComfyUI will automatically reroute the connection through the LoRA node.
3. If auto-routing didn't happen, manually reconnect:
   - `Load Checkpoint` → MODEL → `Load LoRA` → model
   - `Load Checkpoint` → CLIP → `Load LoRA` → clip
   - `Load LoRA` → MODEL → `KSampler` → model
   - `Load LoRA` → CLIP → both `CLIP Text Encode` nodes → clip

The `Load LoRA` node has three widgets:

- **lora_name** — pick the LoRA from the dropdown
- **strength_model** — how much the LoRA affects the diffusion model. 0–1 typical, 0.6–0.9 sweet spot.
- **strength_clip** — how much the LoRA affects text understanding. Often kept equal to strength_model. Lower it to 0 if the LoRA is changing prompt interpretation in unwanted ways.

## Stacking multiple LoRAs

You can chain `Load LoRA` nodes:

```
Load Checkpoint → Load LoRA (style) → Load LoRA (character) → Load LoRA (detail) → KSampler
                                  └────── CLIP wires also chain through ───────┘
```

Each LoRA node's output feeds the next LoRA node's input. Order can matter for conflicting LoRAs but for compatible ones it doesn't.

Tips for stacking:

- **Lower strength when stacking.** Three LoRAs at 1.0 each = mush. Try 0.7, 0.6, 0.4.
- **Style LoRAs first, character LoRAs after.** Style usually wants broad influence; characters want precise control.
- **Don't stack two LoRAs trying to do the same thing.** Two anime style LoRAs at full strength will fight each other.

For 4+ LoRAs, consider the `LoRA Loader Stack` custom node (rgthree-comfy or efficiency-nodes) which packs multiple LoRAs into one node — easier to manage but functionally the same.

## Trigger words and prompt strategy

Many LoRAs need specific trigger words in the prompt to activate properly:

```
positive prompt:
masterpiece, best quality, <ghibli style>, a cottage in a meadow at golden hour
```

Without `<ghibli style>` (the LoRA's documented trigger), the LoRA may add nothing. Always check the LoRA's description page.

For weight emphasis:

```
(ghibli style:1.2)   — emphasize 20% more
[ghibli style:0.8]   — de-emphasize
```

These prompt-level weights stack with the LoRA's `strength_model`. Don't overlap them — pick one place to control intensity.

## Picking strength values

A starting cheat sheet:

| LoRA type | Starting strength | Notes |
|-----------|-------------------|-------|
| Style (anime, painting, etc.) | 0.7–0.8 | Lower if it dominates |
| Character (face/identity) | 0.8–1.0 | Need high to keep features |
| Concept (clothing, item) | 0.6–0.8 | Higher when you want it center-frame |
| Detail/quality enhancers | 0.3–0.6 | Cumulative, less is more |
| Pose/composition | 0.5–0.7 | Tweak to taste |

Generate one image. Note what's wrong. Adjust by 0.1 at a time. Don't change strength + prompt + seed all at once — you won't know what fixed it.

## Common LoRA problems

### The LoRA does nothing

Check:
- Is the base model match? SD 1.5 LoRA on an SDXL checkpoint silently does nothing.
- Did you wire BOTH `model` and `clip` through? A `Load LoRA` only on the model output, with CLIP bypassing it, often produces near-zero effect.
- Did you include the trigger word from the LoRA's documentation?
- Is `strength_model` accidentally set to 0?

### The LoRA dominates everything

- Lower `strength_model` to 0.5 or below
- Reduce prompt weight if you used `(trigger:1.5)`
- Check whether your base prompt is strong enough — a weak prompt + strong LoRA = LoRA wins

### The image is overcooked / fried

Multiple high-strength LoRAs stacked, or one LoRA cranked above 1.0. Bring it down. Three LoRAs at 0.7 each is usually the practical ceiling.

### Faces look wrong

If a character LoRA is trained on portraits, generating wide shots may produce broken faces. Two fixes:

- Generate at native resolution (1024×1024 SDXL), then crop
- Add Face Detailer / ADetailer custom nodes to fix faces in a second pass

### Wrong base — checkpoint mismatch

The LoRA file might still load (no error) but produce noise or non-effects. Check the LoRA's metadata or description for "base model: SD 1.5" / "SDXL 1.0" / "Pony" / etc., and verify your `Load Checkpoint` is the same family. SDXL Pony LoRAs in particular are not interchangeable with regular SDXL.

## Saving the LoRA-enabled workflow

Once it works, save the workflow. `Ctrl+S` writes a JSON file that captures every node, every wire, every value. Reload later by dragging the JSON onto the canvas.

ComfyUI also embeds the workflow into PNG metadata, so any image you generate can be dragged back to restore the exact graph (including LoRA strengths, seeds, samplers — everything). For LoRA experimentation this is invaluable: you can A/B test settings and always know exactly how a given image was made.

## Quick reference: full LoRA-enabled workflow

```
Load Checkpoint
  ├─ MODEL → Load LoRA (style) → Load LoRA (character) → KSampler (model)
  ├─ CLIP  → Load LoRA (style) → Load LoRA (character) → CLIP Text Encode (positive) → KSampler (positive)
  │                                                    └─ CLIP Text Encode (negative) → KSampler (negative)
  └─ VAE → VAE Decode → Save Image

Empty Latent Image → KSampler (latent_image)
KSampler → VAE Decode → Save Image
```

Each `Load LoRA` carries forward both MODEL and CLIP. Don't split them.

## What's next

LoRAs handle style and subject. The next big tool is **ControlNet** — instead of describing what you want with words, you give the model a reference image (a pose skeleton, a depth map, an edge sketch) and it composes around that reference. ControlNet plus LoRAs is the practical workflow most production users settle on. That's the next guide.
