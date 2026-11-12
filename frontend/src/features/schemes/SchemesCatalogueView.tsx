import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ExternalLink } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { api } from '../../services/api';

export const SchemesCatalogueView: React.FC<{ onStartWizard: () => void; onBack: () => void }> = ({
  onStartWizard,
  onBack,
}) => {
  const { i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [schemes, setSchemes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSchemes()
      .then(data => {
        setSchemes(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="max-w-5xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between gap-4 p-6 rounded-panel bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_30px_rgba(23,37,31,0.08)] mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-field-100 text-forest-800 border border-field-200">
              उत्तर प्रदेश विशेष • 6 सत्यापित योजनाएँ
            </span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-forest-900">
            {isHindi ? 'सत्यापित सरकारी योजना पंजीका' : 'Verified Government Schemes Catalogue'}
          </h1>
          <p className="text-xs sm:text-sm text-muted mt-1">
            प्रत्येक योजना का विवरण सीधे सरकारी अधिसूचना एवं परिचालन मार्गदर्शिका से संकलित है।
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={onBack} className="bg-white/80 hover:bg-white border-white/80 shadow-2xs">
            {isHindi ? 'मुख्य पृष्ठ' : 'Home'}
          </Button>
          <Button variant="primary" size="sm" onClick={onStartWizard}>
            {isHindi ? 'पात्रता जाँचें' : 'Check Eligibility'}
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-sm text-muted">डेटा लोड हो रहा है...</div>
      ) : (
        <div className="space-y-4">
          {schemes.map(s => (
            <Card key={s.scheme_code} variant="surface" className="border-appBorder p-5">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-2">
                <div>
                  <div className="flex items-center gap-2 mb-1 text-xs">
                    <span className="font-mono font-bold px-1.5 py-0.5 bg-paper-50 rounded border border-appBorder text-forest-900">
                      {s.scheme_code}
                    </span>
                    <span className="text-muted">{s.level === 'CENTRAL' ? 'केंद्रीय योजना' : 'उत्तर प्रदेश राज्य योजना'}</span>
                    <span>•</span>
                    <span className="text-muted">{s.benefit_type}</span>
                  </div>
                  <h3 className="text-lg font-bold text-ink-950 font-serif">
                    {isHindi ? s.official_name_hi : s.official_name_en}
                  </h3>
                  <div className="text-xs text-muted mt-0.5">{s.department}</div>
                </div>

                <a
                  href={s.official_portal_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-forest-800 hover:underline font-semibold shrink-0"
                >
                  <span>आधिकारिक पोर्टल</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              <p className="text-xs sm:text-sm text-ink-950/80 leading-relaxed mb-4">
                {isHindi ? s.benefit_summary_hi : s.benefit_summary_en}
              </p>

              <div className="p-3 rounded bg-paper-50 border border-appBorder text-xs text-muted flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <span className="font-semibold text-ink-950">सत्यापित स्रोत:</span> {s.source_title} ({s.source_section})
                </div>
                <div className="font-mono text-[11px] text-muted-dark">
                  समीक्षा तिथि: {new Date(s.verified_at).toLocaleDateString()}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
