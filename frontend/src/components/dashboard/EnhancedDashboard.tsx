"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useWebSocketContext } from '@/contexts/WebSocketContext';
import { useApiClient } from '@/hooks/use-api-client';
import axios from 'axios';
import type { ShoppingList, Item, ItemCreate } from '@/types';
import { ShoppingListSelector } from '@/components/ShoppingList/ShoppingListSelector';
import { RealtimeShoppingList } from '@/components/ShoppingList/RealtimeShoppingList';
import { EmptyState } from '@/components/ShoppingList/EmptyState';
import { CreateListDialog } from '@/components/ShoppingList/CreateListDialog';
import { useToast } from '@/hooks/use-toast';
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
  const [resending, setResending] = useState(false);
  const [resendMessage, setResendMessage] = useState('');

  const { toast } = useToast();

  const fetchLists = useCallback(async () => {
    if (!token || !user) {
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
      // Only set selectedList if it is not already set
      if (selectedList === null && sortedLists.length > 0) {
        const lastActiveListId = getLastActiveListId();
        const lastActiveList = lastActiveListId 
          ? sortedLists.find((list: ShoppingList) => list.id === lastActiveListId)
          : null;
        const listToSelect = lastActiveList || sortedLists[0];
        setSelectedList(listToSelect);
        setLastActiveListId(listToSelect.id);
      }
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
  }, [token, user, toast, apiClient]);

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
      console.log('[EnhancedDashboard] � Setting ignore next create flag BEFORE API call');
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
    // Only depend on authLoading to avoid infinite loop from fetchLists
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading]);

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

  if (error) {
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

  // Check if user is logged in but not verified
  // We check both cases:
  // 1. user object exists but is_verified is false (new behavior with backend fix)
  // 2. user object is null but token exists (legacy behavior if backend returns 403)
  const isUnverified = (user && !user.is_verified) || (!user && token);

  if (isUnverified) {
      const handleResendEmail = async () => {
        setResending(true);
        setResendMessage('');
        try {
          let email = '';
          
          // Try to get email from user object first (reliable)
          if (user?.email) {
            email = user.email;
          } 
          // Fallback: try to extract from token (unreliable if token only has sub)
          else {
            try {
              if (token) {
                const parts = token.split('.');
                if (parts.length === 3) {
                  // Handle base64url format
                  const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
                  const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                  }).join(''));
                  const payload = JSON.parse(jsonPayload);
                  email = payload.sub || payload.email; 
                }
              }
            } catch (e) {
              console.error("Failed to decode token", e);
            }
          }

          if (!email) {
             throw new Error("Could not determine email address. Please sign out and sign in again.");
          }

          // Check if email looks like a UUID (which happens if sub is used as email)
          // Simple regex for UUID: 8-4-4-4-12 hex digits
          const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
          if (uuidRegex.test(email)) {
             throw new Error("Cannot verify email: Session contains ID instead of email. Please sign out and sign in again.");
          }

          await axios.post('/api/v1/auth/verify/request-verify-token', 
            { email },
            { headers: { Authorization: `Bearer ${token}` } }
          );
          setResendMessage('Verification email sent! Please check your inbox.');
        } catch (error: any) {
          console.error("Resend email error:", error);
          let msg = 'Failed to resend email. Please try again.';
          
          if (error.response?.data?.detail) {
             const detail = error.response.data.detail;
             if (Array.isArray(detail)) {
                 // Handle Pydantic validation error
                 msg = detail.map((e: any) => `${e.loc.join('.')}: ${e.msg}`).join(', ');
             } else if (typeof detail === 'string') {
                 msg = detail;
             } else {
                 msg = JSON.stringify(detail);
             }
          } else if (error.message) {
             msg = error.message;
          }
          setResendMessage(msg);
        } finally {
          setResending(false);
        }
      };

      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-8 bg-white rounded-lg shadow-lg">
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-3">Verify Your Email</h2>
            <p className="text-slate-600 mb-4">
              We've sent a verification email to your inbox. Please check your email and click the verification link to access your shopping lists.
            </p>
            <p className="text-sm text-slate-500 mb-4">
              Didn't receive the email? Check your spam folder.
            </p>
            <button
              onClick={handleResendEmail}
              disabled={resending}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {resending ? 'Sending...' : 'Resend Verification Email'}
            </button>
            {resendMessage && (
              <p className={`mt-4 text-sm ${resendMessage.includes('sent') ? 'text-green-600' : 'text-red-600'}`}>
                {resendMessage}
              </p>
            )}
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
