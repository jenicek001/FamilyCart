# Quantity Units Implementation Plan

## Overview
This document outlines the implementation of a comprehensive quantity units system for the FamilyCart application, replacing the current simple string-based quantity field with a structured, extensible, and internationalized solution.

## Current State Analysis

### Existing Implementation
- **Database**: `quantity: Mapped[str | None] = mapped_column(String(50))` - Free-form text field
- **Frontend**: Simple number input with no unit specification
- **User Experience**: Basic quantity display like "2" or "5" without units
- **Limitations**: No unit context, no validation, no internationalization

### User Requirements (from USER_STORIES.md)
- **FR009**: Support for pieces, grams, liters/milliliters, pounds, local alternatives
- **FR028**: Natural language parsing ("2 kg of apples", "1 liter of milk with no lactose")
- **Internationalization**: Multi-language support for different regions
- **Context-aware**: Smart suggestions based on item categories

## Proposed Solution Architecture

### 1. Data Model Design

#### Core Interfaces
```typescript
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
  displayText?: string; // For custom expressions like "a bunch of"
}
```

#### Database Schema Changes
```sql
-- Phase 1: Add new structured columns
ALTER TABLE item ADD COLUMN quantity_value DECIMAL(10,3);
ALTER TABLE item ADD COLUMN quantity_unit_id VARCHAR(20);
ALTER TABLE item ADD COLUMN quantity_display_text VARCHAR(100);

-- Phase 2: Create units reference table
CREATE TABLE unit (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    category VARCHAR(20) NOT NULL,
    base_unit VARCHAR(20),
    conversion_factor DECIMAL(15,6),
    is_default BOOLEAN DEFAULT FALSE,
    locale VARCHAR(10)
);
```

### 2. Unit Categories and Definitions

#### COUNT Units
- **Basic**: piece, pieces, item, items
- **Packaging**: pack, packs, box, boxes, bag, bags
- **Containers**: bottle, bottles, can, cans
- **Special**: dozen, pair, bunch, handful

#### WEIGHT Units
- **Metric**: g, kg (base units)
- **Imperial**: lb, oz (US market)
- **Regional**: stone (UK)

#### VOLUME Units
- **Metric**: ml, l, dl, cl (base units)
- **Imperial**: fl oz, cup, pint, quart, gallon (US market)
- **Regional variations**: Different cup sizes by region

#### LENGTH Units
- **Metric**: mm, cm, m (base units)
- **Imperial**: in, ft (US market)

#### AREA Units
- **Metric**: cm², m² (base units)
- **Imperial**: in², ft² (US market)

### 3. Smart Features

#### Context-Aware Unit Suggestions
```typescript
const categoryUnitMap = {
  'Dairy': ['l', 'ml', 'piece', 'pack'],
  'Meat': ['kg', 'g', 'lb', 'piece'],
  'Produce': ['kg', 'g', 'piece', 'bag'],
  'Beverages': ['l', 'ml', 'bottle', 'can'],
  'Pantry': ['kg', 'g', 'pack', 'box'],
  'Frozen': ['kg', 'g', 'pack', 'box'],
  'Bakery': ['piece', 'kg', 'g', 'pack'],
  'Personal Care': ['piece', 'ml', 'l', 'pack'],
  'Household': ['piece', 'pack', 'bottle', 'l'],
  'Other': ['piece', 'pack']
};
```

#### Natural Language Processing
- Parse inputs like "2 kg", "1.5 liters", "a bunch of"
- Support fractions: "1/2 cup", "2-3 pieces"
- Handle ranges: "2-3 kg", "4-6 bottles"
- Recognize custom expressions: "a handful", "some", "many"

#### Localization Support
```typescript
const localePreferences = {
  'en-US': ['piece', 'lb', 'oz', 'cup', 'fl_oz', 'gallon'],
  'en-GB': ['piece', 'kg', 'g', 'l', 'ml', 'stone'],
  'cs-CZ': ['piece', 'kg', 'g', 'l', 'ml', 'dl'],
  'de-DE': ['piece', 'kg', 'g', 'l', 'ml'],
  'fr-FR': ['piece', 'kg', 'g', 'l', 'ml'],
};
```

### 4. User Interface Design

#### Enhanced Quantity Input Component
```typescript
interface QuantityInputProps {
  value: QuantityInput;
  onChange: (quantity: QuantityInput) => void;
  suggestedUnits?: Unit[];
  allowFreeText?: boolean;
  category?: string;
  placeholder?: string;
}
```

#### Display Formats
- **Compact**: "2 kg", "1.5 L", "3 pcs"
- **Verbose**: "2 kilograms", "1.5 liters", "3 pieces"
- **Custom**: "a bunch of", "some", "several"

### 5. Implementation Phases

#### Phase 1: Foundation (Week 1-2)
1. **Database Migration**
   - Add new quantity columns to item table
   - Create units reference table
   - Populate with initial unit definitions

2. **Core Types & Utilities**
   - Create TypeScript interfaces and enums
   - Implement unit conversion functions
   - Build quantity parsing utilities

3. **Backend API Updates**
   - Update item schemas to support new quantity structure
   - Maintain backward compatibility with existing quantity field

#### Phase 2: UI Components (Week 3-4)
1. **Quantity Input Component**
   - Smart dropdown with unit suggestions
   - Free-text input for custom expressions
   - Category-aware unit filtering

2. **Display Components**
   - Enhanced quantity display in item lists
   - Responsive design for mobile/desktop
   - Accessibility improvements

3. **Integration**
   - Update ShoppingListItem component
   - Update AddItemForm components
   - Implement in item editing flows

#### Phase 3: Smart Features (Week 5-6)
1. **Natural Language Processing**
   - Implement quantity text parsing
   - Support for fractions and ranges
   - Handle custom expressions

2. **Context-Aware Suggestions**
   - Category-based unit recommendations
   - User preference learning
   - Recently used units prioritization

3. **Localization**
   - Locale-specific unit preferences
   - Translated unit names
   - Regional measurement standards

#### Phase 4: Advanced Features (Week 7-8)
1. **Unit Conversions**
   - Automatic conversion between compatible units
   - Display alternative measurements
   - Smart rounding and precision

2. **Analytics & Optimization**
   - Usage tracking for unit preferences
   - Performance optimization
   - A/B testing for UX improvements

3. **Migration & Cleanup**
   - Data migration from old quantity field
   - Remove legacy code
   - Update documentation

### 6. Technical Implementation Details

#### Database Migration Script
```sql
-- Create migration file: add_structured_quantity_to_items.sql
BEGIN;

-- Add new columns
ALTER TABLE item ADD COLUMN quantity_value DECIMAL(10,3);
ALTER TABLE item ADD COLUMN quantity_unit_id VARCHAR(20);
ALTER TABLE item ADD COLUMN quantity_display_text VARCHAR(100);

-- Create units table
CREATE TABLE unit (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    category VARCHAR(20) NOT NULL,
    base_unit VARCHAR(20),
    conversion_factor DECIMAL(15,6),
    is_default BOOLEAN DEFAULT FALSE,
    locale VARCHAR(10)
);

-- Insert default units
INSERT INTO unit (id, name, symbol, category, base_unit, conversion_factor, is_default) VALUES
('piece', 'piece', 'pc', 'count', NULL, NULL, true),
('kg', 'kilogram', 'kg', 'weight', 'g', 1000, false),
('g', 'gram', 'g', 'weight', 'g', 1, true),
('l', 'liter', 'l', 'volume', 'ml', 1000, false),
('ml', 'milliliter', 'ml', 'volume', 'ml', 1, true);
-- ... more units

-- Migrate existing data
UPDATE item SET 
    quantity_value = CASE 
        WHEN quantity ~ '^\d+(\.\d+)?$' THEN quantity::DECIMAL
        ELSE NULL 
    END,
    quantity_unit_id = CASE 
        WHEN quantity ~ '^\d+(\.\d+)?$' THEN 'piece'
        ELSE NULL 
    END,
    quantity_display_text = CASE 
        WHEN quantity ~ '^\d+(\.\d+)?$' THEN NULL
        ELSE quantity 
    END
WHERE quantity IS NOT NULL;

COMMIT;
```

#### Backend Model Updates
```python
# app/models/item.py
class Item(Base):
    # ... existing fields ...
    
    # New structured quantity fields
    quantity_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    quantity_unit_id: Mapped[str | None] = mapped_column(String(20))
    quantity_display_text: Mapped[str | None] = mapped_column(String(100))
    
    # Keep old field for migration period
    quantity: Mapped[str | None] = mapped_column(String(50))
    
    # Relationship to unit
    unit: Mapped[Optional["Unit"]] = relationship("Unit", foreign_keys=[quantity_unit_id])

class Unit(Base):
    __tablename__ = "unit"
    
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    base_unit: Mapped[str | None] = mapped_column(String(20))
    conversion_factor: Mapped[Decimal | None] = mapped_column(Numeric(15, 6))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    locale: Mapped[str | None] = mapped_column(String(10))
```

#### Frontend Implementation
```typescript
// utils/units.ts
export const parseQuantityText = (input: string, category?: string): QuantityInput | null => {
  // Parse "2 kg", "1.5 L", "3 pieces", "a bunch of"
  const patterns = [
    /^(\d+(?:\.\d+)?)\s*(kg|g|l|ml|pc|pieces?|items?|bottles?|cans?|packs?|boxes?|bags?)$/i,
    /^(\d+(?:\.\d+)?)\s*(lb|oz|fl\s?oz|cup|pint|quart|gallon|ft|in)$/i,
    /^(a\s+(?:bunch|handful|few|couple|dozen)|some|many|several)(?:\s+of)?$/i,
    /^(\d+[-\/]\d+)\s*(.*?)$/i,
  ];
  
  // Implementation logic here
  return null;
};

export const formatQuantity = (quantity: Quantity, format: 'compact' | 'verbose' = 'compact'): string => {
  if (quantity.displayText) {
    return quantity.displayText;
  }
  
  const symbol = format === 'compact' ? quantity.unit.symbol : quantity.unit.name;
  return `${quantity.value} ${symbol}`;
};

// components/ui/QuantityInput.tsx
export const QuantityInput: React.FC<QuantityInputProps> = ({ 
  value, 
  onChange, 
  suggestedUnits = [],
  allowFreeText = true,
  category,
  placeholder = "Enter quantity..."
}) => {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  const handleInputChange = (text: string) => {
    setInputValue(text);
    
    // Try to parse structured quantity
    const parsed = parseQuantityText(text, category);
    if (parsed) {
      onChange(parsed);
    }
    
    // Show suggestions if typing
    setShowSuggestions(text.length > 0);
  };
  
  return (
    <div className="relative">
      <input
        type="text"
        value={inputValue}
        onChange={(e) => handleInputChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
      />
      
      {showSuggestions && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
          {suggestedUnits.map(unit => (
            <button
              key={unit.id}
              onClick={() => handleUnitSelect(unit)}
              className="w-full px-3 py-2 text-left hover:bg-gray-100"
            >
              {unit.name} ({unit.symbol})
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
```

### 7. Testing Strategy

#### Unit Tests
- Quantity parsing functions
- Unit conversion calculations
- Validation logic
- Edge cases (empty, invalid inputs)

#### Integration Tests
- API endpoints with new quantity structure
- Database migrations
- Frontend component interactions

#### User Acceptance Tests
- Natural language input scenarios
- Cross-browser compatibility
- Mobile responsiveness
- Accessibility compliance

### 8. Performance Considerations

#### Database Optimization
- Index on quantity_unit_id for faster lookups
- Efficient migration script for large datasets
- Query optimization for quantity-based filtering

#### Frontend Performance
- Lazy loading of unit definitions
- Debounced search/parsing
- Memoized conversion calculations
- Optimized re-renders

### 9. Rollback Plan

#### Migration Rollback
- Keep old quantity field during transition
- Ability to revert database changes
- Feature flags for gradual rollout

#### Data Integrity
- Validation before migration
- Backup strategies
- Monitoring for data corruption

### 10. Success Metrics

#### User Experience
- Reduced input time for quantities
- Increased usage of unit specifications
- Lower error rates in quantity entry

#### Technical Metrics
- API response times
- Database query performance
- Frontend rendering performance

#### Business Metrics
- User adoption of new features
- Reduction in support tickets
- Improved data quality

## Next Steps

1. **Review and Approval**: Stakeholder review of this implementation plan
2. **Environment Setup**: Prepare development environment for new features
3. **Database Design**: Finalize database schema and migration strategy
4. **Prototype Development**: Create initial proof-of-concept for core functionality
5. **Implementation**: Begin Phase 1 development following the outlined timeline

This comprehensive implementation plan ensures a robust, scalable, and user-friendly quantity units system that meets current requirements while providing a foundation for future enhancements.
