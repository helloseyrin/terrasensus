import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow embedding Grafana and Looker Studio iframes on the analytics page
  async headers() {
    return [
      {
        source: "/analytics",
        headers: [
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
        ],
      },
    ];
  },
};

export default nextConfig;
