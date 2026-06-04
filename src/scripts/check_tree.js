import fs from 'fs';

const treePath = '/mnt/c/Users/YAGEW/.gemini/antigravity/brain/828b859c-e60a-48b8-bcb0-61d65ae331b3/scratch/navigation_tree.json';
const tree = JSON.parse(fs.readFileSync(treePath, 'utf8'));

function findAndPrint(nodes, targetName) {
  for (const n of nodes) {
    if (n.name && n.name.includes(targetName)) {
      console.log('Found:', n.name, 'Type:', n.type, 'Children count:', n.children ? n.children.length : 0);
      if (n.children) {
        n.children.forEach(c => {
          console.log(`  - Child: ${c.name} | ID: ${c.id} | Type: ${c.type}`);
        });
      }
    }
    if (n.children) {
      findAndPrint(n.children, targetName);
    }
  }
}

console.log('--- Instagram search ---');
findAndPrint(tree, 'instagram');

console.log('--- Facebook search ---');
findAndPrint(tree, 'Facebook');
