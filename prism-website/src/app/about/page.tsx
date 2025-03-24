import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import AnimatedButton from '@/components/ui/AnimatedButton';

export default function AboutPage() {
  return (
    <MainLayout>
      <div className="flex items-center justify-center h-screen">
        <div className="home-nav fixed bottom-0 z-20 w-full">
          <div className="flex items-center justify-center gap-4">
            <AnimatedButton href="/" tabIndex={-1}>
              Go Home
            </AnimatedButton>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
