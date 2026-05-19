---
title: "Your First ComfyUI Workflow: Text-to-Image Step by Step"
description: "Build a complete text-to-image workflow in ComfyUI from an empty canvas. Add each node, wire it up, and generate your first image. Includes the exact settings to use and what to do when something goes wrong."
pubDate: 2026-05-19
lang: en
category: getting-started
tags: ["workflow", "tutorial", "text-to-image", "getting-started", "stable-diffusion"]
---

The fastest way to understand ComfyUI is to build something with it. The default workflow that loads on first launch is fine, but it's also a black box — the nodes are already there. You learn nothing about why they're connected the way they are.

This guide walks through building the same workflow yourself, from an empty canvas. By the end you'll have generated your first image and you'll know exactly which node connects to which and why.

If you don't have ComfyUI installed yet, see the [installation guide](/blog/comfyui-installation-guide/). If you don't know what nodes are, read the [nodes guide](/blog/understanding-comfyui-nodes/) first — it explains the seven core nodes we're about to wire together.

## What you need

- ComfyUI running at http://127.0.0.1:8188
- At least one Stable Diffusion checkpoint in `ComfyUI/models/checkpoints/`
- 6 GB of VRAM minimum (8 GB recommended for SDXL)

A good first checkpoint is **Stable Diffusion 1.5 base** — small, fast, and forgiving. SDXL works too but generations take longer and use more memory.

## Step 1: Clear the canvas

Open ComfyUI in your browser. You'll see the default workflow.

To start fresh:

- Right-click on the canvas → `Clear`
- Or press `Ctrl+A` to select all → `Delete`

You should now have an empty gray canvas. Pan with middle-mouse drag, zoom with mouse wheel.

## Step 2: Add Load Checkpoint

Double-click the empty canvas. A search box appears.

Type `Load Checkpoint` and click the result. The node drops onto your canvas at the cursor.

The node has:

- One widget: a dropdown listing your checkpoints
- Three outputs on the right: MODEL, CLIP, VAE

Click the dropdown and pick your checkpoint. If it's empty, you have no checkpoints in `models/checkpoints/`.

## Step 3: Add the two CLIP Text Encode nodes

Double-click the canvas → search `CLIP Text Encode` → add it.

Drag it to the right of `Load Checkpoint` so there's room to wire them.

Now connect the wires:

1. Click the **CLIP** output (yellow socket on the right of `Load Checkpoint`).
2. Drag a line to the **clip** input (yellow socket on the left of `CLIP Text Encode`).
3. Release. A yellow wire appears.

Click the text area inside the `CLIP Text Encode` node. Type your **positive prompt**:

```
a cinematic photo of a fox sitting on a moss-covered rock in a misty forest, golden hour lighting, sharp focus
```

Now add a second `CLIP Text Encode` node the same way. Wire its `clip` input to the same `CLIP` output of `Load Checkpoint`. (One output can fan out to many inputs.)

In the second node's text area, type a **negative prompt**:

```
blurry, low quality, watermark, text, deformed, extra limbs
```

Tip: rename the nodes to keep them straight. Right-click each → `Rename` → call them "Positive" and "Negative".

## Step 4: Add Empty Latent Image

Double-click → search `Empty Latent Image` → add it.

Place it below the prompt nodes.

It has three widgets and one output (LATENT). Set the widgets:

- **width**: 512 (for SD 1.5) or 1024 (for SDXL)
- **height**: 512 or 1024
- **batch_size**: 1

This node has no inputs. It just creates a blank canvas at the size you ask for.

## Step 5: Add KSampler

Double-click → search `KSampler` → add it.

Place it to the right of everything else. KSampler is the heart of the workflow.

KSampler has four inputs:

- **model** (purple)
- **positive** (orange) — CONDITIONING
- **negative** (orange)
- **latent_image** (pink)

Wire them up:

1. `Load Checkpoint` → MODEL → KSampler → model
2. Positive `CLIP Text Encode` → CONDITIONING → KSampler → positive
3. Negative `CLIP Text Encode` → CONDITIONING → KSampler → negative
4. `Empty Latent Image` → LATENT → KSampler → latent_image

Now configure the widgets:

- **seed**: any number, or click `randomize`
- **control_after_generate**: `randomize` (so each run produces a different image)
- **steps**: 20
- **cfg**: 7.0
- **sampler_name**: `euler` (start simple)
- **scheduler**: `normal`
- **denoise**: 1.0 (full noise, this is pure text-to-image)

Don't change these on the first run. Once you have a working baseline, then experiment.

## Step 6: Add VAE Decode

Double-click → search `VAE Decode` → add it.

Place it to the right of KSampler. VAE Decode converts the latent KSampler produces into a viewable image.

It has two inputs:

- **samples** (pink) — LATENT
- **vae** (red) — VAE

Wire:

1. KSampler → LATENT → VAE Decode → samples
2. Load Checkpoint → VAE → VAE Decode → vae

## Step 7: Add Save Image

Double-click → search `Save Image` → add it.

Place it at the far right. Wire VAE Decode → IMAGE → Save Image → images.

The `filename_prefix` widget controls the start of the saved filename. Set it to something memorable like `forest-fox`.

You can also use `Preview Image` instead — it shows the image in the browser without writing it to disk. Useful while you're iterating on prompts.

## Step 8: Generate

Look at the canvas. You should have seven nodes connected like this:

```
Load Checkpoint ─┬─ MODEL ──────────────┐
                 ├─ CLIP ──┬─ Positive ──┼─ KSampler ─ VAE Decode ─ Save Image
                 │         └─ Negative ──┤
                 └─ VAE ─────────────────│──────────────┘
                                         │
                  Empty Latent Image ────┘
```

Press `Q` or click `Queue Prompt` (top-right area).

Each node turns green as it runs. The KSampler shows a progress bar.

First generation is slowest because the model has to load into VRAM. SD 1.5 takes a few seconds, SDXL takes longer the first time.

When done, the image appears in the `Save Image` node. The file is in `ComfyUI/output/`.

## Saving and reusing your workflow

Once you have a workflow that works, save it.

- Click the `Save` button in the menu, or press `Ctrl+S`
- Save the JSON file somewhere you'll remember

To restore a workflow:

- Drag the JSON file onto the ComfyUI canvas
- Or click `Load` and pick the file

You can also drag a **PNG image** that ComfyUI generated back onto the canvas. ComfyUI embeds the workflow into the PNG metadata, so dropping the image restores the exact graph that produced it. This is one of ComfyUI's best features.

## Iterating on prompts

Now that you have a working baseline, try changing things:

- **Edit the positive prompt.** Re-queue. The seed is fixed (or randomized — set `control_after_generate` to `fixed` if you want to compare with the same seed).
- **Change the seed.** Same prompt, different image.
- **Bump steps to 30.** Slightly more refined output, slower.
- **Try a different sampler.** `dpmpp_2m` with `karras` scheduler is a popular combo for SD 1.5 and SDXL.
- **Change resolution.** 768×512 for landscape, 512×768 for portrait. Stay close to native (512 for SD 1.5, 1024 for SDXL).

Make one change at a time. If you change five things and the image gets worse, you don't know which one caused it.

## Troubleshooting

### "Error occurred when executing CLIPTextEncode"

Usually means the checkpoint loaded badly or the CLIP model is missing. Check the console where ComfyUI is running for the actual Python error.

### Out of memory (OOM)

Lower the resolution to 512×512 first. If that works, you can climb back up.

For SDXL on 8 GB cards, launch ComfyUI with `--lowvram` (in the bat file or the command line). For 6 GB cards, use `--medvram`.

### The image is grey or pure noise

This usually means the wrong VAE is hooked up, or the checkpoint is corrupt. Double-check that the VAE wire goes from `Load Checkpoint` to `VAE Decode`. If you're using a model that doesn't bundle a VAE (rare), you need to load a VAE separately with `Load VAE` and use that instead.

### The image is blurry mush

- denoise is below 1.0 in a text-to-image setup. Set it to 1.0.
- cfg is too low (below 3) or too high (above 14). Reset to 7.
- Steps is too low (below 10). Try 20.

### KSampler runs but no image appears

You forgot to connect VAE Decode to Save Image, or VAE Decode is missing entirely. The KSampler output is a latent, not an image — it has to go through VAE Decode.

### Same image every time

`control_after_generate` is set to `fixed`. Change it to `randomize`.

## What you've learned

You've built a complete text-to-image workflow from scratch. You know:

- Which seven core nodes are needed for any text-to-image generation
- How they connect and why
- What the KSampler widgets do
- How to save and restore workflows
- What to check when generation goes wrong

This workflow is the foundation. Image-to-image, inpainting, ControlNet, LoRAs, upscaling — they all start from this graph and add nodes onto it. Get this one comfortable first.

## Next steps

A few directions to explore from here:

- **Image-to-image.** Replace `Empty Latent Image` with `Load Image` + `VAE Encode`. Lower `denoise` to 0.5–0.7 to vary an existing image instead of generating from noise.
- **LoRAs.** Insert a `Load LoRA` node between `Load Checkpoint` and the rest of the graph to apply style or character LoRAs.
- **Upscaling.** After `VAE Decode`, add an upscaler node (`Upscale Image By` or model-based `UpscaleModelLoader` + `ImageUpscaleWithModel`) to enlarge the result.

Each of these gets its own guide.
