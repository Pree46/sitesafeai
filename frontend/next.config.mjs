/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
  images: {
    domains: ['localhost'],
  },
  // Disable strict mode if you have WebSocket issues
  reactStrictMode: false,
};

export default nextConfig;
