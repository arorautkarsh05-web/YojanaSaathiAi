import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Upload, CheckCircle2, AlertTriangle, XCircle, RefreshCw, 
  Download, ShieldCheck, Info
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

const REJECTION_REASONS = [
  'दस्तावेज़ स्पष्ट या पढ़ने योग्य नहीं है (Blurred or Unreadable Document)',
  'नाम या व्यक्तिगत विवरण में विसंगति (Name or Profile Mismatch)',
  'दस्तावेज़ की वैधता समाप्त हो चुकी है (Document Expired)',
  'गलत या अधूरा दस्तावेज़ अपलोड किया गया (Incorrect or Incomplete Document)',
  'राजस्व मुहर या डिजिटल हस्ताक्षर अनुपलब्ध (Missing Revenue Seal or Digital Signature)',
  'आधार संख्या अस्पष्ट या गैर-मास्क्ड (Aadhaar Number Unclear or Unmasked)',
];

export const DocumentVerificationCenter: React.FC<DocumentVerificationCenterProps> = ({
  planNumber,
  requiredDocs,
  uploadedDocs,
  onWorkflowUpdate,
}) => {
  const { i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [uploadingDocKey, setUploadingDocKey] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Reviewer Simulation Panel State
  const [reviewerModalDoc, setReviewerModalDoc] = useState<FarmerDocumentOut | null>(null);
  const [reviewerAction, setReviewerAction] = useState<'APPROVE' | 'REJECT' | 'REQUEST_REUPLOAD'>('APPROVE');
  const [selectedReason, setSelectedReason] = useState<string>(REJECTION_REASONS[0]);
  const [reviewerRemarks, setReviewerRemarks] = useState<string>('');
  const [isReviewing, setIsReviewing] = useState<boolean>(false);

  const fileInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const uploadedMap = new Map<string, FarmerDocumentOut>();
  uploadedDocs.forEach(d => uploadedMap.set(d.doc_id_key, d));

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
      setSuccessMessage(isHindi ? 'दस्तावेज़ सफलतापूर्वक अपलोड हुआ! समीक्षाधीन है।' : 'Document uploaded successfully! Under review.');
      onWorkflowUpdate();
    } catch (err: any) {
      setErrorMessage(err.message || (isHindi ? 'दस्तावेज़ अपलोड विफल रहा।' : 'Upload failed.'));
    } finally {
      setUploadingDocKey(null);
    }
  };

  const handleReviewerSubmit = async () => {
    if (!reviewerModalDoc) return;
    setIsReviewing(true);
    setErrorMessage(null);
    try {
      await api.verifyDocument(
        planNumber,
        reviewerModalDoc.id,
        reviewerAction,
        reviewerAction !== 'APPROVE' ? selectedReason : undefined,
        reviewerRemarks || (reviewerAction === 'APPROVE' ? 'सत्यापित एवं प्रामाणिक' : undefined)
      );
      setSuccessMessage(
        isHindi 
          ? `दस्तावेज़ की समीक्षा पूर्ण: ${reviewerAction === 'APPROVE' ? 'स्वीकृत (VERIFIED)' : 'अस्वीकृत / पुनः अपलोड'}`
          : `Review recorded: ${reviewerAction}`
      );
      setReviewerModalDoc(null);
      onWorkflowUpdate();
    } catch (err: any) {
      setErrorMessage(err.message || 'समीक्षा विफल रही');
    } finally {
      setIsReviewing(false);
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
            {isHindi ? 'दस्तावेज़ सुरक्षा एवं आधार गोपनीयता परामर्श (Privacy Advisory)' : 'Document Security & Aadhaar Privacy Advisory'}
          </div>
          <p className="leading-relaxed text-muted-dark">
            {isHindi
              ? 'योजना साथी AI सभी दिशा-निर्देशों में आधार की सार्वभौमिक अनिवार्यता लागू नहीं करता है। आधार केवल वहीं आवश्यक है जहां आधिकारिक डीबीटी अधिनियम के तहत कानूनी जनादेश है। सुरक्षा हेतु केवल मास्क्ड आधार (Masked Aadhaar — अंतिम 4 अंक दृश्य) अपलोड करने की अनुशंसा की जाती है।'
              : 'Aadhaar is never universally mandatory. Upload only when legally mandated under official scheme DBT rules. Masked Aadhaar (showing only last 4 digits) is strongly recommended for applicant safety.'}
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
            {isHindi ? 'बहु-योजना साझा दस्तावेज़ सूची' : 'Multi-Scheme Consolidated Document Checklist'}
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
          const isRejected = status === 'REJECTED';
          const isReupload = status === 'REUPLOAD_REQUIRED';
          const isUnderReview = status === 'UNDER_REVIEW' || status === 'UPLOADED';

          return (
            <div
              key={spec.doc_id_key}
              className={`p-4 rounded-natural border transition-all ${
                isVerified
                  ? 'bg-emerald-50/50 border-emerald-300'
                  : isRejected || isReupload
                  ? 'bg-red-50/50 border-red-300'
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
                        {isHindi ? 'मास्क्ड आधार अनुशंसित' : 'Masked Aadhaar'}
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

                  {/* Rejection / Reviewer remarks notice */}
                  {uploaded?.rejection_reason && (
                    <div className="p-2 mt-2 rounded bg-red-100/80 border border-red-200 text-xs text-red-900 flex items-start gap-1.5">
                      <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                      <div>
                        <div className="font-bold">{isHindi ? 'पुनः जांच / अस्वीकृति कारण:' : 'Rejection Reason:'}</div>
                        <div>{uploaded.rejection_reason}</div>
                        {uploaded.verification_remarks && (
                          <div className="text-[11px] text-red-800 mt-0.5 italic">टिप्पणी: {uploaded.verification_remarks}</div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Right: Upload Status & Controls */}
                <div className="flex flex-col sm:flex-row md:flex-col items-start md:items-end gap-2.5 shrink-0">
                  {/* Status Badge */}
                  <div className="flex items-center gap-1.5">
                    {isVerified && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                        {isHindi ? 'सत्यापित (VERIFIED)' : 'VERIFIED'}
                      </span>
                    )}
                    {isUnderReview && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-900 border border-blue-300">
                        <RefreshCw className="w-3.5 h-3.5 text-blue-700 animate-spin" />
                        {isHindi ? 'समीक्षाधीन (Under Review)' : 'UNDER REVIEW'}
                      </span>
                    )}
                    {isRejected && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-900 border border-red-300">
                        <XCircle className="w-3.5 h-3.5 text-red-700" />
                        {isHindi ? 'अस्वीकृत (REJECTED)' : 'REJECTED'}
                      </span>
                    )}
                    {isReupload && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-700" />
                        {isHindi ? 'पुनः अपलोड आवश्यक' : 'REUPLOAD REQUIRED'}
                      </span>
                    )}
                    {status === 'NOT_UPLOADED' && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-paper-200 text-muted-dark border border-appBorder">
                        {isHindi ? 'अपलोड नहीं हुआ' : 'NOT UPLOADED'}
                      </span>
                    )}
                  </div>

                  {/* Upload / Replace Actions */}
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
                        ? (isHindi ? 'दस्तावेज़ बदलें' : 'Replace') 
                        : (isHindi ? 'फ़ाइल अपलोड करें' : 'Upload Document')}
                    </Button>

                    {/* Preview / Download if uploaded */}
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

                    {/* Reviewer Simulation Action (Verification Officer Panel) */}
                    {isUploaded && uploaded && (
                      <Button
                        variant="secondary"
                        size="sm"
                        className="text-[11px] text-leaf-700 border-leaf-300 hover:bg-leaf-50"
                        onClick={() => {
                          setReviewerModalDoc(uploaded);
                          setReviewerAction('APPROVE');
                          setReviewerRemarks('');
                        }}
                      >
                        {isHindi ? 'अधिकारी समीक्षा' : 'Reviewer Action'}
                      </Button>
                    )}
                  </div>

                  {/* File Metadata */}
                  {uploaded && (
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

      {/* Reviewer Verification Modal Dialog */}
      {reviewerModalDoc && (
        <div className="fixed inset-0 z-50 bg-ink-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-natural max-w-lg w-full p-6 shadow-xl border border-appBorder space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="font-bold text-forest-900 text-sm flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-forest-700" />
                <span>{isHindi ? 'सत्यापन अधिकारी समीक्षा (Reviewer Action)' : 'Reviewer Verification Action'}</span>
              </h3>
              <button 
                onClick={() => setReviewerModalDoc(null)}
                className="text-muted hover:text-ink-950"
              >
                ✕
              </button>
            </div>

            <div className="text-xs text-muted-dark space-y-1">
              <div>
                <span className="font-semibold text-ink-950">{isHindi ? 'दस्तावेज़:' : 'Document:'}</span>{' '}
                {isHindi ? reviewerModalDoc.title_hi : reviewerModalDoc.title_en}
              </div>
              <div>
                <span className="font-semibold text-ink-950">{isHindi ? 'मूल फ़ाइल:' : 'File:'}</span>{' '}
                {reviewerModalDoc.file_name_original}
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <label className="text-xs font-bold text-ink-950 block">
                {isHindi ? 'समीक्षा निर्णय (Review Decision):' : 'Review Decision:'}
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setReviewerAction('APPROVE')}
                  className={`p-2 rounded text-xs font-bold border text-center transition-all ${
                    reviewerAction === 'APPROVE'
                      ? 'bg-emerald-100 text-emerald-900 border-emerald-400 ring-2 ring-emerald-300'
                      : 'bg-paper-50 text-muted-dark border-appBorder'
                  }`}
                >
                  ✓ {isHindi ? 'स्वीकार (Approve)' : 'Approve'}
                </button>
                <button
                  type="button"
                  onClick={() => setReviewerAction('REJECT')}
                  className={`p-2 rounded text-xs font-bold border text-center transition-all ${
                    reviewerAction === 'REJECT'
                      ? 'bg-red-100 text-red-900 border-red-400 ring-2 ring-red-300'
                      : 'bg-paper-50 text-muted-dark border-appBorder'
                  }`}
                >
                  ✕ {isHindi ? 'अस्वीकार (Reject)' : 'Reject'}
                </button>
                <button
                  type="button"
                  onClick={() => setReviewerAction('REQUEST_REUPLOAD')}
                  className={`p-2 rounded text-xs font-bold border text-center transition-all ${
                    reviewerAction === 'REQUEST_REUPLOAD'
                      ? 'bg-amber-100 text-amber-900 border-amber-400 ring-2 ring-amber-300'
                      : 'bg-paper-50 text-muted-dark border-appBorder'
                  }`}
                >
                  ↻ {isHindi ? 'पुनः अपलोड' : 'Re-upload'}
                </button>
              </div>

              {reviewerAction !== 'APPROVE' && (
                <div className="space-y-1.5 pt-1">
                  <label className="text-xs font-bold text-red-900 block">
                    {isHindi ? 'अस्वीकृति का आधिकारिक कारण चुनें:' : 'Select Rejection Reason:'}
                  </label>
                  <select
                    value={selectedReason}
                    onChange={e => setSelectedReason(e.target.value)}
                    className="w-full text-xs p-2 rounded border border-appBorder bg-white text-ink-950"
                  >
                    {REJECTION_REASONS.map(r => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="space-y-1 pt-1">
                <label className="text-xs font-medium text-ink-950 block">
                  {isHindi ? 'समीक्षा टिप्पणी (वैकल्पिक):' : 'Reviewer Remarks (Optional):'}
                </label>
                <input
                  type="text"
                  value={reviewerRemarks}
                  onChange={e => setReviewerRemarks(e.target.value)}
                  placeholder={isHindi ? 'उदाहरण: राजस्व मुहर सत्यापित' : 'e.g., Revenue seal verified'}
                  className="w-full text-xs p-2 rounded border border-appBorder bg-white text-ink-950"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-4 border-t">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setReviewerModalDoc(null)}
              >
                {isHindi ? 'रद्द करें' : 'Cancel'}
              </Button>
              <Button
                variant="primary"
                size="sm"
                isLoading={isReviewing}
                onClick={handleReviewerSubmit}
              >
                {isHindi ? 'समीक्षा सहेजें' : 'Save Review'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
