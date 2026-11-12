import React, { useRef, useEffect } from 'react';

interface BackgroundVideoProps {
  videoSrc?: string;
}

export const BackgroundVideo: React.FC<BackgroundVideoProps> = ({
  videoSrc = '/background.mp4',
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const handleMotionChange = (e: MediaQueryListEvent) => {
      if (e.matches && videoRef.current) {
        videoRef.current.pause();
      } else if (!e.matches && videoRef.current) {
        videoRef.current.play().catch(() => {});
      }
    };

    motionQuery.addEventListener('change', handleMotionChange);

    const handleVisibilityChange = () => {
      if (document.hidden && videoRef.current) {
        videoRef.current.pause();
      } else if (!document.hidden && videoRef.current && !motionQuery.matches) {
        videoRef.current.play().catch(() => {});
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    if (videoRef.current) {
      videoRef.current.muted = true;
      videoRef.current.volume = 0;
      if (!motionQuery.matches) {
        videoRef.current.play().catch(() => {});
      } else {
        videoRef.current.pause();
      }
    }

    return () => {
      motionQuery.removeEventListener('change', handleMotionChange);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  return (
    <div
      className="fixed inset-0 w-full h-full -z-10 pointer-events-none overflow-hidden print:hidden select-none"
      aria-hidden="true"
    >
      {/* Background Video Element - Dominant, Vivid & Trimmed (First 2s removed, audio stripped) */}
      <video
        ref={videoRef}
        src={videoSrc}
        autoPlay
        loop
        muted
        playsInline
        preload="auto"
        className="w-full h-full object-cover brightness-[0.98] contrast-[1.02] transition-opacity duration-700"
      />

      {/* Atmospheric Glass Vignette */}
      <div className="absolute inset-0 bg-gradient-to-b from-ink-950/25 via-transparent to-ink-950/45 mix-blend-multiply" />
      <div className="absolute inset-0 bg-paper-50/15 backdrop-blur-[0.5px]" />
    </div>
  );
};
