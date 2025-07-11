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
      <div className="flex flex-col min-h-screen">
        <Header />
        <main className="flex-grow container mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="py-4 text-center text-sm text-muted-foreground border-t border-border">
          © {new Date().getFullYear()} FamilyCart. Keep your shopping organized.
        </footer>
      </div>
    </ShoppingListProvider>
  );
}
