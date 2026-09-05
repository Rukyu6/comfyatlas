import os
import re

print("=== 1. 构建全能 SKU 净化引擎 (彻底拦截 MMO39/ACG-FAKA/DEFAULT 等代码) ===")

enhanced_engine = '''<script is:inline>
window.formatSkuDisplay = function(raw, title, specValues) {
  // 1. 若带有规格明细属性 (如 race: "美国")，优先展示属性
  if (specValues && typeof specValues === 'object') {
    var vals = Object.values(specValues).filter(function(v) { return v && typeof v === 'string'; });
    if (vals.length > 0) return vals.join(' · ') + ' (自动发货)';
  }

  var s = String(raw || '').trim();
  var productTitle = String(title || '');

  // 2. 检测是否属于上游供应商内部工单编号 (MMO39, ACCSZONE, ACG-FAKA, DEFAULT 等)
  var isSupplierId = false;
  if (/^MMO\\d*[\\s\\-_]?/i.test(s)) isSupplierId = true;
  if (/^ACCSZONE/i.test(s) && !s.includes('slug=')) isSupplierId = true;
  if (/^ACG[\\-_]FAKA/i.test(s) && !s.includes('slug=')) isSupplierId = true;
  if (/^DEFAULT$/i.test(s) || s === '') isSupplierId = true;
  if (/^[A-Z0-9\\-_]{6,}$/i.test(s) && !/[\\u4e00-\\u9fa5]/.test(s) && !s.includes('slug=')) isSupplierId = true;

  // 如果属于纯供应商内部代号，自动从商品标题中提取核心属性生成精美规格
  if (isSupplierId) {
    var tags = [];
    if (productTitle.includes('2FA') || productTitle.includes('双重认证')) tags.push('已开启2FA认证');
    if (productTitle.includes('5天') || productTitle.includes('天以上')) tags.push('存活5天以上老号');
    if (productTitle.includes('美国') || productTitle.includes('USA')) tags.push('美国原生IP');
    if (productTitle.includes('独享')) tags.push('独享成品号');
    if (productTitle.includes('白号') || productTitle.includes('空白')) tags.push('纯净白号');
    if (productTitle.includes('带作品') || productTitle.includes('带视频')) tags.push('带历史作品');
    if (productTitle.includes('千粉') || productTitle.includes('万粉')) tags.push('带真实粉丝');

    if (tags.length > 0) {
      return tags.join(' · ') + ' (自动发货)';
    }
    return '【官方正版】独享现货 · 自动发货';
  }

  // 3. 剥离 slug 前缀并进行关键词转译
  s = s.replace(/^[A-Z0-9_\\-]+(?:\\|slug=|\\:|\\/|\\|)/i, '').replace(/^slug=/i, '').trim();

  // 如果已经是规范中文，清理前缀返回
  var chMatch = s.match(/[\\u4e00-\\u9fa5]/g);
  if (chMatch && chMatch.length >= 2) {
    return s.replace(/^(?:MMO\\d+|ACCSZONE-\\d+|ACG-FAKA-[A-Z0-9]+)\\s*\\|?/i, '').trim();
  }

  var lower = s.toLowerCase();
  var parsedTags = [];

  if (lower.includes('usa') || lower.includes('us-ip')) parsedTags.push('美国原生IP');
  else if (lower.includes('japan') || lower.includes('jp')) parsedTags.push('日本原生IP');
  else if (lower.includes('hongkong') || lower.includes('hk')) parsedTags.push('香港原生IP');
  else if (lower.includes('korea')) parsedTags.push('韩国原生IP');
  else if (lower.includes('mixed-ip')) parsedTags.push('混合原生IP');

  if (lower.includes('sms-verified') || lower.includes('pva')) parsedTags.push('实体短信验证');
  if (lower.includes('2fa-enabled') || lower.includes('2fa')) parsedTags.push('已开启2FA');

  if (lower.includes('outlook') || lower.includes('hotmail')) parsedTags.push('自带Outlook/Hotmail邮箱');
  else if (lower.includes('gmail')) parsedTags.push('自带Gmail邮箱');

  if (lower.includes('blank-few-uploads') || lower.includes('blank-or-contains-few-uploads')) parsedTags.push('空白/含少量视频');
  else if (lower.includes('blank')) parsedTags.push('纯白号/空白账户');

  if (parsedTags.length > 0) return parsedTags.join(' · ');

  return '【官方正版】独享现货 · 自动发货';
};
</script>'''

print("=== 2. 安全注入组件与弹窗渲染脚本 ===")
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith(".astro"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            orig = content

            # 使用 lambda 安全替换，避开 Python 3.14 字符串转义错误
            if "window.formatSkuDisplay" in content:
                content = re.sub(r'<script is:inline>[\s\S]*?window\.formatSkuDisplay[\s\S]*?<\/script>', lambda _: enhanced_engine.strip(), content)
            elif "sku-select-btn" in content:
                content = content + "\n" + enhanced_engine

            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"✓ 已安全升级: {path}")

print("=== 3. 部署并验证构建 ===")
