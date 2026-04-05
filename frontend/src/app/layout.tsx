import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Datachain",
  description: "Web3 CCTV Video Management System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50 text-gray-900 min-h-screen flex flex-col`}>
        {/* Standard Navigation Bar */}
        <nav className="bg-slate-900 text-white shadow-md">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex-shrink-0">
                <Link href="/" className="text-xl font-bold tracking-wider text-blue-400">
                  DATACHAIN
                </Link>
              </div>
              <div className="flex space-x-4">
                <Link 
                  href="/dashboard" 
                  className="px-3 py-2 rounded-md text-sm font-medium hover:bg-slate-700 transition"
                >
                  Dashboard
                </Link>
                <button className="px-3 py-2 rounded-md text-sm font-medium bg-red-600 hover:bg-red-700 transition">
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content Area */}
        <main className="flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        {/* Standard Footer */}
        <footer className="bg-slate-900 text-slate-400 py-6 text-center text-sm">
          <p>© {new Date().getFullYear()} Datachain. Cryptographically Secured Video Integrity.</p>
        </footer>
      </body>
    </html>
  );
}