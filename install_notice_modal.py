import os

print("=== 开始安装入站公告弹窗与蓝染音频按钮联动 ===")

# 1. 创建公告组件 src/components/NoticeModal.astro
notice_path = 'src/components/NoticeModal.astro'

notice_component_code = """---
// NoticeModal.astro - 全站重要公告弹窗
---
<div 
  id="site-notice-modal" 
  class="hidden fixed inset-0 bg-black/80 backdrop-blur-md z-[110] flex items-center justify-center p-3 sm:p-4 font-outfit select-none"
  aria-modal="true"
  role="dialog"
>
  <div class="relative bg-[#0B0F1A]/95 border border-[#38BDF8]/40 shadow-[0_20px_60px_rgba(0,0,0,0.9)] rounded-3xl max-w-2xl w-full flex flex-col overflow-hidden backdrop-blur-2xl animate-fadeIn">
    
    <!-- 头部 -->
    <div class="p-5 sm:p-6 pb-3 border-b border-white/10 flex items-start justify-between">
      <div>
        <span class="text-[10px] font-mono tracking-widest uppercase text-[#38BDF8] font-bold block mb-0.5">NOTICE</span>
        <h2 class="text-xl sm:text-2xl font-black text-white flex items-center gap-2 tracking-tight">
          <span>📢</span>
          <span>公告</span>
        </h2>
      </div>
      <button 
        id="notice-modal-close-x" 
        type="button" 
        class="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition cursor-pointer"
        aria-label="关闭公告"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- 滚动正文区域 -->
    <div class="p-5 sm:p-6 overflow-y-auto max-h-[60vh] space-y-4 text-xs sm:text-sm text-slate-200 leading-relaxed font-outfit select-text custom-scrollbar">
      
      <!-- 导言 -->
      <div class="p-4 rounded-2xl bg-white/5 border border-white/10 leading-relaxed text-slate-300">
        欢迎来到全球领先的跨境数字资产与出海营销一站式服务平台。我们致力于为跨境电商、外贸企业及个人开发者提供安全、稳定、高效的底层数字基础设施。平台业务涵盖 Google、Apple ID、YouTube、TikTok、Twitter X、Facebook、Instagram 等全球主流大厂与社交媒体账号，同时稳定供应 Telegram 及 Discord 跨境私域矩阵与高品质 Email 邮箱原材料。 为了全方位助力您的出海业务，我们不仅提供 AI 生产力工具订阅、海外信用卡代付及网站代理技术支持，更配套推出了全网顶尖的社媒数据增长解决方案——涵盖 Telegram 刷粉、YouTube 频道订阅、TikTok 粉丝互动、Twitter (X) 转发赞以及 Facebook 主页点赞等多平台业务，帮助新号快速热场、突破风控、积累初始信任。一手货源，自动发货，安全合规，助您轻松破海，畅行全球。
      </div>

      <!-- 下单前请注意 -->
      <div class="space-y-2 pt-1">
        <h3 class="font-black text-amber-400 text-sm flex items-center gap-1.5">
          <span>🛒</span>
          <span>下单前请注意</span>
        </h3>
        <ul class="space-y-1.5 pl-1 text-slate-300 text-xs">
          <li class="flex items-start gap-2">
            <span class="text-[#38BDF8] font-bold shrink-0">1️⃣</span>
            <span>建议注册并登录后购买，方便查询订单、卡密和售后记录。</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-[#38BDF8] font-bold shrink-0">2️⃣</span>
            <span>下单前请确认商品适用平台、使用期限和账号要求，买错商品可能会很麻烦。</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-[#38BDF8] font-bold shrink-0">3️⃣</span>
            <span>商品价格和库存会根据上游情况调整，请以当前页面显示为准。</span>
          </li>
        </ul>
      </div>

      <div class="border-t border-white/10 my-2"></div>

      <!-- 收到商品后 -->
      <div class="space-y-2">
        <h3 class="font-black text-sky-400 text-sm flex items-center gap-1.5">
          <span>📦</span>
          <span>收到商品后</span>
        </h3>
        <ul class="space-y-1.5 pl-1 text-slate-300 text-xs">
          <li class="flex items-start gap-2">
            <span class="text-slate-400 font-mono shrink-0">1)</span>
            <span>请第一时间保存卡密、兑换码或订单信息。</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-slate-400 font-mono shrink-0">2)</span>
            <span>请先阅读商品说明，再进行登录、兑换或使用。</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-slate-400 font-mono shrink-0">3)</span>
            <span>涉及账号类商品时，请不要公开账号、密码和验证码。</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-slate-400 font-mono shrink-0">4)</span>
            <span>如果遇到问题，请保留订单号和相关截图，不要重复下单。</span>
          </li>
        </ul>
      </div>

      <div class="border-t border-white/10 my-2"></div>

      <!-- 售后说明 -->
      <div class="space-y-2">
        <h3 class="font-black text-rose-400 text-sm flex items-center gap-1.5">
          <span>🧰</span>
          <span>售后说明</span>
        </h3>
        <p class="text-xs text-slate-300 leading-relaxed">
          如遇到发货异常、兑换失败或商品质量问题，请联系客服TG：
          <a href="https://t.me/Rukyu6" target="_blank" class="text-[#38BDF8] underline font-mono font-bold">@Rukyu6</a> / 
          <a href="https://t.me/puppyshop2Bot" target="_blank" class="text-[#38BDF8] underline font-mono font-bold">@puppyshop2Bot</a><br />
          我的X（推特）: <a href="https://x.com/Rukyu88153004" target="_blank" class="text-[#38BDF8] underline font-mono font-bold">@Rukyu88153004</a>
        </p>
        <div class="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300 leading-relaxed mt-2">
          <p class="font-bold">订单号 + 商品名称 + 问题截图</p>
          <p class="text-[11px] text-rose-300/80 mt-1">为了保护你的账号安全，请不要向任何人发送完整密码、验证码或支付信息。数字商品具有特殊性，已查看、兑换或使用的商品，售后规则请以商品页面说明为准。</p>
        </div>
      </div>

      <div class="border-t border-white/10 my-2"></div>

      <!-- 关于代理 -->
      <div class="space-y-2">
        <h3 class="font-black text-emerald-400 text-sm flex items-center gap-1.5">
          <span>🤝</span>
          <span>关于代理</span>
        </h3>
        <p class="text-xs text-slate-300 leading-relaxed">
          本店为独立代理销售渠道，不冒充任何官方平台。<br />
          商品库存、价格、有效期及使用规则可能会随上游调整，最终以页面实际说明为准。
        </p>
        <div class="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 mt-2">
          如需批量采购、货源合作或代理咨询<br />
          TG联系：<a href="https://t.me/Rukyu6" target="_blank" class="font-mono underline font-bold">@Rukyu6</a> / <a href="https://t.me/puppyshop2Bot" target="_blank" class="font-mono underline font-bold">@puppyshop2Bot</a>（联系时请备注）
        </div>
      </div>

      <div class="border-t border-white/10 my-2"></div>

      <!-- 福利 -->
      <div class="text-center py-2.5 text-xs font-bold text-[#38BDF8] bg-[#0284C7]/15 rounded-xl border border-[#38BDF8]/30">
        🎁 给博主推特点点关注，后续会发放福利
      </div>
    </div>

    <!-- 底部按钮区 -->
    <div class="p-4 sm:p-5 pt-3 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#06080F]/60">
      <span class="text-[11px] text-slate-400 font-mono text-center sm:text-left">
        点击“我已知晓”后，1 小时内不再自动弹出。
      </span>
      <div class="flex items-center gap-2.5 w-full sm:w-auto justify-end">
        <button 
          id="notice-btn-cancel" 
          type="button" 
          class="flex-1 sm:flex-initial px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white text-xs font-bold transition cursor-pointer active:scale-95"
        >
          ✕ 取消
        </button>
        <button 
          id="notice-btn-acknowledge" 
          type="button" 
          class="flex-1 sm:flex-initial px-5 py-2 rounded-xl bg-gradient-to-r from-[#0284C7] to-[#38BDF8] hover:brightness-110 text-white font-bold text-xs shadow-[0_0_15px_rgba(56,189,248,0.4)] transition cursor-pointer active:scale-95 flex items-center justify-center gap-1.5"
        >
          <span>✔</span>
          <span>我已知晓</span>
        </button>
      </div>
    </div>

  </div>
</div>

<script is:inline>
  (function() {
    window.openNoticeModal = function() {
      var modal = document.getElementById('site-notice-modal');
      if (modal) {
        modal.classList.remove('hidden');
      }
    };

    window.closeNoticeModal = function(setQuietPeriod) {
      var modal = document.getElementById('site-notice-modal');
      if (modal) {
        modal.classList.add('hidden');
      }
      if (setQuietPeriod) {
        localStorage.setItem('notice_quiet_until', (Date.now() + 3600 * 1000).toString());
      }
    };

    document.getElementById('notice-modal-close-x')?.addEventListener('click', function() {
      window.closeNoticeModal(false);
    });

    document.getElementById('notice-btn-cancel')?.addEventListener('click', function() {
      window.closeNoticeModal(false);
    });

    document.getElementById('notice-btn-acknowledge')?.addEventListener('click', function() {
      window.closeNoticeModal(true);
    });

    document.getElementById('site-notice-modal')?.addEventListener('click', function(e) {
      if (e.target.id === 'site-notice-modal') {
        window.closeNoticeModal(false);
      }
    });

    // 首次进站自动弹出检测（1 小时内不再重复弹出）
    var quietUntil = Number(localStorage.getItem('notice_quiet_until') || 0);
    if (Date.now() > quietUntil) {
      setTimeout(function() {
        window.openNoticeModal();
      }, 600);
    }
  })();
</script>
"""

with open(notice_path, 'w', encoding='utf-8') as f:
    f.write(notice_component_code)
print("✓ [1/3] src/components/NoticeModal.astro 组件已创建")

# 2. 在 BaseLayout.astro 中全局挂载 NoticeModal
base_path = 'src/layouts/BaseLayout.astro'
with open(base_path, 'r', encoding='utf-8') as f:
    base_content = f.read()

if "import NoticeModal from '../components/NoticeModal.astro';" not in base_content:
    base_content = base_content.replace(
        "import CartDrawer from '../components/CartDrawer.astro';",
        "import CartDrawer from '../components/CartDrawer.astro';\nimport NoticeModal from '../components/NoticeModal.astro';"
    )

if "<NoticeModal />" not in base_content:
    base_content = base_content.replace(
        "<CartDrawer />",
        "<CartDrawer />\n    <NoticeModal />"
    )

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(base_content)
print("✓ [2/3] src/layouts/BaseLayout.astro 已全局挂载 NoticeModal")

# 3. 在 Header.astro 中打通蓝染 Icon 点击：重复播放音频并弹出公告
header_path = 'src/components/Header.astro'
with open(header_path, 'r', encoding='utf-8') as f:
    header_content = f.read()

old_aizen_click = """    if (aizenAudio.paused) {
      aizenAudio.currentTime = 0;
      aizenAudio.volume = 0.9;
      aizenAudio.play().then(() => {
        aizenPulse?.classList.remove('hidden');
      }).catch((err) => {
        console.warn('Playback blocked:', err);
      });
    } else {
      aizenAudio.pause();
      aizenAudio.currentTime = 0;
      aizenPulse?.classList.add('hidden');
    }"""

new_aizen_click = """    // 重复点击从头播放音频
    aizenAudio.currentTime = 0;
    aizenAudio.volume = 0.9;
    aizenAudio.play().then(() => {
      aizenPulse?.classList.remove('hidden');
    }).catch((err) => {
      console.warn('Playback blocked:', err);
    });

    // 每次点击同时跳出公告窗口
    if (typeof (window as any).openNoticeModal === 'function') {
      (window as any).openNoticeModal();
    }"""

if old_aizen_click in header_content:
    header_content = header_content.replace(old_aizen_click, new_aizen_click)
    with open(header_path, 'w', encoding='utf-8') as f:
        f.write(header_content)
    print("✓ [3/3] src/components/Header.astro 蓝染头像点击重复播音并跳出公告联动完成")

print("\n=== 开始编译验证 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建 100% 成功！正在推送 Git...")
    os.system('git add -A && git commit -m "feat: popup notice modal on entry with 1h quiet period and wire top aizen sound button to replay and show notice" && git push origin main')
    print("🚀 升级已完成并推送到线上！")
else:
    print("\n❌ 编译未通过，请查看上方输出。")
