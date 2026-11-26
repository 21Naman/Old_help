import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Served as a Render Static Site: every page is a client page, exported to out/.
  output: "export",
  // /home → out/home/index.html, so direct loads and refreshes work on any static host.
  trailingSlash: true,
  images: { unoptimized: true },
  reactStrictMode: true,
  transpilePackages: ["three"],
  experimental: {
    optimizePackageImports: ["framer-motion"],
  },
};

export default nextConfig;
