/**
 * Favicon dark mode image processing utilities
 * 
 * This module provides functions for processing favicons to make them
 * more visible on dark backgrounds by adding white outlines and enhancing contrast.
 */

// Types
export interface CropSettings {
  '16': number;
  '32': number;
  '64': number;
  '180': number;
  '192': number;
  '512': number;
}

export interface ProcessedImages {
  [key: string]: string;
}

// Default crop settings optimized for favicon visibility
export const DEFAULT_CROP_SETTINGS: CropSettings = {
  '16': 80,
  '32': 30,
  '64': 15,
  '180': 10,
  '192': 8,
  '512': 5
};

/**
 * Process an image for dark mode visibility by adding white outline and enhancing contrast
 */
export const processImageForDarkMode = (
  sourceImage: string,
  canvas: HTMLCanvasElement,
  size: number,
  cropPercentage: number,
  outlineWidth: number = 2
): Promise<string> => {
  return new Promise((resolve, reject) => {
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
        resolve(dataUrl);
      } catch (error) {
        reject(error);
      }
    };

    img.onerror = () => reject('Failed to load image');
    img.src = sourceImage;
  });
};

/**
 * Get appropriate outline width for different favicon sizes
 */
export const getOutlineWidthForSize = (size: number): number => {
  if (size <= 32) return 1;
  if (size <= 64) return 2;
  if (size <= 180) return 2;
  if (size <= 192) return 3;
  return 4;
};

/**
 * Process all standard favicon sizes for dark mode
 */
export const processAllDarkModeVersions = async (
  sourceImage: string,
  canvas: HTMLCanvasElement,
  cropSettings: CropSettings,
  onUpdate: (size: string, dataUrl: string) => void
): Promise<void> => {
  const sizes = [16, 32, 64, 180, 192, 512];
  
  for (const size of sizes) {
    const outlineWidth = getOutlineWidthForSize(size);
    const dataUrl = await processImageForDarkMode(
      sourceImage,
      canvas,
      size,
      cropSettings[size.toString() as keyof CropSettings],
      outlineWidth
    );
    onUpdate(`${size}x${size}-dark`, dataUrl);
  }
};

/**
 * Download utility functions
 */
export const downloadImage = (dataUrl: string, filename: string): void => {
  const link = document.createElement('a');
  link.download = filename;
  link.href = dataUrl;
  link.click();
};

/**
 * Get appropriate filename for each favicon size
 */
export const getFilenameForSize = (size: string): string => {
  const cleanSize = size.replace('-dark', '');
  if (cleanSize === '180x180') {
    return 'apple-touch-icon-dark.png';
  } else if (cleanSize === '192x192') {
    return 'android-chrome-192x192-dark.png';
  } else if (cleanSize === '512x512') {
    return 'android-chrome-512x512-dark.png';
  } else {
    return `favicon-${cleanSize}-dark.png`;
  }
};

/**
 * Download all processed dark mode favicon versions
 */
export const downloadAllDarkMode = (processedImages: ProcessedImages): void => {
  Object.entries(processedImages).forEach(([size, dataUrl]) => {
    const filename = getFilenameForSize(size);
    downloadImage(dataUrl, filename);
  });
};