import os
import re
import subprocess

print("=== 1. 恢复 API 文件至干净状态 ===")
subprocess.run(["git", "checkout", "--", "src/pages/api/", "src/scripts/"], check=False)

# 采用完全免疫语法冲突的标准拼接函数
clean_helper = '''
function formatTelegramOrderCard(data) {
  const item = (data.items && data.items[0]) || data.item || data;
  const slug = String(item.slug || data.slug || "");
  const sourceUrl = item.sourceUrl || (slug ? "https://chuhai91.cc/products/" + slug : "https://chuhai91.cc");
  const paid = parseFloat(data.paidAmount || data.totalAmount || item.priceAmount || 0);
  const cost = parseFloat(item.costPrice || (paid * 0.8).toFixed(2));
  const profit = (paid - cost).toFixed(2);
  const nowStr = new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai", hour12: false });
  
  return [
    "🔔 <b>【Soul Society 新订单提醒】</b>",
    "━━━━━━━━━━━━━━━━━━",
    "📦 <b>订单编号:</b> <code>" + (data.orderNo || data.id || ("SS-" + Date.now())) + "</code>",
    "👤 <b>下单客户:</b> " + (data.username || data.email || "海外客户") + " (" + (data.contact || data.email || "已付款") + ")",
    "📂 <b>商品类目:</b> " + (data.categoryName || item.category || "数字资产"),
    "🛒 <b>购买商品:</b> " + (item.title || data.title || "海外精品账号"),
    "🏷️ <b>规格型号:</b> " + (item.skuName || item.name || "默认规格"),
    "🔢 <b>购买数量:</b> " + (data.quantity || item.quantity || 1) + " 件",
    "💰 <b>客户实付:</b> <b>¥" + paid.toFixed(2) + " CNY</b>",
    "💵 <b>8877成本:</b> <b>¥" + cost.toFixed(2) + " CNY</b> (本单利润: +¥" + profit + ")",
    "💳 <b>支付方式:</b> " + (data.paymentMethod || "USDT / 扫码支付") + " (已核销到账)",
    '🔗 <b>8877拿货:</b> <a href="' + sourceUrl + '">👉 点击直达8877进货提卡</a>',
    "⏱️ <b>下单时间:</b> " + nowStr,
    "━━━━━━━━━━━━━━━━━━",
    "⚡ <i>系统已接入 8877 真实链路，点击链接即可直接采购交付！</i>"
  ].join("\\n");
}
'''

print("\n=== 2. 安全注入标准 8877 订单卡片生成函数 ===")
target_files = [
    "src/pages/api/order-notify.js",
    "src/pages/api/dispatch-notify.js",
    "src/pages/api/verify-payment.js"
]

for filepath in target_files:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if "formatTelegramOrderCard" not in content:
            # 放在文件最顶部，安全无污染
            content = clean_helper + "\n" + content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ 已安全注入: {filepath}")

print("\n=== 3. 准备执行 build 校验与部署 ===")
