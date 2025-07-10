"use client";

import React, { useState } from 'react';
import { PlusCircle, X } from 'lucide-react';
import { ShoppingList } from '../../types';

interface CreateListDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateList: (name: string, description?: string) => Promise<void>;
}

export function CreateListDialog({ isOpen, onClose, onCreateList }: CreateListDialogProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('List name is required');
      return;
    }

    setIsCreating(true);
    setError('');

    try {
      await onCreateList(name.trim(), description.trim() || undefined);
      
      // Reset form
      setName('');
      setDescription('');
      onClose();
    } catch (error) {
      console.error('Error creating list:', error);
      setError('Failed to create list. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const handleClose = () => {
    if (isCreating) return; // Prevent closing while creating
    setName('');
    setDescription('');
    setError('');
    onClose();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape' && !isCreating) {
      handleClose();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 transition-opacity duration-200"
        onClick={handleClose}
      />
      
      {/* Dialog */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div 
          className="bg-white rounded-xl shadow-strong max-w-md w-full mx-4 transform transition-all duration-200 scale-100"
          style={{
            background: 'linear-gradient(135deg, #fcfaf8 0%, #f9f5f0 100%)',
            border: '1px solid #f3ece7'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 pb-4">
            <div className="flex items-center gap-3">
              <div 
                className="p-2 rounded-lg"
                style={{ backgroundColor: 'rgba(237, 120, 42, 0.1)' }}
              >
                <PlusCircle className="h-5 w-5" style={{ color: '#ed782a' }} />
              </div>
              <h3 className="text-xl font-semibold" style={{ color: '#1b130d' }}>
                Create New List
              </h3>
            </div>
            <button
              onClick={handleClose}
              disabled={isCreating}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white/50 rounded-lg transition-colors disabled:opacity-50"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="px-6 pb-6">
            <div className="space-y-4">
              {/* List Name */}
              <div>
                <label 
                  htmlFor="list-name" 
                  className="block text-sm font-medium mb-2"
                  style={{ color: '#1b130d' }}
                >
                  List Name *
                </label>
                <input
                  id="list-name"
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    if (error) setError(''); // Clear error when user types
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder="e.g., Weekly Groceries, Family Shopping..."
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-400 focus:border-transparent transition-all duration-200"
                  required
                  autoFocus
                  disabled={isCreating}
                  maxLength={100}
                />
              </div>

              {/* Description (Optional) */}
              <div>
                <label 
                  htmlFor="list-description" 
                  className="block text-sm font-medium mb-2"
                  style={{ color: '#1b130d' }}
                >
                  Description (Optional)
                </label>
                <textarea
                  id="list-description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Add any notes about this shopping list..."
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-400 focus:border-transparent transition-all duration-200 resize-none"
                  rows={3}
                  disabled={isCreating}
                  maxLength={500}
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Help organize and share context with family members</span>
                  <span>{description.length}/500</span>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {/* Preview */}
              {name && (
                <div 
                  className="p-3 rounded-lg border"
                  style={{ 
                    backgroundColor: '#f8fafc', 
                    borderColor: '#e2e8f0' 
                  }}
                >
                  <p className="text-sm font-medium mb-1" style={{ color: '#1b130d' }}>
                    Preview:
                  </p>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-gradient-to-br from-orange-400 to-orange-500">
                      <span className="text-white text-sm">🛒</span>
                    </div>
                    <div>
                      <div className="font-medium" style={{ color: '#1b130d' }}>
                        {name}
                      </div>
                      {description && (
                        <div className="text-sm text-gray-600 truncate">
                          {description}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-6">
              <button
                type="button"
                onClick={handleClose}
                disabled={isCreating}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-white/50 rounded-lg transition-colors font-medium disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!name.trim() || isCreating}
                className="inline-flex items-center px-6 py-2 rounded-lg font-medium transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                style={{
                  backgroundColor: '#ed782a',
                  color: 'white'
                }}
                onMouseEnter={(e) => {
                  if (!isCreating && name.trim()) {
                    e.currentTarget.style.backgroundColor = '#d66a25';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isCreating) {
                    e.currentTarget.style.backgroundColor = '#ed782a';
                  }
                }}
              >
                {isCreating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Creating...
                  </>
                ) : (
                  <>
                    <PlusCircle className="h-4 w-4 mr-2" />
                    Create List
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
