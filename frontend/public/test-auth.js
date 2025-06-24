// test-auth.js - Copy this into your browser console to run a test for auth flow

async function testAuthFlow() {
  console.log('🔍 Testing API authentication flow');
  
  // 1. Login
  console.log('Step 1: Login...');
  try {
    const loginResponse = await fetch('/api/v1/auth/jwt/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        username: 'test@example.com', // Replace with a valid email
        password: 'Password123!'      // Replace with the correct password
      })
    });
    
    if (!loginResponse.ok) {
      throw new Error(`Login failed with status ${loginResponse.status}: ${loginResponse.statusText}`);
    }
    
    const loginData = await loginResponse.json();
    console.log('✅ Login successful', loginData);
    
    // 2. Get user info with obtained token
    console.log('Step 2: Fetching user info...');
    const token = loginData.access_token;
    
    // First, try with users/me (no trailing slash)
    console.log('Testing with /api/v1/users/me (no trailing slash)');
    const userResponse = await fetch('/api/v1/users/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!userResponse.ok) {
      throw new Error(`Get user failed with status ${userResponse.status}: ${userResponse.statusText}`);
    }
    
    const userData = await userResponse.json();
    console.log('✅ User data retrieved', userData);
    
    // 3. Now try with the shopping lists endpoint (no trailing slash)
    console.log('Step 3: Fetching shopping lists without trailing slash...');
    const listsResponse = await fetch('/api/v1/shopping-lists', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    console.log('Shopping lists response status:', listsResponse.status);
    console.log('Shopping lists response text:', await listsResponse.text());
    
    // 4. Try with the trailing slash
    console.log('Step 4: Fetching shopping lists WITH trailing slash...');
    const listsWithSlashResponse = await fetch('/api/v1/shopping-lists/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (listsWithSlashResponse.ok) {
      const listsData = await listsWithSlashResponse.json();
      console.log('✅ Shopping lists retrieved', listsData);
    } else {
      console.log('Shopping lists with slash response status:', listsWithSlashResponse.status);
      console.log('Shopping lists with slash response text:', await listsWithSlashResponse.text());
    }
    
    return { success: true, token };
  } catch (error) {
    console.error('❌ Authentication flow test failed:', error);
    return { success: false, error: error.message };
  }
}

// Run the test and log the result
testAuthFlow().then(result => {
  console.log('🏁 Test completed:', result);
});
