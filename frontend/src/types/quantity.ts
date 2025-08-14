// Unit and Quantity Types for the FamilyCart Application

export enum UnitCategory {
  COUNT = 'count',
  WEIGHT = 'weight',
  VOLUME = 'volume',
  LENGTH = 'length',
  AREA = 'area',
  CUSTOM = 'custom'
}

export interface Unit {
  id: string;
  name: string;
  symbol: string;
  category: UnitCategory;
  baseUnit?: string;
  conversionFactor?: number;
  isDefault?: boolean;
  locale?: string;
}

export interface Quantity {
  value: number;
  unit: Unit;
  displayText?: string; // For custom/free-form text like "a bunch of", "some"
}

export interface QuantityInput {
  value: number | string;
  unitId: string;
  displayText?: string;
}

// Standard units available in the system
export const STANDARD_UNITS: Unit[] = [
  // COUNT Units
  { id: 'piece', name: 'piece', symbol: 'pc', category: UnitCategory.COUNT, isDefault: true },
  { id: 'pieces', name: 'pieces', symbol: 'pcs', category: UnitCategory.COUNT },
  { id: 'item', name: 'item', symbol: 'item', category: UnitCategory.COUNT },
  { id: 'items', name: 'items', symbol: 'items', category: UnitCategory.COUNT },
  { id: 'pack', name: 'pack', symbol: 'pack', category: UnitCategory.COUNT },
  { id: 'packs', name: 'packs', symbol: 'packs', category: UnitCategory.COUNT },
  { id: 'bottle', name: 'bottle', symbol: 'bottle', category: UnitCategory.COUNT },
  { id: 'bottles', name: 'bottles', symbol: 'bottles', category: UnitCategory.COUNT },
  { id: 'can', name: 'can', symbol: 'can', category: UnitCategory.COUNT },
  { id: 'cans', name: 'cans', symbol: 'cans', category: UnitCategory.COUNT },
  { id: 'box', name: 'box', symbol: 'box', category: UnitCategory.COUNT },
  { id: 'boxes', name: 'boxes', symbol: 'boxes', category: UnitCategory.COUNT },
  { id: 'bag', name: 'bag', symbol: 'bag', category: UnitCategory.COUNT },
  { id: 'bags', name: 'bags', symbol: 'bags', category: UnitCategory.COUNT },

  // WEIGHT Units
  { id: 'g', name: 'gram', symbol: 'g', category: UnitCategory.WEIGHT, baseUnit: 'g', conversionFactor: 1, isDefault: true },
  { id: 'kg', name: 'kilogram', symbol: 'kg', category: UnitCategory.WEIGHT, baseUnit: 'g', conversionFactor: 1000 },
  { id: 'lb', name: 'pound', symbol: 'lb', category: UnitCategory.WEIGHT, baseUnit: 'g', conversionFactor: 453.592, locale: 'US' },
  { id: 'oz', name: 'ounce', symbol: 'oz', category: UnitCategory.WEIGHT, baseUnit: 'g', conversionFactor: 28.3495, locale: 'US' },

  // VOLUME Units
  { id: 'ml', name: 'milliliter', symbol: 'ml', category: UnitCategory.VOLUME, baseUnit: 'ml', conversionFactor: 1, isDefault: true },
  { id: 'l', name: 'liter', symbol: 'l', category: UnitCategory.VOLUME, baseUnit: 'ml', conversionFactor: 1000 },
  { id: 'dl', name: 'deciliter', symbol: 'dl', category: UnitCategory.VOLUME, baseUnit: 'ml', conversionFactor: 100 },
  { id: 'cl', name: 'centiliter', symbol: 'cl', category: UnitCategory.VOLUME, baseUnit: 'ml', conversionFactor: 10 },
  { id: 'fl_oz', name: 'fluid ounce', symbol: 'fl oz', category: UnitCategory.VOLUME, baseUnit: 'ml', conversionFactor: 29.5735, locale: 'US' },
  { id: 'cup', name: 'cup', symbol: 'cup', category: UnitCategory.VOLUME, baseUnit: 'ml', conversionFactor: 236.588, locale: 'US' },
  { id: 'pint', name: 'pint', symbol: 'pt', category: UnitCategory.VOLUME, baseUnit: 'ml', conversionFactor: 473.176, locale: 'US' },
  { id: 'quart', name: 'quart', symbol: 'qt', category: UnitCategory.VOLUME, baseUnit: 'ml', conversionFactor: 946.353, locale: 'US' },
  { id: 'gallon', name: 'gallon', symbol: 'gal', category: UnitCategory.VOLUME, baseUnit: 'ml', conversionFactor: 3785.41, locale: 'US' },

  // LENGTH Units
  { id: 'm', name: 'meter', symbol: 'm', category: UnitCategory.LENGTH, baseUnit: 'm', conversionFactor: 1, isDefault: true },
  { id: 'cm', name: 'centimeter', symbol: 'cm', category: UnitCategory.LENGTH, baseUnit: 'm', conversionFactor: 0.01 },
  { id: 'mm', name: 'millimeter', symbol: 'mm', category: UnitCategory.LENGTH, baseUnit: 'm', conversionFactor: 0.001 },
  { id: 'ft', name: 'foot', symbol: 'ft', category: UnitCategory.LENGTH, baseUnit: 'm', conversionFactor: 0.3048, locale: 'US' },
  { id: 'in', name: 'inch', symbol: 'in', category: UnitCategory.LENGTH, baseUnit: 'm', conversionFactor: 0.0254, locale: 'US' },
];

// Context-aware unit suggestions based on item category
export const getCategoryUnits = (category: string): Unit[] => {
  const categoryUnitMap: Record<string, string[]> = {
    'Dairy': ['l', 'ml', 'piece', 'pack', 'bottle'],
    'Meat': ['kg', 'g', 'lb', 'piece', 'pack'],
    'Produce': ['kg', 'g', 'piece', 'bag', 'pack'],
    'Beverages': ['l', 'ml', 'bottle', 'can', 'pack'],
    'Pantry': ['kg', 'g', 'pack', 'box', 'bag'],
    'Frozen': ['kg', 'g', 'pack', 'box', 'bag'],
    'Bakery': ['piece', 'kg', 'g', 'pack', 'bag'],
    'Personal Care': ['piece', 'ml', 'l', 'pack', 'bottle'],
    'Household': ['piece', 'pack', 'bottle', 'l', 'ml'],
    'Other': ['piece', 'pack']
  };

  const unitIds = categoryUnitMap[category] || categoryUnitMap['Other'];
  return STANDARD_UNITS.filter(unit => unitIds.includes(unit.id));
};

// Get locale-specific units
export const getLocaleUnits = (locale: string): Unit[] => {
  const localePreferences: Record<string, string[]> = {
    'en-US': ['piece', 'lb', 'oz', 'cup', 'fl_oz', 'gallon', 'ft', 'in'],
    'en-GB': ['piece', 'kg', 'g', 'l', 'ml', 'cm', 'm'],
    'cs-CZ': ['piece', 'kg', 'g', 'l', 'ml', 'dl', 'cm', 'm'],
    'de-DE': ['piece', 'kg', 'g', 'l', 'ml', 'cm', 'm'],
    'fr-FR': ['piece', 'kg', 'g', 'l', 'ml', 'cm', 'm'],
  };

  const preferredUnits = localePreferences[locale] || localePreferences['en-US'];
  
  return STANDARD_UNITS.filter(unit => 
    !unit.locale || 
    unit.locale === locale.split('-')[1] || 
    preferredUnits.includes(unit.id)
  );
};

// Find unit by ID
export const findUnitById = (unitId: string): Unit | undefined => {
  return STANDARD_UNITS.find(unit => unit.id === unitId);
};

// Format quantity for display
export const formatQuantity = (quantity: Quantity, format: 'compact' | 'verbose' = 'compact'): string => {
  if (quantity.displayText) {
    return quantity.displayText;
  }
  
  const symbol = format === 'compact' ? quantity.unit.symbol : quantity.unit.name;
  const pluralName = quantity.value > 1 ? (quantity.unit.name + 's') : quantity.unit.name;
  const displayName = format === 'compact' ? symbol : pluralName;
  
  return `${quantity.value} ${displayName}`;
};

// Parse quantity text input
export const parseQuantityText = (input: string, category?: string): QuantityInput | null => {
  if (!input || input.trim() === '') {
    return null;
  }

  const trimmed = input.trim();
  
  // Patterns for different quantity formats
  const patterns = [
    // Standard "number unit" format: "2 kg", "1.5 l", "3 pieces"
    /^(\d+(?:\.\d+)?)\s*(kg|g|l|ml|pc|pcs|pieces?|items?|bottles?|cans?|packs?|boxes?|bags?|lb|oz|cup|fl\s?oz|pint|quart|gallon|ft|in|cm|mm|m|dl|cl)$/i,
    
    // Just a number: "2", "1.5"
    /^(\d+(?:\.\d+)?)$/,
    
    // Custom expressions: "a bunch of", "some", "many"
    /^(a\s+(?:bunch|handful|few|couple|dozen)|some|many|several)(?:\s+of)?$/i,
    
    // Fractions: "1/2 cup", "2-3 pieces"
    /^(\d+[-\/]\d+)\s*(.*?)$/i,
  ];

  // Try standard format first
  const standardMatch = trimmed.match(patterns[0]);
  if (standardMatch) {
    const value = parseFloat(standardMatch[1]);
    const unitText = standardMatch[2].toLowerCase();
    
    // Find matching unit
    const unit = STANDARD_UNITS.find(u => 
      u.id === unitText || 
      u.name === unitText || 
      u.symbol === unitText ||
      (unitText.endsWith('s') && u.name === unitText.slice(0, -1))
    );
    
    if (unit) {
      return {
        value: value,
        unitId: unit.id,
      };
    }
  }

  // Try just number
  const numberMatch = trimmed.match(patterns[1]);
  if (numberMatch) {
    const value = parseFloat(numberMatch[1]);
    return {
      value: value,
      unitId: 'piece', // Default to pieces for plain numbers
    };
  }

  // Try custom expressions
  const customMatch = trimmed.match(patterns[2]);
  if (customMatch) {
    return {
      value: 1,
      unitId: 'piece',
      displayText: customMatch[1],
    };
  }

  // Try fractions
  const fractionMatch = trimmed.match(patterns[3]);
  if (fractionMatch) {
    return {
      value: 1,
      unitId: 'piece',
      displayText: trimmed,
    };
  }

  // If nothing matches, treat as custom display text
  return {
    value: 1,
    unitId: 'piece',
    displayText: trimmed,
  };
};

// Convert quantity to legacy format (for backward compatibility)
export const quantityToLegacyFormat = (quantity: Quantity): string => {
  if (quantity.displayText) {
    return quantity.displayText;
  }
  
  if (quantity.unit.id === 'piece' && quantity.value === 1) {
    return '1';
  }
  
  return `${quantity.value} ${quantity.unit.symbol}`;
};

// Convert legacy quantity string to structured format
export const legacyFormatToQuantity = (legacyQuantity: string): Quantity | null => {
  const parsed = parseQuantityText(legacyQuantity);
  if (!parsed) return null;
  
  const unit = findUnitById(parsed.unitId);
  if (!unit) return null;
  
  return {
    value: typeof parsed.value === 'string' ? parseFloat(parsed.value) : parsed.value,
    unit: unit,
    displayText: parsed.displayText,
  };
};
