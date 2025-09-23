import { ColorVariants, ColorCustomizations } from './data';

/**
 * Color utility functions for the FamilyCart palette designer
 */

/**
 * Generate color variants (light/dark) from a base color
 */
export const generateVariants = (baseColor: string): ColorVariants => {
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

/**
 * Check color contrast (simplified implementation)
 * In production, use proper WCAG calculation
 */
export const checkContrast = (fg: string, bg: string): 'PASS' | 'FAIL' => {
  // Simplified contrast check - in real implementation, use proper WCAG calculation
  const fgLuminance = 0.5; // Placeholder
  const bgLuminance = 0.8; // Placeholder
  const ratio = (Math.max(fgLuminance, bgLuminance) + 0.05) / (Math.min(fgLuminance, bgLuminance) + 0.05);
  return ratio >= 4.5 ? 'PASS' : 'FAIL';
};

/**
 * Generate CSS variables from color customizations
 */
export const generateCSS = (customizations: ColorCustomizations): string => {
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

/**
 * Download CSS as file
 */
export const downloadCSS = (css: string, filename: string = 'familycart-colors.css'): void => {
  const blob = new Blob([css], { type: 'text/css' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text: string): Promise<void> => {
  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    console.error('Failed to copy text: ', err);
  }
};