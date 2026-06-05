import re

path = '/home/crono/projects/comfyatlas/src/data/products.json'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# In the actual file, escaped quotes are stored as \"  (backslash + double-quote)
# So an anchor tag in the JSON string looks like:
#   <a href=\"https://bz.chuhai91.cc/\" target=\"_blank\" ...>link text</a>
# The backslash is a real backslash character (0x5c), quote is 0x22.

before = content.count('chuhai91.cc') + content.count('chuhai.store')
print(f"Total chuhai references in file: {before}")

href_before = len(re.findall(r'<a\s[^>]*href=\\"https?://[^"]*chuhai', content))
print(f"Anchor tags pointing to chuhai: {href_before}")

# Strip <a href=\"https://...chuhai...\">text</a>  ->  text
cleaned = re.sub(
    r'<a\s[^>]*href=\\"https?://[^\\"]*chuhai[^\\"]*\\"[^>]*>(.*?)</a>',
    r'\1',
    content,
    flags=re.DOTALL
)

href_after = len(re.findall(r'<a\s[^>]*href=\\"https?://[^"]*chuhai', cleaned))
print(f"Anchor tags remaining after cleanup: {href_after}")

if href_before > 0 and href_after < href_before:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f"SUCCESS: Removed {href_before - href_after} chuhai anchor links. File saved.")
elif href_before == 0:
    print("No chuhai anchor links found.")
else:
    print("WARNING: Regex did not match, file NOT changed.")
