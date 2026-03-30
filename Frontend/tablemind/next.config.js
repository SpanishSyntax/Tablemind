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
        destination: 'http://api_auth:4002/auth/:path*',
      },
      {
        source: '/api/prompt/:path*',
        destination: 'http://api_auth:4003/prompt/:path*',
      },
      {
        source: '/api/media/:path*',
        destination: 'http://api_auth:4003/media/:path*',
      },
      {
        source: '/api/job/:path*',
        destination: 'http://api_auth:4003/job/:path*',
      },
      {
        source: '/api/model/:path*',
        destination: 'http://api_auth:4003/model/:path*',
      },
      {
        source: '/api/:path*',
        destination: 'http://api_auth:4003/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
