import type { NextConfig } from "next";

// API Configuration - centralized port management
const API_CONFIG = {
  DEFAULT_PORT: 8005,
} as const;

const nextConfig: NextConfig = {
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
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
    turbo: {
      rules: {
        // Enable Turbopack for faster builds during development
        "*.svg": {
          loaders: ["@svgr/webpack"],
          as: "*.js",
        },
      },
    },
  },
  async rewrites() {
    let apiUrl: string;
    
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

export default nextConfig;
