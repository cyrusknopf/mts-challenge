"use client";

import React from 'react';
import VideoBackground from '../ui/VideoBackground';

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <main className="relative h-screen w-full overflow-hidden">
      <VideoBackground src="/videos/desktop-bg.mp4" />
      <div className="relative z-10">
        {children}
      </div>
    </main>
  );
}
