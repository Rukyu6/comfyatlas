import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITE } from '../lib/i18n';

export async function GET(context) {
  const posts = await getCollection('blog', ({ data, id }) => !data.draft && data.lang === 'en' && !id.startsWith('zh/'));
  return rss({
    title: SITE.name,
    description: 'A practical atlas for ComfyUI — guides, nodes, workflows.',
    site: context.site ?? SITE.url,
    items: posts
      .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
      .map((post) => ({
        title: post.data.title,
        pubDate: post.data.pubDate,
        description: post.data.description,
        link: `/blog/${post.id}/`,
      })),
  });
}
