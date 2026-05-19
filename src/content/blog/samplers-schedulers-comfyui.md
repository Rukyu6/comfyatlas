---
title: "Samplers and Schedulers in ComfyUI: When to Use Each (with Visual Examples)"
description: "A practical comparison of ComfyUI's main samplers and schedulers — Euler, DPM++ 2M, DPM++ 3M SDE, Karras, exponential. What each does, what makes images differ, and what to pick for speed, quality, or specific styles."
pubDate: 2026-05-22
lang: en
category: workflow-extensions
heroImage: ./_assets/cover-nodes.png
tags: ["samplers", "schedulers", "ksampler", "stable-diffusion", "tutorial"]
---

The KSampler node has two dropdowns most people leave on default: `sampler_name` and `scheduler`. They're the part of the workflow that controls *how* the model denoises noise into an image — same prompt, same seed, different sampler can produce noticeably different results. Understanding these dials is the difference between "generation looks bland" and "generation looks like what I imagined."

This guide is a practical reference — what to use and when. It assumes you have a working text-to-image workflow and have read the [first workflow guide](/blog/your-first-comfyui-workflow/).

## What samplers and schedulers actually do

When you click Queue Prompt, the model is handed a noisy latent and asked to clean it. It doesn't do this in one shot — it does it in steps. At each step, the model predicts the noise that's still in the latent and removes some of it. After 20 steps (or whatever you set), the latent is clean enough to decode into an image.

Two algorithms control this process:

- **Sampler** — the math used to convert a noise prediction into a denoising update. Different samplers take the model's predictions and combine them differently.
- **Scheduler** — the function that controls *how much* noise to remove at each step. Some schedulers move quickly at first then slowly; others are linear.

Together they decide:
- How much information you extract per step
- How smooth or sharp the final image becomes
- Whether the image is deterministic (reproducible) or stochastic (slightly different each run)

## The sampler families

ComfyUI ships with about 20 samplers. They're not all useful. Group them.

### Euler family — fast, simple, reliable

| Sampler | When to use |
|---------|-------------|
| `euler` | Fast and reliable. Always-good default. |
| `euler_ancestral` | Adds noise back at each step → more diversity, less determinism. Good for creative variation. |

Euler is the workhorse. Pick it when you want predictable results in 15-20 steps.

### DPM++ family — sharper, more refined

| Sampler | When to use |
|---------|-------------|
| `dpmpp_2m` | Classic SDXL favorite. Sharper than Euler. Use 20-30 steps. |
| `dpmpp_2m_sde` | Stochastic version. More variation. Same quality. |
| `dpmpp_3m_sde` | Higher-order, better at complex scenes. Slower. |
| `dpmpp_sde` | Original SDE. Stochastic, good for grain/film looks. |

DPM++ samplers usually produce sharper details than Euler at the same step count. Trade-off: a bit slower.

### Heun family — high quality, slow

| Sampler | When to use |
|---------|-------------|
| `heun` | Two function evaluations per step. Higher quality, ~2x slower. |
| `heunpp2` | Improved variant. |

Pick Heun when you need polished output and don't care about speed.

### Other useful samplers

| Sampler | When to use |
|---------|-------------|
| `lms` | Linear multi-step. Fast, slightly soft. Good for early experiments. |
| `lcm` | LCM-LoRA samplers (4-8 steps total). Very fast, requires LCM LoRA loaded. |
| `uni_pc` | Unified predictor-corrector. Very stable across step counts. |

Ignore: `ddim`, `pndm` — older, mostly superseded.

## The scheduler list

Schedulers control noise distribution across steps.

| Scheduler | Effect |
|-----------|--------|
| `normal` | Default, linear-ish. Always fine. |
| `karras` | More steps near the end → finer detail. Pairs well with most samplers. |
| `exponential` | More steps at the start → cleaner large composition. |
| `simple` | Minimal scheduling. Fastest but lower fidelity. |
| `sgm_uniform` | Used for SD 3 and FLUX. Required for those bases. |
| `ddim_uniform` | For DDIM sampler specifically. |

`karras` is the most important upgrade most users miss. Switching from `normal` to `karras` while keeping the same sampler often gives better detail with no other change.

## Recommended pairings

The sampler+scheduler combo matters more than the individual choice. Some pairings are dramatically better than the components alone.

| Goal | Sampler | Scheduler | Steps | Notes |
|------|---------|-----------|-------|-------|
| Default / first try | `euler` | `normal` | 20 | Always works. |
| **Sharper SDXL** | `dpmpp_2m` | `karras` | 25-30 | Most popular SDXL combo. |
| Fast iteration | `euler` | `simple` | 15 | Good for prompt tuning. |
| Maximum quality | `dpmpp_3m_sde` | `karras` | 30-40 | Slow but clean. |
| Photo realism | `dpmpp_2m_sde` | `karras` | 25 | Less artificial than Euler. |
| Anime / illustration | `euler_ancestral` | `karras` | 20 | Creative variation. |
| Film grain look | `dpmpp_sde` | `karras` | 25 | Stochastic gives grain. |
| Low-step LCM workflows | `lcm` | `simple` | 4-8 | Requires LCM LoRA. |
| FLUX | `euler` | `simple` or `sgm_uniform` | 20 | FLUX prefers simple schedulers. |
| SD3 | `dpmpp_2m` | `sgm_uniform` | 28 | Required pairing. |

If you take only one thing from this guide: **switch from `euler` + `normal` to `dpmpp_2m` + `karras` for SDXL**. It's a free upgrade.

## How to compare yourself

Don't take recipe lists at face value. Run your own A/B test:

1. Pick a prompt you've used before. Lock the seed (`control_after_generate: fixed`).
2. Generate at one sampler/scheduler combo. Save.
3. Change *only* the sampler. Generate. Save.
4. Change *only* the scheduler. Generate. Save.
5. Compare the three images.

Differences are usually subtle. Look for:
- Edge sharpness (especially on hair, eyelashes, fabric textures)
- Color saturation
- Composition stability
- Artifacts (grain, smudging, flat areas)

A "best" sampler depends on your style. Photorealism wants different things from anime.

## Step count interactions

Sampler choice interacts with step count.

- Below 10 steps: only LCM and Turbo samplers work. Everything else looks unfinished.
- 15-25 steps: Euler, DPM++ 2M, DPM++ 2M SDE all give good results. This is the sweet spot for most work.
- 30-50 steps: diminishing returns for most samplers. Heun and DPM++ 3M SDE keep improving slightly. Euler stops improving around 25.
- 50+ steps: only useful for showcase pieces or scientific reproducibility. Daily work: 20-25.

If your output looks unfinished, more steps is usually NOT the fix — switch sampler instead. Euler at 50 steps is rarely better than DPM++ 2M at 25.

## CFG interaction

CFG (classifier-free guidance) controls how strongly the model follows the prompt. Different samplers handle high CFG differently.

- Euler: tolerates CFG up to ~10 cleanly. Above 12 it starts oversaturating.
- DPM++ 2M: tolerates CFG up to ~8. Sharper but more easily "burned" at high CFG.
- DPM++ SDE: handles high CFG (10-12) better than DPM++ 2M.
- Ancestral (`*_a` suffix): high CFG can produce noisy speckle.

For SDXL: CFG 5-7 is the practical range. SD 1.5 tolerated 7-12 fine. FLUX uses its own `guidance` widget instead of CFG.

## Stochastic vs deterministic samplers

Sampler names ending in `_a`, `_sde`, or `ancestral` are **stochastic** — they add noise back at each step. Same seed + stochastic sampler = different output each run (slightly).

Deterministic samplers (Euler, DPM++ 2M without `_sde`) give the *exact* same output for the same seed.

Use deterministic when you need to reproduce an image exactly. Use stochastic when you want variation across runs of the same prompt.

## Common failures

### Output is soft / blurry

- Wrong scheduler. Switch to `karras`.
- Step count too low.
- LMS or simple scheduler will look soft. That's their character; switch.

### Output is over-sharpened / fried

- CFG too high. Drop to 6-7.
- Sampler too aggressive (DPM++ 2M at high CFG). Try Euler.

### Same prompt + same seed produces different images

- You picked a stochastic sampler (`*_sde`, `*_ancestral`). Switch to a deterministic one if you need reproducibility.

### Sampler isn't in the dropdown

- Some samplers come from custom node packs. ComfyUI ships with ~20; ComfyUI-Manager auxiliary packs add more (`ipndm`, `lcm`, etc.).

### LCM mode produces noise / low quality

- LCM samplers require LCM LoRA loaded. Without it, low-step generation looks broken.
- Set steps to exactly 4-8. More steps with LCM = artifacts.

## Cheat sheet

If you remember nothing else from this article:

- **Default**: `dpmpp_2m` + `karras` + 25 steps + cfg 7
- **Fast**: `euler` + `simple` + 15 steps
- **Best**: `dpmpp_3m_sde` + `karras` + 35 steps
- **FLUX**: `euler` + `simple` + 20 steps + guidance 3.5
- Switch only one variable at a time when tuning

## What's next

Now you've got the full toolkit: text-to-image, LoRA, ControlNet, Hires Fix, img2img, Inpainting, IP-Adapter, plus sampler tuning. The next major dimension is **video** — turning these workflows into animated sequences. AnimateDiff is the standard approach and gets its own guide.
