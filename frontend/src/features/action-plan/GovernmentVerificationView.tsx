import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Building2, ShieldCheck, Clock, Landmark
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
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

  const [modalSchemeCode, setModalSchemeCode] = useState<string | null>(null);
  const [source, setSource] = useState('UP Agriculture DBT Portal Direct Verification');
  const [refNumber, setRefNumber] = useState('');
  const [remarks, setRemarks] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const verificationMap = new Map<string, BenefitVerificationRecordOut>();
  governmentVerifications.forEach(v => verificationMap.set(v.scheme_code, v));

  const handleRecordGovtVerification = async () => {
    if (!modalSchemeCode || !refNumber) return;
    setIsSubmitting(true);
    try {
      await api.recordGovtVerification(
        planNumber,
        modalSchemeCode,
        source,
        refNumber,
        'GOVERNMENT_VERIFIED',
        remarks || 'आधिकारिक स्वीकृति आदेश सत्यापित'
      );
      setModalSchemeCode(null);
      setRefNumber('');
      setRemarks('');
      onWorkflowUpdate();
    } catch (err) {
      console.error('Govt verify error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Distinction Explanatory Banner */}
      <div className="p-4 rounded-natural bg-paper-100 border border-appBorder text-xs text-muted-dark flex items-start gap-3">
        <Landmark className="w-5 h-5 text-forest-800 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-forest-900 text-sm">
            {isHindi ? 'चरण 7: आधिकारिक सरकारी सत्यापन एवं लाभ स्थिति' : 'Stage 7: Official Government Verification & Benefit Sanction'}
          </div>
          <p className="leading-relaxed">
            {isHindi
              ? 'पारदर्शिता का कड़ा नियम: योजना साथी AI किसान के चेकबॉक्स या प्रारंभिक पात्रता को कभी भी "सरकारी स्वीकृति" का दर्जा नहीं देता। सरकारी सत्यापन केवल तभी दर्ज होता है जब सक्षम प्राधिकारी (जैसे जिला कृषि अधिकारी, उप-कृषि निदेशक या डीबीटी पोर्टल) द्वारा प्रामाणिक स्वीकृति संदर्भ संख्या जारी की गई हो।'
              : 'Strict transparency guarantee: YojanaSaathi AI never treats self-reported farmer actions or algorithmic eligibility as official government approval. Genuine departmental verification requires authoritative sanction reference orders.'}
          </p>
        </div>
      </div>

      {/* Scheme-wise Government Verification Status */}
      <div className="space-y-4">
        {selectedSchemes.map(scheme => {
          const code = scheme.scheme_code;
          const verification = verificationMap.get(code);
          const isVerified = !!verification;

          return (
            <div
              key={code}
              className={`p-5 rounded-natural border transition-all text-xs space-y-3 ${
                isVerified
                  ? 'bg-emerald-50/70 border-emerald-300'
                  : 'bg-white/90 border-appBorder'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-appBorder/80 pb-3">
                <div>
                  <div className="font-bold text-forest-900 text-sm">
                    {isHindi ? scheme.official_name_hi : scheme.official_name_en}
                  </div>
                  <div className="text-muted mt-0.5">
                    {scheme.department} • कोड: <span className="font-mono">{code}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {isVerified ? (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-950 border border-emerald-300">
                      <ShieldCheck className="w-4 h-4 text-emerald-700" />
                      {isHindi ? 'विभागीय रूप से सत्यापित (GOVERNMENT VERIFIED)' : 'GOVERNMENT VERIFIED'}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-paper-200 text-muted-dark border border-appBorder">
                      <Clock className="w-3.5 h-3.5" />
                      {isHindi ? 'विभागीय सत्यापन प्रतीक्षित (Pending Sanction)' : 'Pending Verification'}
                    </span>
                  )}
                </div>
              </div>

              {/* Status Details */}
              {isVerified ? (
                <div className="bg-white/80 p-3.5 rounded-natural border border-emerald-200 space-y-1.5 font-mono text-[11px] text-forest-950">
                  <div>
                    <span className="font-sans font-semibold text-forest-800">सत्यापन स्रोत (Source):</span>{' '}
                    {verification.verification_source}
                  </div>
                  <div>
                    <span className="font-sans font-semibold text-forest-800">आधिकारिक स्वीकृति आदेश संख्या:</span>{' '}
                    <span className="font-bold text-forest-900">{verification.official_reference_number}</span>
                  </div>
                  {verification.remarks && (
                    <div className="font-sans text-muted-dark">
                      <span className="font-semibold text-forest-800">विभागीय टिप्पणी:</span> {verification.remarks}
                    </div>
                  )}
                  <div className="text-[10px] text-muted">
                    सत्यापन तिथि: {new Date(verification.verified_at).toLocaleDateString()}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-muted-dark text-[11px]">
                  <p>
                    {isHindi
                      ? 'संबंधित विभाग में आवेदन प्रक्रियाधीन है। अंतिम स्वीकृति आदेश प्राप्त होने पर आधिकारिक सत्यापन दर्ज करें।'
                      : 'Application in progress at department. Record verification order once issued.'}
                  </p>
                  <Button
                    variant="secondary"
                    size="sm"
                    className="shrink-0 text-leaf-700 border-leaf-300 hover:bg-leaf-50 text-xs"
                    onClick={() => {
                      setModalSchemeCode(code);
                      setRefNumber('');
                      setRemarks('');
                    }}
                  >
                    {isHindi ? '+ विभागीय स्वीकृति दर्ज करें' : '+ Record Sanction Order'}
                  </Button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Verification Entry Modal */}
      {modalSchemeCode && (
        <div className="fixed inset-0 z-50 bg-ink-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-natural max-w-lg w-full p-6 shadow-xl border border-appBorder space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="font-bold text-forest-900 text-sm flex items-center gap-2">
                <Building2 className="w-4 h-4 text-forest-700" />
                <span>{isHindi ? 'विभागीय स्वीकृति आदेश दर्ज करें' : 'Record Departmental Sanction'}</span>
              </h3>
              <button onClick={() => setModalSchemeCode(null)} className="text-muted hover:text-ink-950">
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-ink-950 block mb-1">
                  {isHindi ? 'योजना कोड:' : 'Scheme Code:'}
                </label>
                <div className="p-2 rounded bg-paper-100 font-mono font-bold text-forest-900">
                  {modalSchemeCode}
                </div>
              </div>

              <div>
                <label className="font-semibold text-ink-950 block mb-1">
                  {isHindi ? 'सत्यापन स्रोत (Authority / Portal):' : 'Verification Source:'}
                </label>
                <input
                  type="text"
                  value={source}
                  onChange={e => setSource(e.target.value)}
                  className="w-full p-2 rounded border border-appBorder bg-white"
                />
              </div>

              <div>
                <label className="font-semibold text-ink-950 block mb-1">
                  {isHindi ? 'आधिकारिक स्वीकृति / आदेश संदर्भ संख्या *:' : 'Official Reference / Sanction Order # *:'}
                </label>
                <input
                  type="text"
                  value={refNumber}
                  onChange={e => setRefNumber(e.target.value)}
                  placeholder={isHindi ? 'उदा. UP-AGRI-SANCTION-2026-9182' : 'e.g. UP-AGRI-SANCTION-2026-9182'}
                  className="w-full p-2 rounded border border-appBorder bg-white font-mono"
                  required
                />
              </div>

              <div>
                <label className="font-semibold text-ink-950 block mb-1">
                  {isHindi ? 'विभागीय टिप्पणी (वैकल्पिक):' : 'Remarks (Optional):'}
                </label>
                <input
                  type="text"
                  value={remarks}
                  onChange={e => setRemarks(e.target.value)}
                  placeholder={isHindi ? 'तहसीलदार / उप कृषि निदेशक द्वारा संस्तुत' : 'Sanctioned by DAO'}
                  className="w-full p-2 rounded border border-appBorder bg-white"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-4 border-t">
              <Button variant="secondary" size="sm" onClick={() => setModalSchemeCode(null)}>
                {isHindi ? 'रद्द करें' : 'Cancel'}
              </Button>
              <Button
                variant="primary"
                size="sm"
                isLoading={isSubmitting}
                disabled={!refNumber}
                onClick={handleRecordGovtVerification}
              >
                {isHindi ? 'सत्यापन सहेजें' : 'Save Verification'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
