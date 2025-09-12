import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Aurexus Public AI - Real Estate Intelligence",
  description: "AI-powered insights for real estate macro trends, suburb analytics, and investment strategies",
  authors: [{ name: "Aurexus" }],
  keywords: ["real estate", "AI", "analytics", "investment", "macro trends", "suburb analysis"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body
        className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      >
        {children}
      </body>
    </html>
  );
}