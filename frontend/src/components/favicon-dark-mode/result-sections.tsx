import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ProcessedImages, getFilenameForSize, downloadImage } from '@/lib/favicon-dark-mode-processing';

interface DarkModeTestSectionProps {
  processedImages: ProcessedImages;
  sourceImage: string | null;
}

export const DarkModeTestSection: React.FC<DarkModeTestSectionProps> = ({ 
  processedImages, 
  sourceImage 
}) => {
  const stepNumber = sourceImage ? '5' : '4';

  return (
    <Card>
      <CardHeader>
        <CardTitle>{stepNumber}. Dark Background Visibility Test</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* All Sizes Grid */}
          <div>
            <h4 className="font-medium mb-3">All Sizes on Different Backgrounds</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              
              {/* Dark Background Test */}
              <div className="border rounded p-4 bg-gray-900 text-white">
                <h5 className="font-medium mb-3 text-center">Dark Background</h5>
                <div className="space-y-3">
                  {['16x16', '32x32', '64x64', '180x180', '192x192', '512x512'].map((size) => {
                    const imageKey = `${size}-dark`;
                    if (!processedImages[imageKey]) return null;
                    
                    const displaySize = size === '512x512' ? '32px' : 
                                      size === '192x192' ? '28px' :
                                      size === '180x180' ? '24px' : 
                                      size === '64x64' ? '20px' : 
                                      size === '32x32' ? '18px' : '16px';
                    
                    return (
                      <div key={size} className="flex items-center gap-3 p-2 bg-gray-800 rounded">
                        <img 
                          src={processedImages[imageKey]} 
                          alt={`${size} dark test`} 
                          style={{ width: displaySize, height: displaySize }}
                        />
                        <span className="text-sm">{size} - FamilyCart</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Blue Background Test */}
              <div className="border rounded p-4 bg-blue-900 text-white">
                <h5 className="font-medium mb-3 text-center">Blue Background</h5>
                <div className="space-y-3">
                  {['16x16', '32x32', '64x64', '180x180', '192x192', '512x512'].map((size) => {
                    const imageKey = `${size}-dark`;
                    if (!processedImages[imageKey]) return null;
                    
                    const displaySize = size === '512x512' ? '32px' : 
                                      size === '192x192' ? '28px' :
                                      size === '180x180' ? '24px' : 
                                      size === '64x64' ? '20px' : 
                                      size === '32x32' ? '18px' : '16px';
                    
                    return (
                      <div key={size} className="flex items-center gap-3 p-2 bg-blue-800 rounded">
                        <img 
                          src={processedImages[imageKey]} 
                          alt={`${size} blue test`} 
                          style={{ width: displaySize, height: displaySize }}
                        />
                        <span className="text-sm">{size} - FamilyCart</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Navy Background Test */}
              <div className="border rounded p-4 bg-slate-800 text-white">
                <h5 className="font-medium mb-3 text-center">Navy Background</h5>
                <div className="space-y-3">
                  {['16x16', '32x32', '64x64', '180x180', '192x192', '512x512'].map((size) => {
                    const imageKey = `${size}-dark`;
                    if (!processedImages[imageKey]) return null;
                    
                    const displaySize = size === '512x512' ? '32px' : 
                                      size === '192x192' ? '28px' :
                                      size === '180x180' ? '24px' : 
                                      size === '64x64' ? '20px' : 
                                      size === '32x32' ? '18px' : '16px';
                    
                    return (
                      <div key={size} className="flex items-center gap-3 p-2 bg-slate-700 rounded">
                        <img 
                          src={processedImages[imageKey]} 
                          alt={`${size} navy test`} 
                          style={{ width: displaySize, height: displaySize }}
                        />
                        <span className="text-sm">{size} - FamilyCart</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Browser Context Examples */}
          <div>
            <h4 className="font-medium mb-3">Real Browser Context Examples</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* Browser Tab Simulation */}
              <div className="border rounded p-4 bg-gray-800 text-white">
                <h5 className="font-medium mb-2">Browser Tab (Dark Theme)</h5>
                <div className="bg-gray-700 p-2 rounded flex items-center gap-2 text-sm">
                  {processedImages['16x16-dark'] && (
                    <img src={processedImages['16x16-dark']} alt="tab favicon" className="w-4 h-4" />
                  )}
                  <span>FamilyCart - Shopping Lists</span>
                  <span className="ml-auto text-gray-400">×</span>
                </div>
              </div>

              {/* Android PWA Example */}
              <div className="border rounded p-4 bg-gray-900 text-white">
                <h5 className="font-medium mb-2">Android PWA Install</h5>
                <div className="grid grid-cols-3 gap-2">
                  {processedImages['192x192-dark'] && (
                    <div className="text-center">
                      <div className="bg-gray-700 rounded-lg p-2 mb-1">
                        <img src={processedImages['192x192-dark']} alt="android 192" className="w-8 h-8 mx-auto" />
                      </div>
                      <span className="text-xs">FamilyCart</span>
                    </div>
                  )}
                  {processedImages['512x512-dark'] && (
                    <div className="text-center">
                      <div className="bg-gray-700 rounded-lg p-3 mb-1">
                        <img src={processedImages['512x512-dark']} alt="android 512" className="w-10 h-10 mx-auto" />
                      </div>
                      <span className="text-xs">High-Res</span>
                    </div>
                  )}
                  <div className="text-center">
                    <div className="bg-gray-600 rounded-lg p-2 mb-1 w-12 h-12"></div>
                    <span className="text-xs">Other App</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

interface DownloadSectionProps {
  processedImages: ProcessedImages;
  sourceImage: string | null;
  onDownloadAll: () => void;
}

export const DownloadSection: React.FC<DownloadSectionProps> = ({ 
  processedImages, 
  sourceImage, 
  onDownloadAll 
}) => {
  const stepNumber = sourceImage ? '4' : '3';

  return (
    <Card>
      <CardHeader>
        <CardTitle>{stepNumber}. Download Dark Background Optimized Favicons</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Button onClick={onDownloadAll} className="w-full">
            Download All Dark Mode Favicons
          </Button>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(processedImages).map(([size, dataUrl]) => {
              const displaySize = size.replace('-dark', '');
              const isAndroid = displaySize === '192x192' || displaySize === '512x512';
              const isApple = displaySize === '180x180';
              
              return (
                <div key={size} className="text-center space-y-2">
                  <div className="border rounded p-4 bg-gray-50">
                    <img 
                      src={dataUrl} 
                      alt={`${displaySize} dark favicon`}
                      className="mx-auto"
                      style={{ 
                        width: displaySize === '512x512' ? '48px' : 
                               displaySize === '192x192' ? '40px' : 
                               displaySize === '180x180' ? '32px' : 
                               displaySize === '64x64' ? '28px' :
                               displaySize === '32x32' ? '24px' : '16px',
                        height: displaySize === '512x512' ? '48px' : 
                                displaySize === '192x192' ? '40px' : 
                                displaySize === '180x180' ? '32px' : 
                                displaySize === '64x64' ? '28px' :
                                displaySize === '32x32' ? '24px' : '16px',
                        imageRendering: parseInt(displaySize.split('x')[0]) <= 32 ? 'pixelated' : 'auto'
                      }}
                    />
                  </div>
                  <div className="text-sm font-medium">
                    {displaySize} Dark
                    {isAndroid && <span className="block text-xs text-blue-600">Android</span>}
                    {isApple && <span className="block text-xs text-gray-600">Apple</span>}
                  </div>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => {
                      const filename = getFilenameForSize(size);
                      downloadImage(dataUrl, filename);
                    }}
                  >
                    Download
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};