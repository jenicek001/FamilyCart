"use client";

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function FaviconProcessorPage() {
  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [processedImages, setProcessedImages] = useState<{[key: string]: string}>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const processImage = (size: number, cropPercentage: number, sharpen: boolean = false): Promise<string> => {
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

          // Draw cropped and resized image
          ctx.drawImage(
            img,
            cropX, cropY, cropSize, cropSize, // Source crop
            0, 0, size, size // Destination
          );

          // Apply sharpening for very small sizes
          if (sharpen && size <= 32) {
            const imageData = ctx.getImageData(0, 0, size, size);
            const data = imageData.data;
            
            // Simple contrast enhancement
            for (let i = 0; i < data.length; i += 4) {
              // Increase contrast
              data[i] = Math.min(255, data[i] * 1.2);     // Red
              data[i + 1] = Math.min(255, data[i + 1] * 1.2); // Green
              data[i + 2] = Math.min(255, data[i + 2] * 1.2); // Blue
            }
            
            ctx.putImageData(imageData, 0, 0);
          }

          // Convert to data URL
          const dataUrl = canvas.toDataURL('image/png');
          
          // Update state
          setProcessedImages(prev => ({
            ...prev,
            [`${size}x${size}`]: dataUrl
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

  const processAllSizes = async () => {
    if (!sourceImage) return;
    
    setIsProcessing(true);
    try {
      // Process sizes sequentially to avoid canvas conflicts
      await processImage(16, 80, true);  // 16x16 - Aggressive crop, with sharpening - GOOD!
      await processImage(32, 30, true);  // 32x32 - Light crop, with sharpening  
      await processImage(64, 15, false); // 64x64 - Minimal crop
      await processImage(180, 10, false); // 180x180 - Very minimal crop for Apple touch icon
      await processImage(192, 8, false); // 192x192 - Android Chrome standard
      await processImage(512, 5, false); // 512x512 - Android Chrome high-res
    } catch (error) {
      console.error('Error processing images:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadImage = (dataUrl: string, filename: string) => {
    const link = document.createElement('a');
    link.download = filename;
    link.href = dataUrl;
    link.click();
  };

  const downloadAll = () => {
    Object.entries(processedImages).forEach(([size, dataUrl]) => {
      if (size === '180x180') {
        downloadImage(dataUrl, 'apple-touch-icon.png');
      } else if (size === '192x192') {
        downloadImage(dataUrl, 'android-chrome-192x192.png');
      } else if (size === '512x512') {
        downloadImage(dataUrl, 'android-chrome-512x512.png');
      } else {
        downloadImage(dataUrl, `favicon-${size}.png`);
      }
    });
  };

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Favicon Image Processor</h1>
        <p className="text-muted-foreground">
          Convert your 1024x1024 cart-family logo to optimized favicon sizes
        </p>
      </div>

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>1. Upload Your 1024x1024 Cart-Family Logo</CardTitle>
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
                  alt="Source logo" 
                  className="max-w-64 max-h-64 mx-auto border rounded"
                />
                <p className="text-sm text-gray-600 mt-2">Source image loaded</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Processing Section */}
      <Card>
        <CardHeader>
          <CardTitle>2. Process Favicon Sizes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Button 
                onClick={processAllSizes} 
                disabled={!sourceImage || isProcessing}
                className="flex-1"
              >
                {isProcessing ? 'Processing...' : 'Generate All Favicon Sizes'}
              </Button>
              
              <Button 
                variant="outline"
                onClick={() => setProcessedImages({})}
                disabled={Object.keys(processedImages).length === 0}
              >
                Clear All
              </Button>
            </div>
            
            <div className="text-xs text-gray-600 space-y-1">
              <p>• 16x16: 80% crop + contrast enhancement (browser tabs) ✅ Good</p>
              <p>• 32x32: 30% crop + sharpening (app icons) - Less aggressive</p>
              <p>• 64x64: 15% crop (desktop icons) - Preserve details</p>
              <p>• 180x180: 10% crop (Apple touch icon) - Minimal adjustment</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Advanced Controls */}
      <Card>
        <CardHeader>
          <CardTitle>2a. Fine-Tune Cropping (Optional)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="space-y-2">
              <Label>16x16 Crop %</Label>
              <Input 
                type="number" 
                defaultValue={80} 
                min={0} 
                max={90} 
                id="crop-16"
                className="text-center"
              />
              <Button 
                size="sm" 
                variant="outline" 
                onClick={async () => {
                  const cropValue = parseInt((document.getElementById('crop-16') as HTMLInputElement).value);
                  try {
                    await processImage(16, cropValue, true);
                  } catch (error) {
                    console.error('Error processing 16x16:', error);
                  }
                }}
                disabled={!sourceImage}
              >
                Test 16x16
              </Button>
            </div>
            
            <div className="space-y-2">
              <Label>32x32 Crop %</Label>
              <Input 
                type="number" 
                defaultValue={30} 
                min={0} 
                max={70} 
                id="crop-32"
                className="text-center"
              />
              <Button 
                size="sm" 
                variant="outline" 
                onClick={async () => {
                  const cropValue = parseInt((document.getElementById('crop-32') as HTMLInputElement).value);
                  try {
                    await processImage(32, cropValue, true);
                  } catch (error) {
                    console.error('Error processing 32x32:', error);
                  }
                }}
                disabled={!sourceImage}
              >
                Test 32x32
              </Button>
            </div>
            
            <div className="space-y-2">
              <Label>64x64 Crop %</Label>
              <Input 
                type="number" 
                defaultValue={15} 
                min={0} 
                max={50} 
                id="crop-64"
                className="text-center"
              />
              <Button 
                size="sm" 
                variant="outline" 
                onClick={async () => {
                  const cropValue = parseInt((document.getElementById('crop-64') as HTMLInputElement).value);
                  try {
                    await processImage(64, cropValue, false);
                  } catch (error) {
                    console.error('Error processing 64x64:', error);
                  }
                }}
                disabled={!sourceImage}
              >
                Test 64x64
              </Button>
            </div>
            
            <div className="space-y-2">
              <Label>180x180 Crop %</Label>
              <Input 
                type="number" 
                defaultValue={10} 
                min={0} 
                max={30} 
                id="crop-180"
                className="text-center"
              />
              <Button 
                size="sm" 
                variant="outline" 
                onClick={async () => {
                  const cropValue = parseInt((document.getElementById('crop-180') as HTMLInputElement).value);
                  try {
                    await processImage(180, cropValue, false);
                  } catch (error) {
                    console.error('Error processing 180x180:', error);
                  }
                }}
                disabled={!sourceImage}
              >
                Test 180x180
              </Button>
            </div>
            
            <div className="space-y-2">
              <Label>192x192 Crop % (Android)</Label>
              <Input 
                type="number" 
                defaultValue={8} 
                min={0} 
                max={20} 
                id="crop-192"
                className="text-center"
              />
              <Button 
                size="sm" 
                variant="outline" 
                onClick={async () => {
                  const cropValue = parseInt((document.getElementById('crop-192') as HTMLInputElement).value);
                  try {
                    await processImage(192, cropValue, false);
                  } catch (error) {
                    console.error('Error processing 192x192:', error);
                  }
                }}
                disabled={!sourceImage}
              >
                Test 192x192
              </Button>
            </div>
            
            <div className="space-y-2">
              <Label>512x512 Crop % (Android)</Label>
              <Input 
                type="number" 
                defaultValue={5} 
                min={0} 
                max={15} 
                id="crop-512"
                className="text-center"
              />
              <Button 
                size="sm" 
                variant="outline" 
                onClick={async () => {
                  const cropValue = parseInt((document.getElementById('crop-512') as HTMLInputElement).value);
                  try {
                    await processImage(512, cropValue, false);
                  } catch (error) {
                    console.error('Error processing 512x512:', error);
                  }
                }}
                disabled={!sourceImage}
              >
                Test 512x512
              </Button>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-blue-50 rounded text-sm text-blue-800">
            <strong>Tip:</strong> Lower crop % = less padding removed, higher crop % = more padding removed. 
            Adjust until the logo looks good without being cut off.
          </div>
        </CardContent>
      </Card>

      {/* Results Section */}
      {Object.keys(processedImages).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>3. Download Optimized Favicons</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Button onClick={downloadAll} className="w-full">
                Download All Favicons
              </Button>
              
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {Object.entries(processedImages).map(([size, dataUrl]) => {
                  const isAndroid = size === '192x192' || size === '512x512';
                  const isApple = size === '180x180';
                  
                  return (
                    <div key={size} className="text-center space-y-2">
                      <div className="border rounded p-4 bg-gray-50">
                        <img 
                          src={dataUrl} 
                          alt={`${size} favicon`}
                          className="mx-auto"
                          style={{ 
                            width: size === '512x512' ? '48px' : 
                                   size === '192x192' ? '40px' : 
                                   size === '180x180' ? '32px' : 
                                   size === '64x64' ? '28px' :
                                   size === '32x32' ? '24px' : '16px',
                            height: size === '512x512' ? '48px' : 
                                    size === '192x192' ? '40px' : 
                                    size === '180x180' ? '32px' : 
                                    size === '64x64' ? '28px' :
                                    size === '32x32' ? '24px' : '16px',
                            imageRendering: parseInt(size.split('x')[0]) <= 32 ? 'pixelated' : 'auto'
                          }}
                        />
                      </div>
                      <div className="text-sm font-medium">
                        {size}
                        {isAndroid && <span className="block text-xs text-blue-600">Android</span>}
                        {isApple && <span className="block text-xs text-gray-600">Apple</span>}
                      </div>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          let filename;
                          if (size === '180x180') {
                            filename = 'apple-touch-icon.png';
                          } else if (size === '192x192') {
                            filename = 'android-chrome-192x192.png';
                          } else if (size === '512x512') {
                            filename = 'android-chrome-512x512.png';
                          } else {
                            filename = `favicon-${size}.png`;
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

      {/* Testing Preview */}
      {Object.keys(processedImages).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>4. Visibility Test</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                {/* Light Background Test */}
                <div className="border rounded p-4 bg-white">
                  <h4 className="font-medium mb-2">Light Background</h4>
                  <div className="flex items-center gap-2 p-2 bg-gray-100 rounded">
                    {processedImages['16x16'] && (
                      <img src={processedImages['16x16']} alt="16x16 test" className="w-4 h-4" />
                    )}
                    <span className="text-sm">FamilyCart</span>
                  </div>
                </div>

                {/* Dark Background Test */}
                <div className="border rounded p-4 bg-gray-900 text-white">
                  <h4 className="font-medium mb-2">Dark Background</h4>
                  <div className="flex items-center gap-2 p-2 bg-gray-800 rounded">
                    {processedImages['16x16'] && (
                      <img src={processedImages['16x16']} alt="16x16 test" className="w-4 h-4" />
                    )}
                    <span className="text-sm">FamilyCart</span>
                  </div>
                </div>

                {/* App Icon Test */}
                <div className="border rounded p-4 bg-blue-50">
                  <h4 className="font-medium mb-2">App Icon (32x32)</h4>
                  <div className="flex items-center gap-2 p-2 bg-blue-100 rounded">
                    {processedImages['32x32'] && (
                      <img src={processedImages['32x32']} alt="32x32 test" className="w-8 h-8" />
                    )}
                    <span className="text-sm">FamilyCart</span>
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
