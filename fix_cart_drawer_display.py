import os
import re

print("=== 1. 检查并清理 index.astro 中重复挂载的 CartDrawer ===")
index_path = "src/pages/index.astro"
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    orig = content
    # 如果 index.astro 里有独立的 <CartDrawer />，由于 BaseLayout 已有，移除它防止 DOM 节点重复
    content = re.sub(r'<\s*CartDrawer\s*\/?>', '', content)
    content = re.sub(r'import\s+CartDrawer\s+from\s+[\'"][^\'"]+CartDrawer\.astro[\'"];?', '', content)
    if content != orig:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✓ 已清理 index.astro 中重复的 CartDrawer 挂载")

print("=== 2. 重塑 CartDrawer.astro 结构与滑入滑出逻辑 ===")
cart_component_path = "src/components/CartDrawer.astro"

new_cart_drawer = '''---
// 全局购物车侧边抽屉组件
---
<!-- 购物车全局容器 -->
<div id="cart-drawer" class="fixed inset-0 z-[9999] hidden">
  <!-- 1. 背景毛玻璃遮罩 -->
  <div 
    id="cart-overlay" 
    onclick="window.closeCart()" 
    class="absolute inset-0 bg-black/70 backdrop-blur-md transition-opacity duration-300 opacity-0 cursor-pointer"
  ></div>

  <!-- 2. 右侧滑出面板 -->
  <div 
    id="cart-panel" 
    class="absolute top-0 right-0 h-full w-full max-w-md bg-[#080B12] border-l border-white/10 shadow-2xl flex flex-col transform transition-transform duration-300 ease-out translate-x-full z-10"
  >
    <!-- 头部 -->
    <div class="p-5 border-b border-white/10 flex items-center justify-between bg-[#0B0F19]">
      <div class="flex items-center gap-2.5">
        <div class="p-2 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-white tracking-wide">结算清单</h3>
          <p class="text-xs text-slate-400">SOUL SOCIETY VAULT</p>
        </div>
      </div>
      <button 
        onclick="window.closeCart()" 
        class="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        aria-label="关闭"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- 列表展示区 -->
    <div id="cart-items-list" class="flex-1 overflow-y-auto p-5 space-y-3">
      <!-- 动态渲染商品项 -->
    </div>

    <!-- 底部结算栏 -->
    <div class="p-5 border-t border-white/10 bg-[#0B0F19]/80 backdrop-blur-sm space-y-4">
      <div class="flex items-center justify-between">
        <span class="text-sm text-slate-400 font-medium">合计金额</span>
        <span class="text-2xl font-bold text-sky-400 font-mono" id="cart-total-amount">¥0.00</span>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <button 
          onclick="window.clearCart()" 
          class="py-3 px-4 rounded-xl border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 text-sm font-medium transition-all text-center"
        >
          清空清单
        </button>
        <button 
          id="cart-checkout-btn"
          onclick="window.goToCheckout()" 
          class="py-3 px-4 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 hover:from-sky-400 hover:to-cyan-400 text-white text-sm font-semibold shadow-lg shadow-sky-500/20 transition-all text-center"
        >
          立即结算
        </button>
      </div>
    </div>
  </div>
</div>

<script is:inline>
// 全局购物车交互逻辑
window.openCart = function() {
  const drawer = document.getElementById('cart-drawer');
  const overlay = document.getElementById('cart-overlay');
  const panel = document.getElementById('cart-panel');
  if (!drawer || !panel) return;

  drawer.classList.remove('hidden');
  // 触发重绘以平滑展示过渡动画
  void drawer.offsetWidth;

  if (overlay) {
    overlay.classList.remove('opacity-0');
    overlay.classList.add('opacity-100');
  }
  panel.classList.remove('translate-x-full');
  panel.classList.add('translate-x-0');

  window.renderCartItems();
};

window.closeCart = function() {
  const drawer = document.getElementById('cart-drawer');
  const overlay = document.getElementById('cart-overlay');
  const panel = document.getElementById('cart-panel');
  if (!drawer || !panel) return;

  if (overlay) {
    overlay.classList.remove('opacity-100');
    overlay.classList.add('opacity-0');
  }
  panel.classList.remove('translate-x-0');
  panel.classList.add('translate-x-full');

  setTimeout(() => {
    drawer.classList.add('hidden');
  }, 300);
};

window.getCart = function() {
  try {
    return JSON.parse(localStorage.getItem('cart') || '[]');
  } catch (e) {
    return [];
  }
};

window.setCart = function(items) {
  localStorage.setItem('cart', JSON.stringify(items));
  window.updateCartBadge();
};

window.updateCartBadge = function() {
  const cart = window.getCart();
  const totalCount = cart.reduce((acc, item) => acc + (parseInt(item.quantity) || 1), 0);
  const badges = document.querySelectorAll('#header-cart-count, .cart-badge');
  badges.forEach(b => {
    b.textContent = totalCount;
    if (totalCount > 0) {
      b.classList.remove('hidden');
    } else {
      b.classList.add('hidden');
    }
  });
};

window.clearCart = function() {
  if (confirm('确定要清空购物车清单吗？')) {
    window.setCart([]);
    window.renderCartItems();
  }
};

window.updateItemQty = function(index, delta) {
  const cart = window.getCart();
  if (cart[index]) {
    cart[index].quantity = (parseInt(cart[index].quantity) || 1) + delta;
    if (cart[index].quantity <= 0) {
      cart.splice(index, 1);
    }
    window.setCart(cart);
    window.renderCartItems();
  }
};

window.removeItem = function(index) {
  const cart = window.getCart();
  cart.splice(index, 1);
  window.setCart(cart);
  window.renderCartItems();
};

window.renderCartItems = function() {
  const listEl = document.getElementById('cart-items-list');
  const totalEl = document.getElementById('cart-total-amount');
  const checkoutBtn = document.getElementById('cart-checkout-btn');
  if (!listEl) return;

  const cart = window.getCart();
  let total = 0;

  if (cart.length === 0) {
    listEl.innerHTML = `
      <div class="h-64 flex flex-col items-center justify-center text-center">
        <div class="p-4 rounded-2xl bg-white/5 text-slate-500 mb-3">
          <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <p class="text-sm text-slate-400 font-medium">清单空空如也</p>
        <p class="text-xs text-slate-500 mt-1">快去挑选心仪的数字商品吧</p>
      </div>
    `;
    if (totalEl) totalEl.textContent = '¥0.00';
    if (checkoutBtn) checkoutBtn.disabled = true;
    return;
  }

  if (checkoutBtn) checkoutBtn.disabled = false;

  let html = '';
  cart.forEach((item, idx) => {
    const price = parseFloat(item.price || item.priceAmount || 0);
    const qty = parseInt(item.quantity) || 1;
    total += price * qty;
    
    // 经由汉化引擎翻译
    const skuDisplay = window.formatSkuDisplay ? window.formatSkuDisplay(item.skuName || item.sku || item.name, item.title) : (item.skuName || item.sku || '标准规格');

    html += `
      <div class="p-4 rounded-2xl bg-white/5 border border-white/10 flex flex-col gap-3">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h4 class="text-sm font-medium text-white leading-snug">${item.title || '数字资产'}</h4>
            <div class="text-xs text-sky-400 mt-1 flex items-center gap-1.5 font-mono">
              <span class="inline-block w-1.5 h-1.5 rounded-full bg-sky-400"></span>
              ${skuDisplay}
            </div>
          </div>
          <button onclick="window.removeItem(${idx})" class="text-slate-500 hover:text-rose-400 transition-colors p-1">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-white/5">
          <div class="flex items-center border border-white/10 rounded-lg overflow-hidden bg-black/30">
            <button onclick="window.updateItemQty(${idx}, -1)" class="w-7 h-7 flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/10">-</button>
            <span class="w-8 text-center text-xs font-mono text-white">${qty}</span>
            <button onclick="window.updateItemQty(${idx}, 1)" class="w-7 h-7 flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/10">+</button>
          </div>
          <span class="text-sm font-semibold text-white font-mono">¥${(price * qty).toFixed(2)}</span>
        </div>
      </div>
    `;
  });

  listEl.innerHTML = html;
  if (totalEl) totalEl.textContent = '¥' + total.toFixed(2);
};

window.goToCheckout = function() {
  const cart = window.getCart();
  if (cart.length === 0) return;
  // 直接跳转结算流程
  window.location.href = '/checkout';
};

// 页面载入时初始化角标
document.addEventListener('DOMContentLoaded', () => {
  window.updateCartBadge();
});
</script>
'''

with open(cart_component_path, "w", encoding="utf-8") as f:
    f.write(new_cart_drawer)
print("✓ 已重塑 CartDrawer.astro 结构并彻底修复层级动画与显示逻辑！")

print("=== 3. 部署并验证构建 ===")
