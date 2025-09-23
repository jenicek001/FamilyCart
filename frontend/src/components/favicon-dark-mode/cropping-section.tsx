import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CropSettings, ProcessedImages, processImageForDarkMode, getOutlineWidthForSize } from '@/lib/favicon-dark-mode-processing';

interface CroppingSectionProps {
  sourceImage: string;
  cropSettings: CropSettings;
  setCropSettings: React.Dispatch<React.SetStateAction<CropSettings>>;
  processedImages: ProcessedImages;
  setProcessedImages: React.Dispatch<React.SetStateAction<ProcessedImages>>;
  canvasRef: React.RefObject<HTMLCanvasElement>;
}

export const CroppingSection: React.FC<CroppingSectionProps> = ({
  sourceImage,
  cropSettings,
  setCropSettings,
  processedImages,
  setProcessedImages,
  canvasRef
}) => {
  const processSingleSize = async (size: number) => {
    if (!sourceImage || !canvasRef.current) return;
    
    const outlineWidth = getOutlineWidthForSize(size);
    try {
      const dataUrl = await processImageForDarkMode(
        sourceImage,
        canvasRef.current,
        size,
        cropSettings[size.toString() as keyof CropSettings],
        outlineWidth
      );
      
      setProcessedImages(prev => ({
        ...prev,
        [`${size}x${size}-dark`]: dataUrl
      }));
    } catch (error) {
      console.error(`Error processing ${size}x${size}:`, error);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>2. Adjust Cropping for Each Size</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(cropSettings).map(([size, crop]) => (
            <div key={size} className="space-y-2">
              <Label htmlFor={`crop-${size}`} className="text-sm font-medium">
                {size}x{size}px Crop
                {size === '192' || size === '512' ? (
                  <span className="text-xs text-blue-600 block">Android Chrome</span>
                ) : size === '180' ? (
                  <span className="text-xs text-gray-600 block">Apple Touch</span>
                ) : (
                  <span className="text-xs text-gray-600 block">Standard</span>
                )}
              </Label>
              <div className="space-y-1">
                <Input
                  id={`crop-${size}`}
                  type="range"
                  min="0"
                  max="90"
                  value={crop}
                  onChange={(e) => setCropSettings(prev => ({
                    ...prev,
                    [size]: parseInt(e.target.value)
                  }))}
                  className="w-full"
                />
                <div className="text-xs text-center text-gray-600">
                  {crop}% crop
                </div>
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={() => processSingleSize(parseInt(size))}
                  className="w-full text-xs"
                >
                  Preview {size}x{size}
                </Button>
              </div>
              {/* Show preview if processed */}
              {processedImages[`${size}x${size}-dark`] && (
                <div className="border rounded p-2 bg-gray-50 text-center">
                  <img 
                    src={processedImages[`${size}x${size}-dark`]} 
                    alt={`${size}x${size} preview`}
                    className="mx-auto"
                    style={{ 
                      width: size === '512' ? '48px' : 
                             size === '192' ? '40px' : 
                             size === '180' ? '32px' : 
                             size === '64' ? '28px' :
                             size === '32' ? '24px' : '16px',
                      height: size === '512' ? '48px' : 
                              size === '192' ? '40px' : 
                              size === '180' ? '32px' : 
                              size === '64' ? '28px' :
                              size === '32' ? '24px' : '16px',
                      imageRendering: parseInt(size) <= 32 ? 'pixelated' : 'auto'
                    }}
                  />
                  <div className="text-xs text-gray-600 mt-1">Preview</div>
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="mt-4 text-xs text-gray-600 space-y-1">
          <p>• Higher values = more cropping (tighter focus on logo)</p>
          <p>• Lower values = less cropping (more padding around logo)</p>
          <p>• Recommended: 16px needs most crop, large sizes need least</p>
          <p>• Android Chrome icons (192x192, 512x512) for PWA support</p>
        </div>
      </CardContent>
    </Card>
  );
};