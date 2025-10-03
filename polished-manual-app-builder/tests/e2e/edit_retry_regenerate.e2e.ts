import { test, expect } from '@playwright/test';

test('user can edit, retry, and regenerate app', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('textbox').fill('Create a blog app');
  await page.getByRole('button', { name: /send/i }).click();
  await expect(page.getByText(/scaffolding/i)).toBeVisible();
  await page.getByRole('button', { name: /edit/i }).click();
  await page.getByRole('textbox').fill('Add comments feature');
  await page.getByRole('button', { name: /retry/i }).click();
  await expect(page.getByText(/regenerating/i)).toBeVisible();
  await expect(page.getByText(/build complete/i)).toBeVisible({ timeout: 300000 });
});
