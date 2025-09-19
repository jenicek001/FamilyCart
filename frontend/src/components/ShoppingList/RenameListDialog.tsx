"use client";

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { ShoppingList } from '@/types';
import { useToast } from '@/hooks/use-toast';
import { Edit3, AlertCircle } from 'lucide-react';
import { useApiClient } from '@/hooks/use-api-client';

interface RenameListDialogProps {
  isOpen: boolean;
  onClose: () => void;
  list: ShoppingList;
  onListUpdate?: (updatedList: ShoppingList) => void;
}

export function RenameListDialog({ isOpen, onClose, list, onListUpdate }: RenameListDialogProps) {
  const [newName, setNewName] = useState(list.name);
  const [isLoading, setIsLoading] = useState(false);
  const [nameError, setNameError] = useState('');
  const { toast } = useToast();
  const { apiClient } = useApiClient();

  // Reset form when dialog opens/closes or list changes
  useEffect(() => {
    if (isOpen) {
      setNewName(list.name);
      setNameError('');
    }
  }, [isOpen, list.name]);

  // Validate list name
  const validateName = (name: string): string => {
    const trimmed = name.trim();
    if (!trimmed) {
      return 'List name is required';
    }
    if (trimmed.length < 2) {
      return 'List name must be at least 2 characters';
    }
    if (trimmed.length > 50) {
      return 'List name must be less than 50 characters';
    }
    return '';
  };

  const handleNameChange = (value: string) => {
    setNewName(value);
    setNameError(validateName(value));
  };

  const handleSave = async () => {
    const trimmedName = newName.trim();

    // Final validation
    const error = validateName(trimmedName);
    if (error) {
      setNameError(error);
      return;
    }

    // Check if anything actually changed
    if (trimmedName === list.name) {
      onClose();
      return;
    }

    setIsLoading(true);
    
    try {
      const updateData = { name: trimmedName };

      const data = await apiClient(`/api/v1/shopping-lists/${list.id}/`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      });
      
      // Update parent component
      onListUpdate?.(data);
      
      // Show success message
      toast({
        title: "List renamed",
        description: `List renamed to "${data.name}" successfully`,
        duration: 3000,
      });

      onClose();
    } catch (error: any) {
      console.error('Error renaming list:', error);
      
      // Handle specific error cases
      let errorMessage = "Could not rename list. Please try again.";
      if (error.message?.includes('403')) {
        errorMessage = "You don't have permission to edit this list.";
      } else if (error.message?.includes('404')) {
        errorMessage = "List not found.";
      } else if (error.message) {
        errorMessage = error.message;
      }

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
        duration: 4000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  const hasChanges = newName.trim() !== list.name;
  const canSave = !nameError && hasChanges && newName.trim();

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="w-[90vw] max-w-[320px] mx-auto p-4 sm:w-full sm:max-w-md sm:mx-4 sm:p-6 overflow-hidden rounded-2xl shadow-xl border-0" style={{ 
        backgroundColor: '#ffffff',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(0, 0, 0, 0.05)'
      }}>
        <DialogHeader className="pb-4 sm:pb-4">
          <DialogTitle className="flex items-center gap-3 text-lg sm:text-xl" style={{ color: '#0f172a' }}>
            <div className="p-2 rounded-xl flex-shrink-0" style={{ 
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              border: '1px solid rgba(245, 158, 11, 0.2)'
            }}>
              <Edit3 className="h-5 w-5 sm:h-5 sm:w-5" style={{ color: '#f59e0b' }} />
            </div>
            <span className="text-lg sm:text-lg truncate font-semibold">Rename List</span>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 sm:space-y-4 py-2 min-w-0">
          {/* List Name Field */}
          <div className="space-y-3 min-w-0">
            <Label htmlFor="list-name" className="text-sm font-semibold" style={{ color: '#374151' }}>
              List Name *
            </Label>
            <Input
              id="list-name"
              value={newName}
              onChange={(e) => handleNameChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter list name..."
              className={`text-base transition-all duration-200 w-full rounded-xl border-2 px-4 py-3 ${nameError ? 'border-red-400 focus:border-red-500 focus:ring-red-500' : 'border-gray-200 focus:border-amber-400 focus:ring-amber-400'}`}
              style={{
                borderColor: nameError ? '#f87171' : '#e5e7eb',
                backgroundColor: '#ffffff',
                fontSize: '16px' // Prevents zoom on iOS
              }}
              autoFocus
            />
            {nameError && (
              <div className="flex items-center gap-2 text-sm text-red-500 min-w-0 bg-red-50 p-3 rounded-xl border border-red-200">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                <span className="truncate font-medium">{nameError}</span>
              </div>
            )}
          </div>

          {/* Current Stats - Hidden on mobile, compact on larger screens */}
          <div className="hidden sm:block p-4 rounded-xl border" style={{ 
            backgroundColor: '#f8fafc', 
            borderColor: '#e2e8f0' 
          }}>
            <div className="flex items-center justify-between text-sm" style={{ color: '#64748b' }}>
              <span>Current list</span>
              <span className="font-medium">{list.items?.length || 0} items</span>
            </div>
            <div className="flex items-center justify-between text-sm mt-2" style={{ color: '#64748b' }}>
              <span>Members</span>
              <span className="font-medium">{list.members?.length || 1} member{(list.members?.length || 1) !== 1 ? 's' : ''}</span>
            </div>
          </div>
        </div>

        <DialogFooter className="gap-3 pt-4 flex-col sm:flex-row">
          <Button 
            variant="outline" 
            onClick={onClose}
            disabled={isLoading}
            className="w-full sm:w-auto text-base transition-all duration-200 order-2 sm:order-1 min-w-0 rounded-xl border-2 py-3 font-medium"
            style={{
              backgroundColor: '#ffffff',
              borderColor: '#e5e7eb',
              color: '#374151'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f9fafb';
              e.currentTarget.style.borderColor = '#d1d5db';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#ffffff';
              e.currentTarget.style.borderColor = '#e5e7eb';
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSave}
            disabled={!canSave || isLoading}
            className="w-full sm:w-auto text-base transition-all duration-200 px-6 order-1 sm:order-2 min-w-0 rounded-xl py-3 font-semibold shadow-lg"
            style={{
              backgroundColor: canSave && !isLoading ? '#f59e0b' : '#9ca3af',
              borderColor: 'transparent',
              color: '#ffffff',
              boxShadow: canSave && !isLoading ? '0 10px 15px -3px rgba(245, 158, 11, 0.3), 0 4px 6px -2px rgba(245, 158, 11, 0.1)' : '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
            }}
            onMouseEnter={(e) => {
              if (canSave && !isLoading) {
                e.currentTarget.style.backgroundColor = '#d97706';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(245, 158, 11, 0.4), 0 10px 10px -5px rgba(245, 158, 11, 0.1)';
              }
            }}
            onMouseLeave={(e) => {
              if (canSave && !isLoading) {
                e.currentTarget.style.backgroundColor = '#f59e0b';
                e.currentTarget.style.transform = 'translateY(0px)';
                e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(245, 158, 11, 0.3), 0 4px 6px -2px rgba(245, 158, 11, 0.1)';
              }
            }}
          >
            {isLoading ? (
              <div className="flex items-center gap-2 min-w-0">
                <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin flex-shrink-0" style={{
                  borderColor: '#ffffff',
                  borderTopColor: 'transparent'
                }} />
                <span className="truncate">Saving...</span>
              </div>
            ) : (
              <span className="truncate">Rename List</span>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
