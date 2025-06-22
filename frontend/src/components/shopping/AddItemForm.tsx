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
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg bg-card shadow">
      <h3 className="text-lg font-medium font-headline">Add New Item</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-1">
          <Label htmlFor="itemName">Item Name</Label>
          <Input
            id="itemName"
            value={itemName}
            onChange={(e) => setItemName(e.target.value)}
            placeholder="e.g., Apples"
            required
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="quantity">Quantity</Label>
          <Input
            id="quantity"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="e.g., 1 kg, 2 packs"
          />
        </div>
      </div>
      <div className="space-y-1">
        <Label htmlFor="description">Description (Optional)</Label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Any specific details, like 'Granny Smith' or 'Lactose-free'"
          rows={2}
        />
      </div>
       <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-1">
          <Label htmlFor="category">Category (Optional)</Label>
          <div className="flex items-center gap-2">
            <Input
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g., Produce"
            />
            <Button type="button" variant="outline" size="icon" onClick={handleSuggestCategory} disabled={isCategorizing || !itemName} aria-label="Suggest Category">
              {isCategorizing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
            </Button>
          </div>
        </div>
        <div className="space-y-1">
          <Label htmlFor="icon">Icon (Optional)</Label>
          <div className="flex items-center gap-2">
             <div className="relative w-full">
              <Input
                id="icon"
                value={iconName}
                onChange={(e) => setIconName(e.target.value)}
                placeholder="e.g., apple"
              />
              <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
                <DynamicIcon name={iconName} className="h-5 w-5 text-muted-foreground" />
              </div>
            </div>
            <Button type="button" variant="outline" size="icon" onClick={handleSuggestIcon} disabled={isSuggestingIcon || !itemName} aria-label="Suggest Icon">
              {isSuggestingIcon ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>
      <Button type="submit" className="w-full">
        <PlusCircle className="mr-2 h-4 w-4" /> Add Item
      </Button>
    </form>
  );
}
