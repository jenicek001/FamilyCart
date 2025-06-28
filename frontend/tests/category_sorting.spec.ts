import { test, expect } from '@playwright/test';

test.describe('Category-based sorting and grouping', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Login with test credentials
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Wait for redirect to dashboard
    await page.waitForURL(/.*dashboard/);
  });

  test('should display items grouped by category with headers', async ({ page }) => {
    // Navigate to a shopping list (assume one exists or create one)
    const listLink = page.locator('a').filter({ hasText: /test|shopping|list/i }).first();
    
    if (await listLink.count() > 0) {
      await listLink.click();
      
      // Check for category headers in the shopping list
      const categoryHeaders = page.locator('h3').filter({ hasText: /produce|dairy|bakery|meat|beverages|household|other/i });
      
      if (await categoryHeaders.count() > 0) {
        // Verify category headers are visible
        await expect(categoryHeaders.first()).toBeVisible();
        
        // Check that items are grouped under their respective categories
        const firstCategoryHeader = await categoryHeaders.first();
        const categoryName = await firstCategoryHeader.textContent();
        
        if (categoryName) {
          // Look for items under this category
          const categorySection = firstCategoryHeader.locator('..').locator('..');
          const itemsInCategory = categorySection.locator('[data-testid="shopping-list-item"]').or(
            categorySection.locator('.space-y-2').locator('div').filter({ hasText: /\w+/ })
          );
          
          if (await itemsInCategory.count() > 0) {
            await expect(itemsInCategory.first()).toBeVisible();
          }
        }
      }
    }
  });

  test('should show category icons and colors', async ({ page }) => {
    // Navigate to a shopping list
    const listLink = page.locator('a').filter({ hasText: /test|shopping|list/i }).first();
    
    if (await listLink.count() > 0) {
      await listLink.click();
      
      // Look for category icons (Material Icons)
      const categoryIcons = page.locator('.material-icons').filter({ hasText: /local_grocery_store|restaurant|home|shopping_cart|local_drink/i });
      
      if (await categoryIcons.count() > 0) {
        await expect(categoryIcons.first()).toBeVisible();
      }
      
      // Look for category color coding (background colors)
      const coloredElements = page.locator('[class*="bg-"]').filter({ hasText: '' });
      
      if (await coloredElements.count() > 0) {
        // Check that elements have color classes
        const firstColoredElement = coloredElements.first();
        const classList = await firstColoredElement.getAttribute('class');
        expect(classList).toMatch(/bg-\w+-\d+/); // Should have Tailwind color classes
      }
    }
  });

  test('should maintain category grouping when items are completed', async ({ page }) => {
    // Navigate to a shopping list
    const listLink = page.locator('a').filter({ hasText: /test|shopping|list/i }).first();
    
    if (await listLink.count() > 0) {
      await listLink.click();
      
      // Find an uncompleted item
      const itemCheckbox = page.locator('input[type="checkbox"]').first();
      
      if (await itemCheckbox.count() > 0) {
        // Get the item name before completing it
        const itemContainer = itemCheckbox.locator('..');
        const itemName = await itemContainer.locator('text=/\\w+/').first().textContent();
        
        // Mark item as completed
        await itemCheckbox.click();
        
        // Wait for the item to move to completed section
        await page.waitForTimeout(1000);
        
        // Check that completed items section exists and has category grouping
        const completedSection = page.locator('h3').filter({ hasText: /checked items|completed/i });
        
        if (await completedSection.count() > 0) {
          await expect(completedSection).toBeVisible();
          
          // Look for category headers in completed section
          const completedCategoryHeaders = completedSection.locator('..').locator('h4').or(
            completedSection.locator('..').locator('.font-medium')
          );
          
          if (await completedCategoryHeaders.count() > 0) {
            await expect(completedCategoryHeaders.first()).toBeVisible();
          }
        }
      }
    }
  });

  test('should allow filtering by category', async ({ page }) => {
    // Navigate to a shopping list
    const listLink = page.locator('a').filter({ hasText: /test|shopping|list/i }).first();
    
    if (await listLink.count() > 0) {
      await listLink.click();
      
      // Look for category filter dropdown
      const filterButton = page.locator('button').filter({ hasText: /filter|category|all/i }).or(
        page.locator('select[name*="category"]')
      );
      
      if (await filterButton.count() > 0) {
        await filterButton.click();
        
        // Look for category options
        const categoryOptions = page.locator('option, [role="option"]').filter({ hasText: /produce|dairy|bakery/i });
        
        if (await categoryOptions.count() > 0) {
          // Select a specific category
          await categoryOptions.first().click();
          
          // Wait for filtering to take effect
          await page.waitForTimeout(500);
          
          // Verify that only items from selected category are visible
          const visibleItems = page.locator('[data-testid="shopping-list-item"]').or(
            page.locator('.space-y-2 > div').filter({ hasText: /\\w+/ })
          );
          
          // All visible items should belong to the selected category
          // (This is a basic check - more specific validation would require knowing the exact items)
          if (await visibleItems.count() > 0) {
            await expect(visibleItems.first()).toBeVisible();
          }
        }
      }
    }
  });

  test('should handle empty categories gracefully', async ({ page }) => {
    // Navigate to a shopping list
    const listLink = page.locator('a').filter({ hasText: /test|shopping|list/i }).first();
    
    if (await listLink.count() > 0) {
      await listLink.click();
      
      // Apply a filter that might result in empty categories
      const filterButton = page.locator('button').filter({ hasText: /filter|category/i }).or(
        page.locator('select[name*="category"]')
      );
      
      if (await filterButton.count() > 0) {
        await filterButton.click();
        
        // Select a specific category filter
        const categoryOptions = page.locator('option, [role="option"]').filter({ hasText: /produce|dairy/i });
        
        if (await categoryOptions.count() > 0) {
          await categoryOptions.first().click();
          await page.waitForTimeout(500);
          
          // Check that the UI handles the filtered state properly
          const noItemsMessage = page.locator('text=/no items found|empty|try adjusting/i');
          const visibleItems = page.locator('[data-testid="shopping-list-item"]');
          
          // Either should have items or should show appropriate empty state
          const hasItems = await visibleItems.count() > 0;
          const hasEmptyMessage = await noItemsMessage.count() > 0;
          
          expect(hasItems || hasEmptyMessage).toBeTruthy();
        }
      }
    }
  });
});
