with open("src/pages/index.astro", "r", encoding="utf-8") as f:
    content = f.read()

# 替换服务端侧边栏渲染模块
sidebar_marker_start = 'id="desktop-categories-sidebar">'
sidebar_marker_end = '</div>\n\n        <div class="md:col-span-3">'

new_sidebar_jsx = '''id="desktop-categories-sidebar">
          {database.categories.map((cat, idx) => {
            const hasChildren = cat.children && cat.children.length > 0;
            const isFirst = idx === 0;

            return (
              <div class="category-group mb-2" data-group-id={cat.cid}>
                {hasChildren ? (
                  <div>
                    <div class="flex items-center justify-between p-2 rounded-2xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 transition-all duration-200">
                      <button 
                        type="button" 
                        class="flex-1 text-left flex items-center justify-between pr-2 min-w-0 group cursor-pointer category-parent-toggle"
                        data-group-toggle={cat.cid}
                      >
                        <span class="text-xs font-black text-slate-200 group-hover:text-white truncate">{cat.name}</span>
                        <span class="px-2 py-0.5 rounded-full text-[10px] bg-white/5 text-slate-400 group-hover:text-white font-mono shrink-0 ml-1">
                          {cat.total_count}
                        </span>
                      </button>
                      <button 
                        type="button" 
                        class="p-1.5 rounded-xl bg-[#0284C7]/20 hover:bg-[#0284C7]/40 text-[#38BDF8] transition-all cursor-pointer category-chevron-btn shrink-0"
                        data-group-toggle={cat.cid}
                        title="展开/收起细分子类"
                      >
                        <svg class={`w-3.5 h-3.5 transform transition-transform duration-200 ${isFirst ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                    </div>

                    <div id={`submenu-${cat.cid}`} class={`pl-3 mt-1.5 space-y-1 border-l-2 border-[#38BDF8]/20 ml-3.5 ${isFirst ? '' : 'hidden'}`}>
                      {cat.children.map((sub, sIdx) => {
                        const isSubActive = isFirst && sIdx === 0;
                        return (
                          <button 
                            type="button"
                            class={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-all duration-200 border cursor-pointer ${
                              isSubActive 
                                ? 'bg-[#0284C7]/25 text-[#38BDF8] border-[#38BDF8]/60 font-black shadow-[0_0_12px_rgba(56,189,248,0.2)]'
                                : 'text-slate-400 hover:text-white hover:bg-white/[0.04] border-transparent font-medium'
                            }`}
                            data-category-id={sub.cid}
                          >
                            <span class="truncate pr-2">{sub.name}</span>
                            <span class="px-2 py-0.5 rounded-full text-[10px] bg-white/5 text-slate-400 font-mono">
                              {sub.count}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <button 
                    type="button"
                    class="w-full text-left px-3.5 py-2.5 rounded-2xl text-xs flex items-center justify-between transition-all duration-200 border cursor-pointer text-slate-300 hover:text-white hover:bg-white/[0.04] border-white/5 font-medium"
                    data-category-id={cat.cid}
                  >
                    <span class="truncate pr-2 font-bold">{cat.name}</span>
                    <span class="px-2 py-0.5 rounded-full text-[10px] bg-white/5 text-slate-400 font-mono">
                      {cat.total_count}
                    </span>
                  </button>
                )}
              </div>
            );
          })}'''

# 替换侧边栏与脚本控制
if sidebar_marker_start in content:
    start_pos = content.find(sidebar_marker_start) + len(sidebar_marker_start)
    end_pos = content.find(sidebar_marker_end)
    content = content[:start_pos] + new_sidebar_jsx + content[end_pos:]

# 替换客户端交互 script
script_start = '<script>'
script_replacement = '''<script>
  import database from '../data/products.json';

  let activeCategoryId = '';
  let searchQuery = '';

  const productsGrid = document.getElementById('digital-products-grid');
  const searchInput = document.getElementById('search-bar') as HTMLInputElement;

  function init() {
    // 默认激活第一个有效子类或大类
    const firstCat = database.categories[0];
    if (firstCat) {
      if (firstCat.children && firstCat.children.length > 0) {
        activeCategoryId = firstCat.children[0].cid;
      } else {
        activeCategoryId = firstCat.cid;
      }
    }
    bindEvents();
    renderDigitalProducts();
  }

  function bindEvents() {
    // 1. 父级大类折叠展开事件绑定
    document.querySelectorAll('[data-group-toggle]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const groupId = btn.getAttribute('data-group-toggle');
        const submenu = document.getElementById(`submenu-${groupId}`);
        const groupEl = document.querySelector(`[data-group-id="${groupId}"]`);
        const chevron = groupEl?.querySelector('svg');
        
        if (submenu) {
          const isHidden = submenu.classList.contains('hidden');
          if (isHidden) {
            submenu.classList.remove('hidden');
            chevron?.classList.add('rotate-180');
          } else {
            submenu.classList.add('hidden');
            chevron?.classList.remove('rotate-180');
          }
        }
      });
    });

    // 2. 子分类点击过滤
    document.querySelectorAll('[data-category-id]').forEach(btn => {
      btn.addEventListener('click', () => {
        activeCategoryId = btn.getAttribute('data-category-id') || '';
        searchQuery = '';
        if (searchInput) searchInput.value = '';

        // 更新激活样式
        document.querySelectorAll('[data-category-id]').forEach(b => {
          b.classList.remove('bg-[#0284C7]/25', 'text-[#38BDF8]', 'border-[#38BDF8]/60', 'font-black', 'shadow-[0_0_12px_rgba(56,189,248,0.2)]');
          b.classList.add('text-slate-400', 'border-transparent', 'font-medium');
        });
        btn.classList.remove('text-slate-400', 'border-transparent', 'font-medium');
        btn.classList.add('bg-[#0284C7]/25', 'text-[#38BDF8]', 'border-[#38BDF8]/60', 'font-black', 'shadow-[0_0_12px_rgba(56,189,248,0.2)]');

        renderDigitalProducts();
      });
    });
  }

  function renderDigitalProducts() {
    if (!productsGrid) return;

    let filtered = database.products;
    if (searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(q) || 
        p.category.toLowerCase().includes(q)
      );
    } else {
      filtered = filtered.filter(p => p.cid === activeCategoryId);
    }

    if (filtered.length === 0) {
      productsGrid.innerHTML = `
        <div class="col-span-full text-center py-24 text-slate-400 glass-card">
          <p class="font-bold text-white">暂未检索到相关现货</p>
        </div>
      `;
      return;
    }

    productsGrid.innerHTML = filtered.map(p => {
      let displayPriceCny = p.price_cny;
      if (p.skus && p.skus.length > 0) {
        const pricesCny = p.skus.map((s: any) => s.price_cny);
        displayPriceCny = Math.min(...pricesCny);
      }

      const isOutOfStock = p.stock === '0' || p.stock === '缺货';
      const cleanStock = isOutOfStock ? '暂时缺货' : `现货 ${p.stock} 件`;
      const isMultiOption = p.skus && p.skus.length > 1;
      const cleanId = p.id.replace('pid_', '');
      const primaryPrice = `¥${Math.round(displayPriceCny)}`;

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
    }).join('');
  }

  searchInput?.addEventListener('input', (e) => {
    searchQuery = (e.target as HTMLInputElement).value;
    renderDigitalProducts();
  });

  init();
</script>'''

content_before_script = content.split('<script>')[0]
content = content_before_script + script_replacement

with open("src/pages/index.astro", "w", encoding="utf-8") as f:
    f.write(content)

print(">>> index.astro 树状折叠交互升级完成！")
