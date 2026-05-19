---
title: "LoRA in ComfyUI: How to Apply Styles, Characters, and Concepts"
description: "What LoRAs are, where to find them, and exactly how to wire them into a ComfyUI workflow. Includes how to stack multiple LoRAs, tune their strength, and avoid the most common mistakes."
pubDate: 2026-05-20
lang: en
tags: ["lora", "fine-tuning", "workflow", "stable-diffusion", "tutorial"]
---

A LoRA is the cheapest way to bend a base model toward something specific. Want everything you generate to look like an oil painting? Use an oil-painting LoRA. Want a specific character to appear? Use a character LoRA. Want a particular pose, outfit, or compositional style? There's probably a LoRA for that.

This guide explains what a LoRA actually is, how to install one, and how to wire it into a ComfyUI workflow. By the end you'll have a workflow that loads a base model, applies a LoRA, and generates an image in that style.

Prerequisites: a working ComfyUI install (see the [installation guide](/blog/comfyui-installation-guide/)) and the basic text-to-image workflow (see [Your First ComfyUI Workflow](/blog/your-first-comfyui-workflow/)).

## What a LoRA is, in one paragraph

A LoRA (Low-Rank Adaptation) is a small file — usually 50 to 300 MB — that contains a "delta" you apply on top of a base model. Instead of retraining the entire 4–7 GB checkpoint to learn a new style or character, someone fine-tunes only a tiny number of additional weights. When you apply the LoRA at generation time, those small weights are added to the corresponding layers of the base model, nudging its output in the direction the LoRA was trained on.

Think of the base model as a 3D printer that knows how to print general "things". A LoRA is a small attachment that biases what comes out — same machine, different flavor. Remove the attachment, the printer is back to normal.

## Why use a LoRA instead of a different checkpoint

A checkpoint is the whole brain. A LoRA is a personality patch.

You'd switch checkpoints when the base style of the model needs to change entirely (anime vs photoreal vs painterly). You'd add a LoRA when you want to keep the base style but inject something specific — a character, a clothing style, a lighting mood, a concept the base model doesn't know.

Practical benefits:

- **Small files.** 200 MB vs 7 GB.
- **Stackable.** Apply two or three LoRAs at once, blend their strengths.
- **Switchable.** Same workflow, swap LoRAs to test different styles.
- **Trainable.** With a decent GPU you can train your own LoRA on 20–30 reference images in a few hours. Training a full checkpoint takes orders of magnitude more compute.

## Where to get LoRAs

The two main hubs:

- **[Civitai](https://civitai.com/)** — the largest community library. Filter by Base Model (SD 1.5, SDXL, FLUX, Pony) so you don't accidentally download an SDXL LoRA for an SD 1.5 model.
- **[Hugging Face](https://huggingface.co/)** — more model-research-oriented, but many trainers also publish here. Search with "lora" in the query.

When you download a LoRA, **check three things on its page**:

1. **Base model** — the LoRA must match your checkpoint family. SDXL LoRAs do not work on SD 1.5, FLUX LoRAs don't work on SDXL, and so on.
2. **Trigger words** — many LoRAs require specific keywords in your prompt to activate properly. The page will list them, e.g. "use trigger word `oil painting style`". Without the trigger, the LoRA may have no effect or a weak one.
3. **Recommended strength** — usually a number between 0.5 and 1.0. The author tested specific values; start there.

## Installing a LoRA

LoRAs are plain files, just drop them in the right folder.

1. Download the `.safetensors` file. (Avoid `.ckpt` for LoRAs when there's a `.safetensors` alternative — safer format.)
2. Move it to `ComfyUI/models/loras/`.
3. Refresh the ComfyUI page in your browser (or click the refresh icon in the menu).

The LoRA now appears in the dropdown of any `Load LoRA` node.

You can organize the folder with subfolders if you want: `models/loras/style/`, `models/loras/character/`, etc. ComfyUI will list them in nested groups in the dropdown.

## Adding a LoRA to your workflow

Start with the basic seven-node workflow from the previous guide. Now you'll insert one extra node between `Load Checkpoint` and the rest of the graph.

### Step 1: Add the Load LoRA node

Double-click the canvas → search `Load LoRA` → add it.

`Load LoRA` has:

- Two inputs: **model** (purple) and **clip** (yellow)
- Two outputs: **MODEL** and **CLIP**
- Three widgets: **lora_name**, **strength_model**, **strength_clip**

You're going to splice it into the existing wires from `Load Checkpoint`.

### Step 2: Rewire MODEL and CLIP through the LoRA

Before the LoRA, your wires went:

```
Load Checkpoint ─ MODEL ─→ KSampler
Load Checkpoint ─ CLIP  ─→ CLIP Text Encode (positive)
Load Checkpoint ─ CLIP  ─→ CLIP Text Encode (negative)
```

After adding the LoRA, they go:

```
Load Checkpoint ─ MODEL ─→ Load LoRA ─ MODEL ─→ KSampler
Load Checkpoint ─ CLIP  ─→ Load LoRA ─ CLIP  ─→ CLIP Text Encode (positive)
                                          └──→ CLIP Text Encode (negative)
```

In other words: delete the direct wires from `Load Checkpoint` to `KSampler` and the prompt encoders. Then connect:

1. `Load Checkpoint` → MODEL → `Load LoRA` → model
2. `Load Checkpoint` → CLIP → `Load LoRA` → clip
3. `Load LoRA` → MODEL → `KSampler` → model
4. `Load LoRA` → CLIP → both `CLIP Text Encode` nodes (one output can fan out)

VAE doesn't go through the LoRA. Leave that wire alone — `Load Checkpoint` → VAE → `VAE Decode`.

### Step 3: Configure the LoRA

In `Load LoRA`:

- **lora_name** — pick the LoRA you placed in `models/loras/`
- **strength_model** — start at the LoRA author's recommended value (often `1.0`, sometimes `0.7`–`0.8`)
- **strength_clip** — usually the same as `strength_model`. Set it equal unless the LoRA author says otherwise.

### Step 4: Use the trigger words

Open your **positive prompt** and add the LoRA's trigger words. For example, if the LoRA card on Civitai says "use `oil painting style`", make your prompt:

```
oil painting style, a fox sitting on a moss-covered rock in a forest, golden hour, sharp focus
```

Without the trigger words, many LoRAs barely activate.

### Step 5: Generate

Click `Queue Prompt`. The first generation reloads the model with the LoRA applied — slightly slower than usual.

Compare the result to the same prompt without the LoRA (bypass `Load LoRA` by routing the wires around it, or set both strengths to 0). The difference shows you exactly what the LoRA is contributing.

## Strength tuning

`strength_model` and `strength_clip` go from -2.0 to 2.0 in most ComfyUI versions, but the useful range is usually 0.0 to 1.2.

- **0.0** — LoRA does nothing
- **0.5** — gentle nudge in the LoRA's direction
- **1.0** — full effect, the value the author tested at
- **1.2+** — overcooked, often produces artifacts (oversaturated, deformed, repeating patterns)
- **negative values** — push *away* from what the LoRA was trained on (rarely useful, sometimes used to remove a style baked into the base model)

When in doubt, try `0.7`, `0.85`, and `1.0` with the same seed and prompt, and see which one looks best.

### What strength_clip actually changes

`strength_model` adjusts the LoRA's effect on the diffusion model itself. `strength_clip` adjusts its effect on the text encoder. Most LoRAs are trained against both, so set them equal.

A few LoRAs (especially older "concept" LoRAs) prefer `strength_clip = 0` because their CLIP changes were destructive. The LoRA's Civitai page will tell you when this matters.

## Stacking multiple LoRAs

You can apply two or three LoRAs in series. Just chain `Load LoRA` nodes:

```
Load Checkpoint ─ MODEL ─→ Load LoRA #1 ─ MODEL ─→ Load LoRA #2 ─ MODEL ─→ KSampler
                ─ CLIP  ─→ Load LoRA #1 ─ CLIP  ─→ Load LoRA #2 ─ CLIP  ─→ Encoders
```

Each LoRA's effect adds on top of the previous one. Some practical notes:

- **Two is usually fine, three is the upper limit.** Stacking more than three rarely improves results — the LoRAs start to fight each other and the output looks muddy.
- **Lower individual strengths when stacking.** If two LoRAs both want strength `1.0`, set them to `0.6` and `0.5`. The combined effect should be roughly equivalent to one full-strength LoRA.
- **One style + one character + one concept** is a useful pattern. Avoid stacking two strong style LoRAs — they tend to cancel each other out.

## Common mistakes

### "I see no difference"

Three usual causes:

1. The LoRA is for a different base model (SDXL LoRA on an SD 1.5 checkpoint, etc.). The wires connect, ComfyUI doesn't error, but nothing happens.
2. You forgot the trigger words.
3. Both strengths are at 0, or you bypassed the LoRA in the wiring.

### Output is oversaturated, deformed, repeating

LoRA strength too high, or stacking too many LoRAs. Lower `strength_model` to 0.6–0.8.

### Out of memory after adding a LoRA

LoRAs themselves don't use much VRAM, but applying them duplicates some buffers during the first run. If you were already near the edge on VRAM, this can tip you over. Add `--lowvram` to your launch command, or generate at a lower resolution first.

### Background characters look weird

Character LoRAs sometimes leak into all faces in the image, not just the main subject. This is a training-data artifact, not something you can fix in ComfyUI. If it bothers you, generate a single subject and avoid prompting for crowds.

### LoRA changes the lighting / colors when you only wanted the character

Character LoRAs trained on a specific small dataset often pick up the dataset's lighting style as a side effect. Lower the strength to 0.6–0.7, or look for an alternative LoRA trained on a more diverse set of references.

## Tips that save time

- **Save your LoRA-augmented workflow as a JSON file.** Drag it back onto the canvas later instead of rebuilding it.
- **Drop a generated PNG back onto the canvas** to restore the exact LoRA setup that produced it. ComfyUI embeds the workflow in the metadata.
- **Bypass nodes with Ctrl+B** instead of disconnecting wires, when you want to A/B compare with and without the LoRA.
- **Read the LoRA's Civitai images.** Click any image, the prompt and settings used to generate it are usually visible. Copy them as a starting point, then adapt.

## What's next

You can now apply LoRAs cleanly. Two natural follow-ups:

- **Image-to-image with LoRAs** — same wiring, but replace `Empty Latent Image` with a real image and lower `denoise` to 0.5–0.7. Useful for restyling existing photos.
- **ControlNet** — for controlling the *composition* of the output (pose, edges, depth) instead of the style. ControlNet and LoRAs combine well.

Each of those gets its own guide.
