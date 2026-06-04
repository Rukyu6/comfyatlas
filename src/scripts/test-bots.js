import { fetch, ProxyAgent } from 'undici';

const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
const dispatcher = proxyUrl ? new ProxyAgent(proxyUrl) : undefined;

const BOT_TOKEN_1 = process.env.TELEGRAM_BOT_TOKEN_1;
const BOT_TOKEN_2 = process.env.TELEGRAM_BOT_TOKEN_2;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

console.log("=========================================");
console.log("🤖 TELEGRAM BOT TEST RUNNER");
console.log("=========================================");
console.log("Proxy Configured:", proxyUrl || "None");
console.log("Bot 1 Token (Order):", BOT_TOKEN_1 ? "Found (Ends with " + BOT_TOKEN_1.slice(-6) + ")" : "Missing");
console.log("Bot 2 Token (Support):", BOT_TOKEN_2 ? "Found (Ends with " + BOT_TOKEN_2.slice(-6) + ")" : "Missing");
console.log("Target Chat ID:", CHAT_ID);
console.log("=========================================");

async function sendTelegramMessage(botToken, text, label) {
  if (!botToken) {
    console.log(`❌ [${label}] Skipped: No bot token provided in environment.`);
    return;
  }
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: CHAT_ID,
        text: text,
        parse_mode: 'Markdown'
      }),
      ...(dispatcher ? { dispatcher } : {})
    });
    const data = await res.json();
    if (data.ok) {
      console.log(`✅ [${label}] Sent successfully!`);
    } else {
      console.error(`❌ [${label}] Failed. Telegram response:`, data);
    }
  } catch (err) {
    console.error(`❌ [${label}] Connection Error:`, err.message);
  }
}

async function run() {
  const currentTimestamp = new Date().toLocaleString('zh-CN', { 
    timeZone: 'Asia/Shanghai',
    hour12: false
  });

  // Test 1: Order notification using Bot 1 (as currently configured in checkout.astro)
  const orderMessageBot1 = `💰 *【测试】新订单通知 (Bot 1)*\n` +
                          `-----------------------------\n` +
                          `*商户订单号:* \`test-order-bot1-99999\`\n` +
                          `*会员名称:* 测试账号 (RukyuCrono)\n` +
                          `*订单金额:* $9.00 USD / ¥63.00 CNY\n` +
                          `*网站域名:* comfyatlas.com\n` +
                          `*支付方式:* USDT (TRC-20)\n` +
                          `*创建时间:* ${currentTimestamp}\n` +
                          `*通知状态:* 测试发送成功`;

  // Test 2: Order notification using Bot 2 (to test if user wants order notify via Bot 2)
  const orderMessageBot2 = `💰 *【测试】新订单通知 (Bot 2)*\n` +
                          `-----------------------------\n` +
                          `*商户订单号:* \`test-order-bot2-88888\`\n` +
                          `*会员名称:* 测试账号 (RukyuCrono)\n` +
                          `*订单金额:* $9.00 USD / ¥63.00 CNY\n` +
                          `*网站域名:* comfyatlas.com\n` +
                          `*支付方式:* USDT (TRC-20)\n` +
                          `*创建时间:* ${currentTimestamp}\n` +
                          `*通知状态:* 测试发送成功`;

  // Test 3: Customer Support/Inquiry notification using Bot 2 (as currently configured in support-notify.js)
  const supportMessageBot2 = `💬 *【测试】客户咨询留言 (Bot 2)*\n` +
                             `-----------------------------\n` +
                             `*客户:* 测试用户 (rukyucrono@gmail.com)\n` +
                             `*留言内容:* 这是一个用于测试 Bot 2 的留言推送信息，验证客服咨询流程。\n` +
                             `*发送时间:* ${currentTimestamp}\n` +
                             `*通知状态:* 测试发送成功`;

  console.log("\n🚀 Dispatching test requests to Telegram APIs...\n");
  
  console.log("1. Sending Bot 1 Order Notify...");
  await sendTelegramMessage(BOT_TOKEN_1, orderMessageBot1, "Bot 1 - Order Notification");
  
  console.log("\n2. Sending Bot 2 Order Notify...");
  await sendTelegramMessage(BOT_TOKEN_2, orderMessageBot2, "Bot 2 - Order Notification");
  
  console.log("\n3. Sending Bot 2 Support/Inquiry Notify...");
  await sendTelegramMessage(BOT_TOKEN_2, supportMessageBot2, "Bot 2 - Support Notification");
  
  console.log("\n=========================================");
  console.log("🏁 Test suite completed.");
  console.log("=========================================");
}

run();
