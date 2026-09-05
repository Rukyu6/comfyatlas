import os

print("=== 开始全站全局购物车抽屉联动修复 ===")

# 1. 在 src/layouts/BaseLayout.astro 全局挂载 CartDrawer
base_path = 'src/layouts/BaseLayout.astro'
with open(base_path, 'r', encoding='utf-8') as f:
    base_content = f.read()

if "import CartDrawer from '../components/CartDrawer.astro';" not in base_content:
    base_content = base_content.replace(
        "import TelegramChat from '../components/TelegramChat.astro';",
        "import TelegramChat from '../components/TelegramChat.astro';\nimport CartDrawer from '../components/CartDrawer.astro';"
    )

if "<CartDrawer />" not in base_content:
    base_content = base_content.replace(
        "<TelegramChat />",
        "<CartDrawer />\n    <TelegramChat />"
    )

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(base_content)
print('✓ [1/4] src/layouts/BaseLayout.astro 全局挂载 CartDrawer 完成')

# 2. 清理 index.astro 和 item/[id].astro 中的重复挂载
for p in ['src/pages/index.astro', 'src/pages/item/[id].astro']:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace("import CartDrawer from '../components/CartDrawer.astro';", "// import CartDrawer")
        c = c.replace("import CartDrawer from '../../components/CartDrawer.astro';", "// import CartDrawer")
        c = c.replace("<CartDrawer />", "")
        with open(p, 'w', encoding='utf-8') as f:
            f.write(c)
print('✓ [2/4] 清理单页重复挂载完成')

# 3. 在 src/components/Header.astro 中绑定点击事件与数量徽标
header_path = 'src/components/Header.astro'
with open(header_path, 'r', encoding='utf-8') as f:
    header_content = f.read()

cart_listener_code = """
  // 购物车抽屉点击与角标联动
  function syncHeaderCartBadge() {
    try {
      const cart = JSON.parse(localStorage.getItem('cart') || '[]');
      const count = cart.reduce((total, item) => total + (item.quantity || 1), 0);
      const badge = document.getElementById('cart-count-badge');
      if (badge) {
        if (count > 0) {
          badge.textContent = count > 99 ? '99+' : count.toString();
          badge.classList.remove('hidden');
        } else {
          badge.classList.add('hidden');
        }
      }
    } catch(e) {}
  }

  // 初始同步与侦听
  syncHeaderCartBadge();
  window.addEventListener('cart-updated', syncHeaderCartBadge);
  window.addEventListener('storage', syncHeaderCartBadge);

  // 监听点击打开购物车抽屉
  document.addEventListener('click', (e) => {
    const target = e.target;
    if (target && target.closest('#header-cart-btn')) {
      e.preventDefault();
      e.stopPropagation();
      window.dispatchEvent(new CustomEvent('open-cart'));
    }
  });
"""

if 'syncHeaderCartBadge' not in header_content:
    header_content = header_content.replace("</script>", cart_listener_code + "\n</script>")
    with open(header_path, 'w', encoding='utf-8') as f:
        f.write(header_content)
print('✓ [3/4] src/components/Header.astro 购物车点击与徽标响应注入完成')

# 4. 验证构建
print("\n=== [4/4] 开始编译验证 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建 100% 成功！正在推送 Git...")
    os.system('git add -A && git commit -m "fix(cart): globally mount cart drawer in BaseLayout and wire header cart button click" && git push origin main')
    print("🚀 升级已完成并推送到线上！")
else:
    print("\n❌ 编译未通过，请查看上方输出。")
