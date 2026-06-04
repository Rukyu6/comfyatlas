import fs from 'fs';
const data = JSON.parse(fs.readFileSync('src/data/tutorials.json', 'utf8'));

console.log('--- 问题：接码成功-需要短信费 ---');
const item1 = data.find(x => x.id === '019c078f-95f5-71c5-a8f9-3176f61a80e5');
if (item1) console.log(item1.content_html);

console.log('--- 问题：接码成功-需要邮箱 ---');
const item2 = data.find(x => x.id === '019c078f-a3df-75cf-b641-72edd25f40ba');
if (item2) console.log(item2.content_html);
