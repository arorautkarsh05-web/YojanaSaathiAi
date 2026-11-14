import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Printer, ArrowLeft, CheckCircle2, Circle, MapPin, Compass, ShieldAlert, WifiOff
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { StatusBadge } from '../../components/ui/StatusBadge';
import type { ActionPlanData } from '../../services/api';

interface ActionPlanViewProps {
  planData: ActionPlanData;
  onBack: () => void;
}

export const ActionPlanView: React.FC<ActionPlanViewProps> = ({ planData, onBack }) => {
  const { t, i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [checklist, setChecklist] = useState(planData.checklist_items);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  // Rural low-bandwidth resilience: cache plan in localStorage
  useEffect(() => {
    try {
      localStorage.setItem(`yojanasaathi_plan_${planData.plan_number}`, JSON.stringify(planData));
      localStorage.setItem('yojanasaathi_latest_plan_number', planData.plan_number);
    } catch {
      // ignore quota error
    }

    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [planData]);

  const toggleDoc = (id: string) => {
    setChecklist(prev =>
      prev.map(item => (item.id === id ? { ...item, is_ready: !item.is_ready } : item))
    );
  };

  const handlePrint = () => {
    window.print();
  };

  const readyCount = checklist.filter(c => c.is_ready).length;
  const isDocsComplete = readyCount === checklist.length && checklist.length > 0;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 print:p-0">
      {/* Top action bar (hidden in print) */}
      <div className="flex items-center justify-between gap-4 mb-6 no-print">
        <Button variant="secondary" size="sm" leftIcon={<ArrowLeft className="w-4 h-4" />} onClick={onBack}>
          {isHindi ? 'वापस परिणामों पर जाएँ' : 'Back to Results'}
        </Button>
        <div className="flex items-center gap-2">
          <Button variant="primary" size="sm" leftIcon={<Printer className="w-4 h-4" />} onClick={handlePrint}>
            {isHindi ? 'कार्य योजना प्रिंट / सुरक्षित करें' : 'Print / Save Action Plan'}
          </Button>
        </div>
      </div>

      {isOffline && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-natural flex items-center gap-2 text-xs text-amber-900 no-print">
          <WifiOff className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{isHindi ? 'ऑफ़लाइन मोड सक्रिय: यह कार्य योजना आपके ब्राउज़र में सुरक्षित है और बिना इंटरनेट के उपलब्ध रहेगी।' : 'Offline Mode Active: This action plan is cached locally and available without internet.'}</span>
        </div>
      )}

      {/* Printable Document Container */}
      <div className="bg-white/80 backdrop-blur-xl border border-white/60 rounded-panel p-6 sm:p-10 shadow-[0_12px_40px_rgba(23,37,31,0.08)] print:bg-white print:border-none print:shadow-none print-page">
        {/* Document Header */}
        <div className="border-b-2 border-forest-800 pb-5 mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-field-100 text-forest-800 border border-field-200">
                  उत्तर प्रदेश कृषि कल्याण एवं अभिसरण
                </span>
                <span className="text-xs text-muted font-mono">{planData.plan_number}</span>
              </div>
              <h1 className="font-serif text-2xl sm:text-3xl font-bold text-forest-900 mt-1">
                {t('actionPlan.title')}
              </h1>
            </div>
            <div className="text-right text-xs text-muted">
              <div>{t('actionPlan.generatedOn')}:</div>
              <div className="font-semibold text-ink-950 font-mono">
                {new Date(planData.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
          <p className="text-xs text-muted-dark mt-2 italic">
            {t('actionPlan.validityNotice')}
          </p>
        </div>

        {/* 7-Stage Farmer Benefit Journey Tracker */}
        <div className="mb-8 p-4 rounded-natural bg-paper-100/80 border border-appBorder">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-forest-900 flex items-center gap-1.5">
              <Compass className="w-4 h-4 text-forest-700" />
              <span>{isHindi ? '7-चरणीय पारदर्शी किसान लाभ यात्रा (Farmer Benefit Journey)' : '7-Stage Transparent Farmer Benefit Journey'}</span>
            </h2>
            <span className="text-[11px] font-semibold text-leaf-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              {isHindi ? 'चरण 4 सक्रिय' : 'Stage 4 Active'}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 text-center text-[10px]">
            <div className="p-2 rounded bg-emerald-100/80 border border-emerald-300 text-emerald-950 font-medium">
              <div className="text-xs font-bold text-emerald-900 mb-0.5">1. प्रोफाइल ✓</div>
              <div>{isHindi ? 'सत्यापित विवरण' : 'Profile Done'}</div>
            </div>
            <div className="p-2 rounded bg-emerald-100/80 border border-emerald-300 text-emerald-950 font-medium">
              <div className="text-xs font-bold text-emerald-900 mb-0.5">2. पात्रता जाँच ✓</div>
              <div>{isHindi ? 'नियम मूल्यांकन' : 'Eligible Evaluated'}</div>
            </div>
            <div className="p-2 rounded bg-emerald-100/80 border border-emerald-300 text-emerald-950 font-medium">
              <div className="text-xs font-bold text-emerald-900 mb-0.5">3. छूटी जानकारी ✓</div>
              <div>{isHindi ? 'आवश्यकता पहचानी' : 'Gaps Resolved'}</div>
            </div>
            <div className={`p-2 rounded border font-medium ${isDocsComplete ? 'bg-emerald-100/80 border-emerald-300 text-emerald-950' : 'bg-field-100 border-forest-800 text-forest-950 shadow-2xs'}`}>
              <div className="text-xs font-bold text-forest-900 mb-0.5">4. दस्तावेज़ {isDocsComplete ? '✓' : `(${readyCount}/${checklist.length})`}</div>
              <div>{isHindi ? (isDocsComplete ? 'दस्तावेज़ पूर्ण' : 'तैयारी जारी') : 'Docs Prep'}</div>
            </div>
            <div className="p-2 rounded bg-paper-50 border border-appBorder text-ink-950/70">
              <div className="text-xs font-bold text-ink-950/80 mb-0.5">5. आधिकारिक आवेदन</div>
              <div>{isHindi ? 'पोर्टल मार्गदर्शन' : 'Official Portal'}</div>
            </div>
            <div className="p-2 rounded bg-paper-50 border border-appBorder text-ink-950/60">
              <div className="text-xs font-bold text-ink-950/70 mb-0.5">6. किसान प्रगति</div>
              <div>{isHindi ? 'स्वयं दर्ज स्थिति' : 'Farmer Reported'}</div>
            </div>
            <div className="p-2 rounded bg-paper-50 border border-appBorder text-ink-950/60">
              <div className="text-xs font-bold text-ink-950/70 mb-0.5">7. लाभ संपुष्टि</div>
              <div>{isHindi ? 'विभागीय सत्यापन' : 'Govt Verified'}</div>
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-appBorder/80 flex items-start gap-1.5 text-[10px] text-muted-dark">
            <ShieldAlert className="w-3.5 h-3.5 text-forest-700 shrink-0 mt-0.5" />
            <span>
              {isHindi
                ? 'पारदर्शिता सूचना: चरण 1-5 योजना साथी द्वारा गजट नियमों से संचालित हैं। चरण 6-7 किसान द्वारा स्वयं दर्ज की जाने वाली प्रगति है। आधिकारिक स्वीकृति केवल सक्षम सरकारी विभाग द्वारा प्रदान की जाती है।'
                : 'Transparency Notice: Stages 1-5 are guided by YojanaSaathi based on gazetted rules. Stages 6-7 represent farmer self-reported status. Official sanction is granted solely by the respective government authority.'}
            </span>
          </div>
        </div>

        {/* Section 1: Selected Schemes & Eligibility */}
        <div className="mb-8">
          <h2 className="text-sm font-bold uppercase tracking-wider text-forest-900 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-forest-800" />
            1. {t('actionPlan.selectedSchemes')}
          </h2>
          <div className="space-y-3">
            {planData.selected_schemes.map(scheme => (
              <div
                key={scheme.scheme_code}
                className="p-3.5 rounded-natural border border-appBorder bg-paper-50 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
              >
                <div>
                  <div className="font-bold text-forest-900 text-sm">
                    {isHindi ? scheme.official_name_hi : scheme.official_name_en}
                  </div>
                  <div className="text-muted mt-0.5">
                    {scheme.department} • {scheme.level === 'CENTRAL' ? 'केंद्रीय योजना' : 'राज्य योजना'}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <StatusBadge status={scheme.overall_status} size="sm" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 2: Pairwise Convergence & Compatibility */}
        {planData.convergence_summary.length > 0 && (
          <div className="mb-8">
            <h2 className="text-sm font-bold uppercase tracking-wider text-forest-900 mb-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-forest-800" />
              2. बहु-योजना सह-अस्तित्व स्थिति (Multi-Scheme Convergence)
            </h2>
            <div className="space-y-2.5">
              {planData.convergence_summary.map((pair, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-natural border border-appBorder bg-paper-100 text-xs"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-forest-900">
                      {pair.scheme_code_a} ↔ {pair.scheme_code_b}
                    </span>
                    <StatusBadge status={pair.status} size="sm" />
                  </div>
                  <p className="text-muted-dark leading-relaxed">
                    {pair.evidence_text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Section 3: Document Readiness Checklist */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold uppercase tracking-wider text-forest-900 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-forest-800" />
              3. {t('actionPlan.docChecklist')}
            </h2>
            <span className="text-xs font-semibold text-leaf-600">
              {readyCount} / {checklist.length} दस्तावेज़ तैयार
            </span>
          </div>

          <div className="space-y-2.5">
            {checklist.map(doc => (
              <button
                key={doc.id}
                type="button"
                onClick={() => toggleDoc(doc.id)}
                className={`w-full text-left p-3.5 rounded-natural border transition-all flex items-start justify-between gap-3 text-xs ${
                  doc.is_ready
                    ? 'border-forest-800 bg-field-100/70 text-forest-900 shadow-2xs backdrop-blur-md'
                    : 'border-white/50 bg-white/60 hover:bg-white/80 text-ink-950 backdrop-blur-sm shadow-2xs'
                }`}
              >
                <div className="flex items-start gap-2.5">
                  <div className="mt-0.5">
                    {doc.is_ready ? (
                      <CheckCircle2 className="w-4 h-4 text-brandSuccess shrink-0" />
                    ) : (
                      <Circle className="w-4 h-4 text-muted shrink-0" />
                    )}
                  </div>
                  <div>
                    <div className="font-semibold text-sm">
                      {isHindi ? doc.title_hi : doc.title_en}
                    </div>
                    <div className="text-muted mt-0.5">
                      जारीकर्ता प्राधिकारी: {doc.source_authority}
                    </div>
                    <div className="flex items-center gap-2 mt-1.5">
                      {doc.required_for_schemes.length > 1 ? (
                        <span className="text-[10px] font-semibold bg-emerald-100/90 text-emerald-800 px-1.5 py-0.5 rounded border border-emerald-200">
                          {isHindi ? `साझा दस्तावेज़ (${doc.required_for_schemes.length} योजनाएँ)` : `Shared (${doc.required_for_schemes.length} Schemes)`}
                        </span>
                      ) : (
                        <span className="text-[10px] font-medium bg-paper-100 text-muted-dark px-1.5 py-0.5 rounded border border-appBorder">
                          {isHindi ? 'योजना विशिष्ट' : 'Single Scheme'}
                        </span>
                      )}
                      <span className="text-[11px] font-mono text-leaf-700">
                        {doc.required_for_schemes.join(', ')}
                      </span>
                    </div>
                  </div>
                </div>

                <span className={`text-[11px] font-medium px-2 py-0.5 rounded border shrink-0 ${
                  doc.is_ready
                    ? 'bg-field-100 text-forest-800 border-field-200'
                    : 'bg-paper-100 text-muted-dark border-appBorder'
                }`}>
                  {doc.is_ready ? t('actionPlan.haveIt') : t('actionPlan.missing')}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Section 4: Verified Official Application Next Steps */}
        <div className="mb-8">
          <h2 className="text-sm font-bold uppercase tracking-wider text-forest-900 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-forest-800" />
            4. {t('actionPlan.officialSteps')}
          </h2>

          <div className="space-y-3">
            {planData.official_steps.map(step => (
              <div
                key={step.step_number}
                className="p-4 rounded-natural border border-appBorder bg-paper-50 text-xs flex items-start gap-3"
              >
                <div className="w-6 h-6 rounded-full bg-forest-800 text-paper-50 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                  {step.step_number}
                </div>
                <div className="flex-1">
                  <div className="font-bold text-forest-900 text-sm">
                    {isHindi ? step.title_hi : step.title_en}
                  </div>
                  <p className="text-muted-dark mt-1 leading-relaxed">
                    {isHindi ? step.description_hi : step.description_en}
                  </p>
                  <div className="mt-2 flex items-center gap-1.5 text-leaf-600 font-semibold text-[11px]">
                    <MapPin className="w-3.5 h-3.5" />
                    {step.portal_or_destination.startsWith('http') ? (
                      <span>
                        आधिकारिक पोर्टल:{' '}
                        <a
                          href={step.portal_or_destination}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="underline hover:text-forest-800 transition-colors"
                        >
                          {step.portal_or_destination}
                        </a>
                      </span>
                    ) : (
                      <span>आधिकारिक गंतव्य / पोर्टल: {step.portal_or_destination}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Statutory Disclaimer Footer */}
        <div className="p-4 rounded-subtle bg-paper-100 border border-appBorder text-xs text-muted leading-relaxed">
          <div className="font-bold text-ink-950 mb-1">
            वैधानिक घोषणा एवं अस्वीकरण (Statutory Notice):
          </div>
          <div>{planData.disclaimer}</div>
          <div className="mt-2 text-[11px] font-mono text-muted-dark">
            योजना साथी AI • उत्तर प्रदेश संस्करण 3.0 • साक्ष्य-आधारित किसान सहायता
          </div>
        </div>
      </div>
    </div>
  );
};
