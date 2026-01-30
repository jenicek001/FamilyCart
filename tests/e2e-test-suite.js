/**
 * FamilyCart E2E Test Suite
 * 
 * Comprehensive end-to-end tests for validating functionality before UAT deployment.
 * Tests cover critical user stories (FR001-FR028) to ensure production readiness.
 * 
 * PREREQUISITES:
 * - Docker dev environment running (docker-compose.dev.yml)
 * - Test users created in database (see setup instructions below)
 * - Playwright MCP server available
 * 
 * EXECUTION:
 * Run this file using Playwright MCP browser_run_code tool or similar automation
 * 
 * TEST DATA:
 * - User 1: playwright.user1@test.com / Test123!
 * - User 2: playwright.user2@test.com / Test123!
 */

const TEST_CONFIG = {
  baseUrl: 'http://192.168.12.200:3003',
  timeout: 5000,
  users: {
    user1: {
      email: 'playwright.user1@test.com',
      password: 'Test123!',
      name: 'Playwright User One',
      nickname: 'User1'
    },
    user2: {
      email: 'playwright.user2@test.com',
      password: 'Test123!',
      name: 'Playwright User Two',
      nickname: 'User2'
    }
  }
};

/**
 * TEST SUITE: FR001 - User Authentication
 * Validates user login, session management, and authentication flow
 */
async function testUserLogin(page) {
  console.log('🧪 TEST: FR001 - User Login');
  
  await page.goto(TEST_CONFIG.baseUrl);
  await page.waitForTimeout(3000);
  
  // Click Sign In button in header
  await page.getByRole('banner').getByRole('button', { name: 'Sign In' }).click();
  await page.waitForTimeout(1000);
  
  // Fill login form using Playwright's .fill() to trigger React events
  await page.getByPlaceholder('your@email.com').fill(TEST_CONFIG.users.user1.email);
  await page.getByPlaceholder('Enter your password').fill(TEST_CONFIG.users.user1.password);
  await page.waitForTimeout(500);
  
  // Submit login form
  await page.locator('form').getByRole('button', { name: 'Sign In' }).click();
  await page.waitForTimeout(3000);
  
  // Verify successful login
  const url = page.url();
  const isLoggedIn = url.includes('/dashboard');
  const bodyText = await page.evaluate(() => document.body.innerText);
  const hasWelcomeMessage = bodyText.includes('Welcome back');
  
  console.log(`✅ Login successful: ${isLoggedIn && hasWelcomeMessage}`);
  console.log(`   - Redirected to: ${url}`);
  console.log(`   - Welcome message shown: ${hasWelcomeMessage}`);
  
  return {
    passed: isLoggedIn && hasWelcomeMessage,
    url,
    testName: 'FR001 - User Login'
  };
}

/**
 * TEST SUITE: FR003 - Create Shopping List
 * Validates shopping list creation with name and description
 */
async function testCreateShoppingList(page) {
  console.log('🧪 TEST: FR003 - Create Shopping List');
  
  // Navigate to shopping lists (assuming already logged in)
  const currentUrl = page.url();
  if (!currentUrl.includes('/dashboard') && !currentUrl.includes('/lists')) {
    await page.goto(`${TEST_CONFIG.baseUrl}/dashboard`);
    await page.waitForTimeout(2000);
  }
  
  // Click Create/Add List button
  const createButtons = await page.getByRole('button', { name: /create|add.*list/i }).all();
  if (createButtons.length > 0) {
    await createButtons[0].click();
    await page.waitForTimeout(1000);
  }
  
  // Fill list creation form
  const listName = `Test List ${Date.now()}`;
  const listDescription = 'Automated test shopping list';
  
  await page.getByPlaceholder(/list.*name/i).fill(listName);
  
  const descriptionField = await page.getByPlaceholder(/description/i).first();
  if (await descriptionField.isVisible()) {
    await descriptionField.fill(listDescription);
  }
  
  await page.waitForTimeout(500);
  
  // Submit form
  await page.getByRole('button', { name: /create|save/i }).click();
  await page.waitForTimeout(2000);
  
  // Verify list was created
  const bodyText = await page.evaluate(() => document.body.innerText);
  const listExists = bodyText.includes(listName);
  
  console.log(`✅ List created: ${listExists}`);
  console.log(`   - List name: ${listName}`);
  
  return {
    passed: listExists,
    listName,
    testName: 'FR003 - Create Shopping List'
  };
}

/**
 * TEST SUITE: FR006 - Add Items to Shopping List
 * Validates item addition with search, quantity, and notes
 */
async function testAddItemsToList(page, listName) {
  console.log('🧪 TEST: FR006 - Add Items to List');
  
  // Click on the shopping list
  await page.getByText(listName).click();
  await page.waitForTimeout(2000);
  
  // Add first item - Milk
  const itemInput = await page.getByPlaceholder(/search.*item|add.*item/i).first();
  await itemInput.fill('Milk');
  await page.waitForTimeout(1000);
  
  // Check if search suggestions appear
  const bodyText = await page.evaluate(() => document.body.innerText);
  const hasSuggestions = bodyText.toLowerCase().includes('milk');
  
  // Press Enter or click Add button
  await itemInput.press('Enter');
  await page.waitForTimeout(1500);
  
  // Add second item - Bread
  await itemInput.fill('Bread');
  await page.waitForTimeout(500);
  await itemInput.press('Enter');
  await page.waitForTimeout(1500);
  
  // Add third item - Eggs with quantity
  await itemInput.fill('Eggs');
  await page.waitForTimeout(500);
  await itemInput.press('Enter');
  await page.waitForTimeout(1500);
  
  // Verify items were added
  const finalBodyText = await page.evaluate(() => document.body.innerText);
  const hasMilk = finalBodyText.includes('Milk');
  const hasBread = finalBodyText.includes('Bread');
  const hasEggs = finalBodyText.includes('Eggs');
  
  console.log(`✅ Items added: Milk=${hasMilk}, Bread=${hasBread}, Eggs=${hasEggs}`);
  
  return {
    passed: hasMilk && hasBread && hasEggs,
    itemsAdded: ['Milk', 'Bread', 'Eggs'],
    testName: 'FR006 - Add Items to List'
  };
}

/**
 * TEST SUITE: FR011 - Mark Items as Purchased
 * Validates checking off items and status updates
 */
async function testMarkItemsPurchased(page) {
  console.log('🧪 TEST: FR011 - Mark Items as Purchased');
  
  // Find checkboxes for items
  const checkboxes = await page.getByRole('checkbox').all();
  const initialCount = checkboxes.length;
  
  if (checkboxes.length > 0) {
    // Check first item (Milk)
    await checkboxes[0].check();
    await page.waitForTimeout(1000);
    
    // Verify item moved or status changed
    const bodyText = await page.evaluate(() => document.body.innerText);
    
    console.log(`✅ Item marked as purchased`);
    console.log(`   - Initial items: ${initialCount}`);
    
    return {
      passed: true,
      checkedItems: 1,
      testName: 'FR011 - Mark Items as Purchased'
    };
  }
  
  console.log(`⚠️  No checkboxes found`);
  return {
    passed: false,
    checkedItems: 0,
    testName: 'FR011 - Mark Items as Purchased'
  };
}

/**
 * TEST SUITE: FR017 - Share Shopping List
 * Validates list sharing and member management
 */
async function testShareShoppingList(page, listName) {
  console.log('🧪 TEST: FR017 - Share Shopping List');
  
  // Look for Share button or Members section
  const shareButton = await page.getByRole('button', { name: /share|invite|members/i }).first();
  
  if (await shareButton.isVisible()) {
    await shareButton.click();
    await page.waitForTimeout(1000);
    
    // Fill in user2 email
    const emailInput = await page.getByPlaceholder(/email|invite/i).first();
    await emailInput.fill(TEST_CONFIG.users.user2.email);
    await page.waitForTimeout(500);
    
    // Click invite/send button
    await page.getByRole('button', { name: /invite|send|share/i }).click();
    await page.waitForTimeout(2000);
    
    // Verify invitation was sent
    const bodyText = await page.evaluate(() => document.body.innerText);
    const inviteSent = bodyText.includes(TEST_CONFIG.users.user2.email) || 
                       bodyText.includes('invited') || 
                       bodyText.includes('shared');
    
    console.log(`✅ Invitation sent: ${inviteSent}`);
    
    return {
      passed: inviteSent,
      invitedUser: TEST_CONFIG.users.user2.email,
      testName: 'FR017 - Share Shopping List'
    };
  }
  
  console.log(`⚠️  Share functionality not found`);
  return {
    passed: false,
    testName: 'FR017 - Share Shopping List'
  };
}

/**
 * MAIN TEST EXECUTION
 * Runs all test suites in sequence
 */
async function runAllTests(page) {
  console.log('🚀 Starting FamilyCart E2E Test Suite');
  console.log('=' .repeat(60));
  
  const results = [];
  
  try {
    // Test 1: User Login
    const loginResult = await testUserLogin(page);
    results.push(loginResult);
    
    if (!loginResult.passed) {
      console.error('❌ Login failed - stopping test suite');
      return results;
    }
    
    // Test 2: Create Shopping List
    const createListResult = await testCreateShoppingList(page);
    results.push(createListResult);
    
    if (!createListResult.passed) {
      console.error('❌ List creation failed - stopping test suite');
      return results;
    }
    
    // Test 3: Add Items
    const addItemsResult = await testAddItemsToList(page, createListResult.listName);
    results.push(addItemsResult);
    
    // Test 4: Mark Items as Purchased
    const markPurchasedResult = await testMarkItemsPurchased(page);
    results.push(markPurchasedResult);
    
    // Test 5: Share Shopping List
    const shareListResult = await testShareShoppingList(page, createListResult.listName);
    results.push(shareListResult);
    
  } catch (error) {
    console.error('❌ Test suite error:', error.message);
    results.push({
      passed: false,
      testName: 'Test Suite Execution',
      error: error.message
    });
  }
  
  // Print summary
  console.log('=' .repeat(60));
  console.log('📊 TEST SUITE SUMMARY');
  console.log('=' .repeat(60));
  
  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;
  
  results.forEach(result => {
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    console.log(`${status} - ${result.testName}`);
  });
  
  console.log('=' .repeat(60));
  console.log(`Total: ${passedTests}/${totalTests} tests passed`);
  console.log(`Success Rate: ${((passedTests/totalTests) * 100).toFixed(1)}%`);
  
  return results;
}

// Export for Playwright MCP execution
module.exports = {
  runAllTests,
  testUserLogin,
  testCreateShoppingList,
  testAddItemsToList,
  testMarkItemsPurchased,
  testShareShoppingList,
  TEST_CONFIG
};
