const { test, expect } = require('@playwright/test');
const { createAndLoginUser } = require('./helpers');

test.describe('Configuration', () => {
  test.beforeEach(async ({ page }) => {
    // Create and login user before each test
    await createAndLoginUser(page);
  });

  test('should display config edit page', async ({ page }) => {
    await page.goto('/config/edit');
    await expect(page).toHaveURL('/config/edit');
  });

  test('should display new config page', async ({ page }) => {
    await page.goto('/config/new');
    await expect(page).toHaveURL('/config/new');
    await expect(page.locator('input[name="name"]')).toBeVisible();
    await expect(page.locator('input[name="fuel_efficiency"]')).toBeVisible();
    await expect(page.locator('input[name="cost_per_distance"]')).toBeVisible();
  });

  test('should create new car configuration', async ({ page }) => {
    await page.goto('/config/new');
    await page.fill('input[name="name"]', 'Test Car');
    await page.fill('input[name="currency"]', 'USD');
    await page.fill('input[name="distance_unit"]', 'km');
    await page.fill('input[name="volume_unit"]', 'liters');
    await page.fill('input[name="fuel_efficiency"]', '0.08');
    await page.fill('input[name="cost_per_distance"]', '0.6');
    
    await page.click('button');
    // Should redirect after successful creation
    await expect(page).not.toHaveURL('/config/new');
  });
});