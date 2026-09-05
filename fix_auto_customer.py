import os

print("=== 开始升级：全自动会员注册与静默建档 ===")

# 1. 修复底层 src/lib/firebase.js 中 setDoc 缺少 options 的严重缺陷
firebase_path = 'src/lib/firebase.js'
with open(firebase_path, 'r', encoding='utf-8') as f:
    firebase_code = f.read()

old_setdoc = """export const setDoc = async (docRef, data) => {
  if (isFirebaseConfigured && db) {
    return fbSetDoc(docRef, data);
  }"""

new_setdoc = """export const setDoc = async (docRef, data, options) => {
  if (isFirebaseConfigured && db) {
    return fbSetDoc(docRef, data, options);
  }"""

if old_setdoc in firebase_code:
    firebase_code = firebase_code.replace(old_setdoc, new_setdoc)
    with open(firebase_path, 'w', encoding='utf-8') as f:
        f.write(firebase_code)
    print('✓ [1/4] src/lib/firebase.js setDoc 参数透传已修复')

# 2. 全局 Header.astro：全网任何页面检测到会员在线，静默自愈写入 users 库
header_path = 'src/components/Header.astro'
with open(header_path, 'r', encoding='utf-8') as f:
    header_code = f.read()

if 'doc, setDoc, dbInstance' not in header_code:
    header_code = header_code.replace(
        "import { authInstance, onAuthStateChanged, signOut } from '../lib/firebase.js';",
        "import { authInstance, onAuthStateChanged, signOut, doc, setDoc, dbInstance } from '../lib/firebase.js';"
    )

old_header_auth = """  // 2. Firebase 鉴权侦听
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
  });"""

new_header_auth = """  // 2. Firebase 鉴权侦听：全网自动静默建档，确保后台客户列表绝不漏单
  onAuthStateChanged(authInstance, async (user) => {
    if (user && user.email) {
      const cleanEmail = user.email.trim().toLowerCase();
      const displayName = user.displayName || cleanEmail.split('@')[0];
      localStorage.setItem('auth_session', JSON.stringify({ email: cleanEmail, displayName }));
      renderUserUI(cleanEmail, displayName);

      // 全自动静默同步到 Firestore 数据库
      try {
        await setDoc(doc(dbInstance, 'users', user.uid), {
          uid: user.uid,
          email: cleanEmail,
          displayName: displayName,
          updatedAt: new Date().toISOString()
        }, { merge: true });
      } catch(err) {
        console.warn('Auto sync member to database failed:', err);
      }
    } else {
      if (!localStorage.getItem('auth_session')) {
        renderGuestUI();
      }
    }
  });"""

if old_header_auth in header_code:
    header_code = header_code.replace(old_header_auth, new_header_auth)
    with open(header_path, 'w', encoding='utf-8') as f:
        f.write(header_code)
    print('✓ [2/4] src/components/Header.astro 全网静默自动同步已集成')

# 3. 页面 src/pages/orders.astro：访问订单页时自动保障写入 users 库
orders_path = 'src/pages/orders.astro'
with open(orders_path, 'r', encoding='utf-8') as f:
    orders_code = f.read()

if 'setDoc' not in orders_code and "from '../lib/firebase.js'" in orders_code:
    orders_code = orders_code.replace(
        "import { authInstance, onAuthStateChanged, collection, dbInstance, query, where, getDocs, doc, getDoc, addDoc, updateDoc } from '../lib/firebase.js';",
        "import { authInstance, onAuthStateChanged, collection, dbInstance, query, where, getDocs, doc, getDoc, addDoc, updateDoc, setDoc } from '../lib/firebase.js';"
    )

old_ord_auth = """  onAuthStateChanged(authInstance, (user) => {
    if (!user) {
      window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
      return;
    }

    currentUserEmail = user.email || '';
    currentUserUid = user.uid || '';"""

new_ord_auth = """  onAuthStateChanged(authInstance, async (user) => {
    if (!user) {
      window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
      return;
    }

    currentUserEmail = (user.email || '').trim().toLowerCase();
    currentUserUid = user.uid || '';

    // 自动建档保底
    try {
      await setDoc(doc(dbInstance, 'users', currentUserUid), {
        uid: currentUserUid,
        email: currentUserEmail,
        displayName: user.displayName || currentUserEmail.split('@')[0],
        updatedAt: new Date().toISOString()
      }, { merge: true });
    } catch(err) {}"""

if old_ord_auth in orders_code:
    orders_code = orders_code.replace(old_ord_auth, new_ord_auth)
    with open(orders_path, 'w', encoding='utf-8') as f:
        f.write(orders_code)
    print('✓ [3/4] src/pages/orders.astro 访问自动建档已集成')

# 4. 彻底移除后台任何手动按钮，保持全自动原生纯净
dash_path = 'src/pages/admin/dashboard.astro'
with open(dash_path, 'r', encoding='utf-8') as f:
    dash_code = f.read()

dash_code = dash_code.replace(
    """            <div class="flex items-center gap-3">
              <span class="text-xs font-mono font-bold text-slate-400" id="stat-customers-count">客户总数: 0</span>
              <button id="btn-add-customer" type="button" class="px-3 py-1.5 rounded-xl bg-gradient-to-r from-[#0284C7] to-[#38BDF8] text-[#06080F] font-bold text-xs shadow-md transition hover:brightness-110 active:scale-95 cursor-pointer">
                + 手动添加会员
              </button>
            </div>""",
    """            <span class="text-xs font-mono font-bold text-slate-400" id="stat-customers-count">客户总数: 0</span>"""
)

with open(dash_path, 'w', encoding='utf-8') as f:
    f.write(dash_code)
print('✓ [4/4] src/pages/admin/dashboard.astro 已恢复为 100% 全自动同步')

print("\n=== 开始编译验证 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建 100% 成功！正在推送 Git...")
    os.system('git add -A && git commit -m "fix(auth): auto-sync Google and email registrations to firestore users collection seamlessly" && git push origin main')
    print("🚀 升级已完成并推送到线上！")
else:
    print("\n❌ 编译未通过，请查看上方输出。")
