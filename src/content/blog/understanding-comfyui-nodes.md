---
title: "Understanding ComfyUI Nodes: A Visual Guide for Beginners"
description: "What ComfyUI nodes actually are, how data flows between them, and the seven core nodes that make up the default text-to-image workflow. Written for people who just opened ComfyUI for the first time."
pubDate: 2026-05-19
lang: en
category: getting-started
heroImage: ./_assets/cover-nodes.png
tags: ["nodes", "getting-started", "fundamentals", "stable-diffusion"]
---

The first time you open ComfyUI you see a graph of boxes connected by colored wires. It looks intimidating. It is not.

A ComfyUI workflow is just a chain of small operations. Each box (a node) takes some inputs, does one thing, and passes its output to the next box. Once you know what the seven core nodes do, you can read any text-to-image workflow on the internet.

This guide walks through the default workflow node by node. It assumes you have ComfyUI installed and a checkpoint loaded. If not, see the [installation guide](/blog/comfyui-installation-guide/).

## How a node works

Every node has three parts:

- **Inputs** on the left side. Small dots (sockets) where wires come in.
- **Outputs** on the right side. Sockets where wires go out.
- **Widgets** in the middle. Fields you fill in directly: text, numbers, dropdowns.

A wire connects an output socket on one node to an input socket on another. Data flows left to right.

When you click `Queue Prompt`, ComfyUI starts at the rightmost nodes (`Save Image`), traces backward to find what they need, and runs every node in dependency order. You don't tell it the order. The graph is the order.

## The seven data types

Sockets are color-coded. The color tells you what kind of data flows through that wire. You can only connect outputs to inputs of the same color.

| Color   | Type           | What it is |
|---------|----------------|------------|
| Purple  | MODEL          | The diffusion model itself (the U-Net) |
| Yellow  | CLIP           | The text encoder |
| Red     | VAE            | The variational autoencoder (latent ↔ pixel converter) |
| Orange  | CONDITIONING   | An encoded prompt — the result of running text through CLIP |
| Pink    | LATENT         | An image in latent space (compressed, what the model actually works on) |
| Blue    | IMAGE          | A regular RGB image you can see |
| Gray    | INT / FLOAT / STRING | Plain numbers and text |

These exact colors may shift between ComfyUI versions, but the categories are stable.

The reason there are so many types is the diffusion process itself. A model doesn't operate on pixels. It operates on a compressed representation called a **latent**. The VAE compresses pixels into latents and decompresses them back. The model takes a latent plus a CONDITIONING (encoded prompt) and produces a less-noisy latent, repeated many times.

## The default workflow, node by node

When you first launch ComfyUI, the graph that loads is a complete text-to-image pipeline. Here is what each node does.

### 1. Load Checkpoint

This is the entry point. It reads a checkpoint file from `models/checkpoints/` and outputs three things:

- **MODEL** — the actual diffusion model that turns noisy latents into clean ones
- **CLIP** — the text encoder bundled inside the checkpoint
- **VAE** — the autoencoder bundled inside the checkpoint

A checkpoint is a single file (usually `.safetensors`) that packages all three. SDXL checkpoints, SD 1.5 checkpoints, and FLUX checkpoints all use the same `Load Checkpoint` node. The model knows what it is internally.

The dropdown widget lists every checkpoint in your `models/checkpoints/` folder. If you just added a new model, hit the refresh icon at the top right of ComfyUI to see it.

### 2. CLIP Text Encode (Prompt) — positive

This node takes:

- **CLIP** input (from `Load Checkpoint`)
- A **text** widget where you type your prompt

It outputs **CONDITIONING** — the prompt encoded into the format the model needs.

Two of these nodes are wired up by default. One is the **positive prompt** (what you want), the other is the **negative prompt** (what you don't want).

The text you type here is sent through CLIP's text tokenizer and encoder. The model never sees your raw text. It sees a vector representation.

### 3. CLIP Text Encode (Prompt) — negative

Same node, second copy, used for the negative prompt. Common starting negative prompts include things like `blurry, low quality, watermark`. Some newer models (FLUX, SD3) ignore negative prompts entirely — leave it empty.

### 4. Empty Latent Image

This node creates a blank latent canvas. It has three widgets:

- **width** — output image width in pixels (must be divisible by 8 for SD 1.5, by 64 for SDXL is recommended)
- **height** — output image height
- **batch_size** — how many images to generate in parallel

It outputs a **LATENT** — a tensor full of zeros at the requested dimensions. The KSampler will fill it with noise and then iteratively denoise it.

Native resolutions to know:
- SD 1.5: 512×512
- SDXL: 1024×1024
- FLUX: 1024×1024

Going much larger than native produces tiling artifacts. Going much smaller produces deformed faces. Stick close to native for the first run.

### 5. KSampler

This is the workhorse. It takes:

- **MODEL** — from `Load Checkpoint`
- **positive** — CONDITIONING from the positive prompt encoder
- **negative** — CONDITIONING from the negative prompt encoder
- **latent_image** — the empty LATENT from the previous step

And widgets:

- **seed** — random seed. Same seed + same inputs = same image. Click `randomize` (the dial icon) to get a fresh image each run.
- **control_after_generate** — `randomize`, `fixed`, `increment`, or `decrement`. What to do with the seed after each run.
- **steps** — how many denoising iterations to run. 20 is a sane default for most samplers. More steps = slower, not always better.
- **cfg** — classifier-free guidance scale. How strongly to follow the prompt. 7 is a sane default. Below 3 is too loose, above 12 starts producing artifacts.
- **sampler_name** — the algorithm. `euler` is fast and reliable. `dpmpp_2m` produces sharper results. `dpmpp_3m_sde` is slower but high quality.
- **scheduler** — how the noise schedule is shaped. `normal` is fine. `karras` often produces slightly better images.
- **denoise** — how much of the input latent to replace with noise. `1.0` for pure text-to-image. Anything less is for image-to-image.

The output is a **LATENT** — your generated image, but still in compressed latent form.

### 6. VAE Decode

The latent the KSampler produced is not viewable. It has 4 channels at 1/8 the resolution of the final image. This node converts it back to pixels.

Inputs:
- **samples** — the LATENT from KSampler
- **vae** — the VAE from `Load Checkpoint`

Output: **IMAGE** — a normal RGB image you can finally look at.

### 7. Save Image

The terminal node. It takes an IMAGE and writes it to `ComfyUI/output/`. The `filename_prefix` widget controls the start of the filename.

There is also a `Preview Image` node that displays the image in the browser without saving. Useful while you're tuning prompts.

## Reading the data flow

Look at the default workflow as a sentence:

`Load Checkpoint` provides MODEL, CLIP, and VAE.
↓
The CLIP feeds two `CLIP Text Encode` nodes (positive and negative prompts), which output two CONDITIONINGs.
↓
`Empty Latent Image` produces a blank canvas.
↓
`KSampler` combines MODEL + CONDITIONINGs + LATENT and runs denoising.
↓
`VAE Decode` turns the resulting latent into pixels using the VAE.
↓
`Save Image` writes the pixels to disk.

Once you can read this in your head, you can read any workflow.

## Adding nodes to the canvas

Three ways to add a node:

1. **Right-click** on empty canvas → `Add Node` → drill through the menu by category
2. **Double-click** on empty canvas → search box. Start typing `KSampler`, `CLIP`, etc. — fastest method
3. **Drag a wire** from a socket into empty space → release. ComfyUI shows only nodes with a matching socket type

The double-click search is the most useful. Memorize it.

## Connecting and disconnecting wires

- Click an output socket and drag to an input socket of the same color to connect.
- Click an existing wire to select it.
- Right-click a wire → `Delete` to remove. Or drag the wire end into empty space.
- An input can only have one wire. An output can fan out to many.

If you try to connect mismatched types, the wire snaps back. The colors are a hint about what's allowed.

## Custom nodes

The seven nodes above are core nodes — they ship with ComfyUI. The community has built thousands more. ControlNet preprocessors, IP-Adapter, animation, video, upscaling, face restoration. They install as folders inside `custom_nodes/`.

The most popular installer is **ComfyUI-Manager**. It adds a "Manager" button to the UI from which you can search and install custom node packs. Most workflow JSON files you'll find online expect specific custom nodes. ComfyUI-Manager will detect what's missing and offer to install it.

For a first week with ComfyUI, ignore custom nodes. Build comfort with the core graph first.

## Common beginner mistakes

- **Connecting CLIP to MODEL by accident.** They're both purple-ish in some themes. Look at the socket label — it says `MODEL` or `CLIP` next to the dot.
- **Leaving denoise below 1.0** in a pure text-to-image setup. The KSampler then expects a real input latent, not a blank one. You'll get half-noisy output.
- **Setting batch_size too high.** Each batch image lives in VRAM. A batch of 4 at 1024×1024 on SDXL needs ~16 GB.
- **Using SD 1.5 prompts on SDXL.** SDXL responds to natural-language prompts; long danbooru tag soup designed for SD 1.5 is less effective.

## What's next

You now understand the seven core nodes and how data flows between them. The next step is to actually build a workflow yourself — starting from an empty canvas, dragging in each node, wiring them up, and generating your first image. That walkthrough is the next guide.
