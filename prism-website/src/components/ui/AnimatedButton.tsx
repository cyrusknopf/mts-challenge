"use client";

import React from 'react';
import Link from 'next/link';

interface AnimatedButtonProps {
  children: React.ReactNode;
  href?: string;
  onClick?: () => void;
  className?: string;
  tabIndex?: number;
}

export default function AnimatedButton({
  children,
  href,
  onClick,
  className = '',
  tabIndex = 0,
}: AnimatedButtonProps) {
  const buttonContent = (
    <>
      <span className="btn-text select-none font-albert-sans text-base font-light leading-none">
        {children}
      </span>
      <span className="absolute bottom-0 left-0 right-0 top-0">
        <span className="top bg-white outline"></span>
        <span className="bottom bg-white outline"></span>
      </span>
    </>
  );

  const buttonClasses = `relative appearance-none overflow-hidden rounded-[3px] border-0 bg-transparent px-5 py-4 font-light uppercase leading-none text-white shadow-animated-btn transition-colors duration-100 ease-in-out w-[125px] ${className}`;

  if (href) {
    return (
      <Link
        href={href}
        className={buttonClasses}
        tabIndex={tabIndex}
      >
        {buttonContent}
      </Link>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={buttonClasses}
      tabIndex={tabIndex}
    >
      {buttonContent}
    </button>
  );
}
