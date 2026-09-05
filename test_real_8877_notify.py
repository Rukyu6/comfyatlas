import os
import re
import json
import urllib.request
from datetime import datetime

print("=== 1. 读取 Telegram 配置 ===")
bot_token = None
chat_id = None

for env_file in [".env", ".env.local", ".env.production"]:
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip().upper()
                v = v.strip().strip("'\"")
                if ("TG_BOT_TOKEN" in k or "TELEGRAM_BOT_TOKEN" in k or "BOT_TOKEN" in k) and not bot_token:
                    bot_token = v
                if ("TG_CHAT_ID" in k or "TELEGRAM_CHAT_ID" in k or "ADMIN_CHAT_ID" in k) and not chat_id:
                    chat_id = v

if not bot_token: bot_token = "86857173"
if not chat_id: chat_id = "8474949609"

# 8877 真实的商品链接
real_8877_url = "https://chuhai91.cc/products/youtube-account-2013-2016-channels-blank-or-few-videos-mixed-ip"

print("=== 2. 更新系统源码，将所有拿货网址统一指向 8877 (chuhai91.cc) ===")
for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith((".ts", ".js", ".astro")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
            orig = content

            # 替换以前的 accszone 前缀，换成 8877 的 chuhai91.cc 直达链接
            content = content.replace("https://accszone.com/product/", "https://chuhai91.cc/products/")
            content = content.replace("https://accszone.com/ad_details/", "https://chuhai91.cc/products/")

            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"✓ 已将拿货平台更新为 8877: {path}")

print("\n=== 3. 正在向您的 Telegram 发送 8877 真实拿货测试推送 ===")
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

test_message = f"""🔔 <b>【Soul Society 新订单提醒】</b>
━━━━━━━━━━━━━━━━━━
📦 <b>订单编号:</b> <code>SS-{int(datetime.now().timestamp())}</code>
👤 <b>下单客户:</b> VIP海外客户 (client@digital.vip)
🛒 <b>购买商品:</b> YouTube 账号 | 2013–2016年频道老号
🏷️ <b>规格型号:</b> 2013-2016年老频道 (空白/含少量视频·即买即用)
🔢 <b>购买数量:</b> 1 件
💰 <b>客户实付:</b> <b>¥345.00 CNY</b>
💵 <b>8877成本:</b> <b>¥276.00 CNY</b> (利润: +¥69.00)
💳 <b>支付方式:</b> USDT / 微信支付 (已到账)
🔗 <b>8877拿货:</b> <a href="{real_8877_url}">👉 点击进入8877直达进货提卡</a>
⏱️ <b>下单时间:</b> {now_str}
━━━━━━━━━━━━━━━━━━
⚡ <i>点击上方链接即可秒开 8877 对应商品完成拿货！</i>"""

api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": test_message,
    "parse_mode": "HTML",
    "disable_web_page_preview": False
}

try:
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))
        if result.get("ok"):
            print("✅ 【推送发送成功】！请查看您的 Telegram。")
            print(f"🔗 包含的真实 8877 链接: {real_8877_url}")
        else:
            print("❌ 发送失败:", result)
except Exception as e:
    print(f"❌ 异常: {str(e)}")

