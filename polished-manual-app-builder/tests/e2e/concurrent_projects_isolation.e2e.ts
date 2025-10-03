import { test, expect } from '@playwright/test';

test('multiple users can create projects in isolation', async ({ browser }) => {
  const context1 = await browser.newContext();
  const context2 = await browser.newContext();
  const page1 = await context1.newPage();
  const page2 = await context2.newPage();
  await page1.goto('/');
  await page2.goto('/');
  await page1.getByRole('textbox').fill('App 1');
  await page2.getByRole('textbox').fill('App 2');
  await page1.getByRole('button', { name: /send/i }).click();
  await page2.getByRole('button', { name: /send/i }).click();
  await expect(page1.getByText(/build complete/i)).toBeVisible({ timeout: 300000 });
  await expect(page2.getByText(/build complete/i)).toBeVisible({ timeout: 300000 });
  await context1.close();
  await context2.close();
});
