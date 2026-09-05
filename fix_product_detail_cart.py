import os
import re

print("=== 1. 将 CartDrawer 挂载至全局 BaseLayout.astro ===")
base_layout_path = "src/layouts/BaseLayout.astro"

if os.path.exists(base_layout_path):
    with open(base_layout_path, "r", encoding="utf-8") as f:
        content = f.read()

    orig = content

    # 1. 确保在 frontmatter 导入 CartDrawer
    if "CartDrawer" not in content:
        # 在顶部 frontmatter 注入 import CartDrawer
        content = re.sub(
            r'(---\s*\n)',
            r"\1import CartDrawer from '../components/CartDrawer.astro';\n",
            content,
            count=1
        )

    # 2. 确保在 <body> 底部注入 <CartDrawer />
    if "<CartDrawer" not in content:
        if "</body>" in content:
            content = content.replace("</body>", "  <CartDrawer />\n</body>")
        elif "</slot>" in content:
            content = content.replace("</slot>", "</slot>\n  <CartDrawer />")
        else:
            content = content + "\n<CartDrawer />"

    if content != orig:
        with open(base_layout_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ 成功在 {base_layout_path} 中挂载全局 CartDrawer 组件！")
    else:
        print(f"✓ {base_layout_path} 已存在 CartDrawer 挂载。")

print("\n=== 2. 检查商品详情页组件，确保全局可用 ===")
# 检查所有的 product 页面文件
for root, _, files in os.walk("src/pages"):
    for f in files:
        if f.endswith(".astro") and ("product" in f or "[id]" in f or "[slug]" in f):
            p_path = os.path.join(root, f)
            with open(p_path, "r", encoding="utf-8") as file:
                p_content = file.read()
            
            # 如果该页面没有使用 BaseLayout，则单独确保挂载 CartDrawer
            if "BaseLayout" not in p_content and "<CartDrawer" not in p_content:
                if "import CartDrawer" not in p_content:
                    p_content = re.sub(r'(---\s*\n)', r"\1import CartDrawer from '../../components/CartDrawer.astro';\n", p_content, count=1)
                p_content = p_content.replace("</body>", "  <CartDrawer />\n</body>")
                with open(p_path, "w", encoding="utf-8") as file:
                    file.write(p_content)
                print(f"✓ 已为独立商品页注入 CartDrawer: {p_path}")

print("\n=== 3. 检查并确保 Header.astro 购物车按钮事件完整绑定 ===")
header_path = "src/components/Header.astro"
if os.path.exists(header_path):
    with open(header_path, "r", encoding="utf-8") as f:
        h_content = f.read()

    orig_h = h_content

    # 确保 #header-cart-btn 拥有原生 onclick 调用 window.openCart()
    h_content = re.sub(
        r'(<button\b[^>]*id="header-cart-btn"[^>]*)>',
        lambda m: m.group(1) + ' onclick="if(window.openCart){window.openCart();}else{console.log(\'Cart initializing...\');}">' if "onclick=" not in m.group(1) else m.group(0),
        h_content
    )

    if h_content != orig_h:
        with open(header_path, "w", encoding="utf-8") as f:
            f.write(h_content)
        print("✓ 已加固 Header.astro 购物车按钮触发机制")

print("\n=== 4. 检查 CartDrawer.astro 客户端脚本暴露 ===")
cart_path = "src/components/CartDrawer.astro"
if os.path.exists(cart_path):
    with open(cart_path, "r", encoding="utf-8") as f:
        c_content = f.read()

    orig_c = c_content

    # 保证包含 window.openCart 暴露
    if "window.openCart" not in c_content:
        helper = """
<script is:inline>
window.openCart = function() {
  const drawer = document.getElementById('cart-drawer');
  const overlay = document.getElementById('cart-overlay');
  const panel = document.getElementById('cart-panel');
  if (drawer) drawer.classList.remove('hidden');
  if (overlay) overlay.classList.remove('opacity-0');
  if (panel) {
    panel.classList.remove('translate-x-full');
    panel.classList.add('translate-x-0');
  }
  if (window.renderCartItems) window.renderCartItems();
};
window.closeCart = function() {
  const drawer = document.getElementById('cart-drawer');
  const panel = document.getElementById('cart-panel');
  if (panel) {
    panel.classList.add('translate-x-full');
    panel.classList.remove('translate-x-0');
  }
  setTimeout(() => {
    if (drawer) drawer.classList.add('hidden');
  }, 300);
};
</script>
"""
        c_content = c_content + "\n" + helper
        with open(cart_path, "w", encoding="utf-8") as f:
            f.write(c_content)
        print("✓ 已注入 CartDrawer 全局 openCart / closeCart 控制函数")

print("\n=== 5. 编译构建并推送部署 ===")
