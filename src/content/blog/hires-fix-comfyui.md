---
title: "Hires Fix in ComfyUI: Render Low, Refine High for Sharper Detail"
description: "How to generate at low resolution, then upscale and refine to a high-resolution final image without burning VRAM. The two-stage workflow that replaces A1111's one-click Hires fix in ComfyUI."
pubDate: 2026-05-21
lang: en
category: workflow-extensions
heroImage: ./_assets/cover-hires-fix.png
workflow:
  file: hires-fix.json
  title: Two-pass Hires Fix workflow
  note: Pass 1 at 512×512, Latent Upscale 1.5×, Pass 2 with denoise 0.5 at higher resolution. Same seed locks composition.
tags: ["hires-fix", "upscaling", "workflow", "stable-diffusion", "tutorial"]
---

If you've used Automatic1111 you've seen the Hires fix checkbox — generate at 512 or 1024, then automatically upscale to 2x with a second pass. ComfyUI doesn't have a checkbox, but it has the same capability split across a few nodes. Wiring it up yourself takes a minute and gives you more control over each stage.

This guide assumes you have a working text-to-image workflow ([first workflow](/blog/your-first-comfyui-workflow/)).

## Why Hires Fix exists

Diffusion models have a "native" resolution they were trained at — 512×512 for SD 1.5, 1024×1024 for SDXL. Generate way above native and you get tiling artifacts (the same face appearing twice in one image), OOM errors on smaller GPUs, and sometimes confused composition.

But you also want sharper details, finer textures, larger files. The trick is two passes:

1. Generate at native resolution. The model produces good composition.
2. Upscale the result to the target resolution. Run a *second* shorter denoise pass over it, just enough to add detail without changing the picture.

Memory cost stays low (one full pass at native + one short pass at target), composition stays clean, detail goes up.

## The pieces you need

Three additions to a basic graph:

- **Latent Upscale** — resizes the latent between the first and second sampler
- **Second KSampler** — runs the refinement pass at the higher resolution
- **VAE Decode** at the end (which you already have) — converts the final latent to pixels

Most people skip "Upscale Image" + "VAE Encode" because doing the upscale in latent space is faster and avoids a round trip through pixel space.

## Wiring the two-pass workflow

Start with a working text-to-image graph. Take the LATENT output from your existing KSampler — instead of feeding it straight to VAE Decode, route it through:

```
KSampler (pass 1) ─→ Latent Upscale ─→ KSampler (pass 2) ─→ VAE Decode ─→ Save Image
```

Step by step:

1. **Add Latent Upscale.** Search `Upscale Latent By` (or `Upscale Latent`). Connect KSampler #1's LATENT to its input. Set:
   - `upscale_method` — `nearest-exact` for sharp, `bilinear` for slightly smoother. Try `nearest-exact` first.
   - `scale_by` — 1.5 to 2.0. Going above 2x in one pass tends to lose coherence.

2. **Add second KSampler.** Same node type as the first. Connect:
   - `model` ← from Load Checkpoint (or Load LoRA chain)
   - `positive` / `negative` ← same conditioning as KSampler #1
   - `latent_image` ← Latent Upscale output

3. **Wire VAE Decode** to KSampler #2's output (not #1's anymore).

4. **Wire Save Image** as before.

## Settings for the second sampler

This is where it differs from the first pass.

| Widget | Pass 1 | Pass 2 (refinement) |
|--------|--------|---------------------|
| seed | random or fixed | **same as pass 1** for consistency |
| steps | 20 | **8–15** (shorter is usually better) |
| cfg | 7 | 5–7 |
| sampler_name | euler / dpmpp_2m | same as pass 1 |
| scheduler | normal / karras | same |
| denoise | 1.0 | **0.4–0.6** ← key |

The crucial widget is `denoise`. At 1.0 the second pass would re-noise the latent fully and generate a new image — destroying the composition you just made. At 0.4–0.6 it preserves the composition but injects detail.

- **0.4** — Conservative. Same image, slightly sharper.
- **0.5** — Balanced default.
- **0.6** — More creative refinement. Faces and textures get more detail but can shift slightly.
- **0.7+** — Risky. The image starts to drift from the first pass.

For a first try: same seed, 10 steps, denoise 0.5.

## Why same seed matters

Setting `seed` on the second sampler to the same value as the first locks the noise pattern. Combined with low denoise, you get the same composition with more detail. Different seeds produce different details and sometimes drift the composition.

If you want pass 2 to be deterministic given pass 1, set both seeds to the same fixed value (or wire pass 1's seed to pass 2 if your UI supports it).

## Two-pass with model upscaler (sharper but slower)

The latent-space upscale above is fast and clean. For sharper output, swap in a real upscale model (RealESRGAN, 4x-UltraSharp, etc.):

```
KSampler #1 ─→ VAE Decode ─→ Upscale Image (Using Model) ─→ VAE Encode ─→ KSampler #2 ─→ VAE Decode ─→ Save Image
```

This adds:
- `Load Upscale Model` — loads an `.pth` file from `models/upscale_models/`
- `Upscale Image (Using Model)` — runs the upscale model
- `VAE Encode` — converts back to latent for KSampler #2

Slower (extra VAE round-trip and the upscale model itself) but produces sharper edges and finer texture.

Recommended upscale models:

- **4x-UltraSharp** — general purpose, sharp edges
- **4x_NMKD-Siax** — softer, natural-looking
- **4x-AnimeSharp** — for anime / illustration

Download from openmodeldb.info, drop into `ComfyUI/models/upscale_models/`.

## Memory math

If your card OOMs on the second pass, the issue is that pass 2 runs at the upscaled resolution. Math:

- SD 1.5 at 512×512 → 2x → 1024×1024 — fits on most cards
- SDXL at 1024×1024 → 2x → 2048×2048 — needs ~16 GB
- SDXL at 1024×1024 → 1.5x → 1536×1536 — fits on 12 GB

Drop `scale_by` first if you OOM. 1.5x with a high-quality upscaler often beats 2x with bare latent.

## Common failures

### Pass 2 produces a totally different image

- `denoise` too high. Drop to 0.5 or below.
- Different seed than pass 1. Match them.

### Pass 2 looks identical to pass 1, no improvement

- `denoise` too low (below 0.3) — sampler does almost nothing.
- `steps` too low (below 5) — same effect.

### Faces/details mangle in pass 2

- Common with SDXL at 2048+ resolution. The model wasn't trained that high. Drop scale to 1.5x.
- Try a model upscaler instead of latent upscale.

### Tiled / repeated subjects appear

- Resolution is too far above native. SDXL above 2048 will start tiling. Use ControlNet Tile or 1.5x scale.

### OOM on pass 2

- Pass 2 needs as much VRAM as pass 1 at the higher resolution. Use `--lowvram` or reduce scale.

### Workflow runs but Save Image saves the small version

- Save Image is wired to pass 1's VAE Decode by accident. Re-route it to pass 2's output.

## Hires Fix + LoRA + ControlNet

Stacking is fine. Both LoRAs and ControlNet apply to both passes if wired correctly:

- LoRA modifies MODEL/CLIP — both KSamplers use the same modified MODEL, so LoRA carries over automatically
- ControlNet modifies CONDITIONING — wire the same `Apply ControlNet` output into both samplers' positive input

If pass 2 should ignore ControlNet (sometimes you only want structure on pass 1), wire the raw text encode output to pass 2's positive instead.

## Summary

- Hires Fix = first pass at native resolution + second pass at higher resolution with low denoise
- Use Latent Upscale for fast results, Upscale Image (Using Model) for sharper results
- Pass 2 settings: same seed, 8–15 steps, denoise 0.4–0.6
- Stay within 1.5–2x of native resolution per pass
- LoRAs propagate automatically; ControlNet you choose to propagate or not

## What's next

The third major workflow expansion is **image-to-image** — using a real image as the starting latent instead of an empty one. Style transfer, photo editing, sketch-to-finished-art. Different setup but uses the same KSampler concepts you already know.
