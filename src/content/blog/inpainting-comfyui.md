---
title: "Inpainting in ComfyUI: Selectively Regenerate Hands, Faces, and Backgrounds"
description: "Mask a region of an image and let the model regenerate just that region while keeping the rest untouched. Covers the inpainting workflow, mask blur, denoise tuning, and dedicated inpainting checkpoints."
pubDate: 2026-05-22
lang: en
category: workflow-extensions
heroImage: ./_assets/cover-inpainting.png
tags: ["inpainting", "mask", "workflow", "stable-diffusion", "tutorial"]
---

You generated a great image but the hands look like spaghetti. Or the face is fine but the background has weird artifacts. Re-rolling the whole image risks losing the parts that worked. Inpainting fixes this — you mask the broken region, the model regenerates only that region, and everything else stays bit-for-bit identical.

This is the fourth major workflow expansion alongside [LoRA](/blog/lora-basics-comfyui/), [ControlNet](/blog/controlnet-basics-comfyui/), and [img2img](/blog/img2img-comfyui/). It's also the trickiest to tune well, but the basic graph is small.

## What inpainting does

Take an existing image, paint a black-and-white mask over the part you want to redo, give the model a prompt describing what should be there, run sampling. The model only changes pixels inside the mask. Pixels outside the mask are preserved exactly.

Use cases:

- **Fix bad hands or faces** without re-rolling the whole image
- **Remove or replace objects** (a person from a landscape, a logo from a product shot)
- **Change small details** (eye color, hair color, clothing color)
- **Extend an image** (paint outwards into masked transparent areas)
- **Iterate locally** when 95% of an image is good

## The minimum nodes

Add to a basic graph:

- `Load Image` — your input image
- `Load Image (as Mask)` — your mask image (or use the built-in mask editor)
- `VAE Encode (for Inpainting)` — encodes input + mask into a special inpaint latent
- A second `KSampler` configured with mask awareness

Replace the empty latent + KSampler from the text-to-image graph. Everything else (model, conditioning, VAE Decode, Save Image) stays the same.

## Two ways to make a mask

### Method 1: ComfyUI's built-in mask editor

Right-click any `Load Image` node showing your input → `Open in MaskEditor`. A canvas opens. Paint with the brush over what you want to regenerate. Save. The mask is now bound to that image.

This is the fastest way for one-off masks. It's not great for precise edges.

### Method 2: External mask file

Make a black-and-white PNG in any image editor. White = regenerate, black = preserve. Save as a separate file, load with `Load Image (as Mask)`.

This is better for surgical masks (precise edges, multiple separate regions).

Mask color convention:
- **White / 255**: regenerate this pixel
- **Black / 0**: keep original
- **Gray**: blend at corresponding strength

## Wiring the workflow

Starting from a working text-to-image graph:

1. **Add Load Image.** Pick your input.
2. **Mask the image.** Use MaskEditor (right-click → Open in MaskEditor) for a quick mask, or load a separate mask file.
3. **Replace Empty Latent Image with VAE Encode (for Inpainting).** Inputs:
   - `pixels` ← Load Image's IMAGE
   - `vae` ← Load Checkpoint's VAE
   - `mask` ← Load Image's MASK (the mask channel from the same node, exposed as an output)
4. **Wire VAE Encode (for Inpainting)'s LATENT** to KSampler's `latent_image`.
5. Configure KSampler:
   - `denoise` 1.0 (full noise inside the mask — the model rebuilds from scratch)
   - Other settings same as text-to-image
6. **VAE Decode** and **Save Image** as before.

That's the basic graph. The mask is automatically respected by the KSampler when the input latent comes from `VAE Encode (for Inpainting)`.

## Inpainting checkpoints vs regular checkpoints

You have two choices for the model:

| Type | Behavior |
|------|----------|
| Regular checkpoint | Works, but the mask edge is sometimes visible. Fine for 80% of cases. |
| **Inpainting checkpoint** (suffix `-inpainting` or `-inpaint`) | Trained specifically with mask conditioning. Cleaner edges, better blending. |

For SD 1.5: download `realistic-vision-inpainting`, `dreamshaper-inpainting`, etc. They're versions of regular checkpoints retrained for inpaint. Place in `models/checkpoints/` like any other.

For SDXL: dedicated inpainting checkpoints are less common — most SDXL inpainting works fine with regular checkpoints.

For FLUX: use FLUX.1-fill-dev — Black Forest's official inpainting variant.

If you're going to do a lot of inpainting, downloading a dedicated inpainting checkpoint is worth it. For one-off fixes, your existing checkpoint is usually fine.

## Tuning the mask

### Mask blur

Hard mask edges produce visible seams. The fix: blur the mask before encoding.

Add `MaskBlur` (from custom node packs) or `GaussianBlur` between `Load Image (as Mask)` and `VAE Encode (for Inpainting)`. Blur radius 4-12 pixels softens the transition.

For circular masks (faces, hands), blur radius 8-15 pixels.
For straight-edge masks (a sky region, a wall), blur 4-8 pixels.

### Denoise (different role here)

Unlike img2img, denoise inside the mask should usually stay at **1.0**. The mask already isolates the changed region — you want a full regeneration there. Lower denoise creates ghost echoes of the original image inside the mask.

Exception: if you're doing a *subtle* change to a region (slight color shift), drop denoise to 0.6-0.7.

### Mask grow / shrink

Sometimes your hand-painted mask is slightly too small — the model regenerates *just* the broken hand but the wrist edge still looks bad. Use `GrowMask` to expand by 4-8 pixels. The expansion gives the model context to blend.

If the mask is too generous and bleeds into good areas, `ShrinkMask` does the reverse.

## Prompt strategy

The prompt should describe **what should be in the masked region**, not the whole image. The model only sees the masked area as the generation target.

Bad prompt: `"a portrait of a young woman, smiling, sunlit forest"` (describes the whole picture, wastes attention)

Good prompt: `"a hand holding an apple, fingers clearly defined, photorealistic"` (describes only what you're inpainting)

Negative prompt should still target the failure modes (`deformed, blurry, extra fingers`).

## Outpainting (extending an image)

Outpainting is just inpainting where the mask is the canvas extension area.

Workflow:
1. Take your original image. Use `ImagePadForOutpaint` to extend the canvas with a transparent (masked) border on the desired side(s).
2. Feed result into `VAE Encode (for Inpainting)` — the padded transparent border *is* the mask.
3. Run KSampler. The model fills in the new area, blending with the visible original.

Caveat: outpainting more than 50% in one pass usually fails. The model loses context. Expand in 25-50% increments and rerun.

## Common failures

### Edge of the mask is visible as a hard seam

- No mask blur. Add `MaskBlur` with radius 6-10.
- Or use a dedicated inpainting checkpoint.

### Inpainted region looks completely different from the rest of the image

- denoise too high (you're already at 1.0 — that's expected, this is feature not bug)
- The prompt is describing something inconsistent with the surrounding image. If the image is dim and you prompt "bright daylight", expect a clash.
- Use ControlNet (Depth or Canny on the original image) to keep structure consistent.

### Inpainted hand still has 7 fingers

- Hand inpainting is genuinely hard. Try:
  - Increase mask area to include more of the wrist/forearm
  - Use a hand-fix LoRA (search Civitai for "hand")
  - Try multiple seeds — sometimes only 1 in 5 produces good hands
  - For SDXL, Hands-XL LoRA helps a lot

### Output is a duplicate of the original (no change)

- Mask is empty or all-black. Check the mask actually has white pixels.
- Mask wired to wrong node. The mask must reach `VAE Encode (for Inpainting)`'s `mask` input, not just dangle.

### "Mask size doesn't match image size"

- Mask dimensions ≠ image dimensions. Resize mask to match. ComfyUI doesn't auto-resize.

### OOM on inpaint

- Inpainting at 2048×2048 needs more VRAM than text-to-image at the same size. Drop to 1024 or use `--lowvram`.

## Inpainting + ControlNet

Common combo: inpaint a person's hand using a hand pose from ControlNet OpenPose.

1. Generate a hand pose reference (a separate stick-figure or a real photo of the desired pose).
2. Run OpenPose preprocessor on it.
3. Feed the OpenPose output into `Apply ControlNet` with the inpainting prompt.
4. The masked region gets regenerated *and* matches the reference pose.

This dramatically improves hand inpainting success rate.

## Inpainting + LoRA

LoRAs work the same. A character LoRA + face inpaint = put a specific character's face on an existing body. A "perfect hands" LoRA + hand inpaint = much higher success rate on hand fixes.

## Summary

- Inpainting = mask a region, regenerate only that region
- Wire: Load Image + mask + VAE Encode (for Inpainting) + KSampler with denoise 1.0
- Use a dedicated inpainting checkpoint for cleaner edges
- Always blur the mask 6-10 pixels to avoid hard seams
- Prompt should describe what's in the mask, not the whole image
- For hands and faces, combine with ControlNet pose reference

## What's next

You've now seen the five main workflow patterns: text-to-image, LoRA, ControlNet, Hires Fix, img2img, and inpainting. The next category to explore is **conditioning the model with reference images instead of LoRAs** — that's IP-Adapter, which deserves its own guide.
