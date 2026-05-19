---
title: "LoRA Basics in ComfyUI: Adding Styles and Characters Without Retraining the Model"
description: "What a LoRA is, where to put the file, how to wire the Load LoRA node into a workflow, and how to combine multiple LoRAs without breaking your image. Concrete settings and the failure modes to watch for."
pubDate: 2026-05-19
lang: en
tags: ["lora", "fine-tuning", "stable-diffusion", "workflow", "fundamentals"]
---

A LoRA is a small file — usually 50 to 250 MB — that teaches a base model a new style, character, concept, or composition. You don't retrain the model. You just attach the LoRA at generation time and the model behaves differently.

LoRAs are the second most important thing to understand in Stable Diffusion after the base model itself. This guide covers what they are, how to install them, and how to wire them into the workflow you built in the [first workflow guide](/blog/your-first-comfyui-workflow/).

## What a LoRA actually is

The full name is **Low-Rank Adaptation**. The technical idea: a base diffusion model has billions of weights. Fine-tuning all of them on a new concept is expensive — full fine-tuning produces another multi-GB checkpoint and takes hours on a high-end GPU. LoRA training instead learns a small low-rank matrix that gets added to specific layers of the model at inference time. The math is cheap, the file is small, the result modifies behavior without touching the base.

You don't need to understand the math to use them. What you need to know:

- A LoRA is **paired with a base model**. A LoRA trained on SD 1.5 won't work correctly on SDXL or FLUX. Always check the base model on the LoRA's download page.
- A LoRA has a **strength** value, usually 0.0 to 1.0. Higher strength = stronger effect. Most LoRAs have a sweet spot around 0.6–0.9.
- A LoRA may have a **trigger word** the model expects in the prompt. Without it the LoRA still loads but barely activates.
- **Multiple LoRAs stack.** You can apply 2, 3, or more. Stacking too many degrades the image.

## Categories of LoRA

Most LoRAs fall into one of four categories. The category tells you what to expect.

| Category | What it does | Trigger word? | Typical strength |
|----------|-------------|---------------|------------------|
| Style | Anime style, oil painting, pixel art, etc. | Sometimes | 0.6–1.0 |
| Character | A specific person or fictional character | Usually yes | 0.7–1.0 |
| Concept | An object, pose, or visual effect (laser eyes, ice texture) | Sometimes | 0.5–1.0 |
| Slider | Adjustable axis (age, weight, detail, expression). Strength can go negative. | No | -2.0 to +2.0 |

CivitAI is the largest LoRA hub. The page for each LoRA lists base model, recommended strength, and trigger word. Read it before downloading.

## Step 1: Install a LoRA file

LoRAs go in `ComfyUI/models/loras/`. Drop the `.safetensors` (or older `.pt`/`.ckpt`) file there.

You can organize into subdirectories — `models/loras/style/`, `models/loras/character/`. ComfyUI shows the structure in the dropdown.

After adding a file, reload ComfyUI in the browser, or hit the refresh icon at the top of the UI. The new LoRA should appear in the `Load LoRA` node's dropdown.

## Step 2: Add Load LoRA to the workflow

Start from the workflow you built in the [first workflow guide](/blog/your-first-comfyui-workflow/). Open it (drag the JSON file or PNG onto the canvas).

Now insert a `Load LoRA` node between `Load Checkpoint` and the rest of the graph.

Double-click the canvas → search `Load LoRA` → add it.

`Load LoRA` has these connections:

**Inputs:**
- **model** — MODEL from `Load Checkpoint`
- **clip** — CLIP from `Load Checkpoint`

**Outputs:**
- **MODEL** — the model with LoRA applied
- **CLIP** — the CLIP with LoRA applied

**Widgets:**
- **lora_name** — dropdown of LoRAs in `models/loras/`
- **strength_model** — how strongly the LoRA modifies the diffusion model (default 1.0)
- **strength_clip** — how strongly the LoRA modifies the text encoder (default 1.0)

### Rewiring the connections

Before adding `Load LoRA`, your graph has:

```
Load Checkpoint --MODEL--> KSampler
Load Checkpoint --CLIP--> CLIPTextEncode (positive)
Load Checkpoint --CLIP--> CLIPTextEncode (negative)
```

After:

```
Load Checkpoint --MODEL--> Load LoRA --MODEL--> KSampler
Load Checkpoint --CLIP--> Load LoRA --CLIP--> CLIPTextEncode (positive)
                                            --> CLIPTextEncode (negative)
```

The LoRA wraps both the model wire and the CLIP wire. Skip the CLIP wire and trigger words won't work. Skip the model wire and the LoRA does nothing.

In ComfyUI:

1. Click the existing wire `Load Checkpoint` MODEL → `KSampler` model. Delete it.
2. Drag a new wire `Load Checkpoint` MODEL → `Load LoRA` model.
3. Drag `Load LoRA` MODEL → `KSampler` model.
4. Repeat for CLIP: delete the existing CLIP wire, route it through `Load LoRA`, then on to both `CLIPTextEncode` nodes.
5. The VAE wire is unchanged. LoRAs don't touch the VAE.

## Step 3: Set the LoRA and strength

Pick a LoRA from the dropdown.

Set both strengths to **0.8** as a starting point. Most LoRAs are calibrated to work well at 0.7–0.9.

If the LoRA's CivitAI page lists a recommended strength, use that. If it lists a trigger word, add it to your positive prompt. Example: a cyberpunk style LoRA might require `cyberpunk style` somewhere in the prompt.

Queue the prompt. Compare to the same prompt without the LoRA. The difference should be obvious.

## Reading what each strength does

`strength_model` and `strength_clip` modify different parts of the pipeline:

- **strength_model** affects the diffusion process. This is where most of the visual style change comes from. If your LoRA is a style or character, this is the dial you care about most.
- **strength_clip** affects how the text encoder interprets your prompt. Some LoRAs train new associations into CLIP — when you set strength_clip high, the model takes the trigger word more seriously.

For most LoRAs, keep both equal. If the LoRA produces the right look but ignores your prompt details, lower strength_clip. If it follows the prompt but doesn't quite get the style right, raise strength_model.

A pragmatic shortcut: set both to the same value, tune from there.

## Stacking multiple LoRAs

You apply two LoRAs by chaining `Load LoRA` nodes:

```
Load Checkpoint --MODEL--> Load LoRA #1 --MODEL--> Load LoRA #2 --MODEL--> KSampler
                --CLIP-->                CLIP-->                 CLIP-->  positive/negative
```

The second `Load LoRA` takes the first one's output as input. ComfyUI applies them in order.

Real-world combinations:

- **Style + character.** A "watercolor painting" style LoRA + a specific character LoRA. Strength 0.7 each.
- **Character + outfit/concept.** A character LoRA + a separate "in armor" or "wearing red dress" LoRA.
- **Two slider LoRAs.** Age slider at -1.0 + detail slider at +0.5.

The more LoRAs you stack, the more they fight each other. Three is usually safe. Four+ starts producing artifacts.

If two style LoRAs blend badly, lower both strengths to 0.5–0.6. Combined contribution is what matters; don't run two at full strength simultaneously.

## Where LoRAs go wrong

### "I added the LoRA but nothing changed"

Three usual causes:

1. **Trigger word missing.** Check the LoRA's CivitAI page. Add the trigger word to the positive prompt.
2. **Wrong base model.** A LoRA trained for SD 1.5 will load on SDXL but produce nothing useful. Check that `Load Checkpoint` and the LoRA are on the same base.
3. **Strength too low.** 0.0 means inactive. Raise to 0.8.

Confirm the LoRA actually applied: temporarily set strength to 1.5 (overcooked). The image should look obviously broken or stylized — that proves the LoRA is in the pipeline. Then dial back to 0.7–0.9.

### "The LoRA destroys the image at strength 1.0"

Common with character LoRAs that were over-trained. Drop strength to 0.6–0.7. Some popular LoRAs are documented as "always use at 0.5" on their CivitAI page — don't blindly use 1.0.

### "The character looks right but the style is gone"

Character LoRAs often pull style toward whatever the training data looked like. To preserve a specific aesthetic, layer a style LoRA on top with its own strength. Usually `character LoRA at 0.8 + style LoRA at 0.5` is a workable starting combo.

### "I get black or noisy output"

Either the LoRA file is corrupt, or it's the wrong format for your ComfyUI version. Re-download. If the issue persists, the LoRA may be in a non-standard format that needs an alternative loader (some Kohya outputs need `LoraLoaderModelOnly` or `Load LoRA (LBW)` from custom node packs).

### "Different LoRAs work alone but not stacked"

Two style LoRAs covering similar territory will fight. Try lowering the strength of each to 0.5. If they still don't combine, the styles are simply incompatible — pick one.

## Where to find LoRAs

- **CivitAI** — https://civitai.com — the main hub. Filter by base model (SD 1.5, SDXL, FLUX, etc.). Read the version notes on each LoRA, they often list strength and trigger word.
- **Hugging Face** — https://huggingface.co/models?other=lora — research and official releases. Less curated but good for technical LoRAs.

When you download from CivitAI, you get a `.safetensors`. Drop it in `models/loras/`, refresh ComfyUI, done.

## A practical first session

To get a feel for LoRAs, do this:

1. Pick one well-known SD 1.5 style LoRA from CivitAI — a watercolor or anime style with 1000+ likes.
2. Generate a baseline image without it. Save the seed.
3. Add `Load LoRA`, set strength 0.8. Generate with the same seed and prompt.
4. Compare side by side. The image should have the LoRA's signature style but the same composition (same seed, same denoising).
5. Sweep strength: 0.3, 0.5, 0.7, 1.0. Use the same seed each time. Watch how the image changes.

Twenty minutes of this teaches more about LoRAs than an hour of reading.

## What's next

LoRAs handle style and character. The next layer of control is **structure** — making the model produce an image with a specific pose, depth, or edge layout. That's ControlNet, and it's the topic of the next guide.
