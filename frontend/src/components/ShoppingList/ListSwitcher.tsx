"use client";

import React, { useState } from 'react';
import { ShoppingList } from '../../types';

interface ListSwitcherProps {
  currentList: ShoppingList;
  allLists: ShoppingList[];
  onListSelect: (list: ShoppingList) => void;
}

export function ListSwitcher({ currentList, allLists, onListSelect }: ListSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Only show if there are multiple lists
  if (allLists.length <= 1) {
    return null;
  }

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

  const otherLists = allLists.filter(list => list.id !== currentList.id);

  return (
    <div className="relative">
      {/* Current List Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 px-4 py-2 bg-white border border-[#F3ECE7] rounded-lg hover:bg-[#FCFAF8] transition-colors duration-200 shadow-sm"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <span className="text-xl">{getListIcon(currentList)}</span>
        <div className="flex-1 text-left">
          <div className="font-medium text-[#1B130D]">{currentList.name}</div>
          <div className="text-sm text-[#8B7355]">
            {currentList.items.length} items • {getProgressPercentage(currentList)}% complete
          </div>
        </div>
        <span className="material-icons text-[#8B7355]">
          {isOpen ? 'expand_less' : 'expand_more'}
        </span>
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
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-[#F3ECE7] rounded-lg shadow-lg z-20 max-h-80 overflow-y-auto">
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
                  className="w-full flex items-center gap-3 px-3 py-3 hover:bg-[#FCFAF8] rounded-lg transition-colors duration-200 text-left"
                  role="option"
                >
                  <span className="text-lg">{getListIcon(list)}</span>
                  <div className="flex-1">
                    <div className="font-medium text-[#1B130D]">{list.name}</div>
                    <div className="text-sm text-[#8B7355] flex items-center gap-2">
                      <span>{list.items.length} items</span>
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
                  <span className="material-icons text-[#8B7355] opacity-0 group-hover:opacity-100">
                    arrow_forward
                  </span>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
