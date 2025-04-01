"use client";

import React from 'react';
import AnimatedButton from '../ui/AnimatedButton';

export default function HomeNavigation() {
  return (
    <div className="home-nav fixed bottom-0 z-20 w-full overflow-hidden">
      <div className="ml-0 flex items-center justify-center gap-4 sm:ml-5 md:ml-5 lg:ml-6 xl:ml-5 2xl:ml-6 3xl:ml-[30px]">
        <AnimatedButton href="/leaderboard" tabIndex={-1}>
          Leaderboard
        </AnimatedButton>
        <AnimatedButton href="/about" tabIndex={-1}>
          Information
        </AnimatedButton>
      </div>
    </div>
  );
}
