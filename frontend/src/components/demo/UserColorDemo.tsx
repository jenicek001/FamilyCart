// Demo component to test user color system
// This can be temporarily added to any page to see the color variations

import React from 'react';
import { UserBadge, UserAvatarOnly, UserColorDot } from '../ui/UserBadge';
import { User } from '../../types';

// Mock users for testing
const mockUsers: User[] = [
  {
    id: 'user-1',
    email: 'alice@example.com',
    full_name: 'Alice Johnson',
    nickname: 'Alice',
    first_name: 'Alice',
    last_name: 'Johnson',
    is_active: true,
    is_superuser: false
  },
  {
    id: 'user-2',
    email: 'bob@example.com',
    full_name: 'Bob Smith',
    nickname: 'Bobby',
    first_name: 'Bob',
    last_name: 'Smith',
    is_active: true,
    is_superuser: false
  },
  {
    id: 'user-3',
    email: 'carol@example.com',
    full_name: 'Carol Williams',
    nickname: 'Carol',
    first_name: 'Carol',
    last_name: 'Williams',
    is_active: true,
    is_superuser: false
  },
  {
    id: 'user-4',
    email: 'david@example.com',
    full_name: 'David Brown',
    nickname: 'Dave',
    first_name: 'David',
    last_name: 'Brown',
    is_active: true,
    is_superuser: false
  },
  {
    id: 'user-5',
    email: 'emma@example.com',
    full_name: 'Emma Davis',
    nickname: 'Em',
    first_name: 'Emma',
    last_name: 'Davis',
    is_active: true,
    is_superuser: false
  }
];

export function UserColorDemo() {
  return (
    <div className="p-6 space-y-6 bg-white rounded-lg shadow-soft">
      <h2 className="text-lg font-semibold text-slate-900">User Color System Demo</h2>
      
      <div className="space-y-4">
        <h3 className="text-md font-medium text-slate-700">Full User Badges</h3>
        <div className="flex flex-wrap gap-3">
          {mockUsers.map(user => (
            <UserBadge key={user.id} user={user} size="md" showName={true} />
          ))}
        </div>
      </div>
      
      <div className="space-y-4">
        <h3 className="text-md font-medium text-slate-700">Avatar Only (for lists)</h3>
        <div className="flex gap-2">
          {mockUsers.map(user => (
            <UserAvatarOnly key={user.id} user={user} size="sm" />
          ))}
        </div>
      </div>
      
      <div className="space-y-4">
        <h3 className="text-md font-medium text-slate-700">Color Dots (minimal space)</h3>
        <div className="flex gap-2">
          {mockUsers.map(user => (
            <UserColorDot key={user.id} user={user} size="md" />
          ))}
        </div>
      </div>
      
      <div className="space-y-4">
        <h3 className="text-md font-medium text-slate-700">Simulated Shopping List Items</h3>
        <div className="space-y-2">
          {mockUsers.map((user, index) => (
            <div key={user.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="material-icons text-orange-500">shopping_cart</span>
                <span className="font-medium">Shopping Item {index + 1}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <UserColorDot user={user} size="sm" />
                <span>Added by: {user.nickname}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
