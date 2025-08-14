import { test, expect } from '@playwright/test';

test('should mark item as completed on mobile', async ({ page }) => {
  // Use a mobile viewport defined in the project config
  await page.setViewportSize({ width: 390, height: 844 }); // iPhone 13

  const testEmail = `test_mobile_${Date.now()}@example.com`;
  const testPassword = 'StrongPassword123!';
  const testListName = `Mobile Test List ${Date.now()}`;
  const testItemName = `Mobile Test Item ${Date.now()}`;

  // Register and login before each test
  await page.goto('/register');
  
  // Register
  await page.fill('input[type="email"]', testEmail);
  await page.fill('input[type="password"]', testPassword);
  await page.fill('input[id="firstName"]', 'Test');
  await page.fill('input[id="lastName"]', 'User');
  await page.click('button[type="submit"]');
  
  // Login
  await expect(page).toHaveURL(/.*login/);
  await page.fill('input[type="email"]', testEmail);
  await page.fill('input[type="password"]', testPassword);
  await page.click('button[type="submit"]');
  
  // Wait for dashboard
  await expect(page).toHaveURL(/.*dashboard/);

  // On mobile, the profile/lists might be behind a menu button
  const menuButton = page.locator('button[aria-label="Open menu"]');
  if (await menuButton.isVisible()) {
    await menuButton.click();
  }
  
  // Navigate to profile to access shopping lists
  await page.click('text=Profile');
  await expect(page).toHaveURL(/.*profile/);
  
  // Create a new shopping list
  await page.click('text=Create New List');
  await page.fill('input[name="name"]', testListName);
  await page.click('button[type="submit"]');
  
  // Wait for navigation to the new list page
  await page.waitForURL(new RegExp(`.*${encodeURIComponent(testListName)}`));

  // Add an item to the list
  await page.fill('input[placeholder="Add an item"]', testItemName);
  await page.click('button[aria-label="Add item"]');
  
  // Wait for item to appear
  await expect(page.locator(`text=${testItemName}`)).toBeVisible();

  // Find the checkbox associated with the item
  const itemElement = page.locator(`div:has-text("${testItemName}")`).first();
  const checkbox = itemElement.locator('input[type="checkbox"]');
  
  // Ensure checkbox is visible before clicking
  await expect(checkbox).toBeVisible();

  // Click the checkbox
  await checkbox.check();

  // Verify the item is marked as completed
  // Check for a strikethrough style on the item's text
  const itemText = page.locator(`span:has-text("${testItemName}")`);
  await expect(itemText).toHaveCSS('text-decoration-line', 'line-through', { timeout: 5000 });
});
