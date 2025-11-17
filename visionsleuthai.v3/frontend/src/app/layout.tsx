import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'VisionSleuth AI - Advanced Crime Detection',
  description: 'Advanced AI-powered crime detection system for enhanced security and surveillance.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
} 