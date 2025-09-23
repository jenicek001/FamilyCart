"use client";

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  CropSettings, 
  ProcessedImages, 
  DEFAULT_CROP_SETTINGS,
  processAllDarkModeVersions,
  downloadAllDarkMode
} from '@/lib/favicon-dark-mode-processing';
import { CroppingSection } from '@/components/favicon-dark-mode/cropping-section';
import { DownloadSection, DarkModeTestSection } from '@/components/favicon-dark-mode/result-sections';

export default function FaviconDarkModeProcessor() {
  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [processedImages, setProcessedImages] = useState<ProcessedImages>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [cropSettings, setCropSettings] = useState<CropSettings>(DEFAULT_CROP_SETTINGS);

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

  const processAllDarkModeVersionsHandler = async () => {
    if (!sourceImage || !canvasRef.current) return;
    
    setIsProcessing(true);
    try {
      await processAllDarkModeVersions(
        sourceImage,
        canvasRef.current,
        cropSettings,
        (size, dataUrl) => {
          setProcessedImages(prev => ({
            ...prev,
            [size]: dataUrl
          }));
        }
      );
    } catch (error) {
      console.error('Error processing dark mode images:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownloadAll = () => {
    downloadAllDarkMode(processedImages);
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
        <CroppingSection
          sourceImage={sourceImage}
          cropSettings={cropSettings}
          setCropSettings={setCropSettings}
          processedImages={processedImages}
          setProcessedImages={setProcessedImages}
          canvasRef={canvasRef}
        />
      )}

      {/* Processing Section */}
      <Card>
        <CardHeader>
          <CardTitle>{sourceImage ? '3' : '2'}. Generate Dark Background Optimized Versions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Button 
              onClick={processAllDarkModeVersionsHandler} 
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
        <DownloadSection
          processedImages={processedImages}
          sourceImage={sourceImage}
          onDownloadAll={handleDownloadAll}
        />
      )}

      {/* Dark Background Testing */}
      {Object.keys(processedImages).length > 0 && (
        <DarkModeTestSection
          processedImages={processedImages}
          sourceImage={sourceImage}
        />
      )}

      {/* Hidden canvas for processing */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
}
