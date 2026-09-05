import os
import re

print("=== 1. 检查商品描述完整文本 ===")
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith((".ts", ".js", ".json", ".astro")):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    txt = file.read()
                if "保系统性异常导致的权限丢失" in txt:
                    idx = txt.find("保系统性异常导致的权限丢失")
                    print(f"✓ 在 {path} 中确认完整文本内容存在:")
                    print("  ->", txt[idx : idx + 100].replace('\n', ' '))
            except:
                pass

print("\n=== 2. 移除商品卡片与弹窗中的文本截断限制 (line-clamp / max-h) ===")
modified = []
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith((".astro", ".jsx", ".tsx", ".vue", ".html")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            orig = content

            # 1. 移除针对描述/内容段落 <p> 的 line-clamp-数字
            new_content = re.sub(
                r'(<p\b[^>]*class=["\'][^"\']*)\bline-clamp-\d+\b([^"\']*["\'])',
                r'\1\2',
                content
            )

            # 2. 移除带有 description / desc 上层容器的 line-clamp
            new_content = re.sub(
                r'\bline-clamp-\d+\b(?=[\s\S]*?(?:description|desc|【商品属性】|购买须知))',
                '',
                new_content
            )

            # 3. 如果存在固定 max-h 限制导致内容被裁剪，一并解除
            new_content = re.sub(
                r'(<p\b[^>]*class=["\'][^"\']*)\bmax-h-\[[^\]]+\]([^"\']*["\'])',
                r'\1\2',
                new_content
            )

            # 清理连续空格
            new_content = re.sub(r'class=" +', 'class="', new_content)
            new_content = re.sub(r' +"', '"', new_content)
            new_content = re.sub(r' {2,}', ' ', new_content)

            if new_content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(new_content)
                modified.append(path)
                print(f"✓ 已成功解除截断限制: {path}")

print(f"\n共更新组件数: {len(modified)}")
