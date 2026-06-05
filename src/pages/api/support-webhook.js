import { fetch, ProxyAgent } from 'undici';
import { initializeApp, getApps, getApp } from 'firebase/app';
import { getFirestore, doc, setDoc, getDoc } from 'firebase/firestore';

export const prerender = false; // Run on-demand as a serverless endpoint

const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
const dispatcher = proxyUrl ? new ProxyAgent(proxyUrl) : undefined;

const firebaseConfig = {
  apiKey: import.meta.env.PUBLIC_FIREBASE_API_KEY,
  authDomain: import.meta.env.PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.PUBLIC_FIREBASE_APP_ID
};

const SECRET_TOKEN = 'PuppyShop_Secret_Token_2026';

export async function POST({ request }) {
  try {
    // 1. Verify Secret Token for webhook security
    const secretHeader = request.headers.get('X-Telegram-Bot-Api-Secret-Token');
    if (secretHeader !== SECRET_TOKEN) {
      console.warn("Unauthorized webhook request, missing or invalid secret token.");
      return new Response(JSON.stringify({ error: "Unauthorized" }), { 
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const update = await request.json();
    
    // We only process private text/media messages
    if (!update.message) {
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const message = update.message;
    const chat = message.chat;
    const botToken = import.meta.env.TELEGRAM_BOT_TOKEN_2;
    const adminChatId = Number(import.meta.env.TELEGRAM_CHAT_ID);

    if (!botToken || !adminChatId) {
      console.error("Missing Bot Token 2 or Admin Chat ID on server configuration.");
      return new Response(JSON.stringify({ error: "Server Configuration Error" }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Initialize Firebase Client
    const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
    const db = getFirestore(app);

    // Case A: Customer messages the Bot (Forward to Admin)
    if (chat.id !== adminChatId) {
      const forwardUrl = `https://api.telegram.org/bot${botToken}/forwardMessage`;
      const forwardRes = await fetch(forwardUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: adminChatId,
          from_chat_id: chat.id,
          message_id: message.message_id
        }),
        ...(dispatcher ? { dispatcher } : {})
      });
      const forwardData = await forwardRes.json();

      if (forwardData.ok) {
        const forwardedMessageId = forwardData.result.message_id;
        
        // Save the mapping: admin_message_id -> customer_chat_id
        await setDoc(doc(db, "telegram_support_mappings", String(forwardedMessageId)), {
          user_chat_id: chat.id,
          user_first_name: message.from?.first_name || "Unknown",
          user_username: message.from?.username || "",
          timestamp: new Date().toISOString()
        });
      } else {
        console.error("Failed to forward message to admin:", forwardData);
      }
    }
    
    // Case B: Admin replies to the forwarded message (Forward reply to Customer)
    else if (chat.id === adminChatId) {
      if (message.reply_to_message) {
        const repliedMessageId = message.reply_to_message.message_id;
        
        // Find matching mapping in database
        const docRef = doc(db, "telegram_support_mappings", String(repliedMessageId));
        const docSnap = await getDoc(docRef);

        if (docSnap.exists()) {
          const mapping = docSnap.data();
          const customerChatId = mapping.user_chat_id;

          // Copy Admin's reply to the customer
          const copyUrl = `https://api.telegram.org/bot${botToken}/copyMessage`;
          const copyRes = await fetch(copyUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              chat_id: customerChatId,
              from_chat_id: adminChatId,
              message_id: message.message_id
            }),
            ...(dispatcher ? { dispatcher } : {})
          });
          const copyData = await copyRes.json();

          if (!copyData.ok) {
            console.error("Failed to copy message to customer:", copyData);
            // Notify Admin of failure
            await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                chat_id: adminChatId,
                text: `❌ 发送失败: ${copyData.description}`,
                reply_to_message_id: message.message_id
              }),
              ...(dispatcher ? { dispatcher } : {})
            });
          } else {
            // Confirm delivery back to Admin
            await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                chat_id: adminChatId,
                text: `✅ 已送达`,
                reply_to_message_id: message.message_id
              }),
              ...(dispatcher ? { dispatcher } : {})
            });
          }
        } else {
          // No mapping found
          await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              chat_id: adminChatId,
              text: `⚠️ 找不到该消息对应的客户记录。`,
              reply_to_message_id: message.message_id
            }),
            ...(dispatcher ? { dispatcher } : {})
          });
        }
      }
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (err) {
    console.error("Webhook processing failed:", err);
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
