import React from 'react';
import upAgroImage from '../../assets/up-agro-climatic-zones.jpg';

export const AgriculturalFieldScene: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div
      className={`relative w-full max-w-xl mx-auto rounded-panel overflow-hidden border border-white/60 bg-white/45 backdrop-blur-md shadow-[0_12px_40px_rgba(23,37,31,0.12),inset_0_1px_1px_rgba(255,255,255,0.85)] transition-all duration-300 hover:shadow-[0_16px_48px_rgba(23,37,31,0.16)] ${className}`}
    >
      <img
        src={upAgroImage}
        alt="UP Agro-Climatic Zones - 4-चरणीय पारदर्शी किसान यात्रा (75 Districts)"
        className="w-full h-auto object-cover block select-none transition-transform duration-500 hover:scale-[1.01]"
        loading="eager"
        decoding="async"
      />
    </div>
  );
};
