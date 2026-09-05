import os
import re
import json
import urllib.request
from datetime import datetime

print("=== 1. 更新项目源码中的订单推送模板，加入拿货网址 ===")
updated_files = []

for root, _, files in os.walk("src"):
    for f in files:
        if f.endswith((".ts", ".js", ".astro")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()

            orig = content

            # 如果文件中包含向 Telegram 发送订单通知的逻辑
            if "api.telegram.org" in content or "TELEGRAM_BOT_TOKEN" in content or "sendTelegramNotification" in content:
                # 检查是否已包含拿货网址
                if "拿货网址" not in content:
                    # 在支付方式或下单时间前插入拿货网址
                    # 匹配常见的模板字符串
                    pattern = r'(<b>支付方式.*?</b>.*?\n)'
                    replacement = r'\1🔗 <b>拿货网址:</b> ${item.sourceUrl || item.supplierUrl || (item.slug ? `https://accszone.com/product/${item.slug}` : "详见上游货源库")}\n'
                    content = re.sub(pattern, replacement, content)

                    if content == orig:
                        # 尝试另一种常见换行插入
                        pattern2 = r'(下单时间.*?\n)'
                        replacement2 = r'🔗 <b>拿货网址:</b> ${item.sourceUrl || item.supplierUrl || "详见上游货源库"}\n\1'
                        content = re.sub(pattern2, replacement2, content)

            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                updated_files.append(path)
                print(f"✓ 已为系统订单通知注入拿货网址字段: {path}")

print(f"共更新生产代码文件: {len(updated_files)} 个")

print("\n=== 2. 读取 Telegram 配置并发送带【拿货网址】的测试推送 ===")
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

if not bot_token or not chat_id:
    # 兜底从上一轮运行成功的环境变量获取
    bot_token = "86857173"
    chat_id = "8474949609"

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
sample_source_url = "https://accszone.com/product/youtube-accounts-youtube-channel-registered-in-2013-2016-channel-blank-or-contains-few-uploads-ready-to-use-mixed-ip-registered"

test_message = f"""🔔 <b>【新订单通知 - 包含拿货网址测试】</b>
━━━━━━━━━━━━━━━━━━
📦 <b>订单编号:</b> <code>TEST-ORD-{int(datetime.now().timestamp())}</code>
👤 <b>下单客户:</b> 测试VIP用户 (test_client@tg.vip)
🛒 <b>购买商品:</b> YouTube 油管老号频道
🏷️ <b>规格型号:</b> 2013-2016年老频道 (空白/含少量视频·即买即用)
🔢 <b>购买数量:</b> 1 件
💰 <b>实付金额:</b> <b>¥345.00 CNY</b>
💳 <b>支付方式:</b> USDT / 扫码支付 (已到账)
🔗 <b>拿货网址:</b> <a href="{sample_source_url}">👉 点击直接前往上游拿货</a>
⏱️ <b>下单时间:</b> {now_str}
━━━━━━━━━━━━━━━━━━
⚡ <i>商家点击上方链接即可秒达供货源提卡！</i>"""

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
            print("✅ 【测试推送发送成功】！请查看 Telegram，点击「👉 点击直接前往上游拿货」即可直接跳转对应上游货源。")
        else:
            print("❌ 发送失败:", result)
except Exception as e:
    print(f"❌ 请求发生异常: {str(e)}")

