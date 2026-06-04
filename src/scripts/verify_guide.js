import { chromium } from 'playwright';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // Log browser console logs
  page.on('console', msg => {
    console.log(`[BROWSER CONSOLE] ${msg.type()}: ${msg.text()}`);
  });
  
  page.on('pageerror', err => {
    console.error(`[BROWSER ERROR]`, err);
  });

  console.log('Navigating to http://localhost:4321/guide ...');
  await page.goto('http://localhost:4321/guide');
  await page.waitForTimeout(2000); // wait for page load / translate.js

  console.log('--- BEFORE CLICK ---');
  let activePaneId = await page.evaluate(() => {
    const active = document.querySelector('.tutorial-pane:not(.hidden)');
    return active ? active.id : 'none';
  });
  console.log('Active pane ID on load:', activePaneId);

  console.log('Clicking the target button for 问题：接码成功-需要邮箱...');
  const targetDocId = '019c078f-a3df-75cf-b641-72edd25f40ba';
  
  // Perform click
  await page.click(`button[data-doc-id="${targetDocId}"]`);
  await page.waitForTimeout(1000); // wait for transition

  console.log('--- AFTER CLICK ---');
  const targetPaneInfo = await page.evaluate((id) => {
    const pane = document.getElementById(`tutorial-pane-${id}`);
    if (!pane) return { found: false };
    return {
      found: true,
      classes: pane.className,
      opacity: window.getComputedStyle(pane).opacity,
      display: window.getComputedStyle(pane).display,
      visibility: window.getComputedStyle(pane).visibility,
      height: pane.offsetHeight,
      htmlSnippet: pane.innerHTML.substring(0, 300)
    };
  }, targetDocId);
  console.log('Target pane info after click:', targetPaneInfo);

  // Check if any pane is currently visible
  const allPaneClasses = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.tutorial-pane')).map(p => ({
      id: p.id,
      classes: p.className,
      display: window.getComputedStyle(p).display
    }));
  });
  console.log('All panes classes and display computed styles:', allPaneClasses);

  await browser.close();
}

run().catch(console.error);
