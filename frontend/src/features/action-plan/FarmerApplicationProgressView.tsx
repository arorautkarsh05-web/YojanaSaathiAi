import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { UserCheck } from 'lucide-react';
import { Button } from '../../components/ui/Button';
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

const STATUS_OPTIONS = [
  { value: 'NOT_YET_APPLIED', label_hi: 'आवेदन अभी नहीं किया (Not Yet Applied)', label_en: 'Not Yet Applied' },
  { value: 'APPLICATION_SUBMITTED', label_hi: 'आवेदन जमा किया गया (Application Submitted)', label_en: 'Application Submitted' },
  { value: 'ACKNOWLEDGEMENT_RECEIVED', label_hi: 'पावती / रसीद प्राप्त हुई (Acknowledgement Received)', label_en: 'Acknowledgement Received' },
  { value: 'UNDER_REVIEW', label_hi: 'विभागीय समीक्षाधीन (Under Review)', label_en: 'Under Review' },
  { value: 'ADDITIONAL_INFO_REQUESTED', label_hi: 'अतिरिक्त जानकारी मांगी गई (Additional Info Requested)', label_en: 'Additional Info Requested' },
  { value: 'APPLICATION_REJECTED', label_hi: 'आवेदन निरस्त / आपत्ति (Application Rejected)', label_en: 'Application Rejected' },
  { value: 'BENEFIT_RECEIVED', label_hi: 'लाभ / डीबीटी प्राप्त हुआ (Benefit Received)', label_en: 'Benefit Received' },
];

export const FarmerApplicationProgressView: React.FC<FarmerApplicationProgressViewProps> = ({
  planNumber,
  selectedSchemes,
  applicationProgress,
  onWorkflowUpdate,
}) => {
  const { i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [savingScheme, setSavingScheme] = useState<string | null>(null);
  const [formData, setFormData] = useState<Record<string, { status: string; appRef: string; remarks: string }>>({});

  const progressMap = new Map<string, FarmerApplicationProgressOut>();
  applicationProgress.forEach(p => progressMap.set(p.scheme_code, p));

  const getFormState = (code: string) => {
    if (formData[code]) return formData[code];
    const existing = progressMap.get(code);
    return {
      status: existing?.status || 'NOT_YET_APPLIED',
      appRef: existing?.application_reference_number || '',
      remarks: existing?.farmer_remarks || '',
    };
  };

  const handleUpdate = async (code: string) => {
    const state = getFormState(code);
    setSavingScheme(code);
    try {
      await api.updateSchemeProgress(
        planNumber,
        code,
        state.status,
        state.appRef,
        state.remarks
      );
      onWorkflowUpdate();
    } catch (err) {
      console.error('Update progress error:', err);
    } finally {
      setSavingScheme(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Notice */}
      <div className="p-4 rounded-natural bg-paper-100 border border-appBorder text-xs text-muted-dark flex items-start gap-3">
        <UserCheck className="w-5 h-5 text-forest-700 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-forest-900 text-sm">
            {isHindi ? 'चरण 6: किसान द्वारा दर्ज आवेदन प्रगति (Farmer-Reported Progress)' : 'Stage 6: Farmer-Reported Application Progress'}
          </div>
          <p className="leading-relaxed">
            {isHindi
              ? 'यह अनुभाग किसान को सरकारी पोर्टल पर किए गए अपने आवेदनों की वर्तमान स्थिति दर्ज करने की सुविधा देता है। यह स्थिति पूर्णतः किसान द्वारा स्वयं घोषित (Self-Reported) है और सरकारी डाटाबेस द्वारा स्वचालित रूप से सत्यापित नहीं मानी जाती।'
              : 'This section allows farmers to record their real application progress made across official portals. All statuses here are self-reported by the farmer and distinguished from official government verification.'}
          </p>
        </div>
      </div>

      {/* Scheme Progress Cards */}
      <div className="space-y-4">
        {selectedSchemes.map(scheme => {
          const code = scheme.scheme_code;
          const currentProgress = progressMap.get(code);
          const formState = getFormState(code);
          const isSaving = savingScheme === code;

          return (
            <div
              key={code}
              className="p-5 rounded-natural border border-appBorder bg-white/90 shadow-2xs space-y-4 text-xs"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-appBorder pb-3">
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

                <div className="flex items-center gap-1.5 self-start sm:self-auto">
                  <span className="text-[10px] font-bold px-2 py-1 rounded bg-amber-50 text-amber-900 border border-amber-200">
                    {isHindi ? 'स्वयं दर्ज स्थिति (Self-Reported)' : 'Self-Reported'}
                  </span>
                </div>
              </div>

              {/* Progress Inputs */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-ink-950 block text-[11px]">
                    {isHindi ? 'वर्तमान आवेदन स्थिति:' : 'Application Status:'}
                  </label>
                  <select
                    value={formState.status}
                    onChange={e => setFormData({
                      ...formData,
                      [code]: { ...formState, status: e.target.value }
                    })}
                    className="w-full text-xs p-2 rounded border border-appBorder bg-paper-50 text-ink-950"
                  >
                    {STATUS_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>
                        {isHindi ? opt.label_hi : opt.label_en}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-ink-950 block text-[11px]">
                    {isHindi ? 'आवेदन / पावती संदर्भ संख्या:' : 'Application / Ack Ref #:'}
                  </label>
                  <input
                    type="text"
                    value={formState.appRef}
                    onChange={e => setFormData({
                      ...formData,
                      [code]: { ...formState, appRef: e.target.value }
                    })}
                    placeholder={isHindi ? 'उदा. UP-AGRI-2026-XXXX' : 'e.g. UP-AGRI-2026-XXXX'}
                    className="w-full text-xs p-2 rounded border border-appBorder bg-white font-mono text-ink-950"
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-ink-950 block text-[11px]">
                    {isHindi ? 'टिप्पणी / स्थिति विवरण:' : 'Remarks / Note:'}
                  </label>
                  <input
                    type="text"
                    value={formState.remarks}
                    onChange={e => setFormData({
                      ...formData,
                      [code]: { ...formState, remarks: e.target.value }
                    })}
                    placeholder={isHindi ? 'उदा. तहसील में लेखपाल सत्यापन पूर्ण' : 'e.g. Lekhpal verified at Tehsil'}
                    className="w-full text-xs p-2 rounded border border-appBorder bg-white text-ink-950"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <div className="text-[10px] text-muted font-mono">
                  {currentProgress?.updated_at && (
                    <span>अंतिम अद्यतन: {new Date(currentProgress.updated_at).toLocaleDateString()}</span>
                  )}
                </div>
                <Button
                  variant="primary"
                  size="sm"
                  isLoading={isSaving}
                  onClick={() => handleUpdate(code)}
                >
                  {isHindi ? 'प्रगति सहेजें' : 'Save Progress'}
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
