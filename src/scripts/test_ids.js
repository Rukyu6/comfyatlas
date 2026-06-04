import fs from 'fs';
const data = JSON.parse(fs.readFileSync('src/data/tutorials.json', 'utf8'));
data.forEach(x => {
  console.log(`${x.id} | ${x.name} | ${x.parent_name}`);
});
