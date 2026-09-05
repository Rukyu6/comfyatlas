import os
import re
import json
import urllib.request
from datetime import datetime

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
                k = k.strip()
                v = v.strip().strip("'\"")
                if any(x in k.upper() for x in ["TG_BOT_TOKEN", "TELEGRAM_BOT_TOKEN", "BOT_TOKEN"]) and not bot_token:
                    bot_token = v
                if any(x in k.upper() for x in ["TG_CHAT_ID", "TELEGRAM_CHAT_ID", "ADMIN_CHAT_ID", "TELEGRAM_ADMIN_ID"]) and not chat_id:
                    chat_id = v

if not bot_token or not chat_id:
    for root, _, files in os.walk("src"):
        for f in files:
            if f.endswith((".ts", ".js", ".astro")):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    txt = file.read()
                if not bot_token:
                    m = re.search(r'''(?:botToken|TELEGRAM_BOT_TOKEN|token)\s*[:=]\s*['"]([0-9]{8,11}:[a-zA-Z0-9_-]{30,45})['"]''', txt)
                    if m: bot_token = m.group(1)
                if not chat_id:
                    m2 = re.search(r'''(?:chatId|TELEGRAM_CHAT_ID|adminChatId)\s*[:=]\s*['"]?(-?\d{7,15})['"]?''', txt)
                    if m2: chat_id = m2.group(1)

# 使用 Telegram 原生支持的标准规范排版标签
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
test_message = f"""🔔 <b>【新订单通知 - 测试推送】</b>
━━━━━━━━━━━━━━━━━━
📦 <b>订单编号:</b> <code>TEST-ORD-{int(datetime.now().timestamp())}</code>
👤 <b>下单客户:</b> 测试VIP用户 (test_client@tg.vip)
🛒 <b>购买商品:</b> YouTube 油管老号频道
🏷️ <b>规格型号:</b> 2013-2016年老频道 (空白/含少量视频·即买即用)
🔢 <b>购买数量:</b> 1 件
💰 <b>实付金额:</b> <b>¥345.00 CNY</b>
💳 <b>支付方式:</b> USDT / 扫码支付 (已到账)
⏱️ <b>下单时间:</b> {now_str}
━━━━━━━━━━━━━━━━━━
⚡ <i>订单推送链路检测正常，系统已就绪！</i>"""

api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": test_message,
    "parse_mode": "HTML",
    "disable_web_page_preview": True
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
            print("✅ 测试推送发送成功！请查看您的 Telegram 客户端是否有收到通知。")
        else:
            print("❌ 发送失败，Telegram 返回结果:", result)
except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8")
    print(f"❌ Telegram API HTTP 错误 ({e.code}): {err_body}")
except Exception as e:
    print(f"❌ 请求发生异常: {str(e)}")

