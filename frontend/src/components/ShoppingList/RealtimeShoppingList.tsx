/**
 * Real-time enabled shopping list wrapper component.
 * Integrates WebSocket connection for live updates.
 */

"use client";

import React, { useCallback, useEffect, useState } from 'react';
import { ShoppingList, Item } from '../../types';
import { ShoppingListView } from './ShoppingListView';
import { useWebSocket, WebSocketMessage } from '../../hooks/use-websocket';
import { useToast } from '../../hooks/use-toast';
import { useAuth } from '../../contexts/AuthContext';

interface RealtimeShoppingListProps {
  list: ShoppingList;
  allLists?: ShoppingList[];
  onUpdateItem: (itemId: number, updates: Partial<Item>) => Promise<void>;
  onDeleteItem: (itemId: number) => Promise<void>;
  onAddItem: (item: any) => Promise<void>;
  onBackToSelector?: () => void;
  onSelectList?: (list: ShoppingList) => void;
  onListUpdate?: (listId: number, updatedData: any) => void;
  onItemUpdate?: (listId: number, item: Item) => void;
  onItemDelete?: (listId: number, itemId: number) => void;
  onItemCreate?: (listId: number, item: Item) => void;
  onCreateList?: () => void;
}

export function RealtimeShoppingList({
  list,
  allLists = [],
  onUpdateItem,
  onDeleteItem,
  onAddItem,
  onBackToSelector,
  onSelectList,
  onListUpdate,
  onItemUpdate,
  onItemDelete,
  onItemCreate,
  onCreateList,
}: RealtimeShoppingListProps) {
  const { toast } = useToast();
  const { user, token } = useAuth();
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');

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
    if (!message.item || !message.event_type) return;

    const { event_type, item, user_id } = message;

    // Show notification for changes made by other users
    const isOwnChange = user?.id && user.id === user_id;
    
    switch (event_type) {
      case 'created':
        // Only update state for changes made by other users
        // (our own changes are handled optimistically in the UI)
        if (!isOwnChange) {
          onItemCreate?.(list.id, item);
          toast({
            title: "Item added",
            description: `"${item.name}" was added to the list`,
            duration: 3000,
          });
        }
        break;

      case 'updated':
        // Always update for changes, even our own, because the server may have added 
        // additional data (AI categorization, icons, standardized names, etc.)
        onItemUpdate?.(list.id, item);
        if (!isOwnChange) {
          toast({
            title: "Item updated",
            description: `"${item.name}" was modified`,
            duration: 3000,
          });
        }
        break;

      case 'deleted':
        // Only update state for deletions made by other users
        // (our own deletions are handled optimistically in the UI)
        if (!isOwnChange) {
          onItemDelete?.(list.id, item.id);
          toast({
            title: "Item removed",
            description: `An item was removed from the list`,
            duration: 3000,
          });
        }
        break;

      case 'category_changed':
        // Always update for category changes (since we don't do optimistic updates for this)
        onItemUpdate?.(list.id, item);
        if (!isOwnChange) {
          toast({
            title: "Item categorized",
            description: `"${item.name}" was moved to ${item.category?.name || 'Other'}`,
            duration: 3000,
          });
        }
        break;

      default:
        console.log('Unknown item change event:', event_type);
    }
  }, [list.id, onItemCreate, onItemUpdate, onItemDelete, toast, user]);

  const handleListChange = useCallback((message: WebSocketMessage) => {
    if (!message.list || !message.event_type) return;

    const { event_type, list: listData, user_id, new_member_email, removed_user_id } = message;

    // Show notification for changes made by other users
    const isOwnChange = user?.id && user.id === user_id;

    switch (event_type) {
      case 'updated':
        onListUpdate?.(list.id, listData);
        if (!isOwnChange) {
          toast({
            title: "List updated",
            description: `"${listData.name}" was modified`,
            duration: 3000,
          });
        }
        break;

      case 'shared':
        onListUpdate?.(list.id, listData);
        if (!isOwnChange && new_member_email) {
          toast({
            title: "List shared",
            description: `List was shared with ${new_member_email}`,
            duration: 4000,
          });
        }
        break;

      case 'member_removed':
        onListUpdate?.(list.id, listData);
        if (!isOwnChange && removed_user_id) {
          toast({
            title: "Member removed",
            description: `A member was removed from the list`,
            duration: 3000,
          });
        }
        break;

      case 'deleted':
        if (!isOwnChange) {
          toast({
            title: "List deleted",
            description: `"${list.name}" was deleted`,
            variant: "destructive",
            duration: 5000,
          });
          // Navigate away from deleted list
          onBackToSelector?.();
        }
        break;

      default:
        console.log('Unknown list change event:', event_type);
    }
  }, [list.id, list.name, onListUpdate, onBackToSelector, toast, user]);

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

  // Show connection status in toast when there are issues
  useEffect(() => {
    if (error) {
      // Don't show toast for temporary connection states during login
      if (error.includes('Please log in to enable real-time updates') ||
          error.includes('No list selected') ||
          error.includes('Authentication required')) {
        return;
      }

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
    }
  }, [error, toast, reconnect]);

  // Connection status indicator
  const ConnectionIndicator = () => {
    const statusConfig = {
      connecting: { icon: '⏳', color: 'text-yellow-500', text: 'Connecting...' },
      connected: { icon: '🟢', color: 'text-green-500', text: 'Live updates enabled' },
      disconnected: { icon: '⚫', color: 'text-gray-400', text: 'Offline' },
      error: { icon: '🔴', color: 'text-red-500', text: 'Connection error' },
    };

    const config = statusConfig[connectionStatus];

    return (
      <div className={`flex items-center gap-1 text-xs ${config.color}`} title={config.text}>
        <span>{config.icon}</span>
        <span className="hidden sm:inline">{config.text}</span>
      </div>
    );
  };

  // Handle list updates from the share dialog
  const handleListUpdate = useCallback((updatedList: ShoppingList) => {
    if (onListUpdate) {
      onListUpdate(list.id, updatedList);
    }
  }, [list.id, onListUpdate]);

  return (
    <div className="relative">
      {/* Connection status indicator */}
      <div className="absolute top-2 right-2 z-30">
        <ConnectionIndicator />
      </div>
      
      {/* Shopping list view */}
      <ShoppingListView
        list={list}
        allLists={allLists}
        onUpdateItem={onUpdateItem}
        onDeleteItem={onDeleteItem}
        onAddItem={onAddItem}
        onBackToSelector={onBackToSelector}
        onSelectList={onSelectList}
        onListUpdate={handleListUpdate}
        onCreateList={onCreateList}
      />
    </div>
  );
}
