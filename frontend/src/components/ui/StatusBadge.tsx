import React from 'react';
import { CheckCircle2, XCircle, HelpCircle } from 'lucide-react';

export type EligibilityStatus = 
  | 'PASS' 
  | 'FAIL' 
  | 'UNKNOWN' 
  | 'LIKELY_ELIGIBLE' 
  | 'NEEDS_MORE_INFO' 
  | 'LIKELY_NOT_ELIGIBLE'
  | 'COMPATIBLE_CONFIRMED'
  | 'INCOMPATIBLE_CONFIRMED'
  | 'UNKNOWN_REQUIRES_VERIFICATION';

interface StatusBadgeProps {
  status: EligibilityStatus | string;
  className?: string;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  className = '',
  showIcon = true,
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs font-medium px-2.5 py-1 gap-1.5',
    lg: 'text-sm font-semibold px-3 py-1.5 gap-2',
  }[size];

  switch (status) {
    case 'PASS':
    case 'LIKELY_ELIGIBLE':
    case 'COMPATIBLE_CONFIRMED':
      return (
        <span
          className={`inline-flex items-center rounded-natural bg-[#E8EFE4] text-[#244C3B] border border-[#D5E2CE] font-sans ${sizeClasses} ${className}`}
          role="status"
        >
          {showIcon && <CheckCircle2 className="w-3.5 h-3.5 text-[#28734D] shrink-0" />}
          <span>
            {status === 'PASS' && 'सत्यापित / PASS'}
            {status === 'LIKELY_ELIGIBLE' && 'संभावित पात्र / Likely Eligible'}
            {status === 'COMPATIBLE_CONFIRMED' && 'सह-अस्तित्व मान्य / Compatible'}
          </span>
        </span>
      );

    case 'FAIL':
    case 'LIKELY_NOT_ELIGIBLE':
    case 'INCOMPATIBLE_CONFIRMED':
      return (
        <span
          className={`inline-flex items-center rounded-natural bg-[#FBEBEA] text-[#A33D35] border border-[#F3C7C4] font-sans ${sizeClasses} ${className}`}
          role="status"
        >
          {showIcon && <XCircle className="w-3.5 h-3.5 text-[#A33D35] shrink-0" />}
          <span>
            {status === 'FAIL' && 'अपात्र / FAIL'}
            {status === 'LIKELY_NOT_ELIGIBLE' && 'अपात्र / Ineligible'}
            {status === 'INCOMPATIBLE_CONFIRMED' && 'टकराव / Incompatible'}
          </span>
        </span>
      );

    case 'UNKNOWN':
    case 'NEEDS_MORE_INFO':
    case 'UNKNOWN_REQUIRES_VERIFICATION':
    default:
      return (
        <span
          className={`inline-flex items-center rounded-natural bg-[#FCF6EB] text-[#95621C] border border-[#F2DEB6] font-sans ${sizeClasses} ${className}`}
          role="status"
        >
          {showIcon && <HelpCircle className="w-3.5 h-3.5 text-[#95621C] shrink-0" />}
          <span>
            {status === 'UNKNOWN' && 'अज्ञात / UNKNOWN'}
            {status === 'NEEDS_MORE_INFO' && 'अतिरिक्त जानकारी चाहिए / Needs Info'}
            {status === 'UNKNOWN_REQUIRES_VERIFICATION' && 'सत्यापन आवश्यक / Requires Verification'}
            {!['UNKNOWN', 'NEEDS_MORE_INFO', 'UNKNOWN_REQUIRES_VERIFICATION'].includes(status) && status}
          </span>
        </span>
      );
  }
};

