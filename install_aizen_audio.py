import os
import shutil
import subprocess

print("=== 开始提取 CapCut 0903 音频并配置纯净单次播放 ===")

src_mp4 = "/mnt/c/Users/YAGEW/AppData/Local/CapCut/Videos/0903.mp4"
audio_dir = "public/audio"
os.makedirs(audio_dir, exist_ok=True)
dest_mp3 = os.path.join(audio_dir, "welcome.mp3")
dest_mp4 = os.path.join(audio_dir, "welcome.mp4")

# 1. 复制与提取音频文件
if os.path.exists(src_mp4):
    # 尝试用 ffmpeg 提取干净纯音频
    extracted = False
    try:
        res = subprocess.run(
            ["ffmpeg", "-y", "-i", src_mp4, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", dest_mp3],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if res.returncode == 0:
            extracted = True
            print("✓ 已通过 ffmpeg 成功将 0903.mp4 提取为高质量 welcome.mp3")
    except Exception:
        pass

    # 无论是否提取出 mp3，都保留 mp4 原格式作为双保险
    shutil.copy2(src_mp4, dest_mp4)
    if not extracted:
        shutil.copy2(src_mp4, dest_mp3)
        print("✓ 已直接同步源音频为 welcome.mp3 与 welcome.mp4")
else:
    print(f"⚠️ 未找到路径 {src_mp4}，将使用现有音频目录文件")

# 2. 在 BaseLayout.astro 中植入纯净静默播放器与单次播放记忆
base_path = 'src/layouts/BaseLayout.astro'
with open(base_path, 'r', encoding='utf-8') as f:
    base_content = f.read()

audio_dom_and_script = """
    <!-- 尸魂界欢迎原声音频 (纯静默无界面) -->
    <audio id="soul-society-welcome" preload="auto" class="hidden">
      <source src="/audio/welcome.mp3" type="audio/mpeg" />
      <source src="/audio/welcome.mp4" type="audio/mp4" />
    </audio>

    <script is:inline>
      (function() {
        // 用户进入网站只播放一次 (通过 sessionStorage 记忆)
        if (sessionStorage.getItem('aizen_welcomed')) return;

        function playOnce() {
          var audio = document.getElementById('soul-society-welcome');
          if (!audio) return;
          audio.volume = 0.85;

          var markPlayed = function() {
            sessionStorage.setItem('aizen_welcomed', '1');
            ['click', 'touchstart', 'keydown'].forEach(function(evt) {
              document.removeEventListener(evt, unlock);
            });
          };

          var unlock = function() {
            if (sessionStorage.getItem('aizen_welcomed')) return;
            audio.play().then(markPlayed).catch(function() {});
          };

          audio.play().then(markPlayed).catch(function() {
            // 浏览器策略拦截自动播放时，在用户第一次任意点击网页时唤醒
            ['click', 'touchstart', 'keydown'].forEach(function(evt) {
              document.addEventListener(evt, unlock, { once: true });
            });
          });
        }

        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', playOnce);
        } else {
          playOnce();
        }
      })();
    </script>
  </body>"""

if 'id="soul-society-welcome"' not in base_content:
    base_content = base_content.replace("  </body>", audio_dom_and_script)
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(base_content)
    print("✓ src/layouts/BaseLayout.astro 纯净单次播放逻辑已注入")

print("\n=== 开始编译验证 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建 100% 成功！正在推送 Git...")
    os.system('git add -A && git commit -m "feat: embed 0903 welcome voice, play only once per session without any UI buttons" && git push origin main')
    print("🚀 欢迎语音已成功嵌入并推送到线上！")
else:
    print("\n❌ 编译未通过，请查看上方输出。")
