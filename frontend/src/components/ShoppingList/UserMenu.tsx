"use client";

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { UserBadge } from '@/components/ui/UserBadge';
import { LogOut, User, Settings } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface UserMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onToggle: () => void;
}

export function UserMenu({ isOpen, onClose, onToggle }: UserMenuProps) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, onClose]);

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
    onClose();
  };

  const handleProfile = () => {
    // Navigate to profile page when implemented
    // router.push('/profile');
    onClose();
  };

  const handleSettings = () => {
    // Navigate to settings page when implemented  
    // router.push('/settings');
    onClose();
  };

  if (!user) return null;

  return (
    <div className="relative" ref={menuRef}>
      {/* Menu Button */}
      <button
        onClick={onToggle}
        className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200"
        aria-label="User menu"
        aria-expanded={isOpen}
      >
        <span className="material-icons text-lg">person</span>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 top-12 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
          {/* User Info Header */}
          <div className="px-4 py-3 border-b border-gray-100">
            <UserBadge user={user} size="md" showName />
            <p className="text-xs text-gray-500 mt-1">{user.email}</p>
          </div>

          {/* Menu Items */}
          <div className="py-1">
            <button
              onClick={handleProfile}
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <User className="h-4 w-4" />
              Profile
            </button>
            
            <button
              onClick={handleSettings}
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <Settings className="h-4 w-4" />
              Settings
            </button>

            <hr className="my-1 border-gray-100" />
            
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
