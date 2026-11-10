import type { NextConfig } from "next";
import path from "path";

const apiUpstream = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);

const nextConfig: NextConfig = {
  output: "standalone",
  outputFileTracingRoot: path.join(process.cwd(), "."),
  outputFileTracingIncludes: {
    '/*': [
      '../../node_modules/next/**/*',
      '../../node_modules/react/**/*',
      '../../node_modules/react-dom/**/*',
    ],
  },

  poweredByHeader: false,
  async redirects() {
    return [
      {
        source: "/login",
        destination: "/?login=1",
        permanent: false,
      },
    ];
  },
  async rewrites() {
    return [
      {
        source: "/api-backend/:path*",
        destination: `${apiUpstream}/:path*`,
      },
    ];
  },
};

export default nextConfig;