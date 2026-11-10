import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import { AuthProvider } from "@/lib/auth";
import "./globals.css";

const display = localFont({
  variable: "--font-display",
  src: [
    { path: "./fonts/archivo-latin-500-normal.woff2", weight: "500", style: "normal" },
    { path: "./fonts/archivo-latin-600-normal.woff2", weight: "600", style: "normal" },
    { path: "./fonts/archivo-latin-700-normal.woff2", weight: "700", style: "normal" },
    { path: "./fonts/archivo-latin-800-normal.woff2", weight: "800", style: "normal" },
  ],
});

const sans = localFont({
  variable: "--font-sans",
  src: "./fonts/outfit-latin-400-normal.woff2",
});

const mono = localFont({
  variable: "--font-mono",
  src: [
    { path: "./fonts/ibm-plex-mono-latin-400-normal.woff2", weight: "400", style: "normal" },
    { path: "./fonts/ibm-plex-mono-latin-500-normal.woff2", weight: "500", style: "normal" },
  ],
});

export const metadata: Metadata = {
  title: "АвтоЦентр",
  description: "АвтоЦентр для независимых автосервисов",
  applicationName: "АвтоЦентр",
  icons: {
    icon: [
      { url: "/brand/ratchethub-icon.svg", type: "image/svg+xml" },
      { url: "/brand/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/brand/favicon-16.png", sizes: "16x16", type: "image/png" },
      { url: "/brand/ratchethub-icon.png", type: "image/png" },
    ],
    apple: [{ url: "/brand/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru-RU">
      <body className={`${display.variable} ${sans.variable} ${mono.variable} antialiased`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}