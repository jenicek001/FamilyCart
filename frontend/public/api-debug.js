/**
 * Debug script to help diagnose the trailing slash issue with API requests
 */

// This script adds a global event listener to XMLHttpRequest to track all API requests
// It will help us see if the apiClient is correctly adding trailing slashes

(function() {
  // Original open method
  const originalOpen = XMLHttpRequest.prototype.open;
  
  // Override the open method to log all API requests
  XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
    // Log only API requests
    if (url.includes('/api/')) {
      console.log(`%c${method} ${url}`, 'color: blue; font-weight: bold;');
      
      // Check if the URL has a trailing slash where needed
      const apiPaths = ['/api/v1/shopping-lists', '/api/v1/items', '/api/v1/users/me'];
      
      for (const path of apiPaths) {
        if (url === path) {
          console.warn(`%cWARNING: Missing trailing slash in URL: ${url}`, 'color: red; font-weight: bold;');
          console.info(`%cRecommended URL: ${url}/`, 'color: green;');
        }
      }
    }
    
    // Call the original method
    return originalOpen.apply(this, arguments);
  };
  
  // Track fetch requests too
  const originalFetch = window.fetch;
  window.fetch = function(url, options) {
    // Check if it's a string URL or a Request object
    const urlString = url instanceof Request ? url.url : url;
    
    if (typeof urlString === 'string' && urlString.includes('/api/')) {
      console.log(`%cFetch ${options?.method || 'GET'} ${urlString}`, 'color: purple; font-weight: bold;');
      
      // Check if the URL has a trailing slash where needed
      const apiPaths = ['/api/v1/shopping-lists', '/api/v1/items', '/api/v1/users/me'];
      
      for (const path of apiPaths) {
        if (urlString === path) {
          console.warn(`%cWARNING: Missing trailing slash in URL: ${urlString}`, 'color: red; font-weight: bold;');
          console.info(`%cRecommended URL: ${urlString}/`, 'color: green;');
        }
      }
    }
    
    // Call the original fetch
    return originalFetch.apply(this, arguments);
  };
  
  // Inform that the debug script has been loaded
  console.log('%cAPI request debugging enabled ✓', 'color: green; font-weight: bold; font-size: 14px;');
  console.log('Monitoring requests to /api/ endpoints for trailing slash issues');
})();

// After a short delay, check localStorage for token
setTimeout(() => {
  const token = localStorage.getItem('token');
  console.log('%cAuth token in localStorage:', 'font-weight: bold;', token ? 'Found ✓' : 'Not found ✗');
  
  if (token) {
    console.log(`Token starts with: ${token.substring(0, 15)}...`);
  }
}, 1000);
