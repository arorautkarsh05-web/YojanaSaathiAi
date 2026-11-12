import React from 'react';
import { useTranslation } from 'react-i18next';
import { Languages } from 'lucide-react';

export const LanguageToggle: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { i18n } = useTranslation();
  const currentLang = i18n.resolvedLanguage || i18n.language || 'hi';

  const toggleLanguage = (lang: 'hi' | 'en') => {
    i18n.changeLanguage(lang);
    document.documentElement.lang = lang;
  };

  return (
    <div
      className={`inline-flex items-center p-1 rounded-subtle bg-paper-100 border border-appBorder text-xs font-medium ${className}`}
      role="group"
      aria-label="Language selector / भाषा चयनकर्ता"
    >
      <Languages className="w-3.5 h-3.5 text-muted ml-1.5 mr-1" aria-hidden="true" />
      <button
        type="button"
        onClick={() => toggleLanguage('hi')}
        className={`px-2 py-1 rounded-[4px] transition-colors focus-visible:outline-forest-800 ${
          currentLang.startsWith('hi')
            ? 'bg-forest-800 text-paper-50 font-semibold shadow-xs'
            : 'text-muted-dark hover:text-ink-950'
        }`}
        aria-pressed={currentLang.startsWith('hi')}
      >
        हिन्दी
      </button>
      <button
        type="button"
        onClick={() => toggleLanguage('en')}
        className={`px-2 py-1 rounded-[4px] transition-colors focus-visible:outline-forest-800 ${
          currentLang.startsWith('en')
            ? 'bg-forest-800 text-paper-50 font-semibold shadow-xs'
            : 'text-muted-dark hover:text-ink-950'
        }`}
        aria-pressed={currentLang.startsWith('en')}
      >
        English
      </button>
    </div>
  );
};

