const { test, expect } = require('@playwright/test');
const { createAndLoginUser } = require('./helpers');

test.describe('Debts', () => {
  test.beforeEach(async ({ page }) => {
    // Create and login user before each test
    await createAndLoginUser(page);
  });

  test('should display debts page', async ({ page }) => {
    await page.goto('/debts');
    await expect(page).toHaveURL('/debts');
    await expect(page.locator('text=Debts')).toBeVisible();
  });

  test('should show add transaction form', async ({ page }) => {
    await page.goto('/debts');
    // Check for debt settlement form elements
    const formExists = await page.locator('input[name="amount"]').count() > 0;
    
    if (formExists) {
      await expect(page.locator('input[name="amount"]')).toBeVisible();
      await expect(page.locator('select[name="from_user"]')).toBeVisible();
      await expect(page.locator('select[name="to_user"]')).toBeVisible();
      await expect(page.locator('button:text("Settle up!")')).toBeVisible();
    } else {
      // If only one user, should show message
      await expect(page.locator('text=No debts since you are the only one')).toBeVisible();
    }
  });
});