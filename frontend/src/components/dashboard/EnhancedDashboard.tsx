"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useWebSocketContext } from '@/contexts/WebSocketContext';
import { useApiClient } from '@/hooks/use-api-client';
import type { ShoppingList, Item, ItemCreate } from '@/types';
import { ShoppingListSelector } from '@/components/ShoppingList/ShoppingListSelector';
import { RealtimeShoppingList } from '@/components/ShoppingList/RealtimeShoppingList';
import { EmptyState } from '@/components/ShoppingList/EmptyState';
import { CreateListDialog } from '@/components/ShoppingList/CreateListDialog';
import { useToast } from '@/hooks/use-toast';
import { UnverifiedUserAlert } from '@/components/dashboard/UnverifiedUserAlert';
import { setLastActiveListId, getLastActiveListId } from '@/utils/localStorage';

export default function EnhancedDashboard() {
  const { user, loading: authLoading, token, fetchUser } = useAuth();
  const { trackLocalAction, ignoreNextCreate } = useWebSocketContext();
  const { apiClient } = useApiClient();
  const [lists, setLists] = useState<ShoppingList[]>([]);
  const [selectedList, setSelectedList] = useState<ShoppingList | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateListDialogOpen, setIsCreateListDialogOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { toast } = useToast();

  // Check if user is logged in but not verified
  // We check both cases:
  // 1. user object exists but is_verified is false (new behavior with backend fix)
  // 2. user object is null but token exists (legacy behavior if backend returns 403)
  const isUnverified = (user && !user.is_verified) || (!user && token);

  const fetchLists = useCallback(async () => {
    if (!token || !user) {
      setIsLoading(false);
      return;
    }

    // Don't fetch lists if user is not verified
    if (isUnverified) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient('/api/v1/shopping-lists/', { method: 'GET' });
      const sortedLists = data.sort((a: ShoppingList, b: ShoppingList) => 
        new Date(b.updated_at).getTime() - new Date(a.created_at).getTime()
      );
      setLists(sortedLists);
    } catch (err: any) {
      console.error("Error fetching lists: ", err);
      setError(err?.message || 'Could not fetch shopping lists.');
      toast({ 
        title: "Error", 
        description: "Could not fetch shopping lists.", 
        variant: "destructive" 
      });
    } finally {
      setIsLoading(false);
    }
  }, [token, user, toast, apiClient, isUnverified]);

  // Effect to handle initial list selection
  useEffect(() => {
    if (lists.length > 0 && selectedList === null) {
      const lastActiveListId = getLastActiveListId();
      const lastActiveList = lastActiveListId 
        ? lists.find((list: ShoppingList) => list.id === lastActiveListId)
        : null;
      const listToSelect = lastActiveList || lists[0];
      setSelectedList(listToSelect);
      setLastActiveListId(listToSelect.id);
    }
  }, [lists, selectedList]);

  const handleCreateList = async (name: string, description?: string) => {
    try {
      const payload: { name: string; description?: string } = { name };
      if (description) {
        payload.description = description;
      }
      
      const data = await apiClient('/api/v1/shopping-lists/', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      
      setLists(prev => [data, ...prev]);
      setSelectedList(data);
      setIsCreateListDialogOpen(false);
      
      toast({
        title: "Success",
        description: `Created "${data.name}" shopping list.`
      });
    } catch (error) {
      console.error("Error creating list: ", error);
      toast({
        title: "Error",
        description: "Could not create shopping list.",
        variant: "destructive"
      });
      throw error; // Re-throw so the dialog can handle the error
    }
  };

  const handleSelectList = (list: ShoppingList | null) => {
    if (list) {
      setSelectedList(list);
      // Persist the selected list to localStorage
      setLastActiveListId(list.id);
    } else {
      setSelectedList(null);
    }
  };

  const handleBackToSelector = () => {
    setSelectedList(null);
  };

  const handleUpdateItem = async (itemId: number, updates: Partial<Item>) => {
    if (!selectedList) return;
    
    try {
      // Track this local action BEFORE making the API call
      const actionKey = `updated-${itemId}`;
      console.log('[EnhancedDashboard] 🟢 TRACKING action before API call:', actionKey);
      trackLocalAction(actionKey);
      
      const data = await apiClient(`/api/v1/items/${itemId}`, {
        method: 'PUT',
        body: JSON.stringify(updates)
      });
      
      console.log('[EnhancedDashboard] ✅ Update action tracked, proceeding with state update');
      
      // Update the item in the selected list
      setSelectedList(prev => ({
        ...prev!,
        items: prev!.items.map(item => 
          item.id === itemId ? { ...item, ...data } : item
        )
      }));
      
      // Update the item in the lists array
      setLists(prev => prev.map(list => 
        list.id === selectedList.id 
          ? {
              ...list,
              items: list.items.map(item => 
                item.id === itemId ? { ...item, ...data } : item
              )
            }
          : list
      ));
    } catch (error) {
      console.error("Error updating item: ", error);
      toast({
        title: "Error",
        description: "Could not update item.",
        variant: "destructive"
      });
    }
  };

  const handleDeleteItem = async (itemId: number) => {
    if (!selectedList) return;
    
    try {
      // Track this local action BEFORE making the API call
      const actionKey = `deleted-${itemId}`;
      console.log('[EnhancedDashboard] 🟢 TRACKING action before API call:', actionKey);
      trackLocalAction(actionKey);
      
      await apiClient(`/api/v1/items/${itemId}`, {
        method: 'DELETE'
      });
      
      console.log('[EnhancedDashboard] ✅ Delete action tracked, proceeding with state update');
      
      // Remove the item from the selected list
      setSelectedList(prev => ({
        ...prev!,
        items: prev!.items.filter(item => item.id !== itemId)
      }));
      
      // Remove the item from the lists array
      setLists(prev => prev.map(list => 
        list.id === selectedList.id 
          ? {
              ...list,
              items: list.items.filter(item => item.id !== itemId)
            }
          : list
      ));
      
      toast({
        title: "Success",
        description: "Item deleted."
      });
    } catch (error) {
      console.error("Error deleting item: ", error);
      toast({
        title: "Error",
        description: "Could not delete item.",
        variant: "destructive"
      });
    }
  };

  const handleAddItem = async (item: ItemCreate) => {
    if (!selectedList) return;
    
    try {
      // CRITICAL: Set flag to ignore the next create WebSocket message
      console.log('[EnhancedDashboard] 🟢 Setting ignore next create flag BEFORE API call');
      ignoreNextCreate();
      
      const data = await apiClient(`/api/v1/shopping-lists/${selectedList.id}/items`, {
        method: 'POST',
        body: JSON.stringify(item)
      });
      
      // Also track with the real ID for update/delete operations
      const realActionKey = `created-${data.id}`;
      console.log('[EnhancedDashboard] 🔄 ALSO tracking with real ID for future updates:', realActionKey);
      trackLocalAction(realActionKey);
      
      console.log('[EnhancedDashboard] ✅ Create protection active, proceeding with state update');
      
      // Add the item to the selected list
      setSelectedList(prev => ({
        ...prev!,
        items: [...prev!.items, data]
      }));
      
      // Add the item to the lists array
      setLists(prev => prev.map(list => 
        list.id === selectedList.id 
          ? {
              ...list,
              items: [...list.items, data]
            }
          : list
      ));
      
      toast({
        title: "Success",
        description: `Added "${data.name}" to your list.`
      });
    } catch (error) {
      console.error("Error adding item: ", error);
      toast({
        title: "Error",
        description: "Could not add item to list.",
        variant: "destructive"
      });
    }
  };

  useEffect(() => {
    if (!authLoading) {
      fetchLists();
      
      // If user appears unverified, try to refresh their profile
      // This handles the case where they just verified and were redirected here
      if (user && !user.is_verified) {
        fetchUser();
      }
    }
  }, [authLoading, fetchLists, user, fetchUser]);

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-4 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-600">Loading your shopping lists...</p>
        </div>
      </div>
    );
  }

  if (isUnverified) {
    return <UnverifiedUserAlert user={user} token={token} />;
  }

  if (error && !isUnverified) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-700 mb-2">Error loading shopping lists</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <button
            className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition"
            onClick={() => fetchLists()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!user) {
    // No token - user is not logged in
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Please sign in</h2>
          <p className="text-slate-600">You need to be signed in to view your shopping lists.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {lists.length === 0 ? (
        <EmptyState onCreateList={() => setIsCreateListDialogOpen(true)} />
      ) : selectedList ? (
        <RealtimeShoppingList
          list={selectedList}
          allLists={lists}
          onUpdateItem={handleUpdateItem}
          onDeleteItem={handleDeleteItem}
          onAddItem={handleAddItem}
          onBackToSelector={handleBackToSelector}
          onSelectList={handleSelectList}
          onCreateList={() => setIsCreateListDialogOpen(true)}
          onListUpdate={(listId, updatedData) => {
            // Update the list in both lists array and selectedList
            setLists(prev => prev.map(list => 
              list.id === listId ? { ...list, ...updatedData } : list
            ));
            if (selectedList.id === listId) {
              setSelectedList(prev => ({ ...prev!, ...updatedData }));
            }
          }}
          onItemUpdate={(listId, item) => {
            // Update the item in both lists array and selectedList
            setLists(prev => prev.map(list => 
              list.id === listId 
                ? {
                    ...list,
                    items: list.items.map(i => i.id === item.id ? item : i)
                  }
                : list
            ));
            if (selectedList.id === listId) {
              setSelectedList(prev => ({
                ...prev!,
                items: prev!.items.map(i => i.id === item.id ? item : i)
              }));
            }
          }}
          onItemDelete={(listId, itemId) => {
            // Remove the item from both lists array and selectedList
            setLists(prev => prev.map(list => 
              list.id === listId 
                ? {
                    ...list,
                    items: list.items.filter(i => i.id !== itemId)
                  }
                : list
            ));
            if (selectedList.id === listId) {
              setSelectedList(prev => ({
                ...prev!,
                items: prev!.items.filter(i => i.id !== itemId)
              }));
            }
          }}
          onItemCreate={(listId, item) => {
            // Add the item to both lists array and selectedList
            setLists(prev => prev.map(list => 
              list.id === listId 
                ? {
                    ...list,
                    items: [...list.items, item]
                  }
                : list
            ));
            if (selectedList.id === listId) {
              setSelectedList(prev => ({
                ...prev!,
                items: [...prev!.items, item]
              }));
            }
          }}
        />
      ) : (
        <ShoppingListSelector
          lists={lists}
          currentList={selectedList}
          onSelectList={handleSelectList}
          onCreateList={() => setIsCreateListDialogOpen(true)}
          user={user}
        />
      )}

      {/* Create List Dialog */}
      <CreateListDialog
        isOpen={isCreateListDialogOpen}
        onClose={() => setIsCreateListDialogOpen(false)}
        onCreateList={handleCreateList}
      />
    </>
  );
}
