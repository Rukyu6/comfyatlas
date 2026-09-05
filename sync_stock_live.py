import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://chuhai91.cc"

print(">>> [1/3] 正在全量请求 8877 官方库存 API（分页拉取 2600+ 商品实时库存）...")
live_stock_map = {}
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
            
        for item in items:
            pid = str(item.get("id"))
            # 判断商品总库存
            is_unlimited = item.get("stock_status") == "unlimited" or item.get("manual_stock_available") == -1
            is_sold_out = item.get("is_sold_out", False) or item.get("stock_status") == "out_of_stock"
            auto_qty = item.get("auto_stock_available", 0)
            
            if is_unlimited:
                prod_stock = "充足"
            elif is_sold_out or auto_qty <= 0:
                prod_stock = "0"
            else:
                prod_stock = str(auto_qty)
                
            # SKU 细分库存
            skus_stock = {}
            for sku in item.get("skus", []):
                sid = str(sku.get("id"))
                sku_unlimited = sku.get("stock_status") == "unlimited" or is_unlimited
                sku_sold_out = sku.get("is_sold_out", False) or sku.get("stock_status") == "out_of_stock"
                sku_qty = sku.get("auto_stock_available", 0)
                
                if sku_unlimited:
                    skus_stock[sid] = "充足"
                elif sku_sold_out or sku_qty <= 0:
                    skus_stock[sid] = "0"
                else:
                    skus_stock[sid] = str(sku_qty)
                    
            live_stock_map[pid] = {
                "prod_stock": prod_stock,
                "skus_stock": skus_stock
            }
            
        print(f"  - 第 {page} 页库存拉取完毕，已核对 {len(live_stock_map)} 件商品实时库存")
        page += 1
    except Exception as e:
        print(f"库存抓取完成: {e}")
        break

print(f">>> 成功获取 8877 官方 {len(live_stock_map)} 件在售商品的实时库存数据！")

# 2. 对齐更新本地 products.json
print(">>> [2/3] 正在对齐 Soul Society 数据库商品及各规格库存...")
with open("src/data/products.json", "r", encoding="utf-8") as f:
    db = json.load(f)

in_stock_count = 0
out_of_stock_count = 0
updated_prods = 0

for p in db.get("products", []):
    raw_id = p.get("id", "").replace("pid_", "")
    
    if raw_id in live_stock_map:
        info = live_stock_map[raw_id]
        p["stock"] = info["prod_stock"]
        
        # 同步各 SKU
        for sku in p.get("skus", []):
            raw_sku_id = sku.get("id", "").replace("sku_", "")
            if raw_sku_id in info["skus_stock"]:
                sku["stock"] = info["skus_stock"][raw_sku_id]
            else:
                sku["stock"] = info["prod_stock"]
                
        if p["stock"] == "0":
            out_of_stock_count += 1
        else:
            in_stock_count += 1
        updated_prods += 1
    else:
        # 8877 已下架或不存在的设为缺货
        p["stock"] = "0"
        for sku in p.get("skus", []):
            sku["stock"] = "0"
        out_of_stock_count += 1

# 3. 重新校准类目现货计数
prod_cid_counts = {}
for p in db.get("products", []):
    cid = str(p["cid"])
    prod_cid_counts[cid] = prod_cid_counts.get(cid, 0) + 1

for cat in db.get("categories", []):
    subs = cat.get("children", [])
    if subs:
        for sub in subs:
            sub["count"] = prod_cid_counts.get(str(sub["cid"]), 0)
        cat["total_count"] = sum(s["count"] for s in subs)
    else:
        cat["total_count"] = prod_cid_counts.get(str(cat["cid"]), 0)

with open("src/data/products.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f">>> [3/3] 库存同步完毕！")
print(f"    - 总同步商品: {updated_prods} 件")
print(f"    - 现货在售: {in_stock_count} 件")
print(f"    - 售罄缺货: {out_of_stock_count} 件")
