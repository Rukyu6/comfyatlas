import { fetch, ProxyAgent } from 'undici';

export const prerender = false; // Run on-demand as a serverless endpoint

const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
const dispatcher = proxyUrl ? new ProxyAgent(proxyUrl) : undefined;

export async function POST({ request }) {
  try {
    const body = await request.json();
    const { message, email, username } = body;

    const botToken = import.meta.env.TELEGRAM_BOT_TOKEN_2;
    const chatId = import.meta.env.TELEGRAM_CHAT_ID;

    if (!botToken || !chatId) {
      return new Response(JSON.stringify({ error: "Missing Bot 2 credentials on server" }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const currentTimestamp = new Date().toLocaleString('zh-CN', { 
      timeZone: 'Asia/Shanghai',
      hour12: false
    });

    let formattedMessage = '';
    if (body.type === 'deposit') {
      formattedMessage = `💰 *【充值申请】*\n` +
                         `-----------------------------\n` +
                         `*客户邮箱:* ${email || '未知'}\n` +
                         `*充值金额:* ${body.amount} USDT\n` +
                         `*交易哈希 (TxID):* \`${body.txId}\`\n` +
                         `*发送时间:* ${currentTimestamp}\n` +
                         `*请登录管理员后台进行审核!*`;
    } else {
      let userLabel = `*客户:* 网页游客`;
      if (email) {
        userLabel = username ? `*客户:* ${username} (${email})` : `*客户邮箱:* ${email}`;
      }
      formattedMessage = `💬 *客户咨询留言*\n` +
                         `-----------------------------\n` +
                         `${userLabel}\n` +
                         `*留言内容:* ${message}\n` +
                         `*发送时间:* ${currentTimestamp}\n` +
                         `*通知状态:* 发送成功`;
    }

    const telegramUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;
    const res = await fetch(telegramUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: formattedMessage,
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
