"use client";

import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { createUserBadge } from '../../utils/userColors';
import { User } from '../../types';

interface UserBadgeProps {
  user: User;
  size?: 'sm' | 'md' | 'lg';
  showName?: boolean;
  showInitials?: boolean;
  className?: string;
}

export function UserBadge({ 
  user, 
  size = 'sm', 
  showName = false, 
  showInitials = true,
  className = '' 
}: UserBadgeProps) {
  const badge = createUserBadge(user);
  
  const sizeClasses = {
    sm: 'h-6 w-6 text-xs',
    md: 'h-8 w-8 text-sm', 
    lg: 'h-10 w-10 text-base'
  };
  
  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Avatar className={sizeClasses[size]}>
        <AvatarImage 
          src={badge.avatarUrl} 
          alt={badge.displayName}
        />
        <AvatarFallback 
          className={`${badge.color.bg} ${badge.color.text} border ${badge.color.border} font-medium`}
        >
          {showInitials ? badge.initials : ''}
        </AvatarFallback>
      </Avatar>
      {showName && (
        <span className={`font-medium ${badge.color.text} ${textSizeClasses[size]}`}>
          {badge.displayName}
        </span>
      )}
    </div>
  );
}

interface UserAvatarOnlyProps {
  user: User;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Simple user avatar without name - for inline use in lists
 */
export function UserAvatarOnly({ user, size = 'sm', className = '' }: UserAvatarOnlyProps) {
  return (
    <UserBadge 
      user={user} 
      size={size} 
      showName={false} 
      showInitials={true}
      className={className}
    />
  );
}

interface UserColorDotProps {
  user: User;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Just a colored dot representing the user - minimal space usage
 */
export function UserColorDot({ user, size = 'sm', className = '' }: UserColorDotProps) {
  const badge = createUserBadge(user);
  
  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };
  
  return (
    <div 
      className={`${sizeClasses[size]} rounded-full ${badge.color.accent} border ${badge.color.border} ${className}`}
      title={badge.displayName}
    />
  );
}
