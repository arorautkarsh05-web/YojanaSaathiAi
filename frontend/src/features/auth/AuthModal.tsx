import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Shield, X, AlertCircle } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { api } from '../../services/api';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (user: any) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onAuthSuccess }) => {
  const { t, i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [mode, setMode] = useState<'signin' | 'signup'>('signup');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [termsConsent, setTermsConsent] = useState(true);
  const [profileConsent, setProfileConsent] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (mode === 'signup' && !termsConsent) {
      setErrorMsg(isHindi ? 'कृपया सेवा शर्तों और मार्गदर्शन सूचना की सहमति दें।' : 'Please acknowledge the terms of service.');
      return;
    }

    setIsLoading(true);

    try {
      if (mode === 'signup') {
        try {
          await api.register(email, password, displayName, termsConsent);
        } catch (regErr: any) {
          // If the account already exists, prompt user to sign in
          if (regErr.message && regErr.message.includes('already exists')) {
            setErrorMsg(
              isHindi
                ? 'इस ईमेल से खाता पहले से मौजूद है। कृपया "खाते में प्रवेश करें (Sign In)" टैब चुनें।'
                : 'An account with this email already exists. Please switch to Sign In.'
            );
            setIsLoading(false);
            return;
          }
          throw regErr;
        }
      }

      // Login and establish active session
      const loginRes = await api.login(email, password);
      onAuthSuccess(loginRes.user);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'प्रमाणीकरण विफल रहा। कृपया विवरण पुनः जाँचें।');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-ink-950/45 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white/80 backdrop-blur-xl border border-white/70 rounded-panel max-w-md w-full p-6 shadow-[0_20px_60px_rgba(23,37,31,0.18),inset_0_1px_1px_rgba(255,255,255,0.85)] relative text-ink-950">
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 text-ink-950/50 hover:text-ink-950 p-1 rounded-full hover:bg-white/50 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Guest Mode Assurance Banner */}
        <div className="mb-5 p-3 rounded-natural bg-field-100/70 border border-field-200/80 backdrop-blur-sm text-xs text-forest-900 leading-relaxed shadow-xs">
          <div className="font-bold flex items-center gap-1.5 mb-0.5">
            <Shield className="w-3.5 h-3.5 text-leaf-600" />
            <span>{t('auth.guestNoticeHeader')}</span>
          </div>
          <div>{t('auth.guestNoticeBody')}</div>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-ink-950/10 mb-5">
          <button
            type="button"
            onClick={() => { setMode('signin'); setErrorMsg(null); }}
            className={`flex-1 pb-2.5 text-sm font-semibold border-b-2 transition-colors ${
              mode === 'signin'
                ? 'border-forest-800 text-forest-900'
                : 'border-transparent text-ink-950/50 hover:text-ink-950'
            }`}
          >
            {t('auth.signInTitle')}
          </button>
          <button
            type="button"
            onClick={() => { setMode('signup'); setErrorMsg(null); }}
            className={`flex-1 pb-2.5 text-sm font-semibold border-b-2 transition-colors ${
              mode === 'signup'
                ? 'border-forest-800 text-forest-900'
                : 'border-transparent text-ink-950/50 hover:text-ink-950'
            }`}
          >
            {t('auth.signUpTitle')}
          </button>
        </div>

        {errorMsg && (
          <div className="mb-4 p-3 rounded-natural bg-[#FBEBEA]/90 border border-[#F3C7C4] text-xs text-brandDanger flex items-start gap-2 shadow-xs backdrop-blur-sm">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <div className="leading-snug font-medium">{errorMsg}</div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {mode === 'signup' && (
            <div>
              <label className="block font-semibold text-ink-950 mb-1">
                {t('auth.nameLabel')}
              </label>
              <input
                type="text"
                value={displayName}
                onChange={e => setDisplayName(e.target.value)}
                placeholder="उदा. रमेश कुमार / Utkarsh Arora"
                className="w-full px-3 py-2 rounded-subtle border border-white/70 bg-white/70 text-ink-950 placeholder:text-ink-950/40 text-xs backdrop-blur-sm focus:bg-white/95 focus:border-forest-700 focus:outline-none transition-all shadow-xs"
              />
            </div>
          )}

          <div>
            <label className="block font-semibold text-ink-950 mb-1">
              {t('auth.emailLabel')} <span className="text-brandDanger">*</span>
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="farmer@example.com"
              className="w-full px-3 py-2 rounded-subtle border border-white/70 bg-white/70 text-ink-950 placeholder:text-ink-950/40 text-xs backdrop-blur-sm focus:bg-white/95 focus:border-forest-700 focus:outline-none transition-all shadow-xs"
            />
          </div>

          <div>
            <label className="block font-semibold text-ink-950 mb-1">
              {t('auth.passwordLabel')} <span className="text-brandDanger">*</span>
            </label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="कम से कम 8 अक्षर / Min 8 characters"
              className="w-full px-3 py-2 rounded-subtle border border-white/70 bg-white/70 text-ink-950 placeholder:text-ink-950/40 text-xs backdrop-blur-sm focus:bg-white/95 focus:border-forest-700 focus:outline-none transition-all shadow-xs"
            />
          </div>

          {mode === 'signup' && (
            <div className="space-y-2 pt-2 border-t border-ink-950/10">
              <label className="flex items-start gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={termsConsent}
                  onChange={e => setTermsConsent(e.target.checked)}
                  className="mt-0.5 rounded border-ink-950/30 text-forest-800"
                />
                <span className="text-ink-950/70 leading-tight">
                  {t('auth.consentCheckbox')}
                </span>
              </label>
              <label className="flex items-start gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={profileConsent}
                  onChange={e => setProfileConsent(e.target.checked)}
                  className="mt-0.5 rounded border-ink-950/30 text-forest-800"
                />
                <span className="text-ink-950/70 leading-tight">
                  अलग सहमति: मैं भविष्य के उपयोग हेतु अपनी किसान प्रोफ़ाइल को सुरक्षित सहेजना चाहता हूँ।
                </span>
              </label>
            </div>
          )}

          <div className="pt-2">
            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={isLoading}
              className="w-full shadow-md"
            >
              {mode === 'signin' ? t('auth.signInBtn') : t('auth.signUpBtn')}
            </Button>
          </div>
        </form>

        <div className="mt-4 pt-3 border-t border-ink-950/10 text-center">
          <button
            type="button"
            onClick={onClose}
            className="text-xs text-forest-800 hover:text-forest-950 hover:underline font-semibold"
          >
            {t('auth.continueAsGuest')}
          </button>
        </div>
      </div>
    </div>
  );
};
