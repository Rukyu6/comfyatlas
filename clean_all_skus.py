import os
import re

def translate_sku_slug(raw):
    if not raw:
        return raw
    # 去除外部供应商前缀 (如 ACCSZONE-1234|slug= 或 ACC-...)
    text = re.sub(r'^[A-Z0-9_\-]+(?:\|slug=|\:|\/|\|)', '', raw).strip()
    text = re.sub(r'^slug=', '', text).strip()

    # 如果已经是规范中文，仅清理残留前缀即可
    chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
    if chinese_chars >= 4 and not text.startswith('ACCSZONE'):
        return re.sub(r'ACCSZONE-[0-9]+\|?', '', text).strip()

    tags = []
    lower = text.lower()

    # 1. 识别年份
    year_match = re.search(r'(?:registered-in-|year-)?(20\d{2})-(20\d{2})', lower)
    if year_match:
        tags.append(f"{year_match.group(1)}-{year_match.group(2)}年老号")
    else:
        single_year = re.search(r'(?:registered-in-|year-)(20\d{2})', lower)
        if single_year:
            tags.append(f"{single_year.group(1)}年老号")

    # 2. 识别状态与内容
    if 'channel-blank-or-contains-few-uploads' in lower:
        tags.append("空白频道/含少量视频")
    elif 'channel-blank' in lower:
        tags.append("纯空白全新频道")
    elif 'with-subscribers' in lower or 'subscribers' in lower:
        tags.append("带订阅粉丝")

    # 3. 识别格式与协议
    if 'tdata' in lower:
        tags.append("Tdata电脑端直登")
    elif 'session' in lower:
        tags.append("Session+Json格式")
    if 'cookie' in lower:
        tags.append("含Cookie直登")
    if '2fa' in lower:
        tags.append("已开2FA")

    # 4. 识别 IP 与环境
    if 'ready-to-use-mixed-ip-registered' in lower or 'ready-to-use' in lower or 'mixed-ip' in lower:
        tags.append("混合原生IP·即买即用")
    elif 'usa-ip' in lower or 'us-ip' in lower:
        tags.append("美国原生IP")

    if 'pva' in lower or 'phone-verified' in lower:
        tags.append("已实体验证")

    if 'aged' in lower and not any('年' in t for t in tags):
        tags.append("高权重老号")

    if tags:
        return " | ".join(tags)

    # 兜底：转为规范大写词组
    words = [w.capitalize() for w in text.replace('-', ' ').replace('_', ' ').split() if w]
    return ' '.join(words)

print("=== 1. 扫描并汉化修改全站商品数据中的 SKU ===")
updated_files = 0
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith((".ts", ".js", ".json", ".astro")):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception:
                continue

            orig = content

            # 匹配 name: "ACCSZONE..." 或 'name': '...' 或 "sku": "..."
            def replace_sku_val(match):
                prefix = match.group(1)
                quote = match.group(2)
                val = match.group(3)
                new_val = translate_sku_slug(val)
                if new_val != val:
                    print(f"  [{f}] SKU 汉化: '{val[:40]}...' -> '{new_val}'")
                return f'{prefix}{quote}{new_val}{quote}'

            # 针对 JSON / 对象属性中的 name 或 title
            content = re.sub(
                r'((?:name|title|skuName|sku)\s*:\s*)(["\'])(ACCSZONE-[^"\']+|youtube-accounts-[^"\']+|telegram-accounts-[^"\']+|[a-zA-Z0-9_\-]+-registered-[^"\']+)\2',
                replace_sku_val,
                content
            )

            # 针对通用带 slug 的字符串
            content = re.sub(
                r'((?:name|title|skuName|sku)\s*:\s*)(["\'])([^"\']*\|slug=[^"\']+)\2',
                replace_sku_val,
                content
            )

            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                updated_files += 1
                print(f"✓ 已写入更新文件: {path}")

print(f"共更新商品数据文件: {updated_files} 个")

print("\n=== 2. 在前端组件注入全局 SKU 智能清洗解析器 ===")
# 在 ProductModal.astro 与 CartDrawer.astro 中确保前端显示经过清洗
for comp_name in ["ProductModal.astro", "CartDrawer.astro", "BuyModal.astro"]:
    for root, _, files in os.walk("src"):
        if comp_name in files:
            comp_path = os.path.join(root, comp_name)
            with open(comp_path, "r", encoding="utf-8") as file:
                content = file.read()

            orig = content
            # 如果尚未嵌入 parseSkuDisplay 辅助函数
            helper_code = """
function parseSkuDisplay(name) {
  if (!name) return '';
  if (name.includes('ACCSZONE') || name.includes('|slug=') || name.includes('-registered-')) {
    let clean = name.replace(/^[A-Z0-9_\-]+(?:\\|slug=|\\:|\\/|\\|)/, '').replace(/^slug=/, '');
    let tags = [];
    let lower = clean.toLowerCase();
    let yMatch = lower.match(/(?:registered-in-|year-)?(20\\d{2})-(20\\d{2})/);
    if (yMatch) tags.push(yMatch[1] + '-' + yMatch[2] + '年老号');
    if (lower.includes('channel-blank-or-contains-few-uploads')) tags.push('空白频道/含少量视频');
    else if (lower.includes('channel-blank')) tags.push('空白全新频道');
    if (lower.includes('ready-to-use') || lower.includes('mixed-ip')) tags.push('混合原生IP·即买即用');
    if (lower.includes('tdata')) tags.push('Tdata电脑端直登');
    if (lower.includes('cookie')) tags.push('含Cookie直登');
    if (tags.length > 0) return tags.join(' | ');
    return clean.replace(/-/g, ' ');
  }
  return name.replace(/^ACCSZONE-\\d+\\|?/, '');
}
"""
            if "parseSkuDisplay" not in content and "---" in content:
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    parts[1] = parts[1] + helper_code
                    content = "---".join(parts)
                    content = re.sub(r'\{(\w+)\.name\}', r'{parseSkuDisplay(\1.name)}', content)
                    content = re.sub(r'\{(\w+)\.skuName\}', r'{parseSkuDisplay(\1.skuName)}', content)

            if content != orig:
                with open(comp_path, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"✓ 已为 {comp_path} 注入 SKU 渲染净化逻辑")

