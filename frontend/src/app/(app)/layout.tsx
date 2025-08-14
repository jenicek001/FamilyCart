import Header from '@/components/layout/Header';
import { ShoppingListProvider } from '@/contexts/ShoppingListContext';
import type React from 'react';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ShoppingListProvider>
      <div className="flex flex-col min-h-screen bg-[#FCFAF8] overflow-x-hidden">
        <Header />
        <main className="flex-grow pt-28 sm:pt-20 pb-5 relative">
          {children}
        </main>
        <footer className="py-4 text-center text-sm text-muted-foreground border-t border-border">
          © {new Date().getFullYear()} FamilyCart. Keep your shopping organized.
        </footer>
      </div>
    </ShoppingListProvider>
  );
}
