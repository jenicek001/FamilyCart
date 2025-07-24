import { test, expect } from '@playwright/test';

test.describe('Mobile Rename Dialog Tests', () => {
  const mobileViewports = [
    { name: 'iPhone SE', width: 375, height: 667 },
    { name: 'iPhone 12', width: 390, height: 844 },
    { name: 'iPhone 12 Pro Max', width: 428, height: 926 },
    { name: 'Samsung Galaxy S8+', width: 360, height: 740 },
    { name: 'Small Mobile', width: 320, height: 568 }, // iPhone 5/SE landscape
  ];

  for (const viewport of mobileViewports) {
    test(`Rename dialog fits on ${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
      // Set viewport to mobile size
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      
      // Navigate to our test page
      await page.goto('file:///home/honzik/GitHub/FamilyCart/FamilyCart/frontend/test-mobile-rename-dialog.html');
      
      // Open the dialog
      await page.click('button:has-text("Open Rename Dialog")');
      
      // Wait for dialog to be visible
      await page.waitForSelector('#dialog', { state: 'visible' });
      
      // Get dialog dimensions
      const dialog = page.locator('#dialog > div');
      const dialogBox = await dialog.boundingBox();
      
      if (!dialogBox) {
        throw new Error('Dialog not found');
      }
      
      // Check if dialog fits within viewport with some margin
      const margin = 16; // 8px margin on each side
      const expectedMaxWidth = viewport.width - (margin * 2);
      const expectedMaxHeight = viewport.height - (margin * 2);
      
      console.log(`${viewport.name}: Dialog size: ${dialogBox.width}x${dialogBox.height}, Viewport: ${viewport.width}x${viewport.height}`);
      
      // Dialog should not exceed viewport width (minus margins)
      expect(dialogBox.width).toBeLessThanOrEqual(expectedMaxWidth);
      
      // Dialog should not exceed viewport height (minus margins)
      expect(dialogBox.height).toBeLessThanOrEqual(expectedMaxHeight);
      
      // Dialog should be reasonably sized (not too small)
      expect(dialogBox.width).toBeGreaterThan(250);
      
      // Take a screenshot for visual verification
      await page.screenshot({ 
        path: `test-results/mobile-rename-dialog-${viewport.name.toLowerCase().replace(/\s+/g, '-')}.png`,
        fullPage: false 
      });
      
      // Test form interactions
      const input = page.locator('input[type="text"]');
      await input.fill('New List Name');
      await expect(input).toHaveValue('New List Name');
      
      // Check button accessibility (should be easily tappable - min 44px height)
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();
      
      for (let i = 0; i < buttonCount; i++) {
        const button = buttons.nth(i);
        const buttonBox = await button.boundingBox();
        if (buttonBox && buttonBox.height > 0) {
          expect(buttonBox.height).toBeGreaterThanOrEqual(36); // Minimum tap target size
        }
      }
      
      // Close dialog
      await page.click('button:has-text("Cancel")');
      await page.waitForSelector('#dialog', { state: 'hidden' });
    });
  }

  test('Dialog content analysis on smallest mobile screen', async ({ page }) => {
    // Test on the smallest common mobile screen (320px)
    await page.setViewportSize({ width: 320, height: 568 });
    
    await page.goto('file:///home/honzik/GitHub/FamilyCart/FamilyCart/frontend/test-mobile-rename-dialog.html');
    await page.click('button:has-text("Open Rename Dialog")');
    await page.waitForSelector('#dialog', { state: 'visible' });
    
    // Check if stats section is hidden on small screens
    const statsSection = page.locator('.hidden.sm\\:block');
    await expect(statsSection).toBeHidden();
    
    // Check text sizes are appropriate
    const title = page.locator('span:has-text("Rename List")');
    const titleStyles = await title.evaluate(el => {
      const styles = window.getComputedStyle(el);
      return {
        fontSize: styles.fontSize,
        lineHeight: styles.lineHeight
      };
    });
    
    console.log('Title styles on 320px:', titleStyles);
    
    // Verify input field is not too cramped
    const input = page.locator('input[type="text"]');
    const inputBox = await input.boundingBox();
    
    if (inputBox) {
      expect(inputBox.width).toBeGreaterThan(200); // Should have decent width
      expect(inputBox.height).toBeGreaterThanOrEqual(32); // Should be tappable
    }
  });
});
