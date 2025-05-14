import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ThemeProvider } from "@/components/ui/theme-provider";
import { AuthWrapper } from "./auth-wrapper";
import "./globals.css";
import { cn } from "@/lib/utils";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Verdict360 - Legal Intelligence Platform",
  description: "AI-powered legal intelligence for South African professionals",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={cn(inter.className, "min-h-screen bg-background antialiased")}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AuthWrapper>{children}</AuthWrapper>
        </ThemeProvider>
      </body>
    </html>
  );
}
