import os
import re

print("=== 1. 构建全局客户端 SKU 汉化解析引擎 ===")

engine_code = '''
<script is:inline>
window.formatSkuDisplay = function(raw, title) {
  if (!raw) return '标准套餐';
  var s = String(raw).trim();
  
  // 1. 去除供应商前缀与 slug 标识 (如 ACCSZONE-1705|slug=)
  s = s.replace(/^[A-Z0-9_\\-]+(?:\\|slug=|\\:|\\/|\\|)/i, '').replace(/^slug=/i, '').trim();
  
  // 2. 如果本身已经是规范中文（超过3个汉字），直接返回并清理微小前缀
  var chMatch = s.match(/[\\u4e00-\\u9fa5]/g);
  if (chMatch && chMatch.length >= 3) {
    return s.replace(/^ACCSZONE-\\d+\\|?/i, '').replace(/^DEFAULT/i, '标准规格').trim();
  }

  var lower = s.toLowerCase();
  var tags = [];

  // 年份识别
  var ym = lower.match(/(?:registered-in-|year-)?(20\\d{2})-(20\\d{2})/);
  if (ym) tags.push(ym[1] + '-' + ym[2] + '年老号');
  else {
    var sy = lower.match(/(?:registered-in-|year-)(20\\d{2})/);
    if (sy) tags.push(sy[1] + '年老号');
  }

  // 地区与 IP
  if (lower.includes('usa') || lower.includes('us-ip')) tags.push('美国原生IP');
  else if (lower.includes('uk') || lower.includes('uk-ip')) tags.push('英国原生IP');
  else if (lower.includes('japan') || lower.includes('jp')) tags.push('日本原生IP');
  else if (lower.includes('korea')) tags.push('韩国原生IP');
  else if (lower.includes('hongkong') || lower.includes('hk')) tags.push('香港原生IP');
  else if (lower.includes('taiwan') || lower.includes('tw')) tags.push('台湾原生IP');
  else if (lower.includes('germany')) tags.push('德国原生IP');
  else if (lower.includes('france')) tags.push('法国原生IP');
  else if (lower.includes('mixed-ip') || lower.includes('mix-ip')) tags.push('混合原生IP');

  // 安全与验证
  if (lower.includes('sms-verified') || lower.includes('pva') || lower.includes('phone-verified')) tags.push('实体短信验证');
  if (lower.includes('2fa-enabled') || lower.includes('2fa') || lower.includes('two-factor')) tags.push('已开启2FA');

  // 邮箱绑定
  if (lower.includes('outlook') || lower.includes('hotmail')) tags.push('自带Outlook/Hotmail邮箱');
  else if (lower.includes('gmail')) tags.push('自带Gmail邮箱');
  else if (lower.includes('yahoo')) tags.push('自带Yahoo邮箱');
  else if (lower.includes('mail-ru')) tags.push('自带Mail.ru邮箱');
  else if (lower.includes('email') || lower.includes('mail')) tags.push('自带可登邮箱');

  // 账号状态
  if (lower.includes('blank-or-contains-few-uploads') || lower.includes('blank-few-uploads')) tags.push('空白/含少量视频');
  else if (lower.includes('blank') || lower.includes('white')) tags.push('纯白号/空白账户');
  if (lower.includes('with-followers') || lower.includes('subscribers')) tags.push('带真实粉丝/订阅');

  // 协议与开箱
  if (lower.includes('tdata')) tags.push('Tdata电脑端直登');
  if (lower.includes('session')) tags.push('Session+Json格式');
  if (lower.includes('cookie')) tags.push('含Cookie直登');
  if (lower.includes('ready-to-use')) tags.push('即买即用');

  if (tags.length > 0) {
    return tags.join(' | ');
  }

  if (s === 'DEFAULT' || s === 'default') return '官方正版 · 自动发货';
  if (/^SKU-\\d+$/i.test(s)) return '标准套餐 ' + s.toUpperCase();

  // 兜底转为首字母大写词组
  return s.replace(/-/g, ' ').replace(/\\b\\w/g, function(l) { return l.toUpperCase(); });
};
</script>
'''

print("\n=== 2. 扫描所有弹窗、卡片与页面组件并注入汉化引擎 ===")
modified_count = 0
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith(".astro"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            orig = content

            # 针对所有包含 sku 选择按钮或弹窗组件注入引擎
            if "sku-select-btn" in content or "sku" in content.lower():
                if "window.formatSkuDisplay" not in content:
                    content = content + "\n" + engine_code

                # 将前端 JS 中渲染 sku 名字的地方全部包上 window.formatSkuDisplay
                # 匹配常见渲染模板：${sku.name} -> ${window.formatSkuDisplay(sku.name || sku.sku_code || sku.skuCode)}
                content = re.sub(
                    r'\$\{\s*(sku|item|variant)\.(name|skuName|skuCode|sku_code)\s*\}',
                    r'${window.formatSkuDisplay(\1.name || \1.sku_code || \1.skuCode)}',
                    content
                )
                content = re.sub(
                    r'\{\s*(sku|item|variant)\.(name|skuName|skuCode|sku_code)\s*\}',
                    r'{window.formatSkuDisplay(\1.name || \1.sku_code || \1.skuCode)}',
                    content
                )

            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                modified_count += 1
                print(f"✓ 已升级 SKU 渲染组件: {path}")

print(f"共完成 {modified_count} 个组件的全局清洗与升级！")
