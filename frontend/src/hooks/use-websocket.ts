/**
 * WebSocket hook for real-time shopping list updates.
 * Provides connection management, authentication, and event handling.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/hooks/use-toast';
import { useWebSocketContext } from '@/contexts/WebSocketContext';
import { getWebSocketUrl } from '@/config/constants';

// WebSocket connection states

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
  session_id?: string; // Session ID from connection_established
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
  sessionId: string | null;
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
  const { setSessionId: setContextSessionId } = useWebSocketContext();
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  
  // Connection state management to prevent rapid connects/disconnects
  const connectionAttemptRef = useRef<NodeJS.Timeout | null>(null);
  const isConnectingRef = useRef(false);
  const stableConnectionRef = useRef(false);
  const lastConnectionAttemptRef = useRef<number>(0);
  const minConnectionInterval = 1000; // Minimum 1 second between connection attempts
  
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
    if (connectionAttemptRef.current) {
      clearTimeout(connectionAttemptRef.current);
      connectionAttemptRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    clearTimeouts();
    isConnectingRef.current = false;
    stableConnectionRef.current = false;
    
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
    const now = Date.now();
    
    // Prevent rapid connection attempts
    if (isConnectingRef.current || 
        wsRef.current?.readyState === WebSocket.OPEN ||
        (now - lastConnectionAttemptRef.current) < minConnectionInterval) {
      console.log('WebSocket connection skipped: Too soon or already connecting/connected');
      return;
    }
    
    if (!token || !listId) {
      if (!token) {
        console.log('WebSocket connection skipped: No auth token available');
        setError('Authentication required. Please log in.');
        return;
      }
      if (!listId) {
        console.log('WebSocket connection skipped: No list ID provided');
        setError('No list selected');
        return;
      }
    }

    lastConnectionAttemptRef.current = now;
    isConnectingRef.current = true;
    
    console.log(`Attempting WebSocket connection to list ${listId} with token: ${token.substring(0, 20)}...`);
    setConnecting(true);
    setError(null);

    try {
      // Construct WebSocket URL using centralized configuration
      const wsPath = `/api/v1/ws/lists/${listId}?token=${encodeURIComponent(token)}`;
      const wsUrl = getWebSocketUrl(wsPath);
      console.log(`Connecting to WebSocket: ${wsUrl}`);

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log(`WebSocket connected to list ${listId}`);
        setConnected(true);
        setConnecting(false);
        setError(null);
        reconnectAttemptsRef.current = 0;
        isConnectingRef.current = false;
        stableConnectionRef.current = true;
        onConnectionChange?.(true);
        
        try {
          startPingInterval();
        } catch (pingError) {
          console.warn('Failed to start ping interval:', pingError);
          // Don't fail the connection for ping issues
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('WebSocket message received:', message);
          
          switch (message.type) {
            case 'item_change':
              try {
                onItemChange?.(message);
              } catch (error) {
                console.error('Error in onItemChange handler:', error);
                // Don't propagate handler errors to WebSocket error state
              }
              break;
            case 'list_change':
              try {
                onListChange?.(message);
              } catch (error) {
                console.error('Error in onListChange handler:', error);
                // Don't propagate handler errors to WebSocket error state
              }
              break;
            case 'pong':
              // Handle pong response (connection keepalive)
              break;
            case 'connection_established':
              console.log('WebSocket connection established:', message.message);
              // Capture session ID from the backend
              if (message.session_id) {
                setSessionId(message.session_id);
                setContextSessionId(message.session_id);
                console.log('Session ID received:', message.session_id);
              }
              break;
            default:
              console.log('Unknown WebSocket message type:', message.type);
          }
        } catch (parseError) {
          console.error('Error parsing WebSocket message:', parseError);
          // Don't set error state for parse errors
        }
      };

      wsRef.current.onclose = (event) => {
        console.log(`WebSocket disconnected from list ${listId}:`, event.code, event.reason);
        setConnected(false);
        setConnecting(false);
        clearTimeouts();
        isConnectingRef.current = false;
        stableConnectionRef.current = false;
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
        isConnectingRef.current = false;
      };

    } catch (err) {
      console.error('Error creating WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
      setConnecting(false);
      isConnectingRef.current = false;
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
      console.log('WebSocket useEffect: Token and listId available', { 
        hasToken: !!token, 
        listId,
        isConnecting: isConnectingRef.current,
        hasConnection: !!wsRef.current,
        connectionState: wsRef.current?.readyState
      });
      
      // Don't reconnect if we already have a stable connection with the same parameters
      if (stableConnectionRef.current && 
          wsRef.current?.readyState === WebSocket.OPEN &&
          latestTokenRef.current === token &&
          latestListIdRef.current === listId) {
        console.log('WebSocket useEffect: Skipping connection - already stable');
        return;
      }
      
      // Add a longer delay to ensure authentication state has stabilized
      const connectTimeout = setTimeout(() => {
        // Double-check that we still need to connect and params haven't changed
        if (latestTokenRef.current && latestListIdRef.current) {
          if (connectRef.current) {
            connectRef.current();
          } else {
            connect();
          }
        }
      }, 500); // Increased delay to 500ms for better stability
      
      return () => {
        clearTimeout(connectTimeout);
        // Only disconnect if this useEffect is being cleaned up due to token/listId change
        // Don't disconnect on component unmount - let the cleanup effect handle that
      };
    } else {
      console.log('WebSocket useEffect: Missing token or listId', { hasToken: !!token, listId });
      if (!token) {
        setError('Please log in to enable real-time updates');
      } else if (!listId) {
        setError('No list selected');
      }
      
      // Disconnect if we don't have the required parameters
      disconnect();
    }
  }, [token, listId]); // Only depend on token and listId changes

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
    sessionId,
    send,
    disconnect,
    reconnect,
  };
}
