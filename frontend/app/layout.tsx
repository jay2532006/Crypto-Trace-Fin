import type { Metadata } from "next";
import { Providers } from "./providers";
import "./globals.css";
import "./kestrel.css";

export const metadata: Metadata = {
  title: "CryptoTrace LEA — Law Enforcement Investigation Platform",
  description:
    "Evidence-first, live-data-driven cryptocurrency fraud attribution system for Indian Law Enforcement Agencies (MHA / I4C). SIH 26183.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Noto+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=Work+Sans:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-slate-50 dark:bg-[#070F1E] text-slate-900 dark:text-slate-100 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
