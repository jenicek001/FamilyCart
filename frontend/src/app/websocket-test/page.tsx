/**
 * WebSocket test page for debugging connection issues
 */

'use client';

import { WebSocketTest } from '@/components/WebSocketTest';

export default function WebSocketTestPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <WebSocketTest listId={2} />
    </div>
  );
}
