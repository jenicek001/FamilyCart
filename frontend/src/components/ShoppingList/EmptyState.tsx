"use client";

import React from 'react';

interface EmptyStateProps {
  onCreateList: () => void;
}

export function EmptyState({ onCreateList }: EmptyStateProps) {
  return (
    <div className="min-h-screen bg-[#FCFAF8] flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        {/* Icon */}
        <div className="mb-6">
          <div className="w-20 h-20 mx-auto bg-[#F3ECE7] rounded-2xl flex items-center justify-center">
            <span className="material-icons text-4xl text-[#8B7355]">shopping_cart</span>
          </div>
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-[#1B130D] mb-3">
          Welcome to FamilyCart
        </h2>

        {/* Description */}
        <p className="text-[#8B7355] mb-8 leading-relaxed">
          Start organizing your shopping with your first list. Add items, share with family, 
          and make grocery shopping a breeze.
        </p>

        {/* Create Button */}
        <button
          onClick={onCreateList}
          className="inline-flex items-center gap-2 px-6 py-3 bg-[#ED782A] text-white rounded-lg hover:bg-[#E06A1F] transition-colors duration-200 font-medium shadow-sm"
        >
          <span className="material-icons">add</span>
          Create Your First List
        </button>

        {/* Features Preview */}
        <div className="mt-12 space-y-4">
          <div className="flex items-center gap-3 text-left">
            <div className="w-8 h-8 bg-[#F3ECE7] rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="material-icons text-sm text-[#8B7355]">category</span>
            </div>
            <div>
              <div className="font-medium text-[#1B130D] text-sm">Organize by Categories</div>
              <div className="text-xs text-[#8B7355]">Group items by type with color coding</div>
            </div>
          </div>

          <div className="flex items-center gap-3 text-left">
            <div className="w-8 h-8 bg-[#F3ECE7] rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="material-icons text-sm text-[#8B7355]">people</span>
            </div>
            <div>
              <div className="font-medium text-[#1B130D] text-sm">Share with Family</div>
              <div className="text-xs text-[#8B7355]">Collaborate on lists in real-time</div>
            </div>
          </div>

          <div className="flex items-center gap-3 text-left">
            <div className="w-8 h-8 bg-[#F3ECE7] rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="material-icons text-sm text-[#8B7355]">sync</span>
            </div>
            <div>
              <div className="font-medium text-[#1B130D] text-sm">Cross-Device Sync</div>
              <div className="text-xs text-[#8B7355]">Access from home computer or mobile phone</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
