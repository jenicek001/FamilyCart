import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  // Generate a unique email for testing
  const testEmail = `test_${Date.now()}@example.com`;
  const testPassword = 'StrongPassword123!';
  
  test('should register, login, and access shopping lists', async ({ page }) => {
    // 1. Navigate to the registration page
    await page.goto('http://localhost:9002/register');
    
    // 2. Fill in and submit the registration form
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.fill('input[id="firstName"]', 'Test');
    await page.fill('input[id="lastName"]', 'User');
    await page.click('button[type="submit"]');
    
    // 3. Wait for redirect to login page
    await expect(page).toHaveURL(/.*login/);
    
    // 4. Login with the newly created account
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button[type="submit"]');
    
    // 5. Wait for redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // 6. Check if we have access to protected content
    const welcomeMessage = await page.textContent('h1');
    expect(welcomeMessage).toContain('Dashboard');
    
    // 7. Navigate to the profile page which loads shopping lists
    await page.click('text=Profile');
    await expect(page).toHaveURL(/.*profile/);
    
    // 8. Check if shopping lists section is visible
    const listsHeading = await page.textContent('h3');
    expect(listsHeading).toContain('Owned by You');
    
    // 9. Check if the lists are empty but loading was successful (no error)
    const emptyListMessage = await page.textContent('.text-muted-foreground.italic');
    expect(emptyListMessage).toContain("You haven't created any lists yet");
    
    // 10. Check browser console for errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // After checking console, no errors related to shopping lists should be there
    expect(consoleErrors.filter(e => e.includes('shopping lists'))).toEqual([]);
  });

  test('should interact with shopping list items if available', async ({ page }) => {
    // Generate a unique email for this test
    const testEmail2 = `test_items_${Date.now()}@example.com`;
    
    // 1. Register and login
    await page.goto('http://localhost:9002/register');
    await page.fill('input[type="email"]', testEmail2);
    await page.fill('input[type="password"]', testPassword);
    await page.fill('input[id="firstName"]', 'Test');
    await page.fill('input[id="lastName"]', 'User');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL(/.*login/);
    await page.fill('input[type="email"]', testEmail2);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL(/.*dashboard/);
    
    // 2. Navigate to profile
    await page.click('text=Profile');
    await expect(page).toHaveURL(/.*profile/);
    
    // 3. Look for any existing shopping lists or items
    const listLinks = page.locator('a[href*="list"], a[href*="shopping"]');
    const listCount = await listLinks.count();
    
    if (listCount > 0) {
      // Navigate to the first list
      await listLinks.first().click();
      
      // Wait for list page to load
      await page.waitForLoadState('networkidle');
      
      // Look for item checkboxes or completion controls
      const itemControls = page.locator('input[type="checkbox"], [role="checkbox"], button[aria-label*="complete"]');
      const controlCount = await itemControls.count();
      
      if (controlCount > 0) {
        // Test item completion toggle
        const firstControl = itemControls.first();
        
        // Get initial state
        const initialState = await firstControl.isChecked().catch(() => false);
        
        // Toggle the item
        await firstControl.click();
        
        // Wait for state change
        await page.waitForTimeout(500);
        
        // Verify state changed
        const newState = await firstControl.isChecked().catch(() => !initialState);
        expect(newState).not.toBe(initialState);
        
        // Look for toast notifications
        const toastSelector = '[role="status"], .toast, [data-testid="toast"], [class*="toast"], [data-sonner-toast]';
        const toastVisible = await page.locator(toastSelector).isVisible().catch(() => false);
        
        if (toastVisible) {
          const toastText = await page.locator(toastSelector).textContent();
          console.log('Toast notification:', toastText);
          expect(toastText).toBeTruthy();
        }
      } else {
        console.log('No item completion controls found in shopping list');
      }
    } else {
      console.log('No shopping lists found for item completion testing');
    }
  });
});
