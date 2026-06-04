import fs from 'fs';
import path from 'path';

const cacheDir = '/mnt/c/Users/YAGEW/.gemini/antigravity/brain/828b859c-e60a-48b8-bcb0-61d65ae331b3/scratch/nodes_cache';

function parseHtmlFile(file) {
  const content = fs.readFileSync(path.join(cacheDir, file), 'utf8');
  // Simple regex to extract titles and potential parent info
  const titleMatch = content.match(/<title>([\s\S]*?)<\/title>/i);
  const title = titleMatch ? titleMatch[1].trim() : 'No Title';
  console.log(`File: ${file} | Title: ${title} | Length: ${content.length}`);
}

const targetFiles = [
  '019c0807-6dc8-73a5-be91-4c4cbbf92a6c.html',
  '019c080c-e24d-7528-adf3-9f8c89156906.html'
];

targetFiles.forEach(parseHtmlFile);
