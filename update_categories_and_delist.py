import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://chuhai91.cc"

print(">>> [1/3] 正在从 8877 拉取父子层级分类数据并建立类目树...")
req = urllib.request.Request(f"{BASE}/api/v1/public/categories", headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, context=ctx, timeout=15)
cats_raw = json.loads(resp.read().decode("utf-8")).get("data", [])

# 1. 过滤掉 图二的【代理与源码搭建】(ID: 22)
cats_raw = [c for c in cats_raw if c["id"] != 22 and "代理与源码搭建" not in c.get("name", {}).get("zh-CN", "")]

# 2. 读取现有 products.json，下架图二四个代理商品
with open("src/data/products.json", "r", encoding="utf-8") as f:
    db = json.load(f)

delist_keywords = ["专属代理分站", "机器人代理", "全自动TG电报号发卡系统出售", "各类电报机器人/网站源码", "代理与源码搭建"]
cleaned_products = []
delisted_count = 0

for p in db.get("products", []):
    name = p.get("name", "")
    cid = str(p.get("cid", ""))
    cat = p.get("category", "")
    
    # 命中图二下架条件
    if cid == "22" or cat == "代理与源码搭建" or any(kw in name for kw in delist_keywords):
        delisted_count += 1
        continue
    cleaned_products.append(p)

print(f"已成功下架图二相关代理商品: {delisted_count} 件！")

# 统计每个细分子分类的真实商品数
prod_cid_counts = {}
for p in cleaned_products:
    c = str(p["cid"])
    prod_cid_counts[c] = prod_cid_counts.get(c, 0) + 1

# 3. 组装父子树状类目结构
parents = []
children_by_parent = {}

for c in cats_raw:
    cid = str(c["id"])
    cname = c.get("name", {}).get("zh-CN") or c.get("slug", "")
    pid = c.get("parent_id", 0)
    
    if pid == 0:
        parents.append({
            "cid": cid,
            "name": cname,
            "slug": c.get("slug", ""),
            "sort_order": c.get("sort_order", 0)
        })
    else:
        children_by_parent.setdefault(str(pid), []).append({
            "cid": cid,
            "name": cname,
            "slug": c.get("slug", ""),
            "count": prod_cid_counts.get(cid, 0),
            "sort_order": c.get("sort_order", 0)
        })

# 排序并组装最终树
parents.sort(key=lambda x: x["sort_order"], reverse=True)

hierarchical_categories = []
for p in parents:
    pid = p["cid"]
    subs = children_by_parent.get(pid, [])
    # 按排序字段排序
    subs.sort(key=lambda x: x["sort_order"], reverse=True)
    
    # 计算大类的总件数
    if subs:
        total_cnt = sum(s["count"] for s in subs)
    else:
        total_cnt = prod_cid_counts.get(pid, 0)
    
    # 只要有商品就收录
    if total_cnt > 0:
        hierarchical_categories.append({
            "cid": pid,
            "name": p["name"],
            "slug": p["slug"],
            "total_count": total_cnt,
            "children": subs
        })

print(f">>> [2/3] 树状分类重构完毕，共建立 {len(hierarchical_categories)} 个一级大类及下属细分类目！")

db["categories"] = hierarchical_categories
db["products"] = cleaned_products

with open("src/data/products.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(">>> [3/3] products.json 数据更新完毕！")
