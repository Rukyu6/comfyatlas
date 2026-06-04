import fs from 'fs';

const filePath = '/mnt/c/Users/YAGEW/.gemini/antigravity/brain/828b859c-e60a-48b8-bcb0-61d65ae331b3/.system_generated/steps/2550/content.md';
const html = fs.readFileSync(filePath, 'utf8');

// Search for any links matching /node/
const nodeRegex = /\/node\/([a-zA-Z0-9\-]+)/g;
let match;
const nodes = new Set();
while ((match = nodeRegex.exec(html)) !== null) {
  nodes.add(match[1]);
}
console.log('Found Node IDs:', Array.from(nodes));

// Let's search for keywords "instagram" and "Facebook" in the text
const lines = html.split('\n');
lines.forEach((line, idx) => {
  if (line.includes('instagram') || line.includes('Facebook')) {
    console.log(`Line ${idx + 1}:`, line.substring(0, 300));
  }
});
