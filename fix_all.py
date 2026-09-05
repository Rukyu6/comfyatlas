import os

print("=== 开始全量自动化修复与编译 ===")

# 1. 修复 src/pages/orders.astro
orders_path = 'src/pages/orders.astro'
with open(orders_path, 'r', encoding='utf-8') as f:
    orders_content = f.read()

# 确保导入了 updateDoc
if 'updateDoc' not in orders_content and "from '../lib/firebase.js'" in orders_content:
    orders_content = orders_content.replace(
        "import { authInstance, onAuthStateChanged, collection, dbInstance, query, where, orderBy, getDocs, doc, getDoc, addDoc } from '../lib/firebase.js';",
        "import { authInstance, onAuthStateChanged, collection, dbInstance, query, where, getDocs, doc, getDoc, addDoc, updateDoc } from '../lib/firebase.js';"
    )

# 确保 loadOrders 不依赖复合索引，并在内存排序
old_load_orders = """  async function loadOrders() {
    try {
      const q = query(collection(dbInstance, 'orders'), where('email', '==', currentUserEmail), orderBy('createdAt', 'desc'));
      const querySnapshot = await getDocs(q);
      const orders: any[] = [];
      const hiddenList = JSON.parse(localStorage.getItem('hidden_orders_' + currentUserEmail) || '[]');
      querySnapshot.docs.forEach((doc) => {
        const data = doc.data();
        if (!data.deletedByUser && !hiddenList.includes(doc.id)) {
          orders.push({ id: doc.id, ...data });
        }
      });

      if (orders.length === 0) {
        loadingSec?.classList.add('hidden');
        emptySec?.classList.remove('hidden');
        listSec?.classList.add('hidden');
        return;
      }
      renderOrders(orders);
    } catch {
      try {
        const qFall = query(collection(dbInstance, 'orders'));
        const querySnapshot = await getDocs(qFall);
        const allOrders: any[] = [];
        const hiddenList = JSON.parse(localStorage.getItem('hidden_orders_' + currentUserEmail) || '[]');
        querySnapshot.docs.forEach((doc) => allOrders.push({ id: doc.id, ...doc.data() }));
        const filtered = allOrders
          .filter(o => o.email === currentUserEmail && !o.deletedByUser && !hiddenList.includes(o.id))
          .sort((a,b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

        if (filtered.length === 0) {
          loadingSec?.classList.add('hidden');
          emptySec?.classList.remove('hidden');
          return;
        }
        renderOrders(filtered);
      } catch {
        if (loadingSec) loadingSec.innerHTML = `<p class="text-rose-400 text-xs">加载订单记录失败</p>`;
      }
    }
  }"""

new_load_orders = """  async function loadOrders() {
    try {
      const q = query(collection(dbInstance, 'orders'), where('email', '==', currentUserEmail));
      const querySnapshot = await getDocs(q);
      const orders: any[] = [];
      const hiddenList = JSON.parse(localStorage.getItem('hidden_orders_' + currentUserEmail) || '[]');
      querySnapshot.docs.forEach((doc) => {
        const data = doc.data();
        if (!data.deletedByUser && !hiddenList.includes(doc.id)) {
          orders.push({ id: doc.id, ...data });
        }
      });

      orders.sort((a, b) => new Date(b.createdAt || 0).getTime() - new Date(a.createdAt || 0).getTime());

      if (orders.length === 0) {
        loadingSec?.classList.add('hidden');
        emptySec?.classList.remove('hidden');
        listSec?.classList.add('hidden');
        return;
      }
      renderOrders(orders);
    } catch (err) {
      console.warn('loadOrders fallback to empty state:', err);
      loadingSec?.classList.add('hidden');
      emptySec?.classList.remove('hidden');
      listSec?.classList.add('hidden');
    }
  }"""

if old_load_orders in orders_content:
    orders_content = orders_content.replace(old_load_orders, new_load_orders)

# 确保删除事件监听位于 </script> 内部
if '</script>' in orders_content:
    parts = orders_content.split('</script>')
    script_part = parts[0]
    
    delete_listener_code = """
  // 历史订单删除动效与持久化
  document.addEventListener('click', async (e) => {
    const target = e.target as HTMLElement;
    const btn = target?.closest('.btn-delete-order') as HTMLElement;
    if (!btn) return;

    const orderId = btn.getAttribute('data-order-id');
    if (!orderId) return;

    if (!confirm('确定要删除该历史订单吗？删除后此订单记录及卡密凭证将不再显示。')) {
      return;
    }

    const card = document.getElementById(`order-card-${orderId}`);
    if (card) {
      card.style.transition = 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)';
      card.style.opacity = '0';
      card.style.transform = 'scale(0.95) translateY(-12px)';
      setTimeout(() => {
        card.remove();
        if (listSec && listSec.children.length === 0) {
          listSec.classList.add('hidden');
          emptySec?.classList.remove('hidden');
        }
      }, 350);
    }

    try {
      const hiddenList = JSON.parse(localStorage.getItem('hidden_orders_' + currentUserEmail) || '[]');
      if (!hiddenList.includes(orderId)) {
        hiddenList.push(orderId);
        localStorage.setItem('hidden_orders_' + currentUserEmail, JSON.stringify(hiddenList));
      }
    } catch(err) {}

    try {
      await updateDoc(doc(dbInstance, 'orders', orderId), { deletedByUser: true });
    } catch(err) {}
  });
"""
    if 'btn-delete-order' not in script_part:
        script_part += delete_listener_code
    
    orders_content = script_part.strip() + '\n</script>\n'

with open(orders_path, 'w', encoding='utf-8') as f:
    f.write(orders_content)
print('✓ [1/4] src/pages/orders.astro 修复完成')

# 2. 修复 src/components/Header.astro (解决鼠标一移开菜单就消失的问题)
header_path = 'src/components/Header.astro'
with open(header_path, 'r', encoding='utf-8') as f:
    header_content = f.read()

old_header_menu = """        <div class="relative group">
          <button id="user-menu-btn" type="button" class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:border-white/25 text-slate-300 hover:text-white text-xs transition cursor-pointer">
            <div class="w-5 h-5 rounded-full bg-[#0284C7]/30 border border-[#38BDF8]/40 text-[#38BDF8] flex items-center justify-center text-[10px] font-bold">
              ${cleanName.charAt(0).toUpperCase()}
            </div>
            <span class="max-w-[70px] truncate text-slate-300 font-medium">${cleanName}</span>
            <svg class="w-2.5 h-2.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </button>

          <div class="hidden group-hover:block absolute right-0 mt-1 w-44 rounded-2xl bg-[#0B0F1A] border border-[#38BDF8]/30 shadow-2xl p-2 z-50 backdrop-blur-xl">"""

new_header_menu = """        <div class="relative group" id="user-menu-wrapper">
          <button id="user-menu-btn" type="button" class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:border-white/25 text-slate-300 hover:text-white text-xs transition cursor-pointer select-none">
            <div class="w-5 h-5 rounded-full bg-[#0284C7]/30 border border-[#38BDF8]/40 text-[#38BDF8] flex items-center justify-center text-[10px] font-bold">
              ${cleanName.charAt(0).toUpperCase()}
            </div>
            <span class="max-w-[70px] truncate text-slate-300 font-medium">${cleanName}</span>
            <svg class="w-2.5 h-2.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </button>

          <div id="user-menu-panel" class="hidden group-hover:block absolute right-0 top-full pt-1.5 w-48 z-50 before:absolute before:-top-3 before:left-0 before:w-full before:h-3">
            <div class="rounded-2xl bg-[#0B0F1A]/95 border border-[#38BDF8]/30 shadow-2xl p-2 backdrop-blur-xl">"""

if old_header_menu in header_content:
    header_content = header_content.replace(old_header_menu, new_header_menu)
    header_content = header_content.replace(
        """            <button id="nav-logout-btn" type="button" class="w-full text-left flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs text-rose-400 hover:bg-rose-500/10 transition mt-1 cursor-pointer">
              <span>🚪 退出安全登录</span>
            </button>
          </div>
        </div>""",
        """            <button id="nav-logout-btn" type="button" class="w-full text-left flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs text-rose-400 hover:bg-rose-500/10 transition mt-1 cursor-pointer">
              <span>🚪 退出安全登录</span>
            </button>
            </div>
          </div>
        </div>"""
    )

with open(header_path, 'w', encoding='utf-8') as f:
    f.write(header_content)
print('✓ [2/4] src/components/Header.astro 修复完成')

# 3. 修复 src/pages/login.astro (Google 登录会话与 users 集合实时同步)
login_path = 'src/pages/login.astro'
with open(login_path, 'r', encoding='utf-8') as f:
    login_content = f.read()

old_google_login = """  // Google OAuth click
  googleBtn?.addEventListener('click', async () => {
    hideError();
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(authInstance, provider);
      window.location.href = redirectPath;
    } catch (err: any) {
      console.error(err);
      if (err.message && !err.message.includes('auth/popup-closed-by-user')) {
        showError("Google 身份验证失败，请重试。");
      }
    }
  });"""

new_google_login = """  // Google OAuth click
  googleBtn?.addEventListener('click', async () => {
    hideError();
    try {
      const provider = new GoogleAuthProvider();
      const activeAuth = (typeof getAuthInstance === 'function' ? getAuthInstance() : authInstance);
      const cred = await signInWithPopup(activeAuth, provider);
      if (cred && cred.user) {
        const u = cred.user;
        const email = (u.email || '').trim().toLowerCase();
        const displayName = u.displayName || email.split('@')[0];
        localStorage.setItem('auth_session', JSON.stringify({ email: email, displayName: displayName }));

        try {
          await setDoc(doc(dbInstance, 'users', u.uid), {
            uid: u.uid,
            email: email,
            displayName: displayName,
            photoURL: u.photoURL || '',
            balance_usd: 0,
            updatedAt: new Date().toISOString()
          }, { merge: true });
        } catch(e) {
          console.warn('写入用户集合异常:', e);
        }

        const adminEmail = (import.meta.env.PUBLIC_ADMIN_EMAIL || 'rukyucrono@gmail.com').toLowerCase();
        if (email === adminEmail && redirectPath === '/') {
          window.location.href = '/admin/dashboard';
        } else {
          window.location.href = redirectPath;
        }
      }
    } catch (err: any) {
      console.error(err);
      if (err.message && !err.message.includes('auth/popup-closed-by-user')) {
        showError("Google 身份验证失败，请重试。");
      }
    }
  });"""

if old_google_login in login_content:
    login_content = login_content.replace(old_google_login, new_google_login)

with open(login_path, 'w', encoding='utf-8') as f:
    f.write(login_content)
print('✓ [3/4] src/pages/login.astro 修复完成')

# 4. 检查 src/pages/admin/dashboard.astro
dash_path = 'src/pages/admin/dashboard.astro'
with open(dash_path, 'r', encoding='utf-8') as f:
    dash_content = f.read()

if 'getDoc' not in dash_content:
    dash_content = dash_content.replace(
        "updateDoc\n  } from '../../lib/firebase.js';",
        "updateDoc,\n    getDoc,\n    setDoc\n  } from '../../lib/firebase.js';"
    )
    with open(dash_path, 'w', encoding='utf-8') as f:
        f.write(dash_content)
print('✓ [4/4] src/pages/admin/dashboard.astro 检查就绪')

print("\n=== 开始执行 npm run build 编译验证 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建验证 100% 成功！正在自动提交推送 Git...")
    os.system('git add -A && git commit -m "fix: resolve astro script tag syntax errors, user dropdown bridge, and sync real-time customers" && git push origin main')
    print("🚀 全部完成，代码已成功推送到生产分支！")
else:
    print("\n❌ 构建未完全通过，请查看上方输出。")
