import re

path = '/home/crono/projects/comfyatlas/src/data/products.json'

with open(path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'chuhai91' in line and 'href' in line:
            print(f'LINE {i+1}:')
            idx = line.find('href')
            print(repr(line[idx:idx+150]))
            print()
            break
