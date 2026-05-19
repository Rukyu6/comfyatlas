# ComfyAtlas

A focused knowledge base for ComfyUI — installation guides, node references,
and workflows. Built with Astro, Tailwind, and MDX. Bilingual (English / 中文).

## Stack

- Astro 5 (static output)
- Tailwind CSS 3
- MDX for blog posts
- Built-in i18n (English at `/`, Chinese at `/zh/`)
- Sitemap, RSS, schema.org Article markup, hreflang alternates

## Local development

```bash
npm install         # one-time
npm run dev         # dev server at http://localhost:4321
npm run build       # production build → dist/
npm run preview     # preview production build
```

## Project layout

```
src/
  content.config.ts    # blog collection schema (zod)
  content/blog/
    *.md               # English posts (file slug = URL slug)
    zh/*.md            # Chinese posts (mirror filenames)
  lib/i18n.ts          # locale config + translation strings
  layouts/BaseLayout.astro
  components/{Header,Footer}.astro
  pages/
    index.astro             # English home
    about.astro
    blog/index.astro        # English blog list
    blog/[slug].astro       # English article
    rss.xml.js
    zh/index.astro          # Chinese home
    zh/about.astro
    zh/blog/index.astro
    zh/blog/[slug].astro
  styles/global.css
public/
  robots.txt
astro.config.mjs
```

## Adding a new blog post

1. Create `src/content/blog/<slug>.md` with frontmatter:

   ```md
   ---
   title: "Your title"
   description: "1–2 sentence summary used in meta + OG tags"
   pubDate: 2026-05-19
   lang: en
   tags: ["installation"]
   ---

   Content here.
   ```

2. Create the Chinese mirror at `src/content/blog/zh/<same-slug>.md`
   with `lang: zh`. The slugs **must match** so hreflang links pair up.

3. `npm run build` to verify.

## Frontmatter fields

| Field         | Required | Notes |
|---------------|----------|-------|
| title         | yes      | also used as `<h1>` |
| description   | yes      | meta description, OG, Twitter card |
| pubDate       | yes      | ISO date |
| updatedDate   | no       | ISO date, displayed if present |
| lang          | yes      | `en` or `zh` |
| tags          | no       | array of strings |
| heroImage     | no       | image (optimized by Astro) |
| draft         | no       | `true` to exclude from build |

The URL slug is the filename. Don't put a `slug:` field in frontmatter —
Astro 5's content loader uses the file path as the entry id, and a custom
`slug` field collides between en/zh mirrors.

## Deployment

Site is configured for static hosting. Build output is `dist/`.

**Vercel** (recommended): connect the GitHub repo, framework preset
"Astro", build command `npm run build`, output directory `dist`. Done.

**Cloudflare Pages**: same idea — build command `npm run build`,
output directory `dist`.

After deploying, set `site` in `astro.config.mjs` to your real domain
(currently `https://comfyatlas.com`) so absolute URLs in sitemap and
RSS are correct.

## SEO checklist after first deploy

1. Set up Google Search Console for `comfyatlas.com`. Verify with
   Cloudflare DNS TXT record (easiest).
2. Submit `https://comfyatlas.com/sitemap-index.xml` in Search Console.
3. Set up Google Analytics 4 (or Plausible / Umami if you prefer
   privacy-friendly). Paste the tracking snippet into `BaseLayout.astro`
   inside `<head>`.
4. Use Google's Rich Results Test on your article URL to confirm the
   `Article` schema is valid.
5. PageSpeed Insights for the homepage + a blog post. Aim for green
   LCP / CLS / FID.

## License / disclaimer

ComfyAtlas is independent and not affiliated with the ComfyUI team or
Comfy Org. ComfyUI is GPL-3.0. This site's own content is the
property of its author.
