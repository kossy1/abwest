/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production'
          ? 'https://your-backend.vercel.app/api/:path*'
          : 'http://localhost:8000/api/:path*',
      },
    ];
  },
  images: {
    domains: ['your-mongodb-storage.com'],
  },
  env: {
    MONGODB_URI: process.env.MONGODB_URI,
  },
  experimental: {
    serverActions: true,
  },
};

module.exports = nextConfig;