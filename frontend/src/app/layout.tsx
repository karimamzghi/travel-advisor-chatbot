import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LostNoMore — AI Travel Advisor",
  description:
    "Create personalized travel itineraries with AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
