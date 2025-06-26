"use client";

import React, { useState } from 'react';
import { Item } from '../../types';
import { getCategoryColor, getCategoryIcon, getCategoryColorClass } from '../../utils/categories';
import { ConfirmationDialog } from '../ui/ConfirmationDialog';

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
  const [editQuantity, setEditQuantity] = useState(item.quantity || 1);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const categoryColor = getCategoryColor(item.category?.name);
  const categoryIcon = getCategoryIcon(item.category?.name);
  const categoryColorClass = getCategoryColorClass(item.category?.name);

  const handleSaveEdit = async () => {
    if (editName.trim()) {
      await onUpdate({
        name: editName.trim(),
        quantity: editQuantity,
      });
      setIsEditing(false);
    }
  };

  const handleCancelEdit = () => {
    setEditName(item.name);
    setEditQuantity(item.quantity || 1);
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
    <div className="flex items-center gap-2 bg-white p-3 rounded-xl shadow-sm border border-[#F3ECE7] hover:shadow-md transition-shadow group">
      {/* Drag Handle */}
      <button className="p-1.5 text-gray-500 hover:text-gray-700 cursor-grab active:cursor-grabbing opacity-20 group-hover:opacity-100 transition-opacity duration-200">
        <span className="material-icons text-3xl">drag_indicator</span>
      </button>
      
      {/* Category Icon */}
      <div className={`flex items-center justify-center rounded-lg shrink-0 size-12 ${categoryColorClass}`}>
        <span className="material-icons text-2xl">{categoryIcon}</span>
      </div>
      
      {/* Content */}
      <div className="flex-grow">
        {isEditing ? (
          <div className="space-y-2">
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              onKeyDown={handleKeyPress}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#ED782A]/50 focus:border-[#ED782A] transition-colors"
              placeholder="Item name"
              autoFocus
            />
            <div className="flex items-center space-x-2">
              <label className="text-sm text-slate-600 font-medium">Qty:</label>
              <input
                type="number"
                value={editQuantity}
                onChange={(e) => setEditQuantity(parseInt(e.target.value) || 1)}
                onKeyDown={handleKeyPress}
                min="1"
                className="w-20 px-2 py-1 border border-slate-300 rounded focus:ring-2 focus:ring-[#ED782A]/50 focus:border-[#ED782A] transition-colors"
              />
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleSaveEdit}
                className="px-3 py-1 bg-[#ED782A] text-white rounded text-sm hover:bg-[#D66A25] transition-colors"
              >
                Save
              </button>
              <button
                onClick={handleCancelEdit}
                className="px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <p className={`text-[#1B130D] text-base font-medium leading-normal ${isCompleted ? 'line-through' : ''}`}>
              {item.name}
              {item.quantity && item.quantity > 1 && (
                <span className="ml-2 text-sm text-gray-600">({item.quantity})</span>
              )}
            </p>
            <p className={`text-sm font-normal leading-normal ${isCompleted ? 'line-through' : ''}`} style={{ color: categoryColor }}>
              {item.category?.name || 'Other'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Added by: {item.owner?.nickname || item.owner?.email || 'Unknown'} <span className="text-gray-400">• Last modified: {new Date(item.updated_at).toLocaleDateString()}</span>
            </p>
          </>
        )}
      </div>
      
      {/* Actions */}
      {!isEditing && (
        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => setIsEditing(true)}
            className="p-1.5 text-gray-500 hover:text-gray-700 transition-colors"
            title="Edit item"
          >
            <span className="material-icons text-sm">edit</span>
          </button>
          <button
            onClick={handleDeleteClick}
            className="p-1.5 text-red-500 hover:text-red-700 transition-colors"
            title="Delete item"
          >
            <span className="material-icons text-sm">delete</span>
          </button>
        </div>
      )}
      
      {/* Checkbox */}
      <div className="shrink-0">
        <input
          type="checkbox"
          checked={isCompleted}
          onChange={onToggleComplete}
          className="h-6 w-6 rounded border-[#E7D9CF] border-2 bg-transparent text-[#ED782A] checked:bg-[#ED782A] checked:border-[#ED782A] focus:ring-2 focus:ring-[#ED782A]/50 focus:ring-offset-0 focus:border-[#ED782A] focus:outline-none cursor-pointer"
        />
      </div>

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
