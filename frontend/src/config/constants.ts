/**
 * Application configuration constants
 * Centralized configuration to avoid hardcoded values
 */

// API Configuration
export const getApiUrl = (): string => {
  // 1. Prefer NEXT_PUBLIC_API_URL (Client-side & Build-time)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // 2. Fallback to API_URL (Server-side)
  if (process.env.API_URL) {
    return process.env.API_URL;
  }

  // 3. Fallback for local development if no env vars are set
  // This allows the app to work locally without .env in some cases, but warns
  if (typeof window !== 'undefined') {
    console.warn('No API_URL or NEXT_PUBLIC_API_URL found. Defaulting to http://localhost:8000');
  }
  return 'http://localhost:8000';
};

// WebSocket URL construction
export const getWebSocketUrl = (path: string = ''): string => {
  // 1. Prefer NEXT_PUBLIC_WEBSOCKET_URL
  if (process.env.NEXT_PUBLIC_WEBSOCKET_URL) {
    // Ensure we don't double-slash if path is provided
    const baseUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL.replace(/\/$/, '');
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return path ? `${baseUrl}${cleanPath}` : baseUrl;
  }

  // 2. Derive from API URL
  const baseUrl = getApiUrl();
  const wsUrl = baseUrl.replace(/^http/, 'ws');
  return `${wsUrl}${path}`;
};
