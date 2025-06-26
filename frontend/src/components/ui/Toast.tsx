import React, { useState, useEffect } from 'react';

export interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  onClose?: () => void;
}

export function Toast({ message, type = 'info', duration = 4000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      if (onClose) {
        setTimeout(onClose, 300); // Wait for fade-out animation
      }
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const getToastStyles = () => {
    const baseStyles = "fixed top-4 right-4 z-50 flex items-center p-4 rounded-xl shadow-strong border max-w-sm transition-all duration-300 animate-slide-up";
    
    switch (type) {
      case 'success':
        return `${baseStyles} bg-success-50 border-success-200 text-success-800`;
      case 'error':
        return `${baseStyles} bg-danger-50 border-danger-200 text-danger-800`;
      case 'warning':
        return `${baseStyles} bg-warning-50 border-warning-200 text-warning-800`;
      default:
        return `${baseStyles} bg-primary-50 border-primary-200 text-primary-800`;
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return 'check_circle';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'info';
    }
  };

  if (!isVisible) return null;

  return (
    <div className={getToastStyles()}>
      <span className="material-icons text-sm mr-2">{getIcon()}</span>
      <span className="flex-1 text-sm font-medium">{message}</span>
      <button
        onClick={() => {
          setIsVisible(false);
          if (onClose) {
            setTimeout(onClose, 300);
          }
        }}
        className="ml-3 p-1 hover:bg-white/50 rounded transition-colors"
      >
        <span className="material-icons text-sm opacity-70">close</span>
      </button>
    </div>
  );
}

// Toast Context and Hook for global toast management
import { createContext, useContext, ReactNode } from 'react';

interface ToastContextType {
  showToast: (message: string, type?: ToastProps['type']) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

interface ToastProviderProps {
  children: ReactNode;
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Array<ToastProps & { id: string }>>([]);

  const showToast = (message: string, type: ToastProps['type'] = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = {
      id,
      message,
      type,
      onClose: () => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
      }
    };
    setToasts(prev => [...prev, newToast]);
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toasts.map(toast => (
        <Toast key={toast.id} {...toast} />
      ))}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
