/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
  compiler: {
    styledComponents: true,
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.join(__dirname, 'src'),
    };
    return config;
  },
  // Removed rewrites - App Router handles routes automatically
  // /about -> /app/about/page.tsx
  // /privacy -> /app/pages/privacy/page.tsx
  // /terms -> /app/pages/terms/page.tsx
}

module.exports = nextConfig 
