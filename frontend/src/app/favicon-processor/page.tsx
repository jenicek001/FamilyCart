"use client";

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  processAllFaviconSizes, 
  downloadAllFavicons, 
  downloadImage,
  FAVICON_SIZES 
} from '@/lib/image-processing';

export default function FaviconProcessorPage() {
  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [processedImages, setProcessedImages] = useState<{[key: string]: string}>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [cropPercentage, setCropPercentage] = useState(0);
  const [sharpenEnabled, setSharpenEnabled] = useState(false);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSourceImage(e.target?.result as string);
        setProcessedImages({}); // Clear previous results
      };
      reader.readAsDataURL(file);
    }
  };

  const handleProcessAllSizes = async () => {
    if (!sourceImage || !canvasRef.current) return;

    setIsProcessing(true);
    try {
      const results = await processAllFaviconSizes(
        sourceImage, 
        canvasRef.current, 
        cropPercentage, 
        sharpenEnabled
      );
      setProcessedImages(results);
    } catch (error) {
      console.error('Processing failed:', error);
      alert('Failed to process images. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownloadAll = () => {
    downloadAllFavicons(processedImages);
  };

  const handleDownloadSingle = (size: string, dataUrl: string) => {
    downloadImage(dataUrl, `favicon-${size}.png`);
  };

  const reset = () => {
    setSourceImage(null);
    setProcessedImages({});
    setCropPercentage(0);
    setSharpenEnabled(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Favicon Processor</h1>
        <p className="text-gray-600">
          Upload an image and generate favicons in multiple sizes with optional cropping and sharpening
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload Image</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="image-upload">Select Image</Label>
            <Input
              id="image-upload"
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              ref={fileInputRef}
            />
          </div>

          {sourceImage && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <img 
                  src={sourceImage} 
                  alt="Source" 
                  className="max-w-64 max-h-64 object-contain border rounded"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="crop-slider">
                    Crop Percentage: {cropPercentage}%
                  </Label>
                  <Input
                    id="crop-slider"
                    type="range"
                    min="0"
                    max="40"
                    value={cropPercentage}
                    onChange={(e) => setCropPercentage(parseInt(e.target.value))}
                    className="mt-1"
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    id="sharpen-checkbox"
                    type="checkbox"
                    checked={sharpenEnabled}
                    onChange={(e) => setSharpenEnabled(e.target.checked)}
                  />
                  <Label htmlFor="sharpen-checkbox">Enable Sharpening</Label>
                </div>
              </div>

              <div className="flex justify-center space-x-4">
                <Button 
                  onClick={handleProcessAllSizes}
                  disabled={isProcessing}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isProcessing ? 'Processing...' : 'Process All Sizes'}
                </Button>
                
                <Button 
                  onClick={reset}
                  variant="outline"
                >
                  Reset
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {Object.keys(processedImages).length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Processed Favicons</CardTitle>
            <Button 
              onClick={handleDownloadAll}
              className="bg-green-600 hover:bg-green-700"
            >
              Download All
            </Button>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(processedImages).map(([size, dataUrl]) => (
                <div key={size} className="text-center space-y-2">
                  <div className="border rounded p-2 bg-gray-50">
                    <img 
                      src={dataUrl} 
                      alt={`${size} favicon`} 
                      className="mx-auto"
                      style={{ 
                        width: `${Math.min(FAVICON_SIZES[size], 64)}px`,
                        height: `${Math.min(FAVICON_SIZES[size], 64)}px`,
                        imageRendering: 'pixelated'
                      }}
                    />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{size}</p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDownloadSingle(size, dataUrl)}
                      className="mt-1"
                    >
                      Download
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Hidden canvas for processing */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
}