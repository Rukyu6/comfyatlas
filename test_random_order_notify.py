import os
import re
import json
import random
import urllib.request
from datetime import datetime

# 1. 真实商品池（100% 对应 8877 chuhai91.cc 真实在售商品）
REAL_PRODUCTS = [
    {
        "title": "【独享不翻车】ChatGPT Plus 官方订阅 | 1个月纯净成品号",
        "sku": "独享成品号 (可改密·独立邮箱·带售后30天)",
        "sell_price": "249.00",
        "cost_price": "199.00",
        "slug": "chatgpt-plus-1-gpt-5-5-codex-658",
        "category": "AI 生产力大模型"
    },
    {
        "title": "Twitter 推特【国家高权重老号】资料位置可选",
        "sku": "美国原生IP | 实体手机号验证 | 带2FA密钥",
        "sell_price": "45.00",
        "cost_price": "30.00",
        "slug": "twitter-aged-usa-france-canada-japan-italy-uk-germany-1415",
        "category": "海外社媒矩阵"
    },
    {
        "title": "Shadowrocket 苹果小火箭 ID (永久可用·无惧封号)",
        "sku": "美区已购小火箭独享兑换码 | 终身维护更新",
        "sell_price": "29.90",
        "cost_price": "19.80",
        "slug": "recommended-permanent-little-rocket-id-no-ban-freeze-rent-accounts",
        "category": "Apple ID 资产"
    },
    {
        "title": "YouTube 账号 | 包含 2013–2016 年注册的 YouTube 频道",
        "sku": "2013-2016年老频道 (空白/含少量视频·即买即用)",
        "sell_price": "345.00",
        "cost_price": "276.00",
        "slug": "youtube-account-2013-2016-channels-blank-or-few-videos-mixed-ip",
        "category": "油管高权重频道"
    },
    {
        "title": "Gmail 谷歌精品老号 (24年以上极高权重)",
        "sku": "已开2FA双重验证 | 包含辅助邮箱 | 随机国家IP",
        "sell_price": "25.00",
        "cost_price": "15.90",
        "slug": "gmail-account-24-years-old-used-2fa-enabled-us-ip",
        "category": "邮箱基础设施"
    }
]

item = random.choice(REAL_PRODUCTS)
profit = float(item['sell_price']) - float(item['cost_price'])
source_url = f"https://chuhai91.cc/products/{item['slug']}"

# 2. 自动搜索读取项目完整 .env 配置
bot_token = None
chat_id = None

possible_env_files = [
    "/home/crono/projects/comfyatlas/.env",
    os.path.expanduser("~/projects/comfyatlas/.env"),
    ".env",
    ".env.local"
]

for env_file in possible_env_files:
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
    print("❌ 未能在项目中找到完整有效的 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID！")
    exit(1)

print(f"✓ 成功加载完整 Bot Token (长度: {len(bot_token)} 位)")
print(f"✓ 成功加载 Chat ID: {chat_id}")
print(f"=== 本次抽中商品: {item['title']} ===")
print(f"🔗 8877 真实链接: {source_url}")

# 3. 构造推送消息
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
random_order_no = f"SS-{int(datetime.now().timestamp())}{random.randint(100, 999)}"

test_message = f"""🔔 <b>【Soul Society 随机订单推送】</b>
━━━━━━━━━━━━━━━━━━
📦 <b>订单编号:</b> <code>{random_order_no}</code>
👤 <b>下单客户:</b> 跨境企业客户 (enterprise@chuhai.com)
📂 <b>商品类目:</b> {item['category']}
🛒 <b>购买商品:</b> {item['title']}
🏷️ <b>规格型号:</b> {item['sku']}
🔢 <b>购买数量:</b> 1 件
💰 <b>客户实付:</b> <b>¥{item['sell_price']} CNY</b>
💵 <b>8877成本:</b> <b>¥{item['cost_price']} CNY</b> (本单利润: +¥{profit:.2f})
💳 <b>支付方式:</b> USDT-TRC20 (已自动核销)
🔗 <b>8877拿货:</b> <a href="{source_url}">👉 点击直达8877进货提卡</a>
⏱️ <b>下单时间:</b> {now_str}
━━━━━━━━━━━━━━━━━━
⚡ <i>系统已接入 8877 真实链路，点击链接即可直接采购交付！</i>"""

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
            print("✅ 【随机订单测试推送成功】！请查看您的 Telegram 客户端。")
        else:
            print("❌ 推送失败:", result)
except Exception as e:
    print(f"❌ 异常: {str(e)}")

