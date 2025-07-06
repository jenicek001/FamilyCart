"use client";

import { FamilyCartLogo, LogoIconOnly, LogoWithText } from '@/components/ui/Logo';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function LogoTestPage() {
  const variants = [
    { key: 'cart-family', name: 'Cart + Family', description: 'Shopping cart with family figures' },
    { key: 'connected-containers', name: 'Connected Containers', description: 'Multiple baskets in network formation' },
    { key: 'list', name: 'List Focus', description: 'Checklist and shopping elements' },
    { key: 'logo', name: 'Primary Logo', description: 'Main logo design' },
    { key: 'tech-cart', name: 'Tech Cart', description: 'Shopping cart with technology elements' },
  ] as const;

  const sizes = [
    { key: 'sm', name: 'Small' },
    { key: 'md', name: 'Medium' },
    { key: 'lg', name: 'Large' },
    { key: 'xl', name: 'Extra Large' },
  ] as const;

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">FamilyCart Logo Testing</h1>
        <p className="text-muted-foreground">Testing all generated logo variants and sizes</p>
      </div>

      {/* Logo Variants Overview */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Logo Variants</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {variants.map((variant) => (
            <Card key={variant.key}>
              <CardHeader>
                <CardTitle className="text-lg">{variant.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{variant.description}</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-center p-4 bg-gray-50 rounded">
                  <LogoWithText variant={variant.key as any} size="lg" />
                </div>
                <div className="flex items-center justify-center p-4 bg-gray-900 rounded">
                  <LogoWithText variant={variant.key as any} size="lg" className="text-white" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Size Testing */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Size Testing (Primary Logo)</h2>
        <Card>
          <CardContent className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {sizes.map((size) => (
                <div key={size.key} className="text-center space-y-2">
                  <h3 className="font-medium">{size.name}</h3>
                  <div className="flex justify-center p-4 bg-gray-50 rounded">
                    <LogoWithText variant="logo" size={size.key as any} />
                  </div>
                  <div className="flex justify-center p-2 bg-gray-100 rounded">
                    <LogoIconOnly variant="logo" size={size.key as any} />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Header Context Testing */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Header Context Testing</h2>
        <div className="space-y-4">
          {variants.map((variant) => (
            <Card key={variant.key}>
              <CardHeader>
                <CardTitle>{variant.name} in Header Context</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-card border-b border-border shadow-sm p-4 rounded">
                  <div className="container mx-auto h-16 flex items-center justify-between">
                    <LogoWithText variant={variant.key as any} size="lg" href="#" />
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">Menu items would be here</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Favicon Preview */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Favicon Size Testing</h2>
        <Card>
          <CardContent className="p-6">
            <div className="grid grid-cols-4 md:grid-cols-8 gap-4">
              {variants.map((variant) => (
                <div key={variant.key} className="text-center space-y-2">
                  <h4 className="text-xs font-medium">{variant.name}</h4>
                  <div className="flex justify-center p-2 bg-gray-50 rounded border">
                    <LogoIconOnly variant={variant.key as any} size="sm" />
                  </div>
                  <div className="flex justify-center p-1 bg-gray-100 rounded border">
                    <div className="w-4 h-4 relative">
                      <FamilyCartLogo 
                        variant={variant.key as any} 
                        size="sm" 
                        showText={false}
                        className="w-4 h-4"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Recommendations */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle>Implementation Recommendations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p><strong>Header Logo:</strong> Use "lg" size with text for main navigation</p>
            <p><strong>Favicon:</strong> Choose the variant that works best at 16x16px (icon only)</p>
            <p><strong>Mobile:</strong> Consider "md" size for smaller screens</p>
            <p><strong>Loading Screen:</strong> Use "xl" size for splash screens</p>
            <p><strong>Email Templates:</strong> Use "md" or "lg" with full branding</p>
          </CardContent>
        </Card>
      </section>

      {/* Smart Selection Demo - Cart Family Optimization */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="text-blue-900">🎯 Selected: Cart + Family Logo with Smart Optimization</CardTitle>
        </CardHeader>
        <CardContent className="text-blue-800">
          <div className="space-y-4">
            <p><strong>Primary Choice:</strong> cart-family variant represents family collaboration perfectly!</p>
            <p><strong>Optimization Strategy:</strong> Smart size-based variant selection implemented.</p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div className="bg-white p-4 rounded border">
                <h4 className="font-medium mb-2">Large Sizes (lg, xl)</h4>
                <FamilyCartLogo variant="cart-family" size="lg" showText={true} />
                <p className="text-xs mt-2">Full cart-family logo with text</p>
              </div>
              
              <div className="bg-white p-4 rounded border">
                <h4 className="font-medium mb-2">Medium Sizes (md)</h4>
                <FamilyCartLogo variant="cart-family" size="md" showText={false} />
                <p className="text-xs mt-2">Cart-family icon only</p>
              </div>
              
              <div className="bg-white p-4 rounded border">
                <h4 className="font-medium mb-2">Small Sizes (sm) - Auto-Optimized</h4>
                <FamilyCartLogo variant="cart-family" size="sm" showText={false} />
                <p className="text-xs mt-2">Automatically switches to 'list' variant for clarity</p>
              </div>
            </div>
            
            <div className="bg-yellow-100 p-3 rounded mt-4">
              <p className="text-sm"><strong>Next Step:</strong> Generate optimized favicon versions (16x16, 32x32) with thicker lines and reduced padding for cart-family logo.</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
