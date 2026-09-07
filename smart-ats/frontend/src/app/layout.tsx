import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Smart ATS | Premium",
  description: "Next-Gen Applicant Tracking System powered by AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl">
      <body className={`${inter.className} bg-slate-900 text-slate-100 antialiased selection:bg-teal-500/30`}>
        
        <div className="fixed inset-0 z-[-1] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-800 via-slate-900 to-black">
        </div>

        <main className="relative flex min-h-screen flex-col items-center justify-center p-6">
          <div className="z-10 w-full max-w-7xl">
            {children}
          </div>
        </main>

      </body>
    </html>
  );
}