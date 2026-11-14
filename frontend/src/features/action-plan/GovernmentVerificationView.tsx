import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  ShieldCheck, Clock, Landmark, CheckSquare, Square
} from 'lucide-react';
import { api } from '../../services/api';
import type { 
  SchemeEvaluation, 
  BenefitVerificationRecordOut 
} from '../../services/api';

interface GovernmentVerificationViewProps {
  planNumber: string;
  selectedSchemes: SchemeEvaluation[];
  governmentVerifications: BenefitVerificationRecordOut[];
  onWorkflowUpdate: () => void;
}

export const GovernmentVerificationView: React.FC<GovernmentVerificationViewProps> = ({
  planNumber,
  selectedSchemes,
  governmentVerifications,
  onWorkflowUpdate,
}) => {
  const { i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [togglingScheme, setTogglingScheme] = useState<string | null>(null);

  const verificationMap = new Map<string, BenefitVerificationRecordOut>();
  governmentVerifications.forEach(v => verificationMap.set(v.scheme_code, v));

  const handleToggleGovtVerification = async (code: string, isCurrentlyVerified: boolean) => {
    setTogglingScheme(code);
    try {
      await api.toggleGovtVerification(planNumber, code, !isCurrentlyVerified);
      onWorkflowUpdate();
    } catch (err) {
      console.error('Govt verify toggle error:', err);
    } finally {
      setTogglingScheme(null);
    }
  };

  const totalSchemes = selectedSchemes.length;
  const verifiedSchemesCount = selectedSchemes.filter(s => verificationMap.has(s.scheme_code)).length;

  return (
    <div className="space-y-6">
      {/* Distinction Explanatory Banner */}
      <div className="p-4 rounded-natural bg-paper-100 border border-appBorder text-xs text-muted-dark flex items-start gap-3">
        <Landmark className="w-5 h-5 text-forest-800 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-forest-900 text-sm">
            {isHindi ? 'चरण 7: आधिकारिक सरकारी सत्यापन एवं लाभ स्थिति (1-क्लिक संपुष्टि)' : 'Stage 7: Official Government Verification (1-Click Confirmation)'}
          </div>
          <p className="leading-relaxed">
            {isHindi
              ? 'विभागीय पोर्टल से स्वीकृति प्राप्त होने पर सीधे टिक-बॉक्स पर क्लिक करके सरकारी स्वीकृति दर्ज करें।'
              : 'Once departmental sanction is received, click the tick box to confirm government verification.'}
          </p>
        </div>
      </div>

      {/* Counter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-natural bg-field-100/70 border border-forest-800/30">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-forest-800">
            {isHindi ? 'चरण 7 सत्यापन स्थिति' : 'Stage 7 Verification'}
          </div>
          <div className="text-sm font-semibold text-forest-950 mt-0.5">
            {isHindi ? 'विभागीय स्वीकृति संपुष्टि' : 'Departmental Sanction Confirmation'}
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
          verifiedSchemesCount === totalSchemes && totalSchemes > 0
            ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
            : 'bg-amber-100 text-amber-900 border-amber-300'
        }`}>
          {verifiedSchemesCount} / {totalSchemes} {isHindi ? 'विभागीय स्वीकृत' : 'Sanctioned'}
        </span>
      </div>

      {/* Scheme-wise Government Verification Status */}
      <div className="space-y-4">
        {selectedSchemes.map(scheme => {
          const code = scheme.scheme_code;
          const verification = verificationMap.get(code);
          const isVerified = !!verification;
          const isToggling = togglingScheme === code;

          return (
            <div
              key={code}
              className={`p-4 rounded-natural border transition-all text-xs space-y-3 ${
                isVerified
                  ? 'bg-emerald-50/70 border-emerald-300 shadow-2xs'
                  : 'bg-white/90 border-appBorder'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="font-bold text-forest-900 text-sm">
                    {isHindi ? scheme.official_name_hi : scheme.official_name_en}
                  </div>
                  <div className="text-muted mt-0.5">
                    {scheme.department} • कोड: <span className="font-mono">{code}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {/* Status Badge */}
                  {isVerified ? (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-950 border border-emerald-300">
                      <ShieldCheck className="w-4 h-4 text-emerald-700" />
                      {isHindi ? 'विभागीय रूप से सत्यापित (VERIFIED)' : 'VERIFIED'}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-paper-200 text-muted-dark border border-appBorder">
                      <Clock className="w-3.5 h-3.5" />
                      {isHindi ? 'सत्यापन प्रतीक्षित' : 'PENDING'}
                    </span>
                  )}

                  {/* 1-Click Interactive Tick Box */}
                  <button
                    type="button"
                    disabled={isToggling}
                    onClick={() => handleToggleGovtVerification(code, isVerified)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-natural border font-semibold text-xs transition-all shadow-2xs ${
                      isVerified
                        ? 'bg-emerald-100 text-emerald-950 border-emerald-400 hover:bg-emerald-200/80'
                        : 'bg-white text-ink-950 border-appBorder hover:border-forest-700 hover:bg-field-50'
                    }`}
                  >
                    {isVerified ? (
                      <CheckSquare className="w-4 h-4 text-emerald-700 shrink-0" />
                    ) : (
                      <Square className="w-4 h-4 text-muted hover:text-forest-800 shrink-0" />
                    )}
                    <span>
                      {isVerified 
                        ? (isHindi ? 'विभागीय स्वीकृति संपुष्ट ✓' : 'Sanction Confirmed ✓') 
                        : (isHindi ? 'स्वीकृति संपुष्ट करें' : 'Confirm Sanction')}
                    </span>
                  </button>
                </div>
              </div>

              {/* Status Details if verified */}
              {isVerified && (
                <div className="bg-white/80 p-3 rounded-natural border border-emerald-200 space-y-1 font-mono text-[11px] text-forest-950">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-sans font-semibold text-forest-800">स्रोत:</span>{' '}
                      {verification.verification_source}
                    </div>
                    <div>
                      <span className="font-sans font-semibold text-forest-800">आदेश संख्या:</span>{' '}
                      <span className="font-bold text-forest-900">{verification.official_reference_number}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
