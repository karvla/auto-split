const { expect } = require('@playwright/test');

async function createAndLoginUser(page) {
  const uniqueUser = `testuser_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  const password = 'testpassword123';
  
  // Create account
  await page.goto('/signup');
  await page.fill('input[name="name"]', uniqueUser);
  await page.fill('input[name="password"]', password);
  await page.click('button');
  
  // Should redirect to / and show "you are not in any car-group" message
  await expect(page).toHaveURL('/');
  await expect(page.locator('text=you are not in any car-group')).toBeVisible();
  
  // Create new car group to enable access to other features
  await page.click('a[href="/config/new"]');
  await expect(page).toHaveURL('/config/new');
  
  // Fill in car configuration
  await page.fill('input[name="name"]', `Test Car ${uniqueUser}`);
  await page.fill('input[name="currency"]', 'USD');
  await page.fill('input[name="distance_unit"]', 'km');  
  await page.fill('input[name="volume_unit"]', 'liters');
  await page.fill('input[name="fuel_efficiency"]', '0.08');
  await page.fill('input[name="cost_per_distance"]', '0.6');
  await page.click('button');
  
  // Should redirect to config/edit after successful creation
  await page.waitForURL('/config/edit');
  
  return { username: uniqueUser, password };
}

module.exports = { createAndLoginUser };