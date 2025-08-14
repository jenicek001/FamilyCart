"use client";

import React, { useState, useRef, useEffect } from 'react';
import { getAllCategories, inferCategory } from '../../utils/categories';
import { ItemCreate } from '../../types';

interface SmartSearchBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  categories: string[];
  onAddItem?: (item: ItemCreate) => Promise<void>;
  placeholder?: string;
}

export function SmartSearchBar({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  categories,
  onAddItem,
  placeholder = "Search items or type to add new..."
}: SmartSearchBarProps) {
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [showAddSuggestion, setShowAddSuggestion] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Close filter dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (filterRef.current && !filterRef.current.contains(event.target as Node)) {
        setIsFilterOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Show add suggestion when typing something that's not just a search
  useEffect(() => {
    if (searchQuery.length > 2 && onAddItem) {
      setShowAddSuggestion(true);
    } else {
      setShowAddSuggestion(false);
    }
  }, [searchQuery, onAddItem]);

  const allCategories = getAllCategories();
  const availableCategories = categories.length > 0 ? categories : allCategories.map(c => c.name.toLowerCase());

  const handleAddItemFromSearch = async () => {
    if (!onAddItem || !searchQuery.trim()) return;

    const suggestedCategory = inferCategory(searchQuery);
    
    await onAddItem({
      name: searchQuery.trim(),
      quantity: '1',
      category_name: suggestedCategory,
      description: null,
      icon_name: null
    });

    onSearchChange('');
    setShowAddSuggestion(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && showAddSuggestion) {
      handleAddItemFromSearch();
    }
  };

  return (
    <div className="relative">
      <span className="material-icons absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">search</span>
      <input 
        ref={inputRef}
        type="text"
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        onKeyDown={handleKeyPress}
        placeholder={placeholder}
        className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[#E7D9CF] bg-white text-[#1B130D] placeholder-gray-400 focus:ring-2 focus:ring-[#ED782A]/50 focus:border-[#ED782A] focus:outline-none shadow-sm hover:shadow-md transition-shadow"
      />
      
      {/* Add Item Suggestion */}
      {showAddSuggestion && onAddItem && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-[#E7D9CF] rounded-lg shadow-lg z-30 p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="material-icons text-[#ED782A] text-sm mr-2">add_circle</span>
              <div>
                <p className="text-sm font-medium text-[#1B130D]">
                  Add "{searchQuery}"
                </p>
                <p className="text-xs text-gray-600">
                  Category: {inferCategory(searchQuery)}
                </p>
              </div>
            </div>
            <button
              onClick={handleAddItemFromSearch}
              className="px-3 py-1.5 bg-[#ED782A] text-white rounded-lg hover:bg-[#D66A25] transition-colors text-sm font-medium"
            >
              Add
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
