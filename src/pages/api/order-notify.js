import { fetch, ProxyAgent } from 'undici';

export const prerender = false; // Run on-demand as a serverless endpoint

const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
const dispatcher = proxyUrl ? new ProxyAgent(proxyUrl) : undefined;

export async function POST({ request }) {
  try {
    const body = await request.json();
    const { orderId, totalUsd, totalCny, paymentMethod, createdAt, username } = body;

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
                    `*会员名称:* ${username || '游客'}\n` +
                    `*订单金额:* $${totalUsd.toFixed(2)} USD / ¥${totalCny} CNY\n` +
                    `*网站域名:* ${host}\n` +
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
