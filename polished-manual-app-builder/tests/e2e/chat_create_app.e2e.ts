import { test, expect } from '@playwright/test';

test('user can create a CRUD app via chat', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('textbox').fill('Create a CRUD app with React and FastAPI');
  await page.getByRole('button', { name: /send/i }).click();
  await expect(page.getByText(/scaffolding/i)).toBeVisible();
  await expect(page.getByText(/build complete/i)).toBeVisible({ timeout: 300000 });
  await expect(page.getByRole('link', { name: /download/i })).toBeVisible();
});
