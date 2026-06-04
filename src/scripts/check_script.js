import fs from 'fs';
import { execSync } from 'child_process';

const html = execSync('curl -s http://localhost:4321/guide').toString();
const scriptRegex = /<script\b[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let count = 1;

while ((match = scriptRegex.exec(html)) !== null) {
  console.log(`--- Script Block ${count++} ---`);
  console.log(match[0].substring(0, 1000));
}
