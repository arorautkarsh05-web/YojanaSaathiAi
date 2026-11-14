import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Upload, CheckCircle2, XCircle, 
  Download, ShieldCheck, Info, CheckSquare, Square
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { api } from '../../services/api';
import type { 
  RequiredDocumentSpec, 
  FarmerDocumentOut 
} from '../../services/api';

interface DocumentVerificationCenterProps {
  planNumber: string;
  requiredDocs: RequiredDocumentSpec[];
  uploadedDocs: FarmerDocumentOut[];
  onWorkflowUpdate: () => void;
}

export const DocumentVerificationCenter: React.FC<DocumentVerificationCenterProps> = ({
  planNumber,
  requiredDocs,
  uploadedDocs,
  onWorkflowUpdate,
}) => {
  const { i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [uploadingDocKey, setUploadingDocKey] = useState<string | null>(null);
  const [togglingDocKey, setTogglingDocKey] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fileInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const uploadedMap = new Map<string, FarmerDocumentOut>();
  uploadedDocs.forEach(d => uploadedMap.set(d.doc_id_key, d));

  // Toggling a non-upload document (Khatauni, Bank Passbook, etc.)
  const handleToggleCheck = async (docKey: string, currentlyVerified: boolean) => {
    setErrorMessage(null);
    setSuccessMessage(null);
    setTogglingDocKey(docKey);
    try {
      await api.toggleDocumentCheck(planNumber, docKey, !currentlyVerified);
      setSuccessMessage(
        !currentlyVerified
          ? (isHindi ? 'दस्तावेज़ की पुष्टि दर्ज कर ली गई और सत्यापित चिह्नित हुआ!' : 'Document confirmed and verified!')
          : (isHindi ? 'दस्तावेज़ स्थिति रीसेट की गई।' : 'Document status reset.')
      );
      onWorkflowUpdate();
    } catch (err: any) {
      setErrorMessage(err.message || 'स्थिति बदलने में विफल');
    } finally {
      setTogglingDocKey(null);
    }
  };

  // Uploading Aadhaar or Photo (Auto-verified immediately)
  const handleFileChange = async (docKey: string, file: File | null) => {
    if (!file) return;
    setErrorMessage(null);
    setSuccessMessage(null);

    // Validate size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrorMessage(isHindi ? 'फ़ाइल 5MB से अधिक बड़ी है। कृपया छोटी फ़ाइल चुनें।' : 'File size exceeds 5MB limit.');
      return;
    }

    // Validate type extension
    const validExts = ['.pdf', '.jpg', '.jpeg', '.png'];
    const lowerName = file.name.toLowerCase();
    const isValid = validExts.some(ext => lowerName.endsWith(ext));
    if (!isValid) {
      setErrorMessage(isHindi ? 'केवल PDF, JPG या PNG फ़ाइलें ही स्वीकार्य हैं।' : 'Only PDF, JPG or PNG files are accepted.');
      return;
    }

    setUploadingDocKey(docKey);
    try {
      await api.uploadDocument(planNumber, docKey, file);
      setSuccessMessage(
        isHindi 
          ? 'दस्तावेज़ सफलतापूर्वक अपलोड हुआ और स्वचालित रूप से सत्यापित (VERIFIED) कर दिया गया!' 
          : 'Document uploaded and auto-verified successfully!'
      );
      onWorkflowUpdate();
    } catch (err: any) {
      setErrorMessage(err.message || (isHindi ? 'दस्तावेज़ अपलोड विफल रहा।' : 'Upload failed.'));
    } finally {
      setUploadingDocKey(null);
    }
  };

  const mandatoryCount = requiredDocs.filter(d => d.is_mandatory).length;
  const verifiedMandatoryCount = requiredDocs.filter(
    d => d.is_mandatory && uploadedMap.get(d.doc_id_key)?.verification_status === 'VERIFIED'
  ).length;

  return (
    <div className="space-y-6">
      {/* Aadhaar Privacy & Legal Advisory Notice */}
      <div className="p-4 rounded-natural bg-paper-100 border border-emerald-300 text-xs text-forest-950 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-forest-800 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-forest-900 text-sm">
            {isHindi ? 'दस्तावेज़ सुरक्षा एवं स्वचालित सत्यापन' : 'Document Security & Instant Verification'}
          </div>
          <p className="leading-relaxed text-muted-dark">
            {isHindi
              ? 'केवल आधार एवं फोटो के लिए फ़ाइल अपलोड आवश्यक है (अपलोड होते ही स्वचालित सत्यापित हो जाती है)। खतौनी, बैंक पासबुक एवं अन्य दस्तावेज़ों के लिए सीधे टिक-बॉक्स पर क्लिक करके दस्तावेज़ की उपलब्धता सत्यापित करें।'
              : 'Upload is required only for Aadhaar and Photograph (automatically verified on upload). For all other documents (Khatauni, Bank Passbook), simply click the checkbox to mark as verified.'}
          </p>
        </div>
      </div>

      {/* Progress & Verification Status Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-natural bg-field-100/70 border border-forest-800/30">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-forest-800">
            {isHindi ? 'चरण 4: दस्तावेज़ सत्यापन केंद्र' : 'Stage 4: Document Verification Centre'}
          </div>
          <div className="text-sm font-semibold text-forest-950 mt-0.5">
            {isHindi ? 'साझा दस्तावेज़ सूची (सरल 1-क्लिक सत्यापन)' : 'Consolidated Checklist (1-Click Verification)'}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
            verifiedMandatoryCount === mandatoryCount && mandatoryCount > 0
              ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
              : 'bg-amber-100 text-amber-900 border-amber-300'
          }`}>
            {verifiedMandatoryCount} / {mandatoryCount} {isHindi ? 'अनिवार्य सत्यापित' : 'Mandatory Verified'}
          </span>
        </div>
      </div>

      {/* Alert Messages */}
      {errorMessage && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-natural text-xs text-red-800 flex items-center gap-2">
          <XCircle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{errorMessage}</span>
        </div>
      )}
      {successMessage && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-natural text-xs text-emerald-800 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Dynamic Required Documents List */}
      <div className="space-y-4">
        {requiredDocs.map(spec => {
          const uploaded = uploadedMap.get(spec.doc_id_key);
          const isUploaded = !!uploaded;
          const status = uploaded?.verification_status || 'NOT_UPLOADED';
          const isVerified = status === 'VERIFIED';
          const isUnderReview = status === 'UNDER_REVIEW' || status === 'UPLOADED';

          // File upload only for Aadhaar and Photo as instructed
          const isUploadRequired = spec.doc_id_key === 'doc_aadhaar' || spec.doc_id_key === 'doc_photo';
          const isToggling = togglingDocKey === spec.doc_id_key;

          return (
            <div
              key={spec.doc_id_key}
              className={`p-4 rounded-natural border transition-all ${
                isVerified
                  ? 'bg-emerald-50/60 border-emerald-300 shadow-2xs'
                  : isUnderReview
                  ? 'bg-blue-50/40 border-blue-200'
                  : 'bg-white/80 border-appBorder'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                {/* Left: Document Info */}
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-forest-900 text-sm">
                      {isHindi ? spec.title_hi : spec.title_en}
                    </span>
                    {spec.is_mandatory ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-forest-800 text-paper-50">
                        {isHindi ? 'अनिवार्य' : 'Mandatory'}
                      </span>
                    ) : (
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-paper-100 text-muted-dark border border-appBorder">
                        {isHindi ? 'ऐच्छिक' : 'Optional'}
                      </span>
                    )}
                    {spec.is_aadhaar && (
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-200">
                        {isHindi ? 'मास्क्ड आधार' : 'Masked Aadhaar'}
                      </span>
                    )}
                    {isUploadRequired && (
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-900 border border-blue-200">
                        {isHindi ? 'फ़ाइल अपलोड' : 'File Upload'}
                      </span>
                    )}
                  </div>

                  <div className="text-xs text-muted-dark">
                    <span className="font-medium text-ink-950">{isHindi ? 'सक्षम प्राधिकारी:' : 'Issuing Authority:'}</span>{' '}
                    {spec.source_authority}
                  </div>

                  {/* Deduplication: Applicable Schemes */}
                  <div className="flex items-center gap-1.5 flex-wrap pt-1 text-[11px]">
                    <span className="text-muted font-medium">
                      {isHindi ? 'लागू योजनाएँ (साझा):' : 'Shared with schemes:'}
                    </span>
                    {spec.applicable_schemes.map(code => (
                      <span
                        key={code}
                        className="px-1.5 py-0.5 rounded bg-paper-200 text-forest-900 font-mono text-[10px] border border-appBorder"
                      >
                        {code}
                      </span>
                    ))}
                  </div>

                  {spec.notes_hi && (
                    <div className="text-[11px] text-muted italic flex items-center gap-1 mt-1">
                      <Info className="w-3 h-3 shrink-0" />
                      <span>{spec.notes_hi}</span>
                    </div>
                  )}
                </div>

                {/* Right: Tick box OR File Upload */}
                <div className="flex flex-col sm:flex-row md:flex-col items-start md:items-end gap-2.5 shrink-0">
                  {/* Status Badge */}
                  <div className="flex items-center gap-1.5">
                    {isVerified ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                        {isHindi ? 'सत्यापित (VERIFIED)' : 'VERIFIED'}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-paper-200 text-muted-dark border border-appBorder">
                        {isHindi ? 'लंबित / असत्यापित' : 'PENDING'}
                      </span>
                    )}
                  </div>

                  {/* Tick Box for Non-Aadhaar/Photo docs */}
                  {!isUploadRequired ? (
                    <button
                      type="button"
                      disabled={isToggling}
                      onClick={() => handleToggleCheck(spec.doc_id_key, isVerified)}
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
                          ? (isHindi ? 'दस्तावेज़ उपलब्ध व सत्यापित ✓' : 'Verified & Ready ✓') 
                          : (isHindi ? 'दस्तावेज़ उपलब्ध चिह्नित करें' : 'Mark Document Available')}
                      </span>
                    </button>
                  ) : (
                    /* File Upload for Aadhaar and Photo with Immediate Auto-Verification */
                    <div className="flex items-center gap-2">
                      <input
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        className="hidden"
                        ref={el => { fileInputRefs.current[spec.doc_id_key] = el; }}
                        onChange={e => {
                          const file = e.target.files?.[0] || null;
                          handleFileChange(spec.doc_id_key, file);
                          e.target.value = '';
                        }}
                      />

                      <Button
                        variant={isUploaded ? 'secondary' : 'primary'}
                        size="sm"
                        leftIcon={<Upload className="w-3.5 h-3.5" />}
                        isLoading={uploadingDocKey === spec.doc_id_key}
                        onClick={() => fileInputRefs.current[spec.doc_id_key]?.click()}
                      >
                        {isUploaded 
                          ? (isHindi ? 'फ़ाइल बदलें' : 'Replace File') 
                          : (isHindi ? 'फ़ाइल अपलोड करें (स्वतः सत्यापित)' : 'Upload File (Auto-Verify)')}
                      </Button>

                      {isUploaded && uploaded && (
                        <a
                          href={api.getDocumentDownloadUrl(planNumber, uploaded.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 rounded border border-appBorder hover:bg-paper-100 text-forest-800 transition-colors"
                          title={isHindi ? 'दस्तावेज़ देखें / डाउनलोड' : 'View / Download'}
                        >
                          <Download className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  )}

                  {/* File Metadata if uploaded */}
                  {uploaded && isUploadRequired && (
                    <div className="text-[10px] text-muted font-mono">
                      {uploaded.file_name_original} ({(uploaded.file_size_bytes / 1024).toFixed(1)} KB)
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
