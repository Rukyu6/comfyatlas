import { chromium } from 'playwright';
import path from 'path';

async function run() {
  console.log('Launching browser...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 1024 }
  });
  const page = await context.newPage();
  
  const outputDir = '/mnt/c/Users/YAGEW/.gemini/antigravity/brain/828b859c-e60a-48b8-bcb0-61d65ae331b3';

  console.log('Navigating to comfyatlas login page...');
  await page.goto('https://www.comfyatlas.com/login');
  await page.waitForTimeout(4000); // Wait for page to load and translate.js to execute

  // Take screenshot before click
  await page.screenshot({ path: path.join(outputDir, 'login_pre_click.png') });
  console.log('Saved login_pre_click.png');

  console.log('Clicking Google auth button...');
  const googleBtn = page.locator('#google-btn');
  
  // Set up listener for the popup
  const popupPromise = context.waitForEvent('page', { timeout: 10000 }).catch(e => null);
  
  await googleBtn.click();
  
  // Wait a bit to check for immediate errors or popup opening
  await page.waitForTimeout(4000);
  
  const popup = await popupPromise;
  if (popup) {
    console.log('Google Auth popup opened successfully!');
    const url = popup.url();
    console.log('Popup URL:', url);
    try {
      await popup.screenshot({ path: path.join(outputDir, 'google_popup.png') });
      console.log('Saved google_popup.png');
    } catch (e) {
      console.log('Could not screenshot popup:', e.message);
    }
  } else {
    console.log('No popup opened.');
  }

  // Check if error banner is visible and check its text
  const errorBanner = page.locator('#auth-error-banner');
  const isVisible = await errorBanner.isVisible();
  if (isVisible) {
    const errorText = await errorBanner.textContent();
    console.log('Error Banner shown with text:', errorText.trim());
  } else {
    console.log('No error banner shown.');
  }

  // Take final screenshot
  await page.screenshot({ path: path.join(outputDir, 'login_post_click.png') });
  console.log('Saved login_post_click.png');

  await browser.close();
}

run().catch(err => {
  console.error('Run error:', err);
  process.exit(1);
});
