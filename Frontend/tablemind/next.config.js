/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone", // Para despliegues en Docker
  images: {
    domains: ['localhost'],
  },
  eslint: {
    ignoreDuringBuilds: true, // 👈 Esto evita errores de ESLint durante el build
  },
  async rewrites() {
    return [
      {
        source: '/api/auth/:path*',
        destination: 'http://api_auth:4002/public/auth/:path*',
      },
      {
        source: '/api/prompt/:path*',
        destination: 'http://api_auth:4003/public/prompt/:path*',
      },
      {
        source: '/api/media/:path*',
        destination: 'http://api_auth:4003/public/media/:path*',
      },
      {
        source: '/api/job/:path*',
        destination: 'http://api_auth:4003/public/job/:path*',
      },
      {
        source: '/api/model/:path*',
        destination: 'http://api_auth:4003/public/model/:path*',
      },
      {
        source: '/api/:path*',
        destination: 'http://api_auth:4003/public/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
