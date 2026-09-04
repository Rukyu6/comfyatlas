import json, re, os, urllib.request

img_dir = "public/images/products"
os.makedirs(img_dir, exist_ok=True)

with open("src/data/products.json", "r", encoding="utf-8") as f:
    db = json.load(f)

download_map = {}
for p in db.get("products", []):
    intro = p.get("introduce", "")
    if intro:
        for src in re.findall(r"src=[\x27\"]([^\x27\"]+)[\x27\"]", intro):
            if src.startswith("/assets/"):
                download_map[src] = "https://chuhai91.cc" + src
            elif "chuhai91.cc" in src:
                download_map[src] = src
    img = p.get("image", "")
    if img and "chuhai91.cc" in img:
        download_map[img] = img

url_to_local = {}
print(f"扫描到 {len(download_map)} 个图片资源，开始从 8877 抓取...")
for key, full_url in download_map.items():
    try:
        fname = full_url.split("/")[-1].split("?")[0]
        if not fname or len(fname) < 4:
            continue
        local_file = os.path.join(img_dir, fname)
        if not os.path.exists(local_file):
            req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                with open(local_file, "wb") as out_f:
                    out_f.write(resp.read())
        url_to_local[key] = f"/images/products/{fname}"
        if full_url != key:
            url_to_local[full_url] = f"/images/products/{fname}"
    except Exception:
        if key.startswith("/assets/"):
            url_to_local[key] = f"https://chuhai91.cc{key}"

for p in db.get("products", []):
    if p.get("image") in url_to_local:
        p["image"] = url_to_local[p["image"]]
    for sku in p.get("skus", []):
        if sku.get("picture") in url_to_local:
            sku["picture"] = url_to_local[sku["picture"]]
    intro = p.get("introduce", "")
    if intro:
        for old_src, new_src in url_to_local.items():
            intro = intro.replace(old_src, new_src)
        intro = re.sub(r"https?://bz\.chuhai91\.cc[^\s\"\'<>]*", "/guide", intro)
        intro = re.sub(r"https?://(?:www\.)?chuhai91\.cc/blog[^\s\"\'<>]*", "/guide", intro)
        intro = re.sub(r"https?://(?:www\.)?2fa\.run[^\s\"\'<>]*", "/guide#soul-2fa-tool", intro)
        intro = re.sub(r"https?://jf7p5fl5cwo\.sg\.larksuite\.com[^\s\"\'<>]*", "/guide", intro)
        intro = intro.replace("bz.chuhai91.cc", "comfyatlas.com/guide")
        intro = intro.replace("chuhai91.cc", "comfyatlas.com")
        intro = intro.replace("Puppy Shop", "Soul Society").replace("puppyshop", "Soul Society")
        p["introduce"] = intro

with open("src/data/products.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(">>> 图片抓取与链接清洗完成!")