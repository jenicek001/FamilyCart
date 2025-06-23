"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, ShoppingCart } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // The auth check is now handled by layout components or the dashboard itself.
    // This page simply acts as an entry point and redirects.
    router.replace('/dashboard');
  }, [router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground p-4">
      <ShoppingCart className="h-16 w-16 text-primary mb-6 animate-pulse" />
      <h1 className="text-4xl font-headline font-bold mb-3 text-primary">FamilyCart</h1>
      <p className="text-lg text-muted-foreground mb-8">Loading your shared shopping experience...</p>
      <Loader2 className="h-10 w-10 animate-spin text-accent" />
    </div>
  );
}
