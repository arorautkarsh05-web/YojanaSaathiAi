import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Printer, ArrowLeft, Compass, ShieldAlert, WifiOff,
  Download, FileCheck, Layers, ClipboardCheck, Building2, UserCheck, CheckCircle2
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { api } from '../../services/api';
import type { 
  ActionPlanData, 
  ActionPlanWorkflowSummaryResponse,
  ActionPlanConfirmationResponse 
} from '../../services/api';
import { DocumentVerificationCenter } from './DocumentVerificationCenter';
import { InteractiveOfficialSteps } from './InteractiveOfficialSteps';
import { FarmerApplicationProgressView } from './FarmerApplicationProgressView';
import { GovernmentVerificationView } from './GovernmentVerificationView';
import { FinalConfirmationModal } from './FinalConfirmationModal';

interface ActionPlanViewProps {
  planData: ActionPlanData;
  onBack: () => void;
}

type ActiveTab = 'overview' | 'docs' | 'steps' | 'farmer_progress' | 'govt_verification';

export const ActionPlanView: React.FC<ActionPlanViewProps> = ({ planData, onBack }) => {
  const { t, i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [activeTab, setActiveTab] = useState<ActiveTab>('docs');
  const [workflow, setWorkflow] = useState<ActionPlanWorkflowSummaryResponse | null>(null);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [isConfirmationModalOpen, setIsConfirmationModalOpen] = useState(false);

  const fetchWorkflow = async () => {
    try {
      const summary = await api.getWorkflowSummary(planData.plan_number);
      setWorkflow(summary);
    } catch (err) {
      console.warn('Could not fetch workflow summary, fallback to local state', err);
    }
  };

  useEffect(() => {
    // Offline caching resilience
    try {
      localStorage.setItem(`yojanasaathi_plan_${planData.plan_number}`, JSON.stringify(planData));
      localStorage.setItem('yojanasaathi_latest_plan_number', planData.plan_number);
    } catch {
      // ignore quota error
    }

    const handleOnline = () => { setIsOffline(false); fetchWorkflow(); };
    const handleOffline = () => setIsOffline(true);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    fetchWorkflow();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [planData.plan_number]);

  const handlePrint = () => {
    window.print();
  };

  const handleConfirmationSuccess = (_conf: ActionPlanConfirmationResponse) => {
    fetchWorkflow();
  };

  // Derive stage counters
  const requiredDocs = workflow?.required_documents || [];
  const uploadedDocs = workflow?.uploaded_documents || [];
  const actionSteps = workflow?.action_steps || [];
  const applicationProgress = workflow?.application_progress || [];
  const govtVerifications = workflow?.government_verifications || [];
  const confirmation = workflow?.confirmation;

  const totalMandatoryDocs = requiredDocs.filter(d => d.is_mandatory).length;
  const verifiedMandatoryDocs = requiredDocs.filter(
    d => d.is_mandatory && uploadedDocs.some(u => u.doc_id_key === d.doc_id_key && u.verification_status === 'VERIFIED')
  ).length;

  const completedStepsCount = actionSteps.filter(s => s.is_completed).length;
  const isStage4Complete = verifiedMandatoryDocs === totalMandatoryDocs && totalMandatoryDocs > 0;
  const isStage5Complete = completedStepsCount > 0 && completedStepsCount >= actionSteps.length;
  const isStage7Complete = govtVerifications.length > 0;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 print:p-0">
      {/* Top action bar (hidden in print) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 no-print">
        <Button variant="secondary" size="sm" leftIcon={<ArrowLeft className="w-4 h-4" />} onClick={onBack}>
          {isHindi ? 'वापस परिणामों पर जाएँ' : 'Back to Results'}
        </Button>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Confirmation Button */}
          <Button
            variant="primary"
            size="sm"
            leftIcon={<FileCheck className="w-4 h-4" />}
            onClick={() => setIsConfirmationModalOpen(true)}
            className="bg-emerald-800 hover:bg-emerald-900 border-emerald-950 text-white"
          >
            {confirmation
              ? (isHindi ? 'संक्षिप्त लाभ संक्षेप (देखें)' : 'View Benefit Summary')
              : (isHindi ? 'कार्य योजना संपुष्ट करें' : 'Confirm Action Plan')}
          </Button>

          {/* 1-Page PDF Summary Download */}
          <a
            href={api.getSummaryPdfUrl(planData.plan_number)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-natural bg-forest-800 hover:bg-forest-900 text-paper-50 text-xs font-semibold transition-colors shadow-2xs"
            title={isHindi ? '1-पेज किसान लाभ संक्षेप (PDF) डाउनलोड करें' : 'Download 1-Page Summary PDF'}
          >
            <Download className="w-4 h-4" />
            <span>{isHindi ? 'लाभ संक्षेप (PDF)' : 'Summary PDF'}</span>
          </a>

          {/* Print Button */}
          <Button variant="secondary" size="sm" leftIcon={<Printer className="w-4 h-4" />} onClick={handlePrint}>
            {isHindi ? 'प्रिंट करें' : 'Print'}
          </Button>
        </div>
      </div>

      {isOffline && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-natural flex items-center gap-2 text-xs text-amber-900 no-print">
          <WifiOff className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{isHindi ? 'ऑफ़लाइन मोड सक्रिय: यह कार्य योजना स्थानीय रूप से सुरक्षित है और बिना इंटरनेट के उपलब्ध रहेगी।' : 'Offline Mode Active: This action plan is cached locally and available without internet.'}</span>
        </div>
      )}

      {/* Main Container */}
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
              {confirmation 
                ? (isHindi ? 'योजना संपुष्ट ✓' : 'Plan Confirmed ✓')
                : (isHindi ? 'चरण 4-5 सक्रिय' : 'Stages 4-5 Active')}
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
            <button
              type="button"
              onClick={() => setActiveTab('docs')}
              className={`p-2 rounded border font-medium transition-all text-left ${
                isStage4Complete
                  ? 'bg-emerald-100/80 border-emerald-300 text-emerald-950'
                  : activeTab === 'docs'
                  ? 'bg-field-100 border-forest-800 text-forest-950 ring-2 ring-forest-700/30'
                  : 'bg-white border-appBorder text-ink-950'
              }`}
            >
              <div className="text-xs font-bold text-forest-900 mb-0.5">
                4. दस्तावेज़ {isStage4Complete ? '✓' : `(${verifiedMandatoryDocs}/${totalMandatoryDocs})`}
              </div>
              <div>{isHindi ? (isStage4Complete ? 'सत्यापन पूर्ण' : 'सत्यापन केंद्र') : 'Verification'}</div>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('steps')}
              className={`p-2 rounded border font-medium transition-all text-left ${
                isStage5Complete
                  ? 'bg-emerald-100/80 border-emerald-300 text-emerald-950'
                  : activeTab === 'steps'
                  ? 'bg-field-100 border-forest-800 text-forest-950 ring-2 ring-forest-700/30'
                  : 'bg-white border-appBorder text-ink-950'
              }`}
            >
              <div className="text-xs font-bold text-forest-900 mb-0.5">
                5. आधिकारिक कदम {isStage5Complete ? '✓' : `(${completedStepsCount}/${actionSteps.length})`}
              </div>
              <div>{isHindi ? 'पोर्टल निर्देश' : 'Official Portal'}</div>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('farmer_progress')}
              className={`p-2 rounded border font-medium transition-all text-left ${
                activeTab === 'farmer_progress'
                  ? 'bg-field-100 border-forest-800 text-forest-950 ring-2 ring-forest-700/30'
                  : 'bg-white border-appBorder text-ink-950'
              }`}
            >
              <div className="text-xs font-bold text-forest-900 mb-0.5">6. किसान प्रगति</div>
              <div>{isHindi ? 'स्वयं दर्ज स्थिति' : 'Farmer Reported'}</div>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('govt_verification')}
              className={`p-2 rounded border font-medium transition-all text-left ${
                isStage7Complete
                  ? 'bg-emerald-100/80 border-emerald-300 text-emerald-950'
                  : activeTab === 'govt_verification'
                  ? 'bg-field-100 border-forest-800 text-forest-950 ring-2 ring-forest-700/30'
                  : 'bg-white border-appBorder text-ink-950'
              }`}
            >
              <div className="text-xs font-bold text-forest-900 mb-0.5">
                7. लाभ संपुष्टि {isStage7Complete ? '✓' : ''}
              </div>
              <div>{isHindi ? (isStage7Complete ? 'विभागीय स्वीकृत' : 'सत्यापन प्रतीक्षित') : 'Govt Sanction'}</div>
            </button>
          </div>

          <div className="mt-3 pt-2 border-t border-appBorder/80 flex items-start gap-1.5 text-[10px] text-muted-dark">
            <ShieldAlert className="w-3.5 h-3.5 text-forest-700 shrink-0 mt-0.5" />
            <span>
              {isHindi
                ? 'पारदर्शिता सूचना: चरण 1-5 योजना साथी द्वारा गजट नियमों से संचालित हैं। चरण 6 किसान द्वारा स्वयं दर्ज की जाने वाली प्रगति है। चरण 7 में आधिकारिक स्वीकृति केवल सक्षम सरकारी विभाग द्वारा प्रदान की जाती है।'
                : 'Transparency Notice: Stages 1-5 are guided by YojanaSaathi based on gazetted rules. Stage 6 represents farmer self-reported status. Stage 7 sanction is granted solely by the respective government authority.'}
            </span>
          </div>
        </div>

        {/* Interactive Workflow Navigation Tabs (Hidden in print) */}
        <div className="flex items-center gap-2 mb-6 border-b border-appBorder overflow-x-auto pb-2 no-print text-xs font-semibold">
          <button
            type="button"
            onClick={() => setActiveTab('docs')}
            className={`px-3.5 py-2 rounded-natural transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === 'docs'
                ? 'bg-forest-800 text-paper-50 shadow-2xs font-bold'
                : 'bg-paper-100 text-ink-950 hover:bg-paper-200'
            }`}
          >
            <ClipboardCheck className="w-4 h-4" />
            <span>4. दस्तावेज़ सत्यापन केंद्र ({verifiedMandatoryDocs}/{totalMandatoryDocs})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('steps')}
            className={`px-3.5 py-2 rounded-natural transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === 'steps'
                ? 'bg-forest-800 text-paper-50 shadow-2xs font-bold'
                : 'bg-paper-100 text-ink-950 hover:bg-paper-200'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>5. आधिकारिक आवेदन कदम ({completedStepsCount}/{actionSteps.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('farmer_progress')}
            className={`px-3.5 py-2 rounded-natural transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === 'farmer_progress'
                ? 'bg-forest-800 text-paper-50 shadow-2xs font-bold'
                : 'bg-paper-100 text-ink-950 hover:bg-paper-200'
            }`}
          >
            <UserCheck className="w-4 h-4" />
            <span>6. किसान प्रगति ट्रैकर</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('govt_verification')}
            className={`px-3.5 py-2 rounded-natural transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === 'govt_verification'
                ? 'bg-forest-800 text-paper-50 shadow-2xs font-bold'
                : 'bg-paper-100 text-ink-950 hover:bg-paper-200'
            }`}
          >
            <Building2 className="w-4 h-4" />
            <span>7. सरकारी सत्यापन स्थिति</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('overview')}
            className={`px-3.5 py-2 rounded-natural transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeTab === 'overview'
                ? 'bg-forest-800 text-paper-50 shadow-2xs font-bold'
                : 'bg-paper-100 text-ink-950 hover:bg-paper-200'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>कार्य योजना अवलोकन (Overview)</span>
          </button>
        </div>

        {/* Tab 1: Stage 4 — Document Upload & Verification Centre */}
        {(activeTab === 'docs' || window.matchMedia('print').matches) && (
          <div className="mb-8">
            <DocumentVerificationCenter
              planNumber={planData.plan_number}
              requiredDocs={requiredDocs}
              uploadedDocs={uploadedDocs}
              onWorkflowUpdate={fetchWorkflow}
            />
          </div>
        )}

        {/* Tab 2: Stage 5 — Verified Official Next Steps */}
        {(activeTab === 'steps' || window.matchMedia('print').matches) && (
          <div className="mb-8">
            <InteractiveOfficialSteps
              planNumber={planData.plan_number}
              officialSteps={planData.official_steps}
              stepCompletions={actionSteps}
              onWorkflowUpdate={fetchWorkflow}
            />
          </div>
        )}

        {/* Tab 3: Stage 6 — Farmer-Reported Progress Tracking */}
        {activeTab === 'farmer_progress' && (
          <div className="mb-8">
            <FarmerApplicationProgressView
              planNumber={planData.plan_number}
              selectedSchemes={planData.selected_schemes}
              applicationProgress={applicationProgress}
              onWorkflowUpdate={fetchWorkflow}
            />
          </div>
        )}

        {/* Tab 4: Stage 7 — Government Verification & Sanction */}
        {activeTab === 'govt_verification' && (
          <div className="mb-8">
            <GovernmentVerificationView
              planNumber={planData.plan_number}
              selectedSchemes={planData.selected_schemes}
              governmentVerifications={govtVerifications}
              onWorkflowUpdate={fetchWorkflow}
            />
          </div>
        )}

        {/* Tab 5: Complete Action Plan Overview */}
        {(activeTab === 'overview' || window.matchMedia('print').matches) && (
          <div className="space-y-8">
            {/* Selected Schemes & Eligibility */}
            <div>
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

            {/* Pairwise Convergence */}
            {planData.convergence_summary.length > 0 && (
              <div>
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
          </div>
        )}

        {/* Bottom Confirmation Banner */}
        <div className="mt-8 p-5 rounded-natural bg-field-100 border border-forest-800/40 flex flex-col sm:flex-row sm:items-center justify-between gap-4 no-print">
          <div>
            <div className="font-bold text-forest-950 text-sm">
              {confirmation 
                ? (isHindi ? 'कार्य योजना संपुष्ट संदर्भ: ' + confirmation.summary_ref_id : 'Confirmed Ref: ' + confirmation.summary_ref_id)
                : (isHindi ? 'कार्य योजना की अंतिम संपुष्टि' : 'Final Action Plan Confirmation')}
            </div>
            <p className="text-xs text-muted-dark mt-0.5">
              {isHindi
                ? 'सभी अनिवार्य दस्तावेज़ सत्यापित होने पर अपनी योजना संपुष्ट करें और 1-पेज लाभ संक्षेप प्राप्त करें।'
                : 'Confirm roadmap once all mandatory documents are verified and download the 1-page summary.'}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Button
              variant="primary"
              size="sm"
              leftIcon={<FileCheck className="w-4 h-4" />}
              onClick={() => setIsConfirmationModalOpen(true)}
            >
              {confirmation
                ? (isHindi ? 'विवरण देखें' : 'View Confirmation')
                : (isHindi ? 'कार्य योजना संपुष्ट करें' : 'Confirm Action Plan')}
            </Button>
          </div>
        </div>

        {/* Statutory Disclaimer Footer */}
        <div className="mt-6 p-4 rounded-subtle bg-paper-100 border border-appBorder text-xs text-muted leading-relaxed">
          <div className="font-bold text-ink-950 mb-1">
            वैधानिक घोषणा एवं अस्वीकरण (Statutory Notice):
          </div>
          <div>{planData.disclaimer}</div>
          <div className="mt-2 text-[11px] font-mono text-muted-dark">
            योजना साथी AI • उत्तर प्रदेश संस्करण 3.0 • साक्ष्य-आधारित किसान सहायता
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {isConfirmationModalOpen && (
        <FinalConfirmationModal
          planNumber={planData.plan_number}
          canConfirm={workflow?.can_confirm ?? false}
          unmetPrerequisites={workflow?.unmet_prerequisites ?? []}
          existingConfirmation={confirmation}
          onClose={() => setIsConfirmationModalOpen(false)}
          onSuccess={handleConfirmationSuccess}
        />
      )}
    </div>
  );
};
