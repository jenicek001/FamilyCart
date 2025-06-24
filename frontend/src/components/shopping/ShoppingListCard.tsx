"use client";

import type { ShoppingList, ShoppingListItem, User } from '@/types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, XCircle, Edit3, Trash2, Users, CalendarDays, ShoppingBasket, ChevronDown, ChevronUp, icons, Apple, Beef, Milk } from 'lucide-react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { useState, useEffect } from 'react';
import Image from 'next/image';
import AddItemForm from './AddItemForm';

interface ShoppingListCardProps {
  list: ShoppingList;
  currentUser: User | null;
  onAddItem: (listId: number, item: { name: string; quantity?: string; description?: string; category_name?: string }) => void;
  onToggleItem: (listId: number, itemId: number) => void;
  onDeleteItem: (listId: number, itemId: number) => void;
  onEditList: (list: ShoppingList) => void;
  onDeleteList: (listId: number) => void;
  onShareList: (listId: number, email: string) => void;
}

// Helper to render a Lucide icon dynamically by name
const DynamicIcon = ({ name, ...props }: { name: string | null | undefined } & React.ComponentProps<typeof ShoppingBasket>) => {
  if (!name) return <ShoppingBasket {...props} />;

  const toPascalCase = (str: string) => 
    str.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join('');

  const IconComponent = icons[toPascalCase(name) as keyof typeof icons];

  if (!IconComponent) {
    return <ShoppingBasket {...props} />;
  }

  return <IconComponent {...props} />;
};

// Helper to get a generic Lucide icon or placeholder based on category
const getItemIcon = (item: ShoppingListItem) => {
  // Prioritize the AI-suggested icon if it exists
  if (item.icon_name) {
    return <DynamicIcon name={item.icon_name} className="h-5 w-5 text-muted-foreground" />;
  }

  // Fallback to category-based icons
  const categoryName = item.category?.name.toLowerCase();
  if (categoryName?.includes('produce')) return <Apple className="h-5 w-5 text-green-500" data-ai-hint="produce vegetable"/>;
  if (categoryName?.includes('dairy')) return <Milk className="h-5 w-5 text-blue-500" data-ai-hint="milk cheese"/>;
  if (categoryName?.includes('meat')) return <Beef className="h-5 w-5 text-red-500" data-ai-hint="meat steak"/>;
  
  return <ShoppingBasket className="h-5 w-5 text-muted-foreground" data-ai-hint="grocery item"/>;
};


export default function ShoppingListCard({ 
  list, 
  currentUser,
  onAddItem,
  onToggleItem,
  onDeleteItem,
  onEditList, 
  onDeleteList,
  onShareList
}: ShoppingListCardProps) {
  const [sortedItems, setSortedItems] = useState<ShoppingListItem[]>([]);

  useEffect(() => {
    const itemsToSort = [...(list.items || [])];
    itemsToSort.sort((a, b) => {
      if (a.category && b.category) {
        if (a.category.name < b.category.name) return -1;
        if (a.category.name > b.category.name) return 1;
      } else if (a.category) {
        return -1; // Items with category come first
      } else if (b.category) {
        return 1;
      }
      return a.name.localeCompare(b.name);
    });
    setSortedItems(itemsToSort);
  }, [list.items]);


  const purchasedItemsCount = (list.items || []).filter(item => item.is_completed).length;
  const totalItemsCount = (list.items || []).length;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <Card className="w-full shadow-lg hover:shadow-xl transition-shadow duration-300">
      <CardHeader className="pb-4">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="font-headline text-2xl mb-1">{list.name}</CardTitle>
            <CardDescription className="flex items-center text-xs text-muted-foreground">
              <Users className="h-3 w-3 mr-1" /> {list.members.length} member(s)
              <CalendarDays className="h-3 w-3 ml-3 mr-1" /> Created: {formatDate(list.created_at)}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="icon" onClick={() => onEditList(list)} aria-label="Edit list">
              <Edit3 className="h-4 w-4" />
            </Button>
            <Button variant="destructive" size="icon" onClick={() => onDeleteList(list.id)} aria-label="Delete list">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {sortedItems.length === 0 ? (
          <p className="text-muted-foreground italic">This list is empty. Add some items!</p>
        ) : (
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="items">
              <AccordionTrigger className="text-sm font-medium">
                Items ({purchasedItemsCount}/{totalItemsCount} purchased)
              </AccordionTrigger>
              <AccordionContent>
                <ul className="space-y-3">
                  {sortedItems.map(item => (
                    <li key={item.id} className="flex items-center justify-between group">
                      <div className="flex items-center flex-1 min-w-0">
                        <Button variant="ghost" size="icon" className="h-8 w-8 mr-2 flex-shrink-0" onClick={() => onToggleItem(list.id, item.id)}>
                          {item.is_completed ? <CheckCircle2 className="h-5 w-5 text-green-500" /> : <Circle className="h-5 w-5 text-muted-foreground" />}
                        </Button>
                        <div className="w-6 mr-3 flex-shrink-0">
                          {getItemIcon(item)}
                        </div>
                        <span className={`flex-1 truncate ${item.is_completed ? 'line-through text-muted-foreground' : ''}`}>
                          {item.name}
                          {item.quantity && (
                            <span className="ml-2 text-xs text-muted-foreground">× {item.quantity}</span>
                          )}
                        </span>
                        {item.category && <Badge variant="outline" className="ml-2 flex-shrink-0">{item.category.name}</Badge>}
                      </div>
                      <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" onClick={() => onDeleteItem(list.id, item.id)}>
                        <XCircle className="h-5 w-5 text-destructive" />
                      </Button>
                    </li>
                  ))}
                </ul>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        )}
        <div className="mt-4">
          <AddItemForm listId={list.id} onAddItem={onAddItem} />
        </div>
      </CardContent>
    </Card>
  );
}
