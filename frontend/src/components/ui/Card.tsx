import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'surface' | 'flat' | 'highlight' | 'muted';
  as?: React.ElementType;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'surface',
  as: Component = 'div',
  className = '',
  ...props
}) => {
  const variantStyles = {
    surface: 'bg-white/50 backdrop-blur-lg border border-white/50 text-ink-950 shadow-[0_8px_32px_rgba(23,37,31,0.06),inset_0_1px_1px_rgba(255,255,255,0.7)]',
    flat: 'bg-white/40 backdrop-blur-md border border-white/40 text-ink-950 shadow-[0_4px_20px_rgba(23,37,31,0.04)]',
    highlight: 'bg-[#E8EFE4]/55 backdrop-blur-lg border border-[#D5E2CE]/70 text-forest-900 shadow-[0_4px_20px_rgba(36,76,59,0.05)]',
    muted: 'bg-white/30 backdrop-blur-sm border border-white/30 text-ink-950',
  }[variant];

  return (
    <Component
      className={`rounded-panel p-5 sm:p-6 transition-all duration-200 ${variantStyles} ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
};
