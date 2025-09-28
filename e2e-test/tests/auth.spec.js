const { test, expect } = require('@playwright/test');

test.describe('Authentication', () => {
  let uniqueUser;
  
  test.beforeEach(() => {
    uniqueUser = `testuser_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  });
  test('should redirect to login when not authenticated', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/login');
  });

  test('should show login form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('input[name="name"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button')).toBeVisible();
  });

  test('should create account and login successfully', async ({ page }) => {
    // First create an account
    await page.goto('/signup');
    await page.fill('input[name="name"]', uniqueUser);
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button');
    
    // Should redirect to / and show "you are not in any car-group" message
    await expect(page).toHaveURL('/');
    await expect(page.locator('text=you are not in any car-group')).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="name"]', 'invalid');
    await page.fill('input[name="password"]', 'invalid');
    await page.click('button');
    
    // Should stay on login page or show error
    await expect(page).toHaveURL('/login');
  });
});