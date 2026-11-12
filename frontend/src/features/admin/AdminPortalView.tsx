import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldAlert, Lock, ArrowLeft, LogIn } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { api } from '../../services/api';

interface AdminPortalViewProps {
  onBack: () => void;
  user?: any | null;
  onOpenAuthModal?: () => void;
}

export const AdminPortalView: React.FC<AdminPortalViewProps> = ({ 
  onBack, 
  user, 
  onOpenAuthModal 
}) => {
  const { i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [schemes, setSchemes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const isAdmin = Boolean(user && Array.isArray(user.roles) && user.roles.includes('ADMIN'));

  useEffect(() => {
    if (!isAdmin) {
      setLoading(false);
      return;
    }
    api.getSchemes()
      .then(data => {
        setSchemes(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [isAdmin]);

  // If user is not authenticated as an ADMIN, show strict role-access boundary
  if (!isAdmin) {
    return (
      <div className="max-w-2xl mx-auto py-16 px-4">
        <div className="p-8 rounded-panel bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_16px_50px_rgba(23,37,31,0.12)] text-center space-y-5">
          <div className="w-14 h-14 rounded-full bg-brandDanger/10 text-brandDanger flex items-center justify-center mx-auto border border-brandDanger/20">
            <Lock className="w-7 h-7" />
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-brandDanger bg-brandDanger/10 px-3 py-1 rounded-full">
              403 — Unauthorized Administrative Access
            </span>
            <h1 className="font-serif text-2xl sm:text-3xl font-bold text-forest-900 mt-3">
              {isHindi ? 'प्रशासकीय समीक्षा क्षेत्र सुरक्षित है' : 'Administrative Review Portal Restricted'}
            </h1>
            <p className="text-sm text-ink-950/80 max-w-md mx-auto mt-2 leading-relaxed">
              {isHindi 
                ? 'यह क्षेत्र केवल अधिकृत समीक्षा अधिकारियों (ADMIN Role) के लिए आरक्षित है। सामान्य किसान एवं अतिथि उपयोगकर्ताओं को यहाँ प्रवेश की अनुमति नहीं है।'
                : 'This section is strictly reserved for authorized reviewers with verified ADMIN roles. Ordinary farmer and guest sessions cannot access administrative rule logs.'}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-3">
            {onOpenAuthModal && (
              <Button
                variant="primary"
                size="md"
                onClick={onOpenAuthModal}
                leftIcon={<LogIn className="w-4 h-4" />}
                className="w-full sm:w-auto"
              >
                {isHindi ? 'प्रशासक लॉगिन करें' : 'Sign In as Administrator'}
              </Button>
            )}
            <Button
              variant="secondary"
              size="md"
              onClick={onBack}
              leftIcon={<ArrowLeft className="w-4 h-4" />}
              className="w-full sm:w-auto bg-white/70 hover:bg-white"
            >
              {isHindi ? 'मुख्य पृष्ठ पर वापस जाएँ' : 'Back to Home'}
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 p-6 rounded-panel bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_30px_rgba(23,37,31,0.08)] mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-forest-800 text-paper-50 flex items-center gap-1">
              <ShieldAlert className="w-3 h-3 text-leaf-600" />
              <span>प्रशासकीय समीक्षा पोर्टल • Admin Audit</span>
            </span>
            <span className="text-xs text-muted font-mono">v3.0.0</span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-forest-900">
            {isHindi ? 'सत्यापित योजना एवं नियम पंजीका' : 'Statutory Scheme & Rule Register'}
          </h1>
          <p className="text-xs sm:text-sm text-ink-950/70 mt-1">
            प्रत्येक नियम एवं सह-अस्तित्व शर्त उत्तर प्रदेश एवं भारत सरकार के आधिकारिक राजपत्रों से सत्यापित है।
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={onBack} className="bg-white/80 hover:bg-white border-white/80 shadow-2xs">
          {isHindi ? 'वापस मुख्य पृष्ठ' : 'Back to Home'}
        </Button>
      </div>

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <Card variant="surface">
          <div className="text-xs font-semibold text-muted uppercase tracking-wider">सत्यापित योजनाएँ</div>
          <div className="text-2xl font-bold text-forest-900 font-serif mt-1">6 योजनाएँ</div>
          <div className="text-[11px] text-muted-dark mt-1">100% आधिकारिक साक्ष्य उपलब्ध</div>
        </Card>
        <Card variant="surface">
          <div className="text-xs font-semibold text-muted uppercase tracking-wider">नियम इंजन तर्क</div>
          <div className="text-2xl font-bold text-forest-900 font-serif mt-1">3-Valued Logic</div>
          <div className="text-[11px] text-muted-dark mt-1">PASS / FAIL / UNKNOWN</div>
        </Card>
        <Card variant="surface">
          <div className="text-xs font-semibold text-muted uppercase tracking-wider">अभिसरण साक्ष्य (Convergence)</div>
          <div className="text-2xl font-bold text-forest-900 font-serif mt-1">5 गजट जोड़े</div>
          <div className="text-[11px] text-muted-dark mt-1">अपुष्ट जोड़े UNKNOWN सुरक्षित</div>
        </Card>
      </div>

      {/* Verified Schemes Table */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-forest-900 font-serif">
          उत्तर प्रदेश सक्रिय योजना पंजीका (Active UP Register)
        </h2>

        {loading ? (
          <div className="p-8 text-center text-sm text-muted">डेटा लोड हो रहा है...</div>
        ) : (
          schemes.map(s => (
            <Card key={s.scheme_code} variant="surface" className="p-5 border-appBorder">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono font-bold bg-field-100 text-forest-800 px-2 py-0.5 rounded border border-field-200">
                      {s.scheme_code}
                    </span>
                    <span className="text-xs text-muted">{s.level} • {s.department}</span>
                  </div>
                  <h3 className="font-bold text-ink-950 font-serif text-base">
                    {s.official_name_hi} ({s.official_name_en})
                  </h3>
                </div>
                <div className="text-right text-[11px] text-muted font-mono shrink-0">
                  समीक्षक: {s.verified_by}<br />
                  अंतिम सत्यापन: {new Date(s.verified_at).toLocaleDateString()}
                </div>
              </div>

              {/* Source Details */}
              <div className="p-3 rounded-natural bg-paper-50 border border-appBorder text-xs space-y-1 mb-3">
                <div className="font-semibold text-forest-900">राजपत्र / मार्गदर्शिका स्रोत:</div>
                <div className="text-muted-dark">{s.source_title} ({s.source_section})</div>
                <div className="text-[11px] font-mono text-leaf-600 truncate">{s.source_url}</div>
              </div>

              {/* Rules list */}
              <div>
                <div className="text-xs font-bold text-muted uppercase tracking-wider mb-2">
                  कम्प्यूटेशनल पात्रता नियम ({s.rules?.length || 0}):
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  {s.rules?.map((r: any) => (
                    <div key={r.rule_code} className="p-2.5 rounded bg-paper-100 border border-appBorder">
                      <div className="font-bold text-forest-900">{r.title_hi}</div>
                      <div className="text-[11px] text-muted mt-0.5 font-mono">
                        {r.field_name} {r.operator} {JSON.stringify(r.target_value)}
                      </div>
                      <div className="text-[10px] text-muted-dark mt-1 italic">{r.citation}</div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};
