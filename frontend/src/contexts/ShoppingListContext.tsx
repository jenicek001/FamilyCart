/**
 * Shopping List Context for sharing shopping list state across components
 */

"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { ShoppingList } from '@/types';

interface ShoppingListContextType {
  currentList: ShoppingList | null;
  allLists: ShoppingList[];
  setCurrentList: (list: ShoppingList | null) => void;
  setAllLists: (lists: ShoppingList[]) => void;
  onListSelect?: (list: ShoppingList) => void;
  onCreateList?: () => void;
  onListUpdate?: (updatedList: ShoppingList) => void;
  connectionStatus?: 'connecting' | 'connected' | 'disconnected' | 'error';
  onBackToSelector?: () => void;
  setShoppingListHandlers: (handlers: {
    onListSelect?: (list: ShoppingList) => void;
    onCreateList?: () => void;
    onListUpdate?: (updatedList: ShoppingList) => void;
    connectionStatus?: 'connecting' | 'connected' | 'disconnected' | 'error';
    onBackToSelector?: () => void;
  }) => void;
}

const ShoppingListContext = createContext<ShoppingListContextType | undefined>(undefined);

export function ShoppingListProvider({ children }: { children: ReactNode }) {
  const [currentList, setCurrentList] = useState<ShoppingList | null>(null);
  const [allLists, setAllLists] = useState<ShoppingList[]>([]);
  const [handlers, setHandlers] = useState<{
    onListSelect?: (list: ShoppingList) => void;
    onCreateList?: () => void;
    onListUpdate?: (updatedList: ShoppingList) => void;
    connectionStatus?: 'connecting' | 'connected' | 'disconnected' | 'error';
    onBackToSelector?: () => void;
  }>({});

  const setShoppingListHandlers = (newHandlers: typeof handlers) => {
    setHandlers(newHandlers);
  };

  return (
    <ShoppingListContext.Provider
      value={{
        currentList,
        allLists,
        setCurrentList,
        setAllLists,
        setShoppingListHandlers,
        ...handlers,
      }}
    >
      {children}
    </ShoppingListContext.Provider>
  );
}

export function useShoppingListContext() {
  const context = useContext(ShoppingListContext);
  if (context === undefined) {
    throw new Error('useShoppingListContext must be used within a ShoppingListProvider');
  }
  return context;
}

// Hook for safe usage (returns undefined if not in provider)
export function useShoppingListContextSafe() {
  return useContext(ShoppingListContext);
}
