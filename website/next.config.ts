import type { NextConfig } from 'next'
import path from 'path'
import packageJson from './package.json'

const nextConfig: NextConfig = {
  output: 'export',
  env: {
    NEXT_PUBLIC_APP_VERSION: packageJson.version,
  },
  // trailingSlash: true, // Disable trailingSlash to ensure index.html is generated for root
  images: {
    unoptimized: true,
  },
  serverExternalPackages: ['vscode-oniguruma'],
  // Turbopack root configuration
  turbopack: {
    root: path.resolve(__dirname, '..'),
  },
}

export default nextConfig
