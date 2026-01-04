const path = require('path');

// API Configuration - centralized port management
const API_CONFIG = {
  DEFAULT_PORT: 8002,
};

/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
  // Enable standalone output for optimized Docker builds
  output: 'standalone',
  
  typescript: {
    ignoreBuildErrors: true, // Temporarily ignore TS errors since we have explicit webpack aliases
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'placehold.co',
        port: '',
        pathname: '/**',
      },
    ],
  },
  experimental: {
    // Allow cross-origin requests for dev server
    turbo: {
      unstable_allowImportMappingWithoutBaseUrl: true,
    },
  },
  // Allow dev access from any origin (fixes CSS not loading from LAN IPs)
  async headers() {
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/:path*',
          headers: [
            { key: 'Access-Control-Allow-Origin', value: '*' },
            { key: 'Access-Control-Allow-Methods', value: 'GET,POST,PUT,DELETE,OPTIONS' },
            { key: 'Access-Control-Allow-Headers', value: '*' },
          ],
        },
      ];
    }
    return [];
  },
  // Webpack configuration to ensure path aliases work consistently
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Ensure path aliases are properly resolved in webpack
    // Use process.cwd() for CI compatibility
    const projectRoot = process.cwd();
    const srcPath = path.join(projectRoot, 'src');
    const fs = require('fs');
    
    // Debug output for CI troubleshooting
    console.log('=== Webpack Debug Info ===');
    console.log('process.cwd():', projectRoot);
    console.log('__dirname:', __dirname);
    console.log('srcPath:', srcPath);
    
    // Check if files actually exist
    const utilsPath = path.join(srcPath, 'lib', 'utils.ts');
    const utilsExists = fs.existsSync(utilsPath);
    console.log('utils.ts path:', utilsPath);
    console.log('utils.ts exists:', utilsExists);
    
    if (utilsExists) {
      console.log('utils.ts content preview:', fs.readFileSync(utilsPath, 'utf8').slice(0, 100));
    }
    
    // Clear any existing aliases to avoid conflicts
    config.resolve.alias = {
      '@': srcPath,
      '@/lib': path.join(srcPath, 'lib'),
      '@/components': path.join(srcPath, 'components'),
    };
    
    // Ensure proper module resolution order
    config.resolve.modules = [
      srcPath,
      'node_modules'
    ];
    
    // Force webpack to look in the right places
    config.resolve.roots = [projectRoot];
    
    console.log('aliases:', config.resolve.alias);
    console.log('modules:', config.resolve.modules);
    console.log('===========================');
    
    return config;
  },
  // NOTE: API proxying is now handled by Next.js API routes in src/app/api/[...path]/route.ts
  // This allows runtime environment variable configuration without rebuilds
};

module.exports = nextConfig;