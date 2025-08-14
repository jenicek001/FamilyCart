/**
 * Simple WebSocket test component to debug connection issues
 */

import React, { useState, useCallback } from 'react';
import { useWebSocket, WebSocketMessage } from '@/hooks/use-websocket';

interface WebSocketTestProps {
  listId: number;
}

export function WebSocketTest({ listId }: WebSocketTestProps) {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `${timestamp}: ${message}`]);
    console.log(`[WebSocketTest] ${message}`);
  }, []);

  const handleItemChange = useCallback((message: WebSocketMessage) => {
    addLog(`Received item_change: ${JSON.stringify(message)}`);
    setMessages(prev => [...prev, message]);
  }, [addLog]);

  const handleListChange = useCallback((message: WebSocketMessage) => {
    addLog(`Received list_change: ${JSON.stringify(message)}`);
    setMessages(prev => [...prev, message]);
  }, [addLog]);

  const handleConnectionChange = useCallback((connected: boolean) => {
    addLog(`Connection status changed: ${connected ? 'connected' : 'disconnected'}`);
  }, [addLog]);

  const { connected, connecting, error, reconnect } = useWebSocket({
    listId,
    onItemChange: handleItemChange,
    onListChange: handleListChange,
    onConnectionChange: handleConnectionChange,
    autoReconnect: true,
  });

  React.useEffect(() => {
    addLog(`WebSocket state: connected=${connected}, connecting=${connecting}, error=${error}`);
  }, [connected, connecting, error, addLog]);

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">WebSocket Test for List {listId}</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="border rounded p-4">
          <h2 className="text-lg font-semibold mb-2">Connection Status</h2>
          <div className="space-y-2">
            <p>Connected: <span className={connected ? 'text-green-600' : 'text-red-600'}>{connected.toString()}</span></p>
            <p>Connecting: <span className={connecting ? 'text-yellow-600' : 'text-gray-600'}>{connecting.toString()}</span></p>
            <p>Error: <span className={error ? 'text-red-600' : 'text-gray-600'}>{error || 'None'}</span></p>
          </div>
          {error && (
            <button 
              onClick={reconnect}
              className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Reconnect
            </button>
          )}
        </div>

        <div className="border rounded p-4">
          <h2 className="text-lg font-semibold mb-2">Messages ({messages.length})</h2>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {messages.slice(-5).map((msg, idx) => (
              <div key={idx} className="text-sm bg-gray-100 p-2 rounded">
                <strong>{msg.type}</strong>: {msg.event_type}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 border rounded p-4">
        <h2 className="text-lg font-semibold mb-2">Debug Logs</h2>
        <div className="bg-black text-green-400 p-3 rounded font-mono text-sm max-h-60 overflow-y-auto">
          {logs.slice(-20).map((log, idx) => (
            <div key={idx}>{log}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
