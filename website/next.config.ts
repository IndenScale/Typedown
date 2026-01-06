import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: "export",
  // trailingSlash: true, // Disable trailingSlash to ensure index.html is generated for root
  images: {
    unoptimized: true,
  },
  serverExternalPackages: ["vscode-oniguruma"],
  // Turbopack root configuration
  turbopack: {
    root: path.resolve(__dirname, ".."),
  },
};

export default nextConfig;
