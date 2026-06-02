import urllib.request
import re
import json
import html

# Target base URL
base_url = "https://chuhai91.cc"

def fetch_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def scrape_products():
    print("Fetching homepage to find categories...")
    home_html = fetch_url(base_url)
    if not home_html:
        print("Failed to load homepage.")
        return

    # Regex to find categories: href="/?cid=XX" and category name
    # e.g., <a class="nav-main-link" href="/?cid=67"> ... <span class="nav-main-link-name">Apple苹果ID【<font color="#f9963b">带密保</font>】
    category_pattern = r'href="/\?cid=(\d+)"[^>]*>.*?<span class="nav-main-link-name">(.*?)</span>'
    categories_raw = re.findall(category_pattern, home_html, re.DOTALL)
    
    categories = []
    seen_cids = set()
    for cid, name in categories_raw:
        if cid in seen_cids:
            continue
        seen_cids.add(cid)
        # Clean HTML tags from name
        clean_name = re.sub(r'<[^>]+>', '', name).strip()
        # Clean double spaces or linebreaks
        clean_name = re.sub(r'\s+', ' ', clean_name)
        categories.append({'cid': cid, 'name': clean_name})

    print(f"Found {len(categories)} categories.")
    
    all_products = []
    
    for cat in categories:
        cid = cat['cid']
        cat_name = cat['name']
        print(f"Scraping category {cid}: {cat_name}...")
        
        cat_url = f"{base_url}/?cid={cid}"
        cat_html = fetch_url(cat_url)
        if not cat_html:
            continue
            
        # Regex to find product rows
        # E.g. <a class="home-row-link" href="/item?id=6188"> ...
        product_row_pattern = r'<a class="home-row-link" href="/item\?id=(\d+)">.*?<div class="home-list-row-title">(.*?)</div>.*?<div class="home-list-td-price">([^<]+)</div>'
        products_raw = re.findall(product_row_pattern, cat_html, re.DOTALL)
        
        # We also need images for products, let's extract them
        # We can extract the entire block and parse it carefully
        blocks = re.findall(r'<a class="home-row-link" href="/item\?id=\d+">.*?</a>', cat_html, re.DOTALL)
        
        cat_products_count = 0
        for block in blocks:
            try:
                id_match = re.search(r'href="/item\?id=(\d+)"', block)
                title_match = re.search(r'<div class="home-list-row-title">(.*?)</div>', block)
                price_match = re.search(r'<div class="home-list-td-price">([^<]+)</div>', block)
                img_match = re.search(r'src="([^"]+)"', block)
                stock_match = re.search(r'<span class="home-list-stock-only">([^<]+)</span>', block)
                if not stock_match:
                    stock_match = re.search(r'<span class="home-meta-v home-meta-stock">([^<]+)</span>', block)
                
                if id_match and title_match and price_match:
                    pid = id_match.group(1)
                    title = html.unescape(title_match.group(1).strip())
                    price_str = price_match.group(1).strip()
                    img_url = img_match.group(1).strip() if img_match else "/images/book.png"
                    stock = stock_match.group(1).strip() if stock_match else "In Stock"
                    
                    if img_url.startswith("/"):
                        img_url = base_url + img_url
                        
                    # Extract price float
                    price_num = 0.0
                    price_match_num = re.search(r'[\d\.]+', price_str)
                    if price_match_num:
                        price_num = float(price_match_num.group(0))
                        
                    all_products.append({
                        'id': f"pid_{pid}",
                        'name': title,
                        'price_cny': price_num,
                        'price_usd': round(price_num / 6.8, 2), # Exchange rate 6.8 roughly
                        'image': img_url,
                        'stock': stock,
                        'cid': cid,
                        'category': cat_name,
                        'type': 'digital'
                    })
                    cat_products_count += 1
            except Exception as ex:
                print(f"Error parsing product block: {ex}")
                
        print(f"  Found {cat_products_count} products.")
        
    print(f"Scraping complete. Total products: {len(all_products)}")
    
    # Save to data directory
    output_data = {
        'categories': categories,
        'products': all_products
    }
    
    with open('/home/crono/projects/comfyatlas/src/data/products.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print("Successfully wrote data to src/data/products.json")

if __name__ == "__main__":
    scrape_products()
