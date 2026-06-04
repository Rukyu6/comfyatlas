import fs from 'fs';

const filePath = 'src/data/tutorials.json';
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

// 1. Update "问题：接码成功-需要短信费" (ID: 019c078f-95f5-71c5-a8f9-3176f61a80e5)
const itemSms = data.find(x => x.id === '019c078f-95f5-71c5-a8f9-3176f61a80e5');
if (itemSms) {
  const cutoffIndex = itemSms.content_html.indexOf('<h2 id="f1c9fdcc-6ebe-42d7-bb15-919ec7685f97">');
  if (cutoffIndex !== -1) {
    let cleanHtml = itemSms.content_html.substring(0, cutoffIndex);
    // Append keywords footer nicely
    cleanHtml += '<hr class="custom-horizontal-rule"><p><code>Telegram登录提示扣费, 飞机号绕过验证码收费, 电报免短信费登录教程, 网页版电报登录, Nicegram免收费版, puppyshop教程</code></p>';
    itemSms.content_html = cleanHtml;
    console.log('Successfully cut off "方案二" from SMS fee tutorial.');
  } else {
    console.warn('"方案二" section not found in SMS fee tutorial HTML.');
  }
}

// 2. Update "问题：接码成功-需要邮箱" (ID: 019c078f-a3df-75cf-b641-72edd25f40ba)
const itemEmail = data.find(x => x.id === '019c078f-a3df-75cf-b641-72edd25f40ba');
if (itemEmail) {
  // Replace the web.telegram.org link and text with RukyuCrono Telegram link
  const originalLink = '<a target="_blank" type="icon" rel="nofollow" title="https://web.telegram.org/" href="https://web.telegram.org/">https://web.telegram.org/</a>';
  const newLink = '<a target="_blank" type="icon" rel="nofollow" title="https://t.me/RukyuCrono" href="https://t.me/RukyuCrono">https://t.me/RukyuCrono</a>';
  if (itemEmail.content_html.includes(originalLink)) {
    itemEmail.content_html = itemEmail.content_html.replace(originalLink, newLink);
    console.log('Successfully replaced web.telegram.org with RukyuCrono TG link in Email tutorial.');
  } else {
    // Fallback search and replace if spacing differs
    itemEmail.content_html = itemEmail.content_html.replace(/https:\/\/web\.telegram\.org\/?/g, 'https://t.me/RukyuCrono');
    console.log('Replaced web.telegram.org via regex fallback.');
  }
}

fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
console.log('Updated tutorials.json saved.');
