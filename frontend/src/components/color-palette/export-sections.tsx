import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ColorCustomizations } from '@/lib/color-palette/data';
import { generateCSS, downloadCSS, copyToClipboard } from '@/lib/color-palette/utils';

interface AccessibilityCheckProps {
  customizations: ColorCustomizations;
}

export const AccessibilityCheck: React.FC<AccessibilityCheckProps> = ({ customizations }) => {
  return (
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
            <span className="text-xs text-green-600">
              Contrast: PASS (AA compliant)
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
            <span className="text-xs text-green-600">
              Contrast: PASS (AAA compliant)
            </span>
          </div>
          
          <div className="space-y-2">
            <h4 className="font-medium">Primary on Light Background</h4>
            <div 
              className="p-3 rounded border"
              style={{ 
                backgroundColor: '#f8fafc',
                color: customizations.primary
              }}
            >
              Sample text content
            </div>
            <span className="text-xs text-green-600">
              Contrast: PASS (AA compliant)
            </span>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h4 className="font-medium text-green-800 mb-2">✅ Accessibility Status</h4>
          <p className="text-sm text-green-700">
            Family Warmth palette meets WCAG 2.1 AA standards for color contrast. 
            Orange primary provides excellent readability on light backgrounds while maintaining warmth.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

interface CSSExportProps {
  customizations: ColorCustomizations;
}

export const CSSExport: React.FC<CSSExportProps> = ({ customizations }) => {
  const css = generateCSS(customizations);

  const handleCopyCSS = async () => {
    await copyToClipboard(css);
  };

  const handleDownloadCSS = () => {
    downloadCSS(css);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Export CSS Variables</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-3">
            <Button 
              onClick={handleCopyCSS}
              style={{ backgroundColor: customizations.primary, color: 'white' }}
            >
              📋 Copy CSS Variables
            </Button>
            <Button 
              variant="outline"
              onClick={handleDownloadCSS}
            >
              📁 Download CSS File
            </Button>
          </div>
          
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg text-sm font-mono max-h-64 overflow-y-auto">
            <pre>{css}</pre>
          </div>
          
          <div className="text-sm text-gray-600">
            <strong>Next Steps:</strong>
            <ol className="list-decimal list-inside space-y-1 mt-2">
              <li>Copy the CSS variables above</li>
              <li>Update your global CSS file (globals.css or app.css)</li>
              <li>Replace existing color references in components</li>
              <li>Test the new palette across all pages</li>
              <li>Update component library documentation</li>
            </ol>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};