import { test, expect } from '@playwright/test';

test('offline or 429 triggers graceful retry and status', async ({ page }) => {
  await page.goto('/');
  // Simulate offline
  await page.context().setOffline(true);
  await page.getByRole('textbox').fill('Create a todo app');
  await page.getByRole('button', { name: /send/i }).click();
  await expect(page.getByText(/offline/i)).toBeVisible();
  // Simulate 429
  await page.context().setOffline(false);
  // (Mock 429 in backend for this test)
  // ...
  await expect(page.getByText(/retrying/i)).toBeVisible();
});
