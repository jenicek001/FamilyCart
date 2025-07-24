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
      <div className={`flex items-center gap-2 px-2 py-2 rounded-full border ${config.bgColor} ${config.borderColor} transition-all duration-200 h-8 sm:h-10`} title={config.text}>
        <span className={`material-icons text-base sm:text-xl ${config.iconColor} ${connectionStatus === 'connecting' ? 'animate-spin' : ''}`}>
          {config.icon}
        </span>
        <span className={`text-xs font-medium ${config.iconColor} hidden sm:inline`}>
          {config.text}
        </span>
      </div>
    );
  };

  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-border shadow-sm sticky top-0 z-50">
      {/* 2-line mobile layout: top line (logo + actions), bottom line (list selector) */}
      {currentList ? (
        <div className="container mx-auto px-2 sm:px-4">
          {/* First Line: Logo + Actions (mobile) / Full Header (desktop) */}
          <div className="h-12 sm:h-16 flex items-center justify-between gap-2">
            <div className="flex items-center gap-1 sm:gap-2 min-w-0 flex-1">
              {/* Logo */}
              <div className="flex-shrink-0">
                <LogoWithText 
                  variant="cart-family" 
                  size="2xl" 
                  href="/dashboard" 
                />
              </div>
              
              {/* Desktop List Controls - hidden on mobile */}
              <div className="hidden sm:flex items-center gap-2 min-w-0 flex-1">
                {/* Desktop List Selector with constrained width */}
                <div className="min-w-0 flex-1 max-w-sm lg:max-w-md">
                  <HeaderListSelector
                    currentList={currentList}
                    allLists={allLists}
                    onListSelect={onListSelect || (() => {})}
                    onCreateList={onCreateList}
                  />
                </div>
              </div>
            </div>
            
            <nav className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
              {/* Connection status indicator - desktop only */}
              {connectionStatus && (
                <div className="hidden sm:flex items-center">
                  <ConnectionIndicator />
                </div>
              )}
              
              {/* Action buttons */}
              <button 
                onClick={() => setIsRenameDialogOpen(true)}
                className="flex items-center justify-center overflow-hidden rounded-full h-8 w-8 sm:h-10 sm:w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200"
                aria-label="Rename list"
              >
                <Edit3 className="h-4 w-4 sm:h-5 sm:w-5" />
              </button>
              
              <button 
                onClick={() => setIsShareDialogOpen(true)}
                className="flex items-center justify-center overflow-hidden rounded-full h-8 w-8 sm:h-10 sm:w-10 bg-[#ED782A] text-white hover:bg-[#D66A25] transition-colors duration-200"
                aria-label="Share list"
              >
                <span className="material-icons text-base sm:text-xl">share</span>
              </button>
              
              {/* User Menu */}
              {loading ? (
                 <Loader2 className="h-4 w-4 sm:h-5 sm:w-5 animate-spin text-primary"/>
              ) : user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-8 w-8 sm:h-10 sm:w-10 rounded-full">
                      <Avatar className="h-8 w-8 sm:h-10 sm:w-10">
                        <AvatarImage src={userBadge?.avatarUrl} alt={userBadge?.displayName || "User"} />
                        <AvatarFallback className={userBadge ? `${userBadge.color.bg} ${userBadge.color.text} border ${userBadge.color.border} font-medium text-xs sm:text-sm` : ''}>
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
                        <p className="text-xs leading-none text-muted-foreground truncate">
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
                <Button asChild className="bg-accent hover:bg-accent/90 text-accent-foreground text-sm sm:text-base px-3 sm:px-4">
                  <Link href="/login">Login</Link>
                </Button>
              )}
            </nav>
          </div>
          
          {/* Second Line: Mobile List Selector + Connection Status */}
          <div className="sm:hidden pb-2 border-t border-border/30">
            <div className="flex items-center gap-2 pt-2">
              {/* Mobile List Selector - full width */}
              <div className="min-w-0 flex-1">
                <HeaderListSelector
                  currentList={currentList}
                  allLists={allLists}
                  onListSelect={onListSelect || (() => {})}
                  onCreateList={onCreateList}
                />
              </div>
              
              {/* Mobile Connection Status */}
              {connectionStatus && (
                <div className="flex-shrink-0">
                  <ConnectionIndicator />
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        // Dashboard view - single line layout
        <div className="container mx-auto px-2 sm:px-4 h-14 sm:h-16 flex items-center justify-between gap-2">
          <div className="flex items-center gap-1 sm:gap-2 min-w-0 flex-1">
            <div className="flex-shrink-0">
              <LogoWithText 
                variant="cart-family" 
                size="2xl" 
                href="/dashboard" 
              />
            </div>
          </div>
          
          <nav className="flex items-center gap-1 flex-shrink-0">
            {loading ? (
               <Loader2 className="h-4 w-4 sm:h-5 sm:w-5 animate-spin text-primary"/>
            ) : user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 sm:h-10 sm:w-10 rounded-full">
                    <Avatar className="h-8 w-8 sm:h-10 sm:w-10">
                      <AvatarImage src={userBadge?.avatarUrl} alt={userBadge?.displayName || "User"} />
                      <AvatarFallback className={userBadge ? `${userBadge.color.bg} ${userBadge.color.text} border ${userBadge.color.border} font-medium text-xs sm:text-sm` : ''}>
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
                      <p className="text-xs leading-none text-muted-foreground truncate">
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
              <Button asChild className="bg-accent hover:bg-accent/90 text-accent-foreground text-sm sm:text-base px-3 sm:px-4">
                <Link href="/login">Login</Link>
              </Button>
            )}
          </nav>
        </div>
      )}
      
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
