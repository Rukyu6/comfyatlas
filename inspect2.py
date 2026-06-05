import re

path = '/home/crono/projects/comfyatlas/src/data/products.json'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Inspect actual bytes in the file around the href
idx = content.find('href')
while idx != -1:
    snippet = content[idx:idx+30]
    if 'chuhai' in content[idx:idx+200]:
        print(f"At pos {idx}: bytes = {[hex(ord(c)) for c in snippet]}")
        print(f"Repr: {repr(snippet)}")
        break
    idx = content.find('href', idx+1)
