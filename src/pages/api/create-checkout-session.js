import Stripe from 'stripe';

export const prerender = false; // Run on-demand as a serverless endpoint

export async function POST({ request }) {
  try {
    const { orderId, email, items } = await request.json();

    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey) {
      return new Response(JSON.stringify({ error: "Stripe secret key not configured on server" }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const stripe = new Stripe(stripeSecretKey);
    const host = request.headers.get('host') || 'comfyatlas.com';
    
    // Determine protocol: secure Vercel deployments usually proxy over HTTPS
    const protocol = host.includes('localhost') || host.includes('127.0.0.1') ? 'http' : 'https';
    const origin = `${protocol}://${host}`;

    // Map cart items to Stripe line items
    const lineItems = items.map(item => {
      // Stripe amount is in cents
      const unitAmountCents = Math.round(item.price * 100);
      return {
        price_data: {
          currency: 'usd',
          product_data: {
            name: item.name,
            images: item.image ? [item.image] : []
          },
          unit_amount: unitAmountCents
        },
        quantity: item.quantity
      };
    });

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card', 'alipay', 'wechat_pay'],
      line_items: lineItems,
      mode: 'payment',
      customer_email: email,
      metadata: {
        orderId: orderId
      },
      payment_method_options: {
        wechat_pay: {
          client: 'web'
        }
      },
      success_url: `${origin}/checkout?status=success&order_id=${orderId}&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/checkout?status=cancel&order_id=${orderId}`
    });

    return new Response(JSON.stringify({ url: session.url }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error("Stripe Session Creation Error:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
