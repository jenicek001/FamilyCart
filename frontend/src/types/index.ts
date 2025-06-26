export interface User {
  id: number;
  email: string;
  full_name: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface Category {
  id: number;
  name: string;
}

export interface ShoppingListItem {
  id: number;
  name: string;
  is_completed: boolean;
  shopping_list_id: number;
  owner_id: number;
  created_at: string; // ISO 8601 date string
  updated_at: string; // ISO 8601 date string
  category_id?: number | null;
  category?: Category | null;
  quantity?: number | null;
  description?: string | null;
  notes?: string | null;
  icon_name?: string | null;
}

// Alias for compatibility
export type Item = ShoppingListItem;

export interface ShoppingList {
  id: number;
  name: string;
  owner_id: number;
  created_at: string; // ISO 8601 date string
  updated_at: string; // ISO 8601 date string
  icon?: string | null; // Shopping list icon (placeholder for future AI generation)
  items: ShoppingListItem[];
  members: User[];
}
