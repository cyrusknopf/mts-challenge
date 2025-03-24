import type { Metadata } from "next";
import "./globals.css";
import ClientBody from "./ClientBody";

export const metadata: Metadata = {
  title: "PRISM Leaderboard",
  description: "PRISM Trading Competition Leaderboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <ClientBody>
        {children}
      </ClientBody>
    </html>
  );
}
