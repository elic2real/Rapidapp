import { test, expect } from '@playwright/test';
import { runAxe } from '../utils/axe_runner';

test('chat and status views have no serious a11y violations', async ({ page }) => {
  await page.goto('/');
  const results = await runAxe(page, { runOnly: ['serious', 'critical'] });
  expect(results.violations.length).toBe(0);
});
