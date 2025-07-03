/**
 * WebSocket hook for real-time shopping list updates.
 * Provides connection management, authentication, and event handling.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';

export interface WebSocketMessage {
  type: 'item_change' | 'list_change' | 'pong' | 'connection_established';
  event_type?: 'created' | 'updated' | 'deleted' | 'shared' | 'member_removed' | 'category_changed';
  list_id?: number;
  item?: any;
  list?: any;
  timestamp?: string;
  user_id?: string;
  new_member_email?: string;
  removed_user_id?: string;
  message?: string; // For connection_established type
}

export interface UseWebSocketOptions {
  listId: number;
  onItemChange?: (message: WebSocketMessage) => void;
  onListChange?: (message: WebSocketMessage) => void;
  onConnectionChange?: (connected: boolean) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

export interface UseWebSocketReturn {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  send: (message: any) => void;
  disconnect: () => void;
  reconnect: () => void;
}

export function useWebSocket({
  listId,
  onItemChange,
  onListChange,
  onConnectionChange,
  autoReconnect = true,
  reconnectInterval = 3000,
}: UseWebSocketOptions): UseWebSocketReturn {
  const { token } = useAuth();
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  
  // Use refs to avoid stale closures in callbacks
  const connectRef = useRef<(() => void) | null>(null);
  const latestTokenRef = useRef(token);
  const latestListIdRef = useRef(listId);
  
  // Update refs when values change
  useEffect(() => {
    latestTokenRef.current = token;
  }, [token]);
  
  useEffect(() => {
    latestListIdRef.current = listId;
  }, [listId]);

  const clearTimeouts = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    clearTimeouts();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
    setConnecting(false);
    setError(null);
    onConnectionChange?.(false);
  }, [clearTimeouts, onConnectionChange]);

  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const startPingInterval = useCallback(() => {
    clearInterval(pingIntervalRef.current!);
    pingIntervalRef.current = setInterval(() => {
      send({ type: 'ping' });
    }, 30000); // Send ping every 30 seconds
  }, [send]);

  const connect = useCallback(() => {
    if (!token || !listId || wsRef.current?.readyState === WebSocket.OPEN) {
      if (!token) {
        console.log('WebSocket connection skipped: No auth token available');
        setError('Authentication required. Please log in.');
        return;
      }
      return;
    }

    console.log(`Attempting WebSocket connection to list ${listId} with token: ${token.substring(0, 20)}...`);
    setConnecting(true);
    setError(null);

    try {
      // Construct WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = process.env.NEXT_PUBLIC_API_URL?.replace(/^https?:\/\//, '') || 'localhost:8000';
      const wsUrl = `${protocol}//${host}/api/v1/ws/lists/${listId}?token=${encodeURIComponent(token)}`;

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log(`WebSocket connected to list ${listId}`);
        setConnected(true);
        setConnecting(false);
        setError(null);
        reconnectAttemptsRef.current = 0;
        onConnectionChange?.(true);
        startPingInterval();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('WebSocket message received:', message);
          
          switch (message.type) {
            case 'item_change':
              onItemChange?.(message);
              break;
            case 'list_change':
              onListChange?.(message);
              break;
            case 'pong':
              // Handle pong response (connection keepalive)
              break;
            case 'connection_established':
              console.log('WebSocket connection established:', message.message);
              break;
            default:
              console.log('Unknown WebSocket message type:', message.type);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log(`WebSocket disconnected from list ${listId}:`, event.code, event.reason);
        setConnected(false);
        setConnecting(false);
        clearTimeouts();
        onConnectionChange?.(false);

        // Handle specific close codes
        if (event.code === 1008) { // Policy Violation (Authentication failed)
          setError('Authentication failed. Please log in again.');
          return;
        } else if (event.code === 1003) { // Unsupported Data (No list access)
          setError('Access denied to this shopping list.');
          return;
        }

        // Auto-reconnect with exponential backoff for other errors
        if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(reconnectInterval * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectAttemptsRef.current++;
          
          setError(`Connection lost, reconnecting in ${delay / 1000}s... (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            // Use connectRef to access the latest connect function to avoid stale closure
            if (connectRef.current) {
              connectRef.current();
            }
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('Failed to reconnect after maximum attempts. Please refresh the page.');
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
        setConnecting(false);
      };

    } catch (err) {
      console.error('Error creating WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
      setConnecting(false);
    }
  }, [token, listId, onItemChange, onListChange, onConnectionChange, autoReconnect, reconnectInterval, startPingInterval]);

  // Assign connect function to ref for stable access
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setTimeout(() => {
      if (connectRef.current) {
        connectRef.current();
      }
    }, 1000);
  }, [disconnect]);

  // Connect when token and listId are available
  useEffect(() => {
    if (token && listId) {
      console.log('WebSocket useEffect: Attempting connection', { hasToken: !!token, listId });
      connect();
    } else {
      console.log('WebSocket useEffect: Skipping connection', { hasToken: !!token, listId });
      if (!token) {
        setError('Please log in to enable real-time updates');
      } else if (!listId) {
        setError('No list selected');
      }
    }
    
    return () => {
      disconnect();
    };
  }, [token, listId]); // Removed connect and disconnect from dependencies

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connected,
    connecting,
    error,
    send,
    disconnect,
    reconnect,
  };
}
