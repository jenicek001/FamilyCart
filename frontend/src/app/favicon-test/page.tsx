"use client";

export default function FaviconTestPage() {
  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Favicon Testing</h1>
        <p className="text-muted-foreground">Test favicon visibility and formats</p>
      </div>

      {/* Favicon Preview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* 16x16 Favicon */}
        <div className="border rounded-lg p-4 bg-white">
          <h3 className="font-medium mb-4">16x16 Browser Tab</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-2 p-2 bg-gray-100 rounded">
              <img src="/favicon-16x16.png" alt="16x16 favicon" className="w-4 h-4" />
              <span className="text-sm">FamilyCart - Dashboard</span>
            </div>
            <div className="text-xs text-gray-600">
              Must be clearly visible in browser tabs
            </div>
          </div>
        </div>

        {/* 32x32 App Icon */}
        <div className="border rounded-lg p-4 bg-white">
          <h3 className="font-medium mb-4">32x32 App Icon</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-2 bg-gray-100 rounded">
              <img src="/favicon-32x32.png" alt="32x32 icon" className="w-8 h-8" />
              <span className="text-sm">FamilyCart</span>
            </div>
            <div className="text-xs text-gray-600">
              Taskbar and bookmark visibility
            </div>
          </div>
        </div>

        {/* 64x64 Standard */}
        <div className="border rounded-lg p-4 bg-white">
          <h3 className="font-medium mb-4">64x64 Standard</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-3 bg-gray-100 rounded">
              <img src="/favicon-64x64.png" alt="64x64 icon" className="w-16 h-16" />
              <span className="text-sm">FamilyCart</span>
            </div>
            <div className="text-xs text-gray-600">
              Desktop and larger mobile contexts
            </div>
          </div>
        </div>

        {/* Apple Touch Icon */}
        <div className="border rounded-lg p-4 bg-white">
          <h3 className="font-medium mb-4">180x180 Apple Touch</h3>
          <div className="space-y-4">
            <div className="flex flex-col items-center gap-2 p-3 bg-gray-100 rounded">
              <img src="/apple-touch-icon.png" alt="Apple touch icon" className="w-16 h-16 rounded-xl border" />
              <span className="text-xs text-center">FamilyCart</span>
            </div>
            <div className="text-xs text-gray-600">
              iOS home screen icon
            </div>
          </div>
        </div>
      </div>

      {/* Background Testing */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">Background Testing</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          {/* Light Background */}
          <div className="border rounded-lg p-4 bg-white">
            <h3 className="font-medium mb-4">Light Background</h3>
            <div className="flex items-center gap-2 p-3 bg-gray-50 rounded">
              <img src="/favicon-32x32.png" alt="Light bg test" className="w-8 h-8" />
              <span className="text-sm">FamilyCart</span>
            </div>
          </div>

          {/* Dark Background */}
          <div className="border rounded-lg p-4 bg-gray-900 text-white">
            <h3 className="font-medium mb-4">Dark Background</h3>
            <div className="flex items-center gap-2 p-3 bg-gray-800 rounded">
              <img src="/favicon-32x32.png" alt="Dark bg test" className="w-8 h-8" />
              <span className="text-sm">FamilyCart</span>
            </div>
          </div>

          {/* Colored Background */}
          <div className="border rounded-lg p-4 bg-blue-600 text-white">
            <h3 className="font-medium mb-4">Colored Background</h3>
            <div className="flex items-center gap-2 p-3 bg-blue-700 rounded">
              <img src="/favicon-32x32.png" alt="Colored bg test" className="w-8 h-8" />
              <span className="text-sm">FamilyCart</span>
            </div>
          </div>
        </div>
      </div>

      {/* Generation Status */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="font-medium text-yellow-800 mb-2">🚧 Favicon Generation Status</h3>
        <div className="text-sm text-yellow-700 space-y-1">
          <p>✅ Favicon integration setup complete</p>
          <p>⏳ Optimized cart-family favicons need to be generated</p>
          <p>📝 Use the prompts in <code>/docs/FAVICON_GENERATION_GUIDE.md</code></p>
          <p>🎯 Focus on thick lines, reduced padding, and high contrast</p>
        </div>
      </div>

      {/* Browser Tab Simulation */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">Browser Tab Simulation</h2>
        <div className="bg-gray-100 rounded-lg p-4">
          <div className="flex items-center gap-2 text-sm">
            <img src="/favicon-16x16.png" alt="Tab favicon" className="w-4 h-4" />
            <span>FamilyCart - Shopping Lists</span>
            <span className="ml-auto text-gray-500">×</span>
          </div>
        </div>
      </div>
    </div>
  );
}
