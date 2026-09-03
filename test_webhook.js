import { fetch } from 'undici';

const url = 'http://localhost:4321/api/support-webhook';
const token = 'PuppyShop_Secret_Token_2026';

const payload = {
  update_id: 10000,
  message: {
    message_id: 1,
    from: {
      id: 12345,
      is_bot: false,
      first_name: 'TestUser',
      username: 'testuser'
    },
    chat: {
      id: 12345,
      type: 'private',
      first_name: 'TestUser',
      username: 'testuser'
    },
    date: Math.floor(Date.now() / 1000),
    text: 'Hello bot'
  }
};

async function run() {
  console.log('Sending mock webhook request to localhost...');
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Telegram-Bot-Api-Secret-Token': token
    },
    body: JSON.stringify(payload)
  });

  console.log('Response Status:', res.status);
  const text = await res.text();
  console.log('Response Body:', text);
}

run().catch(console.error);
