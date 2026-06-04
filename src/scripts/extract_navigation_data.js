import fs from 'fs';

const filePath = '/mnt/c/Users/YAGEW/.gemini/antigravity/brain/828b859c-e60a-48b8-bcb0-61d65ae331b3/.system_generated/steps/2550/content.md';
const html = fs.readFileSync(filePath, 'utf8');

// Find all HTML anchor tags and print their href and inner text
const linkRegex = /<a\b[^>]*href=["']([^"']*)["'][^>]*>([\s\S]*?)<\/a>/gi;
let match;
while ((match = linkRegex.exec(html)) !== null) {
  const href = match[1];
  const text = match[2].replace(/<[^>]*>/g, '').trim();
  if (href.includes('/node/') || text.includes('instagram') || text.includes('Facebook')) {
    console.log(`Href: ${href} | Text: ${text}`);
  }
}
