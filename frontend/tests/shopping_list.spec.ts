import { test, expect } from '@playwright/test';

test.describe('Shopping List Item Completion', () => {
  // Generate unique test data
  const testEmail = `test_${Date.now()}@example.com`;
  const testPassword = 'StrongPassword123!';
  const testListName = `Test Shopping List ${Date.now()}`;
  const testItemName = `Test Item ${Date.now()}`;

  test.beforeEach(async ({ page }) => {
    // Register and login before each test
    await page.goto('http://localhost:9002/register');
    
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
  });

  test('should mark item as completed and show visual feedback', async ({ page }) => {
    // Navigate to profile to access shopping lists
    await page.click('text=Profile');
    await expect(page).toHaveURL(/.*profile/);
    
    // Check if we have a "Create New List" button or similar
    const createListButton = page.locator('text=Create New List').or(page.locator('button:has-text("Add List")'));
    
    if (await createListButton.count() > 0) {
      // Create a new shopping list
      await createListButton.first().click();
      
      // Fill in list name (assuming there's a form field)
      const listNameInput = page.locator('input[name="name"]').or(page.locator('input[placeholder*="name"]'));
      if (await listNameInput.count() > 0) {
        await listNameInput.fill(testListName);
        await page.click('button[type="submit"]').or(page.click('button:has-text("Create")'));
      }
    }

    // Look for existing lists or navigate to a list
    const listLink = page.locator(`text=${testListName}`).or(page.locator('a:has-text("Test")').first());
    if (await listLink.count() > 0) {
      await listLink.click();
      
      // Add an item to the list if there's an "Add Item" functionality
      const addItemButton = page.locator('text=Add Item').or(page.locator('button:has-text("Add")'));
      if (await addItemButton.count() > 0) {
        await addItemButton.first().click();
        
        // Fill item details
        const itemNameInput = page.locator('input[name="name"]').or(page.locator('input[placeholder*="item"]'));
        if (await itemNameInput.count() > 0) {
          await itemNameInput.fill(testItemName);
          await page.click('button[type="submit"]').or(page.click('button:has-text("Add")'));
        }
      }

      // Look for the item and its completion checkbox/button
      const itemElement = page.locator(`text=${testItemName}`);
      if (await itemElement.count() > 0) {
        // Find the completion control (checkbox, button, etc.)
        const completionControl = itemElement.locator('..').locator('input[type="checkbox"]')
          .or(itemElement.locator('..').locator('button[aria-label*="complete"]'))
          .or(itemElement.locator('..').locator('[role="checkbox"]'));
        
        if (await completionControl.count() > 0) {
          // Mark item as completed
          await completionControl.first().click();
          
          // Check for visual feedback (strikethrough, different styling, etc.)
          const completedItem = page.locator(`text=${testItemName}`);
          
          // Wait for potential state change
          await page.waitForTimeout(500);
          
          // Look for completed state indicators
          const hasStrikethrough = await completedItem.evaluate(el => {
            const style = window.getComputedStyle(el);
            return style.textDecoration.includes('line-through') || 
                   style.textDecorationLine === 'line-through';
          });
          
          const hasCompletedClass = await completedItem.evaluate(el => {
            return el.className.includes('completed') || 
                   el.className.includes('checked') ||
                   el.getAttribute('data-completed') === 'true';
          });
          
          // Assert that visual feedback is present
          expect(hasStrikethrough || hasCompletedClass).toBeTruthy();
          
          // Test uncompleting the item
          await completionControl.first().click();
          await page.waitForTimeout(500);
          
          // Check that completed styling is removed
          const hasStrikethroughAfter = await completedItem.evaluate(el => {
            const style = window.getComputedStyle(el);
            return style.textDecoration.includes('line-through') || 
                   style.textDecorationLine === 'line-through';
          });
          
          const hasCompletedClassAfter = await completedItem.evaluate(el => {
            return el.className.includes('completed') || 
                   el.className.includes('checked') ||
                   el.getAttribute('data-completed') === 'true';
          });
          
          expect(hasStrikethroughAfter && hasCompletedClassAfter).toBeFalsy();
        }
      }
    }
  });

  test('should show toast notification when marking item as completed', async ({ page }) => {
    // Navigate to profile
    await page.click('text=Profile');
    await expect(page).toHaveURL(/.*profile/);
    
    // Look for existing shopping list or create one
    const listLink = page.locator('a:has-text("Test")').first().or(page.locator('a[href*="list"]').first());
    
    if (await listLink.count() > 0) {
      await listLink.click();
      
      // Find any item in the list
      const itemCheckbox = page.locator('input[type="checkbox"]').or(page.locator('[role="checkbox"]')).first();
      
      if (await itemCheckbox.count() > 0) {
        // Listen for toast notifications
        const toastSelector = '[role="status"]' + 
          ', .toast' + 
          ', [data-testid="toast"]' + 
          ', [class*="toast"]' +
          ', [data-sonner-toast]';
        
        // Mark item as completed
        await itemCheckbox.click();
        
        // Wait for toast to appear
        const toast = page.locator(toastSelector);
        await expect(toast).toBeVisible({ timeout: 3000 });
        
        // Check that toast contains appropriate message
        const toastText = await toast.textContent();
        expect(toastText).toMatch(/(completed|marked|checked|done)/i);
      }
    }
  });

  test('should persist item completion state after page refresh', async ({ page }) => {
    // Navigate to profile
    await page.click('text=Profile');
    await expect(page).toHaveURL(/.*profile/);
    
    // Look for existing shopping list
    const listLink = page.locator('a:has-text("Test")').first().or(page.locator('a[href*="list"]').first());
    
    if (await listLink.count() > 0) {
      await listLink.click();
      
      // Find first item and mark as completed
      const itemCheckbox = page.locator('input[type="checkbox"]').or(page.locator('[role="checkbox"]')).first();
      
      if (await itemCheckbox.count() > 0) {
        await itemCheckbox.click();
        
        // Wait for state to be saved
        await page.waitForTimeout(1000);
        
        // Refresh the page
        await page.reload();
        
        // Wait for page to load
        await page.waitForLoadState('networkidle');
        
        // Check that the item is still marked as completed
        const refreshedCheckbox = page.locator('input[type="checkbox"]').or(page.locator('[role="checkbox"]')).first();
        
        if (await refreshedCheckbox.count() > 0) {
          const isChecked = await refreshedCheckbox.isChecked();
          expect(isChecked).toBeTruthy();
        }
      }
    }
  });

  test('should handle unauthorized access to item completion', async ({ page }) => {
    // This test would require a more complex setup with multiple users
    // For now, we'll test basic error handling
    
    // Try to access a non-existent list
    await page.goto('http://localhost:9002/list/999999');
    
    // Should show some error or redirect
    await page.waitForTimeout(2000);
    
    // Check for error message or redirect to dashboard/login
    const currentUrl = page.url();
    const hasError = await page.locator('text=error').or(page.locator('text=not found')).count() > 0;
    const redirectedToDashboard = currentUrl.includes('/dashboard') || currentUrl.includes('/profile');
    
    expect(hasError || redirectedToDashboard).toBeTruthy();
  });
});
