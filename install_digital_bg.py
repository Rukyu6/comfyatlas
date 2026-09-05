import os
import shutil

print("=== 开始替换数字商品现货库背景为死神全员插画 ===")

# 1. 复制用户上传的原画到 public/images/gotei13_bg.jpg
src_img = "/mnt/c/Users/YAGEW/.gemini/antigravity/brain/d30a0077-5c2b-45f2-abbc-d64c81304cac/.user_uploaded/media_1788575598084.jpg"
dest_img = "public/images/gotei13_bg.jpg"
os.makedirs("public/images", exist_ok=True)

if os.path.exists(src_img):
    shutil.copy2(src_img, dest_img)
    print("✓ 死神护廷十三队全员插画已同步至 public/images/gotei13_bg.jpg")
else:
    print(f"⚠️ 未找到路径 {src_img}，请核对路径")

# 2. 改造 src/pages/index.astro 中的 section#digital
index_path = 'src/pages/index.astro'
with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_section = """  <!-- 数字商品现货库商品阵列区 -->
  <section id="digital" class="py-12 relative z-10 font-outfit">
    <div class="max-w-7xl mx-auto px-6">"""

new_section = """  <!-- 数字商品现货库商品阵列区 (配护廷十三队全员画作背景) -->
  <section id="digital" class="py-12 relative z-10 font-outfit overflow-hidden">
    
    <!-- 死神全员原画暗黑水印背景层 -->
    <div class="absolute inset-0 z-0 pointer-events-none overflow-hidden select-none">
      <img 
        src="/images/gotei13_bg.jpg" 
        alt="Bleach Gotei 13 Artwork" 
        class="w-full h-full object-cover object-top opacity-15 filter contrast-125 saturate-125"
      />
      <!-- 渐变遮罩保护层：自然过渡并确保商品信息高对比度 -->
      <div class="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-[#06080F] via-[#06080F]/80 to-transparent"></div>
      <div class="absolute inset-0 bg-[#06080F]/60 backdrop-blur-[1px]"></div>
      <div class="absolute inset-x-0 bottom-0 h-36 bg-gradient-to-t from-[#06080F] via-[#06080F]/80 to-transparent"></div>
    </div>

    <div class="max-w-7xl mx-auto px-6 relative z-10">"""

if old_section in content:
    content = content.replace(old_section, new_section)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ src/pages/index.astro 数字商品库背景层已成功挂载")
else:
    print("⚠️ 未找到匹配的 section#digital 标签，可能已被修改")

print("\n=== 开始编译验证 ===")
res = os.system("npm run build")
if res == 0:
    print("\n🎉 构建 100% 成功！正在推送 Git...")
    os.system('git add -A && git commit -m "style: set Gotei 13 Bleach illustration as background for digital product catalog section" && git push origin main')
    print("🚀 升级已完成并推送到线上！")
else:
    print("\n❌ 编译未通过，请查看上方输出。")
