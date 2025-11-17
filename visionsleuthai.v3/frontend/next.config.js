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
  async rewrites() {
    return [
      {
        source: '/about',
        destination: '/pages/about',
      },
      {
        source: '/privacy',
        destination: '/pages/privacy',
      },
      {
        source: '/terms',
        destination: '/pages/terms',
      },
      {
        source: '/pricing',
        destination: '/pages/pricing',
      },
    ]
  },
}

module.exports = nextConfig 
