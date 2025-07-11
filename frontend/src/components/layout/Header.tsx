"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useShoppingListContextSafe } from '@/contexts/ShoppingListContext';
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { createUserBadge } from '@/utils/userColors';
import { LogoWithText } from '@/components/ui/Logo';
import { Edit3 } from 'lucide-react';
import { HeaderListSelector } from '../ShoppingList/HeaderListSelector';
import { ShareDialog } from '../ShoppingList/ShareDialog';
import { RenameListDialog } from '../ShoppingList/RenameListDialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Home, LogOut, Settings, UserCircle, Loader2 } from 'lucide-react';
import { useState } from 'react';

export default function Header() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const shoppingListContext = useShoppingListContextSafe();
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Create user badge data for consistent styling
  const userBadge = user ? createUserBadge(user) : null;

  // Get shopping list data from context
  const currentList = shoppingListContext?.currentList;
  const allLists = shoppingListContext?.allLists || [];
  const onListSelect = shoppingListContext?.onListSelect;
  const onCreateList = shoppingListContext?.onCreateList;
  const onListUpdate = shoppingListContext?.onListUpdate;
  const connectionStatus = shoppingListContext?.connectionStatus;
  const onBackToSelector = shoppingListContext?.onBackToSelector;

  // Connection status indicator - Family Warmth themed
  const ConnectionIndicator = () => {
    if (!connectionStatus) return null;
    
    const statusConfig = {
      connecting: { 
        icon: 'sync', 
        bgColor: 'bg-amber-100', 
        iconColor: 'text-amber-600',
        borderColor: 'border-amber-200',
        text: 'Connecting...' 
      },
      connected: { 
        icon: 'wifi', 
        bgColor: 'bg-green-100', 
        iconColor: 'text-green-600',
        borderColor: 'border-green-200',
        text: 'Live updates' 
      },
      disconnected: { 
        icon: 'wifi_off', 
        bgColor: 'bg-gray-100', 
        iconColor: 'text-gray-500',
        borderColor: 'border-gray-200',
        text: 'Offline' 
      },
      error: { 
        icon: 'signal_wifi_connected_no_internet_4', 
        bgColor: 'bg-red-100', 
        iconColor: 'text-red-600',
        borderColor: 'border-red-200',
        text: 'Connection error' 
      },
    };

    const config = statusConfig[connectionStatus];

    return (
      <div className={`flex items-center gap-2 px-2 py-2 rounded-full border ${config.bgColor} ${config.borderColor} transition-all duration-200 h-10`} title={config.text}>
        <span className={`material-icons text-lg ${config.iconColor} ${connectionStatus === 'connecting' ? 'animate-spin' : ''}`}>
          {config.icon}
        </span>
        <span className={`text-xs font-medium ${config.iconColor} hidden sm:inline`}>
          {config.text}
        </span>
      </div>
    );
  };

  return (
    <header className="bg-card border-b border-border shadow-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <LogoWithText variant="cart-family" size="lg" href="/dashboard" />
          
          {/* Shopping List Controls - when viewing a list */}
          {currentList && (
            <div className="flex items-center gap-3 ml-4">
              {/* Back button for mobile */}
              {onBackToSelector && (
                <button
                  onClick={onBackToSelector}
                  className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200 lg:hidden"
                  aria-label="Back to list selection"
                >
                  <span className="material-icons text-lg">arrow_back</span>
                </button>
              )}
              
              {/* List Selector */}
              <HeaderListSelector
                currentList={currentList}
                allLists={allLists}
                onListSelect={onListSelect || (() => {})}
                onCreateList={onCreateList}
              />
            </div>
          )}
        </div>
        
        <nav className="flex items-center gap-3">
          {/* Shopping List Action Controls - when viewing a list */}
          {currentList && (
            <>
              {/* Connection status indicator */}
              {connectionStatus && (
                <div className="flex items-center">
                  <ConnectionIndicator />
                </div>
              )}
              
              {/* Rename button */}
              <button 
                onClick={() => setIsRenameDialogOpen(true)}
                className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200"
                aria-label="Rename list"
              >
                <Edit3 className="h-5 w-5" />
              </button>
              
              {/* Share button */}
              <button 
                onClick={() => setIsShareDialogOpen(true)}
                className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200"
                aria-label="Share list"
              >
                <span className="material-icons text-lg">share</span>
              </button>
            </>
          )}
          
          {/* User Menu */}
          {loading ? (
             <Loader2 className="h-6 w-6 animate-spin text-primary"/>
          ) : user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                  <Avatar className="h-9 w-9">
                    {/* Using a service like DiceBear for avatars based on user info */}
                    <AvatarImage src={userBadge?.avatarUrl} alt={userBadge?.displayName || "User"} />
                    <AvatarFallback className={userBadge ? `${userBadge.color.bg} ${userBadge.color.text} border ${userBadge.color.border} font-medium` : ''}>
                      {userBadge?.initials || 'FC'}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {userBadge?.displayName || 'User'}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => router.push('/dashboard')}>
                  <Home className="mr-2 h-4 w-4" />
                  <span>Dashboard</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push('/profile')}>
                  <UserCircle className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button asChild className="bg-accent hover:bg-accent/90 text-accent-foreground">
              <Link href="/login">Login</Link>
            </Button>
          )}
        </nav>
      </div>
      
      {/* Dialogs */}
      {currentList && (
        <>
          <ShareDialog
            isOpen={isShareDialogOpen}
            onClose={() => setIsShareDialogOpen(false)}
            list={currentList}
            onListUpdate={onListUpdate}
          />
          <RenameListDialog
            isOpen={isRenameDialogOpen}
            onClose={() => setIsRenameDialogOpen(false)}
            list={currentList}
            onListUpdate={onListUpdate}
          />
        </>
      )}
    </header>
  );
}
