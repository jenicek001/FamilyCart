import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ColorCustomizations } from '@/lib/color-palette/data';

interface LivePreviewProps {
  customizations: ColorCustomizations;
  currentColors: {
    brand: { primary: string; primaryLight: string; primaryDark: string; };
    semantic: { success: string; warning: string; danger: string; info: string; };
    categories: Record<string, string>;
    neutrals: { background: string; cardBg: string; textPrimary: string; textSecondary: string; border: string; };
  };
}

export function LivePreview({ customizations, currentColors }: LivePreviewProps) {
  return (
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

          {/* Shopping List Preview */}
          <div className="border rounded-lg p-4 bg-white">
            <h4 className="font-medium mb-3" style={{ color: customizations.primary }}>
              🛒 Family Shopping List Preview
            </h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 rounded border-l-4" 
                   style={{ borderLeftColor: customizations.accent }}>
                <span>🥕 Carrots</span>
                <span className="text-sm px-2 py-1 rounded" 
                      style={{ backgroundColor: customizations.accent + '20', color: customizations.accent }}>
                  Produce
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded border-l-4" 
                   style={{ borderLeftColor: customizations.secondary }}>
                <span>🥛 Milk</span>
                <span className="text-sm px-2 py-1 rounded" 
                      style={{ backgroundColor: customizations.secondary + '20', color: customizations.secondary }}>
                  Dairy
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded border-l-4" 
                   style={{ borderLeftColor: customizations.primary }}>
                <span>🍞 Bread</span>
                <span className="text-sm px-2 py-1 rounded" 
                      style={{ backgroundColor: customizations.primary + '20', color: customizations.primary }}>
                  Bakery
                </span>
              </div>
            </div>
          </div>

          {/* Family Member Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="border rounded-lg p-3 bg-gradient-to-r" 
                 style={{ 
                   background: `linear-gradient(135deg, ${customizations.primary}10, ${customizations.accent}10)` 
                 }}>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm"
                     style={{ backgroundColor: customizations.primary }}>
                  👨
                </div>
                <div>
                  <div className="font-medium">Dad</div>
                  <div className="text-sm text-gray-600">3 items added</div>
                </div>
              </div>
            </div>
            <div className="border rounded-lg p-3 bg-gradient-to-r" 
                 style={{ 
                   background: `linear-gradient(135deg, ${customizations.secondary}10, ${customizations.primary}10)` 
                 }}>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm"
                     style={{ backgroundColor: customizations.secondary }}>
                  👩
                </div>
                <div>
                  <div className="font-medium">Mom</div>
                  <div className="text-sm text-gray-600">5 items added</div>
                </div>
              </div>
            </div>
            <div className="border rounded-lg p-3 bg-gradient-to-r" 
                 style={{ 
                   background: `linear-gradient(135deg, ${customizations.accent}10, ${customizations.secondary}10)` 
                 }}>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm"
                     style={{ backgroundColor: customizations.accent }}>
                  👧
                </div>
                <div>
                  <div className="font-medium">Sarah</div>
                  <div className="text-sm text-gray-600">1 item added</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};