import axios from 'axios';

// Function to check if a URL should have a trailing slash
const ensureTrailingSlash = (url: string): string => {
  // These are API endpoint base paths that should have a trailing slash
  const pathsNeedingSlash = [
    '/api/v1/shopping-lists',
    '/api/v1/items',
    // Add other API paths that need trailing slashes
  ];
  
  // First, let's handle exact matches
  for (const path of pathsNeedingSlash) {
    if (url === path) {
      console.log(`Adding trailing slash to exact match: ${url} → ${url}/`);
      return url + '/';
    }
  }
  
  // Then handle paths that might be subpaths or have parameters
  for (const path of pathsNeedingSlash) {
    // Skip if URL already has a trailing slash after the base path
    if (url.startsWith(path + '/')) {
      return url;
    }
    
    // If URL starts with the path but has something after it (without a /)
    if (url.startsWith(path) && url.length > path.length) {
      // Add a slash between the base path and whatever comes after
      const prefix = path;
      const suffix = url.substring(path.length);
      const newUrl = `${prefix}/${suffix}`;
      console.log(`Adding slash to path with suffix: ${url} → ${newUrl}`);
      return newUrl;
    }
  }
  
  return url;
};

// Create an axios instance without a base URL
// We'll set it dynamically in the interceptor to handle SSR correctly
const apiClient = axios.create();

// Add a request interceptor to set the baseURL dynamically and add trailing slashes
apiClient.interceptors.request.use(
  (config) => {
    // Set baseURL dynamically on each request (fixes SSR issue where window.location doesn't exist during module init)
    if (typeof window !== 'undefined' && !config.baseURL) {
      config.baseURL = window.location.origin;
      console.log(`Set baseURL dynamically: ${config.baseURL}`);
    }
    
    if (config.url) {
      const originalUrl = config.url;
      
      // Handle the specific problem URLs directly to ensure they always have trailing slashes
      if (config.url === '/api/v1/shopping-lists') {
        config.url = '/api/v1/shopping-lists/';
        console.log(`FORCED trailing slash: ${originalUrl} → ${config.url}`);
      } else if (config.url === '/api/v1/items') {
        config.url = '/api/v1/items/';
        console.log(`FORCED trailing slash: ${originalUrl} → ${config.url}`);
      } else {
        config.url = ensureTrailingSlash(config.url);
      }
      
      // Log URL transformations for debugging
      if (originalUrl !== config.url) {
        console.log(`API URL transformed: ${originalUrl} → ${config.url}`);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    // Get the token from localStorage (with SSR safety)
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    
    // If token exists, add it to the Authorization header with Bearer prefix
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log(`Request to ${config.url} with Authorization: Bearer ${token.substring(0, 10)}...`);
    } else {
      console.warn(`Request to ${config.url} has NO authorization token!`);
    }
    
    return config;
  },
  (error: any) => {
    console.error("Request interceptor error:", error);
    return Promise.reject(error);
  }
);

// Add a response interceptor to log responses - useful for debugging
apiClient.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}: ${response.status} ${response.statusText}`);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`Error response from ${error.config?.url}: ${error.response.status} ${error.response.statusText}`);
      
      // Log response data for debugging (especially useful for 422 validation errors)
      if (error.response.data) {
        console.error('Response data:', error.response.data);
      }
      
      // For 401 unauthorized errors, handle token expiration
      if (error.response.status === 401) {
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        console.error(`401 Unauthorized with token: ${token ? 'Token exists - likely expired' : 'No token'}`);
        
        // Clear expired token and redirect to login
        if (token && typeof window !== 'undefined') {
          console.warn('Token expired - clearing localStorage and redirecting to login');
          localStorage.removeItem('token');
          
          // Only redirect if we're not already on a public page
          const currentPath = window.location.pathname;
          const publicPaths = ['/login', '/signup', '/'];
          if (!publicPaths.includes(currentPath)) {
            window.location.href = '/login';
          }
        }
      }
    } else {
      console.error(`Request error for ${error.config?.url}:`, error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
