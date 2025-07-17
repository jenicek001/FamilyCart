"use client";

import React from 'react';

interface ConfirmationDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  variant?: 'danger' | 'warning' | 'info';
}

export function ConfirmationDialog({ 
  isOpen, 
  title, 
  message, 
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm, 
  onCancel,
  variant = 'danger'
}: ConfirmationDialogProps) {
  if (!isOpen) return null;

  const getVariantStyles = () => {
    switch (variant) {
      case 'danger':
        return {
          icon: 'warning',
          iconColor: 'text-red-500',
          confirmButton: 'bg-red-600 hover:bg-red-700 text-white'
        };
      case 'warning':
        return {
          icon: 'warning',
          iconColor: 'text-yellow-500',
          confirmButton: 'bg-yellow-600 hover:bg-yellow-700 text-white'
        };
      case 'info':
        return {
          icon: 'info',
          iconColor: 'text-blue-500',
          confirmButton: 'bg-blue-600 hover:bg-blue-700 text-white'
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onCancel}
      />
      
      {/* Dialog */}
      <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full mx-2 sm:mx-4 p-4 sm:p-6 border border-[#F3ECE7]">
        {/* Icon and Title */}
        <div className="flex items-center gap-3 mb-4">
          <div className={`flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-100 ${styles.iconColor}`}>
            <span className="material-icons text-xl sm:text-2xl">{styles.icon}</span>
          </div>
          <h3 className="text-base sm:text-lg font-semibold text-[#1B130D]">
            {title}
          </h3>
        </div>
        
        {/* Message */}
        <div className="mb-4 sm:mb-6">
          <p className="text-sm sm:text-base text-[#8B7355] leading-relaxed">
            {message}
          </p>
        </div>
        
        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end">
          <button
            onClick={onCancel}
            className="w-full sm:w-auto px-4 py-2 text-[#8B7355] hover:text-[#1B130D] font-medium rounded-lg hover:bg-[#F3ECE7] transition-colors duration-200"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`w-full sm:w-auto px-4 py-2 font-medium rounded-lg transition-colors duration-200 ${styles.confirmButton}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
