"use client";

import React, { useState, useMemo } from 'react';
import { ShoppingList, Item, ItemCreate } from '../../types';
import { ShoppingListItem } from './ShoppingListItem';
import { SmartSearchBar } from './SmartSearchBar';
import { getCategoryIcon, getCategoryColorClass } from '../../utils/categories';
import { useToast } from '../../hooks/use-toast';

interface ShoppingListViewProps {
  list: ShoppingList;
  onUpdateItem: (itemId: number, updates: Partial<Item>) => Promise<void>;
  onDeleteItem: (itemId: number) => Promise<void>;
  onAddItem: (item: ItemCreate) => Promise<void>;
}

export function ShoppingListView({ 
  list, 
  onUpdateItem, 
  onDeleteItem, 
  onAddItem
}: ShoppingListViewProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const { toast } = useToast();

  // Group items by completion status and category, then filter
  const { pendingItemsByCategory, completedItemsByCategory, allCategories } = useMemo(() => {
    const filtered = list.items.filter(item => {
      const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || item.category?.name === selectedCategory;
      return matchesSearch && matchesCategory;
    });

    const pending = filtered.filter(item => !item.is_completed);
    const completed = filtered.filter(item => item.is_completed);

    // Group pending items by category
    const pendingByCategory = pending.reduce((acc, item) => {
      const categoryName = item.category?.name || 'Other';
      if (!acc[categoryName]) {
        acc[categoryName] = [];
      }
      acc[categoryName].push(item);
      return acc;
    }, {} as Record<string, Item[]>);

    // Group completed items by category 
    const completedByCategory = completed.reduce((acc, item) => {
      const categoryName = item.category?.name || 'Other';
      if (!acc[categoryName]) {
        acc[categoryName] = [];
      }
      acc[categoryName].push(item);
      return acc;
    }, {} as Record<string, Item[]>);

    // Get all unique categories from all items
    const allCats = new Set(list.items.map(item => item.category?.name || 'Other'));
    const sortedCategories = Array.from(allCats).sort((a, b) => {
      // Put "Other" category at the end
      if (a === 'Other' && b !== 'Other') return 1;
      if (b === 'Other' && a !== 'Other') return -1;
      return a.localeCompare(b);
    });

    return {
      pendingItemsByCategory: pendingByCategory,
      completedItemsByCategory: completedByCategory,
      allCategories: sortedCategories
    };
  }, [list.items, searchQuery, selectedCategory]);

  const categories = useMemo(() => {
    // Extract unique category names from all categories we found
    return allCategories.filter((name): name is string => Boolean(name));
  }, [allCategories]);

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
    <div className="w-full max-w-2xl mx-auto">
      <div className="px-2 sm:px-4 lg:px-8">
        {/* List header with progress info */}
        <div className="flex items-center justify-between px-1 sm:px-2 pb-3 sm:pb-4 pt-1 sm:pt-2">
          <div className="min-w-0 flex-1">
            <h2 className="text-[#1B130D] text-lg sm:text-2xl font-bold leading-tight tracking-[-0.015em]">Shopping List</h2>
            <p className="text-xs sm:text-sm text-gray-600 mt-1">
              {Object.values(pendingItemsByCategory).flat().length} items remaining
              {list.members && list.members.length > 1 && (
                <span className="ml-2 hidden sm:inline">• {list.members.length} members</span>
              )}
            </p>
          </div>
        </div>

        {/* Search/Add bar */}
        <div className="mb-3 sm:mb-4 px-1 sm:px-2">
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

        {/* Pending Items List - Grouped by Category */}
        {Object.keys(pendingItemsByCategory).length > 0 && (
          <div className="space-y-4 sm:space-y-6 mb-4 sm:mb-6">
            {allCategories.filter(categoryName => pendingItemsByCategory[categoryName]?.length > 0).map((categoryName) => (
              <div key={categoryName} className="space-y-2 sm:space-y-3">
                {/* Category Header */}
                <div className="flex items-center gap-2 sm:gap-3 px-2 py-2 bg-white rounded-lg border border-[#F3ECE7]">
                  <div className={`flex items-center justify-center rounded-lg shrink-0 size-6 sm:size-8 ${getCategoryColorClass(categoryName)}`}>
                    <span className="material-icons text-base sm:text-lg">{getCategoryIcon(categoryName)}</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-[#1B130D] font-semibold text-base sm:text-lg truncate">{categoryName}</h3>
                    <p className="text-xs sm:text-sm text-gray-600">
                      {pendingItemsByCategory[categoryName].length} item{pendingItemsByCategory[categoryName].length !== 1 ? 's' : ''}
                    </p>
                  </div>
                </div>
                
                {/* Items in this category */}
                <div className="space-y-2 pl-2 sm:pl-4">
                  {pendingItemsByCategory[categoryName].map((item: Item) => (
                    <ShoppingListItem
                      key={item.id}
                      item={item}
                      onToggleComplete={() => handleToggleComplete(item)}
                      onUpdate={(updates: Partial<Item>) => onUpdateItem(item.id, updates)}
                      onDelete={() => onDeleteItem(item.id)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Completed Items - Grouped by Category */}
        {Object.keys(completedItemsByCategory).length > 0 && (
          <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-[#F3ECE7]">
            <h3 className="text-[#1B130D] text-lg sm:text-xl font-semibold leading-tight tracking-[-0.01em] px-1 sm:px-2 pb-2 sm:pb-3">
              Checked Items ({Object.values(completedItemsByCategory).flat().length})
            </h3>
            <div className="space-y-3 sm:space-y-4 opacity-60">
              {allCategories.filter(categoryName => completedItemsByCategory[categoryName]?.length > 0).map((categoryName) => (
                <div key={`completed-${categoryName}`} className="space-y-2">
                  {/* Category Header for completed items */}
                  <div className="flex items-center gap-2 sm:gap-3 px-1 sm:px-2 py-1">
                    <div className={`flex items-center justify-center rounded-lg shrink-0 size-5 sm:size-6 ${getCategoryColorClass(categoryName)} opacity-50`}>
                      <span className="material-icons text-xs sm:text-sm">{getCategoryIcon(categoryName)}</span>
                    </div>
                    <h4 className="text-xs sm:text-sm font-medium text-gray-500 truncate">{categoryName}</h4>
                  </div>
                  
                  {/* Completed items in this category */}
                  <div className="space-y-2 pl-2 sm:pl-4">
                    {completedItemsByCategory[categoryName].map((item: Item) => (
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
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {Object.keys(pendingItemsByCategory).length === 0 && Object.keys(completedItemsByCategory).length === 0 && (
          <div className="text-center py-8 sm:py-12">
            <div className="w-16 h-16 sm:w-24 sm:h-24 mx-auto mb-3 sm:mb-4 bg-slate-100 rounded-full flex items-center justify-center">
              <span className="material-icons text-2xl sm:text-4xl text-slate-400">shopping_cart</span>
            </div>
            <h3 className="text-lg sm:text-xl font-semibold text-slate-600 mb-2">
              {searchQuery || selectedCategory !== 'all' ? 'No items found' : 'Your list is empty'}
            </h3>
            <p className="text-sm sm:text-base text-slate-500 mb-4 sm:mb-6 px-4">
              {searchQuery || selectedCategory !== 'all' 
                ? 'Try adjusting your search or filter'
                : 'Use the search bar above to add items to your shopping list'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
