import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow the FastAPI backend origin for API calls from server components
  // TODO: replace with actual backend domain before deploying
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
