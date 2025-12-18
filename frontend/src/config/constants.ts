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
  // 1. Prefer NEXT_PUBLIC_WEBSOCKET_URL if set (allows override for local dev)
  if (process.env.NEXT_PUBLIC_WEBSOCKET_URL) {
    console.log('Using NEXT_PUBLIC_WEBSOCKET_URL:', process.env.NEXT_PUBLIC_WEBSOCKET_URL);
    // Ensure we don't double-slash if path is provided
    const baseUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL.replace(/\/$/, '');
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return path ? `${baseUrl}${cleanPath}` : baseUrl;
  }

  console.log('NEXT_PUBLIC_WEBSOCKET_URL not found, falling back to window/api url');

  // 2. Client-side: Derive from window.location.origin (Best for UAT/Prod/Dev with proxy)
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const hostname = window.location.hostname;

    // SPECIAL CASE FOR LOCAL DEV:
    // If we are running on the frontend dev port (9002), we assume the backend is running
    // on the standard backend dev port (8000) on the SAME hostname.
    // This supports localhost, 127.0.0.1, and LAN IPs (e.g. 192.168.x.x).
    if (window.location.port === '9002') {
        const devBackendPort = '8000';
        const baseUrl = `${protocol}//${hostname}:${devBackendPort}`;
        console.log(`Detected local dev on port 9002, using backend on same host port ${devBackendPort}: ${baseUrl}`);
        const cleanPath = path && !path.startsWith('/') ? `/${path}` : path;
        return `${baseUrl}${cleanPath}`;
    }

    const baseUrl = `${protocol}//${host}`;
    // Ensure path starts with / if provided
    const cleanPath = path && !path.startsWith('/') ? `/${path}` : path;
    console.log('Derived WebSocket URL from window:', `${baseUrl}${cleanPath}`);
    return `${baseUrl}${cleanPath}`;
  }

  // 3. Derive from API URL
  const baseUrl = getApiUrl();
  const wsUrl = baseUrl.replace(/^http/, 'ws');
  return `${wsUrl}${path}`;
};
