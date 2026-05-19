export const SITE = {
  domain: 'comfyatlas.com',
  url: 'https://comfyatlas.com',
  name: 'ComfyAtlas',
  defaultLocale: 'en' as const,
  locales: ['en', 'zh'] as const,
};

export type Locale = (typeof SITE.locales)[number];

export const ui = {
  en: {
    'site.tagline': 'A practical atlas for ComfyUI — guides, nodes, workflows.',
    'site.description':
      'ComfyAtlas is a focused knowledge base for ComfyUI. Step-by-step installation guides, node references, and end-to-end workflows for Stable Diffusion users.',
    'nav.home': 'Home',
    'nav.guides': 'Guides',
    'nav.about': 'About',
    'nav.search': 'Search',
    'home.hero.title': 'Master ComfyUI, one node at a time.',
    'home.hero.sub':
      'Clear, hands-on guides for installing ComfyUI, understanding nodes, and building real workflows. No fluff.',
    'home.hero.cta': 'Start with the install guide',
    'home.latest': 'Latest guides',
    'home.section.start.title': 'Start here',
    'home.section.start.desc': 'New to ComfyUI? Walk through the basics in order.',
    'category.getting-started': 'Getting started',
    'category.workflow-extensions': 'Workflow extensions',
    'category.models': 'Models',
    'category.troubleshooting': 'Troubleshooting',
    'blog.title': 'Guides',
    'blog.empty': 'No posts yet.',
    'post.published': 'Published',
    'post.updated': 'Updated',
    'post.toc': 'On this page',
    'footer.copy': '© {year} ComfyAtlas. Independent project, not affiliated with the ComfyUI team.',
    'footer.lang': 'Language',
  },
  zh: {
    'site.tagline': 'ComfyUI 实战图册 — 教程、节点、工作流。',
    'site.description':
      'ComfyAtlas 专注于 ComfyUI 知识库,提供安装教程、节点详解和完整工作流,服务 Stable Diffusion 用户。',
    'nav.home': '首页',
    'nav.guides': '教程',
    'nav.about': '关于',
    'nav.search': '搜索',
    'home.hero.title': '一节点一节点,精通 ComfyUI。',
    'home.hero.sub':
      '清晰、可上手的 ComfyUI 教程:安装、节点解析、完整工作流。不灌水。',
    'home.hero.cta': '从安装教程开始',
    'home.latest': '最新教程',
    'home.section.start.title': '从这里开始',
    'home.section.start.desc': '第一次接触 ComfyUI?按顺序看完基础。',
    'category.getting-started': '入门',
    'category.workflow-extensions': '工作流扩展',
    'category.models': '模型',
    'category.troubleshooting': '故障排查',
    'blog.title': '教程',
    'blog.empty': '还没有文章。',
    'post.published': '发布于',
    'post.updated': '更新于',
    'post.toc': '本页目录',
    'footer.copy': '© {year} ComfyAtlas. 独立项目,与 ComfyUI 官方无关联。',
    'footer.lang': '语言',
  },
} as const;

export function t(locale: Locale, key: keyof typeof ui.en): string {
  return ui[locale][key] ?? ui.en[key];
}

export function localizedPath(locale: Locale, path: string): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  if (locale === SITE.defaultLocale) return clean;
  return `/${locale}${clean === '/' ? '' : clean}`;
}
