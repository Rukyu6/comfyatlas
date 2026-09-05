import os
import shutil

print("=== 开始配置置顶正中蓝染原声播放 Icon ===")

# 1. 复制用户上传的原图到 public/images/aizen_audio_icon.jpg
src_icon = "/mnt/c/Users/YAGEW/.gemini/antigravity/brain/d30a0077-5c2b-45f2-abbc-d64c81304cac/.user_uploaded/media_1788572770061.jpg"
dest_icon = "public/images/aizen_audio_icon.jpg"
os.makedirs("public/images", exist_ok=True)

if os.path.exists(src_icon):
    shutil.copy2(src_icon, dest_icon)
    print("✓ 蓝染音效头像已成功同步到 public/images/aizen_audio_icon.jpg")
else:
    print(f"⚠️ 未找到源图片 {src_icon}，请检查路径")

# 2. 取消 BaseLayout.astro 里的进站自动播放
base_path = 'src/layouts/BaseLayout.astro'
with open(base_path, 'r', encoding='utf-8') as f:
    base_content = f.read()

# 移除自动播放代码段
if 'id="soul-society-welcome"' in base_content:
    parts = base_content.split('<!-- 尸魂界欢迎原声音频 (纯静默无界面) -->')
    head_part = parts[0]
    tail_part = parts[1].split('</body>')[1]
    base_content = head_part.strip() + '\n  </body>' + tail_part
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(base_content)
    print("✓ 已彻底取消网站进站自动播放")

# 3. 在 Header.astro 正中间置顶插入蓝染播放 Icon
header_path = 'src/components/Header.astro'
with open(header_path, 'r', encoding='utf-8') as f:
    header_code = f.read()

old_logo_end = """      </div>
    </a>"""

center_icon_html = """      </div>
    </a>

    <!-- 网页置顶正中间：蓝染原声点击播放 Icon -->
    <div class="absolute left-1/2 -translate-x-1/2 flex items-center justify-center pointer-events-auto">
      <button 
        id="aizen-sound-btn" 
        type="button" 
        class="relative flex items-center justify-center p-0.5 rounded-2xl bg-[#0B0F1A]/90 border-2 border-[#38BDF8]/40 hover:border-[#38BDF8] shadow-[0_0_15px_rgba(56,189,248,0.3)] hover:shadow-[0_0_25px_rgba(56,189,248,0.7)] hover:scale-105 active:scale-95 transition-all duration-300 cursor-pointer group select-none"
        title="点击播放：蓝染惣右介原声"
        aria-label="播放蓝染原声"
      >
        <img 
          src="/images/aizen_audio_icon.jpg" 
          alt="Aizen Voice" 
          class="w-10 h-10 sm:w-11 sm:h-11 object-cover rounded-xl group-hover:brightness-110 transition-all"
        />
        <!-- 播放时动态声波光环 -->
        <span id="aizen-sound-pulse" class="hidden absolute -inset-1 rounded-2xl border-2 border-[#38BDF8] animate-ping pointer-events-none opacity-60"></span>
      </button>

      <!-- 原声音频播放源 -->
      <audio id="aizen-voice-player" preload="auto" class="hidden">
        <source src="/audio/welcome.mp3" type="audio/mpeg" />
        <source src="/audio/welcome.mp4" type="audio/mp4" />
      </audio>
    </div>"""

if old_logo_end in header_code and 'id="aizen-sound-btn"' not in header_code:
    header_code = header_code.replace(old_logo_end, center_icon_html)

# 插入播放与点击响应逻辑
aizen_click_script = """
  // 网页置顶正中：蓝染原声点击播放/暂停交互
  const aizenBtn = document.getElementById('aizen-sound-btn');
  const aizenAudio = document.getElementById('aizen-voice-player');
  const aizenPulse = document.getElementById('aizen-sound-pulse');

  aizenBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!aizenAudio) return;

    if (aizenAudio.paused) {
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
    }
  });

  aizenAudio?.addEventListener('ended', () => {
    aizenPulse?.classList.add('hidden');
  });

  aizenAudio?.addEventListener('pause', () => {
    aizenPulse?.classList.add('hidden');
  });
"""

if 'aizen-sound-btn' not in header_code:
    pass
elif 'const aizenBtn' not in header_code:
    header_code = header_code.replace("</script>", aizen_click_script + "\n</script>")

with open(header_path, 'w', encoding='utf-8') as f:
    f.write(header_code)
print("✓ src/components/Header.astro 居中播放 Icon 与点击交互已就绪")

print("\n=== 开始编译验证 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建 100% 成功！正在推送 Git...")
    os.system('git add -A && git commit -m "feat: place Aizen audio player icon at top-center of header and disable autoplay" && git push origin main')
    print("🚀 升级已完成并推送到线上！")
else:
    print("\n❌ 编译未通过，请查看上方输出。")
