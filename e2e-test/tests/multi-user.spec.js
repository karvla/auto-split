const { test, expect } = require('@playwright/test');

test.describe('Multi-user workflow', () => {
  test('should allow two users to share expenses in same car group', async ({ browser }) => {
    // Create two separate browser contexts for two users
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    let carSecret;

    try {
      // STEP 1: Create first user and car group
      const user1 = `user1_${Date.now()}_${Math.random().toString(36).substring(7)}`;
      await page1.goto('/signup');
      await page1.fill('input[name="name"]', user1);
      await page1.fill('input[name="password"]', 'testpassword123');
      await page1.click('button');

      // Should redirect to / with "not in any car-group" message
      await expect(page1).toHaveURL('/');
      await expect(page1.locator('text=you are not in any car-group')).toBeVisible();

      // Create new car group
      await page1.click('a[href="/config/new"]');
      await expect(page1).toHaveURL('/config/new');

      // Extract car secret before filling the form
      carSecret = await page1.locator('input[name="car_secret"]').inputValue();
      expect(carSecret).toBeTruthy();

      await page1.fill('input[name="name"]', `Test Car ${user1}`);
      await page1.fill('input[name="currency"]', 'USD');
      await page1.fill('input[name="distance_unit"]', 'km');
      await page1.fill('input[name="volume_unit"]', 'liters');
      await page1.fill('input[name="fuel_efficiency"]', '0.08');
      await page1.fill('input[name="cost_per_distance"]', '0.6');
      await page1.click('button');

      // Should redirect to config/edit
      await expect(page1).toHaveURL('/config/edit');

      // STEP 2: Create second user and join the group
      const user2 = `user2_${Date.now()}_${Math.random().toString(36).substring(7)}`;
      await page2.goto('/signup');
      await page2.fill('input[name="name"]', user2);
      await page2.fill('input[name="password"]', 'testpassword123');
      await page2.click('button');

      // Should redirect to / with "not in any car-group" message
      await expect(page2).toHaveURL('/');
      await expect(page2.locator('text=you are not in any car-group')).toBeVisible();

      // Join existing car group using the secret
      await page2.fill('input[name="car_secret"]', carSecret);
      await page2.click('button:text("Join")');

      // Should now be part of the group
      await page2.waitForURL('/');

      // STEP 3: Have both users add expenses
      // User 1 adds an expense
      await page1.goto('/expenses/add');
      await page1.fill('input[name="title"]', 'User 1 Expense - Gas');
      await page1.fill('input[name="cost"]', '50');
      await page1.fill('textarea[name="note"]', 'Gas station fill-up');
      await page1.fill('input[name="date"]', '2024-01-01');
      await page1.click('input[name="type"][value="shared"]');
      await page1.click('button');
      await expect(page1).toHaveURL('/expenses');

      // User 2 adds an expense
      await page2.goto('/expenses/add');
      await page2.fill('input[name="title"]', 'User 2 Expense - Groceries');
      await page2.fill('input[name="cost"]', '75');
      await page2.fill('textarea[name="note"]', 'Shared groceries for trip');
      await page2.fill('input[name="date"]', '2024-01-02');
      await page2.click('input[name="type"][value="shared"]');
      await page2.click('button');
      await expect(page2).toHaveURL('/expenses');

      // STEP 4: Verify both users can see both expenses
      // User 1 should see both expenses
      await page1.goto('/expenses');
      await expect(page1.locator('text=User 1 Expense - Gas')).toBeVisible();
      await expect(page1.locator('text=User 2 Expense - Groceries')).toBeVisible();
      await expect(page1.locator('text=50 USD')).toBeVisible();
      await expect(page1.locator('text=75 USD')).toBeVisible();

      // User 2 should see both expenses
      await page2.goto('/expenses');
      await expect(page2.locator('text=User 1 Expense - Gas')).toBeVisible();
      await expect(page2.locator('text=User 2 Expense - Groceries')).toBeVisible();
      await expect(page2.locator('text=50 USD')).toBeVisible();
      await expect(page2.locator('text=75 USD')).toBeVisible();

      // Bonus: Check debts page shows the relationship
      await page1.goto('/debts');
      await expect(page1).toHaveURL('/debts');
      await expect(page1.locator('text=Debts')).toBeVisible();

      await page2.goto('/debts');
      await expect(page2).toHaveURL('/debts');
      await expect(page2.locator('text=Debts')).toBeVisible();

    } finally {
      // Clean up
      await context1.close();
      await context2.close();
    }
  });
});