const { test, expect } = require('@playwright/test');
const { createAndLoginUser } = require('./helpers');

test.describe('Expenses', () => {
  test.beforeEach(async ({ page }) => {
    // Create and login user before each test
    await createAndLoginUser(page);
  });

  test('should display expenses page', async ({ page }) => {
    await page.goto('/expenses');
    await expect(page).toHaveURL('/expenses');
    await expect(page.locator('text=Expenses')).toBeVisible();
    await expect(page.locator('a[href="/expenses/add"]')).toContainText('Add expense');
  });

  test('should show add expense form', async ({ page }) => {
    await page.goto('/expenses/add');
    await expect(page.locator('input[name="title"]')).toBeVisible();
    await expect(page.locator('input[name="cost"]')).toBeVisible();
    await expect(page.locator('input[name="type"][value="individual"]')).toBeVisible();
    await expect(page.locator('input[name="type"][value="shared"]')).toBeVisible();
  });

  test('should add new expense', async ({ page }) => {
    await page.goto('/expenses/add');
    await page.fill('input[name="title"]', 'Test Expense');
    await page.fill('input[name="cost"]', '50');
    await page.fill('textarea[name="note"]', 'Test note');
    await page.click('input[name="type"][value="individual"]');
    
    await page.click('button');
    await expect(page).toHaveURL('/expenses');
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/expenses/add');
    await page.click('button');
    
    // Should show validation errors or stay on form
    await expect(page).toHaveURL('/expenses/add');
  });
});