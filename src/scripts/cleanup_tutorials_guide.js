// src/scripts/cleanup_tutorials_guide.js
// Cleans up tutorials.json for the new /guide page.
// 1. Replace all "8877" with "puppyshop".
// 2. Replace any Telegram links with "https://t.me/RukyuCrono".
// 3. Keep only entries whose parent_name is in the allowed sidebar categories (图一).

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Resolve the tutorials.json relative to this script (located in src/scripts)
const tutorialsPath = path.resolve(__dirname, '../data/tutorials.json');

const allowedParents = [
  'telegram/电报 登录教程',
  '推特/ X 登录教程',
  '谷歌账号 - 登录方式',
  'instagram账号 登录教程',
  'Facebook 脸书登录教程',
  'Discord的登录以及修改密码',
  '苹果id账号 登录教程',
  '网站代理设置教程',
  '住宅ip 的使用教程',
  '镜像GPT网站介绍+教程'
];

function replaceAll(str, find, replace) {
  return typeof str === 'string' ? str.split(find).join(replace) : str;
}

function cleanTutorials(data) {
  return data
    .map(item => {
      const cleaned = {
        ...item,
        name: replaceAll(item.name, '8877', 'puppyshop'),
        parent_name: replaceAll(item.parent_name, '8877', 'puppyshop'),
        emoji: replaceAll(item.emoji, '8877', 'puppyshop'),
        content_html: replaceAll(item.content_html, '8877', 'puppyshop')
      };
      if (cleaned.content_html) {
        cleaned.content_html = cleaned.content_html.replace(/https?:\/\/t\.me\/[^"'\s]*/g, 'https://t.me/RukyuCrono');
      }
      return cleaned;
    })
    .filter(item => item.parent_name && allowedParents.includes(item.parent_name));
}

try {
  const raw = fs.readFileSync(tutorialsPath, 'utf8');
  const tutorials = JSON.parse(raw);
  const cleaned = cleanTutorials(tutorials);
  fs.writeFileSync(tutorialsPath, JSON.stringify(cleaned, null, 2), 'utf8');
  console.log('Cleaned tutorials written to', tutorialsPath);
} catch (err) {
  console.error('Error processing tutorials.json:', err);
  process.exit(1);
}
