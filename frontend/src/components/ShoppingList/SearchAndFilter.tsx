import React, { useState, useRef, useEffect } from 'react';
import { getAllCategories } from '../../utils/categories';

interface SearchAndFilterProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  categories: string[];
}

export function SearchAndFilter({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  categories
}: SearchAndFilterProps) {
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);

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

  const allCategories = getAllCategories();
  const availableCategories = categories.length > 0 ? categories : allCategories.map(c => c.name.toLowerCase());

  return (
    <div className="flex flex-col sm:flex-row gap-4">
      {/* Search Bar */}
      <div className="relative flex-1">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <span className="material-icons text-slate-400 text-sm">search</span>
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search items..."
          className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors bg-white shadow-soft"
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <span className="material-icons text-slate-400 hover:text-slate-600 text-sm">clear</span>
          </button>
        )}
      </div>

      {/* Filter Dropdown */}
      <div className="relative" ref={filterRef}>
        <button
          onClick={() => setIsFilterOpen(!isFilterOpen)}
          className={`inline-flex items-center px-4 py-2.5 border rounded-xl font-medium transition-colors shadow-soft ${
            selectedCategory === 'all'
              ? 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
              : 'border-primary-300 bg-primary-50 text-primary-700 hover:bg-primary-100'
          }`}
        >
          <span className="material-icons text-sm mr-2">filter_list</span>
          <span className="hidden sm:inline">
            {selectedCategory === 'all' ? 'All Categories' : selectedCategory}
          </span>
          <span className="sm:hidden">Filter</span>
          <span className={`material-icons text-sm ml-2 transition-transform ${
            isFilterOpen ? 'rotate-180' : ''
          }`}>
            keyboard_arrow_down
          </span>
        </button>

        {/* Dropdown Menu */}
        {isFilterOpen && (
          <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-strong border border-slate-200 z-20 animate-slide-up">
            <div className="py-2">
              <button
                onClick={() => {
                  onCategoryChange('all');
                  setIsFilterOpen(false);
                }}
                className={`w-full flex items-center px-4 py-2 text-left hover:bg-slate-50 transition-colors ${
                  selectedCategory === 'all' ? 'bg-primary-50 text-primary-700' : 'text-slate-700'
                }`}
              >
                <span className="material-icons text-sm mr-3">grid_view</span>
                All Categories
                {selectedCategory === 'all' && (
                  <span className="material-icons text-sm ml-auto text-primary-600">check</span>
                )}
              </button>

              <div className="border-t border-slate-100 my-2"></div>

              {availableCategories.map((category) => {
                const categoryConfig = allCategories.find(c => 
                  c.name.toLowerCase() === category.toLowerCase()
                );
                
                return (
                  <button
                    key={category}
                    onClick={() => {
                      onCategoryChange(category);
                      setIsFilterOpen(false);
                    }}
                    className={`w-full flex items-center px-4 py-2 text-left hover:bg-slate-50 transition-colors ${
                      selectedCategory === category ? 'bg-primary-50 text-primary-700' : 'text-slate-700'
                    }`}
                  >
                    {categoryConfig && (
                      <span 
                        className="material-icons text-sm mr-3"
                        style={{ color: categoryConfig.color }}
                      >
                        {categoryConfig.icon}
                      </span>
                    )}
                    <span className="capitalize">
                      {categoryConfig?.name || category}
                    </span>
                    {selectedCategory === category && (
                      <span className="material-icons text-sm ml-auto text-primary-600">check</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Clear Filters */}
      {(searchQuery || selectedCategory !== 'all') && (
        <button
          onClick={() => {
            onSearchChange('');
            onCategoryChange('all');
          }}
          className="inline-flex items-center px-3 py-2.5 text-slate-600 hover:text-slate-800 transition-colors"
          title="Clear all filters"
        >
          <span className="material-icons text-sm">clear_all</span>
          <span className="hidden sm:inline ml-1">Clear</span>
        </button>
      )}
    </div>
  );
}
