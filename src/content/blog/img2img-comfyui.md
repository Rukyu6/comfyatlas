---
title: "Image-to-Image in ComfyUI: Style Transfer, Photo Edits, and Sketch-to-Finished-Art"
description: "Use a real image as the starting latent instead of pure noise. The full img2img workflow in ComfyUI, with denoise tuning, common use cases, and how it interacts with LoRAs and ControlNet."
pubDate: 2026-05-21
lang: en
category: workflow-extensions
heroImage: ./_assets/cover-img2img.png
workflow:
  file: img2img.json
  title: Image-to-image style transfer workflow
  note: Drop your input image into Load Image. Tune denoise (0.4–0.7) for the amount of stylization.
tags: ["img2img", "image-to-image", "workflow", "stable-diffusion", "tutorial"]
---

Text-to-image starts from random noise. Image-to-image (img2img) starts from your image. The model treats your input as a partially-noised latent, then runs the same denoising process — except the denoising target is informed by what you provided. The output keeps the structure and broad colors of your input but takes its style and details from the prompt.

This is one of the three workflow extensions most users want, alongside [LoRA](/blog/lora-basics-comfyui/) and [ControlNet](/blog/controlnet-basics-comfyui/). It's also the simplest to wire — just two new nodes.

## What img2img is good for

- **Style transfer** — turn a photo into an oil painting, or anime, or pixel art
- **Photo editing** — change a season, time of day, or environment of an existing photo
- **Sketch to finished art** — draw a rough composition, let the model render it
- **Iterating an existing generation** — take an output you almost like and re-generate it with prompt tweaks

What it's *not* good for: pixel-perfect edits to specific regions. For that you need inpainting, which is a separate workflow.

## How it differs from text-to-image

In a text-to-image workflow:

```
Empty Latent Image  →  KSampler  →  VAE Decode  →  Save Image
   (blank canvas)    (full denoise)
```

In img2img:

```
Load Image  →  VAE Encode  →  KSampler  →  VAE Decode  →  Save Image
                              (partial denoise)
```

Two changes:

1. The empty latent is replaced by your encoded image (Load Image + VAE Encode)
2. KSampler's `denoise` is set below 1.0 — usually 0.4 to 0.7 — so it preserves part of your input

That's the whole pattern. Everything else (model, LoRAs, prompts, sampler) works the same.

## The minimum nodes

Search and add:

- `Load Image` — picks an image file or uploads from your computer
- `VAE Encode` — converts the pixel image to a latent

Then re-route your existing KSampler's `latent_image` input to come from VAE Encode instead of Empty Latent Image.

Wire VAE Encode's `vae` input to Load Checkpoint's VAE output.

## Wiring step by step

Starting from a working text-to-image graph:

1. **Add Load Image.** Drag the node onto canvas. Click `choose file to upload` and pick your input.
2. **Add VAE Encode.**
   - `pixels` ← Load Image's IMAGE output
   - `vae` ← Load Checkpoint's VAE (or Load VAE if you load it separately)
3. **Disconnect Empty Latent Image** from KSampler's `latent_image` input.
4. **Connect VAE Encode's LATENT** to KSampler's `latent_image`.
5. (Optional) Delete the Empty Latent Image node — you don't need it anymore.

You can keep Empty Latent Image around if you want to switch between text-to-image and img2img by re-routing. ComfyUI doesn't mind unused nodes.

## The denoise widget

This is the only knob you need to learn for img2img.

`denoise` on KSampler controls how much of your image gets replaced with new content. The math: at denoise = X, the sampler adds noise to your image to a level corresponding to X*total_steps, then runs (X*total_steps) denoising iterations.

Effective range:

| denoise | What happens |
|---------|--------------|
| 0.1 | Almost no change. The output is your input plus tiny stylistic touches. |
| 0.3 | Light style transfer. Photo stays photo-like; subtle prompt influence. |
| 0.5 | **Sweet spot for most use cases.** Visible style change, structure preserved. |
| 0.7 | Heavy reinterpretation. Same subject and rough composition, very different feel. |
| 0.9 | Very loose. The output barely resembles the input. |
| 1.0 | Pure text-to-image. Your input is ignored. |

For style transfer (photo → painting): start at 0.5, climb to 0.7 if the painting style isn't strong enough.

For "tweak this generation": 0.3–0.4 — preserves the image, just nudges the prompt.

For sketch-to-art: 0.7–0.8 — your sketch provides composition, the model fills in detail and refines.

## Resolution behavior

Your input image's dimensions become the output's dimensions. If you load a 1280×768 photo into VAE Encode, the output is 1280×768 — there's no separate width/height widget.

This has two consequences:

- The image dimensions need to be divisible by 8 (or 64 for SDXL). Most photos already are; if yours isn't, the encode will round.
- Loading a giant 4K photo will OOM your GPU. Resize your input to the model's native range (≈512 for SD 1.5, ≈1024 for SDXL) before processing.

To resize automatically, add an `Upscale Image` or `Image Resize` node between Load Image and VAE Encode. Set target to 1024 longer-edge for SDXL.

## Sketch-to-art example

You drew a rough sketch in any drawing app — a stick-figure landscape, a doodled portrait. Save as PNG, drop into ComfyUI.

Settings:

- `denoise` 0.75 — most of the sketch's detail gets replaced, but composition holds
- Prompt: describe what you want the final art to look like, including style and mood
- Negative: `sketch, line drawing, rough, low quality`
- Steps: 20–25
- CFG: 7

The output keeps the sketch's spatial layout but renders it as a finished painting / photo / illustration.

## Style transfer example

You have a daytime photo. You want it as a moonlit nightscape.

Settings:

- `denoise` 0.45 — preserves recognizable subject and layout
- Prompt: full target description ("moonlit night, cool blue tones, stars in sky")
- Steps: 20
- CFG: 7

Higher denoise = more dramatic style change but more compositional drift. Iterate.

## img2img + LoRA

LoRAs work identically — the modified MODEL feeds KSampler the same way. Use a "watercolor painting" LoRA at strength 0.8 with denoise 0.5 for clean watercolor stylization of any input photo.

## img2img + ControlNet

A common combination: img2img provides starting content, ControlNet locks structure.

Example: you have a 3D render. You want it as a stylized illustration but with **exact** edges preserved.

- img2img: 3D render at denoise 0.7 (heavy reinterpretation)
- ControlNet Canny: edges from same 3D render at strength 0.8

The img2img keeps colors and rough forms; ControlNet keeps edges precise. Together they give you stylization without losing the original geometry.

## Common failures

### Output looks identical to input

- denoise too low (0.1–0.2)
- Or wrong wiring — check that VAE Encode's output reaches KSampler's `latent_image` input

### Output ignores input completely

- denoise = 1.0. Drop to 0.5–0.7
- Or VAE Encode is disconnected — check the wire

### Output is grainy / noisy

- VAE mismatch. Make sure the VAE you wired to VAE Encode and VAE Decode is the same one (from the same checkpoint)
- Some checkpoints have a broken bundled VAE. Load a known-good VAE separately (`Load VAE`) and use it everywhere

### Output ignores your prompt

- denoise too low — model has no headroom to express prompt
- Try 0.6 instead of 0.4

### OOM

- Input resolution too high. Resize before VAE Encode.
- 4K photos at 0.7 denoise on SDXL will OOM most cards

### Color shifts unexpectedly

- VAE round-trip imprecision. Acceptable at 0.4 denoise; very visible at 0.1 denoise (which you should rarely use anyway).
- Use a model upscaler instead of latent space if pixel-precise color preservation matters.

## When to use img2img vs text-to-image with reference

If your goal is purely stylistic ("paint this scene in the style of X"), img2img is direct and quick. If you want the model to invent a new scene that just *resembles* yours in some way, text-to-image with a ControlNet reference (Canny or Depth) gives more freedom.

Rule of thumb:

- "Make THIS image look different" → img2img
- "Make a NEW image that has X attributes of this image" → text-to-image + ControlNet

## Summary

- img2img = real image instead of empty latent, partial denoise instead of full
- Two nodes added: Load Image + VAE Encode
- denoise 0.4–0.7 covers most use cases
- Preserves input dimensions; resize huge inputs first
- Stacks with LoRAs and ControlNet — common combo for style transfer with locked structure

## What's next

You've now seen the four main workflow building blocks: text-to-image, LoRA, ControlNet, Hires Fix, and img2img. Most workflows you'll find online combine these. Next areas worth exploring:

- **Inpainting** — selectively regenerate a region (a face, a hand, a background) without touching the rest
- **AnimateDiff** — turn a still workflow into video
- **IP-Adapter** — feed a reference image directly into conditioning instead of using LoRAs
- **Custom samplers and schedulers** — what `dpmpp_2m_sde + karras` actually means and when to use it
