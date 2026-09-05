import os
import re
import json

KEYWORD_MAP = [
    ("2013-2016", "2013-2016年老号"),
    ("2010-2022", "2010-2022年老号"),
    ("2020-2022", "2020-2022年老号"),
    ("2024-2026", "2024-2026年老号"),
    ("2018", "2018年老号"),
    ("usa", "美国原生IP"),
    ("us-ip", "美国原生IP"),
    ("uk", "英国原生IP"),
    ("japan", "日本原生IP"),
    ("korea", "韩国原生IP"),
    ("hongkong", "香港原生IP"),
    ("taiwan", "台湾原生IP"),
    ("germany", "德国原生IP"),
    ("france", "法国原生IP"),
    ("mixed-ip", "混合原生IP"),
    ("mix-ip", "混合原生IP"),
    ("sms-verified", "实体短信验证"),
    ("pva", "实体手机号验证"),
    ("phone-verified", "实体手机号验证"),
    ("2fa-enabled", "已开启2FA双重验证"),
    ("2fa", "已开2FA"),
    ("outlook-hotmail", "自带Outlook/Hotmail邮箱"),
    ("outlook", "自带Outlook邮箱"),
    ("hotmail", "自带Hotmail邮箱"),
    ("gmail", "自带Gmail邮箱"),
    ("yahoo", "自带Yahoo邮箱"),
    ("blank-or-contains-few-uploads", "空白/含少量视频"),
    ("blank-few-uploads", "空白/含少量视频"),
    ("channel-blank", "纯空白频道"),
    ("blank", "纯白号/空白账户"),
    ("with-followers", "带真实粉丝"),
    ("subscribers", "带订阅"),
    ("tdata", "Tdata电脑端直登"),
    ("session", "Session+Json格式"),
    ("cookie", "含Cookie直登"),
    ("ready-to-use", "即买即用"),
    ("token", "带Token"),
    ("aged", "高权重老号"),
]

def translate_slug(text):
    if not text or not isinstance(text, str):
        return text
    clean = re.sub(r'^[A-Z0-9_\-]+(?:\|slug=|\:|\/|\|)', '', text)
    clean = re.sub(r'^slug=', '', clean).strip()

    # 如果已有多个汉字，直接去除前缀返回
    ch_count = len(re.findall(r'[\u4e00-\u9fa5]', clean))
    if ch_count >= 3:
        return re.sub(r'ACCSZONE-\d+\|?', '', clean).strip()

    lower = clean.lower()
    tags = []
    
    # 匹配年份
    ym = re.search(r'(?:registered-in-|year-)?(20\d{2})-(20\d{2})', lower)
    if ym:
        tags.append(f"{ym.group(1)}-{ym.group(2)}年老号")
    else:
        sy = re.search(r'(?:registered-in-|year-)?(20\d{2})', lower)
        if sy and sy.group(1) not in ["2024", "2025", "2026"]:
            tags.append(f"{sy.group(1)}年老号")

    for kw, label in KEYWORD_MAP:
        if kw in lower and label not in tags:
            tags.append(label)

    if tags:
        return " | ".join(tags)

    if clean.upper() == "DEFAULT":
        return "官方正版·自动发货"
    return clean.replace('-', ' ').title()

print("=== 1. 扫描并直接汉化全站数据文件中的 SKU 属性 ===")
data_files_updated = 0
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith((".ts", ".js", ".json", ".astro")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()

            orig = content

            # 匹配对象属性中的 sku_code 或 name 包含 slug/ACCSZONE
            def repl_sku_prop(match):
                prefix = match.group(1)
                q = match.group(2)
                val = match.group(3)
                new_val = translate_slug(val)
                return f"{prefix}{q}{new_val}{q}"

            content = re.sub(
                r'((?:sku_code|skuCode|sku|name|skuName)\s*:\s*)(["\'])(ACCSZONE-[^"\']+|[^"\']*\|slug=[^"\']+)\2',
                repl_sku_prop,
                content
            )

            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                data_files_updated += 1
                print(f"✓ 已清洗数据文件: {path}")

print(f"共清理数据文件: {data_files_updated} 个")

print("\n=== 2. 检查并锁定前端动态渲染处（确保弹窗一律过滤）===")
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith(".astro"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            orig = content
            if "sku-select-btn" in content or "selectedSku" in content or "openProductModal" in content:
                # 检查所有插入 button 文本的逻辑，强制加上 formatSkuDisplay
                # 例如 innerHTML = ... <button ...>${sku.name || sku.sku_code}...
                content = re.sub(
                    r'(class="[^"]*sku-select-btn[^"]*"[^>]*>[\s\S]*?)\$\{([^}]+)\}([\s\S]*?<\/button>)',
                    lambda m: f"{m.group(1)}${{window.formatSkuDisplay ? window.formatSkuDisplay({m.group(2)}) : {m.group(2)}}}{m.group(3)}" if "formatSkuDisplay" not in m.group(2) else m.group(0),
                    content
                )

                # 将针对单行渲染的代码替换
                content = re.sub(
                    r'span[^>]*class="[^"]*font-semibold[^"]*"[^>]*>\s*\$\{([^}]+)\}\s*<\/span>',
                    lambda m: f'span class="font-semibold">${{window.formatSkuDisplay ? window.formatSkuDisplay({m.group(1)}) : {m.group(1)}}}</span>' if "formatSkuDisplay" not in m.group(1) else m.group(0),
                    content
                )

            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"✓ 已加固弹窗渲染组件: {path}")

print("\n=== 3. 最终扫描：检查全站是否还残留原始 ACCSZONE / slug 字符串 ===")
residual_count = 0
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith((".ts", ".js", ".astro")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                lines = file.readlines()
            for line_idx, line in enumerate(lines):
                if ("ACCSZONE-" in line or "|slug=" in line) and "replace" not in line and "clean" not in line and "re.sub" not in line:
                    residual_count += 1
                    print(f"  [发现残留] {path}:{line_idx+1} -> {line.strip()[:80]}")

if residual_count == 0:
    print("🎉 完美！全站所有商品 SKU 中的原始 Slug 已 100% 彻底清洗完毕，无任何残留！")
else:
    print(f"⚠️ 剩余 {residual_count} 处残留，请核对。")

