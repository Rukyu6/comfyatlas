import fs from 'fs';
import { execSync } from 'child_process';

const html = execSync('curl -s http://localhost:4321/guide').toString();
const targetId = 'tutorial-pane-019c078f-a3df-75cf-b641-72edd25f40ba';
const startIndex = html.indexOf(`id="${targetId}"`);

if (startIndex === -1) {
  console.log('ID not found in HTML!');
} else {
  const endArticleStr = '</article>';
  const endIndex = html.indexOf(endArticleStr, startIndex);
  console.log('HTML Content:');
  console.log(html.substring(startIndex - 50, endIndex + endArticleStr.length));
}
