/**
 * Application configuration constants
 * Centralized configuration to avoid hardcoded values
 */

// API Configuration
export const API_CONFIG = {
  DEFAULT_PORT: 8005,
  LOCALHOST_HOST: 'localhost',
  FALLBACK_URL: 'http://localhost:8005',
} as const;

// Environment-specific API URL construction
export const getApiUrl = (): string => {
  // In production/deployed environments, use environment variable or current host
  if (process.env.NODE_ENV === 'production' || process.env.API_URL) {
    return process.env.API_URL || `http://${window?.location?.hostname || 'localhost'}:${API_CONFIG.DEFAULT_PORT}`;
  }
  
  // In development, always use localhost with configured port
  return API_CONFIG.FALLBACK_URL;
};

// WebSocket URL construction
export const getWebSocketUrl = (path: string = ''): string => {
  const baseUrl = getApiUrl();
  const wsUrl = baseUrl.replace(/^http/, 'ws');
  return `${wsUrl}${path}`;
};
