import React from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Shield, CheckCircle2, ArrowRight,
  Sparkles, AlertTriangle
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { AgriculturalFieldScene } from '../../components/illustrations/AgriculturalFieldScene';
import { StatusBadge } from '../../components/ui/StatusBadge';

interface LandingPageProps {
  onStartWizard: () => void;
  onOpenSchemes: () => void;
  onOpenAssistant: () => void;
  onOpenActionPlan?: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartWizard,
  onOpenSchemes,
  onOpenAssistant,
  onOpenActionPlan,
}) => {
  const { t, i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');
  const [cachedPlanNum, setCachedPlanNum] = React.useState<string | null>(null);

  React.useEffect(() => {
    try {
      const num = localStorage.getItem('yojanasaathi_latest_plan_number');
      if (num) {
        setCachedPlanNum(num);
      }
    } catch {
      // ignore
    }
  }, []);

  return (
    <div className="space-y-16 sm:space-y-24 pb-16">
      {/* Hero Section */}
      <section className="pt-8 sm:pt-12 px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
          {/* Left Column: Glass Headline Lens */}
          <div className="lg:col-span-6 space-y-5 bg-white/45 backdrop-blur-md p-6 sm:p-9 rounded-panel border border-white/50 shadow-[0_12px_40px_rgba(23,37,31,0.08),inset_0_1px_1px_rgba(255,255,255,0.7)]">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-field-100/80 border border-white/50 text-xs font-semibold text-forest-900 shadow-2xs backdrop-blur-sm">
              <span className="w-2 h-2 rounded-full bg-leaf-600 animate-pulse"></span>
              <span>{t('hero.badge')}</span>
            </div>

            <h1 className="font-serif text-3xl sm:text-4xl lg:text-[40px] font-bold text-forest-900 leading-[1.2] tracking-tight drop-shadow-2xs">
              {t('hero.headline')}
            </h1>

            <p className="text-sm sm:text-base text-ink-950 leading-relaxed font-sans max-w-xl font-medium">
              {t('hero.subheadline')}
            </p>

            {/* 5 Farmer-First Journey Milestones */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-xs text-forest-950 font-medium">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-forest-800 text-white text-[11px] font-bold flex items-center justify-center shrink-0 shadow-2xs">1</span>
                <span>{t('hero.benefit1')}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-forest-800 text-white text-[11px] font-bold flex items-center justify-center shrink-0 shadow-2xs">2</span>
                <span>{t('hero.benefit2')}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-forest-800 text-white text-[11px] font-bold flex items-center justify-center shrink-0 shadow-2xs">3</span>
                <span>{t('hero.benefit3')}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-forest-800 text-white text-[11px] font-bold flex items-center justify-center shrink-0 shadow-2xs">4</span>
                <span>{t('hero.benefit4')}</span>
              </div>
              <div className="flex items-center gap-2 sm:col-span-2">
                <span className="w-5 h-5 rounded-full bg-forest-800 text-white text-[11px] font-bold flex items-center justify-center shrink-0 shadow-2xs">5</span>
                <span>{t('hero.benefit5')}</span>
              </div>
            </div>

            {/* CTAs with non-wrapping buttons and balanced layout */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3.5 pt-3">
              <Button
                variant="primary"
                size="lg"
                rightIcon={<ArrowRight className="w-4 h-4 shrink-0" />}
                onClick={onStartWizard}
                className="whitespace-nowrap px-6 py-3 min-h-[46px] justify-center shadow-md font-semibold text-sm"
              >
                {t('hero.ctaStart')}
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={onOpenSchemes}
                className="bg-white/70 hover:bg-white/90 border border-white/70 text-forest-900 shadow-xs backdrop-blur-sm whitespace-nowrap px-6 py-3 min-h-[46px] justify-center font-semibold text-sm"
              >
                {t('hero.ctaSchemes')}
              </Button>
            </div>

            {/* Offline Recovered Action Plan Alert */}
            {cachedPlanNum && onOpenActionPlan && (
              <div className="p-3 bg-white/70 border border-forest-800/20 rounded-natural flex items-center justify-between gap-3 text-xs text-forest-900 shadow-2xs backdrop-blur-sm">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-leaf-600 animate-pulse" />
                  <span className="font-semibold">
                    {isHindi ? `सहेजी गई कार्य योजना (#${cachedPlanNum}) उपलब्ध है` : `Cached Offline Plan (#${cachedPlanNum}) available`}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={onOpenActionPlan}
                  className="px-3 py-1 bg-forest-800 text-white rounded font-medium hover:bg-forest-900 transition-colors shadow-2xs cursor-pointer"
                >
                  {isHindi ? 'योजना खोलें' : 'Open Plan'}
                </button>
              </div>
            )}

            {/* Trust disclaimer note */}
            <div className="pt-3 border-t border-white/40 text-xs text-ink-950 font-medium flex items-start gap-2">
              <Shield className="w-4 h-4 text-leaf-600 shrink-0 mt-0.5" />
              <span>{t('hero.trustBanner')}</span>
            </div>
          </div>

          {/* Right Column: UP Agro-Climatic Zones Infographic Card */}
          <div className="lg:col-span-6 flex items-center justify-center">
            <AgriculturalFieldScene />
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-10 bg-white/45 backdrop-blur-md p-6 rounded-panel border border-white/50 shadow-[0_4px_24px_rgba(23,37,31,0.05)]">
          <div className="text-xs uppercase font-bold tracking-wider text-leaf-600 mb-1">
            सरल एवं निष्पक्ष कार्यप्रणाली
          </div>
          <h2 className="font-serif text-2xl sm:text-3xl font-bold text-forest-900 drop-shadow-2xs">
            {t('howItWorks.title')}
          </h2>
          <p className="text-sm text-ink-950 font-medium mt-2">
            {t('howItWorks.subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 sm:gap-6">
          {[
            {
              num: '1',
              title: t('howItWorks.step1Title'),
              desc: t('howItWorks.step1Desc'),
              badge: 'Need Intake',
            },
            {
              num: '2',
              title: t('howItWorks.step2Title'),
              desc: t('howItWorks.step2Desc'),
              badge: 'Minimal Profile',
            },
            {
              num: '3',
              title: t('howItWorks.step3Title'),
              desc: t('howItWorks.step3Desc'),
              badge: '3-Valued Rules',
            },
            {
              num: '4',
              title: t('howItWorks.step4Title'),
              desc: t('howItWorks.step4Desc'),
              badge: 'Action Plan',
            },
          ].map(step => (
            <Card key={step.num} variant="surface" className="flex flex-col justify-between p-5">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="w-8 h-8 rounded-natural bg-forest-800 text-white font-serif font-bold text-base flex items-center justify-center shadow-xs">
                    {step.num}
                  </span>
                  <span className="text-[10px] font-mono uppercase text-forest-900 tracking-wide font-bold">
                    {step.badge}
                  </span>
                </div>
                <h3 className="text-base font-bold text-ink-950 font-serif mb-2">
                  {step.title}
                </h3>
                <p className="text-xs text-ink-950 leading-relaxed font-medium">
                  {step.desc}
                </p>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Product Proof & Capabilities Section */}
      <section className="px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="bg-white/45 backdrop-blur-md border border-white/50 rounded-panel p-6 sm:p-10 shadow-[0_12px_40px_rgba(23,37,31,0.06)]">
          <div className="max-w-2xl mb-8">
            <span className="text-xs font-bold uppercase tracking-wider text-leaf-600">
              वास्तविक कार्यप्रणाली का प्रमाण (Implemented Proof)
            </span>
            <h2 className="font-serif text-2xl sm:text-3xl font-bold text-forest-900 mt-1 drop-shadow-2xs">
              {isHindi ? 'पारदर्शिता जो विश्वास पैदा करती है' : 'Engineered for Radical Trust'}
            </h2>
            <p className="text-xs sm:text-sm text-ink-950 font-medium mt-2">
              हम कभी भी पात्रता का अनुमान नहीं लगाते। नीचे देखें कि हमारा तीन-मान्य नियम इंजन किस प्रकार काम करता है:
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Capability 1: Deterministic Logic */}
            <div className="p-4 rounded-natural bg-white/55 backdrop-blur-sm border border-white/50 shadow-2xs">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-forest-900 font-serif">1. निष्पक्ष पात्रता जाँच</span>
                <StatusBadge status="PASS" size="sm" />
              </div>
              <p className="text-xs text-ink-950 leading-relaxed mb-3 font-medium">
                खतौनी भूमि रकबा (2.0 एकड़ &ge; 0.01 एकड़ न्यूनतम सीमा)। सरकारी नियम संख्या PMK-2020 Sec 2 के तहत शर्त संतुष्ट।
              </p>
              <div className="text-[11px] font-mono text-leaf-600 font-bold">स्थिति: PASS (उत्तीर्ण)</div>
            </div>

            {/* Capability 2: Safe UNKNOWN Handling */}
            <div className="p-4 rounded-natural bg-white/55 backdrop-blur-sm border border-white/50 shadow-2xs">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-forest-900 font-serif">2. अज्ञात जानकारी का सुरक्षित व्यवहार</span>
                <StatusBadge status="UNKNOWN" size="sm" />
              </div>
              <p className="text-xs text-ink-950 leading-relaxed mb-3 font-medium">
                यदि किसान ने संस्थागत भूमि या सिंचाई स्रोत स्पष्ट नहीं किया, तो हम उसे पास नहीं मानते। यह UNKNOWN रहता है।
              </p>
              <div className="text-[11px] font-mono text-brandWarning font-bold">स्थिति: UNKNOWN (सत्यापन आवश्यक)</div>
            </div>

            {/* Capability 3: Multi-Scheme Compatibility */}
            <div className="p-4 rounded-natural bg-white/55 backdrop-blur-sm border border-white/50 shadow-2xs">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-forest-900 font-serif">3. बहु-योजना सह-अस्तित्व</span>
                <StatusBadge status="COMPATIBLE_CONFIRMED" size="sm" />
              </div>
              <p className="text-xs text-ink-950 leading-relaxed mb-3 font-medium">
                पीएम-किसान और फसल बीमा (PMFBY) दोनों का लाभ साथ लिया जा सकता है। भारत सरकार कार्यालय ज्ञापन 2021-Agri-09 द्वारा पुष्ट।
              </p>
              <div className="text-[11px] font-mono text-leaf-600 font-bold">स्थिति: COMPATIBLE_CONFIRMED</div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust & Limitations Section */}
      <section className="px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* What we help with */}
          <Card variant="surface" className="p-6">
            <h3 className="font-serif text-lg font-bold text-forest-900 mb-3 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-brandSuccess" />
              <span>{isHindi ? 'योजना साथी आपकी क्या मदद कर सकता है:' : 'What YojanaSaathi AI Can Do:'}</span>
            </h3>
            <ul className="space-y-2.5 text-xs text-ink-950 leading-relaxed font-medium">
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-leaf-600 mt-1.5 shrink-0" />
                <span>उत्तर प्रदेश के किसानों के लिए मान्य योजनाओं की पारदर्शी व निष्पक्ष पात्रता जाँचना।</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-leaf-600 mt-1.5 shrink-0" />
                <span>प्रत्येक शर्त का आधिकारिक गजट संदर्भ एवं समीक्षा तिथि स्पष्ट दिखाना।</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-leaf-600 mt-1.5 shrink-0" />
                <span>आवश्यक दस्तावेज़ों की चेकलिस्ट और आधिकारिक पोर्टल लिंक तैयार करना।</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-leaf-600 mt-1.5 shrink-0" />
                <span>अतिथि मोड में बिना पंजीकरण के सम्पूर्ण सुविधा उपलब्ध कराना।</span>
              </li>
            </ul>
          </Card>

          {/* Non-goals / What we do not do */}
          <Card variant="surface" className="p-6">
            <h3 className="font-serif text-lg font-bold text-brandDanger mb-3 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-brandDanger" />
              <span>{isHindi ? 'हम क्या नहीं करते (महत्वपूर्ण सीमाएं):' : 'Clear Boundaries & Non-Goals:'}</span>
            </h3>
            <ul className="space-y-2.5 text-xs text-ink-950 leading-relaxed font-medium">
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-brandDanger mt-1.5 shrink-0" />
                <span>हम सरकारी आवेदन सीधे जमा नहीं करते—यह कार्य आधिकारिक पोर्टल अथवा सीएससी द्वारा ही होता है।</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-brandDanger mt-1.5 shrink-0" />
                <span>हम आधार संख्या, बैंक खाता नंबर, ओटीपी या पहचान पत्र अपलोड नहीं मांगते।</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-brandDanger mt-1.5 shrink-0" />
                <span>हम अनुमोदन की काल्पनिक 'गारंटी' या 'स्वीकृति संभावना' कभी नहीं दर्शाते।</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-brandDanger mt-1.5 shrink-0" />
                <span>अंतिम वैधानिक निर्णय सक्षम सरकारी प्राधिकारी (तहसीलदार / जिला कृषि अधिकारी) का होता है।</span>
              </li>
            </ul>
          </Card>
        </div>
      </section>

      {/* Floating Grounded Assistant Banner */}
      <section className="px-4 sm:px-6 max-w-7xl mx-auto">
        <div className="p-6 rounded-panel bg-white/45 backdrop-blur-md border border-white/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-[0_8px_30px_rgba(23,37,31,0.06)]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-natural bg-forest-800 text-paper-50 flex items-center justify-center shrink-0 shadow-xs">
              <Sparkles className="w-5 h-5 text-field-100" />
            </div>
            <div>
              <h3 className="font-serif text-lg font-bold text-forest-900 drop-shadow-2xs">
                {isHindi ? 'किसी योजना के बारे में सवाल है?' : 'Have a Question About Any Scheme?'}
              </h3>
              <p className="text-xs text-ink-950 font-medium">
                {isHindi 
                  ? 'हमारे साक्ष्य-आधारित सहायक से पूछें। उत्तर केवल अनुमोदित सरकारी स्रोतों से दिए जाते हैं।' 
                  : 'Ask our grounded assistant. All answers are strictly retrieved from official gazetted records.'}
              </p>
            </div>
          </div>
          <Button variant="primary" onClick={onOpenAssistant}>
            {isHindi ? 'सहायक से प्रश्न पूछें' : 'Ask Grounded Assistant'}
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 sm:px-6 max-w-7xl mx-auto pt-8 border-t border-white/30 text-xs text-ink-950">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white/40 backdrop-blur-md p-4 rounded-subtle border border-white/40 shadow-2xs font-medium">
          <div className="flex items-center gap-2">
            <span className="font-serif font-bold text-forest-900">योजना साथी AI (YojanaSaathi)</span>
            <span>•</span>
            <span>Spark2Scale Hackathon 2026 • Track 5</span>
          </div>
          <div>
            उत्तर प्रदेश 75 जिलों हेतु किसान-प्रथम डिजिटल मार्गदर्शक
          </div>
        </div>
      </footer>
    </div>
  );
};
