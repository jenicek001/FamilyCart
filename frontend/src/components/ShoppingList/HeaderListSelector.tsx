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

  if (!showSelector) {
    // Simple header without selector when only one list
    return (
      <div className="flex items-center gap-3">
        <span className="text-2xl">{getListIcon(currentList)}</span>
        <div>
          <h1 className="text-[#1B130D] text-xl font-bold leading-tight tracking-[-0.015em]">
            {currentList.name}
          </h1>
          <div className="text-sm text-[#8B7355] leading-tight">
            {getPendingItemsCount(currentList)} items • {getProgressPercentage(currentList)}% complete
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Current List Button with integrated selector */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 group hover:bg-[#F3ECE7]/50 rounded-lg px-2 py-1 transition-all duration-200"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <span className="text-2xl">{getListIcon(currentList)}</span>
        <div className="text-left">
          <div className="flex items-center gap-2">
            <h1 className="text-[#1B130D] text-xl font-bold leading-tight tracking-[-0.015em]">
              {currentList.name}
            </h1>
            <span className="material-icons text-[#8B7355] text-lg group-hover:text-[#ED782A] transition-colors duration-200">
              {isOpen ? 'expand_less' : 'expand_more'}
            </span>
          </div>
          <div className="text-sm text-[#8B7355] leading-tight flex items-center gap-2">
            <span>{getPendingItemsCount(currentList)} items</span>
            <span>•</span>
            <div className="flex items-center gap-1">
              <div className="w-12 h-1.5 bg-[#F3ECE7] rounded-full overflow-hidden">
                <div 
                  className="h-full bg-[#ED782A] rounded-full transition-all duration-300"
                  style={{ width: `${getProgressPercentage(currentList)}%` }}
                />
              </div>
              <span className="text-xs">{getProgressPercentage(currentList)}%</span>
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
          
          {/* Menu */}
          <div className="absolute top-full left-0 mt-2 bg-white border border-[#F3ECE7] rounded-lg shadow-lg z-20 min-w-80 max-h-80 overflow-y-auto">
            <div className="p-2">
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
                  className="w-full flex items-center gap-3 px-3 py-3 hover:bg-[#FCFAF8] rounded-lg transition-colors duration-200 text-left group"
                  role="option"
                >
                  <span className="text-lg">{getListIcon(list)}</span>
                  <div className="flex-1">
                    <div className="font-medium text-[#1B130D]">{list.name}</div>
                    <div className="text-sm text-[#8B7355] flex items-center gap-2">
                      <span>{getPendingItemsCount(list)} items</span>
                      <span>•</span>
                      <div className="flex items-center gap-1">
                        <div className="w-12 h-1.5 bg-[#F3ECE7] rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-[#ED782A] rounded-full transition-all duration-300"
                            style={{ width: `${getProgressPercentage(list)}%` }}
                          />
                        </div>
                        <span className="text-xs">{getProgressPercentage(list)}%</span>
                      </div>
                    </div>
                  </div>
                  <span className="material-icons text-[#8B7355] opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    arrow_forward
                  </span>
                </button>
              ))}

              {/* Create New List Button */}
              {onCreateList && (
                <>
                  <div className="border-t border-[#F3ECE7] my-2" />
                  <button
                    onClick={() => {
                      onCreateList();
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center gap-3 px-3 py-3 hover:bg-[#FCFAF8] rounded-lg transition-colors duration-200 text-left group"
                  >
                    <div className="w-5 h-5 rounded-full bg-[#ED782A] flex items-center justify-center">
                      <span className="material-icons text-white text-sm">add</span>
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-[#ED782A]">Create New List</div>
                      <div className="text-sm text-[#8B7355]">Start a fresh shopping list</div>
                    </div>
                    <span className="material-icons text-[#ED782A] opacity-0 group-hover:opacity-100 transition-opacity duration-200">
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
