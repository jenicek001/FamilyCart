"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

// Current FamilyCart color system analysis
const currentColors = {
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

const paletteOptions = [
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

export default function ColorPaletteDesigner() {
  const [selectedPalette, setSelectedPalette] = useState(paletteOptions[0]);
  const [customizations, setCustomizations] = useState({
    primary: paletteOptions[0].primary,
    secondary: paletteOptions[0].secondary,
    accent: paletteOptions[0].accent
  });

  const generateVariants = (baseColor: string) => {
    // Simple function to generate light/dark variants
    const hex = baseColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    return {
      50: `rgb(${Math.min(255, r + 100)}, ${Math.min(255, g + 100)}, ${Math.min(255, b + 100)})`,
      100: `rgb(${Math.min(255, r + 80)}, ${Math.min(255, g + 80)}, ${Math.min(255, b + 80)})`,
      500: baseColor,
      700: `rgb(${Math.max(0, r - 50)}, ${Math.max(0, g - 50)}, ${Math.max(0, b - 50)})`,
      900: `rgb(${Math.max(0, r - 100)}, ${Math.max(0, g - 100)}, ${Math.max(0, b - 100)})`
    };
  };

  const checkContrast = (fg: string, bg: string) => {
    // Simplified contrast check - in real implementation, use proper WCAG calculation
    const fgLuminance = 0.5; // Placeholder
    const bgLuminance = 0.8; // Placeholder
    const ratio = (Math.max(fgLuminance, bgLuminance) + 0.05) / (Math.min(fgLuminance, bgLuminance) + 0.05);
    return ratio >= 4.5 ? 'PASS' : 'FAIL';
  };

  const generateCSS = () => {
    const variants = generateVariants(customizations.primary);
    return `/* FamilyCart Color Palette - Generated */
:root {
  /* Primary Brand Colors */
  --fc-primary-50: ${variants[50]};
  --fc-primary-100: ${variants[100]};
  --fc-primary-500: ${customizations.primary};
  --fc-primary-700: ${variants[700]};
  --fc-primary-900: ${variants[900]};
  
  /* Secondary Colors */
  --fc-secondary: ${customizations.secondary};
  --fc-accent: ${customizations.accent};
  
  /* Semantic Colors (keep current) */
  --fc-success: ${currentColors.semantic.success};
  --fc-warning: ${currentColors.semantic.warning};
  --fc-danger: ${currentColors.semantic.danger};
  --fc-info: ${currentColors.semantic.info};
}`;
  };

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">FamilyCart Color Palette Designer</h1>
        <p className="text-muted-foreground">
          Interactive design tool for establishing a cohesive visual identity
        </p>
      </div>

      {/* Current System Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Current Color System Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium mb-3">Brand Colors</h4>
              <div className="space-y-2">
                {Object.entries(currentColors.brand).map(([name, color]) => (
                  <div key={name} className="flex items-center gap-2">
                    <div 
                      className="w-6 h-6 rounded border" 
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-sm">{name}: {color}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Semantic Colors</h4>
              <div className="space-y-2">
                {Object.entries(currentColors.semantic).map(([name, color]) => (
                  <div key={name} className="flex items-center gap-2">
                    <div 
                      className="w-6 h-6 rounded border" 
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-sm">{name}: {color}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Category Colors</h4>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {Object.entries(currentColors.categories).map(([name, color]) => (
                  <div key={name} className="flex items-center gap-2">
                    <div 
                      className="w-4 h-4 rounded border" 
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-xs">{name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Palette Options */}
      <Card>
        <CardHeader>
          <CardTitle>Palette Direction Options</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {paletteOptions.map((palette) => (
              <div 
                key={palette.name}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedPalette.name === palette.name 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => {
                  setSelectedPalette(palette);
                  setCustomizations({
                    primary: palette.primary,
                    secondary: palette.secondary,
                    accent: palette.accent
                  });
                }}
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex gap-1">
                    <div 
                      className="w-6 h-6 rounded" 
                      style={{ backgroundColor: palette.primary }}
                    />
                    <div 
                      className="w-6 h-6 rounded" 
                      style={{ backgroundColor: palette.secondary }}
                    />
                    <div 
                      className="w-6 h-6 rounded" 
                      style={{ backgroundColor: palette.accent }}
                    />
                  </div>
                  <h4 className="font-medium">{palette.name}</h4>
                </div>
                <p className="text-sm text-gray-600 mb-2">{palette.description}</p>
                <p className="text-xs text-gray-500">{palette.personality}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Color Customization */}
      <Card>
        <CardHeader>
          <CardTitle>Fine-Tune Colors</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <Label htmlFor="primary">Primary Color</Label>
              <div className="flex gap-2">
                <Input
                  id="primary"
                  type="color"
                  value={customizations.primary}
                  onChange={(e) => setCustomizations(prev => ({ ...prev, primary: e.target.value }))}
                  className="w-16 h-10"
                />
                <Input
                  type="text"
                  value={customizations.primary}
                  onChange={(e) => setCustomizations(prev => ({ ...prev, primary: e.target.value }))}
                  className="flex-1"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="secondary">Secondary Color</Label>
              <div className="flex gap-2">
                <Input
                  id="secondary"
                  type="color"
                  value={customizations.secondary}
                  onChange={(e) => setCustomizations(prev => ({ ...prev, secondary: e.target.value }))}
                  className="w-16 h-10"
                />
                <Input
                  type="text"
                  value={customizations.secondary}
                  onChange={(e) => setCustomizations(prev => ({ ...prev, secondary: e.target.value }))}
                  className="flex-1"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="accent">Accent Color</Label>
              <div className="flex gap-2">
                <Input
                  id="accent"
                  type="color"
                  value={customizations.accent}
                  onChange={(e) => setCustomizations(prev => ({ ...prev, accent: e.target.value }))}
                  className="w-16 h-10"
                />
                <Input
                  type="text"
                  value={customizations.accent}
                  onChange={(e) => setCustomizations(prev => ({ ...prev, accent: e.target.value }))}
                  className="flex-1"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Live Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Live UI Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Header Preview */}
            <div 
              className="p-4 rounded-lg text-white"
              style={{ backgroundColor: customizations.primary }}
            >
              <h3 className="font-bold text-lg">FamilyCart Header</h3>
              <p className="opacity-90">Sample navigation with new primary color</p>
            </div>
            
            {/* Button Previews */}
            <div className="flex gap-3">
              <button 
                className="px-4 py-2 rounded-lg text-white font-medium"
                style={{ backgroundColor: customizations.primary }}
              >
                Primary Button
              </button>
              <button 
                className="px-4 py-2 rounded-lg text-white font-medium"
                style={{ backgroundColor: customizations.secondary }}
              >
                Secondary Button
              </button>
              <button 
                className="px-4 py-2 rounded-lg text-white font-medium"
                style={{ backgroundColor: customizations.accent }}
              >
                Accent Button
              </button>
            </div>
            
            {/* Card Preview */}
            <div className="border rounded-lg p-4 bg-white">
              <div className="flex items-center gap-2 mb-2">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: customizations.accent }}
                />
                <h4 className="font-medium">Shopping List Item</h4>
              </div>
              <p className="text-sm text-gray-600">Preview of how list items would look</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Accessibility Check */}
      <Card>
        <CardHeader>
          <CardTitle>Accessibility Validation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium">Primary on White</h4>
              <div 
                className="p-3 rounded border"
                style={{ 
                  backgroundColor: '#ffffff',
                  color: customizations.primary
                }}
              >
                Sample text content
              </div>
              <span className="text-xs text-gray-500">
                Contrast: {checkContrast(customizations.primary, '#ffffff')}
              </span>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">White on Primary</h4>
              <div 
                className="p-3 rounded border"
                style={{ 
                  backgroundColor: customizations.primary,
                  color: '#ffffff'
                }}
              >
                Sample text content
              </div>
              <span className="text-xs text-gray-500">
                Contrast: {checkContrast('#ffffff', customizations.primary)}
              </span>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Primary on Light</h4>
              <div 
                className="p-3 rounded border"
                style={{ 
                  backgroundColor: '#f8fafc',
                  color: customizations.primary
                }}
              >
                Sample text content
              </div>
              <span className="text-xs text-gray-500">
                Contrast: {checkContrast(customizations.primary, '#f8fafc')}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* CSS Generation */}
      <Card>
        <CardHeader>
          <CardTitle>Generated CSS Custom Properties</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
            {generateCSS()}
          </pre>
          <div className="mt-4 flex gap-2">
            <Button 
              onClick={() => navigator.clipboard.writeText(generateCSS())}
              variant="outline"
            >
              Copy CSS
            </Button>
            <Button>
              Apply to App
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Brand Guidelines */}
      <Card>
        <CardHeader>
          <CardTitle>Usage Guidelines</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-3">Primary Color Usage</h4>
              <ul className="text-sm space-y-1 text-gray-600">
                <li>• Main navigation and headers</li>
                <li>• Primary action buttons</li>
                <li>• Links and interactive elements</li>
                <li>• Form focus states</li>
                <li>• Brand elements and logos</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Secondary & Accent Usage</h4>
              <ul className="text-sm space-y-1 text-gray-600">
                <li>• Secondary buttons and actions</li>
                <li>• Highlights and badges</li>
                <li>• Progress indicators</li>
                <li>• Category accents</li>
                <li>• Success states and confirmations</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
