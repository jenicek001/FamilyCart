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
    <div className="bg-white p-3 rounded-xl shadow-sm border border-[#F3ECE7] hover:shadow-md transition-shadow group">
      {/* Main content row */}
      <div className="flex items-start gap-1 sm:gap-3">
        {/* Drag Handle - Hidden on mobile */}
        <button className="hidden sm:block p-1.5 text-gray-500 hover:text-gray-700 cursor-grab active:cursor-grabbing opacity-20 group-hover:opacity-100 transition-opacity duration-200">
          <span className="material-icons text-2xl sm:text-3xl">drag_indicator</span>
        </button>
        
        {/* Category Icon */}
        <div className={`flex items-center justify-center rounded-lg shrink-0 size-10 sm:size-12 ${categoryColorClass}`}>
          <span className="material-icons text-xl sm:text-2xl">{categoryIcon}</span>
        </div>
        
        {/* Content - Takes all available space */}
        <div className="flex-1 min-w-0 overflow-hidden">
          {isEditing ? (
            <div className="space-y-3">
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                onKeyDown={handleKeyPress}
                className="w-full px-3 py-2 text-base border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#ED782A]/50 focus:border-[#ED782A] transition-colors"
                placeholder="Item name"
                autoFocus
              />
              <div className="flex items-center space-x-2">
                <label className="text-sm text-slate-600 font-medium whitespace-nowrap">Qty:</label>
                <QuantityInput
                  value={editQuantity}
                  onChange={setEditQuantity}
                  categoryName={item.category?.name}
                  onKeyDown={handleKeyPress}
                  className="flex-1 min-w-0"
                  placeholder="1 piece"
                />
              </div>
              <div>
                <label className="text-sm text-slate-600 font-medium block mb-1">Comment:</label>
                <textarea
                  value={editComment}
                  onChange={(e) => setEditComment(e.target.value)}
                  onKeyDown={handleKeyPress}
                  className="w-full px-3 py-2 text-base border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#ED782A]/50 focus:border-[#ED782A] transition-colors resize-none"
                  placeholder="Add a comment..."
                  rows={2}
                />
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleSaveEdit}
                  className="px-4 py-2 text-sm bg-[#ED782A] text-white rounded-lg hover:bg-[#D66A25] transition-colors font-medium"
                >
                  Save
                </button>
                <button
                  onClick={handleCancelEdit}
                  className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div>
              {/* Item name - Full width, wraps naturally */}
              <div className="flex items-start justify-between gap-2 mb-1">
                <h3 className={`text-[#1B130D] text-base font-medium leading-tight flex-1 min-w-0 ${isCompleted ? 'line-through' : ''}`}>
                  {item.name}
                </h3>
              </div>
              
              {/* Category and metadata row */}
              <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
                <span className={`font-medium ${isCompleted ? 'line-through' : ''}`} style={{ color: categoryColor }}>
                  {item.category?.name || 'Other'}
                </span>
                
                {/* Quantity display */}
                {getItemQuantityDisplay(item) !== '1' && (
                  <span className="text-gray-600 font-medium">
                    ({getItemQuantityDisplay(item)})
                  </span>
                )}
                
                {/* Comment */}
                {item.comment && (
                  <span className="text-gray-500 flex items-center gap-1">
                    <span>💬</span>
                    <span className="break-words">{item.comment}</span>
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
        
        {/* Action buttons + Checkbox - Right side - Only on desktop hover or always on mobile */}
        <div className="flex items-center gap-1 shrink-0">
          {/* Action buttons */}
          {!isEditing && (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-all touch-manipulation opacity-100 sm:opacity-0 group-hover:opacity-100"
                title="Edit item"
              >
                <span className="material-icons text-xl">edit</span>
              </button>
              <button
                onClick={handleDeleteClick}
                className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-md transition-all touch-manipulation opacity-100 sm:opacity-0 group-hover:opacity-100"
                title="Delete item"
              >
                <span className="material-icons text-xl">delete</span>
              </button>
            </>
          )}
          
          {/* Checkbox - Same size and alignment as action buttons */}
          <div className="p-2 flex items-center justify-center">
            <input
              type="checkbox"
              checked={isCompleted}
              onChange={onToggleComplete}
              className="h-5 w-5 rounded border-[#E7D9CF] border-2 bg-transparent text-[#ED782A] checked:bg-[#ED782A] checked:border-[#ED782A] focus:ring-2 focus:ring-[#ED782A]/50 focus:ring-offset-0 focus:border-[#ED782A] focus:outline-none cursor-pointer touch-manipulation"
            />
          </div>
        </div>
      </div>

      {/* Mobile user info - Full width usage outside content constraints */}
      {!isEditing && (
        <div className="sm:hidden mt-1 text-xs text-gray-400 pl-11">
          {/* Added by info - no date, full width */}
          <div className="flex items-center gap-1">
            {item.owner && <UserColorDot user={item.owner} size="sm" />}
            <span>Added by {item.owner?.nickname || item.owner?.email || 'Unknown'}</span>
          </div>
          
          {/* Updated info - with date, full width, single line */}
          {item.last_modified_by && (
            <div className="flex items-center gap-1">
              <UserColorDot user={item.last_modified_by} size="sm" />
              <span>Updated {formatSmartTime(item.updated_at)} by {item.last_modified_by.nickname || item.last_modified_by.email || 'Unknown'}</span>
            </div>
          )}
        </div>
      )}

      {/* Desktop user info row - Hidden on mobile, hidden during editing */}
      {!isEditing && (
        <div className="hidden sm:flex items-center gap-1 sm:gap-2 text-xs text-gray-500 mt-2 sm:mt-1 pl-10 sm:pl-16">
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
