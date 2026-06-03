export const prerender = false; // Run on-demand as a serverless endpoint

export async function POST({ request }) {
  try {
    const body = await request.json();
    const { orderId, email, createdAt, items, dispatchContent, username } = body;

    const botToken = import.meta.env.TELEGRAM_BOT_TOKEN_1;
    const chatId = import.meta.env.TELEGRAM_CHAT_ID;

    if (!botToken || !chatId) {
      return new Response(JSON.stringify({ error: "Missing Bot 1 credentials on server" }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Format details based on items array
    const firstItemName = items && items.length > 0 ? items[0].name : '虚拟商品';
    const totalQuantity = items ? items.reduce((sum, i) => sum + i.quantity, 0) : 1;
    const itemNamesText = items && items.length > 1 ? `${firstItemName} 等 (共 ${totalQuantity} 件)` : `${firstItemName}`;
    const totalCostUsd = items ? items.reduce((sum, i) => sum + (i.price * i.quantity), 0) : 0;

    // Formatting date to CST (Shanghai)
    let formattedOrderDate = '';
    try {
      formattedOrderDate = new Date(createdAt).toLocaleString('zh-CN', { 
        timeZone: 'Asia/Shanghai',
        hour12: false
      });
    } catch (e) {
      formattedOrderDate = new Date().toLocaleString('zh-CN', { 
        timeZone: 'Asia/Shanghai',
        hour12: false
      });
    }

    const currentTimestamp = new Date().toLocaleString('zh-CN', { 
      timeZone: 'Asia/Shanghai',
      hour12: false
    });

    const userLabel = username ? `${username} (${email || '游客'})` : (email || '游客');

    const message = `📦 *【发货通知】商品已发货！*\n` +
                    `-----------------------------\n` +
                    `*商品名称:* ${itemNamesText}\n` +
                    `*订单号:* \`${orderId}\`\n` +
                    `*下单时间:* ${formattedOrderDate}\n` +
                    `*商品金额:* $${totalCostUsd.toFixed(2)} USD\n` +
                    `*商品数量:* ${totalQuantity}\n` +
                    `*通知时间:* ${currentTimestamp}\n` +
                    `*会员名称:* ${userLabel}\n` +
                    `*下单链接:* https://comfyatlas.com/orders\n` +
                    `*发货内容:* \`${dispatchContent || ''}\``;

    const telegramUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;
    const res = await fetch(telegramUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: 'Markdown'
      })
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
