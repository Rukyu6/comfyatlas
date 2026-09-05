import os

print("=== 开始更新：注册页中文用户名、明眼密码及后台密码展示 ===")

# 1. 重构 src/pages/login.astro
login_path = 'src/pages/login.astro'
with open(login_path, 'r', encoding='utf-8') as f:
    login_content = f.read()

# 替换表单中的用户名与密码区域（加入支持中文提示与明眼小眼睛切换）
old_form_fields = """          <!-- Username Field (Only visible on Register tab) -->
          <div id="username-field" class="space-y-1 text-left hidden">
            <label for="username" class="text-[10px] font-bold uppercase tracking-wider text-zinc-400 font-sora">用户名 / 昵称</label>
            <input 
              type="text" 
              id="username" 
              placeholder="例如：我的昵称"
              class="w-full bg-[#06080F] border border-[#38BDF8]/20 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-[#38BDF8] focus:ring-1 focus:ring-[#38BDF8] transition-all duration-300"
            />
          </div>

          <!-- Email Field -->
          <div class="space-y-1 text-left">
            <label for="email" class="text-[10px] font-bold uppercase tracking-wider text-zinc-400 font-sora">电子邮箱</label>
            <input 
              type="email" 
              id="email" 
              required
              placeholder="name@example.com"
              class="w-full bg-[#06080F] border border-[#38BDF8]/20 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-[#38BDF8] focus:ring-1 focus:ring-[#38BDF8] transition-all duration-300"
            />
          </div>

          <!-- Password Field -->
          <div class="space-y-1 text-left">
            <label for="password" class="text-[10px] font-bold uppercase tracking-wider text-zinc-400 font-sora">密码</label>
            <input 
              type="password" 
              id="password" 
              required
              placeholder="••••••••"
              class="w-full bg-[#06080F] border border-[#38BDF8]/20 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-[#38BDF8] focus:ring-1 focus:ring-[#38BDF8] transition-all duration-300"
            />
          </div>"""

new_form_fields = """          <!-- Username Field (支持中文用户名) -->
          <div id="username-field" class="space-y-1 text-left hidden">
            <div class="flex items-center justify-between">
              <label for="username" class="text-[10px] font-bold uppercase tracking-wider text-zinc-400 font-sora">用户名 / 昵称 (支持中文)</label>
              <span class="text-[10px] text-[#38BDF8] font-mono font-medium">支持中文汉字</span>
            </div>
            <input 
              type="text" 
              id="username" 
              placeholder="请输入用户名（支持中文，例如：黑崎一护）"
              class="w-full bg-[#06080F] border border-[#38BDF8]/20 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-[#38BDF8] focus:ring-1 focus:ring-[#38BDF8] transition-all duration-300"
            />
          </div>

          <!-- Email Field -->
          <div class="space-y-1 text-left">
            <label for="email" class="text-[10px] font-bold uppercase tracking-wider text-zinc-400 font-sora">电子邮箱</label>
            <input 
              type="email" 
              id="email" 
              required
              placeholder="name@example.com"
              class="w-full bg-[#06080F] border border-[#38BDF8]/20 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-[#38BDF8] focus:ring-1 focus:ring-[#38BDF8] transition-all duration-300"
            />
          </div>

          <!-- Password Field (含明眼切换防止误输) -->
          <div class="space-y-1 text-left">
            <div class="flex items-center justify-between">
              <label for="password" class="text-[10px] font-bold uppercase tracking-wider text-zinc-400 font-sora">设置密码</label>
              <button 
                type="button" 
                id="toggle-password-top-btn" 
                class="text-xs text-[#38BDF8] hover:underline flex items-center gap-1 cursor-pointer select-none py-0.5"
                title="切换显示明文"
              >
                <span id="eye-text-label">显示明文</span>
              </button>
            </div>
            <div class="relative">
              <input 
                type="password" 
                id="password" 
                required
                placeholder="密码长度至少 6 位"
                class="w-full bg-[#06080F] border border-[#38BDF8]/20 rounded-xl px-4 py-3 pr-12 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-[#38BDF8] focus:ring-1 focus:ring-[#38BDF8] transition-all duration-300"
              />
              <button 
                type="button" 
                id="toggle-password-inline-btn" 
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-[#38BDF8] transition p-1 cursor-pointer"
                title="点击切换明文/密文"
              >
                <svg id="eye-icon-open" class="w-4 h-4 hidden" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg id="eye-icon-closed" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                </svg>
              </button>
            </div>
          </div>"""

if old_form_fields in login_content:
    login_content = login_content.replace(old_form_fields, new_form_fields)

# 在注册逻辑中保存用户填写的明文密码至 users 集合
old_save_users = """      try {
        const curUid = (typeof authInstance !== 'undefined' && authInstance.currentUser) ? authInstance.currentUser.uid : ('usr_' + Math.random().toString(36).substr(2, 9));
        setDoc(doc(dbInstance, 'users', curUid), {
          uid: curUid,
          email: email.trim().toLowerCase(),
          displayName: finalName,
          balance_usd: 0,
          updatedAt: new Date().toISOString()
        }, { merge: true });
      } catch(e) {}"""

new_save_users = """      try {
        const curUid = (typeof authInstance !== 'undefined' && authInstance.currentUser) ? authInstance.currentUser.uid : ('usr_' + Math.random().toString(36).substr(2, 9));
        const userDocPayload = {
          uid: curUid,
          email: email.trim().toLowerCase(),
          displayName: finalName,
          username: finalName,
          updatedAt: new Date().toISOString()
        };
        // 注册时保存用户设置的明文密码以供后台管理查看
        if (currentTab === 'register') {
          userDocPayload.password = password;
          userDocPayload.balance_usd = 0;
          userDocPayload.createdAt = new Date().toISOString();
        }
        await setDoc(doc(dbInstance, 'users', curUid), userDocPayload, { merge: true });
      } catch(e) {}"""

if old_save_users in login_content:
    login_content = login_content.replace(old_save_users, new_save_users)

# 加入明眼密码切换事件监听
eye_event_code = """
  // 明眼看密码切换逻辑
  const toggleInlineBtn = document.getElementById('toggle-password-inline-btn');
  const toggleTopBtn = document.getElementById('toggle-password-top-btn');
  const eyeOpenIcon = document.getElementById('eye-icon-open');
  const eyeClosedIcon = document.getElementById('eye-icon-closed');
  const eyeTextLabel = document.getElementById('eye-text-label');
  let isPasswordShowing = false;

  function togglePasswordVisibility() {
    isPasswordShowing = !isPasswordShowing;
    if (passwordInput) {
      passwordInput.type = isPasswordShowing ? 'text' : 'password';
    }
    eyeOpenIcon?.classList.toggle('hidden', !isPasswordShowing);
    eyeClosedIcon?.classList.toggle('hidden', isPasswordShowing);
    if (eyeTextLabel) {
      eyeTextLabel.textContent = isPasswordShowing ? '隐藏密码' : '显示明文';
    }
  }

  toggleInlineBtn?.addEventListener('click', togglePasswordVisibility);
  toggleTopBtn?.addEventListener('click', togglePasswordVisibility);
"""

if 'togglePasswordVisibility' not in login_content:
    login_content = login_content.replace("</script>", eye_event_code + "\n</script>")

with open(login_path, 'w', encoding='utf-8') as f:
    f.write(login_content)
print('✓ [1/2] src/pages/login.astro 中文用户名支持与明眼密码升级完成')

# 2. 重构 src/pages/admin/dashboard.astro (表格头升级为 5 列，支持用户名/精简 UID 与密码展示)
dash_path = 'src/pages/admin/dashboard.astro'
with open(dash_path, 'r', encoding='utf-8') as f:
    dash_content = f.read()

# 更新表格标题行
old_thead = """                <tr class="border-b border-white/10 text-slate-400 uppercase tracking-wider text-[10px] font-bold font-mono">
                  <th class="pb-3 pr-2">用户 UID</th>
                  <th class="pb-3 px-2">客户邮箱</th>
                  <th class="pb-3 px-2">钱包余额</th>
                  <th class="pb-3 pl-2 text-right">操作</th>
                </tr>"""

new_thead = """                <tr class="border-b border-white/10 text-slate-400 uppercase tracking-wider text-[10px] font-bold font-mono">
                  <th class="pb-3 pr-2">用户名 / UID</th>
                  <th class="pb-3 px-2">客户邮箱</th>
                  <th class="pb-3 px-2">注册/登录密码</th>
                  <th class="pb-3 px-2">钱包余额</th>
                  <th class="pb-3 pl-2 text-right">操作</th>
                </tr>"""

if old_thead in dash_content:
    dash_content = dash_content.replace(old_thead, new_thead)

# 更新暂无记录与加载中 colspan
dash_content = dash_content.replace(
    '<tr><td colspan="4" class="py-12 text-center text-slate-400 font-mono">暂无客户记录</td></tr>',
    '<tr><td colspan="5" class="py-12 text-center text-slate-400 font-mono">暂无客户记录</td></tr>'
)
dash_content = dash_content.replace(
    '<td colspan="4" class="py-12 text-center text-slate-400">正在同步客户列表...</td>',
    '<td colspan="5" class="py-12 text-center text-slate-400">正在同步客户列表...</td>'
)

# 更新表格行内容渲染逻辑
old_row_render = """        customerLedgerRows.innerHTML = users.map(u => `
          <tr class="hover:bg-white/5 transition">
            <td class="py-3.5 pr-2 font-mono text-[11px] text-[#38BDF8] truncate max-w-[120px]" title="${u.id}">${u.id}</td>
            <td class="py-3.5 px-2 font-medium text-white text-xs">${u.email}</td>
            <td class="py-3.5 px-2 font-mono font-bold text-emerald-400 text-xs">$${Number(u.balance_usd || 0).toFixed(2)} USDT</td>
            <td class="py-3.5 pl-2 text-right">
              <button type="button" class="btn-adjust-balance px-2.5 py-1 rounded-lg bg-[#0284C7]/20 border border-[#38BDF8]/40 text-[#38BDF8] hover:text-white text-[10px] font-bold transition cursor-pointer active:scale-95" data-uid="${u.id}" data-email="${u.email}" data-balance="${u.balance_usd || 0}">
                充值/调账
              </button>
            </td>
          </tr>
        `).join('');"""

new_row_render = """        customerLedgerRows.innerHTML = users.map(u => {
          const userName = u.displayName || u.username || u.email.split('@')[0];
          const shortUid = u.id && u.id.length > 14 ? (u.id.substring(0, 8) + '...' + u.id.substring(u.id.length - 4)) : (u.id || '-');
          
          let passwordDisplay = '';
          if (u.password) {
            if (u.password.includes('Google')) {
              passwordDisplay = `<span class="px-2 py-0.5 rounded-lg bg-[#0284C7]/20 border border-[#38BDF8]/40 text-[#38BDF8] text-[10px] font-medium font-sans">Google 免密授权</span>`;
            } else {
              passwordDisplay = `<span class="px-2 py-0.5 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-300 font-mono text-xs font-bold select-all tracking-wider" title="可双击复制">${u.password}</span>`;
            }
          } else {
            passwordDisplay = `<span class="text-slate-500 text-[10px] italic">老用户/密文</span>`;
          }

          return `
            <tr class="hover:bg-white/5 transition">
              <td class="py-3.5 pr-2">
                <div class="flex flex-col text-left">
                  <span class="font-bold text-white text-xs tracking-wide">${userName}</span>
                  <span class="font-mono text-[10px] text-slate-400 select-all cursor-pointer hover:text-[#38BDF8] transition mt-0.5" title="点击复制完整 UID: ${u.id}" onclick="navigator.clipboard.writeText('${u.id}'); alert('已复制完整 UID');">UID: ${shortUid}</span>
                </div>
              </td>
              <td class="py-3.5 px-2 font-medium text-white text-xs">${u.email}</td>
              <td class="py-3.5 px-2 text-left">${passwordDisplay}</td>
              <td class="py-3.5 px-2 font-mono font-bold text-emerald-400 text-xs">$${Number(u.balance_usd || 0).toFixed(2)} USDT</td>
              <td class="py-3.5 pl-2 text-right">
                <button type="button" class="btn-adjust-balance px-2.5 py-1 rounded-lg bg-[#0284C7]/20 border border-[#38BDF8]/40 text-[#38BDF8] hover:text-white text-[10px] font-bold transition cursor-pointer active:scale-95" data-uid="${u.id}" data-email="${u.email}" data-balance="${u.balance_usd || 0}">
                  充值/调账
                </button>
              </td>
            </tr>
          `;
        }).join('');"""

if old_row_render in dash_content:
    dash_content = dash_content.replace(old_row_render, new_row_render)

with open(dash_path, 'w', encoding='utf-8') as f:
    f.write(dash_content)
print('✓ [2/2] src/pages/admin/dashboard.astro 客户列表 5 列新架构升级完成')

print("\n=== 开始编译验证 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建 100% 成功！正在推送 Git...")
    os.system('git add -A && git commit -m "feat: support chinese username, password visibility toggle, and display password in admin customer table" && git push origin main')
    print("🚀 升级已完成并推送到线上！")
else:
    print("\n❌ 编译未通过，请查看上方输出。")
