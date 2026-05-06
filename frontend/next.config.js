/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: { unoptimized: true },
  basePath: '/autovid',
  env: {
    NEXT_PUBLIC_BASE_URL: '/autovid/',
  },
}

module.exports = nextConfig
