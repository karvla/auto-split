const { test, expect } = require('@playwright/test');
const { createAndLoginUser } = require('./helpers');

test.describe('Bookings', () => {
  test.beforeEach(async ({ page }) => {
    // Create and login user before each test
    await createAndLoginUser(page);
  });

  test('should display bookings page', async ({ page }) => {
    await page.goto('/bookings');
    await expect(page).toHaveURL('/bookings');
    await expect(page.locator('text=Bookings')).toBeVisible();
    await expect(page.locator('a[href="/bookings/add"]')).toContainText('New Booking');
  });

  test('should show add booking form', async ({ page }) => {
    await page.goto('/bookings/add');
    await expect(page.locator('input[name="date_from"]')).toBeVisible();
    await expect(page.locator('input[name="date_to"]')).toBeVisible();
    await expect(page.locator('input[name="distance"]')).toBeVisible();
    await expect(page.locator('input[name="note"]')).toBeVisible();
    await expect(page.locator('select[name="user"]')).toBeVisible();
  });

  test('should add new booking', async ({ page }) => {
    await page.goto('/bookings/add');
    
    // Fill all required fields with valid data
    await page.fill('input[name="date_from"]', '2024-01-01');
    await page.fill('input[name="date_to"]', '2024-01-02');
    await page.fill('input[name="distance"]', '100');
    await page.fill('input[name="note"]', 'Test booking note');
    
    await page.click('button');
    await expect(page).toHaveURL('/bookings');
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/bookings/add');
    await page.click('button');
    
    // Should show validation errors or stay on form
    await expect(page).toHaveURL('/bookings/add');
  });
});