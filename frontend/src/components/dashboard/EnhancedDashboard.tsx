"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/lib/api';
import type { ShoppingList, Item } from '@/types';
import { ShoppingListSelector } from '@/components/ShoppingList/ShoppingListSelector';
import { ShoppingListView } from '@/components/ShoppingList/ShoppingListView';
import { EmptyState } from '@/components/ShoppingList/EmptyState';
import { useToast } from '@/hooks/use-toast';
import { setLastActiveListId, getLastActiveListId } from '@/utils/localStorage';

export default function EnhancedDashboard() {
  const { user, loading: authLoading, token } = useAuth();
  const [lists, setLists] = useState<ShoppingList[]>([]);
  const [selectedList, setSelectedList] = useState<ShoppingList | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [newListName, setNewListName] = useState('');
  const [isCreateListDialogOpen, setIsCreateListDialogOpen] = useState(false);

  const { toast } = useToast();

  const fetchLists = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const { data } = await apiClient.get<ShoppingList[]>('/api/v1/shopping-lists/');
      const sortedLists = data.sort((a: ShoppingList, b: ShoppingList) => 
        new Date(b.updated_at).getTime() - new Date(a.created_at).getTime()
      );
      setLists(sortedLists);
      
      // Try to restore the last active list from localStorage
      if (!selectedList && sortedLists.length > 0) {
        const lastActiveListId = getLastActiveListId();
        const lastActiveList = lastActiveListId 
          ? sortedLists.find(list => list.id === lastActiveListId)
          : null;
        
        // Use last active list if found, otherwise use most recently updated
        const listToSelect = lastActiveList || sortedLists[0];
        setSelectedList(listToSelect);
        
        // Save the selected list to localStorage
        setLastActiveListId(listToSelect.id);
      }
    } catch (error) {
      console.error("Error fetching lists: ", error);
      toast({ 
        title: "Error", 
        description: "Could not fetch shopping lists.", 
        variant: "destructive" 
      });
    } finally {
      setIsLoading(false);
    }
  }, [token, toast, selectedList]);

  const handleCreateList = async () => {
    if (!newListName.trim()) return;
    
    try {
      const { data } = await apiClient.post<ShoppingList>('/api/v1/shopping-lists/', {
        name: newListName.trim()
      });
      
      setLists(prev => [data, ...prev]);
      setSelectedList(data);
      setNewListName('');
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
    }
  };

  const handleSelectList = (list: ShoppingList) => {
    setSelectedList(list);
    // Persist the selected list to localStorage
    setLastActiveListId(list.id);
  };

  const handleBackToSelector = () => {
    setSelectedList(null);
  };

  const handleUpdateItem = async (itemId: number, updates: Partial<Item>) => {
    if (!selectedList) return;
    
    try {
      const { data } = await apiClient.put<Item>(`/api/v1/items/${itemId}`, updates);
      
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
      await apiClient.delete(`/api/v1/items/${itemId}`);
      
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

  const handleAddItem = async (item: Omit<Item, 'id' | 'created_at' | 'updated_at'>) => {
    if (!selectedList) return;
    
    try {
      const { data } = await apiClient.post<Item>(`/api/v1/shopping-lists/${selectedList.id}/items/`, {
        name: item.name,
        quantity: item.quantity?.toString() || null,
        description: item.description || null,
        category_name: item.category?.name || null  // Send category_name instead of category_id
      });
      
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
    }
  }, [authLoading, fetchLists]);

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

  if (!user) {
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
        <ShoppingListView
          list={selectedList}
          allLists={lists}
          onUpdateItem={handleUpdateItem}
          onDeleteItem={handleDeleteItem}
          onAddItem={handleAddItem}
          onBackToSelector={handleBackToSelector}
          onSelectList={handleSelectList}
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
      {isCreateListDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-strong max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Create New Shopping List</h3>
            <input
              type="text"
              value={newListName}
              onChange={(e) => setNewListName(e.target.value)}
              placeholder="Enter list name..."
              className="w-full px-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors mb-4"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreateList();
                if (e.key === 'Escape') setIsCreateListDialogOpen(false);
              }}
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setIsCreateListDialogOpen(false)}
                className="px-4 py-2 text-slate-600 hover:text-slate-800 hover:bg-slate-50 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateList}
                disabled={!newListName.trim()}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Create List
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
