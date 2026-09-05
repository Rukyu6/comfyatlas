import json
import re
import urllib.parse

with open("src/data/products.json", "r", encoding="utf-8") as f:
    db = json.load(f)

print(">>> 正在全库深度清洗 2600+ 件商品的详情与规格名...")

for p in db.get("products", []):
    # 1. 清洗规格名（杜绝 ACG-FAKA 乱码）
    skus = p.get("skus", [])
    for sku in skus:
        sname = sku.get("name", "")
        # 解码 URL 编码（如 race=%E7%BE%8E%E5%9B%BD）
        if "%" in sname:
            sname = urllib.parse.unquote(sname)
            if "race=" in sname:
                sname = sname.replace("race=", "")
        
        # 拦截上游内部代码
        if "ACG-FAKA" in sname or sname in ["DEFAULT", "默认规格", "Default Option"] or sname.startswith("SKU-"):
            if len(skus) == 1:
                # 单规格商品：提取标题精简名称
                title = p.get("name", "")
                if "（" in title and "）" in title:
                    sname = title.split("（")[1].split("）")[0] + " 独享配置"
                elif "(" in title and ")" in title:
                    sname = title.split("(")[1].split(")")[0] + " 独享配置"
                else:
                    sname = "官方正规独享配置"
            else:
                sname = "标准专属配置"
                
        sku["name"] = sname.strip()

    # 2. 清洗右侧详情文案
    intro = p.get("introduce", "")
    if intro:
        # 移除 8877 原站机械模板废话
        intro = intro.replace("商品信息以实际库存为准，适合需要对应地区、注册年份、好友数量、邮箱类型或2FA状态的用户。", "")
        intro = intro.replace("购买后请及时保存交付内容，并按页面提示完成登录和安全验证。", "")
        intro = intro.replace("交付内容格式：账号----密码----邮箱----邮箱密码----2FA----Token----邮箱地址", "<b>发货格式：</b>账号----密码----邮箱----邮箱密码----2FA/Token")
        
        # 移除建议充余额与死链接
        intro = re.sub(r"🔵?\s*建议使用余额购买[，,][^。<br\n]*[。.]?", "", intro)
        intro = re.sub(r"🔴?\s*自助站点[：:]\s*(<[^>]+>)?\s*点我直达\s*(</[^>]+>)?", "", intro)
        intro = intro.replace("点我直达", "")
        
        # 去除连续 2 次以上的重复句子（如 Grok 出现 3 次的 正规IOS充值）
        intro = re.sub(r"(🔵\s*Grok Super 正规IOS充值\s*（30刀）\s*){2,}", "🔵 Grok Super 官方正规 iOS 渠道充值（30美元档次）", intro)
        intro = re.sub(r"(🔵\s*Grok Super 正规IOS充值\s*\(30刀\)\s*){2,}", "🔵 Grok Super 官方正规 iOS 渠道充值（30美元档次）", intro)
        
        # 压缩多余换行与空段落
        intro = re.sub(r"(<br\s*/?>\s*){3,}", "<br/><br/>", intro)
        intro = re.sub(r"(<p>\s*</p>\s*){2,}", "", intro)
        
        p["introduce"] = intro.strip()

with open("src/data/products.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(">>> products.json 详情文案与规格名称清洗完毕！")
