import os
import re

print("=== 1. 查找并修正商品数据中的原始 SKU Slug ===")
replaced_count = 0
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith((".ts", ".js", ".json", ".astro")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            orig = content
            # 替换 ACCSZONE-2305... 原始英文编码为规范中文名
            if "ACCSZONE" in content or "youtube-accounts-youtube-channel-registered" in content:
                content = re.sub(
                    r'ACCSZONE-\d+\|slug=youtube-accounts-youtube-channel-registered-in-2013-2016[a-zA-Z0-9\-_]*',
                    '2013-2016年老频道 (空白/含少量视频·即买即用)',
                    content
                )
                content = re.sub(
                    r'youtube-accounts-youtube-channel-registered-in-2013-2016[a-zA-Z0-9\-_]*',
                    '2013-2016年老频道 (空白/含少量视频·即买即用)',
                    content
                )

            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                replaced_count += 1
                print(f"✓ 已将原始 SKU 编码汉化更新: {path}")

print(f"\n=== 2. 在 SKU 按钮渲染处增加自动清洗过滤 ===")
for root, _, files in os.walk("src/components"):
    for f in files:
        if f.endswith(".astro"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            if "sku-select-btn" in content:
                orig = content
                # 针对 sku.name 增加净化逻辑，去掉 ACCSZONE 与 slug= 杂质
                clean_helper = """
// 自动净化 SKU 显示名称
function formatSkuName(name) {
  if (!name) return '';
  if (name.includes('|slug=')) {
    let parts = name.split('|slug=')[1] || name;
    return parts.replace(/-/g, ' ').replace(/^./, str => str.toUpperCase());
  }
  return name.replace(/^ACCSZONE-\d+\|?/, '');
}
"""
                # 如果没有 formatSkuName 函数则注入
                if "formatSkuName" not in content and "---" in content:
                    # 在 frontmatter 头部注入辅助函数
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        parts[1] = parts[1] + clean_helper
                        content = "---".join(parts)
                        # 替换渲染 sku.name 为 formatSkuName(sku.name)
                        content = re.sub(r'\{(\w+)\.name\}', r'{formatSkuName(\1.name)}', content)

                if content != orig:
                    with open(path, "w", encoding="utf-8") as file:
                        file.write(content)
                    print(f"✓ 已为 SKU 按钮组件添加净化过滤器: {path}")

