"use client";

import React, { useState, useMemo } from 'react';
import { Edit3 } from 'lucide-react';
import { ShoppingList, Item, ItemCreate } from '../../types';
import { ShoppingListItem } from './ShoppingListItem';
import { SmartSearchBar } from './SmartSearchBar';
import { HeaderListSelector } from './HeaderListSelector';
import { getCategoryIcon, getCategoryColorClass } from '../../utils/categories';
import { useToast } from '../../hooks/use-toast';
import { ShareDialog } from './ShareDialog';
import { RenameListDialog } from './RenameListDialog';
import { UserMenu } from './UserMenu';

interface ShoppingListViewProps {
  list: ShoppingList;
  allLists?: ShoppingList[];
  onUpdateItem: (itemId: number, updates: Partial<Item>) => Promise<void>;
  onDeleteItem: (itemId: number) => Promise<void>;
  onAddItem: (item: ItemCreate) => Promise<void>;
  onBackToSelector?: () => void;
  onSelectList?: (list: ShoppingList) => void;
  onListUpdate?: (updatedList: ShoppingList) => void;
  onCreateList?: () => void;
  connectionIndicator?: React.ReactNode;
}

export function ShoppingListView({ 
  list, 
  allLists = [],
  onUpdateItem, 
  onDeleteItem, 
  onAddItem,
  onBackToSelector,
  onSelectList,
  onListUpdate,
  onCreateList,
  connectionIndicator
}: ShoppingListViewProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
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
                <span className="material-icons text-lg">arrow_back</span>
              </button>
            )}
            {/* Integrated List Selector - moved right with increased left margin */}
            <div className="ml-4">
              <HeaderListSelector
                currentList={list}
                allLists={allLists}
                onListSelect={onSelectList || (() => {})}
                onCreateList={onCreateList}
              />
            </div>
          </div>
          <div className="flex items-center gap-3 mr-4">
            {/* Connection status indicator */}
            {connectionIndicator && (
              <div className="flex items-center">
                {connectionIndicator}
              </div>
            )}
            
            {/* Rename button */}
            <button 
              onClick={() => setIsRenameDialogOpen(true)}
              className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200"
              aria-label="Rename list"
            >
              <Edit3 className="h-5 w-5" />
            </button>
            {/* Share button */}
            <button 
              onClick={() => setIsShareDialogOpen(true)}
              className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200"
              aria-label="Share list"
            >
              <span className="material-icons text-lg">share</span>
            </button>
            {/* User menu */}
            <div className="flex items-center">
              <UserMenu
                isOpen={isUserMenuOpen}
                onClose={() => setIsUserMenuOpen(false)}
                onToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
              />
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
                  {Object.values(pendingItemsByCategory).flat().length} items remaining
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

            {/* Pending Items List - Grouped by Category */}
            {Object.keys(pendingItemsByCategory).length > 0 && (
              <div className="space-y-6 mb-6">
                {allCategories.filter(categoryName => pendingItemsByCategory[categoryName]?.length > 0).map((categoryName) => (
                  <div key={categoryName} className="space-y-3">
                    {/* Category Header */}
                    <div className="flex items-center gap-3 px-2 py-2 bg-white rounded-lg border border-[#F3ECE7]">
                      <div className={`flex items-center justify-center rounded-lg shrink-0 size-8 ${getCategoryColorClass(categoryName)}`}>
                        <span className="material-icons text-lg">{getCategoryIcon(categoryName)}</span>
                      </div>
                      <div>
                        <h3 className="text-[#1B130D] font-semibold text-lg">{categoryName}</h3>
                        <p className="text-sm text-gray-600">
                          {pendingItemsByCategory[categoryName].length} item{pendingItemsByCategory[categoryName].length !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                    
                    {/* Items in this category */}
                    <div className="space-y-2 pl-4">
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
              <div className="mt-8 pt-6 border-t border-[#F3ECE7]">
                <h3 className="text-[#1B130D] text-xl font-semibold leading-tight tracking-[-0.01em] px-2 pb-3">
                  Checked Items ({Object.values(completedItemsByCategory).flat().length})
                </h3>
                <div className="space-y-4 opacity-60">
                  {allCategories.filter(categoryName => completedItemsByCategory[categoryName]?.length > 0).map((categoryName) => (
                    <div key={`completed-${categoryName}`} className="space-y-2">
                      {/* Category Header for completed items */}
                      <div className="flex items-center gap-3 px-2 py-1">
                        <div className={`flex items-center justify-center rounded-lg shrink-0 size-6 ${getCategoryColorClass(categoryName)} opacity-50`}>
                          <span className="material-icons text-sm">{getCategoryIcon(categoryName)}</span>
                        </div>
                        <h4 className="text-sm font-medium text-gray-500">{categoryName}</h4>
                      </div>
                      
                      {/* Completed items in this category */}
                      <div className="space-y-2 pl-4">
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

      {/* Share Dialog */}
      <ShareDialog
        isOpen={isShareDialogOpen}
        onClose={() => setIsShareDialogOpen(false)}
        list={list}
        onListUpdate={onListUpdate}
      />

      {/* Rename Dialog */}
      <RenameListDialog
        isOpen={isRenameDialogOpen}
        onClose={() => setIsRenameDialogOpen(false)}
        list={list}
        onListUpdate={onListUpdate}
      />
    </div>
  );
}
