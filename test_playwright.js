import { chromium } from 'playwright';
import path from 'path';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 1024 }
  });
  const page = await context.newPage();

  const outputDir = '/mnt/c/Users/YAGEW/.gemini/antigravity/brain/828b859c-e60a-48b8-bcb0-61d65ae331b3';

  // 1. Test Home Page
  console.log('Visiting Home Page...');
  await page.goto('http://localhost:4321/');
  
  // Wait 4 seconds for preloader fade-out and translation
  console.log('Waiting for preloader and translation to complete...');
  await page.waitForTimeout(4000);
  
  // Capture Home page screenshot
  await page.screenshot({ path: path.join(outputDir, 'home_playwright.png') });
  console.log('Saved home_playwright.png');

  // 2. Test Query Page
  console.log('Visiting Query Page...');
  await page.goto('http://localhost:4321/query');
  await page.waitForTimeout(3000); // Wait for translation
  await page.screenshot({ path: path.join(outputDir, 'query_playwright.png') });
  console.log('Saved query_playwright.png');

  // 3. Test Login Page
  console.log('Visiting Login Page...');
  await page.goto('http://localhost:4321/login');
  await page.waitForTimeout(3000); // Wait for translation
  await page.screenshot({ path: path.join(outputDir, 'login_playwright.png') });
  console.log('Saved login_playwright.png');

  await browser.close();
  console.log('Tests completed successfully!');
}

run().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
