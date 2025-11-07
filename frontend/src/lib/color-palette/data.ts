/**
 * Color palette data and definitions for FamilyCart
 */

// Current FamilyCart color system analysis
export const currentColors = {
  brand: {
    primary: '#3b82f6',      // Blue-500
    primaryLight: '#dbeafe', // Blue-100
    primaryDark: '#1d4ed8',  // Blue-700
  },
  semantic: {
    success: '#22c55e',      // Green-500
    warning: '#f59e0b',      // Amber-500
    danger: '#ef4444',       // Red-500
    info: '#06b6d4',         // Cyan-500
  },
  categories: {
    produce: '#22c55e',      // Green
    dairy: '#3b82f6',        // Blue  
    meat: '#ef4444',         // Red
    pantry: '#f59e0b',       // Amber
    frozen: '#06b6d4',       // Cyan
    bakery: '#8b5cf6',       // Violet
    household: '#6b7280',    // Gray
    personal: '#ec4899',     // Pink
    beverages: '#10b981',    // Emerald
    snacks: '#f97316',       // Orange
  },
  neutrals: {
    background: '#f8fafc',   // Slate-50
    cardBg: '#ffffff',       // White
    textPrimary: '#0f172a',  // Slate-900
    textSecondary: '#64748b', // Slate-500
    border: '#e2e8f0',       // Slate-200
  }
};

export interface PaletteOption {
  name: string;
  description: string;
  primary: string;
  secondary: string;
  accent: string;
  personality: string;
}

export const paletteOptions: PaletteOption[] = [
  {
    name: 'Current (Blue Primary)',
    description: 'Keep existing blue-based palette with optimizations',
    primary: '#3b82f6',
    secondary: '#22c55e',
    accent: '#f59e0b',
    personality: 'Professional, trustworthy, familiar'
  },
  {
    name: 'Family Warmth',
    description: 'Warm orange primary with blue secondary for family comfort',
    primary: '#f59e0b',
    secondary: '#3b82f6', 
    accent: '#22c55e',
    personality: 'Warm, inviting, family-focused'
  },
  {
    name: 'Fresh & Natural',
    description: 'Green primary inspired by fresh produce and family nutrition',
    primary: '#22c55e',
    secondary: '#3b82f6',
    accent: '#f59e0b',
    personality: 'Fresh, healthy, organized'
  },
  {
    name: 'Modern Collaboration',
    description: 'Purple primary for innovation with familiar blue secondary',
    primary: '#8b5cf6',
    secondary: '#3b82f6',
    accent: '#22c55e',
    personality: 'Modern, innovative, collaborative'
  }
];

export interface ColorCustomizations {
  primary: string;
  secondary: string;
  accent: string;
}

export interface ColorVariants {
  50: string;
  100: string;
  500: string;
  700: string;
  900: string;
}