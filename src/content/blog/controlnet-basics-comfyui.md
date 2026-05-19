---
title: "ControlNet Basics in ComfyUI: Composition Control with Pose, Depth, and Edges"
description: "How ControlNet steers a Stable Diffusion generation toward a specific pose, depth layout, or line drawing. Covers preprocessors, the Apply ControlNet node, model selection, and how to combine ControlNet with LoRAs."
pubDate: 2026-05-20
lang: en
tags: ["controlnet", "composition", "workflow", "stable-diffusion", "tutorial"]
---

A plain text-to-image workflow gives you control over *what* is in the image (subject, style, mood) but very little control over *where* things are. The figure stands somewhere, the building leans some direction, the camera frames the way the model felt like framing.

ControlNet fixes that. You give it a reference — a pose skeleton, a depth map, a Canny edge drawing — and the model is steered to match that structure while still respecting your prompt for content and style.

This guide assumes you already have a working text-to-image workflow. If not, start with [your first workflow](/blog/your-first-comfyui-workflow/). LoRA understanding ([LoRA basics](/blog/lora-basics-comfyui/)) helps but isn't required.

## What ControlNet actually is

ControlNet is a separate neural network trained alongside a base diffusion model. At inference time it takes a "control image" — usually some kind of structural map — and injects guidance into the diffusion process so the output matches that structure.

There's not one ControlNet. There are many, each trained on a specific type of control:

| Type | What it controls | Typical use |
|------|------------------|-------------|
| OpenPose | Human body pose (skeleton) | Posing characters precisely |
| Depth | Depth map (near/far) | Preserving 3D layout |
| Canny | Edge lines | Following an existing line drawing or photo outline |
| Lineart | Line art | Coloring sketches, manga panels |
| Scribble | Loose scribbles | Sketching layouts roughly |
| MLSD | Straight lines | Architecture, interiors |
| Tile | Tiled detail injection | Upscaling with structure preservation |
| SoftEdge | Soft outlines (HED) | Like Canny but more forgiving |

You pick the type that matches what you want to control. Posing characters? OpenPose. Recreating the layout of a reference photo? Depth or Canny.

## How a ControlNet workflow looks

You add three things to a basic text-to-image graph:

1. A **control image** — the input that defines the structure
2. A **preprocessor** node — converts your raw image (a photo, a sketch) into the format the ControlNet expects (a pose skeleton, a depth map, an edge map)
3. An **Apply ControlNet** node — feeds the preprocessed image plus a ControlNet model into the conditioning so it influences sampling

The data flow:

```
Load Image ─→ Preprocessor ─→ control image
                                   │
Load ControlNet Model ─────────────┤
                                   ▼
Positive CONDITIONING ─→ Apply ControlNet ─→ KSampler
```

The KSampler still gets MODEL, positive CONDITIONING, negative CONDITIONING, and a latent like before — but the positive CONDITIONING is now augmented with structural control.

## Setting up the model files

ControlNet models live in:

```
ComfyUI/models/controlnet/
```

Each control type has its own model file. Naming convention varies but you'll see files like:

```
control_v11p_sd15_openpose.pth
control_v11p_sd15_canny.pth
control_v11p_sd15_depth.pth
diffusers_xl_canny_full.safetensors
diffusers_xl_depth_full.safetensors
```

`sd15` means trained for SD 1.5, `xl` means SDXL. **They are not interchangeable.** A SD 1.5 ControlNet on an SDXL checkpoint just won't work.

Where to download:

- For SD 1.5: lllyasviel/ControlNet-v1-1 on Hugging Face — the original, comprehensive set
- For SDXL: diffusers/controlnet-canny-sdxl-1.0 and similar Hugging Face repos
- Civitai also hosts community ControlNet retrains

You also need preprocessor models. The most common installer is **ComfyUI-Manager** — it has a ControlNet auxiliary preprocessors node pack that handles preprocessor models automatically. Without that pack, you'd be downloading individual preprocessor weights manually.

## The minimum nodes you need

Search and add these in ComfyUI:

- `Load Image` — loads your reference image
- One of the preprocessor nodes (e.g. `OpenPose Pose`, `Canny Edge`, `Zoe Depth Map`) — these come from ComfyUI-Manager's auxiliary preprocessors
- `Load ControlNet Model` — picks a `.pth` or `.safetensors` from `models/controlnet/`
- `Apply ControlNet` (or `Apply ControlNet (Advanced)`)

## Wiring an OpenPose example

You have a photo of someone in a specific pose. You want to generate a fantasy character in the same pose.

1. **Load Image** — drag your reference photo onto the canvas, or use the file picker.
2. **Preprocessor** — add `OpenPose Pose`. Connect Load Image's IMAGE → preprocessor's image input. The preprocessor's output is the pose skeleton (a black image with colored stick-figure lines).
3. **Load ControlNet Model** — pick the OpenPose model matching your base (SD 1.5 → openpose-sd15, SDXL → openpose-sdxl).
4. **Apply ControlNet** — three inputs:
   - `positive` ← positive CONDITIONING from your text encode node
   - `control_net` ← from Load ControlNet Model
   - `image` ← preprocessor output
5. Apply ControlNet outputs a new positive CONDITIONING. Wire it to KSampler's `positive` input.

The negative CONDITIONING bypasses ControlNet — wire negative directly from text encode to KSampler.

## The strength dial

Apply ControlNet has a `strength` widget (0.0–2.0). What it does:

- **0.0** — ControlNet effectively off
- **0.5** — Loose adherence. Good for poses you want to hint at
- **1.0** — Default. Strong adherence to the structure
- **1.5+** — Will sometimes override the prompt entirely if they conflict

For OpenPose, 1.0 is fine. For Canny on detailed line art, 0.7 often produces better results — full strength sometimes traces the lines too literally and stiffens the image.

The Advanced node also exposes `start_percent` and `end_percent` — what range of the diffusion timesteps the control applies during. Default is 0–1 (full range). Setting `end_percent` to 0.5 means ControlNet only guides the first half, and the model freelances the rest. This helps when you want the structure but not the exact details.

## Picking the right control type

A quick decision tree:

- Reference is a person and you want **the same body pose**? → OpenPose
- Reference is a 3D scene or photo and you want **the same depth layout**? → Depth (Zoe or MiDaS)
- Reference is a sketch / line drawing? → Lineart or Scribble
- Reference is a finished image and you want a **pixel-accurate redraw with style change**? → Canny at strength 0.7
- Reference is architecture / interior with **straight lines**? → MLSD
- You want the original colors and large shapes preserved? → Tile (used with low denoise)

Mixing two ControlNets is normal. OpenPose + Depth in series gives you both pose and 3D layout. Add a second `Apply ControlNet` after the first, feed the previous CONDITIONING in.

## ControlNet + LoRA stack together

ControlNet operates on conditioning. LoRA operates on the model + clip. They don't fight. A common stack:

```
Load Checkpoint ─→ Load LoRA ─→ KSampler.model
                  └─→ Load LoRA.CLIP ─→ Text Encode (positive) ─→ Apply ControlNet ─→ KSampler.positive
```

Use a character LoRA + OpenPose ControlNet to put a specific character in a specific pose. Use a style LoRA + Depth ControlNet to render a 3D scene in a specific painting style.

Strength budget still applies: ControlNet at 1.0 + 2 LoRAs at 0.7 each is about the upper limit. Pushing all three to max usually breaks something.

## Common failures

### Output ignores the control image

- Wrong base model (SD 1.5 ControlNet with SDXL checkpoint, or vice versa)
- Strength is 0
- Apply ControlNet is wired wrong — its output must reach KSampler's positive, not be left dangling

### Output rigidly traces the control even when it shouldn't

- Strength too high. Drop to 0.7
- Or set `end_percent` to 0.5 so control fades after midway

### Preprocessor node not in the menu

- ComfyUI-Manager isn't installed, or the auxiliary preprocessors pack isn't installed via Manager. Open Manager → Install Custom Nodes → search "controlnet aux" → install
- Restart ComfyUI after installing

### Preprocessor outputs a black image

- Reference image is wrong format. Convert to standard RGB
- For OpenPose: no detectable human in the input. The skeleton stays empty.

### Out of memory after adding ControlNet

- ControlNet eats 1–4 GB extra VRAM. SDXL + ControlNet on 8 GB is tight
- Lower resolution to 768 first, then climb back up if it fits
- Use `--lowvram` flag

## When NOT to use ControlNet

ControlNet adds complexity. Skip it if:

- You just want **prompt-driven** generation with no structural reference. ControlNet is overkill.
- You're starting from a description, not a reference image. ControlNet needs *something* to control from.
- You only want vague composition guidance. Prompt engineering ("low angle shot", "medium close-up") gets you 70% of the way without setup.

ControlNet is for when prompt language alone can't convey what you mean. "Person sitting cross-legged with arms raised over their head" is a fight. A pose reference is two seconds.

## Summary

- ControlNet steers structure (pose, depth, edges) while text steers content (subject, style)
- Pick the control type that matches what you want to lock down
- Need: preprocessor + ControlNet model file matching your base + Apply ControlNet node
- Strength 1.0 is the default; 0.7 for delicate references; `end_percent: 0.5` to soften
- Stacks cleanly with LoRAs, just watch the total strength budget

## What's next

ControlNet is one of three big workflow expansions you'll want. The other two:

- **Hires Fix** — generate at low resolution, refine at high resolution. Better detail without burning VRAM
- **Image-to-Image** — use a real image as the starting latent. Style transfer, photo editing, sketch-to-finished-art

Both have their own guides.
