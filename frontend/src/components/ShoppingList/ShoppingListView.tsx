"use client";

import React, { useState, useMemo } from 'react';
import { ShoppingList, Item, ItemCreate } from '../../types';
import { ShoppingListItem } from './ShoppingListItem';
import { SmartSearchBar } from './SmartSearchBar';
import { HeaderListSelector } from './HeaderListSelector';
import { useToast } from '../../hooks/use-toast';

interface ShoppingListViewProps {
  list: ShoppingList;
  allLists?: ShoppingList[];
  onUpdateItem: (itemId: number, updates: Partial<Item>) => Promise<void>;
  onDeleteItem: (itemId: number) => Promise<void>;
  onAddItem: (item: ItemCreate) => Promise<void>;
  onBackToSelector?: () => void;
  onSelectList?: (list: ShoppingList) => void;
}

export function ShoppingListView({ 
  list, 
  allLists = [],
  onUpdateItem, 
  onDeleteItem, 
  onAddItem,
  onBackToSelector,
  onSelectList 
}: ShoppingListViewProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const { toast } = useToast();

  // Group items by completion status and filter
  const { pendingItems, completedItems } = useMemo(() => {
    const filtered = list.items.filter(item => {
      const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || item.category?.name === selectedCategory;
      return matchesSearch && matchesCategory;
    });

    return {
      pendingItems: filtered.filter(item => !item.is_completed),
      completedItems: filtered.filter(item => item.is_completed),
    };
  }, [list.items, searchQuery, selectedCategory]);

  const categories = useMemo(() => {
    const cats = new Set(list.items.map(item => item.category?.name).filter((name): name is string => Boolean(name)));
    return Array.from(cats).sort();
  }, [list.items]);

  const handleToggleComplete = async (item: Item) => {
    try {
      await onUpdateItem(item.id, { is_completed: !item.is_completed });
      
      // Show toast feedback based on completion status
      const wasCompleted = item.is_completed;
      const isNowCompleted = !wasCompleted;
      
      toast({
        title: isNowCompleted ? "Item completed!" : "Item unchecked!",
        description: `"${item.name}" has been ${isNowCompleted ? 'marked as completed' : 'unchecked'}`,
        duration: 2000,
      });
    } catch (error) {
      console.error('Error toggling item completion:', error);
      toast({
        title: "Error",
        description: `Failed to update "${item.name}". Please try again.`,
        variant: "destructive",
        duration: 3000,
      });
    }
  };

  return (
    <div className="relative flex size-full min-h-screen flex-col bg-[#FCFAF8]">
      <div className="layout-container flex h-full grow flex-col">
        {/* Header - matching Stitch design */}
        <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#F3ECE7] px-4 sm:px-6 lg:px-8 py-3 sticky top-0 z-20 bg-[#FCFAF8]/80 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            {/* Back button for mobile */}
            {onBackToSelector && (
              <button
                onClick={onBackToSelector}
                className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200 lg:hidden"
                aria-label="Back to list selection"
              >
                <span className="material-icons text-2xl">arrow_back</span>
              </button>
            )}
            <div className="size-7 text-[#ED782A]">
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <path d="M44 11.2727C44 14.0109 39.8386 16.3957 33.69 17.6364C39.8386 18.877 44 21.2618 44 24C44 26.7382 39.8386 29.123 33.69 30.3636C39.8386 31.6043 44 33.9891 44 36.7273C44 40.7439 35.0457 44 24 44C12.9543 44 4 40.7439 4 36.7273C4 33.9891 8.16144 31.6043 14.31 30.3636C8.16144 29.123 4 26.7382 4 24C4 21.2618 8.16144 18.877 14.31 17.6364C8.16144 16.3957 4 14.0109 4 11.2727C4 7.25611 12.9543 4 24 4C35.0457 4 44 7.25611 44 11.2727Z" fill="currentColor"></path>
              </svg>
            </div>
            {/* Integrated List Selector */}
            <HeaderListSelector
              currentList={list}
              allLists={allLists}
              onListSelect={onSelectList || (() => {})}
            />
          </div>
          <div className="flex items-center gap-2">
            {/* Share button */}
            <button 
              className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200"
              aria-label="Share list"
            >
              <span className="material-icons text-2xl">share</span>
            </button>
            {/* User menu */}
            <div className="relative group">
              <button 
                className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200"
                aria-label="User menu"
              >
                <span className="material-icons text-2xl">person</span>
              </button>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="px-4 sm:px-6 lg:px-8 flex flex-1 justify-center py-5">
          <div className="layout-content-container flex flex-col w-full max-w-2xl flex-1">
            {/* List header with progress info */}
            <div className="flex items-center justify-between px-2 pb-4 pt-2">
              <div>
                <h2 className="text-[#1B130D] text-2xl font-bold leading-tight tracking-[-0.015em]">Shopping List</h2>
                <p className="text-sm text-gray-600 mt-1">
                  {pendingItems.length} items remaining
                  {list.members && list.members.length > 1 && (
                    <span className="ml-2">• {list.members.length} members</span>
                  )}
                </p>
              </div>
            </div>

            {/* Search/Add bar */}
            <div className="mb-4 px-2">
              <SmartSearchBar
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
                selectedCategory={selectedCategory}
                onCategoryChange={setSelectedCategory}
                categories={categories}
                onAddItem={onAddItem}
                placeholder="Search items or type to add new..."
              />
            </div>

            {/* Pending Items List */}
            {pendingItems.length > 0 && (
              <div className="space-y-2 mb-6">
                {pendingItems.map((item) => (
                  <ShoppingListItem
                    key={item.id}
                    item={item}
                    onToggleComplete={() => handleToggleComplete(item)}
                    onUpdate={(updates: Partial<Item>) => onUpdateItem(item.id, updates)}
                    onDelete={() => onDeleteItem(item.id)}
                  />
                ))}
              </div>
            )}

            {/* Completed Items */}
            {completedItems.length > 0 && (
              <div className="mt-8 pt-6 border-t border-[#F3ECE7]">
                <h3 className="text-[#1B130D] text-xl font-semibold leading-tight tracking-[-0.01em] px-2 pb-3">
                  Checked Items ({completedItems.length})
                </h3>
                <div className="space-y-2 opacity-60">
                  {completedItems.map((item) => (
                    <ShoppingListItem
                      key={item.id}
                      item={item}
                      onToggleComplete={() => handleToggleComplete(item)}
                      onUpdate={(updates: Partial<Item>) => onUpdateItem(item.id, updates)}
                      onDelete={() => onDeleteItem(item.id)}
                      isCompleted
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {pendingItems.length === 0 && completedItems.length === 0 && (
              <div className="text-center py-12">
                <div className="w-24 h-24 mx-auto mb-4 bg-slate-100 rounded-full flex items-center justify-center">
                  <span className="material-icons text-4xl text-slate-400">shopping_cart</span>
                </div>
                <h3 className="text-xl font-semibold text-slate-600 mb-2">
                  {searchQuery || selectedCategory !== 'all' ? 'No items found' : 'Your list is empty'}
                </h3>
                <p className="text-slate-500 mb-6">
                  {searchQuery || selectedCategory !== 'all' 
                    ? 'Try adjusting your search or filter'
                    : 'Use the search bar above to add items to your shopping list'
                  }
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
