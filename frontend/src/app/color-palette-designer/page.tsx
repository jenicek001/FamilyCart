"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  currentColors, 
  paletteOptions, 
  ColorCustomizations, 
  PaletteOption 
} from '@/lib/color-palette/data';
import { generateVariants } from '@/lib/color-palette/utils';
import { LivePreview } from '@/components/color-palette/live-preview';
import { AccessibilityCheck, CSSExport } from '@/components/color-palette/export-sections';

export default function ColorPaletteDesigner() {
  const [selectedPalette, setSelectedPalette] = useState<PaletteOption>(paletteOptions[1]); // Family Warmth
  const [customizations, setCustomizations] = useState<ColorCustomizations>({
    primary: paletteOptions[1].primary,   // #f59e0b - Warm Orange
    secondary: paletteOptions[1].secondary, // #3b82f6 - Trusted Blue
    accent: paletteOptions[1].accent      // #22c55e - Fresh Green
  });

  const checkContrast = (fg: string, bg: string) => {
    // Simplified contrast check - in real implementation, use proper WCAG calculation
    const fgLuminance = 0.5; // Placeholder
    const bgLuminance = 0.8; // Placeholder
    const ratio = (Math.max(fgLuminance, bgLuminance) + 0.05) / (Math.min(fgLuminance, bgLuminance) + 0.05);
    return ratio >= 4.5 ? 'PASS' : 'FAIL';
  };

  const generateCSS = () => {
    const primaryVariants = generateVariants(customizations.primary);
    const secondaryVariants = generateVariants(customizations.secondary);
    const accentVariants = generateVariants(customizations.accent);
    
    return `/* FamilyCart Family Warmth Color Palette - Generated ${new Date().toISOString().split('T')[0]} */
:root {
  /* Primary Brand Colors (Warm Orange) */
  --fc-primary-50: ${primaryVariants[50]};
  --fc-primary-100: ${primaryVariants[100]};
  --fc-primary-500: ${customizations.primary};
  --fc-primary-700: ${primaryVariants[700]};
  --fc-primary-900: ${primaryVariants[900]};
  
  /* Secondary Colors (Trusted Blue) */
  --fc-secondary-50: ${secondaryVariants[50]};
  --fc-secondary-100: ${secondaryVariants[100]};
  --fc-secondary-500: ${customizations.secondary};
  --fc-secondary-700: ${secondaryVariants[700]};
  --fc-secondary-900: ${secondaryVariants[900]};
  
  /* Accent Colors (Fresh Green) */
  --fc-accent-50: ${accentVariants[50]};
  --fc-accent-100: ${accentVariants[100]};
  --fc-accent-500: ${customizations.accent};
  --fc-accent-700: ${accentVariants[700]};
  --fc-accent-900: ${accentVariants[900]};
  
  /* Semantic Colors (enhanced for family context) */
  --fc-success: ${customizations.accent};
  --fc-warning: ${customizations.primary};
  --fc-danger: #ef4444;
  --fc-info: ${customizations.secondary};
  
  /* Family-focused category colors */
  --fc-category-produce: ${customizations.accent};
  --fc-category-dairy: ${customizations.secondary};
  --fc-category-meat: #ef4444;
  --fc-category-pantry: ${customizations.primary};
  --fc-category-frozen: #06b6d4;
  --fc-category-bakery: #8b5cf6;
  --fc-category-household: #6b7280;
  --fc-category-personal: #ec4899;
  --fc-category-beverages: #10b981;
  --fc-category-snacks: #f97316;
  
  /* UI Colors */
  --fc-background: #f8fafc;
  --fc-card-bg: #ffffff;
  --fc-text-primary: #0f172a;
  --fc-text-secondary: #64748b;
  --fc-border: #e2e8f0;
  --fc-border-hover: #cbd5e1;
}

/* Dark mode overrides */
@media (prefers-color-scheme: dark) {
  :root {
    --fc-background: #0f172a;
    --fc-card-bg: #1e293b;
    --fc-text-primary: #f1f5f9;
    --fc-text-secondary: #94a3b8;
    --fc-border: #334155;
    --fc-border-hover: #475569;
  }
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
      <LivePreview customizations={customizations} currentColors={currentColors} />

      {/* Accessibility Check */}
      <AccessibilityCheck customizations={customizations} />

      {/* CSS Export */}
      <CSSExport customizations={customizations} />
    </div>
  );
}
