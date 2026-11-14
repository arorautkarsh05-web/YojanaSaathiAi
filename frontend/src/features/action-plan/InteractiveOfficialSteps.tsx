import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  MapPin, ExternalLink, ShieldAlert, FileText, CheckSquare, Square
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { api } from '../../services/api';
import type { OfficialStep, ActionItemCompletionOut } from '../../services/api';

interface InteractiveOfficialStepsProps {
  planNumber: string;
  officialSteps: OfficialStep[];
  stepCompletions: ActionItemCompletionOut[];
  onWorkflowUpdate: () => void;
}

export const InteractiveOfficialSteps: React.FC<InteractiveOfficialStepsProps> = ({
  planNumber,
  officialSteps,
  stepCompletions,
  onWorkflowUpdate,
}) => {
  const { i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [togglingStep, setTogglingStep] = useState<number | null>(null);
  const [ackInputs, setAckInputs] = useState<Record<number, string>>({});
  const [editingAckStep, setEditingAckStep] = useState<number | null>(null);

  const completionMap = new Map<number, ActionItemCompletionOut>();
  stepCompletions.forEach(c => completionMap.set(c.step_number, c));

  const handleToggle = async (step: OfficialStep, currentCompleted: boolean) => {
    setTogglingStep(step.step_number);
    try {
      const codeTag = step.title_en.includes(']') 
        ? step.title_en.split(']')[0].replace('[', '').trim() 
        : 'SCHEME';
      const existingAck = completionMap.get(step.step_number)?.acknowledgement_ref || ackInputs[step.step_number];

      await api.toggleActionStep(
        planNumber,
        step.step_number,
        codeTag,
        !currentCompleted,
        existingAck,
        'Checked via interactive workflow'
      );
      onWorkflowUpdate();
    } catch (err: any) {
      console.error('Toggle error:', err);
    } finally {
      setTogglingStep(null);
    }
  };

  const handleSaveAck = async (step: OfficialStep) => {
    const ackVal = ackInputs[step.step_number];
    if (!ackVal) return;
    setTogglingStep(step.step_number);
    try {
      const codeTag = step.title_en.includes(']') 
        ? step.title_en.split(']')[0].replace('[', '').trim() 
        : 'SCHEME';
      await api.toggleActionStep(
        planNumber,
        step.step_number,
        codeTag,
        true, // completing when ack is added
        ackVal,
        'Application reference recorded'
      );
      setEditingAckStep(null);
      onWorkflowUpdate();
    } catch (err) {
      console.error('Save ack error:', err);
    } finally {
      setTogglingStep(null);
    }
  };

  const completedCount = officialSteps.filter(s => completionMap.get(s.step_number)?.is_completed).length;

  return (
    <div className="space-y-6">
      {/* Prominent Legal Distinction Notice */}
      <div className="p-4 rounded-natural bg-amber-50 border border-amber-300 text-xs text-amber-950 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-amber-900 text-sm">
            {isHindi ? 'महत्वपूर्ण सूचना: यह सरकारी आवेदन नहीं है (Statutory Notice)' : 'Statutory Notice: Not an Official Government Submission'}
          </div>
          <p className="leading-relaxed">
            {isHindi
              ? 'यहाँ चेकबॉक्स पर टिक करने से आपकी व्यक्तिगत तैयारी योजना अद्यतन होती है। इससे सरकारी विभाग में आपका आवेदन जमा या स्वीकृत नहीं होता है। वास्तविक आवेदन केवल संबंधित आधिकारिक पोर्टल लिंक अथवा तहसील / जन सुविधा केंद्र (CSC) पर जाकर ही पूरा करें।'
              : 'Checking these checkboxes tracks your personal preparation milestones on YojanaSaathi AI. It does NOT submit, register, or approve your official government benefit application. You must apply directly on the designated official portals or at a Common Service Centre (CSC).'}
          </p>
        </div>
      </div>

      {/* Header with counter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-natural bg-field-100/70 border border-forest-800/30">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-forest-800">
            {isHindi ? 'चरण 5: सत्यापित आधिकारिक आवेदन कदम' : 'Stage 5: Verified Official Next Steps'}
          </div>
          <div className="text-sm font-semibold text-forest-950 mt-0.5">
            {isHindi ? 'आधिकारिक पोर्टल दिशा-निर्देश एवं चरणबद्ध कार्य' : 'Official Portal Directives & Step-by-Step Actions'}
          </div>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-bold bg-forest-800 text-paper-50 border border-forest-900">
          {completedCount} / {officialSteps.length} {isHindi ? 'कदम पूर्ण' : 'Steps Completed'}
        </span>
      </div>

      {/* Steps List */}
      <div className="space-y-3.5">
        {officialSteps.map(step => {
          const completion = completionMap.get(step.step_number);
          const isDone = completion?.is_completed || false;
          const isToggling = togglingStep === step.step_number;
          const ackRef = completion?.acknowledgement_ref;

          return (
            <div
              key={step.step_number}
              className={`p-4 rounded-natural border transition-all text-xs flex flex-col sm:flex-row items-start gap-3.5 ${
                isDone
                  ? 'bg-emerald-50/60 border-emerald-300'
                  : 'bg-white/90 border-appBorder hover:border-forest-700/40'
              }`}
            >
              {/* Interactive Checkbox Button */}
              <button
                type="button"
                disabled={isToggling}
                onClick={() => handleToggle(step, isDone)}
                className="mt-0.5 flex items-center justify-center text-forest-800 hover:text-forest-950 transition-colors shrink-0"
                title={isDone ? (isHindi ? 'अपूर्ण चिह्नित करें' : 'Mark Incomplete') : (isHindi ? 'पूर्ण चिह्नित करें' : 'Mark Completed')}
              >
                {isDone ? (
                  <CheckSquare className="w-5 h-5 text-emerald-700" />
                ) : (
                  <Square className="w-5 h-5 text-muted hover:text-forest-800" />
                )}
              </button>

              {/* Step Details */}
              <div className="flex-1 space-y-1.5">
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <span className={`font-bold text-sm ${isDone ? 'text-forest-950 line-through decoration-emerald-600/70' : 'text-forest-900'}`}>
                    {step.step_number}. {isHindi ? step.title_hi : step.title_en}
                  </span>
                  {isDone && completion?.completed_at && (
                    <span className="text-[10px] font-mono text-emerald-800 bg-emerald-100/90 px-2 py-0.5 rounded border border-emerald-200">
                      ✓ {new Date(completion.completed_at).toLocaleDateString()} को दर्ज
                    </span>
                  )}
                </div>

                <p className="text-muted-dark leading-relaxed">
                  {isHindi ? step.description_hi : step.description_en}
                </p>

                {/* Portal Link */}
                <div className="pt-1 flex items-center gap-1.5 text-leaf-700 font-semibold text-[11px]">
                  <MapPin className="w-3.5 h-3.5 shrink-0" />
                  {step.portal_or_destination.startsWith('http') ? (
                    <a
                      href={step.portal_or_destination}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline hover:text-forest-900 transition-colors flex items-center gap-1"
                    >
                      <span>{step.portal_or_destination}</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <span>आधिकारिक गंतव्य / कार्यालय: {step.portal_or_destination}</span>
                  )}
                </div>

                {/* Application Reference / Acknowledgement Number */}
                <div className="pt-2 flex items-center gap-2 flex-wrap">
                  {ackRef ? (
                    <div className="flex items-center gap-1.5 text-[11px] font-mono bg-field-100 text-forest-950 px-2.5 py-1 rounded border border-forest-800/30">
                      <span className="font-sans font-bold text-forest-800">पावती / संदर्भ संख्या:</span>
                      <span>{ackRef}</span>
                      <button
                        onClick={() => {
                          setEditingAckStep(step.step_number);
                          setAckInputs(prev => ({ ...prev, [step.step_number]: ackRef }));
                        }}
                        className="text-xs text-leaf-600 underline ml-1 hover:text-forest-900 font-sans"
                      >
                        (बदलें)
                      </button>
                    </div>
                  ) : editingAckStep === step.step_number ? (
                    <div className="flex items-center gap-1.5">
                      <input
                        type="text"
                        value={ackInputs[step.step_number] || ''}
                        onChange={e => setAckInputs({ ...ackInputs, [step.step_number]: e.target.value })}
                        placeholder={isHindi ? 'पावती संख्या दर्ज करें' : 'Enter Ack Ref #'}
                        className="text-xs p-1.5 rounded border border-appBorder bg-white w-48 font-mono"
                      />
                      <Button
                        variant="primary"
                        size="sm"
                        className="text-xs py-1 px-2.5"
                        onClick={() => handleSaveAck(step)}
                      >
                        {isHindi ? 'सहेजें' : 'Save'}
                      </Button>
                      <button
                        onClick={() => setEditingAckStep(null)}
                        className="text-xs text-muted hover:text-ink-950"
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setEditingAckStep(step.step_number)}
                      className="text-[11px] text-leaf-700 hover:text-forest-900 underline flex items-center gap-1"
                    >
                      <FileText className="w-3 h-3" />
                      <span>{isHindi ? '+ पावती / आवेदन संदर्भ संख्या दर्ज करें' : '+ Add Acknowledgement / Reference Number'}</span>
                    </button>
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
