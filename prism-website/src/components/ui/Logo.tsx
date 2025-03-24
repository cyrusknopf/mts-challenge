"use client";

import React from 'react';
import Link from 'next/link';

interface LogoProps {
  variant?: 'full' | 'icon';
  className?: string;
}

export default function Logo({ variant = 'full', className = '' }: LogoProps) {
  return (
    <Link href="/" className={`text-white inline-block ${className}`}>
      {variant === 'icon' ? (
        <div className="text-white">
          <svg width="100" height="70" viewBox="0 0 100 70" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M50 0L0 70H100L50 0Z" fill="white" />
          </svg>
        </div>
      ) : (
        <div className="flex items-center">
          <div className="mr-4">
            <svg width="100" height="70" viewBox="0 0 100 70" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M50 0L0 70H100L50 0Z" fill="white" />
            </svg>
          </div>
          <div className="text-3xl font-light uppercase tracking-wider">
            PRISM
          </div>
        </div>
      )}
    </Link>
  );
}
