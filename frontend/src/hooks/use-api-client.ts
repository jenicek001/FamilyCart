/**
 * Enhanced API client that includes WebSocket session ID for real-time sync exclusion
 */

import { useWebSocketContext } from '@/contexts/WebSocketContext';

interface ApiRequestOptions extends RequestInit {
  sessionId?: string;
}

export function useApiClient() {
  const { sessionId: contextSessionId } = useWebSocketContext();

  const apiClient = async (url: string, options: ApiRequestOptions = {}) => {
    const { sessionId, ...fetchOptions } = options;

    // Use provided session ID or fall back to context session ID
    const activeSessionId = sessionId || contextSessionId;

    // Convert relative URLs to absolute URLs to bypass Next.js proxy
    let fullUrl = url;
    if (url.startsWith('/api/')) {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL;
      
      // Server-side: always use environment variable or fallback
      // Client-side: use relative URLs and let Next.js proxy handle it
      if (typeof window === 'undefined') {
        // Server-side rendering: use absolute URLs
        const fallbackUrl = 'http://localhost:8005';
        fullUrl = `${baseUrl || fallbackUrl}${url}`;
      } else {
        // Client-side: use relative URLs and let Next.js proxy handle it
        fullUrl = url;
      }
    }

    console.log(`API Client: Calling ${fullUrl} (original: ${url})`);

    // Add session ID to headers if available
    const headers = new Headers(fetchOptions.headers);
    if (activeSessionId) {
      headers.set('x-session-id', activeSessionId);
    }

    // Add auth token if available (using 'token' key like the old API client)
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    // Add content type for JSON requests
    if (!headers.has('Content-Type') && (fetchOptions.method === 'POST' || fetchOptions.method === 'PUT' || fetchOptions.method === 'PATCH')) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(fullUrl, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    const contentType = response.headers.get('Content-Type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }

    return response;
  };

  return { apiClient };
}
