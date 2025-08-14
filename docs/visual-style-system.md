# Visual Style System - FamilyCart

This document describes the visual design system implemented for FamilyCart, based on modern UI principles and Stitch-inspired styling.

## Design Principles

### Typography
- **Primary Font**: Plus Jakarta Sans (headings and body text)
- **Fallback Font**: Noto Sans
- **Font Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Color Palette

#### Primary Colors
- **Primary Blue**: `#3b82f6` (primary-600) - Main brand color for buttons and accents
- **Primary Light**: `#dbeafe` (primary-100) - Light backgrounds and hover states
- **Primary Dark**: `#1d4ed8` (primary-700) - Dark variants and active states

#### Semantic Colors
- **Success Green**: `#22c55e` - Completed items, success messages
- **Warning Yellow**: `#f59e0b` - Warnings and alerts
- **Danger Red**: `#ef4444` - Errors and destructive actions
- **Info Cyan**: `#06b6d4` - Information and neutral actions

#### Category Colors
Each shopping list category has a unique color and icon:
- **Produce**: `#22c55e` (Green) - `local_florist`
- **Dairy**: `#3b82f6` (Blue) - `water_drop`
- **Meat & Seafood**: `#ef4444` (Red) - `restaurant`
- **Pantry**: `#f59e0b` (Orange) - `inventory_2`
- **Frozen**: `#06b6d4` (Cyan) - `ac_unit`
- **Bakery**: `#8b5cf6` (Purple) - `bakery_dining`
- **Household**: `#6b7280` (Gray) - `cleaning_services`
- **Personal Care**: `#ec4899` (Pink) - `face`
- **Beverages**: `#10b981` (Emerald) - `local_drink`
- **Snacks**: `#f97316` (Orange) - `cookie`

#### Neutral Colors
- **Background**: `#f8fafc` (slate-50) - Main background
- **Card Background**: `#ffffff` - White cards and surfaces
- **Text Primary**: `#0f172a` (slate-900) - Main text
- **Text Secondary**: `#64748b` (slate-500) - Secondary text
- **Border**: `#e2e8f0` (slate-200) - Default borders

## Layout System

### Container
- **Max Width**: `1024px` (max-w-4xl)
- **Padding**: `16px` on mobile, `24px` on desktop
- **Centered**: Horizontally centered with auto margins

### Spacing Scale
- **xs**: `4px` (1)
- **sm**: `8px` (2)
- **md**: `16px` (4)
- **lg**: `24px` (6)
- **xl**: `32px` (8)
- **2xl**: `48px` (12)

### Border Radius
- **Small**: `8px` (rounded-lg)
- **Medium**: `12px` (rounded-xl)
- **Large**: `16px` (rounded-2xl)

## Component Library

### Buttons

#### Primary Button
```tsx
<button className="btn-primary">
  <span className="material-icons text-sm mr-2">add</span>
  Add Item
</button>
```

#### Secondary Button
```tsx
<button className="btn-secondary">
  Cancel
</button>
```

#### Outline Button
```tsx
<button className="btn-outline">
  Edit
</button>
```

### Cards

#### Basic Card
```tsx
<div className="card p-4">
  Card content
</div>
```

#### Interactive Card
```tsx
<div className="card card-hover p-4">
  Hoverable card content
</div>
```

### Inputs

#### Text Input
```tsx
<input className="input-primary" placeholder="Enter text..." />
```

#### Search Input with Icon
```tsx
<div className="relative">
  <span className="material-icons absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400">
    search
  </span>
  <input className="input-primary pl-10" placeholder="Search..." />
</div>
```

## Icons

### Material Icons Implementation
All icons use Google's Material Icons font:

```html
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet" />
```

### Common Icons
- **Navigation**: `menu`, `arrow_back`, `close`
- **Actions**: `add`, `edit`, `delete`, `check`, `clear`
- **Categories**: `local_florist`, `restaurant`, `inventory_2`, etc.
- **Status**: `check_circle`, `radio_button_unchecked`, `warning`, `error`

### Usage
```tsx
<span className="material-icons text-primary-600">add</span>
```

## Animations

### Keyframes
- **Fade In**: Smooth opacity transition
- **Slide Up**: Slides from bottom with fade
- **Bounce Soft**: Subtle bounce effect

### Usage
```tsx
<div className="animate-fade-in">Content</div>
<div className="animate-slide-up">Modal content</div>
```

## Shadows

### Shadow Scale
- **Soft**: `0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)`
- **Medium**: `0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)`
- **Strong**: `0 10px 40px -10px rgba(0, 0, 0, 0.15), 0 4px 25px -5px rgba(0, 0, 0, 0.1)`

### Usage
```tsx
<div className="shadow-soft">Light shadow</div>
<div className="shadow-medium">Medium shadow</div>
<div className="shadow-strong">Strong shadow</div>
```

## Shopping List Components

### ShoppingListView
Main container component with:
- Sticky header with gradient background
- Centered max-width container
- Search and filter functionality
- Grouped items (pending/completed)
- Empty state handling

### ShoppingListItem
Individual item card featuring:
- Category icon with color coding
- Inline editing capabilities
- Hover actions (edit, delete)
- Completion toggle
- Drag handle for reordering

### AddItemForm
Form component with:
- Auto-category detection
- Real-time preview
- Validation and feedback
- Material Icons integration

### SearchAndFilter
Filter interface with:
- Icon-led search input
- Dropdown category filter
- Active filter indicators
- Clear all functionality

## Accessibility

### Focus States
All interactive elements have visible focus rings:
```css
focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
```

### Color Contrast
All text meets WCAG AA standards:
- Primary text: 21:1 contrast ratio
- Secondary text: 7:1 contrast ratio
- Interactive elements: 4.5:1 minimum

### Screen Reader Support
- Semantic HTML structure
- ARIA labels on interactive elements
- Meaningful alt text for icons
- Proper heading hierarchy

## Responsive Design

### Breakpoints
- **Mobile**: `< 640px`
- **Tablet**: `640px - 1024px`
- **Desktop**: `> 1024px`

### Grid System
Uses CSS Grid and Flexbox:
```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
```

### Mobile-First Approach
All styles are mobile-first with progressive enhancement:
```tsx
<div className="p-4 sm:p-6 lg:p-8">
```

## Implementation Notes

### Tailwind Configuration
Custom design tokens are defined in `tailwind.config.js`:
- Extended color palette
- Custom font families
- Additional spacing values
- Custom shadows and animations

### CSS Organization
Styles are organized in layers:
1. **Base**: Reset and fundamental styles
2. **Components**: Reusable component classes
3. **Utilities**: Tailwind utilities and overrides

### Performance
- Tailwind CSS purges unused styles in production
- Material Icons are loaded from Google CDN
- Fonts are preloaded for better performance
- Critical styles are inlined where possible

## Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Graceful Degradation
- CSS Grid falls back to Flexbox
- Custom properties have fallback values
- Progressive enhancement for advanced features
