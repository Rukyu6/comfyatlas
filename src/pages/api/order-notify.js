
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
  ].join("\n");
}

import { fetch, ProxyAgent } from 'undici';

export const prerender = false; // Run on-demand as a serverless endpoint

const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
const dispatcher = proxyUrl ? new ProxyAgent(proxyUrl) : undefined;

export async function POST({ request }) {
  try {
    const body = await request.json();
    const { orderId, totalUsd, paymentMethod, createdAt, username, items = [] } = body;

    const botToken = import.meta.env.TELEGRAM_BOT_TOKEN_1;
    const chatId = import.meta.env.TELEGRAM_CHAT_ID;

    if (!botToken || !chatId) {
      return new Response(JSON.stringify({ error: "Missing Bot 1 credentials on server" }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const host = request.headers.get('host') || 'comfyatlas.com';
    const methodLabel = paymentMethod;
    
    // Formatting date to CST (Shanghai)
    let formattedDate = '';
    try {
      formattedDate = new Date(createdAt).toLocaleString('zh-CN', { 
        timeZone: 'Asia/Shanghai',
        hour12: false
      });
    } catch (e) {
      formattedDate = new Date().toLocaleString('zh-CN', { 
        timeZone: 'Asia/Shanghai',
        hour12: false
      });
    }

    const message = `💰 *新订单通知*\n` +
                    `-----------------------------\n` +
                    `*商户订单号:* \`${orderId}\`\n` +
`🛒 *货源拿货直达:* ${items && items[0] && items[0].id ? 'https://chuhai91.cc/item/' + String(items[0].id).replace(/\D/g,'') : 'https://chuhai91.cc/products'}\n` +
                    `*会员名称:* ${username || '游客'}\n` +
                    `*订单金额:* ¥${totalCny || Math.round(totalUsd * 7.2)} CNY (≈ ${Math.ceil(totalUsd)} USDT)
` +
                    `*支付方式:* ${methodLabel}\n` +
                    `*创建时间:* ${formattedDate}\n` +
                    `*通知状态:* 通知成功`;

    const telegramUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;
    const res = await fetch(telegramUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: 'Markdown'
      }),
      ...(dispatcher ? { dispatcher } : {})
    });

    const data = await res.json();
    return new Response(JSON.stringify({ success: data.ok }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
