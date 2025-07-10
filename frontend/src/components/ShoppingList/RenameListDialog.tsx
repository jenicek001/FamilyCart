"use client";

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { ShoppingList } from '../../types';
import { useToast } from '../../hooks/use-toast';
import { Edit3, AlertCircle } from 'lucide-react';
import apiClient from '../../lib/api';

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

      const { data } = await apiClient.put<ShoppingList>(`/api/v1/shopping-lists/${list.id}`, updateData);
      
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
      if (error.response?.status === 403) {
        errorMessage = "You don't have permission to edit this list.";
      } else if (error.response?.status === 404) {
        errorMessage = "List not found.";
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
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
      <DialogContent className="max-w-md" style={{ backgroundColor: '#ffffff' }}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3 text-xl" style={{ color: '#0f172a' }}>
            <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)' }}>
              <Edit3 className="h-5 w-5" style={{ color: '#f59e0b' }} />
            </div>
            Rename List
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* List Name Field */}
          <div className="space-y-2">
            <Label htmlFor="list-name" className="text-sm font-medium" style={{ color: '#374151' }}>
              List Name *
            </Label>
            <Input
              id="list-name"
              value={newName}
              onChange={(e) => handleNameChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter list name..."
              className={`transition-colors ${nameError ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
              style={{
                borderColor: nameError ? '#ef4444' : '#e2e8f0',
                backgroundColor: '#ffffff'
              }}
              autoFocus
            />
            {nameError && (
              <div className="flex items-center gap-2 text-sm text-red-600">
                <AlertCircle className="h-4 w-4" />
                {nameError}
              </div>
            )}
          </div>

          {/* Current Stats */}
          <div className="p-3 rounded-lg" style={{ backgroundColor: '#f8fafc', borderColor: '#e2e8f0' }}>
            <div className="flex items-center justify-between text-sm" style={{ color: '#64748b' }}>
              <span>Current list</span>
              <span>{list.items?.length || 0} items</span>
            </div>
            <div className="flex items-center justify-between text-sm mt-1" style={{ color: '#64748b' }}>
              <span>Members</span>
              <span>{list.members?.length || 1} member{(list.members?.length || 1) !== 1 ? 's' : ''}</span>
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button 
            variant="outline" 
            onClick={onClose}
            disabled={isLoading}
            className="transition-colors"
            style={{
              backgroundColor: '#ffffff',
              borderColor: '#e2e8f0',
              color: '#374151'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f8fafc';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#ffffff';
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSave}
            disabled={!canSave || isLoading}
            className="transition-colors px-6"
            style={{
              backgroundColor: canSave && !isLoading ? '#f59e0b' : '#94a3b8',
              borderColor: 'transparent',
              color: '#ffffff'
            }}
            onMouseEnter={(e) => {
              if (canSave && !isLoading) {
                e.currentTarget.style.backgroundColor = '#d97706';
              }
            }}
            onMouseLeave={(e) => {
              if (canSave && !isLoading) {
                e.currentTarget.style.backgroundColor = '#f59e0b';
              }
            }}
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin" style={{
                  borderColor: '#ffffff',
                  borderTopColor: 'transparent'
                }} />
                Saving...
              </div>
            ) : (
              'Rename List'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
