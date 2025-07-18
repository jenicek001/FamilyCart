"use client";

import React, { useState } from 'react';
import { Item } from '../../types';
import { getCategoryColor, getCategoryIcon, getCategoryColorClass } from '../../utils/categories';
import { formatSmartTime } from '../../utils/dateUtils';
import { UserColorDot } from '../ui/UserBadge';
import { ConfirmationDialog } from '../ui/ConfirmationDialog';
import { QuantityInput } from '../QuantityInput';
import { getItemQuantityDisplay, getItemQuantityForEdit, parseUserQuantityInput } from '../../utils/quantity';

interface ShoppingListItemProps {
  item: Item;
  onToggleComplete: () => void;
  onUpdate: (updates: Partial<Item>) => Promise<void>;
  onDelete: () => void;
  isCompleted?: boolean;
}

export function ShoppingListItem({ 
  item, 
  onToggleComplete, 
  onUpdate, 
  onDelete,
  isCompleted = false 
}: ShoppingListItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(item.name);
  const [editQuantity, setEditQuantity] = useState(getItemQuantityForEdit(item));
  const [editComment, setEditComment] = useState(item.comment || '');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const categoryColor = getCategoryColor(item.category?.name);
  const categoryIcon = getCategoryIcon(item.category?.name);
  const categoryColorClass = getCategoryColorClass(item.category?.name);

  const handleSaveEdit = async () => {
    if (editName.trim()) {
      // Parse the quantity input
      const quantityInput = parseUserQuantityInput(editQuantity, item.category?.name);
      
      const updates: Partial<Item> = {
        name: editName.trim(),
        comment: editComment.trim() || null,
      };
      
      if (quantityInput) {
        // Update with structured quantity
        updates.quantity_value = typeof quantityInput.value === 'string' ? parseFloat(quantityInput.value) : quantityInput.value;
        updates.quantity_unit_id = quantityInput.unitId;
        updates.quantity_display_text = quantityInput.displayText || null;
        // Also update legacy quantity for backward compatibility
        updates.quantity = editQuantity;
      } else {
        // Fallback to legacy quantity
        updates.quantity = editQuantity;
      }
      
      await onUpdate(updates);
      setIsEditing(false);
    }
  };

  const handleCancelEdit = () => {
    setEditName(item.name);
    setEditQuantity(getItemQuantityForEdit(item));
    setEditComment(item.comment || '');
    setIsEditing(false);
  };

  const handleDeleteClick = () => {
    setShowDeleteConfirm(true);
  };

  const handleConfirmDelete = () => {
    onDelete();
    setShowDeleteConfirm(false);
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveEdit();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  return (
    <div className="bg-white p-2 sm:p-3 rounded-xl shadow-sm border border-[#F3ECE7] hover:shadow-md transition-shadow group">
      {/* Main content row */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Drag Handle - Hidden on mobile */}
        <button className="hidden sm:block p-1.5 text-gray-500 hover:text-gray-700 cursor-grab active:cursor-grabbing opacity-20 group-hover:opacity-100 transition-opacity duration-200">
          <span className="material-icons text-2xl sm:text-3xl">drag_indicator</span>
        </button>
        
        {/* Category Icon */}
        <div className={`flex items-center justify-center rounded-lg shrink-0 size-8 sm:size-12 ${categoryColorClass}`}>
          <span className="material-icons text-lg sm:text-2xl">{categoryIcon}</span>
        </div>
        
        {/* Content */}
        <div className="flex-grow min-w-0 pr-2">
          {isEditing ? (
            <div className="space-y-2">
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                onKeyDown={handleKeyPress}
                className="w-full px-2 sm:px-3 py-1 sm:py-2 text-sm sm:text-base border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#ED782A]/50 focus:border-[#ED782A] transition-colors"
                placeholder="Item name"
                autoFocus
              />
              <div className="flex items-center space-x-2">
                <label className="text-xs sm:text-sm text-slate-600 font-medium">Qty:</label>
                <QuantityInput
                  value={editQuantity}
                  onChange={setEditQuantity}
                  categoryName={item.category?.name}
                  onKeyDown={handleKeyPress}
                  className="w-32 sm:w-40"
                  placeholder="1 piece"
                />
              </div>
              <div>
                <label className="text-xs sm:text-sm text-slate-600 font-medium block mb-1">Comment:</label>
                <textarea
                  value={editComment}
                  onChange={(e) => setEditComment(e.target.value)}
                  onKeyDown={handleKeyPress}
                  className="w-full px-2 sm:px-3 py-1 sm:py-2 text-sm sm:text-base border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#ED782A]/50 focus:border-[#ED782A] transition-colors resize-none"
                  placeholder="Add a comment..."
                  rows={2}
                />
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleSaveEdit}
                  className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-[#ED782A] text-white rounded hover:bg-[#D66A25] transition-colors"
                >
                  Save
                </button>
                <button
                  onClick={handleCancelEdit}
                  className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <p className={`text-[#1B130D] text-sm sm:text-base font-medium leading-normal truncate ${isCompleted ? 'line-through' : ''}`}>
                {item.name}
              </p>
              <p className={`text-xs sm:text-sm font-normal leading-normal truncate ${isCompleted ? 'line-through' : ''}`} style={{ color: categoryColor }}>
                {item.category?.name || 'Other'}
                {/* Quantity display */}
                {getItemQuantityDisplay(item) !== '1' && (
                  <span className="ml-2 text-xs sm:text-sm text-gray-600">
                    ({getItemQuantityDisplay(item)})
                  </span>
                )}
                {/* Comment */}
                {item.comment && (
                  <span className="ml-2 text-xs text-gray-500">
                    💬 {item.comment}
                  </span>
                )}
              </p>
            </>
          )}
        </div>
        
        {/* Actions */}
        {!isEditing && (
          <div className="flex items-center space-x-1 opacity-100 sm:opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => setIsEditing(true)}
              className="p-1.5 text-gray-500 hover:text-gray-700 transition-colors touch-manipulation"
              title="Edit item"
            >
              <span className="material-icons text-base sm:text-sm">edit</span>
            </button>
            <button
              onClick={handleDeleteClick}
              className="p-1.5 text-red-500 hover:text-red-700 transition-colors touch-manipulation"
              title="Delete item"
            >
              <span className="material-icons text-base sm:text-sm">delete</span>
            </button>
          </div>
        )}
        
        {/* Checkbox */}
        <div className="shrink-0">
          <input
            type="checkbox"
            checked={isCompleted}
            onChange={onToggleComplete}
            className="h-5 w-5 sm:h-6 sm:w-6 rounded border-[#E7D9CF] border-2 bg-transparent text-[#ED782A] checked:bg-[#ED782A] checked:border-[#ED782A] focus:ring-2 focus:ring-[#ED782A]/50 focus:ring-offset-0 focus:border-[#ED782A] focus:outline-none cursor-pointer touch-manipulation"
          />
        </div>
      </div>

      {/* User info row - Full width on mobile, hidden during editing */}
      {!isEditing && (
        <div className="flex items-center gap-1 sm:gap-2 text-xs text-gray-500 mt-2 sm:mt-1 pl-10 sm:pl-16">
          {item.owner && <UserColorDot user={item.owner} size="md" />}
          <span className="shrink-0">
            Added by: {item.owner?.nickname || item.owner?.email || 'Unknown'}
          </span>
          
          {/* Show updated info with time */}
          {item.last_modified_by && (
            <>
              <span className="text-gray-400 mx-1">•</span>
              <span className="text-gray-400 shrink-0">
                Updated: {formatSmartTime(item.updated_at)} by
              </span>
              <UserColorDot user={item.last_modified_by} size="md" />
              <span className="text-gray-500 shrink-0">
                {item.last_modified_by.nickname || item.last_modified_by.email || 'Unknown'}
              </span>
            </>
          )}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showDeleteConfirm}
        title="Delete Item"
        message={`Are you sure you want to delete "${item.name}"? This action cannot be undone.`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        variant="danger"
      />
    </div>
  );
}
