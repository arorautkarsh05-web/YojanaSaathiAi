import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { UserCheck, CheckSquare, Square, CheckCircle2, Clock } from 'lucide-react';
import { api } from '../../services/api';
import type { 
  SchemeEvaluation, 
  FarmerApplicationProgressOut 
} from '../../services/api';

interface FarmerApplicationProgressViewProps {
  planNumber: string;
  selectedSchemes: SchemeEvaluation[];
  applicationProgress: FarmerApplicationProgressOut[];
  onWorkflowUpdate: () => void;
}

export const FarmerApplicationProgressView: React.FC<FarmerApplicationProgressViewProps> = ({
  planNumber,
  selectedSchemes,
  applicationProgress,
  onWorkflowUpdate,
}) => {
  const { i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [savingScheme, setSavingScheme] = useState<string | null>(null);

  const progressMap = new Map<string, FarmerApplicationProgressOut>();
  applicationProgress.forEach(p => progressMap.set(p.scheme_code, p));

  const handleToggleSchemeProgress = async (code: string, isCurrentlySubmitted: boolean) => {
    setSavingScheme(code);
    try {
      const nextStatus = isCurrentlySubmitted ? 'NOT_YET_APPLIED' : 'APPLICATION_SUBMITTED';
      const appRef = isCurrentlySubmitted ? '' : `UP-APP-${code.slice(0, 4)}-${Date.now().toString().slice(-4)}`;
      const remarks = isCurrentlySubmitted ? '' : 'किसान द्वारा आवेदन पूर्ण एवं जमा संपुष्ट';

      await api.updateSchemeProgress(
        planNumber,
        code,
        nextStatus,
        appRef,
        remarks
      );
      onWorkflowUpdate();
    } catch (err) {
      console.error('Update progress error:', err);
    } finally {
      setSavingScheme(null);
    }
  };

  const totalSchemes = selectedSchemes.length;
  const submittedSchemes = selectedSchemes.filter(s => {
    const prog = progressMap.get(s.scheme_code);
    return prog && prog.status !== 'NOT_YET_APPLIED';
  }).length;

  return (
    <div className="space-y-6">
      {/* Notice */}
      <div className="p-4 rounded-natural bg-paper-100 border border-appBorder text-xs text-muted-dark flex items-start gap-3">
        <UserCheck className="w-5 h-5 text-forest-700 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-forest-900 text-sm">
            {isHindi ? 'चरण 6: किसान द्वारा दर्ज आवेदन प्रगति (1-क्लिक पुष्टि)' : 'Stage 6: Farmer-Reported Progress (1-Click Confirmation)'}
          </div>
          <p className="leading-relaxed">
            {isHindi
              ? 'जैसे ही आप संबंधित सरकारी पोर्टल पर आवेदन कर लें, नीचे दिए गए टिक-बॉक्स पर क्लिक करके अपनी आवेदन स्थिति संपुष्ट करें।'
              : 'Once you have applied on the respective government portal, tick the checkbox to confirm your application status.'}
          </p>
        </div>
      </div>

      {/* Counter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-natural bg-field-100/70 border border-forest-800/30">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-forest-800">
            {isHindi ? 'चरण 6 प्रगति स्थिति' : 'Stage 6 Progress'}
          </div>
          <div className="text-sm font-semibold text-forest-950 mt-0.5">
            {isHindi ? 'योजना आवेदन संपुष्टि' : 'Scheme Application Confirmation'}
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
          submittedSchemes === totalSchemes && totalSchemes > 0
            ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
            : 'bg-amber-100 text-amber-900 border-amber-300'
        }`}>
          {submittedSchemes} / {totalSchemes} {isHindi ? 'आवेदन दर्ज' : 'Applied'}
        </span>
      </div>

      {/* Scheme Progress Cards */}
      <div className="space-y-4">
        {selectedSchemes.map(scheme => {
          const code = scheme.scheme_code;
          const currentProgress = progressMap.get(code);
          const isSubmitted = !!currentProgress && currentProgress.status !== 'NOT_YET_APPLIED';
          const isSaving = savingScheme === code;

          return (
            <div
              key={code}
              className={`p-4 rounded-natural border transition-all text-xs space-y-3 ${
                isSubmitted
                  ? 'bg-emerald-50/60 border-emerald-300 shadow-2xs'
                  : 'bg-white/90 border-appBorder'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-forest-900 bg-paper-200 px-2 py-0.5 rounded text-[11px]">
                      {code}
                    </span>
                    <span className="font-bold text-forest-950 text-sm">
                      {isHindi ? scheme.official_name_hi : scheme.official_name_en}
                    </span>
                  </div>
                  <div className="text-[11px] text-muted mt-0.5">
                    {scheme.department} • {scheme.level === 'CENTRAL' ? 'केंद्रीय' : 'राज्य (उ.प्र.)'}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {/* Status Badge */}
                  {isSubmitted ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                      {isHindi ? 'आवेदन जमा (Submitted)' : 'SUBMITTED'}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-paper-200 text-muted-dark border border-appBorder">
                      <Clock className="w-3.5 h-3.5" />
                      {isHindi ? 'आवेदन अभी नहीं किया' : 'NOT APPLIED'}
                    </span>
                  )}

                  {/* 1-Click Interactive Tick Box */}
                  <button
                    type="button"
                    disabled={isSaving}
                    onClick={() => handleToggleSchemeProgress(code, isSubmitted)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-natural border font-semibold text-xs transition-all shadow-2xs ${
                      isSubmitted
                        ? 'bg-emerald-100 text-emerald-950 border-emerald-400 hover:bg-emerald-200/80'
                        : 'bg-white text-ink-950 border-appBorder hover:border-forest-700 hover:bg-field-50'
                    }`}
                  >
                    {isSubmitted ? (
                      <CheckSquare className="w-4 h-4 text-emerald-700 shrink-0" />
                    ) : (
                      <Square className="w-4 h-4 text-muted hover:text-forest-800 shrink-0" />
                    )}
                    <span>
                      {isSubmitted 
                        ? (isHindi ? 'आवेदन जमा संपुष्ट ✓' : 'Application Confirmed ✓') 
                        : (isHindi ? 'आवेदन जमा चिह्नित करें' : 'Mark as Applied')}
                    </span>
                  </button>
                </div>
              </div>

              {/* Reference Details if submitted */}
              {isSubmitted && currentProgress?.application_reference_number && (
                <div className="p-2 rounded bg-white/80 border border-emerald-200 text-[11px] font-mono text-emerald-900 flex items-center justify-between">
                  <span>पावती संदर्भ: {currentProgress.application_reference_number}</span>
                  {currentProgress.updated_at && (
                    <span className="text-[10px] text-muted font-sans">
                      दिनांक: {new Date(currentProgress.updated_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
