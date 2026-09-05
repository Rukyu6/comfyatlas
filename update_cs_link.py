import os
import re

target_url = "https://t.me/puppyshop2Bot"
changed_files = []

for root, _, files in os.walk("src"):
    for file in files:
        if file.endswith((".astro", ".html", ".js", ".ts", ".jsx", ".tsx")):
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            if "在线客服" in content:
                original = content

                def replace_a_tag(match):
                    tag_content = match.group(0)
                    # 替换或添加 href
                    if re.search(r'href=["\'][^"\']*["\']', tag_content):
                        new_tag = re.sub(r'href=["\'][^"\']*["\']', f'href="{target_url}"', tag_content, count=1)
                    else:
                        new_tag = re.sub(r'<a\b', f'<a href="{target_url}"', tag_content, count=1)

                    # 确保在新标签页打开
                    if not re.search(r'target=["\'][^"\']*["\']', new_tag):
                        new_tag = re.sub(r'<a\b', '<a target="_blank"', new_tag, count=1)
                    else:
                        new_tag = re.sub(r'target=["\'][^"\']*["\']', 'target="_blank"', new_tag, count=1)

                    # 确保安全属性 rel
                    if not re.search(r'rel=["\'][^"\']*["\']', new_tag):
                        new_tag = re.sub(r'<a\b', '<a rel="noopener noreferrer"', new_tag, count=1)
                    else:
                        new_tag = re.sub(r'rel=["\'][^"\']*["\']', 'rel="noopener noreferrer"', new_tag, count=1)

                    return new_tag

                # 1. 匹配包含 "在线客服" 的 <a> 链接标签
                new_content = re.sub(
                    r'<a\b[^>]*>(?:(?!<\/a>)[\s\S])*?在线客服(?:(?!<\/a>)[\s\S])*?<\/a>',
                    replace_a_tag,
                    content
                )

                # 2. 匹配如果是对象/配置项结构 (例如: { label: '在线客服', href: '...' })
                def replace_obj(match):
                    obj_content = match.group(0)
                    if any(k in obj_content for k in ["href", "url", "link"]):
                        obj_content = re.sub(
                            r"""(href|url|link)\s*:\s*["'][^"']*["']""",
                            rf'\1: "{target_url}"',
                            obj_content
                        )
                    return obj_content

                new_content = re.sub(r'\{[^{}\n]*在线客服[^{}\n]*\}', replace_obj, new_content)

                if new_content != original:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    changed_files.append(filepath)
                    print(f"✓ 已成功更新 {filepath} 中的在线客服链接为: {target_url}")

print(f"\n共更新文件数: {len(changed_files)}")
