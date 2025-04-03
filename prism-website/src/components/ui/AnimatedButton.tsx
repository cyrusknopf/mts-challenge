// "use client";
//
// import React from 'react';
// import Link from 'next/link';
//
// interface AnimatedButtonProps {
//   children: React.ReactNode;
//   href?: string;
//   onClick?: () => void;
//   className?: string;
//   tabIndex?: number;
// }
//
// export default function AnimatedButton({
//   children,
//   href,
//   onClick,
//   className = '',
//   tabIndex = 0,
// }: AnimatedButtonProps) {
//   const baseClasses = `group relative flex h-[50px] w-[150px] items-center justify-center overflow-hidden rounded-[3px] border-0 bg-transparent px-5 py-4 font-light uppercase leading-none text-white shadow-md transition-all duration-300 ease-in-out hover:scale-105 ${className}`;
//
//   const content = (
//     <>
//       {/* Button Text */}
//       <span className="relative z-10 text-center break-words font-albert-sans text-base font-light">
//         {children}
//       </span>
//       {/* Top Bar */}
//       <span
//         className="absolute left-0 right-0 h-0.5 bg-white opacity-0 transition-all duration-300 ease-in-out
//                    top-0 group-hover:top-1/2 group-hover:-translate-y-1/2 group-hover:opacity-100"
//       ></span>
//       {/* Bottom Bar */}
//       <span
//         className="absolute left-0 right-0 h-0.5 bg-white opacity-0 transition-all duration-300 ease-in-out
//                    top-full group-hover:top-1/2 group-hover:-translate-y-1/2 group-hover:opacity-100"
//       ></span>
//     </>
//   );
//
//   if (href) {
//     return (
//       <Link href={href} tabIndex={tabIndex} className={baseClasses}>
//         {content}
//       </Link>
//     );
//   }
//
//   return (
//     <button type="button" onClick={onClick} tabIndex={tabIndex} className={baseClasses}>
//       {content}
//     </button>
//   );
// }

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
  const baseClasses = `group relative flex h-[50px] w-[150px] items-center justify-center overflow-hidden rounded-[3px] border-0 bg-white/3 px-5 py-4 font-light uppercase leading-none text-white shadow-xl transition-all duration-300 ease-in-out hover:scale-105 ${className}`;

  const content = (
    <>
      {/* Button Text */}
      <span className="relative z-10 text-center break-words font-albert-sans text-base font-light">
        {children}
      </span>
      {/* Top Bar */}
      <span
        className="absolute left-0 right-0 h-0.5 bg-white opacity-0 transition-all duration-300 ease-in-out
                   top-0 group-hover:top-1/2 group-hover:-translate-y-1/2 group-hover:opacity-100"
      ></span>
      {/* Bottom Bar */}
      <span
        className="absolute left-0 right-0 h-0.5 bg-white opacity-0 transition-all duration-300 ease-in-out
                   top-full group-hover:top-1/2 group-hover:-translate-y-1/2 group-hover:opacity-100"
      ></span>
    </>
  );

  if (href) {
    return (
      <Link href={href} tabIndex={tabIndex} className={baseClasses}>
        {content}
      </Link>
    );
  }

  return (
    <button type="button" onClick={onClick} tabIndex={tabIndex} className={baseClasses}>
      {content}
    </button>
  );
}
