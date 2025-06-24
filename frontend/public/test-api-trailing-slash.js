// Test script for debugging trailing slash redirects
document.addEventListener('DOMContentLoaded', async () => {
  const outputDiv = document.createElement('div');
  outputDiv.style.padding = '20px';
  outputDiv.style.fontFamily = 'monospace';
  outputDiv.style.whiteSpace = 'pre';
  outputDiv.style.fontSize = '14px';
  outputDiv.style.lineHeight = '1.5';
  outputDiv.style.backgroundColor = '#f5f5f5';
  outputDiv.style.border = '1px solid #ddd';
  outputDiv.style.borderRadius = '5px';
  outputDiv.style.margin = '20px';
  outputDiv.style.overflow = 'auto';
  
  document.body.appendChild(outputDiv);

  const log = (message) => {
    console.log(message);
    outputDiv.innerHTML += message + '<br>';
  };

  const error = (message) => {
    console.error(message);
    outputDiv.innerHTML += `<span style="color: red">${message}</span><br>`;
  };

  // Test URLs
  const urlsToTest = [
    '/api/v1/shopping-lists',
    '/api/v1/shopping-lists/',
    '/api/v1/shopping-lists/123',
    '/api/v1/shopping-lists?param=value',
    '/api/v1/users/me',
    '/api/v1/users/me/',
  ];

  log('=== TESTING URL TRANSFORMATIONS ===');

  // Get token from localStorage
  const token = localStorage.getItem('token');
  
  if (!token) {
    error('No auth token found in localStorage. Please login first.');
    return;
  }

  log(`Found token: ${token.substring(0, 10)}...`);

  // Test our URL transformation logic
  const ensureTrailingSlash = (url) => {
    const pathsNeedingSlash = [
      '/api/v1/shopping-lists',
      '/api/v1/items',
      '/api/v1/users/me',
    ];
    
    for (const path of pathsNeedingSlash) {
      if (url === path || url.startsWith(path + '/') || url.startsWith(path + '?')) {
        if (url === path) {
          return url + '/';
        }
      } else if (url.startsWith(path)) {
        const restOfUrl = url.substring(path.length);
        return `${path}/${restOfUrl}`;
      }
    }
    
    return url;
  };

  // Test the transformation logic
  log('\n=== URL TRANSFORMATION TESTS ===');
  urlsToTest.forEach(url => {
    const transformed = ensureTrailingSlash(url);
    log(`${url} → ${transformed}`);
  });

  // Test actual API calls
  log('\n=== API CALL TESTS ===');

  const apiCall = async (url) => {
    try {
      // Create headers with token
      const headers = {
        'Authorization': `Bearer ${token}`
      };

      // Make the call
      log(`Fetching: ${url}`);
      const response = await fetch(url, { headers });
      
      // Log the result
      if (response.redirected) {
        log(`⚠️ REDIRECTED to ${response.url}, status: ${response.status}`);
      }
      
      if (response.ok) {
        log(`✓ SUCCESS: ${response.status}`);
        const data = await response.json();
        log(`  Data: ${JSON.stringify(data).substring(0, 100)}...`);
      } else {
        error(`✗ ERROR: ${response.status}`);
        try {
          const errorData = await response.json();
          error(`  Error details: ${JSON.stringify(errorData)}`);
        } catch (e) {
          error(`  Could not parse error response`);
        }
      }
    } catch (e) {
      error(`✗ EXCEPTION: ${e.message}`);
    }
  };

  // Test each URL
  log('\nTesting direct fetch() calls:');
  for (const url of urlsToTest) {
    await apiCall(url);
    log('---');
  }

  // Test with transformed URLs
  log('\nTesting transformed URLs:');
  for (const url of urlsToTest) {
    await apiCall(ensureTrailingSlash(url));
    log('---');
  }
});
