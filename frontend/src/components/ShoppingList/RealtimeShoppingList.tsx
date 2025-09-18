/**
 * Real-time enabled shopping list wrapper component.
 * Integrates WebSocket connection for live updates.
 */

"use client";

import React, { useCallback, useEffect, useState, useMemo, useRef } from 'react';
import { ShoppingList, Item } from '../../types';
import { ShoppingListView } from './ShoppingListView';
import { useWebSocket, WebSocketMessage } from '../../hooks/use-websocket';
import { useToast } from '../../hooks/use-toast';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocketContext } from '../../contexts/WebSocketContext';
import { useShoppingListContextSafe } from '../../contexts/ShoppingListContext';

interface RealtimeShoppingListProps {
  list: ShoppingList;
  allLists: ShoppingList[];
  onSelectList?: (list: ShoppingList | null) => void;
  onCreateList: (name: string) => void;
  onBackToSelector?: () => void;
  onItemCreate?: (listId: number, item: Item) => void;
  onItemUpdate?: (listId: number, item: Item) => void;
  onItemDelete?: (listId: number, itemId: number) => void;
  onListUpdate?: (listId: number, list: ShoppingList) => void;
  onAddItem: (item: any) => Promise<void>;
  onUpdateItem: (itemId: number, updates: Partial<Item>) => Promise<void>;
  onDeleteItem: (itemId: number) => Promise<void>;
}

export function RealtimeShoppingList({
  list,
  allLists,
  onSelectList,
  onCreateList,
  onBackToSelector,
  onItemCreate,
  onItemUpdate,
  onItemDelete,
  onListUpdate,
  onAddItem,
  onUpdateItem,
  onDeleteItem,
}: RealtimeShoppingListProps) {
  const { toast } = useToast();
  const { user, token } = useAuth();
  const { isLocalAction, shouldIgnoreCreate } = useWebSocketContext();
  const shoppingListContext = useShoppingListContextSafe();
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  
  // Ref to track the delayed toast timeout
  const connectionErrorTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Handle list updates from the share dialog
  const handleListUpdate = useCallback((updatedList: ShoppingList) => {
    if (onListUpdate) {
      onListUpdate(list.id, updatedList);
    }
  }, [list.id, onListUpdate]);

  // Memoize handlers to prevent unnecessary re-renders
  const shoppingListHandlers = useMemo(() => ({
    onListSelect: onSelectList,
    onCreateList: () => {
      // Context expects no parameters - open create dialog or use default name
      onCreateList('New Shopping List');
    },
    onListUpdate: handleListUpdate,
    connectionStatus,
    onBackToSelector,
  }), [onSelectList, onCreateList, handleListUpdate, connectionStatus, onBackToSelector]);

  // Update shopping list context when component mounts or list changes
  useEffect(() => {
    if (shoppingListContext) {
      shoppingListContext.setCurrentList(list);
      shoppingListContext.setAllLists(allLists);
    }

    // Cleanup when component unmounts
    return () => {
      if (shoppingListContext) {
        shoppingListContext.setCurrentList(null);
        shoppingListContext.setAllLists([]);
        shoppingListContext.setShoppingListHandlers({});
      }
    };
  }, [list, allLists, shoppingListContext]);

  // Update handlers separately to avoid dependency loop
  useEffect(() => {
    if (shoppingListContext) {
      shoppingListContext.setShoppingListHandlers(shoppingListHandlers);
    }
  }, [shoppingListContext, shoppingListHandlers]);

  // Debug logging
  useEffect(() => {
    console.log('RealtimeShoppingList: Auth state changed', {
      hasUser: !!user,
      hasToken: !!token,
      userId: user?.id,
      listId: list.id,
      tokenLength: token?.length
    });
  }, [user, token, list.id]);

  // WebSocket handlers
  const handleItemChange = useCallback((message: WebSocketMessage) => {
    console.log('[RealtimeShoppingList] 📨 RAW WebSocket message received:', JSON.stringify(message, null, 2));
    
    if (!message.item || !message.event_type) {
      console.log('[RealtimeShoppingList] ⚠️ Invalid message - missing item or event_type');
      return;
    }

    const { event_type, item, user_id, timestamp } = message;
    
    // Special handling for create events - check ignore flag first
    if (event_type === 'created') {
      if (shouldIgnoreCreate()) {
        console.log('[RealtimeShoppingList] 🚫 IGNORING create WebSocket message due to ignore flag');
        return;
      }
    }
    
    // Check if this is a duplicate of a recent local action (for update/delete)
    const standardActionKey = `${event_type}-${item.id}`;
    console.log('[RealtimeShoppingList] 🔑 Checking standard action key:', standardActionKey);
    
    if (isLocalAction(standardActionKey)) {
      console.log('[RealtimeShoppingList] 🚫 SKIPPING WebSocket duplicate for recent local action:', standardActionKey);
      return;
    }
    
    console.log('[RealtimeShoppingList] ✅ PROCESSING WebSocket message:', {
      event_type,
      itemId: item.id,
      itemName: item.name,
      user_id,
      timestamp
    });

    // Apply WebSocket updates for remote changes
    console.log('Applying WebSocket item change:', { event_type, itemId: item.id, itemName: item.name });
    
    switch (event_type) {
      case 'created':
        onItemCreate?.(list.id, item);
        toast({
          title: "Item added",
          description: `"${item.name}" was added to the list`,
          duration: 3000,
        });
        break;

      case 'updated':
        // Update for all changes - server may have added AI categorization, icons, etc.
        onItemUpdate?.(list.id, item);
        toast({
          title: "Item updated",
          description: `"${item.name}" was modified`,
          duration: 3000,
        });
        break;

      case 'deleted':
        // Update state for all received deletion events
        // The backend has already excluded the originating session
        onItemDelete?.(list.id, item.id);
        toast({
          title: "Item removed",
          description: `An item was removed from the list`,
          duration: 3000,
        });
        break;

      case 'category_changed':
        // Update for category changes
        onItemUpdate?.(list.id, item);
        toast({
          title: "Item categorized",
          description: `"${item.name}" was moved to ${item.category?.name || 'Other'}`,
          duration: 3000,
        });
        break;

      default:
        console.log('Unknown item change event:', event_type);
    }
  }, [list.id, onItemCreate, onItemUpdate, onItemDelete, toast, isLocalAction]);

  const handleListChange = useCallback((message: WebSocketMessage) => {
    if (!message.list || !message.event_type) return;

    const { event_type, list: listData, user_id, new_member_email, removed_user_id } = message;

    // Session-based exclusion: Since the backend already excludes the originating session,
    // ALL messages received here should be processed and applied to update the UI.
    // This enables real-time sync between different sessions of the same user.

    switch (event_type) {
      case 'updated':
        onListUpdate?.(list.id, listData);
        toast({
          title: "List updated",
          description: `"${listData.name}" was modified`,
          duration: 3000,
        });
        break;

      case 'shared':
        onListUpdate?.(list.id, listData);
        if (new_member_email) {
          toast({
            title: "List shared",
            description: `List was shared with ${new_member_email}`,
            duration: 4000,
          });
        }
        break;

      case 'member_removed':
        onListUpdate?.(list.id, listData);
        if (removed_user_id) {
          toast({
            title: "Member removed",
            description: `A member was removed from the list`,
            duration: 3000,
          });
        }
        break;

      case 'deleted':
        toast({
          title: "List deleted",
          description: `"${list.name}" was deleted`,
          variant: "destructive",
          duration: 5000,
        });
        // Navigate away from deleted list
        onBackToSelector?.();
        break;

      default:
        console.log('Unknown list change event:', event_type);
    }
  }, [list.id, list.name, onListUpdate, onBackToSelector, toast]);

  const handleConnectionChange = useCallback((connected: boolean) => {
    setConnectionStatus(connected ? 'connected' : 'disconnected');
  }, []);

  // WebSocket connection
  const { connected, connecting, error, reconnect } = useWebSocket({
    listId: list.id,
    onItemChange: handleItemChange,
    onListChange: handleListChange,
    onConnectionChange: handleConnectionChange,
    autoReconnect: true,
  });

  // Update connection status
  useEffect(() => {
    if (connecting) {
      setConnectionStatus('connecting');
    } else if (connected) {
      setConnectionStatus('connected');
    } else if (error) {
      setConnectionStatus('error');
    } else {
      setConnectionStatus('disconnected');
    }
  }, [connected, connecting, error]);

  // Show connection status in toast when there are issues (with delay)
  useEffect(() => {
    // Clear any existing timeout
    if (connectionErrorTimeoutRef.current) {
      clearTimeout(connectionErrorTimeoutRef.current);
      connectionErrorTimeoutRef.current = null;
    }

    if (error) {
      // Don't show toast for temporary connection states during login
      if (error.includes('Please log in to enable real-time updates') ||
          error.includes('No list selected') ||
          error.includes('Authentication required')) {
        return;
      }

      // Set a timeout to show the toast only if the error persists for more than 10 seconds
      connectionErrorTimeoutRef.current = setTimeout(() => {
        // Show different actions based on error type
        let action = (
          <button
            onClick={reconnect}
            className="px-3 py-1 text-sm bg-white text-red-600 rounded border hover:bg-gray-50"
          >
            Retry
          </button>
        );

        // For authentication errors, suggest refresh instead
        if (error.includes('Authentication failed') || error.includes('log in again')) {
          action = (
            <button
              onClick={() => window.location.reload()}
              className="px-3 py-1 text-sm bg-white text-red-600 rounded border hover:bg-gray-50"
            >
              Refresh Page
            </button>
          );
        }

        toast({
          title: "Connection issue",
          description: error,
          variant: "destructive",
          duration: 8000,
          action: action,
        });
      }, 10000); // 10 second delay before showing the toast
    }

    // Cleanup function to clear timeout when component unmounts or error changes
    return () => {
      if (connectionErrorTimeoutRef.current) {
        clearTimeout(connectionErrorTimeoutRef.current);
        connectionErrorTimeoutRef.current = null;
      }
    };
  }, [error, toast, reconnect]);

  return (
    <div className="relative">      
      {/* Shopping list view - controls now moved to header */}
      <ShoppingListView
        list={list}
        onUpdateItem={onUpdateItem}
        onDeleteItem={onDeleteItem}
        onAddItem={onAddItem}
      />
    </div>
  );
}
