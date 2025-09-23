/**
 * WebSocket context for sharing session ID and local action tracking across components
 */

"use client";

import React, { createContext, useContext, useState, useRef, ReactNode } from 'react';

export interface WebSocketContextType {
  sessionId: string | null;
  setSessionId: (sessionId: string | null) => void;
  trackLocalAction: (actionKey: string) => void;
  isLocalAction: (actionKey: string) => boolean;
  ignoreNextCreate: () => void;
  shouldIgnoreCreate: () => boolean;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const recentActionsRef = useRef<Set<string>>(new Set());
  const ignoreCreateRef = useRef<boolean>(false);

  const trackLocalAction = (actionKey: string) => {
    console.log('[WebSocketContext] 🟢 TRACKING local action:', actionKey);
    console.log('[WebSocketContext] Current tracked actions before add:', Array.from(recentActionsRef.current));
    recentActionsRef.current.add(actionKey);
    console.log('[WebSocketContext] Current tracked actions after add:', Array.from(recentActionsRef.current));
    
    // Clean up after 5 seconds
    setTimeout(() => {
      recentActionsRef.current.delete(actionKey);
      console.log('[WebSocketContext] 🧹 CLEANED UP action:', actionKey);
      console.log('[WebSocketContext] Remaining tracked actions:', Array.from(recentActionsRef.current));
    }, 5000);
  };

  const isLocalAction = (actionKey: string) => {
    const exists = recentActionsRef.current.has(actionKey);
    console.log('[WebSocketContext] 🔍 CHECKING local action:', actionKey, 'exists:', exists);
    console.log('[WebSocketContext] All tracked actions:', Array.from(recentActionsRef.current));
    return exists;
  };

  const ignoreNextCreate = () => {
    console.log('[WebSocketContext] 🚫 SETTING ignore next create flag');
    ignoreCreateRef.current = true;
    
    // Clear the flag after 3 seconds as a safety measure
    setTimeout(() => {
      if (ignoreCreateRef.current) {
        console.log('[WebSocketContext] ⏰ AUTO-CLEARING ignore create flag after timeout');
        ignoreCreateRef.current = false;
      }
    }, 3000);
  };

  const shouldIgnoreCreate = () => {
    const should = ignoreCreateRef.current;
    if (should) {
      console.log('[WebSocketContext] 🔍 CHECKING ignore create flag: YES - clearing flag');
      ignoreCreateRef.current = false; // Clear immediately after use
    } else {
      console.log('[WebSocketContext] 🔍 CHECKING ignore create flag: NO');
    }
    return should;
  };

  return (
    <WebSocketContext.Provider value={{ sessionId, setSessionId, trackLocalAction, isLocalAction, ignoreNextCreate, shouldIgnoreCreate }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocketContext() {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
}
