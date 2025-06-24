"use client";

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import apiClient from '@/lib/api';
import type { ShoppingList, ShoppingListItem } from '@/types';
import ShoppingListCard from '@/components/shopping/ShoppingListCard';
import AddItemForm from '@/components/shopping/AddItemForm';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { useToast } from '@/hooks/use-toast';
import { PlusCircle, ListPlus, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const { user, loading: authLoading, token } = useAuth();
  const [lists, setLists] = useState<ShoppingList[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newListName, setNewListName] = useState('');
  const [isCreateListDialogOpen, setIsCreateListDialogOpen] = useState(false);
  const [listToEdit, setListToEdit] = useState<ShoppingList | null>(null);
  const [isEditListDialogOpen, setIsEditListDialogOpen] = useState(false);
  const [editedListName, setEditedListName] = useState('');

  const { toast } = useToast();
  const router = useRouter();

  const fetchLists = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      // Always use trailing slash to avoid 307 redirects losing auth headers
      const { data } = await apiClient.get<ShoppingList[]>('/api/v1/shopping-lists/');
      setLists(data.sort((a: ShoppingList, b: ShoppingList) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
    } catch (error) {
      console.error("Error fetching lists: ", error);
      toast({ title: "Error", description: "Could not fetch shopping lists.", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  }, [token, toast]);

  useEffect(() => {
    if (!authLoading) {
      if (user) {
        fetchLists();
      } else {
        router.push('/login');
      }
    }
  }, [user, authLoading, router, fetchLists]);

  const handleCreateList = async () => {
    if (!newListName.trim()) return;
    try {
      const { data: newList } = await apiClient.post<ShoppingList>('/api/v1/shopping-lists', { name: newListName });
      setLists(prev => [newList, ...prev]);
      setNewListName('');
      setIsCreateListDialogOpen(false);
      toast({ title: "List Created!", description: `\"${newListName}\" has been created.` });
    } catch (error) {
      console.error("Error creating list: ", error);
      toast({ title: "Error", description: "Could not create list.", variant: "destructive" });
    }
  };

  const handleEditList = (list: ShoppingList) => {
    setListToEdit(list);
    setEditedListName(list.name);
    setIsEditListDialogOpen(true);
  };

  const handleUpdateListName = async () => {
    if (!listToEdit || !editedListName.trim()) return;
    try {
      const { data: updatedList } = await apiClient.put<ShoppingList>(
        `/api/v1/shopping-lists/${listToEdit.id}`,
        { name: editedListName }
      );
      setLists(prev => prev.map(l => l.id === updatedList.id ? updatedList : l));
      setIsEditListDialogOpen(false);
      setListToEdit(null);
      toast({ title: "Success", description: "List name updated." });
    } catch (error) {
      console.error("Error updating list name: ", error);
      toast({ title: "Error", description: "Could not update list name.", variant: "destructive" });
    }
  };

  const handleDeleteList = async (listId: number) => {
    try {
      await apiClient.delete(`/api/v1/shopping-lists/${listId}`);
      setLists(prev => prev.filter(l => l.id !== listId));
      toast({ title: "List Deleted", description: "The shopping list has been removed." });
    } catch (error) {
      console.error("Error deleting list: ", error);
      toast({ title: "Error", description: "Could not delete list.", variant: "destructive" });
    }
  };

  const handleAddItem = async (listId: number, item: { name: string; quantity?: string; description?: string; category_name?: string; icon_name?: string }) => {
    try {
      const { data: newItem } = await apiClient.post<ShoppingListItem>(
        `/api/v1/shopping-lists/${listId}/items`,
        item,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const updatedLists = lists.map(list => {
        if (list.id === listId) {
          // Create a new items array with the new item included
          const newItems = [...(list.items || []), newItem];
          return { ...list, items: newItems };
        }
        return list;
      });
      setLists(updatedLists);
      toast({ title: "Item Added", description: `\"${item.name}\" was added to the list.` });
    } catch (error) {
      console.error("Error adding item: ", error);
      toast({ title: "Error", description: "Could not add item.", variant: "destructive" });
    }
  };

  const handleToggleItem = async (listId: number, itemId: number) => {
    const list = lists.find(l => l.id === listId);
    const item = list?.items.find(i => i.id === itemId);
    if (!item) return;

    try {
      const { data: updatedItem } = await apiClient.put<ShoppingListItem>(
        `/api/v1/items/${itemId}`,
        { is_completed: !item.is_completed }
      );
      const updatedLists = lists.map(l => {
        if (l.id === listId) {
          return { ...l, items: l.items.map(i => i.id === itemId ? updatedItem : i) };
        }
        return l;
      });
      setLists(updatedLists);
    } catch (error) {
      console.error("Error toggling item: ", error);
      toast({ title: "Error", description: "Could not update item status.", variant: "destructive" });
    }
  };

  const handleDeleteItem = async (listId: number, itemId: number) => {
    try {
      await apiClient.delete(`/api/v1/items/${itemId}`);
      const updatedLists = lists.map(l => {
        if (l.id === listId) {
          return { ...l, items: l.items.filter(i => i.id !== itemId) };
        }
        return l;
      });
      setLists(updatedLists);
      toast({ title: "Item Removed" });
    } catch (error) {
      console.error("Error deleting item: ", error);
      toast({ title: "Error", description: "Could not remove item.", variant: "destructive" });
    }
  };

  const handleShareList = async (listId: number, email: string) => {
    try {
      await apiClient.post(`/api/v1/shopping-lists/${listId}/share`, { email });
      toast({ title: "List Shared!", description: `Successfully shared with ${email}.` });
      // Optionally, refetch the list to show new members
      fetchLists();
    } catch (error) {
      console.error("Error sharing list: ", error);
      toast({ title: "Sharing Failed", description: (error as any).response?.data?.detail || "Could not share list.", variant: "destructive" });
    }
  };

  if (authLoading || isLoading) {
    return (
      <div className="flex-1 p-4 md:p-8 space-y-6">
        <div className="flex justify-between items-center">
          <div className="h-10 bg-muted rounded w-1/3 animate-pulse"></div>
          <div className="h-10 bg-muted rounded w-32 animate-pulse"></div>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="w-full shadow-lg">
              <CardHeader><div className="h-8 bg-muted rounded w-3/4 animate-pulse"></div></CardHeader>
              <CardContent><div className="h-20 bg-muted rounded animate-pulse"></div></CardContent>
              <CardFooter><div className="h-6 bg-muted rounded w-1/2 animate-pulse"></div></CardFooter>
            </Card>
          ))}
        </div>
      </div>
    );
  }
  
  if (!user) { // Should be caught by useEffect redirect, but as a fallback
     return (
      <div className="flex items-center justify-center min-h-[calc(100vh-theme(spacing.32))]">
        <p className="text-lg">Please log in to access your dashboard.</p>
         <Button onClick={() => router.push('/login')} className="ml-4">Login</Button>
      </div>
    );
  }


  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <h2 className="text-3xl font-headline font-bold">Your Shopping Lists</h2>
        <Dialog open={isCreateListDialogOpen} onOpenChange={setIsCreateListDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-accent hover:bg-accent/90 text-accent-foreground">
              <ListPlus className="mr-2 h-5 w-5" /> Create New List
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="font-headline">Create a New Shopping List</DialogTitle>
              <DialogDescription>
                Enter a name for your new list. You can invite others later.
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <Input
                type="text"
                placeholder="e.g., Weekly Groceries, Party Supplies"
                value={newListName}
                onChange={(e) => setNewListName(e.target.value)}
                className="w-full"
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateListDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleCreateList} className="bg-primary hover:bg-primary/90 text-primary-foreground">Create List</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Edit List Dialog */}
      <Dialog open={isEditListDialogOpen} onOpenChange={setIsEditListDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="font-headline">Edit Shopping List Name</DialogTitle>
              <DialogDescription>
                Update the name for &quot;{listToEdit?.name}&quot;.
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <Input
                type="text"
                value={editedListName}
                onChange={(e) => setEditedListName(e.target.value)}
                className="w-full"
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsEditListDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleUpdateListName} className="bg-primary hover:bg-primary/90 text-primary-foreground">Save Changes</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>


      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3].map(i => (
            <Card key={i} className="w-full shadow-lg">
              <CardHeader><div className="h-8 bg-muted rounded w-3/4 animate-pulse"></div></CardHeader>
              <CardContent><div className="h-20 bg-muted rounded animate-pulse"></div></CardContent>
              <CardFooter><div className="h-6 bg-muted rounded w-1/2 animate-pulse"></div></CardFooter>
            </Card>
          ))}
        </div>
      ) : lists.length === 0 ? (
        <div className="text-center py-10 border-2 border-dashed border-border rounded-lg">
          <ListPlus className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-xl font-medium text-muted-foreground">No shopping lists yet.</p>
          <p className="text-muted-foreground">Create your first list to get started!</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {lists.map((list) => (
            <ShoppingListCard
              key={list.id}
              list={list}
              currentUser={user}
              onAddItem={handleAddItem}
              onToggleItem={handleToggleItem}
              onDeleteItem={handleDeleteItem}
              onEditList={() => handleEditList(list)}
              onDeleteList={handleDeleteList}
              onShareList={handleShareList}
            />
          ))}
        </div>
      )}
    </div>
  );
}
