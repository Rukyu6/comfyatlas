import Stripe from 'stripe';
import { initializeApp, getApps, getApp } from 'firebase/app';
import { getFirestore, doc, updateDoc, getDoc } from 'firebase/firestore';

export const prerender = false; // Run on-demand as a serverless endpoint

// Firebase configuration for server-side initialization
const firebaseConfig = {
  apiKey: process.env.PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.PUBLIC_FIREBASE_APP_ID
};

const isFirebaseConfigured = !!firebaseConfig.apiKey;

export async function POST({ request }) {
  try {
    const { orderId, sessionId } = await request.json();

    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey) {
      return new Response(JSON.stringify({ error: "Stripe secret key not configured on server" }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const stripe = new Stripe(stripeSecretKey);
    
    // Retrieve Checkout Session from Stripe
    const session = await stripe.checkout.sessions.retrieve(sessionId);
    
    if (session.payment_status === 'paid') {
      // Verify that the order ID matches
      const sessionOrderId = session.metadata.orderId;
      if (sessionOrderId !== orderId) {
        return new Response(JSON.stringify({ error: "Order ID mismatch" }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      // Update Firebase Order Status if Firebase is configured
      if (isFirebaseConfigured) {
        const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
        const db = getFirestore(app);
        
        const orderRef = doc(db, 'orders', orderId);
        
        // Fetch current status to avoid duplicate updates or notifications
        const docSnap = await getDoc(orderRef);
        const orderData = docSnap.exists() ? docSnap.data() : null;
        
        if (orderData && orderData.status === 'pending') {
          // Update status to 'paid'
          await updateDoc(orderRef, {
            status: 'paid',
            stripeSessionId: sessionId
          });
          
          // Trigger Telegram order notify (simulate checkout.astro notify)
          const botToken = process.env.TELEGRAM_BOT_TOKEN_1;
          const chatId = process.env.TELEGRAM_CHAT_ID;
          
          if (botToken && chatId) {
            const host = request.headers.get('host') || 'comfyatlas.com';
            const currentTimestamp = new Date().toLocaleString('zh-CN', { 
              timeZone: 'Asia/Shanghai',
              hour12: false
            });
            
            const totalUsd = orderData.totalUsd || (session.amount_total / 100);
            const totalCny = orderData.totalCny || Math.round(totalUsd * 6.8);
            
            const message = `💰 *新订单通知 (Stripe 已付款)*\n` +
                            `-----------------------------\n` +
                            `*商户订单号:* \`${orderId}\`\n` +
                            `*会员名称:* ${orderData.username || '游客'}\n` +
                            `*订单金额:* $${totalUsd.toFixed(2)} USD / ¥${totalCny} CNY\n` +
                            `*网站域名:* ${host}\n` +
                            `*支付方式:* Stripe (信用卡)\n` +
                            `*创建时间:* ${currentTimestamp}\n` +
                            `*通知状态:* 通知成功`;
            
            const telegramUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;
            
            // Check for proxy agent
            const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
            let fetchOptions = {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                chat_id: chatId,
                text: message,
                parse_mode: 'Markdown'
              })
            };
            
            if (proxyUrl) {
              const { ProxyAgent } = await import('undici');
              fetchOptions.dispatcher = new ProxyAgent(proxyUrl);
            }
            
            await fetch(telegramUrl, fetchOptions);
          }
        }
      }

      return new Response(JSON.stringify({ success: true, paymentStatus: 'paid' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      return new Response(JSON.stringify({ error: "Payment not completed on Stripe side" }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  } catch (error) {
    console.error("Stripe Verification Error:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
