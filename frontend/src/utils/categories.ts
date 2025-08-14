/**
 * Category utilities for shopping list items
 * Provides category colors, icons, and mapping functions
 */

export interface CategoryConfig {
  name: string;
  color: string;
  icon: string;
}

export const CATEGORY_CONFIGS: Record<string, CategoryConfig> = {
  produce: {
    name: 'Produce',
    color: '#22c55e',
    icon: 'local_florist'
  },
  dairy: {
    name: 'Dairy',
    color: '#3b82f6',
    icon: 'water_drop'
  },
  meat: {
    name: 'Meat & Seafood',
    color: '#ef4444',
    icon: 'restaurant'
  },
  pantry: {
    name: 'Pantry',
    color: '#f59e0b',
    icon: 'inventory_2'
  },
  frozen: {
    name: 'Frozen',
    color: '#06b6d4',
    icon: 'ac_unit'
  },
  bakery: {
    name: 'Bakery',
    color: '#8b5cf6',
    icon: 'bakery_dining'
  },
  household: {
    name: 'Household',
    color: '#6b7280',
    icon: 'cleaning_services'
  },
  personal: {
    name: 'Personal Care',
    color: '#ec4899',
    icon: 'face'
  },
  beverages: {
    name: 'Beverages',
    color: '#10b981',
    icon: 'local_drink'
  },
  snacks: {
    name: 'Snacks',
    color: '#f97316',
    icon: 'cookie'
  },
  other: {
    name: 'Other',
    color: '#64748b',
    icon: 'category'
  }
};

/**
 * Get the color for a given category
 */
export function getCategoryColor(category: string | undefined): string {
  if (!category) return CATEGORY_CONFIGS.other.color;
  
  const normalizedCategory = category.toLowerCase().trim();
  return CATEGORY_CONFIGS[normalizedCategory]?.color || CATEGORY_CONFIGS.other.color;
}

/**
 * Get the Material Icons name for a given category
 */
export function getCategoryIcon(category: string | undefined): string {
  if (!category) return CATEGORY_CONFIGS.other.icon;
  
  const normalizedCategory = category.toLowerCase().trim();
  return CATEGORY_CONFIGS[normalizedCategory]?.icon || CATEGORY_CONFIGS.other.icon;
}

/**
 * Get the display name for a given category
 */
export function getCategoryDisplayName(category: string | undefined): string {
  if (!category) return CATEGORY_CONFIGS.other.name;
  
  const normalizedCategory = category.toLowerCase().trim();
  return CATEGORY_CONFIGS[normalizedCategory]?.name || category;
}

/**
 * Get all available categories
 */
export function getAllCategories(): CategoryConfig[] {
  return Object.values(CATEGORY_CONFIGS);
}

/**
 * Infer category from item name (basic implementation)
 * In a real application, this would use AI/ML
 */
export function inferCategory(itemName: string): string {
  const name = itemName.toLowerCase();
  
  // Produce
  if (/apple|banana|orange|lettuce|tomato|carrot|onion|potato|fruit|vegetable|spinach|broccoli/.test(name)) {
    return 'produce';
  }
  
  // Dairy
  if (/milk|cheese|yogurt|butter|cream|egg/.test(name)) {
    return 'dairy';
  }
  
  // Meat
  if (/chicken|beef|pork|fish|salmon|turkey|ham|bacon|meat/.test(name)) {
    return 'meat';
  }
  
  // Pantry
  if (/rice|pasta|bread|cereal|flour|sugar|salt|oil|sauce|can|jar/.test(name)) {
    return 'pantry';
  }
  
  // Frozen
  if (/frozen|ice cream|pizza/.test(name)) {
    return 'frozen';
  }
  
  // Beverages
  if (/water|juice|soda|coffee|tea|beer|wine|drink/.test(name)) {
    return 'beverages';
  }
  
  // Household
  if (/detergent|soap|paper|towel|cleaner|toilet|trash/.test(name)) {
    return 'household';
  }
  
  // Personal
  if (/shampoo|toothpaste|deodorant|lotion/.test(name)) {
    return 'personal';
  }
  
  return 'other';
}

/**
 * Get category color class for Tailwind CSS styling
 */
export function getCategoryColorClass(categoryName?: string): string {
  if (!categoryName) return 'bg-gray-100 text-gray-600';
  
  const key = categoryName.toLowerCase().replace(/\s+/g, '').replace(/&/g, '');
  
  const colorClasses: Record<string, string> = {
    produce: 'bg-green-100 text-green-600',
    dairy: 'bg-blue-100 text-blue-600', 
    'dairyeggs': 'bg-blue-100 text-blue-600',
    meat: 'bg-red-100 text-red-600',
    'meatseafood': 'bg-red-100 text-red-600',
    pantry: 'bg-orange-100 text-orange-600',
    frozen: 'bg-cyan-100 text-cyan-600',
    bakery: 'bg-yellow-100 text-yellow-700',
    household: 'bg-indigo-100 text-indigo-600',
    personal: 'bg-pink-100 text-pink-600',
    'personalcare': 'bg-pink-100 text-pink-600',
    beverages: 'bg-teal-100 text-teal-600',
    snacks: 'bg-purple-100 text-purple-600',
    other: 'bg-gray-100 text-gray-600'
  };
  
  return colorClasses[key] || 'bg-gray-100 text-gray-600';
}
