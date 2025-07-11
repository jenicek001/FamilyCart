"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2, ShoppingCart } from 'lucide-react';
import WelcomePage from './welcome/page';

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Redirect authenticated users to dashboard
    if (!loading && user) {
      router.replace('/dashboard');
    }
  }, [user, loading, router]);

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-orange-400 to-red-400 rounded-full blur-xl opacity-50 animate-pulse"></div>
          <div className="relative bg-white rounded-full p-6 shadow-2xl">
            <ShoppingCart className="h-16 w-16 text-orange-500 animate-pulse" />
          </div>
        </div>
        <h1 className="text-4xl font-bold mt-6 mb-3 bg-gradient-to-r from-orange-500 to-red-500 bg-clip-text text-transparent">
          FamilyCart
        </h1>
        <p className="text-lg text-gray-600 mb-8">Loading your shared shopping experience...</p>
        <Loader2 className="h-10 w-10 animate-spin text-orange-500" />
      </div>
    );
  }

  // Show welcome page for unauthenticated users
  if (!user) {
    return <WelcomePage />;
  }

  // This shouldn't be reached due to the useEffect redirect, but just in case
  return null;
}
