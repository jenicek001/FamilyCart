// Image processing utilities for favicon generation
// Extracted from favicon-processor page to comply with file size limits

export interface ProcessImageOptions {
  size: number;
  cropPercentage: number;
  sharpen?: boolean;
}

export interface FaviconSizes {
  [key: string]: number;
}

export const FAVICON_SIZES: FaviconSizes = {
  '16x16': 16,
  '32x32': 32,
  '48x48': 48,
  '64x64': 64,
  '128x128': 128,
  '256x256': 256
};

/**
 * Process an image for favicon generation
 * @param sourceImage Base64 encoded source image
 * @param canvas Canvas element for processing
 * @param options Processing options
 * @returns Promise resolving to processed image as base64 string
 */
export function processImage(
  sourceImage: string, 
  canvas: HTMLCanvasElement, 
  options: ProcessImageOptions
): Promise<string> {
  const { size, cropPercentage, sharpen = false } = options;
  
  return new Promise((resolve, reject) => {
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      reject('Canvas context not available');
      return;
    }

    const img = new Image();
    img.onload = () => {
      // Calculate crop dimensions
      const cropAmount = Math.min(img.width, img.height) * (cropPercentage / 100);
      const cropSize = Math.min(img.width, img.height) - (cropAmount * 2);
      const cropX = (img.width - cropSize) / 2;
      const cropY = (img.height - cropSize) / 2;

      // Set canvas size
      canvas.width = size;
      canvas.height = size;

      // Apply high-quality scaling
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';

      // Draw and scale the image
      ctx.drawImage(img, cropX, cropY, cropSize, cropSize, 0, 0, size, size);

      // Apply sharpening filter if requested
      if (sharpen) {
        applySharpenFilter(ctx, size);
      }

      // Return processed image
      resolve(canvas.toDataURL('image/png'));
    };

    img.onerror = () => reject('Failed to load image');
    img.src = sourceImage;
  });
}

/**
 * Apply a sharpening filter to the canvas
 */
function applySharpenFilter(ctx: CanvasRenderingContext2D, size: number): void {
  const imageData = ctx.getImageData(0, 0, size, size);
  const data = imageData.data;
  const sharpenKernel = [
    0, -1, 0,
    -1, 5, -1,
    0, -1, 0
  ];

  const newData = new Uint8ClampedArray(data);

  for (let y = 1; y < size - 1; y++) {
    for (let x = 1; x < size - 1; x++) {
      for (let c = 0; c < 3; c++) { // RGB channels only
        let value = 0;
        for (let ky = -1; ky <= 1; ky++) {
          for (let kx = -1; kx <= 1; kx++) {
            const kernelIndex = (ky + 1) * 3 + (kx + 1);
            const pixelIndex = ((y + ky) * size + (x + kx)) * 4 + c;
            value += data[pixelIndex] * sharpenKernel[kernelIndex];
          }
        }
        const currentIndex = (y * size + x) * 4 + c;
        newData[currentIndex] = Math.max(0, Math.min(255, value));
      }
    }
  }

  const newImageData = new ImageData(newData, size, size);
  ctx.putImageData(newImageData, 0, 0);
}

/**
 * Process all favicon sizes from a source image
 */
export async function processAllFaviconSizes(
  sourceImage: string, 
  canvas: HTMLCanvasElement, 
  cropPercentage: number = 0,
  sharpen: boolean = false
): Promise<{[key: string]: string}> {
  const results: {[key: string]: string} = {};
  
  for (const [key, size] of Object.entries(FAVICON_SIZES)) {
    try {
      results[key] = await processImage(sourceImage, canvas, { 
        size, 
        cropPercentage, 
        sharpen 
      });
    } catch (error) {
      console.error(`Failed to process ${key}:`, error);
      throw new Error(`Failed to process favicon size ${key}`);
    }
  }
  
  return results;
}

/**
 * Download a processed image
 */
export function downloadImage(dataUrl: string, filename: string): void {
  const link = document.createElement('a');
  link.download = filename;
  link.href = dataUrl;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Download all processed favicons as a zip-like collection
 */
export function downloadAllFavicons(processedImages: {[key: string]: string}): void {
  Object.entries(processedImages).forEach(([size, dataUrl]) => {
    downloadImage(dataUrl, `favicon-${size}.png`);
  });
}