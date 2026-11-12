import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  CheckCircle2, XCircle, HelpCircle, ChevronDown, ChevronUp,
  ExternalLink, ArrowRight, Layers
} from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { api } from '../../services/api';
import type { SchemeEvaluation, PairwiseConvergence } from '../../services/api';

interface ResultsViewProps {
  schemes: SchemeEvaluation[];
  onGeneratePlan: (selectedCodes: string[]) => void;
  onRestart: () => void;
}

export const RecommendationResultsView: React.FC<ResultsViewProps> = ({
  schemes,
  onGeneratePlan,
  onRestart,
}) => {
  const { t, i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [expandedScheme, setExpandedScheme] = useState<string | null>(schemes[0]?.scheme_code || null);
  const [selectedForPlan, setSelectedForPlan] = useState<string[]>(
    schemes.filter(s => s.overall_status !== 'LIKELY_NOT_ELIGIBLE').map(s => s.scheme_code).slice(0, 3)
  );

  const [convergencePairs, setConvergencePairs] = useState<PairwiseConvergence[]>([]);
  const [isCheckingConvergence, setIsCheckingConvergence] = useState(false);
  const [showConvergenceModal, setShowConvergenceModal] = useState(false);

  const toggleSelectForPlan = (code: string) => {
    setSelectedForPlan(prev =>
      prev.includes(code) ? prev.filter(c => c !== code) : [...prev, code]
    );
  };

  const handleRunConvergence = async () => {
    if (selectedForPlan.length < 2) return;
    setIsCheckingConvergence(true);
    try {
      const res = await api.checkConvergence(selectedForPlan);
      setConvergencePairs(res.pairs);
      setShowConvergenceModal(true);
    } catch (err) {
      console.error(err);
    } finally {
      setIsCheckingConvergence(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 p-6 rounded-panel bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_30px_rgba(23,37,31,0.08)]">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-field-100 text-forest-800 border border-field-200">
              उत्तर प्रदेश • 75 जिले
            </span>
            <span className="text-xs text-muted-dark">
              {schemes.length} योजनाएँ जाँची गईं
            </span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-forest-900">
            {t('results.title')}
          </h1>
          <p className="text-sm text-muted mt-1">
            {t('results.subtitle')}
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button variant="secondary" size="sm" onClick={onRestart} className="bg-white/80 hover:bg-white border-white/80 shadow-2xs">
            {isHindi ? 'नया विवरण बदलें' : 'Change Inputs'}
          </Button>
          <Button
            variant="primary"
            size="md"
            disabled={selectedForPlan.length === 0}
            rightIcon={<ArrowRight className="w-4 h-4" />}
            onClick={() => onGeneratePlan(selectedForPlan)}
          >
            {t('results.generatePlanBtn')} ({selectedForPlan.length})
          </Button>
        </div>
      </div>

      {/* Convergence Check Callout Bar */}
      {selectedForPlan.length >= 2 && (
        <div className="mb-6 p-4 rounded-panel bg-white/85 backdrop-blur-xl border border-white/70 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-natural bg-leaf-600 text-paper-50 flex items-center justify-center shrink-0 shadow-xs">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-forest-900">
                {t('results.convergenceTitle')}
              </div>
              <div className="text-xs text-muted-dark">
                {t('results.convergenceDesc')} ({selectedForPlan.length} चयनित)
              </div>
            </div>
          </div>
          <Button
            variant="secondary"
            size="sm"
            isLoading={isCheckingConvergence}
            onClick={handleRunConvergence}
            className="bg-white/90 hover:bg-white shadow-2xs"
          >
            {isHindi ? 'टकराव / सह-अस्तित्व जाँचें' : 'Check Pairwise Compatibility'}
          </Button>
        </div>
      )}

      {/* Schemes List */}
      <div className="space-y-4">
        {schemes.map(scheme => {
          const isExpanded = expandedScheme === scheme.scheme_code;
          const isSelected = selectedForPlan.includes(scheme.scheme_code);

          return (
            <Card
              key={scheme.scheme_code}
              variant="surface"
              className={`border transition-all ${
                isSelected ? 'border-forest-800 shadow-xs' : 'border-appBorder'
              }`}
            >
              {/* Scheme Card Header */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <StatusBadge status={scheme.overall_status} size="sm" />
                    {scheme.ranking_factors && (
                      <span className="text-[11px] font-medium text-forest-800 bg-field-100/90 px-2 py-0.5 rounded border border-field-200">
                        {isHindi ? 'आवश्यकता मेल' : 'Need Match'}: {scheme.ranking_factors.need_relevance_pct}%
                      </span>
                    )}
                    <span className="text-[11px] font-mono text-muted bg-paper-50 px-2 py-0.5 rounded border border-appBorder">
                      {scheme.level === 'CENTRAL' ? 'केंद्र सरकार' : 'उत्तर प्रदेश सरकार'} • {scheme.benefit_type}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-ink-950 font-serif leading-snug">
                    {isHindi ? scheme.official_name_hi : scheme.official_name_en}
                  </h3>
                  <div className="text-xs text-muted mt-0.5">
                    {isHindi ? scheme.official_name_en : scheme.official_name_hi} • {scheme.department}
                  </div>

                  <p className="text-sm text-ink-950/80 mt-2 leading-relaxed">
                    {isHindi ? scheme.benefit_summary_hi : scheme.benefit_summary_en}
                  </p>

                  {/* Recommendation Reasoning & Ranking Factors */}
                  {scheme.recommendation_reason && (
                    <div className="mt-2.5 p-2.5 rounded-natural bg-[#F4F8F1]/80 backdrop-blur-xs border border-[#D5E2CE]/70 text-xs flex items-center justify-between gap-2">
                      <span className="text-forest-900 font-medium">{scheme.recommendation_reason}</span>
                      {scheme.ranking_score !== undefined && (
                        <span className="shrink-0 font-mono text-[11px] font-semibold text-leaf-700 bg-white/90 px-2 py-0.5 rounded border border-field-200">
                          {isHindi ? 'पारदर्शी स्कोर' : 'Score'}: {scheme.ranking_score.toFixed(0)}/100
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Card Action Controls */}
                <div className="flex sm:flex-col items-center sm:items-end justify-between gap-2 shrink-0 pt-2 sm:pt-0">
                  <button
                    type="button"
                    onClick={() => toggleSelectForPlan(scheme.scheme_code)}
                    className={`text-xs px-3 py-1.5 rounded-natural border font-medium flex items-center gap-1.5 transition-colors ${
                      isSelected
                        ? 'bg-forest-800 text-white border-forest-800'
                        : 'bg-paper-50 text-ink-950 border-appBorder hover:bg-paper-100'
                    }`}
                  >
                    <span>{isSelected ? t('results.removeFromPlan') : t('results.addToPlan')}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setExpandedScheme(isExpanded ? null : scheme.scheme_code)}
                    className="text-xs text-leaf-600 hover:text-forest-900 font-medium flex items-center gap-1 p-1"
                  >
                    <span>{isExpanded ? (isHindi ? 'नियम छुपाएं' : 'Hide Rules') : t('results.viewDetails')}</span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* Expandable Rule-Level Gap Analyzer */}
              {isExpanded && (
                <div className="mt-5 pt-4 border-t border-appBorder">
                  <div className="flex items-center justify-between mb-3 text-xs">
                    <span className="font-semibold text-forest-900 uppercase tracking-wider">
                      नियम-वार पात्रता विश्लेषण (Rule-Level Gap Analyzer)
                    </span>
                    <span className="text-muted">
                      सत्यापन तिथि: {new Date(scheme.verified_at).toLocaleDateString()}
                    </span>
                  </div>

                  <div className="space-y-2.5 mb-4">
                    {/* Passed Rules */}
                    {scheme.passed_rules.map(rule => (
                      <div
                        key={rule.rule_code}
                        className="p-3 rounded-natural bg-[#F3F7F0]/65 backdrop-blur-sm border border-[#D5E2CE]/70 text-xs flex items-start gap-2.5 shadow-2xs"
                      >
                        <CheckCircle2 className="w-4 h-4 text-brandSuccess shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <div className="font-semibold text-forest-900">
                            {isHindi ? rule.title_hi : rule.title_en}
                            <span className="ml-2 font-mono text-[10px] text-muted-dark font-normal">[{rule.rule_code}]</span>
                          </div>
                          <div className="text-muted-dark mt-0.5">{rule.reason}</div>
                          <div className="text-[11px] font-mono text-muted mt-1">स्रोत संदर्भ: {rule.citation}</div>
                        </div>
                        <StatusBadge status="PASS" size="sm" showIcon={false} />
                      </div>
                    ))}

                    {/* Unknown Rules */}
                    {scheme.unknown_rules.map(rule => (
                      <div
                        key={rule.rule_code}
                        className="p-3 rounded-natural bg-[#FCF6EB]/65 backdrop-blur-sm border border-[#F2DEB6]/70 text-xs flex items-start gap-2.5 shadow-2xs"
                      >
                        <HelpCircle className="w-4 h-4 text-brandWarning shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <div className="font-semibold text-[#825413]">
                            {isHindi ? rule.title_hi : rule.title_en}
                            <span className="ml-2 font-mono text-[10px] text-muted-dark font-normal">[{rule.rule_code}]</span>
                          </div>
                          <div className="text-muted-dark mt-0.5">{rule.reason}</div>
                          <div className="text-[11px] font-mono text-muted mt-1">स्रोत संदर्भ: {rule.citation}</div>
                        </div>
                        <StatusBadge status="UNKNOWN" size="sm" showIcon={false} />
                      </div>
                    ))}

                    {/* Failed Rules */}
                    {scheme.failed_rules.map(rule => (
                      <div
                        key={rule.rule_code}
                        className="p-3 rounded-natural bg-[#FBEBEA]/65 backdrop-blur-sm border border-[#F3C7C4]/70 text-xs flex items-start gap-2.5 shadow-2xs"
                      >
                        <XCircle className="w-4 h-4 text-brandDanger shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <div className="font-semibold text-brandDanger">
                            {isHindi ? rule.title_hi : rule.title_en}
                            <span className="ml-2 font-mono text-[10px] text-muted-dark font-normal">[{rule.rule_code}]</span>
                          </div>
                          <div className="text-muted-dark mt-0.5">{rule.reason}</div>
                          <div className="text-[11px] font-mono text-muted mt-1">स्रोत संदर्भ: {rule.citation}</div>
                        </div>
                        <StatusBadge status="FAIL" size="sm" showIcon={false} />
                      </div>
                    ))}
                  </div>

                  {/* Official Source Provenance Footer */}
                  <div className="p-3 rounded-natural bg-white/50 backdrop-blur-sm border border-white/50 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] text-ink-950">
                    <div>
                      <span className="font-semibold text-forest-900">आधिकारिक स्रोत:</span> {scheme.source_title} ({scheme.source_section})
                    </div>
                    <a
                      href={scheme.official_portal_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-forest-800 hover:underline font-bold shrink-0"
                    >
                      <span>पोर्टल खोलें</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {/* Multi-Scheme Convergence Modal */}
      {showConvergenceModal && (
        <div className="fixed inset-0 z-50 bg-ink-950/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-paper-50 border border-appBorder rounded-panel max-w-2xl w-full p-6 max-h-[85vh] overflow-y-auto shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-appBorder mb-4">
              <div>
                <h3 className="font-serif text-xl font-bold text-forest-900">
                  {t('results.convergenceTitle')}
                </h3>
                <p className="text-xs text-muted">
                  सरकारी गजट एवं विभागीय अधिसूचनाओं के आधार पर सह-अस्तित्व परिणाम
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowConvergenceModal(false)}
                className="text-muted hover:text-ink-950 p-1 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 mb-6">
              {convergencePairs.map((pair, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-natural border border-appBorder bg-paper-100 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-forest-900 text-sm">
                      {pair.scheme_code_a} ↔ {pair.scheme_code_b}
                    </span>
                    <StatusBadge status={pair.status} size="sm" />
                  </div>
                  <p className="text-ink-950 leading-relaxed">
                    {pair.evidence_text}
                  </p>
                  <div className="pt-2 border-t border-appBorder/60 flex flex-wrap justify-between text-[11px] text-muted">
                    <span>प्राधिकृत स्रोत: {pair.authoritative_source} ({pair.source_section})</span>
                    <span>समीक्षक: {pair.verified_by}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end">
              <Button variant="primary" onClick={() => setShowConvergenceModal(false)}>
                {isHindi ? 'समझ लिया / बंद करें' : 'Understood'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
