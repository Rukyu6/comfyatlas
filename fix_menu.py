import os

print("=== 开始升级顶部用户菜单与退出机制 ===")

# 1. 深度重构 src/components/Header.astro
header_path = 'src/components/Header.astro'

new_header_code = """---
// Header.astro - Soul Society Dark High-Tech
---

<header class="fixed top-0 left-0 right-0 z-50 bg-[#06080F]/80 backdrop-blur-xl border-b border-white/5 transition-all duration-300">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
    
    <!-- Logo & Brand -->
    <a href="/" class="flex items-center gap-3 group shrink-0">
      <div class="relative w-9 h-9 rounded-xl overflow-hidden border border-[#38BDF8]/30 group-hover:border-[#38BDF8] transition-all shadow-[0_0_15px_rgba(56,189,248,0.2)]">
        <img 
          src="/images/soul_society_logo.jpg" 
          alt="Soul Society Logo" 
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
      <div class="flex flex-col">
        <span class="text-sm font-black tracking-wider text-white group-hover:text-[#38BDF8] transition-colors font-mono">SOUL SOCIETY</span>
        <span class="text-[9px] text-slate-400 font-mono tracking-widest uppercase">CORP. DIGITAL VAULT</span>
      </div>
    </a>

    <!-- Right Controls: Language Switcher + Cart + Auth -->
    <div class="flex items-center gap-2 sm:gap-3">
      
      <!-- 动态登录/用户状态容器 (0ms 无闪烁渲染) -->
      <div id="auth-state-container" class="flex items-center gap-2">
        <a id="nav-login-btn" href="/login" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/15 hover:border-[#38BDF8]/60 hover:bg-[#0284C7]/15 text-slate-200 hover:text-white text-xs font-bold transition-all shadow-xs">
          <span>登录 / 注册</span>
        </a>
      </div>

      <!-- 语言切换器 (多语言选择器) -->
      <div class="relative" id="lang-menu-wrapper">
        <button 
          id="lang-menu-btn" 
          type="button" 
          class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 text-slate-300 hover:text-white text-xs transition cursor-pointer select-none"
          aria-label="切换语言"
        >
          <svg class="w-3.5 h-3.5 text-[#38BDF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
          </svg>
          <span id="current-lang-label" class="font-mono text-xs">简体中文</span>
          <svg class="w-2.5 h-2.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <div id="lang-menu-panel" class="hidden absolute right-0 mt-1 w-32 rounded-2xl bg-[#0B0F1A]/95 border border-white/10 shadow-2xl p-1.5 z-50 backdrop-blur-xl">
          <button type="button" onclick="window.changeSiteLang('zh-CN')" class="w-full text-left px-3 py-1.5 rounded-xl text-xs text-slate-300 hover:text-white hover:bg-[#0284C7]/20 transition">
            <span>简体中文</span>
          </button>
          <button type="button" onclick="window.changeSiteLang('en')" class="w-full text-left px-3 py-1.5 rounded-xl text-xs text-slate-300 hover:text-white hover:bg-[#0284C7]/20 transition">
            <span>English</span>
          </button>
          <button type="button" onclick="window.changeSiteLang('ja')" class="w-full text-left px-3 py-1.5 rounded-xl text-xs text-slate-300 hover:text-white hover:bg-[#0284C7]/20 transition">
            <span>日本語</span>
          </button>
          <button type="button" onclick="window.changeSiteLang('ko')" class="w-full text-left px-3 py-1.5 rounded-xl text-xs text-slate-300 hover:text-white hover:bg-[#0284C7]/20 transition">
            <span>한국어</span>
          </button>
        </div>
      </div>

      <!-- 购物车抽屉按钮 -->
      <button id="header-cart-btn" type="button" class="relative p-2 rounded-xl bg-white/5 border border-white/10 hover:border-[#38BDF8]/60 hover:bg-[#0284C7]/15 text-slate-200 hover:text-white transition-all cursor-pointer" aria-label="打开购物车">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path></svg>
        <span id="cart-count-badge" class="hidden absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#0284C7] text-white text-[9px] font-black flex items-center justify-center border border-[#38BDF8] shadow-sm">0</span>
      </button>
    </div>
  </div>
</header>

<script>
  import { authInstance, onAuthStateChanged, signOut } from '../lib/firebase.js';

  const authContainer = document.getElementById('auth-state-container');
  const adminEmail = (import.meta.env.PUBLIC_ADMIN_EMAIL || 'rukyucrono@gmail.com').toLowerCase();

  function renderUserUI(email, displayName) {
    if (!authContainer) return;
    const cleanEmail = (email || '').toLowerCase();
    const isAdmin = (cleanEmail === adminEmail);
    const cleanName = displayName || cleanEmail.split('@')[0] || '会员';

    authContainer.innerHTML = `
      <div class="flex items-center gap-2">
        ${isAdmin ? `
          <a href="/admin/dashboard" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-[#0284C7] to-[#38BDF8] text-[#06080F] font-black text-xs shadow-[0_0_15px_rgba(56,189,248,0.4)] transition hover:brightness-110 active:scale-95">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            <span>管理后台</span>
          </a>
        ` : ''}

        <a href="/orders" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:border-[#38BDF8]/40 hover:bg-[#0284C7]/15 text-slate-200 hover:text-white text-xs font-bold transition-all">
          <svg class="w-3.5 h-3.5 text-[#38BDF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path></svg>
          <span class="hidden sm:inline">我的订单</span>
        </a>

        <!-- 用户头像与常驻面板容器 -->
        <div class="relative" id="user-menu-wrapper">
          <button 
            id="user-menu-btn" 
            type="button" 
            class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:border-[#38BDF8]/50 text-slate-300 hover:text-white text-xs transition cursor-pointer select-none"
            title="点击展开/固定账号菜单"
          >
            <div class="w-5 h-5 rounded-full bg-[#0284C7]/30 border border-[#38BDF8]/40 text-[#38BDF8] flex items-center justify-center text-[10px] font-bold">
              ${cleanName.charAt(0).toUpperCase()}
            </div>
            <span class="max-w-[70px] truncate text-slate-300 font-medium">${cleanName}</span>
            <svg class="w-2.5 h-2.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </button>

          <!-- 彻底摒弃 group-hover，由 JS 绝对常驻掌控，鼠标移开绝不闪退！ -->
          <div id="user-menu-panel" class="hidden absolute right-0 top-full pt-2 w-56 z-50 select-none">
            <div class="rounded-2xl bg-[#0B0F1A]/95 border border-[#38BDF8]/40 shadow-[0_15px_40px_rgba(0,0,0,0.85)] p-2.5 backdrop-blur-2xl space-y-1.5">
              <div class="px-3 py-2 border-b border-white/10 mb-1">
                <div class="text-[11px] text-slate-300 font-medium truncate">${cleanEmail}</div>
                <div class="text-[9px] font-bold mt-0.5 ${isAdmin ? 'text-[#38BDF8]' : 'text-emerald-400'}">
                  ${isAdmin ? '👑 最高管理员席位' : '✦ 正式注册会员'}
                </div>
              </div>
              <a href="/orders" class="flex items-center gap-2 px-3 py-2 rounded-xl text-xs text-slate-300 hover:text-white hover:bg-white/10 transition">
                <span>📦 历史订单与资产</span>
              </a>
              <button 
                id="nav-logout-btn" 
                type="button" 
                class="w-full text-left flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs text-rose-400 hover:bg-rose-500/20 hover:text-rose-300 transition cursor-pointer active:scale-95 font-bold border border-rose-500/20"
              >
                <span>🚪 退出安全登录</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function renderGuestUI() {
    if (!authContainer) return;
    authContainer.innerHTML = `
      <a id="nav-login-btn" href="/login" class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-white/5 border border-white/15 hover:border-[#38BDF8]/60 hover:bg-[#0284C7]/15 text-slate-200 hover:text-white text-xs font-bold transition-all shadow-xs">
        <span>登录 / 注册</span>
      </a>
    `;
  }

  // 1. 本地快照极速识别
  try {
    const cachedSession = localStorage.getItem('auth_session');
    if (cachedSession) {
      const parsed = JSON.parse(cachedSession);
      if (parsed && parsed.email) {
        renderUserUI(parsed.email, parsed.displayName);
      }
    }
  } catch(e) {}

  // 2. Firebase 鉴权侦听
  onAuthStateChanged(authInstance, (user) => {
    if (user && user.email) {
      const displayName = user.displayName || user.email.split('@')[0];
      localStorage.setItem('auth_session', JSON.stringify({ email: user.email, displayName }));
      renderUserUI(user.email, displayName);
    } else {
      if (!localStorage.getItem('auth_session')) {
        renderGuestUI();
      }
    }
  });

  // 3. 全局高稳事件代理：支持【点击永久常驻锁定】与【800ms 宽容滑出】
  let isPinned = false;
  let timer: any = null;

  document.addEventListener('click', async (e) => {
    const target = e.target as HTMLElement;
    if (!target) return;

    const btn = target.closest('#user-menu-btn');
    const panel = document.getElementById('user-menu-panel');
    const logoutBtn = target.closest('#nav-logout-btn');

    // 点击退出安全登录
    if (logoutBtn) {
      e.preventDefault();
      e.stopPropagation();
      localStorage.removeItem('auth_session');
      try { await signOut(authInstance); } catch(err) {}
      window.location.href = '/';
      return;
    }

    // 点击用户按钮：切换展开并永久锁定常驻！鼠标移开绝不消失！
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      if (panel) {
        const isHidden = panel.classList.contains('hidden');
        if (isHidden) {
          panel.classList.remove('hidden');
          isPinned = true;
        } else {
          panel.classList.add('hidden');
          isPinned = false;
        }
      }
      return;
    }

    // 点击页面其它空白区域收起
    if (panel && !panel.contains(target)) {
      panel.classList.add('hidden');
      isPinned = false;
    }
  });

  // 悬停自动展开
  document.addEventListener('mouseover', (e) => {
    const target = e.target as HTMLElement;
    if (target?.closest('#user-menu-wrapper')) {
      if (timer) clearTimeout(timer);
      const panel = document.getElementById('user-menu-panel');
      panel?.classList.remove('hidden');
    }
  });

  // 移出保护：若点击已锁定则永久保持；若纯悬停则留有 800ms 充足时间
  document.addEventListener('mouseout', (e) => {
    const target = e.target as HTMLElement;
    const related = (e as MouseEvent).relatedTarget as HTMLElement;
    const wrapper = document.getElementById('user-menu-wrapper');
    if (wrapper && !wrapper.contains(related)) {
      if (isPinned) return; // 锁定状态，鼠标怎么移都不会消失
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        if (!isPinned) {
          const panel = document.getElementById('user-menu-panel');
          panel?.classList.add('hidden');
        }
      }, 800);
    }
  });
</script>

<script is:inline>
  document.addEventListener('DOMContentLoaded', function() {
    var btn = document.getElementById('lang-menu-btn');
    var panel = document.getElementById('lang-menu-panel');
    if (btn && panel) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        panel.classList.toggle('hidden');
      });
      document.addEventListener('click', function() {
        panel.classList.add('hidden');
      });
    }

    var cur = localStorage.getItem('active_language') || 'zh-CN';
    var label = document.getElementById('current-lang-label');
    if (label) {
      var nameMap = { 'zh-CN': '简体中文', 'en': 'English', 'ja': '日本語', 'ko': '한국어' };
      if (nameMap[cur]) label.textContent = nameMap[cur];
    }
  });

  window.changeSiteLang = function(lang) {
    localStorage.setItem('active_language', lang);
    var langMap = { 'zh-CN': 'chinese_simplified', 'en': 'english', 'ja': 'japanese', 'ko': 'korean' };
    var target = langMap[lang] || 'chinese_simplified';
    if (target === 'chinese_simplified') {
      window.location.reload();
    } else if (window.translate) {
      try {
        translate.changeLanguage(target);
      } catch(e) {
        window.location.reload();
      }
    } else {
      window.location.reload();
    }
  };
</script>
"""

with open(header_path, 'w', encoding='utf-8') as f:
    f.write(new_header_code)
print('✓ [1/2] src/components/Header.astro 用户菜单与锁定交互重构完成')

# 2. 在 src/pages/orders.astro 页面内增加直出安全退出按钮
orders_path = 'src/pages/orders.astro'
with open(orders_path, 'r', encoding='utf-8') as f:
    orders_content = f.read()

# 在 orders-user-badge 内添加退出登录按钮
old_badge = """    if (userBadge) {
      userBadge.innerHTML = `<span class=\"text-slate-400\">已登录账号:</span> <span class=\"text-[#38BDF8] font-bold\">${currentUserEmail}</span>`;
    }"""

new_badge = """    if (userBadge) {
      userBadge.innerHTML = `
        <span class=\"text-slate-400\">已登录账号:</span> 
        <span class=\"text-[#38BDF8] font-bold font-mono\">${currentUserEmail}</span>
        <button id=\"direct-logout-btn\" type=\"button\" class=\"ml-2.5 px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 text-[11px] font-bold transition cursor-pointer active:scale-95\">退出登录</button>
      `;
    }"""

if old_badge in orders_content:
    orders_content = orders_content.replace(old_badge, new_badge)

# 绑定 direct-logout-btn 事件
if 'direct-logout-btn' not in orders_content:
    orders_content = orders_content.replace(
        "// 历史订单删除动效与持久化",
        """// 直出退出登录
  document.addEventListener('click', async (e) => {
    const target = e.target as HTMLElement;
    if (target?.closest('#direct-logout-btn')) {
      e.preventDefault();
      localStorage.removeItem('auth_session');
      try { await signOut(authInstance); } catch(err) {}
      window.location.href = '/';
      return;
    }
  });

  // 历史订单删除动效与持久化"""
    )

with open(orders_path, 'w', encoding='utf-8') as f:
    f.write(orders_content)
print('✓ [2/2] src/pages/orders.astro 直出退出按钮集成完成')

print("\n=== 开始编译验证 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建 100% 成功！正在自动提交推送 Git...")
    os.system('git add -A && git commit -m "feat: permanent pinned user menu, safe hover buffer, and direct logout button on orders page" && git push origin main')
    print("🚀 升级已完成并推送到线上！")
else:
    print("\n❌ 编译未通过，请查看上方输出。")
