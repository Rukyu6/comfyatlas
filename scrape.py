import urllib.request
import re
import json
import html
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Target base URL
base_url = "https://chuhai91.cc"

def fetch_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        # Silently fail or log minimally
        return ""

def parse_embedded_json(html_content):
    """
    Locates and parses the setVar("item", {...}) object from HTML
    """
    marker = 'setVar("item",'
    start_idx = html_content.find(marker)
    if start_idx == -1:
        return None
    
    # Find the opening brace of the JSON object
    brace_start = html_content.find('{', start_idx)
    if brace_start == -1:
        return None
    
    # Scan characters to find the matching closing brace
    brace_count = 0
    chars = []
    for i in range(brace_start, len(html_content)):
        char = html_content[i]
        chars.append(char)
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                break
                
    json_str = "".join(chars)
    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"JSON load error: {e}")
        return None

def scrape_single_product_details(p):
    pid = p['id'].replace('pid_', '')
    item_url = f"{base_url}/item?id={pid}"
    item_html = fetch_url(item_url)
    if not item_html:
        return p
    
    item_data = parse_embedded_json(item_html)
    if not item_data:
        return p
    
    # Extract Description (introduce)
    # introduce can be in source or root
    introduce = ""
    if 'source' in item_data and isinstance(item_data['source'], dict):
        introduce = item_data['source'].get('introduce', '')
    if not introduce:
        introduce = item_data.get('introduce', '')
        
    # Clean up the introduce HTML slightly
    if introduce:
        # Remove empty paragraphs or useless styles if needed, but keeping HTML structure
        introduce = introduce.strip()
    
    # Extract SKUs
    skus_raw = item_data.get('sku', [])
    skus = []
    for sku in skus_raw:
        s_price = float(sku.get('price', '0'))
        skus.append({
            'id': f"sku_{sku.get('id', '')}",
            'name': sku.get('name', 'Default Option'),
            'price_cny': s_price,
            'price_usd': round(s_price / 6.8, 2),
            'stock': sku.get('stock', '0'),
            'picture': sku.get('picture_url') or p['image']
        })
        
    p['introduce'] = introduce
    p['skus'] = skus
    return p

def scrape_products():
    print("Fetching homepage to find categories...")
    home_html = fetch_url(base_url)
    if not home_html:
        print("Failed to load homepage.")
        return

    category_pattern = r'href="/\?cid=(\d+)"[^>]*>.*?<span class="nav-main-link-name">(.*?)</span>'
    categories_raw = re.findall(category_pattern, home_html, re.DOTALL)
    
    categories = []
    seen_cids = set()
    for cid, name in categories_raw:
        if cid in seen_cids:
            continue
        seen_cids.add(cid)
        clean_name = re.sub(r'<[^>]+>', '', name).strip()
        clean_name = re.sub(r'\s+', ' ', clean_name)
        categories.append({'cid': cid, 'name': clean_name})

    print(f"Found {len(categories)} categories.")
    
    initial_products = []
    
    for cat in categories:
        cid = cat['cid']
        cat_name = cat['name']
        
        cat_url = f"{base_url}/?cid={cid}"
        cat_html = fetch_url(cat_url)
        if not cat_html:
            continue
            
        blocks = re.findall(r'<a class="home-row-link" href="/item\?id=\d+">.*?</a>', cat_html, re.DOTALL)
        
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
                        
                    price_num = 0.0
                    price_match_num = re.search(r'[\d\.]+', price_str)
                    if price_match_num:
                        price_num = float(price_match_num.group(0))
                        
                    initial_products.append({
                        'id': f"pid_{pid}",
                        'name': title,
                        'price_cny': price_num,
                        'price_usd': round(price_num / 6.8, 2),
                        'image': img_url,
                        'stock': stock,
                        'cid': cid,
                        'category': cat_name,
                        'type': 'digital',
                        'introduce': '',
                        'skus': []
                    })
            except Exception as ex:
                pass
                
    total_to_scrape = len(initial_products)
    print(f"Found {total_to_scrape} products in catalog. Scraping details concurrently...")
    
    detailed_products = []
    
    # Run requests concurrently using ThreadPoolExecutor
    # 20 workers to get fast results without rate-limiting
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(scrape_single_product_details, p): p for p in initial_products}
        
        completed_count = 0
        for future in as_completed(futures):
            try:
                res = future.result()
                detailed_products.append(res)
            except Exception as e:
                orig = futures[future]
                detailed_products.append(orig)
                
            completed_count += 1
            if completed_count % 50 == 0 or completed_count == total_to_scrape:
                print(f"  Progress: {completed_count}/{total_to_scrape} details crawled...")
                
    end_time = time.time()
    print(f"Details crawled in {end_time - start_time:.2f} seconds.")
    print(f"Scraping complete. Total detailed products: {len(detailed_products)}")
    
    output_data = {
        'categories': categories,
        'products': detailed_products
    }
    
    with open('/home/crono/projects/comfyatlas/src/data/products.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print("Successfully wrote detailed data to src/data/products.json")

if __name__ == "__main__":
    scrape_products()
