import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Sprout, Droplets, Shield, CreditCard, Wrench, HeartHandshake,
  HelpCircle, ChevronRight, ChevronLeft, Check, Sparkles
} from 'lucide-react';
import { UP_DISTRICTS } from '../../data/upDistricts';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import type { FarmerProfileInput } from '../../services/api';

interface WizardProps {
  onComplete: (statedNeeds: string[], profile: FarmerProfileInput) => void;
  onCancel: () => void;
}

const NEED_OPTIONS = [
  { id: 'income_support', labelHi: 'सीधी आर्थिक सहायता (सम्मान निधि)', labelEn: 'Direct Income Support', icon: Sprout },
  { id: 'crop_insurance', labelHi: 'फसल नुकसान सुरक्षा (बीमा)', labelEn: 'Crop Loss Insurance', icon: Shield },
  { id: 'irrigation', labelHi: 'ड्रिप व स्प्रिंकलर सिंचाई अनुदान', labelEn: 'Micro-Irrigation Subsidy', icon: Droplets },
  { id: 'credit', labelHi: 'सस्ता कृषि ऋण (किसान क्रेडिट कार्ड)', labelEn: 'Subsidized Agriculture Credit (KCC)', icon: CreditCard },
  { id: 'machinery', labelHi: 'कृषि यंत्र / ट्रैक्टर अनुदान', labelEn: 'Farm Machinery Subsidy', icon: Wrench },
  { id: 'social_security', labelHi: 'कृषक दुर्घटना कल्याण / सामाजिक सुरक्षा', labelEn: 'Accident Relief & Social Security', icon: HeartHandshake },
];

export const FarmerIntakeWizard: React.FC<WizardProps> = ({ onComplete, onCancel }) => {
  const { t, i18n } = useTranslation();
  const isHindi = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi');

  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [selectedNeeds, setSelectedNeeds] = useState<string[]>(['income_support', 'crop_insurance']);
  const [freeTextNeed, setFreeTextNeed] = useState('');

  // Profile fields
  const [district, setDistrict] = useState('Varanasi');
  const [landholding, setLandholding] = useState<string>('2.0');
  const [farmerCategory, setFarmerCategory] = useState<'MARGINAL' | 'SMALL' | 'MEDIUM_LARGE'>('MARGINAL');
  const [primaryCrops, setPrimaryCrops] = useState<string[]>(['wheat', 'paddy']);
  const [irrigationSource, setIrrigationSource] = useState<string>('tubeWell');
  const [socialCategory, setSocialCategory] = useState<string>('OBC');

  // Helper toggle for "Why do we ask this"
  const [showWhyDistrict, setShowWhyDistrict] = useState(false);
  const [showWhyLand, setShowWhyLand] = useState(false);

  const toggleNeed = (id: string) => {
    setSelectedNeeds(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const toggleCrop = (crop: string) => {
    setPrimaryCrops(prev =>
      prev.includes(crop) ? prev.filter(c => c !== crop) : [...prev, crop]
    );
  };

  const handleLandChange = (val: string) => {
    setLandholding(val);
    const num = parseFloat(val);
    if (!isNaN(num)) {
      if (num <= 2.5) setFarmerCategory('MARGINAL');
      else if (num <= 5.0) setFarmerCategory('SMALL');
      else setFarmerCategory('MEDIUM_LARGE');
    }
  };

  const handleSubmit = () => {
    const parsedLand = landholding ? parseFloat(landholding) : null;
    const profile: FarmerProfileInput = {
      district,
      landholding_acres: isNaN(parsedLand as number) ? null : parsedLand,
      farmer_category: farmerCategory,
      primary_crops: primaryCrops,
      irrigation_source: irrigationSource,
      social_category: socialCategory,
      is_temporary: true,
    };
    onComplete(selectedNeeds, profile);
  };

  return (
    <div className="max-w-3xl mx-auto py-6 px-4">
      {/* Wizard Progress Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-xs font-medium text-muted mb-2">
          <span className={step >= 1 ? 'text-forest-800 font-semibold' : ''}>
            1. {t('profileWizard.stepNeed')}
          </span>
          <span className="w-8 h-px bg-appBorder" />
          <span className={step >= 2 ? 'text-forest-800 font-semibold' : ''}>
            2. {t('profileWizard.stepProfile')}
          </span>
          <span className="w-8 h-px bg-appBorder" />
          <span className={step === 3 ? 'text-forest-800 font-semibold' : ''}>
            3. {t('profileWizard.stepReview')}
          </span>
        </div>
        <div className="w-full bg-paper-100 h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-forest-800 h-full transition-all duration-300 ease-out"
            style={{ width: step === 1 ? '33.3%' : step === 2 ? '66.6%' : '100%' }}
          />
        </div>
      </div>

      {/* Step 1: Farming Needs */}
      {step === 1 && (
        <Card variant="surface" className="border-appBorder">
          <div className="mb-6">
            <h2 className="font-serif text-xl sm:text-2xl text-forest-900 font-bold mb-1">
              {isHindi ? 'आपको किस प्रकार की सरकारी सहायता की आवश्यकता है?' : 'What kind of support does your farm need?'}
            </h2>
            <p className="text-sm text-muted">
              {isHindi 
                ? 'एक या एक से अधिक विकल्प चुनें। हम केवल वही योजनाएँ दिखाएंगे जो आपकी ज़रूरत से संबंधित हैं।' 
                : 'Select one or more needs. We will surface official schemes specifically aligned with your goals.'}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
            {NEED_OPTIONS.map(opt => {
              const Icon = opt.icon;
              const isSelected = selectedNeeds.includes(opt.id);
              return (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => toggleNeed(opt.id)}
                  className={`flex items-start gap-3 p-4 rounded-subtle border text-left transition-all ${
                    isSelected
                      ? 'border-forest-800 bg-field-100/90 text-forest-900 shadow-xs backdrop-blur-md'
                      : 'border-white/60 bg-white/75 hover:bg-white/95 text-ink-950 backdrop-blur-md shadow-2xs'
                  }`}
                >
                  <div className={`p-2 rounded-natural shrink-0 ${isSelected ? 'bg-forest-800 text-paper-50' : 'bg-field-100 text-forest-800'}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold">{isHindi ? opt.labelHi : opt.labelEn}</div>
                    <div className="text-xs text-muted-dark">{isHindi ? opt.labelEn : opt.labelHi}</div>
                  </div>
                  <div className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5 ${
                    isSelected ? 'bg-forest-800 border-forest-800 text-white' : 'border-appBorder bg-paper-50'
                  }`}>
                    {isSelected && <Check className="w-3.5 h-3.5" />}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Optional free-text need */}
          <div className="mb-6">
            <label className="block text-xs font-semibold text-muted-dark uppercase tracking-wider mb-1.5">
              {isHindi ? 'अन्य कोई विशिष्ट आवश्यकता? (वैकल्पिक)' : 'Any other specific farming need? (Optional)'}
            </label>
            <input
              type="text"
              value={freeTextNeed}
              onChange={e => setFreeTextNeed(e.target.value)}
              placeholder={isHindi ? 'उदा. सोलर पंप, तारबंदी, जैविक खाद...' : 'e.g. solar pump, organic fertilizer...'}
              className="w-full px-3.5 py-2.5 rounded-subtle border border-appBorder bg-white/95 text-sm focus:border-forest-800 focus:outline-none shadow-2xs"
            />
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-appBorder">
            <Button variant="subtle" onClick={onCancel}>
              {isHindi ? 'रद्द करें' : 'Cancel'}
            </Button>
            <Button
              variant="primary"
              disabled={selectedNeeds.length === 0}
              rightIcon={<ChevronRight className="w-4 h-4" />}
              onClick={() => setStep(2)}
            >
              {isHindi ? 'अगला: खेती विवरण' : 'Next: Farm Profile'}
            </Button>
          </div>
        </Card>
      )}

      {/* Step 2: Minimum Required Profile */}
      {step === 2 && (
        <Card variant="surface" className="border-appBorder">
          <div className="mb-6">
            <h2 className="font-serif text-xl sm:text-2xl text-forest-900 font-bold mb-1">
              {isHindi ? 'न्यूनतम कृषि प्रोफ़ाइल दर्ज करें' : 'Confirm Your Farming Profile'}
            </h2>
            <p className="text-sm text-muted">
              {isHindi
                ? 'हम केवल वही जानकारी पूछते हैं जो सरकारी नियमों द्वारा पात्रता तय करने के लिए आवश्यक है।'
                : 'We strictly request fields required by statutory eligibility rules. No Aadhaar or bank details are collected.'}
            </p>
          </div>

          <div className="space-y-5">
            {/* District */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-sm font-semibold text-ink-950">
                  {t('profileWizard.districtLabel')} <span className="text-brandDanger">*</span>
                </label>
                <button
                  type="button"
                  onClick={() => setShowWhyDistrict(!showWhyDistrict)}
                  className="text-xs text-leaf-600 hover:text-forest-800 flex items-center gap-1 font-medium"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>{t('profileWizard.whyWeAsk')}</span>
                </button>
              </div>
              {showWhyDistrict && (
                <div className="p-3 mb-2 rounded-subtle bg-field-100 border border-field-200 text-xs text-forest-900 leading-relaxed">
                  {t('profileWizard.whyDistrictText')}
                </div>
              )}
              <select
                value={district}
                onChange={e => setDistrict(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-subtle border border-white/50 bg-white/70 backdrop-blur-md text-sm text-ink-950 font-medium focus:border-forest-800 focus:outline-none shadow-2xs"
              >
                {UP_DISTRICTS.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            {/* Landholding */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-sm font-semibold text-ink-950">
                  {t('profileWizard.landHoldingLabel')} <span className="text-brandDanger">*</span>
                </label>
                <button
                  type="button"
                  onClick={() => setShowWhyLand(!showWhyLand)}
                  className="text-xs text-leaf-600 hover:text-forest-800 flex items-center gap-1 font-medium"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>{t('profileWizard.whyWeAsk')}</span>
                </button>
              </div>
              {showWhyLand && (
                <div className="p-3 mb-2 rounded-subtle bg-field-100 border border-field-200 text-xs text-forest-900 leading-relaxed">
                  {t('profileWizard.whyLandText')}
                </div>
              )}
              <div className="flex gap-3">
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={landholding}
                  onChange={e => handleLandChange(e.target.value)}
                  placeholder="उदा. 2.0 एकड़"
                  className="flex-1 px-3.5 py-2.5 rounded-subtle border border-white/50 bg-white/70 backdrop-blur-md text-sm text-ink-950 font-medium focus:border-forest-800 focus:outline-none shadow-2xs"
                />
                <button
                  type="button"
                  onClick={() => handleLandChange('')}
                  className="text-xs px-3 py-2 border border-white/50 rounded-subtle bg-white/60 backdrop-blur-md text-forest-900 font-medium hover:bg-white/80 shadow-2xs"
                >
                  {t('profileWizard.preferNotToSay')}
                </button>
              </div>
              <p className="text-xs text-muted mt-1">
                {t('profileWizard.landHoldingHelp')} • वर्तमान श्रेणी: <span className="font-semibold text-forest-800">{farmerCategory}</span>
              </p>
            </div>

            {/* Primary Crops */}
            <div>
              <label className="block text-sm font-semibold text-ink-950 mb-1.5">
                {t('profileWizard.cropLabel')}
              </label>
              <div className="flex flex-wrap gap-2">
                {[
                  { id: 'wheat', label: t('profileWizard.wheat') },
                  { id: 'paddy', label: t('profileWizard.paddy') },
                  { id: 'sugarcane', label: t('profileWizard.sugarcane') },
                  { id: 'pulses', label: t('profileWizard.pulses') },
                  { id: 'vegetables', label: t('profileWizard.vegetables') },
                ].map(c => {
                  const active = primaryCrops.includes(c.id);
                  return (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => toggleCrop(c.id)}
                      className={`text-xs px-3 py-2 rounded-natural border transition-all ${
                        active
                          ? 'bg-forest-800 text-paper-50 border-forest-800 font-semibold shadow-xs'
                          : 'bg-white/60 text-ink-950 border-white/50 hover:bg-white/85 backdrop-blur-sm'
                      }`}
                    >
                      {active && '✓ '}
                      {c.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Irrigation Source */}
            <div>
              <label className="block text-sm font-semibold text-ink-950 mb-1.5">
                {t('profileWizard.irrigationSourceLabel')}
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                {[
                  { id: 'tubeWell', label: t('profileWizard.tubeWell') },
                  { id: 'canal', label: t('profileWizard.canal') },
                  { id: 'rainfed', label: t('profileWizard.rainfed') },
                ].map(irr => (
                  <button
                    key={irr.id}
                    type="button"
                    onClick={() => setIrrigationSource(irr.id)}
                    className={`p-2.5 rounded-natural border text-left transition-all ${
                      irrigationSource === irr.id
                        ? 'bg-field-100/80 border-forest-800 text-forest-900 font-bold shadow-xs backdrop-blur-md'
                        : 'bg-white/60 border-white/50 text-ink-950 hover:bg-white/85 backdrop-blur-sm'
                    }`}
                  >
                    {irr.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Social Category */}
            <div>
              <label className="block text-sm font-semibold text-ink-950 mb-1.5">
                {t('profileWizard.casteCategoryLabel')}
              </label>
              <div className="flex gap-2">
                {[
                  { id: 'GENERAL', label: t('profileWizard.general') },
                  { id: 'OBC', label: t('profileWizard.obc') },
                  { id: 'SC_ST', label: t('profileWizard.sc_st') },
                ].map(cat => (
                  <button
                    key={cat.id}
                    type="button"
                    onClick={() => setSocialCategory(cat.id)}
                    className={`text-xs px-3.5 py-2 rounded-natural border transition-all ${
                      socialCategory === cat.id
                        ? 'bg-forest-800 text-paper-50 border-forest-800 font-semibold shadow-xs'
                        : 'bg-white/60 text-ink-950 border-white/50 hover:bg-white/85 backdrop-blur-sm'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-6 border-t border-appBorder mt-6">
            <Button variant="secondary" leftIcon={<ChevronLeft className="w-4 h-4" />} onClick={() => setStep(1)}>
              {isHindi ? 'पीछे' : 'Back'}
            </Button>
            <Button
              variant="primary"
              rightIcon={<ChevronRight className="w-4 h-4" />}
              onClick={() => setStep(3)}
            >
              {isHindi ? 'समीक्षा एवं पुष्टि' : 'Review & Confirm'}
            </Button>
          </div>
        </Card>
      )}

      {/* Step 3: Review and Confirm */}
      {step === 3 && (
        <Card variant="surface" className="border-appBorder">
          <div className="mb-6">
            <h2 className="font-serif text-xl sm:text-2xl text-forest-900 font-bold mb-1">
              {isHindi ? 'विवरण की पुष्टि करें' : 'Confirm Stated Information'}
            </h2>
            <p className="text-sm text-muted">
              {isHindi
                ? 'पात्रता की पारदर्शी जाँच से पूर्व दर्ज किए गए विवरण का मिलान करें।'
                : 'Review your attributes before executing the deterministic eligibility rules engine.'}
            </p>
          </div>

          <div className="bg-white/40 backdrop-blur-md border border-white/40 rounded-natural p-4 space-y-3 mb-6 text-sm shadow-xs">
            <div className="flex justify-between py-1 border-b border-white/30">
              <span className="text-ink-950 font-medium">{isHindi ? 'राज्य / जिला:' : 'State / District:'}</span>
              <span className="font-semibold text-forest-900">उत्तर प्रदेश, {district}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-white/30">
              <span className="text-ink-950 font-medium">{isHindi ? 'कृषि भूमि (रकबा):' : 'Landholding:'}</span>
              <span className="font-semibold text-forest-900">
                {landholding ? `${landholding} एकड़ (${farmerCategory})` : 'अज्ञात / Unconfirmed'}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-white/30">
              <span className="text-ink-950 font-medium">{isHindi ? 'फसलें:' : 'Crops Cultivated:'}</span>
              <span className="font-semibold text-forest-900">{primaryCrops.join(', ') || 'सामान्य'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-white/30">
              <span className="text-ink-950 font-medium">{isHindi ? 'सिंचाई व्यवस्था:' : 'Irrigation Source:'}</span>
              <span className="font-semibold text-forest-900">{irrigationSource}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-ink-950 font-medium">{isHindi ? 'सामाजिक वर्ग:' : 'Category:'}</span>
              <span className="font-semibold text-forest-900">{socialCategory}</span>
            </div>
          </div>

          <div className="p-3.5 rounded-subtle bg-field-100/60 backdrop-blur-md border border-white/40 text-xs text-forest-900 leading-relaxed mb-6 flex items-start gap-2 shadow-2xs">
            <Sparkles className="w-4 h-4 text-leaf-600 shrink-0 mt-0.5" />
            <span>
              {isHindi
                ? 'नियम इंजन सीधे सरकारी दिशा-निर्देशों से प्रत्येक शर्त (पास, फेल या अज्ञात) की गणना करेगा। कोई अनुमान या काल्पनिक पात्रता नहीं।'
                : 'The rules engine will evaluate statutory conditions deterministically. Missing data remains UNKNOWN rather than assumed.'}
            </span>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-appBorder">
            <Button variant="secondary" leftIcon={<ChevronLeft className="w-4 h-4" />} onClick={() => setStep(2)}>
              {isHindi ? 'सुधारें' : 'Edit Info'}
            </Button>
            <Button
              variant="primary"
              size="lg"
              rightIcon={<Check className="w-4 h-4" />}
              onClick={handleSubmit}
            >
              {t('profileWizard.confirmProfileBtn')}
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};
