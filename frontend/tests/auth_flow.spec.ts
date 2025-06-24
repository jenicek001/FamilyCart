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
});
