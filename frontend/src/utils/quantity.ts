// Utility functions for working with quantities in the FamilyCart app

import { 
  Quantity, 
  QuantityInput, 
  parseQuantityText, 
  findUnitById, 
  formatQuantity,
  STANDARD_UNITS,
  getCategoryUnits,
  UnitCategory
} from '../types/quantity';
import { ShoppingListItem } from '../types';

/**
 * Get the display quantity for an item, handling both legacy and structured formats
 */
export const getItemQuantityDisplay = (item: ShoppingListItem): string => {
  // If we have structured quantity data, use it
  if (item.quantity_value && item.quantity_unit_id) {
    const unit = findUnitById(item.quantity_unit_id);
    if (unit) {
      const quantity: Quantity = {
        value: item.quantity_value,
        unit: unit,
        displayText: item.quantity_display_text || undefined
      };
      return formatQuantity(quantity);
    }
  }
  
  // If we have display text, use it
  if (item.quantity_display_text) {
    return item.quantity_display_text;
  }
  
  // Fall back to legacy quantity field
  if (item.quantity) {
    return item.quantity;
  }
  
  // Default to "1" for items without quantity
  return '1';
};

/**
 * Get the editable quantity for an item (for input fields)
 */
export const getItemQuantityForEdit = (item: ShoppingListItem): string => {
  // If we have display text, use it for editing
  if (item.quantity_display_text) {
    return item.quantity_display_text;
  }
  
  // If we have structured quantity data, format it
  if (item.quantity_value && item.quantity_unit_id) {
    const unit = findUnitById(item.quantity_unit_id);
    if (unit) {
      return `${item.quantity_value} ${unit.symbol}`;
    }
  }
  
  // Fall back to legacy quantity field
  if (item.quantity) {
    return item.quantity;
  }
  
  // Default to "1" for items without quantity
  return '1';
};

/**
 * Convert user input to structured quantity format for API calls
 */
export const parseUserQuantityInput = (input: string, categoryName?: string): QuantityInput | null => {
  if (!input || input.trim() === '') {
    return null;
  }
  
  return parseQuantityText(input, categoryName);
};

/**
 * Get suggested units for a category
 */
export const getSuggestedUnits = (categoryName?: string): Array<{id: string, name: string, symbol: string, category: string}> => {
  if (!categoryName) {
    // Default suggestions for items without category
    return [
      { id: 'piece', name: 'piece', symbol: 'pc', category: 'count' },
      { id: 'pack', name: 'pack', symbol: 'pack', category: 'count' },
      { id: 'kg', name: 'kilogram', symbol: 'kg', category: 'weight' },
      { id: 'l', name: 'liter', symbol: 'l', category: 'volume' },
    ];
  }
  
  const categoryUnits = getCategoryUnits(categoryName);
  return categoryUnits.map(unit => ({
    id: unit.id,
    name: unit.name,
    symbol: unit.symbol,
    category: unit.category
  }));
};

/**
 * Smart quantity parsing with category context
 */
export const smartParseQuantity = (input: string, categoryName?: string): {
  value: number;
  unitId: string;
  displayText?: string;
  confidence: number; // 0-1 scale
} | null => {
  const parsed = parseUserQuantityInput(input, categoryName);
  if (!parsed) return null;
  
  let confidence = 0.5; // Base confidence
  
  // Increase confidence if we found a matching unit
  const unit = findUnitById(parsed.unitId);
  if (unit) {
    confidence += 0.3;
    
    // Increase confidence if unit matches category
    if (categoryName) {
      const categoryUnits = getCategoryUnits(categoryName);
      if (categoryUnits.some(u => u.id === unit.id)) {
        confidence += 0.2;
      }
    }
  }
  
  // Decrease confidence for display text (custom input)
  if (parsed.displayText) {
    confidence -= 0.2;
  }
  
  return {
    value: typeof parsed.value === 'string' ? parseFloat(parsed.value) : parsed.value,
    unitId: parsed.unitId,
    displayText: parsed.displayText,
    confidence: Math.max(0, Math.min(1, confidence))
  };
};

/**
 * Get unit suggestions based on partial input
 */
export const getUnitSuggestions = (partialInput: string, categoryName?: string): Array<{
  id: string;
  name: string;
  symbol: string;
  category: string;
}> => {
  const query = partialInput.toLowerCase();
  
  // Get category-specific units first
  const categoryUnits = categoryName ? getCategoryUnits(categoryName) : [];
  const allUnits = [...categoryUnits, ...STANDARD_UNITS];
  
  // Remove duplicates
  const uniqueUnits = allUnits.filter((unit, index, self) => 
    index === self.findIndex(u => u.id === unit.id)
  );
  
  return uniqueUnits
    .filter(unit => 
      unit.name.toLowerCase().includes(query) || 
      unit.symbol.toLowerCase().includes(query) ||
      unit.id.toLowerCase().includes(query)
    )
    .map(unit => ({
      id: unit.id,
      name: unit.name,
      symbol: unit.symbol,
      category: unit.category
    }))
    .slice(0, 10); // Limit to 10 suggestions
};

/**
 * Format quantity for different contexts
 */
export const formatQuantityForContext = (
  item: ShoppingListItem, 
  context: 'list' | 'edit' | 'compact' | 'verbose'
): string => {
  const quantity = getItemQuantityDisplay(item);
  
  switch (context) {
    case 'list':
      return quantity;
    case 'edit':
      return getItemQuantityForEdit(item);
    case 'compact':
      return quantity;
    case 'verbose':
      // For verbose format, try to expand abbreviations
      if (item.quantity_value && item.quantity_unit_id) {
        const unit = findUnitById(item.quantity_unit_id);
        if (unit) {
          const pluralName = item.quantity_value > 1 ? (unit.name + 's') : unit.name;
          return `${item.quantity_value} ${pluralName}`;
        }
      }
      return quantity;
    default:
      return quantity;
  }
};

/**
 * Validate quantity input
 */
export const validateQuantityInput = (input: string): {
  isValid: boolean;
  error?: string;
  parsed?: QuantityInput;
} => {
  if (!input || input.trim() === '') {
    return { isValid: false, error: 'Quantity cannot be empty' };
  }
  
  const parsed = parseQuantityText(input);
  if (!parsed) {
    return { isValid: false, error: 'Invalid quantity format' };
  }
  
  // Check if the value is reasonable
  const value = typeof parsed.value === 'string' ? parseFloat(parsed.value) : parsed.value;
  if (isNaN(value) || value <= 0) {
    return { isValid: false, error: 'Quantity must be a positive number' };
  }
  
  if (value > 10000) {
    return { isValid: false, error: 'Quantity seems unusually large' };
  }
  
  return { isValid: true, parsed };
};
