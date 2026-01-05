import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";
import { GlobalLSPManager } from "@/components/GlobalLSPManager";
import { LSPStatusIndicator } from "@/components/LSPStatusIndicator";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Typedown — Markdown that Scales",
  description:
    "Build trusted knowledge bases with Markdown, Pydantic, and Pytest. Progressive formalization for documentation that scales.",
  icons: {
    icon: [
      { url: "/icon-dark.svg", media: "(prefers-color-scheme: light)" },
      { url: "/icon-light.svg", media: "(prefers-color-scheme: dark)" },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange>
          <GlobalLSPManager />
          {children}

          {/* Global Footer with LSP Status */}
          <footer className="fixed bottom-0 left-0 right-0 h-7 bg-gray-50 dark:bg-[#0A0A0A] border-t border-gray-200 dark:border-gray-800 flex items-center justify-end px-4 z-50">
            <LSPStatusIndicator />
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
