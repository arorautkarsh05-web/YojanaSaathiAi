import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  ShieldCheck, AlertTriangle, CheckCircle2, Download, X
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { api } from '../../services/api';
import type { ActionPlanConfirmationResponse } from '../../services/api';

interface FinalConfirmationModalProps {
  planNumber: string;
  canConfirm: boolean;
  unmetPrerequisites: string[];
  existingConfirmation?: ActionPlanConfirmationResponse | null;
  onClose: () => void;
  onSuccess: (conf: ActionPlanConfirmationResponse) => void;
}

export const FinalConfirmationModal: React.FC<FinalConfirmationModalProps> = ({
  planNumber,
  canConfirm,
  unmetPrerequisites,
  existingConfirmation,
  onClose,
  onSuccess,
}) => {
  const { i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [farmerConsent, setFarmerConsent] = useState(true);
  const [farmerName, setFarmerName] = useState('');
  const [farmerMobile, setFarmerMobile] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [confirmedData, setConfirmedData] = useState<ActionPlanConfirmationResponse | null>(
    existingConfirmation || null
  );

  const maskedPreview = farmerMobile && farmerMobile.length >= 4 
    ? `${'*'.repeat(Math.max(0, farmerMobile.length - 4))}${farmerMobile.slice(-4)}`
    : '******1234';

  const handleConfirm = async () => {
    if (!farmerConsent) {
      setErrorMessage(isHindi ? 'कृपया संपुष्टि से पहले सहमति चेकबॉक्स चुनें।' : 'Please check the consent box.');
      return;
    }
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const res = await api.confirmActionPlan(
        planNumber,
        farmerConsent,
        farmerName || undefined,
        farmerMobile || undefined
      );
      setConfirmedData(res);
      onSuccess(res);
    } catch (err: any) {
      setErrorMessage(err.message || 'कार्य योजना संपुष्टि विफल रही।');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-ink-950/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-panel max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-appBorder space-y-5 animate-in fade-in duration-200">
        {/* Header */}
        <div className="flex items-center justify-between border-b pb-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-forest-800" />
            <h2 className="font-serif font-bold text-lg text-forest-900">
              {isHindi ? 'कार्य योजना संपुष्टि एवं लाभ संक्षेप' : 'Action Plan Confirmation & Summary'}
            </h2>
          </div>
          <button 
            onClick={onClose} 
            className="text-muted hover:text-ink-950 p-1 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Confirmed Success State */}
        {confirmedData ? (
          <div className="space-y-5 text-center py-2">
            <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center mx-auto shadow-inner">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                {isHindi ? 'कार्य योजना सफलतापूर्वक संपुष्ट' : 'Action Plan Confirmed'}
              </span>
              <h3 className="text-base font-bold text-forest-950 mt-2 font-mono">
                {confirmedData.summary_ref_id}
              </h3>
              <p className="text-xs text-muted-dark mt-1">
                {isHindi
                  ? 'आपकी तैयारी योजना एवं सत्यापित दस्तावेज़ संक्षेप तैयार है। आप इसे 1-पेज संक्षेप के रूप में सुरक्षित अथवा डाउनलोड कर सकते हैं।'
                  : 'Your preparation roadmap and verified document summary is generated. Download your official 1-page summary PDF below.'}
              </p>
            </div>

            <div className="p-3 bg-paper-100 rounded-natural border border-appBorder text-left text-xs space-y-1 font-mono">
              <div className="text-muted">
                <span className="font-sans font-bold text-ink-950">योजना संदर्भ:</span> {confirmedData.plan_number}
              </div>
              <div className="text-muted">
                <span className="font-sans font-bold text-ink-950">आवेदक:</span> {confirmedData.farmer_name || 'आवेदक किसान'}
              </div>
              <div className="text-muted">
                <span className="font-sans font-bold text-ink-950">संपर्क (मास्क्ड):</span> {confirmedData.farmer_mobile_masked || '******1234'}
              </div>
              <div className="text-[10px] text-muted-dark font-sans pt-1 italic">
                * यह एक स्वतंत्र गैर-सरकारी तैयारी संक्षेप है।
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <a
                href={api.getSummaryPdfUrl(planNumber)}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-natural bg-forest-800 hover:bg-forest-900 text-paper-50 font-bold text-xs transition-colors shadow-sm"
              >
                <Download className="w-4 h-4" />
                <span>{isHindi ? 'किसान लाभ संक्षेप (PDF) डाउनलोड करें' : 'Download Summary PDF'}</span>
              </a>
              <Button variant="secondary" size="sm" onClick={onClose}>
                {isHindi ? 'बंद करें' : 'Close'}
              </Button>
            </div>
          </div>
        ) : (
          /* Pre-Confirmation Form */
          <div className="space-y-4 text-xs">
            {/* Prerequisites Check */}
            {!canConfirm ? (
              <div className="p-4 rounded-natural bg-red-50 border border-red-300 space-y-2">
                <div className="font-bold text-red-900 flex items-center gap-2 text-sm">
                  <AlertTriangle className="w-4 h-4 text-red-700 shrink-0" />
                  <span>{isHindi ? 'संपुष्टि से पूर्व अनिवार्य शर्तें अधूरी हैं' : 'Prerequisites Incomplete'}</span>
                </div>
                <p className="text-red-800 leading-relaxed">
                  {isHindi
                    ? 'कार्य योजना संपुष्ट करने के लिए सभी अनिवार्य दस्तावेज़ों का अपलोड एवं सत्यापन आवश्यक है:'
                    : 'All mandatory documents must be uploaded and verified before confirmation:'}
                </p>
                <ul className="list-disc list-inside space-y-1 text-red-950 pl-1 font-medium">
                  {unmetPrerequisites.map((req, i) => (
                    <li key={i}>{req}</li>
                  ))}
                </ul>
                <div className="pt-2">
                  <Button variant="secondary" size="sm" onClick={onClose} className="w-full">
                    {isHindi ? 'दस्तावेज़ सत्यापन केंद्र पर वापस जाएँ' : 'Return to Document Centre'}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-natural text-emerald-900 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
                  <span className="font-bold">{isHindi ? 'सभी अनिवार्य दस्तावेज़ सत्यापित हैं!' : 'All mandatory documents verified!'}</span>
                </div>

                {errorMessage && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-natural text-red-900">
                    {errorMessage}
                  </div>
                )}

                {/* Farmer Details */}
                <div className="space-y-3">
                  <div>
                    <label className="font-semibold text-ink-950 block mb-1">
                      {isHindi ? 'किसान का नाम (Applicant Name):' : 'Farmer Name:'}
                    </label>
                    <input
                      type="text"
                      value={farmerName}
                      onChange={e => setFarmerName(e.target.value)}
                      placeholder={isHindi ? 'उदा. राम कुमार वर्मा' : 'e.g. Ram Kumar Verma'}
                      className="w-full p-2.5 rounded border border-appBorder bg-white text-ink-950 text-xs"
                    />
                  </div>

                  <div>
                    <label className="font-semibold text-ink-950 block mb-1 flex items-center justify-between">
                      <span>{isHindi ? 'मोबाइल नंबर (सुरक्षित मास्किंग):' : 'Mobile Number (Masked for Privacy):'}</span>
                      <span className="font-mono text-[10px] text-muted">दृश्य: {maskedPreview}</span>
                    </label>
                    <input
                      type="tel"
                      value={farmerMobile}
                      onChange={e => setFarmerMobile(e.target.value)}
                      placeholder={isHindi ? 'उदा. 9876543210' : 'e.g. 9876543210'}
                      maxLength={10}
                      className="w-full p-2.5 rounded border border-appBorder bg-white text-ink-950 font-mono text-xs"
                    />
                  </div>
                </div>

                {/* Mandatory Consent Checkbox */}
                <div className="p-3.5 rounded-natural bg-paper-100 border border-appBorder space-y-2">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={farmerConsent}
                      onChange={e => setFarmerConsent(e.target.checked)}
                      className="mt-0.5 rounded border-appBorder text-forest-800 focus:ring-forest-800"
                    />
                    <span className="text-[11px] text-ink-950 leading-relaxed font-medium">
                      {isHindi
                        ? 'मैं समझता/समझती हूँ कि यह योजना साथी AI द्वारा तैयार की गई एक स्वतंत्र तैयारी योजना है। यह सरकारी प्रमाण-पत्र नहीं है और अंतिम पात्रता व अनुदान संबंधित सरकारी विभाग के विवेकाधीन सत्यापन पर निर्भर है।'
                        : 'I understand this is an independent benefit preparation summary by YojanaSaathi AI. It is NOT a government certificate, and official sanction depends exclusively on departmental verification.'}
                    </span>
                  </label>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-end gap-2 pt-2 border-t">
                  <Button variant="secondary" size="sm" onClick={onClose}>
                    {isHindi ? 'रद्द करें' : 'Cancel'}
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    isLoading={isSubmitting}
                    disabled={!farmerConsent}
                    onClick={handleConfirm}
                  >
                    {isHindi ? 'कार्य योजना संपुष्ट करें' : 'Confirm Action Plan'}
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
