"use client";

import React, { useState } from 'react';
import { ShoppingList } from '../../types';

interface HeaderListSelectorProps {
  currentList: ShoppingList;
  allLists: ShoppingList[];
  onListSelect: (list: ShoppingList) => void;
  onCreateList?: () => void;
}

export function HeaderListSelector({ currentList, allLists, onListSelect, onCreateList }: HeaderListSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const getListIcon = (list: ShoppingList) => {
    // Default icons until AI generation is implemented
    const defaultIcons = ['🛒', '🏪', '📝', '🛍️', '📋', '🥕', '🏠', '💼'];
    return list.icon || defaultIcons[list.id % defaultIcons.length];
  };

  const getProgressPercentage = (list: ShoppingList) => {
    if (list.items.length === 0) return 0;
    const completedItems = list.items.filter(item => item.is_completed).length;
    return Math.round((completedItems / list.items.length) * 100);
  };

  const getPendingItemsCount = (list: ShoppingList) => {
    return list.items.filter(item => !item.is_completed).length;
  };

  const otherLists = allLists.filter(list => list.id !== currentList.id);
  const showSelector = allLists.length > 1;

  // Always show selector button on mobile for better UX, even with single list
  // This allows users to access the "Create New List" functionality easily
  const showMobileSelector = allLists.length >= 1 && onCreateList;

  if (!showSelector && !showMobileSelector) {
    // Simple header without any selector functionality
    return (
      <div className="flex items-center gap-2 sm:gap-3">
        <span className="text-base sm:text-2xl flex-shrink-0">{getListIcon(currentList)}</span>
        <div className="min-w-0 flex-1">
          <h1 className="text-[#1B130D] text-sm sm:text-xl font-bold leading-tight tracking-[-0.015em] truncate">
            {currentList.name}
          </h1>
          <div className="text-xs sm:text-sm text-[#8B7355] leading-tight">
            {getPendingItemsCount(currentList)} items • {getProgressPercentage(currentList)}% complete
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full">
      {/* Current List Button with integrated selector */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 sm:gap-2 group hover:bg-[#F3ECE7]/50 rounded-lg px-1 sm:px-2 py-1 transition-all duration-200 w-full min-w-0"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <span className="text-base sm:text-xl flex-shrink-0">{getListIcon(currentList)}</span>
        <div className="text-left min-w-0 flex-1">
          <div className="flex items-center gap-1 justify-between w-full">
            <h1 className="text-[#1B130D] text-sm sm:text-lg font-bold leading-tight tracking-[-0.015em] truncate">
              {currentList.name}
            </h1>
            <span className="material-icons text-[#8B7355] text-sm sm:text-base group-hover:text-[#ED782A] transition-colors duration-200 flex-shrink-0 ml-1">
              {isOpen ? 'expand_less' : 'expand_more'}
            </span>
          </div>
          {/* Mobile-optimized progress section */}
          <div className="text-xs sm:text-sm text-[#8B7355] leading-tight">
            <div className="flex items-center gap-2 sm:gap-2">
              <span className="whitespace-nowrap">{getPendingItemsCount(currentList)} items</span>
              <div className="flex items-center gap-1 min-w-0 flex-1">
                <div className="w-8 sm:w-12 h-1.5 sm:h-2 bg-[#F3ECE7] rounded-full overflow-hidden flex-shrink-0">
                  <div 
                    className="h-full bg-[#ED782A] rounded-full transition-all duration-300"
                    style={{ width: `${getProgressPercentage(currentList)}%` }}
                  />
                </div>
                <span className="text-xs font-medium whitespace-nowrap">{getProgressPercentage(currentList)}%</span>
              </div>
            </div>
          </div>
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Menu - Responsive positioning and sizing */}
          <div className="absolute top-full left-0 right-0 mt-1 sm:mt-2 bg-white border border-[#F3ECE7] rounded-lg shadow-lg z-20 w-screen max-w-sm sm:max-w-md max-h-[70vh] sm:max-h-80 overflow-y-auto
                         sm:left-0 sm:right-auto sm:w-80">
            <div className="p-2">
              {/* Only show "Switch to" section if there are other lists */}
              {showSelector && (
                <>
                  <div className="text-xs font-medium text-[#8B7355] px-3 py-2 uppercase tracking-wide">
                    Switch to
                  </div>
                  
                  {otherLists.map((list) => (
                    <button
                      key={list.id}
                      onClick={() => {
                        onListSelect(list);
                        setIsOpen(false);
                      }}
                      className="w-full flex items-center gap-2 sm:gap-3 px-2 sm:px-3 py-3 hover:bg-[#FCFAF8] rounded-lg transition-colors duration-200 text-left group"
                      role="option"
                    >
                      <span className="text-base sm:text-lg flex-shrink-0">{getListIcon(list)}</span>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-[#1B130D] truncate">{list.name}</div>
                        <div className="text-sm text-[#8B7355] flex items-center gap-1 sm:gap-2">
                          <span className="whitespace-nowrap">{getPendingItemsCount(list)} items</span>
                          <span className="hidden sm:inline">•</span>
                          <div className="flex items-center gap-1 min-w-0">
                            <div className="w-8 sm:w-12 h-1 sm:h-1.5 bg-[#F3ECE7] rounded-full overflow-hidden flex-shrink-0">
                              <div 
                                className="h-full bg-[#ED782A] rounded-full transition-all duration-300"
                                style={{ width: `${getProgressPercentage(list)}%` }}
                              />
                            </div>
                            <span className="text-xs whitespace-nowrap">{getProgressPercentage(list)}%</span>
                          </div>
                        </div>
                      </div>
                      <span className="material-icons text-[#8B7355] opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex-shrink-0 text-base sm:text-lg">
                        arrow_forward
                      </span>
                    </button>
                  ))}
                </>
              )}

              {/* Create New List Button - Always show if onCreateList is available */}
              {onCreateList && (
                <>
                  {showSelector && <div className="border-t border-[#F3ECE7] my-2" />}
                  {!showSelector && (
                    <div className="text-xs font-medium text-[#8B7355] px-3 py-2 uppercase tracking-wide">
                      Options
                    </div>
                  )}
                  <button
                    onClick={() => {
                      onCreateList();
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center gap-2 sm:gap-3 px-2 sm:px-3 py-3 hover:bg-[#FCFAF8] rounded-lg transition-colors duration-200 text-left group"
                  >
                    <div className="w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-[#ED782A] flex items-center justify-center flex-shrink-0">
                      <span className="material-icons text-white text-xs sm:text-sm">add</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-[#ED782A] text-sm sm:text-base">Create New List</div>
                      <div className="text-xs sm:text-sm text-[#8B7355] truncate">Start a fresh shopping list</div>
                    </div>
                    <span className="material-icons text-[#ED782A] opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex-shrink-0 text-base sm:text-lg">
                      arrow_forward
                    </span>
                  </button>
                </>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
