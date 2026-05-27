const { test, expect } = require('@playwright/test');

test('loads homepage and shows title', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toHaveText('Kudos');
});
