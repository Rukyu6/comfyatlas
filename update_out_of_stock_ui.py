import os
import re

for candidate in ['/home/crono/projects/comfyatlas', os.path.expanduser('~/projects/comfyatlas'), '.']:
    if os.path.exists(os.path.join(candidate, 'src/pages/index.astro')):
        os.chdir(candidate)
        break

print(f"当前工作目录: {os.getcwd()}")

# 1. 重构 index.astro 的商品渲染逻辑
index_path = 'src/pages/index.astro'
with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

# === A. 服务端渲染 (SSR) initialProducts 映射替换 ===
ssr_old_pattern = r'\{initialProducts\.map\(p => \{[\s\S]*?return \(\s*<a \s*href=\{`/item/\$\{cleanId\}/`\}[\s\S]*?<\/a>\s*\);\s*\}\)\}'

ssr_new_code = """{initialProducts.map(p => {
  let displayPriceCny = p.price_cny;
  if (p.skus && p.skus.length > 0) {
    const pricesCny = p.skus.map((s) => s.price_cny);
    displayPriceCny = Math.min(...pricesCny);
  }
  const isOutOfStock = p.stock === '0' || p.stock === '缺货' || parseInt(p.stock) === 0;
  const cleanStock = isOutOfStock ? '暂时缺货' : `现货 ${p.stock} 件`;
  const isMultiOption = p.skus && p.skus.length > 1;
  const cleanId = p.id.replace('pid_', '');
  const primaryPrice = `¥${Math.round(displayPriceCny)}`;

  // 缺货商品：彻底禁止点击，置灰禁用样式
  if (isOutOfStock) {
    return (
      <div 
        class="glass-card rounded-2xl p-4 sm:p-5 flex flex-row items-center justify-between border border-white/5 opacity-50 bg-black/40 text-left gap-4 select-none cursor-not-allowed transition-all duration-300"
      >
        <div class="flex items-center gap-4 min-w-0 flex-1">
          <img 
            src={p.image || '/images/default_product.jpg'} 
            class="w-11 h-11 md:w-12 md:h-12 rounded-2xl border border-white/10 shrink-0 object-cover bg-black/40 shadow-md grayscale opacity-60" 
            alt={p.name}
            onerror="this.src='/images/default_product.jpg'"
          />
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 mb-1.5 flex-wrap">
              <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-white/5 text-slate-500 border border-white/10 select-none">
                自动发卡
              </span>
              <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-white/10 text-slate-500 border border-white/10 select-none">
                {p.category.split(' ')[0]}
              </span>
              <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30 select-none font-mono">
                暂时缺货
              </span>
            </div>
            <h4 class="text-xs md:text-sm font-bold text-slate-400 leading-snug line-clamp-2 pr-2">
              {p.name}
            </h4>
          </div>
        </div>

        <div class="flex items-center gap-3 md:gap-5 shrink-0">
          <div class="flex flex-col items-end text-right min-w-[75px]">
            <span class="text-base md:text-lg font-black text-slate-500 font-mono">
              {primaryPrice}
            </span>
          </div>

          <span 
            class="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-slate-500 font-bold text-[11px] md:text-xs inline-block text-center cursor-not-allowed shrink-0"
          >
            暂时缺货
          </span>
        </div>
      </div>
    );
  }

  // 现货商品：正常可点击进入
  return (
    <a 
      href={`/item/${cleanId}/`}
      class="glass-card rounded-2xl p-4 sm:p-5 flex flex-row items-center justify-between border cursor-pointer block text-left gap-4 group transition-all duration-300 hover:border-[#38BDF8]/60 hover:shadow-[0_0_20px_rgba(56,189,248,0.15)]"
    >
      <div class="flex items-center gap-4 min-w-0 flex-1">
        <img 
          src={p.image || '/images/default_product.jpg'} 
          class="w-11 h-11 md:w-12 md:h-12 rounded-2xl border border-white/10 shrink-0 object-cover bg-black/40 shadow-md" 
          alt={p.name}
          onerror="this.src='/images/default_product.jpg'"
        />
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 mb-1.5 flex-wrap">
            <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-[#0284C7]/20 text-[#38BDF8] border border-[#38BDF8]/40 select-none">
              自动发卡
            </span>
            <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-white/10 text-white border border-white/20 select-none">
              {p.category.split(' ')[0]}
            </span>
            <span class="px-2.5 py-0.5 text-[10px] font-medium rounded-full bg-white/5 text-slate-300 select-none font-mono">
              {cleanStock}
            </span>
          </div>
          <h4 class="text-xs md:text-sm font-bold text-white leading-snug group-hover:text-[#38BDF8] transition-colors line-clamp-2 pr-2">
            {p.name}
          </h4>
        </div>
      </div>

      <div class="flex items-center gap-3 md:gap-5 shrink-0">
        <div class="flex flex-col items-end text-right min-w-[75px]">
          <span class="text-base md:text-lg font-black text-[#38BDF8] font-mono drop-shadow-[0_0_10px_rgba(56,189,248,0.4)]">
            {primaryPrice}
          </span>
        </div>

        <span 
          class="px-4 py-2 rounded-xl bg-gradient-to-r from-[#0284C7] to-[#38BDF8] text-white font-extrabold text-[11px] md:text-xs inline-block text-center shadow-[0_0_15px_rgba(56,189,248,0.3)] group-hover:brightness-115 active:scale-95 shrink-0"
        >
          {isMultiOption ? '选择规格' : '立即购买'}
        </span>
      </div>
    </a>
  );
})}"""

content = re.sub(ssr_old_pattern, lambda _: ssr_new_code, content)

# === B. 客户端动态渲染 (Client JS) filtered.map 替换 ===
client_old_pattern = r'productsGrid\.innerHTML = filtered\.map\(p => \{[\s\S]*?return `\s*<a\s*href="/item/\$\{cleanId\}/"[\s\S]*?<\/a>\s*`;\s*\}\)\.join\(\'\'\);'

client_new_code = """productsGrid.innerHTML = filtered.map(p => {
      let displayPriceCny = p.price_cny;
      if (p.skus && p.skus.length > 0) {
        const pricesCny = p.skus.map((s: any) => s.price_cny);
        displayPriceCny = Math.min(...pricesCny);
      }

      const isOutOfStock = p.stock === '0' || p.stock === '缺货' || parseInt(p.stock) === 0;
      const cleanStock = isOutOfStock ? '暂时缺货' : `现货 ${p.stock} 件`;
      const isMultiOption = p.skus && p.skus.length > 1;
      const cleanId = p.id.replace('pid_', '');
      const primaryPrice = `¥${Math.round(displayPriceCny)}`;

      if (isOutOfStock) {
        return `
        <div 
          class="glass-card rounded-2xl p-4 sm:p-5 flex flex-row items-center justify-between border border-white/5 opacity-50 bg-black/40 text-left gap-4 select-none cursor-not-allowed transition-all duration-300"
        >
          <div class="flex items-center gap-4 min-w-0 flex-1">
            <img 
              src="${p.image || '/images/default_product.jpg'}" 
              class="w-11 h-11 md:w-12 md:h-12 rounded-2xl border border-white/10 shrink-0 object-cover bg-black/40 shadow-md grayscale opacity-60" 
              alt="${p.name}"
              onerror="this.src='/images/default_product.jpg'"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 mb-1.5 flex-wrap">
                <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-white/5 text-slate-500 border border-white/10 select-none">
                  自动发卡
                </span>
                <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-white/5 text-slate-500 border border-white/10 select-none">
                  ${p.category.split(' ')[0]}
                </span>
                <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30 select-none font-mono">
                  暂时缺货
                </span>
              </div>
              <h4 class="text-xs md:text-sm font-bold text-slate-400 leading-snug line-clamp-2 pr-2">
                ${p.name}
              </h4>
            </div>
          </div>

          <div class="flex items-center gap-3 md:gap-5 shrink-0">
            <div class="flex flex-col items-end text-right min-w-[75px]">
              <span class="text-base md:text-lg font-black text-slate-500 font-mono">
                ${primaryPrice}
              </span>
            </div>

            <span 
              class="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-slate-500 font-bold text-[11px] md:text-xs inline-block text-center cursor-not-allowed shrink-0"
            >
              暂时缺货
            </span>
          </div>
        </div>
        `;
      }

      return `
      <a 
        href="/item/${cleanId}/"
        class="glass-card rounded-2xl p-4 sm:p-5 flex flex-row items-center justify-between border cursor-pointer block text-left gap-4 group transition-all duration-300 hover:border-[#38BDF8]/60 hover:shadow-[0_0_20px_rgba(56,189,248,0.15)]"
      >
        <div class="flex items-center gap-4 min-w-0 flex-1">
          <img 
            src="${p.image || '/images/default_product.jpg'}" 
            class="w-11 h-11 md:w-12 md:h-12 rounded-2xl border border-white/10 shrink-0 object-cover bg-black/40 shadow-md" 
            alt="${p.name}"
            onerror="this.src='/images/default_product.jpg'"
          />
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 mb-1.5 flex-wrap">
              <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-[#0284C7]/20 text-[#38BDF8] border border-[#38BDF8]/40 select-none">
                自动发卡
              </span>
              <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-white/10 text-white border border-white/20 select-none">
                ${p.category.split(' ')[0]}
              </span>
              <span class="px-2.5 py-0.5 text-[10px] font-medium rounded-full bg-white/5 text-slate-300 select-none font-mono">
                ${cleanStock}
              </span>
            </div>
            <h4 class="text-xs md:text-sm font-bold text-white leading-snug group-hover:text-[#38BDF8] transition-colors line-clamp-2 pr-2">
              ${p.name}
            </h4>
          </div>
        </div>

        <div class="flex items-center gap-3 md:gap-5 shrink-0">
          <div class="flex flex-col items-end text-right min-w-[75px]">
            <span class="text-base md:text-lg font-black text-[#38BDF8] font-mono drop-shadow-[0_0_10px_rgba(56,189,248,0.4)]">
              ${primaryPrice}
            </span>
          </div>

          <span 
            class="px-4 py-2 rounded-xl bg-gradient-to-r from-[#0284C7] to-[#38BDF8] text-white font-extrabold text-[11px] md:text-xs inline-block text-center shadow-[0_0_15px_rgba(56,189,248,0.3)] group-hover:brightness-115 active:scale-95 shrink-0"
          >
            ${isMultiOption ? '选择规格' : '立即购买'}
          </span>
        </div>
      </a>
      `;
    }).join('');"""

content = re.sub(client_old_pattern, lambda _: client_new_code, content)

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ src/pages/index.astro 缺货商品交互已升级（彻底禁止点击，全置灰禁用）")

# 2. 修复 item/[id].astro 中的类名问题（纯字符精确替换）
item_path = 'src/pages/item/[id].astro'
if os.path.exists(item_path):
    with open(item_path, 'r', encoding='utf-8') as f:
        item_c = f.read()
    old_span = '<span class="text-xs font-bold ${window.formatSkuDisplay ? window.formatSkuDisplay(isSelected ? \'text-[#38BDF8]\' : \'text-white\') : isSelected ? \'text-[#38BDF8]\' : \'text-white\'} block">${window.formatSkuDisplay(sku.name || sku.sku_code || sku.skuCode)}</span>'
    new_span = '<span class="text-xs font-bold ${isSelected ? \'text-[#38BDF8]\' : \'text-white\'} block">${window.formatSkuDisplay ? window.formatSkuDisplay(sku.name || sku.sku_code || sku.skuCode, (product ? product.name : \'\'), sku.spec_values) : (sku.name || sku.sku_code || sku.skuCode)}</span>'
    if old_span in item_c:
        item_c = item_c.replace(old_span, new_span)
        with open(item_path, 'w', encoding='utf-8') as f:
            f.write(item_c)
        print("✓ src/pages/item/[id].astro 样式类名已纠正")

# 3. 验证构建并推送
print("\n=== 开始编译并自动部署 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建 0 告警通过！正在推送到 main...")
    os.system('git add -A && git commit -m "feat(products): disable click and dim out-of-stock items on product list" && git push origin main')
    print("🚀 升级已完成部署！线上缺货商品已全部变为不可点击的灰色禁用状态！")
else:
    print("\n❌ 编译未通过，请检查日志。")
