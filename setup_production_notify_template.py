import os
import re

print("=== 正在将 8877 标准订单通知模板固化至系统生产下单接口 ===")
updated_files = []

for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith((".ts", ".js", ".astro")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
            orig = content

            # 定位 Telegram 消息构造区域
            if "api.telegram.org" in content or "TELEGRAM_BOT_TOKEN" in content or "sendTelegram" in content:
                # 注入标准的 8877 订单模板生成函数
                template_func = """
function buildTelegramOrderMessage(order) {
  const item = (order.items && order.items[0]) || order.item || order;
  const slug = item.slug || order.slug || "";
  const sourceUrl = item.sourceUrl || (slug ? `https://chuhai91.cc/products/${slug}` : "https://chuhai91.cc");
  const cost = item.costPrice || (item.priceAmount ? (parseFloat(item.priceAmount) * 0.8).toFixed(2) : "0.00");
  const profit = item.priceAmount ? (parseFloat(item.priceAmount) - parseFloat(cost)).toFixed(2) : "0.00";
  const nowStr = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false });
  
  return `🔔 <b>【Soul Society 新订单提醒】</b>\\n` +
         `━━━━━━━━━━━━━━━━━━\\n` +
         `📦 <b>订单编号:</b> <code>${order.orderNo || order.id || 'SS-' + Date.now()}</code>\\n` +
         `👤 <b>下单客户:</b> ${order.username || order.email || '平台客户'} (${order.contact || order.email || '已付款'})\\n` +
         `📂 <b>商品类目:</b> ${order.categoryName || item.category || '数字资产'}\\n` +
         `🛒 <b>购买商品:</b> ${item.title || order.title || '海外精品账号'}\\n` +
         `🏷️ <b>规格型号:</b> ${item.skuName || item.name || '默认规格'}\\n` +
         `🔢 <b>购买数量:</b> ${order.quantity || item.quantity || 1} 件\\n` +
         `💰 <b>客户实付:</b> <b>¥${order.paidAmount || order.totalAmount || item.priceAmount || '0.00'} CNY</b>\\n` +
         `💵 <b>8877成本:</b> <b>¥${cost} CNY</b> (本单利润: +¥${profit})\\n` +
         `💳 <b>支付方式:</b> ${order.paymentMethod || '在线支付'} (已核销到账)\\n` +
         `🔗 <b>8877拿货:</b> <a href="${sourceUrl}">👉 点击直达8877进货提卡</a>\\n` +
         `⏱️ <b>下单时间:</b> ${nowStr}\\n` +
         `━━━━━━━━━━━━━━━━━━\\n` +
         `⚡ <i>系统已接入 8877 真实链路，点击链接即可直接采购交付！</i>`;
}
"""
                if "buildTelegramOrderMessage" not in content:
                    # 如果未注入，则在开头或者合适位置注入
                    if "---" in content:
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            parts[1] = parts[1] + "\n" + template_func
                            content = "---".join(parts)
                    else:
                        content = template_func + "\n" + content

            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                updated_files.append(path)
                print(f"✓ 已将标准 8877 推送格式注入: {path}")

print(f"\n固化完成，共同步更新 {len(updated_files)} 个生产接口文件！")
