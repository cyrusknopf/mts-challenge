"use client";

import React, { useEffect, useRef } from 'react';

interface VideoBackgroundProps {
  src: string;
  className?: string;
}

export default function VideoBackground({ src, className = '' }: VideoBackgroundProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (video) {
      video.play().catch(error => {
        console.error("Video autoplay failed:", error);
      });
    }
  }, []);

  return (
    <video
      ref={videoRef}
      id="vid"
      className={`fixed left-0 top-0 -z-10 h-full w-full object-cover h-full duration-200 ${className}`}
      autoPlay
      muted
      loop
      playsInline
      preload="auto"
    >
      <source src={src} type="video/mp4" media="(min-width: 768px)" />
      Your browser does not support the video tag.
    </video>
  );
}
