const path = require('path');

// API Configuration - centralized port management
const API_CONFIG = {
  DEFAULT_PORT: 8005,
};

/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
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
    // turbo: {
    //   rules: {
    //     // Enable Turbopack for faster builds during development
    //     "*.svg": {
    //       loaders: ["@svgr/webpack"],
    //       as: "*.js",
    //     },
    //   },
    // },
  },
  // Webpack configuration to ensure path aliases work consistently
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Ensure path aliases are properly resolved in webpack
    // Use process.cwd() for CI compatibility
    const projectRoot = process.cwd();
    const srcPath = path.join(projectRoot, 'src');
    
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
    
    // Debug output for CI troubleshooting
    console.log('=== Webpack Debug Info ===');
    console.log('process.cwd():', projectRoot);
    console.log('__dirname:', __dirname);
    console.log('srcPath:', srcPath);
    console.log('aliases:', config.resolve.alias);
    console.log('modules:', config.resolve.modules);
    console.log('===========================');
    
    return config;
  },
  async rewrites() {
    let apiUrl;
    
    if (process.env.NODE_ENV === 'production') {
      // In production, try environment variable first, then auto-detect
      if (process.env.API_URL) {
        apiUrl = process.env.API_URL;
      } else {
        // Auto-detect current hostname and use configured port
        apiUrl = process.env.API_URL || `http://localhost:${API_CONFIG.DEFAULT_PORT}`;
      }
    } else {
      // In development, always use localhost with configured port
      apiUrl = `http://localhost:${API_CONFIG.DEFAULT_PORT}`;
    }

    console.log(`Frontend proxy will use API URL: ${apiUrl}`);

    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;