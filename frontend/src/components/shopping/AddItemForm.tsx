"use client";

import type React from 'react';
import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PlusCircle, Zap, Loader2, Sparkles, ShoppingBasket } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import { icons } from 'lucide-react';

interface AddItemFormProps {
  listId: number;
  onAddItem: (listId: number, item: { name: string; quantity?: string; description?: string; category_name?: string; icon_name?: string }) => void;
}

// Helper to render a Lucide icon dynamically by name
const DynamicIcon = ({ name, ...props }: { name: string | null | undefined } & React.ComponentProps<typeof ShoppingBasket>) => {
  if (!name) return null; // Render nothing if no name

  const toPascalCase = (str: string) => 
    str.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join('');

  const IconComponent = icons[toPascalCase(name) as keyof typeof icons];

  if (!IconComponent) {
    return null; // Or a default icon
  }

  return <IconComponent {...props} />;
};


export default function AddItemForm({ listId, onAddItem }: AddItemFormProps) {
  const [itemName, setItemName] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [iconName, setIconName] = useState('');
  const [isCategorizing, setIsCategorizing] = useState(false);
  const [isSuggestingIcon, setIsSuggestingIcon] = useState(false);
  const { toast } = useToast();
  const { token } = useAuth();

  const handleSuggestCategory = async () => {
    if (!itemName) {
      toast({ title: "Item name required", description: "Please enter an item name to suggest a category.", variant: "destructive" });
      return;
    }
    setIsCategorizing(true);
    try {
      const response = await axios.post('/api/v1/ai/categorize-item', 
        { item_name: itemName },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const suggestedCategory = response.data.category_name;
      setCategory(suggestedCategory);
      toast({ title: "Category Suggested!", description: `Category: ${suggestedCategory}`});
    } catch (error) {
      console.error("Error suggesting category:", error);
      toast({ title: "AI Error", description: "Could not suggest a category at this time.", variant: "destructive" });
    } finally {
      setIsCategorizing(false);
    }
  };

  const handleSuggestIcon = async () => {
    if (!itemName) {
      toast({ title: "Item name required", description: "Please enter an item name to suggest an icon.", variant: "destructive" });
      return;
    }
    setIsSuggestingIcon(true);
    try {
      const response = await axios.post('/api/v1/ai/suggest-icon', 
        { item_name: itemName, category_name: category || undefined },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const suggestedIcon = response.data.icon_name;
      setIconName(suggestedIcon);
      toast({ title: "Icon Suggested!", description: `Icon: ${suggestedIcon}`});
    } catch (error) {
      console.error("Error suggesting icon:", error);
      toast({ title: "AI Error", description: "Could not suggest an icon at this time.", variant: "destructive" });
    } finally {
      setIsSuggestingIcon(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!itemName.trim()) {
      toast({ title: "Item name required", variant: "destructive" });
      return;
    }
    
    onAddItem(listId, {
      name: itemName,
      quantity: quantity,
      description: description,
      category_name: category,
      icon_name: iconName,
    });

    // Reset form
    setItemName('');
    setQuantity('1');
    setDescription('');
    setCategory('');
    setIconName('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg bg-muted/40">
      <div className="space-y-2">
        <Label htmlFor={`item-name-${listId}`}>Item Name</Label>
        <Input 
          id={`item-name-${listId}`}
          placeholder="e.g., Organic Milk" 
          value={itemName}
          onChange={(e) => setItemName(e.target.value)}
          required 
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor={`quantity-${listId}`}>Quantity</Label>
          <Input 
            id={`quantity-${listId}`}
            placeholder="e.g., 1 gallon" 
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor={`category-${listId}`}>Category (Optional)</Label>
          <div className="flex items-center gap-2">
            <Input 
              id={`category-${listId}`}
              placeholder="e.g., Dairy" 
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
            <Button type="button" size="sm" onClick={handleSuggestCategory} disabled={isCategorizing || !itemName} className="w-48 shrink-0">
              {isCategorizing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Zap className="mr-2 h-4 w-4" />}
              Suggest Category
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor={`description-${listId}`}>Description (Optional)</Label>
        <Textarea 
          id={`description-${listId}`}
          placeholder="Any specific details..." 
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <Label>Icon (Optional)</Label>
        <div className="flex items-center gap-2">
          <Input 
            id={`icon-${listId}`}
            placeholder="e.g., 'milk' or 'apple'"
            value={iconName}
            onChange={(e) => setIconName(e.target.value)}
            className="w-full"
          />
          <Button type="button" size="sm" onClick={handleSuggestIcon} disabled={isSuggestingIcon || !itemName} className="w-48 shrink-0">
            {isSuggestingIcon ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
            Suggest Icon
          </Button>
        </div>
        {iconName && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground pt-2">
             <span className="font-medium">Preview:</span>
            <DynamicIcon name={iconName} className="h-5 w-5" />
            <span>{iconName}</span>
          </div>
        )}
      </div>

      <Button type="submit" className="w-full">
        <PlusCircle className="mr-2 h-4 w-4" /> Add Item
      </Button>
    </form>
  );
}
