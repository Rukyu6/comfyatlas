# 接下来你要做的事

骨架已经搭好,build 跑通。接下来的步骤需要你在浏览器里点,我做不到。

## 第一步:本地预览(可选,2 分钟)

```bash
cd /home/crono/projects/comfyatlas
npm run dev
```

然后浏览器打开 http://localhost:4321 看英文站,/zh/ 看中文站。
确认满意了再继续。Ctrl+C 停止。

## 第二步:注册账号

如果之前没注册过,需要这几个(都免费):

1. **GitHub** — https://github.com/signup
   托管代码,用邮箱注册即可
2. **Vercel** — https://vercel.com/signup
   选 "Continue with GitHub",直接用 GitHub 账号登录
3. **Cloudflare** — https://dash.cloudflare.com/sign-up
   用来管理域名 DNS 和加速

## 第三步:买域名 comfyatlas.com

推荐 Cloudflare Registrar(顺便可以管 DNS):

1. 登录 Cloudflare,左侧菜单选 "Domain Registration" → "Register Domains"
2. 搜 comfyatlas.com
3. .com 一年大约 $9-10
4. 信用卡付款

为什么不用 GoDaddy / Namesilo:Cloudflare 不加价、续费同价、自动启用安全配置。

## 第四步:把代码推到 GitHub

完成后告诉我,这一步我可以帮你做(初始化 git、写 commit、推送)。
我需要你先:

1. 在 GitHub 创建一个空仓库,叫 `comfyatlas`(public 或 private 随你)
2. **不要勾**任何 README / .gitignore / license 选项
3. 把仓库地址告诉我(类似 git@github.com:你的用户名/comfyatlas.git)
4. 你需要在本机配好 SSH key 或 GitHub CLI 认证才能推送

## 第五步:Vercel 部署(浏览器里点)

1. vercel.com → New Project
2. Import 你刚推上去的 comfyatlas 仓库
3. Framework Preset: 自动识别为 Astro
4. Build Command / Output Directory: 默认即可
5. Deploy

部署成功后会给你一个 *.vercel.app 的临时域名,可以先访问看看。

## 第六步:绑定自定义域名

1. Vercel 项目 → Settings → Domains → Add → 输入 comfyatlas.com
2. Vercel 会给你两条 DNS 记录(A 和 CNAME)
3. 在 Cloudflare DNS 面板里加上这两条记录
4. 等 5-30 分钟 DNS 生效
5. https://comfyatlas.com 上线

## 第七步:接 Google Search Console

1. https://search.google.com/search-console
2. 添加资源 → Domain → 输入 comfyatlas.com
3. 它会让你加一个 TXT 记录到 Cloudflare DNS,加完点验证
4. 验证通过后,提交 sitemap:https://comfyatlas.com/sitemap-index.xml

## 第八步:接 Google Analytics(可选)

1. https://analytics.google.com 创建 GA4 资源
2. 拿到 G-XXXXXXX 这样的 Measurement ID
3. 把 ID 给我,我把统计代码塞进 BaseLayout.astro

## 现在的状态

  ✓ Astro 项目骨架(src + 配置 + 路由)
  ✓ 双语 i18n(英文主站 + /zh/ 镜像)
  ✓ 第一篇文章:ComfyUI 安装教程(英文 1500+ 词、中文对应)
  ✓ SEO:meta、OG、Twitter card、Article schema、hreflang
  ✓ sitemap-index.xml、robots.txt、RSS feed
  ✓ Tailwind 排版、移动端响应式
  ✓ build 通过,8 个页面静态生成

## 内容生产节奏建议

- 每周 2-3 篇文章,每篇至少 1000 词
- 第二篇:Understanding ComfyUI Nodes(节点视觉指南)
- 第三篇:Your First ComfyUI Workflow(从 0 到 1 出图)
- 第四篇起:具体节点详解 / 工作流示例 / 故障排查

需要我开始写第二篇就告诉我。
