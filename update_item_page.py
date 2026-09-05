with open("src/pages/item/[id].astro", "r", encoding="utf-8") as f:
    code = f.read()

# 替换 selectSku 函数，实现缺货锁定
old_select_sku = '''  function selectSku(sku: any) {
    selectedSku = sku;
    renderSkus();
    if (stockDisplay) stockDisplay.textContent = `现货库存: ${sku.stock} 件`;
    if (stockBadge) stockBadge.textContent = `现货库存: ${sku.stock}`;
    updateQtyDisplay();
  }'''

new_select_sku = '''  function selectSku(sku: any) {
    selectedSku = sku;
    renderSkus();
    
    const isOut = sku.stock === '0' || sku.stock === '缺货' || parseInt(sku.stock) === 0;
    if (stockDisplay) stockDisplay.textContent = isOut ? '暂时缺货' : `现货库存: ${sku.stock} 件`;
    if (stockBadge) {
      stockBadge.textContent = isOut ? '暂时缺货' : `现货库存: ${sku.stock}`;
      stockBadge.className = isOut 
        ? 'text-[10px] font-bold uppercase tracking-wider bg-rose-500/20 text-rose-400 px-2.5 py-0.5 rounded-full border border-rose-500/30'
        : 'text-[10px] font-bold uppercase tracking-wider bg-[#0284C7]/20 text-[#38BDF8] px-2.5 py-0.5 rounded-full border border-[#38BDF8]/30';
    }
    
    // 动态判断加购按钮状态
    if (addToBagBtn) {
      if (isOut) {
        addToBagBtn.setAttribute('disabled', 'true');
        addToBagBtn.className = 'flex-grow sm:flex-grow-0 px-8 py-3.5 rounded-xl bg-slate-800 border border-white/10 text-slate-500 font-extrabold uppercase tracking-wider text-xs cursor-not-allowed transition flex items-center justify-center gap-2';
        addToBagBtn.innerHTML = '<span>暂时缺货 / Out of Stock</span>';
      } else {
        addToBagBtn.removeAttribute('disabled');
        addToBagBtn.className = 'flex-grow sm:flex-grow-0 px-8 py-3.5 rounded-xl bg-gradient-to-r from-[#0284C7] to-[#38BDF8] text-white font-extrabold uppercase tracking-wider text-xs shadow-[0_0_20px_rgba(56,189,248,0.4)] hover:brightness-110 active:scale-95 transition flex items-center justify-center gap-2 cursor-pointer';
        addToBagBtn.innerHTML = '<svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg><span>加入结算清单</span>';
      }
    }
    
    updateQtyDisplay();
  }'''

if old_select_sku in code:
    code = code.replace(old_select_sku, new_select_sku)
    with open("src/pages/item/[id].astro", "w", encoding="utf-8") as f:
        f.write(code)
    print(">>> [id].astro 详情页逻辑升级完成！")
else:
    print(">>> [id].astro 已经更新")
