import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Sprout, ShieldCheck, LogIn, FileText, CheckSquare, Sparkles, ShieldAlert, Menu, X } from 'lucide-react';
import { LanguageToggle } from '../ui/LanguageToggle';

interface HeaderProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  user: any | null;
  onOpenAuthModal: () => void;
  onSignOut: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onSelectTab,
  user,
  onOpenAuthModal,
  onSignOut,
}) => {
  const { t } = useTranslation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isAdmin = Boolean(user && Array.isArray(user.roles) && user.roles.includes('ADMIN'));

  const handleNavClick = (tab: string) => {
    onSelectTab(tab);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-30 bg-white/50 backdrop-blur-md border-b border-white/50 shadow-[0_4px_24px_rgba(23,37,31,0.06)]" role="banner">
      {/* Top micro-bar for geography & trust disclaimer */}
      <div className="bg-field-100/60 border-b border-white/30 px-4 py-1 text-xs text-forest-800 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-forest-900 tracking-wide uppercase text-[10px] bg-white/80 px-2 py-0.5 rounded border border-white/60 shadow-2xs">
            {t('geographyTag')}
          </span>
          <span className="hidden sm:inline text-ink-950 font-medium drop-shadow-2xs">
            प्रामाणिक सरकारी योजनाओं का निष्पक्ष विश्लेषण • उत्तर प्रदेश
          </span>
        </div>
        <div className="flex items-center gap-3">
          {user ? (
            <span className="flex items-center gap-1 font-medium text-forest-800">
              <ShieldCheck className="w-3.5 h-3.5 text-leaf-600" />
              <span>{user.email}</span>
              {isAdmin && (
                <span className="ml-1 text-[10px] font-bold uppercase bg-forest-800 text-white px-1.5 py-0.5 rounded shadow-2xs">
                  ADMIN
                </span>
              )}
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 text-xs text-forest-900 font-medium">
              <span className="w-2 h-2 rounded-full bg-sun-400 animate-pulse" />
              <span>{t('nav.guestNotice')}</span>
            </span>
          )}
        </div>
      </div>

      {/* Main navigation row */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Wordmark and brand */}
        <button
          type="button"
          onClick={() => handleNavClick('home')}
          className="flex items-center gap-2.5 text-left focus-visible:outline-forest-800 rounded-subtle p-1 hover:bg-white/40 transition-colors"
          aria-label="YojanaSaathi Home"
        >
          <div className="w-9 h-9 rounded-natural bg-forest-800 flex items-center justify-center text-paper-50 shadow-sm border border-forest-700">
            <Sprout className="w-5 h-5 text-field-100" />
          </div>
          <div>
            <div className="font-serif text-lg font-bold text-forest-900 leading-tight tracking-tight drop-shadow-2xs">
              {t('appName')}
            </div>
            <div className="text-[11px] text-ink-950/80 font-sans font-medium">
              Farmer Benefit Navigator
            </div>
          </div>
        </button>

        {/* Desktop navigation tabs */}
        <nav className="hidden md:flex items-center gap-1.5 text-sm font-medium" role="navigation" aria-label="Main Navigation">
          <button
            type="button"
            onClick={() => handleNavClick('home')}
            aria-current={currentTab === 'home' ? 'page' : undefined}
            className={`px-3 py-1.5 rounded-subtle transition-all min-h-[38px] ${
              currentTab === 'home'
                ? 'bg-forest-800 text-white font-semibold shadow-xs'
                : 'text-ink-950 hover:text-forest-900 hover:bg-white/60'
            }`}
          >
            {t('nav.home')}
          </button>
          <button
            type="button"
            onClick={() => handleNavClick('wizard')}
            aria-current={currentTab === 'wizard' ? 'page' : undefined}
            className={`px-3 py-1.5 rounded-subtle transition-all min-h-[38px] flex items-center gap-1.5 ${
              currentTab === 'wizard'
                ? 'bg-forest-800 text-white font-semibold shadow-xs'
                : 'text-ink-950 hover:text-forest-900 hover:bg-white/60'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-leaf-600" />
            <span>पात्रता जाँच (Check Eligibility)</span>
          </button>
          <button
            type="button"
            onClick={() => handleNavClick('schemes')}
            aria-current={currentTab === 'schemes' ? 'page' : undefined}
            className={`px-3 py-1.5 rounded-subtle transition-all min-h-[38px] flex items-center gap-1.5 ${
              currentTab === 'schemes'
                ? 'bg-forest-800 text-white font-semibold shadow-xs'
                : 'text-ink-950 hover:text-forest-900 hover:bg-white/60'
            }`}
          >
            <CheckSquare className="w-3.5 h-3.5 text-leaf-600" />
            <span>{t('nav.schemes')}</span>
          </button>
          <button
            type="button"
            onClick={() => handleNavClick('action-plan')}
            aria-current={currentTab === 'action-plan' ? 'page' : undefined}
            className={`px-3 py-1.5 rounded-subtle transition-all min-h-[38px] flex items-center gap-1.5 ${
              currentTab === 'action-plan'
                ? 'bg-forest-800 text-white font-semibold shadow-xs'
                : 'text-ink-950 hover:text-forest-900 hover:bg-white/60'
            }`}
          >
            <FileText className="w-3.5 h-3.5 text-leaf-600" />
            <span>{t('nav.actionPlan')}</span>
          </button>

          {/* CRITICAL ADMIN RULE: Render Admin Review ONLY for authenticated users with ADMIN role */}
          {isAdmin && (
            <button
              type="button"
              onClick={() => handleNavClick('admin')}
              aria-current={currentTab === 'admin' ? 'page' : undefined}
              className={`px-3 py-1.5 rounded-subtle transition-all min-h-[38px] flex items-center gap-1 text-xs border border-forest-800/20 ${
                currentTab === 'admin'
                  ? 'bg-forest-800 text-white font-semibold shadow-xs'
                  : 'text-forest-900 bg-white/40 hover:bg-white/70'
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5 text-leaf-600" />
              <span>{t('nav.adminPortal')}</span>
            </button>
          )}
        </nav>

        {/* Right side controls: Language toggle, User auth, Mobile Hamburger */}
        <div className="flex items-center gap-2 sm:gap-3">
          <LanguageToggle className="bg-white/70 backdrop-blur-md border-white/60 shadow-2xs" />

          {user ? (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onSignOut}
                className="text-xs px-3 py-1.5 rounded-subtle border border-white/60 bg-white/70 hover:bg-white/90 text-ink-950 font-medium transition-colors shadow-2xs min-h-[36px]"
              >
                {t('nav.signOut')}
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenAuthModal}
              className="inline-flex items-center gap-1.5 text-xs sm:text-sm px-3.5 py-1.5 rounded-subtle bg-forest-800 hover:bg-forest-900 text-paper-50 border border-forest-900 font-medium transition-all shadow-xs min-h-[36px]"
            >
              <LogIn className="w-3.5 h-3.5 text-field-100" />
              <span>{t('nav.signIn')}</span>
            </button>
          )}

          {/* Mobile hamburger button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(prev => !prev)}
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle mobile menu"
            className="md:hidden p-2 rounded-subtle bg-white/60 hover:bg-white/80 border border-white/50 text-ink-950 focus-visible:outline-forest-800 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center shadow-2xs"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Responsive Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-white/40 bg-white/90 backdrop-blur-xl px-4 py-4 space-y-2 shadow-xl animate-in slide-in-from-top-2 duration-200">
          <button
            type="button"
            onClick={() => handleNavClick('home')}
            className={`w-full text-left px-3.5 py-2.5 rounded-subtle text-sm font-medium transition-all flex items-center justify-between ${
              currentTab === 'home'
                ? 'bg-forest-800 text-white font-semibold shadow-xs'
                : 'text-ink-950 hover:bg-white/60'
            }`}
          >
            <span>{t('nav.home')}</span>
          </button>

          <button
            type="button"
            onClick={() => handleNavClick('wizard')}
            className={`w-full text-left px-3.5 py-2.5 rounded-subtle text-sm font-medium transition-all flex items-center gap-2 ${
              currentTab === 'wizard'
                ? 'bg-forest-800 text-white font-semibold shadow-xs'
                : 'text-ink-950 hover:bg-white/60'
            }`}
          >
            <Sparkles className="w-4 h-4 text-leaf-600" />
            <span>पात्रता जाँच (Check Eligibility)</span>
          </button>

          <button
            type="button"
            onClick={() => handleNavClick('schemes')}
            className={`w-full text-left px-3.5 py-2.5 rounded-subtle text-sm font-medium transition-all flex items-center gap-2 ${
              currentTab === 'schemes'
                ? 'bg-forest-800 text-white font-semibold shadow-xs'
                : 'text-ink-950 hover:bg-white/60'
            }`}
          >
            <CheckSquare className="w-4 h-4 text-leaf-600" />
            <span>{t('nav.schemes')}</span>
          </button>

          <button
            type="button"
            onClick={() => handleNavClick('action-plan')}
            className={`w-full text-left px-3.5 py-2.5 rounded-subtle text-sm font-medium transition-all flex items-center gap-2 ${
              currentTab === 'action-plan'
                ? 'bg-forest-800 text-white font-semibold shadow-xs'
                : 'text-ink-950 hover:bg-white/60'
            }`}
          >
            <FileText className="w-4 h-4 text-leaf-600" />
            <span>{t('nav.actionPlan')}</span>
          </button>

          {/* Admin link in mobile drawer strictly if role is ADMIN */}
          {isAdmin && (
            <button
              type="button"
              onClick={() => handleNavClick('admin')}
              className={`w-full text-left px-3.5 py-2.5 rounded-subtle text-sm font-medium transition-all flex items-center gap-2 ${
                currentTab === 'admin'
                  ? 'bg-forest-800 text-white font-semibold shadow-xs'
                  : 'text-forest-900 bg-field-100/60 hover:bg-field-100'
              }`}
            >
              <ShieldAlert className="w-4 h-4 text-leaf-600" />
              <span>{t('nav.adminPortal')} (Admin Only)</span>
            </button>
          )}
        </div>
      )}
    </header>
  );
};
