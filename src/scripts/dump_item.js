import fs from 'fs';
const data = JSON.parse(fs.readFileSync('src/data/tutorials.json', 'utf8'));
const item = data.find(x => x.id === '019c078f-a3df-75cf-b641-72edd25f40ba');
if (item) {
  console.log('Item found!');
  console.log('Name:', item.name);
  console.log('Length of content_html:', item.content_html ? item.content_html.length : 0);
  console.log('Content snippet:', item.content_html ? item.content_html.substring(0, 500) : 'null');
} else {
  console.log('Item not found!');
}
