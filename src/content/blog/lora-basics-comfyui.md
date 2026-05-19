---
title: "LoRA Basics in ComfyUI: How to Apply Style and Character Models"
description: "What a LoRA is, where it lives in your ComfyUI folder, and how to wire one into a text-to-image workflow. Includes the strength dial, stacking multiple LoRAs, and the trigger-word habit that catches most beginners off guard."
pubDate: 2026-05-20
lang: en
category: workflow-extensions
heroImage: ./_assets/cover-lora.png
tags: ["lora", "fine-tuning", "workflow", "stable-diffusion", "tutorial"]
---

A LoRA (Low-Rank Adaptation) is a small file that nudges a base diffusion model toward a specific style, character, or concept without retraining the whole model. A typical LoRA is 50–200 MB. A full SDXL checkpoint is 7 GB. That ratio is why LoRAs are everywhere — they're cheap to train, cheap to share, and you can stack them.

This guide assumes you already have a working text-to-image workflow. If not, build one first using the [first workflow guide](/blog/your-first-comfyui-workflow/). Once that runs, adding a LoRA is one more node.

## What a LoRA actually does

A diffusion model is a stack of weight matrices. Training a LoRA produces a much smaller pair of matrices for each layer. At inference time, those small matrices are multiplied together and added to the base weights. The model behaves like a slightly different model — one that's been pulled toward whatever the LoRA was trained on.

Practical consequences:

- **You don't replace the base model.** LoRAs ride on top. A character LoRA trained on SD 1.5 needs an SD 1.5 checkpoint loaded.
- **The base matters.** A LoRA trained on `sd-v1-5` will behave oddly on `realistic-vision-v6` even though both are SD 1.5. Closer base = better results.
- **You can stack them.** Two LoRAs at 0.7 strength each is normal. Four at full strength tends to fight itself.

## Where LoRA files go

Drop them into:

```
ComfyUI/models/loras/
```

Subfolders are allowed. Most users organize by source or type:

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

After adding files, hit the refresh button (top right of ComfyUI) — the dropdown reads the folder fresh. No restart needed.

## Where to download LoRAs

Two main hubs:

- **Civitai** — civitai.com. The biggest collection. Quality varies wildly. Filter by base model and download count.
- **Hugging Face** — huggingface.co. Smaller selection but generally cleaner provenance. Search "lora sdxl" or "lora sd1.5".

A LoRA listing always tells you the **base model**. SD 1.5, SDXL, FLUX, Pony, Illustrious — these are not interchangeable. Download a LoRA matching the checkpoint you load in `Load Checkpoint`.

A good listing also includes:

- A few example images with the prompts that produced them
- The **trigger word** — a token you must include in your prompt to activate the LoRA
- A recommended strength range (often 0.6–1.0)

If a listing has no trigger word and no example prompts, it's a bad listing. Skip it.

## The Load LoRA node

Search `Load LoRA` in the node menu. The node has:

**Inputs (left side):**
- `model` (purple) — the MODEL you want to modify
- `clip` (yellow) — the CLIP you want to modify

**Outputs (right side):**
- `MODEL` — the modified MODEL
- `CLIP` — the modified CLIP

**Widgets:**
- `lora_name` — dropdown listing files in `models/loras/`
- `strength_model` — how strongly the LoRA affects the diffusion model itself (typical: 0.6–1.0)
- `strength_clip` — how strongly the LoRA affects the text encoder (typical: same as strength_model)

The node sits *between* `Load Checkpoint` and the rest of your graph, intercepting both MODEL and CLIP.

## Wiring it in

Take your working text-to-image graph. Find the wires going from `Load Checkpoint`:

- MODEL → KSampler
- CLIP → both `CLIP Text Encode` nodes (positive + negative)
- VAE → VAE Decode

Don't touch the VAE wire — LoRAs don't affect the VAE. But intercept the MODEL and CLIP wires:

1. Add a `Load LoRA` node between `Load Checkpoint` and the rest.
2. Disconnect the MODEL wire from `Load Checkpoint` to KSampler.
3. Connect: `Load Checkpoint`.MODEL → `Load LoRA`.model → `Load LoRA`.MODEL → KSampler.model
4. Disconnect the CLIP wires.
5. Connect: `Load Checkpoint`.CLIP → `Load LoRA`.clip → `Load LoRA`.CLIP → both text encoders.

That's it. Pick a LoRA from the dropdown, set strengths to 1.0 to start.

## The trigger word habit

This is where most beginners trip up. Many LoRAs need a specific token in the positive prompt to activate. The token is set during training — without it, the LoRA's effect is partial or invisible.

Examples (made up, but representative):

```
LoRA: aragorn-sdxl.safetensors
Trigger: aragorn-strider
Use it like: "portrait of aragorn-strider in a forest, cinematic lighting"
```

```
LoRA: pixel-art-xl.safetensors
Trigger: pixel art
Use it like: "pixel art of a fox sitting on a moss-covered rock"
```

Always check the LoRA's listing for the trigger word. If you put the LoRA in the graph at strength 1.0 and the output looks normal — no trigger word, that's why.

Some LoRAs are "always on" and don't need a trigger. The listing will tell you.

## Strength tuning

Three numbers, three different effects:

| strength_model | strength_clip | Behavior |
|----------------|---------------|----------|
| 1.0            | 1.0           | Full effect, default starting point |
| 0.6            | 0.6           | Subtle. Good for blending into base style. |
| 1.2            | 1.0           | Strong on visuals, normal prompt response. Risk: can cook the image. |
| 1.0            | 0.0           | Visual style applied, but prompt encoding stays clean. Useful for tricky combinations. |
| 0.0            | 0.0           | LoRA disabled (same as not having the node) |

For a first run, 1.0/1.0. If results are too strong (faces deformed, colors blown out), drop to 0.7. If too weak, try 1.1 — but going much above 1.2 usually breaks generation.

`strength_clip` matters more than people realize. If a character LoRA is contaminating your prompt understanding (the model "forgets" what blue means), drop `strength_clip` toward 0.5 while keeping `strength_model` at 1.0.

## Stacking multiple LoRAs

To use two LoRAs at once, chain `Load LoRA` nodes:

```
Load Checkpoint → Load LoRA (style) → Load LoRA (character) → KSampler
```

Each node modifies the MODEL and CLIP it receives, then passes them on. Order matters less than total strength.

Rule of thumb for stacking: **the sum of strengths should stay around 1.0–1.5**. Two LoRAs at 0.7 each is fine. Three at 1.0 each almost always produces garbage. The model has limited "headroom" before competing fine-tunes start fighting.

If you stack a style LoRA + a character LoRA:
- Use the character LoRA's trigger word in the prompt
- Use the style LoRA's trigger word too if it has one
- Start both at 0.7 strength, tune from there

## Common failures

### Result looks identical with and without the LoRA

- Trigger word missing from the prompt. Most common cause.
- Wrong base model. SD 1.5 LoRA on SDXL checkpoint = no effect or noise.
- `strength_model` is 0.0. Check the slider didn't get reset.

### Output is over-saturated, distorted, or "fried"

- Strength too high. Drop to 0.7 or 0.6.
- Stacking too many LoRAs. Disable all but one and re-test.
- Some LoRAs are over-trained — try the same LoRA at 0.5 and see if quality jumps.

### Faces are mangled when you weren't even asking for faces

- A character LoRA at 1.0 is biasing every face toward its training subject.
- Drop `strength_clip` to 0.4–0.5, keep `strength_model` at 1.0.

### "LoRA not found" / dropdown empty

- File extension wrong. ComfyUI accepts `.safetensors` and `.ckpt`. Anything else (`.pt`, `.bin`) needs to be renamed or converted.
- File in wrong folder. Must be under `models/loras/`, not `models/checkpoints/`.
- Forgot the refresh button. Top right of the UI.

### Color/style applied but the character is wrong

- The LoRA is style-only, not a character LoRA. Use a separate character LoRA, or describe the character in the prompt.

## LoRAs vs. checkpoints vs. embeddings

A quick mental map of the three things you might download:

| Type | Size | Where it goes | What it does |
|------|------|---------------|--------------|
| Checkpoint | 2–24 GB | `models/checkpoints/` | Whole model. Replaces the diffusion brain. |
| LoRA | 50–500 MB | `models/loras/` | Patches the model. Style/character/concept. |
| Embedding | 5–500 KB | `models/embeddings/` | Text-side only. A new "word" the model knows. |

LoRAs are the middle ground — small enough to download casually, expressive enough to actually change generations. Most workflows you'll see online use one or two LoRAs plus the base checkpoint.

## What's next

You can now apply any character or style LoRA to your base text-to-image workflow. Two natural next directions:

- **ControlNet** — control composition with depth maps, edge maps, or pose skeletons. Stacks cleanly with LoRAs.
- **Hires Fix** — render at low resolution, then upscale-and-refine for sharper detail without burning VRAM.

Each gets its own guide.
