"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from '@/lib/firebase/firebase';
import { Loader2, ShoppingCart } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        router.replace('/dashboard');
      } else {
        router.replace('/login');
      }
      // setLoading(false); // Keep loading until redirect completes
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
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
