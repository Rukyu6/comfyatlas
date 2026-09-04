import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://chuhai91.cc"

print(">>> [1/4] 正在拉取 8877 官方实时分类...")
req = urllib.request.Request(f"{BASE}/api/v1/public/categories", headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, context=ctx, timeout=15)
cats_raw = json.loads(resp.read().decode("utf-8")).get("data", [])

category_map = {}
valid_categories = []
for c in cats_raw:
    cid = str(c["id"])
    cname = c.get("name", {}).get("zh-CN") or c.get("slug", "")
    category_map[cid] = cname
    # 只要存在商品或属于子分类就收录
    if c.get("product_count", 0) > 0 or c.get("parent_id") != 0:
        valid_categories.append({
            "cid": cid,
            "name": cname,
            "slug": c.get("slug", ""),
            "parent_id": c.get("parent_id", 0)
        })

print(f"已同步 8877 分类: {len(valid_categories)} 个")

print(">>> [2/4] 正在全量拉取 8877 真实在售商品（约 2600+ 件）...")
all_products = []
page = 1
while True:
    url = f"{BASE}/api/v1/public/products?per_page=100&page={page}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        res = json.loads(resp.read().decode("utf-8"))
        items = res.get("data", [])
        if not items:
            break
        all_products.extend(items)
        print(f"  - 已同步第 {page} 页，当前累计 {len(all_products)} 件商品")
        page += 1
    except Exception as e:
        print(f"抓取完毕: {e}")
        break

def get_retail_price(cost):
    cost = float(cost)
    if cost <= 0: return 0, 0
    if cost <= 15:
        cny = round(max(cost * 2.5, 25.0))
    elif cost <= 40:
        cny = round(cost * 1.75)
    elif cost <= 120:
        cny = round(cost * 1.5)
    elif cost <= 220:
        cny = round(cost * 1.33)
    else:
        cny = round(cost * 1.25)
    usd = round(cny / 7.2, 1)
    return cny, usd

print(">>> [3/4] 正在清洗商品详情并计算零售利润矩阵...")
transformed = []
for item in all_products:
    cid = str(item.get("category_id"))
    cat_name = category_map.get(cid, item.get("category", {}).get("name", {}).get("zh-CN", "其他"))
    title = item.get("title", {}).get("zh-CN") or item.get("title", {}).get("en-US", "未知商品")
    cost_cny = float(item.get("price_amount", 0))
    price_cny, price_usd = get_retail_price(cost_cny)
    
    images = item.get("images", [])
    img_url = "/images/default_product.jpg"
    if images:
        img_url = images[0] if images[0].startswith("http") else BASE + images[0]
        
    intro = item.get("content", {}).get("zh-CN") or item.get("description", {}).get("zh-CN", "")
    intro = re.sub(r"https?://bz\.chuhai91\.cc[^\s\"\'<>]*", "/guide", intro)
    intro = re.sub(r"https?://(?:www\.)?chuhai91\.cc/blog[^\s\"\'<>]*", "/guide", intro)
    intro = re.sub(r"https?://(?:www\.)?2fa\.run[^\s\"\'<>]*", "/guide#soul-2fa-tool", intro)
    intro = intro.replace("chuhai91.cc", "comfyatlas.com")
    
    is_unlimited = item.get("stock_status") == "unlimited" or item.get("manual_stock_available") == -1
    stock_str = "充足" if is_unlimited else str(item.get("auto_stock_available", 0))
    
    skus_data = []
    for sku in item.get("skus", []):
        s_cost = float(sku.get("price_amount") or cost_cny)
        s_cny, s_usd = get_retail_price(s_cost)
        spec = sku.get("spec_values", {})
        sku_name = "默认规格"
        if isinstance(spec, dict) and spec:
            sku_name = " / ".join(str(v) for v in spec.values())
        elif sku.get("sku_code") and sku.get("sku_code") != "DEFAULT":
            sku_name = sku.get("sku_code")
            
        sku_stock = "充足" if (sku.get("stock_status") == "unlimited" or is_unlimited) else str(sku.get("auto_stock_available", 0))
        skus_data.append({
            "id": f"sku_{sku.get('id')}",
            "name": sku_name,
            "price_cny": s_cny,
            "price_usd": s_usd,
            "cost_cny": s_cost,
            "stock": sku_stock,
            "picture": img_url
        })
        
    transformed.append({
        "id": f"pid_{item.get('id')}",
        "name": title,
        "price_cny": price_cny,
        "price_usd": price_usd,
        "cost_cny": cost_cny,
        "image": img_url,
        "stock": stock_str,
        "cid": cid,
        "category": cat_name,
        "type": "digital",
        "introduce": intro,
        "skus": skus_data
    })

active_cids = set(p["cid"] for p in transformed)
final_categories = [c for c in valid_categories if c["cid"] in active_cids]

final_db = {
    "categories": final_categories,
    "products": transformed
}

with open("src/data/products.json", "w", encoding="utf-8") as f:
    json.dump(final_db, f, ensure_ascii=False, indent=2)

print(f">>> [4/4] 替换成功！已将 Soul Society 全站商品 100% 替换为 8877 真实货源（共 {len(transformed)} 件）！")
