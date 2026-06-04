import fs from 'fs';
const data = JSON.parse(fs.readFileSync('src/data/tutorials.json', 'utf8'));
const item = data.find(x => x.id === '019c078f-95f5-71c5-a8f9-3176f61a80e5');
if (item) {
  console.log(item.content_html);
}
