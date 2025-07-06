"use client";

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function FaviconDarkModeProcessor() {
  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [processedImages, setProcessedImages] = useState<{[key: string]: string}>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Cropping controls for each size
  const [cropSettings, setCropSettings] = useState({
    '16': 80,
    '32': 30,
    '64': 15,
    '180': 10,
    '192': 8,
    '512': 5
  });

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSourceImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const processImageForDarkMode = (size: number, cropPercentage: number, outlineWidth: number = 2): Promise<string> => {
    return new Promise((resolve, reject) => {
      if (!sourceImage || !canvasRef.current) {
        reject('No source image or canvas');
        return;
      }

      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject('No canvas context');
        return;
      }

      const img = new Image();
      img.onload = () => {
        try {
          // Calculate crop dimensions
          const cropAmount = Math.min(img.width, img.height) * (cropPercentage / 100);
          const cropSize = Math.min(img.width, img.height) - (cropAmount * 2);
          const cropX = (img.width - cropSize) / 2;
          const cropY = (img.height - cropSize) / 2;

          // Set canvas size
          canvas.width = size;
          canvas.height = size;

          // Clear canvas
          ctx.clearRect(0, 0, size, size);

          // Improve rendering quality
          ctx.imageSmoothingEnabled = true;
          ctx.imageSmoothingQuality = 'high';

          // Create a temporary canvas for outline effect
          const tempCanvas = document.createElement('canvas');
          const tempCtx = tempCanvas.getContext('2d');
          if (!tempCtx) {
            reject('No temp canvas context');
            return;
          }
          
          tempCanvas.width = size;
          tempCanvas.height = size;

          // Draw the image to temp canvas first
          tempCtx.drawImage(
            img,
            cropX, cropY, cropSize, cropSize,
            0, 0, size, size
          );

          // Create white outline for dark background visibility
          if (outlineWidth > 0) {
            const imageData = tempCtx.getImageData(0, 0, size, size);
            const data = imageData.data;
            const outlineData = new ImageData(size, size);

            // Create outline by expanding non-transparent pixels
            for (let y = 0; y < size; y++) {
              for (let x = 0; x < size; x++) {
                const index = (y * size + x) * 4;
                const alpha = data[index + 3];

                if (alpha > 0) {
                  // This pixel has content, create outline around it
                  for (let dy = -outlineWidth; dy <= outlineWidth; dy++) {
                    for (let dx = -outlineWidth; dx <= outlineWidth; dx++) {
                      const nx = x + dx;
                      const ny = y + dy;
                      if (nx >= 0 && nx < size && ny >= 0 && ny < size) {
                        const outlineIndex = (ny * size + nx) * 4;
                        if (dx * dx + dy * dy <= outlineWidth * outlineWidth) {
                          outlineData.data[outlineIndex] = 255;     // White
                          outlineData.data[outlineIndex + 1] = 255; // White
                          outlineData.data[outlineIndex + 2] = 255; // White
                          outlineData.data[outlineIndex + 3] = 180; // Semi-transparent
                        }
                      }
                    }
                  }
                }
              }
            }

            // Draw outline first
            ctx.putImageData(outlineData, 0, 0);
          }

          // Draw original image on top
          ctx.drawImage(tempCanvas, 0, 0);

          // Enhance contrast for better visibility
          const finalImageData = ctx.getImageData(0, 0, size, size);
          const finalData = finalImageData.data;
          
          for (let i = 0; i < finalData.length; i += 4) {
            if (finalData[i + 3] > 0) { // Only process non-transparent pixels
              // Increase contrast and brightness
              finalData[i] = Math.min(255, finalData[i] * 1.3);     // Red
              finalData[i + 1] = Math.min(255, finalData[i + 1] * 1.3); // Green
              finalData[i + 2] = Math.min(255, finalData[i + 2] * 1.3); // Blue
            }
          }
          
          ctx.putImageData(finalImageData, 0, 0);

          // Convert to data URL
          const dataUrl = canvas.toDataURL('image/png');
          
          // Update state
          setProcessedImages(prev => ({
            ...prev,
            [`${size}x${size}-dark`]: dataUrl
          }));
          
          resolve(dataUrl);
        } catch (error) {
          reject(error);
        }
      };

      img.onerror = () => reject('Failed to load image');
      img.src = sourceImage;
    });
  };

  const processAllDarkModeVersions = async () => {
    if (!sourceImage) return;
    
    setIsProcessing(true);
    try {
      // Process sizes with white outline for dark background visibility
      await processImageForDarkMode(16, cropSettings['16'], 1);   // 16x16 with 1px outline
      await processImageForDarkMode(32, cropSettings['32'], 1);   // 32x32 with 1px outline
      await processImageForDarkMode(64, cropSettings['64'], 2);   // 64x64 with 2px outline
      await processImageForDarkMode(180, cropSettings['180'], 2); // 180x180 with 2px outline
      await processImageForDarkMode(192, cropSettings['192'], 3); // 192x192 with 3px outline
      await processImageForDarkMode(512, cropSettings['512'], 4); // 512x512 with 4px outline
    } catch (error) {
      console.error('Error processing dark mode images:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const processSingleSize = async (size: number) => {
    if (!sourceImage) return;
    
    const outlineWidth = size <= 32 ? 1 : size <= 64 ? 2 : size <= 180 ? 2 : size <= 192 ? 3 : 4;
    await processImageForDarkMode(size, cropSettings[size.toString() as keyof typeof cropSettings], outlineWidth);
  };

  const downloadImage = (dataUrl: string, filename: string) => {
    const link = document.createElement('a');
    link.download = filename;
    link.href = dataUrl;
    link.click();
  };

  const downloadAllDarkMode = () => {
    Object.entries(processedImages).forEach(([size, dataUrl]) => {
      const cleanSize = size.replace('-dark', '');
      if (cleanSize === '180x180') {
        downloadImage(dataUrl, 'apple-touch-icon-dark.png');
      } else if (cleanSize === '192x192') {
        downloadImage(dataUrl, 'android-chrome-192x192-dark.png');
      } else if (cleanSize === '512x512') {
        downloadImage(dataUrl, 'android-chrome-512x512-dark.png');
      } else {
        downloadImage(dataUrl, `favicon-${cleanSize}-dark.png`);
      }
    });
  };

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Dark Background Favicon Optimizer</h1>
        <p className="text-muted-foreground">
          Add white outlines to your cart-family favicons for better visibility on dark/blue backgrounds
        </p>
      </div>

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>1. Upload Your Cart-Family Favicon</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              ref={fileInputRef}
            />
            {sourceImage && (
              <div className="text-center">
                <img 
                  src={sourceImage} 
                  alt="Source favicon" 
                  className="max-w-32 max-h-32 mx-auto border rounded"
                />
                <p className="text-sm text-gray-600 mt-2">Source favicon loaded</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Cropping Controls Section */}
      {sourceImage && (
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
      )}

      {/* Processing Section */}
      <Card>
        <CardHeader>
          <CardTitle>{sourceImage ? '3' : '2'}. Generate Dark Background Optimized Versions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Button 
              onClick={processAllDarkModeVersions} 
              disabled={!sourceImage || isProcessing}
              className="w-full"
            >
              {isProcessing ? 'Processing...' : 'Generate Dark Background Versions'}
            </Button>
            
            <div className="text-xs text-gray-600 space-y-1">
              <p>• Adds white outline for visibility on dark backgrounds</p>
              <p>• Enhances contrast and brightness</p>
              <p>• Maintains original logo design</p>
              <p>• Creates "-dark" suffix versions</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Section */}
      {Object.keys(processedImages).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{sourceImage ? '4' : '3'}. Download Dark Background Optimized Favicons</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Button onClick={downloadAllDarkMode} className="w-full">
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
                          let filename;
                          if (displaySize === '180x180') {
                            filename = 'apple-touch-icon-dark.png';
                          } else if (displaySize === '192x192') {
                            filename = 'android-chrome-192x192-dark.png';
                          } else if (displaySize === '512x512') {
                            filename = 'android-chrome-512x512-dark.png';
                          } else {
                            filename = `favicon-${displaySize}-dark.png`;
                          }
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
      )}

      {/* Dark Background Testing */}
      {Object.keys(processedImages).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{sourceImage ? '5' : '4'}. Dark Background Visibility Test</CardTitle>
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
      )}

      {/* Hidden canvas for processing */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
}
