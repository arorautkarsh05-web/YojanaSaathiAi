import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Send, Bot, ShieldCheck, X, Sparkles, Globe, AlertTriangle, ArrowRight } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { api } from '../../services/api';
import type { ConversationalIntakeResponse, FarmerProfileInput } from '../../services/api';

interface GroundedAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStartWithProfile?: (profile: FarmerProfileInput, needs: string[]) => void;
}

type SupportedLanguage = 'hi' | 'en' | 'hinglish' | 'pa';

interface LanguageOption {
  id: SupportedLanguage;
  label: string;
  nativeLabel: string;
  flag: string;
}

const LANGUAGES: LanguageOption[] = [
  { id: 'hi', label: 'Hindi', nativeLabel: 'हिन्दी', flag: '🇮🇳' },
  { id: 'en', label: 'English', nativeLabel: 'English', flag: '🌐' },
  { id: 'hinglish', label: 'Hinglish', nativeLabel: 'हिंग्लिश', flag: '💬' },
  { id: 'pa', label: 'Punjabi', nativeLabel: 'ਪੰਜਾਬੀ', flag: '🌾' },
];

const WELCOME_MESSAGES: Record<SupportedLanguage, string> = {
  hi: 'नमस्ते किसान साथी! आप उत्तर प्रदेश में पीएम-किसान, फसल बीमा, ड्रिप सिंचाई या केसीसी के नियमों और दस्तावेज़ों के बारे में पूछ सकते हैं। हमारे सभी उत्तर आधिकारिक सरकारी गजट से प्रमाणित हैं।',
  en: 'Welcome Farmer! You can ask any question about PM-KISAN, PMFBY Crop Insurance, Micro-Irrigation (Drip/Sprinkler), KCC, or Accident Relief in Uttar Pradesh. All answers are strictly grounded in gazetted records.',
  hinglish: 'Namaste Kisan Bhai/Behen! Aap UP me PM-KISAN, Fasal Bima, KCC Loan ya Drip Sinchai ke bare me koi bhi sawal pooch sakte hain. Sabhi jawab 100% official sarkari gazette se verified hain.',
  pa: 'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਵੀਰੋ/ਭੈਣੋ! ਤੁਸੀਂ ਉੱਤਰ ਪ੍ਰਦੇਸ਼ ਵਿੱਚ ਪੀ.ਐਮ-ਕਿਸਾਨ, ਫ਼ਸਲ ਬੀਮਾ, ਡ੍ਰਿਪ ਸਿੰਚਾਈ ਜਾਂ ਕੇ.ਸੀ.ਸੀ. ਦੇ ਨਿਯਮਾਂ ਤੇ ਕਾਗਜ਼ਾਂ ਬਾਰੇ ਪੁੱਛ ਸਕਦੇ ਹੋ। ਸਾਰੇ ਜਵਾਬ ਸਰਕਾਰੀ ਰਿਕਾਰਡ ਤੋਂ ਪ੍ਰਮਾਣਿਤ ਹਨ।'
};

const SUGGESTED_QUERIES: Record<SupportedLanguage, string[]> = {
  hi: [
    'मेरे पास दो बीघा जमीन है, गेहूं उगाता हूं, सिंचाई चाहिए',
    'पीएम-किसान में ₹6000 की किस्त कब मिलती है?',
    'फसल नुकसान होने पर 72 घंटे में बीमा दावा कैसे करें?',
    'केसीसी लोन पर 4% ब्याज के क्या नियम हैं?',
    'ड्रिप सिंचाई पर 55% सब्सिडी के लिए क्या कागज़ चाहिए?',
    'दुर्घटना कल्याण योजना में ₹5 लाख की सहायता कैसे मिलती है?'
  ],
  en: [
    'I have 2 bigha land and grow wheat, need irrigation help',
    'What are the eligibility rules for PM-KISAN?',
    'How to intimate crop damage within 72 hrs under PMFBY?',
    'What is the interest rate and limit for KCC in UP?',
    'What subsidy is available for drip irrigation?',
    'Can I combine PM-KISAN, KCC, and crop insurance?'
  ],
  hinglish: [
    'PM-KISAN me ₹6000 kab milte hain aur eKYC kaise kare?',
    'Fasal kharab ho jaye to PMFBY claim kaise kare?',
    'KCC loan kitne percent par milta hai aur documents kya chahiye?',
    'Drip irrigation par 55% subsidy kaise milegi?',
    'Krishak Durghatna yojana me ₹5 lakh kab milte hain?',
    'Kya PM-KISAN aur KCC dono ek saath le sakte hain?'
  ],
  pa: [
    'ਪੀ.ਐਮ-ਕਿਸਾਨ ਯੋਜਨਾ ਵਿੱਚ ₹6000 ਦੀ ਕਿਸ਼ਤ ਕਦੋਂ ਮਿਲਦੀ ਹੈ?',
    'ਫ਼ਸਲ ਖ਼ਰਾਬ ਹੋਣ \'ਤੇ 72 ਘੰਟਿਆਂ ਵਿੱਚ ਬੀਮਾ ਦਾਅਵਾ ਕਿਵੇਂ ਕਰੀਏ?',
    'ਕੇਸੀਸੀ ਕਰਜ਼ੇ ਉੱਤੇ 4% ਵਿਆਜ ਦਰ ਦੇ ਕੀ ਨਿਯਮ ਹਨ?',
    'ਡ੍ਰਿਪ ਸਿੰਚਾਈ ਉੱਤੇ 55% ਸਬਸਿਡੀ ਲਈ ਕਿਹੜੇ ਕਾਗਜ਼ ਚਾਹੀਦੇ ਹਨ?',
    'ਮੁੱਖ ਮੰਤਰੀ ਕਿਸਾਨ ਦੁਰਘਟਨਾ ਕਲਿਆਣ ਯੋਜਨਾ ਵਿੱਚ ਕੀ ਲਾਭ ਮਿਲਦਾ ਹੈ?',
    'ਕੀ ਇੱਕ ਤੋਂ ਵੱਧ ਸਕੀਮਾਂ ਦਾ ਲਾਭ ਇਕੱਠਾ ਲਿਆ ਜਾ ਸਕਦਾ ਹੈ?'
  ]
};

const PLACEHOLDERS: Record<SupportedLanguage, string> = {
  hi: 'उदा. पीएम-किसान के नियम या फसल बीमा की समय सीमा क्या है?',
  en: 'e.g. What are the rules for PM-KISAN or crop insurance deadline?',
  hinglish: 'e.g. KCC loan lene ke liye kaun se kagaz lagenge?',
  pa: 'ਜਿਵੇਂ ਕਿ: ਪੀ.ਐਮ-ਕਿਸਾਨ ਲਈ ਯੋਗਤਾ ਨਿਯਮ ਕੀ ਹਨ?'
};

export const GroundedAssistantModal: React.FC<GroundedAssistantModalProps> = ({ isOpen, onClose, onStartWithProfile }) => {
  const { i18n } = useTranslation();
  const defaultLang: SupportedLanguage = (i18n.resolvedLanguage || i18n.language || 'hi').startsWith('hi') ? 'hi' : 'en';

  const [selectedLanguage, setSelectedLanguage] = useState<SupportedLanguage>(defaultLang);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Array<{
    sender: 'user' | 'assistant';
    text: string;
    sourceTitle?: string;
    authority?: string;
    section?: string;
    verifiedAt?: string;
    canVerify?: boolean;
    language?: SupportedLanguage;
    intakeResponse?: ConversationalIntakeResponse;
  }>>([
    {
      sender: 'assistant',
      text: WELCOME_MESSAGES[defaultLang],
      language: defaultLang
    }
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  if (!isOpen) return null;

  const handleLanguageChange = (newLang: SupportedLanguage) => {
    if (newLang === selectedLanguage) return;
    setSelectedLanguage(newLang);
    // Add assistant announcement of language switch
    setMessages(prev => [
      ...prev,
      {
        sender: 'assistant',
        text: WELCOME_MESSAGES[newLang],
        language: newLang
      }
    ]);
  };

  const handleSend = async (queryText?: string) => {
    const textToQuery = (queryText || inputQuery).trim();
    if (!textToQuery || isLoading) return;

    setInputQuery('');
    setMessages(prev => [...prev, { sender: 'user', text: textToQuery }]);
    setIsLoading(true);

    const isIntake = /बीघा|bigha|एकड़|acre|हेक्टेयर|hectare|खेती|जमीन|सिंचाई|loan|कर्ज|केसीसी|फसल|kheti|jamin|crops/i.test(textToQuery);

    try {
      if (isIntake) {
        const res = await api.naturalLanguageIntake(textToQuery, selectedLanguage);
        setMessages(prev => [
          ...prev,
          {
            sender: 'assistant',
            text: res.summary_message,
            language: selectedLanguage,
            intakeResponse: res
          }
        ]);
      } else {
        const res = await api.queryAssistant(textToQuery, undefined, selectedLanguage);
        setMessages(prev => [
          ...prev,
          {
            sender: 'assistant',
            text: res.answer,
            sourceTitle: res.source_title,
            authority: res.authority,
            section: res.section,
            verifiedAt: res.verified_at,
            canVerify: res.can_verify,
            language: selectedLanguage
          }
        ]);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'assistant',
          text: selectedLanguage === 'hi'
            ? 'क्षमा करें, सर्वर से संपर्क नहीं हो सका। कृपया बाद में प्रयास करें।'
            : selectedLanguage === 'pa'
            ? 'ਮੁਆਫ਼ ਕਰਨਾ, ਸਰਵਰ ਨਾਲ ਸੰਪਰਕ ਨਹੀਂ ਹੋ ਸਕਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਥੋੜ੍ਹੀ ਦੇਰ ਬਾਅਦ ਕੋਸ਼ਿਸ਼ ਕਰੋ।'
            : selectedLanguage === 'hinglish'
            ? 'Server se contact nahi ho paya. Kripya thodi der baad dobara try karein.'
            : 'Unable to reach assistant service. Please retry shortly.',
          canVerify: false,
          language: selectedLanguage
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-ink-950/45 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4 animate-fadeIn">
      <div className="bg-white/90 backdrop-blur-xl border border-white/80 rounded-panel max-w-2xl w-full h-[640px] flex flex-col shadow-[0_20px_60px_rgba(23,37,31,0.22),inset_0_1px_1px_rgba(255,255,255,0.9)] overflow-hidden text-ink-950">
        
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-ink-950/10 bg-white/50 backdrop-blur-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-natural bg-forest-800 text-paper-50 flex items-center justify-center shadow-xs">
              <Bot className="w-5 h-5 text-field-100" />
            </div>
            <div>
              <div className="text-sm font-bold text-forest-900 font-serif flex items-center gap-2">
                <span>
                  {selectedLanguage === 'hi' ? 'सत्यापित योजना सहायक' :
                   selectedLanguage === 'pa' ? 'ਪ੍ਰਮਾਣਿਤ ਯੋਜਨਾ ਸਹਾਇਕ' :
                   selectedLanguage === 'hinglish' ? 'Verified Scheme Assistant' :
                   'Grounded Scheme Assistant'}
                </span>
                <span className="text-[10px] font-sans px-1.5 py-0.5 rounded-full bg-forest-100 text-forest-800 font-medium">
                  UP Gazette Verified
                </span>
              </div>
              <div className="text-[11px] text-ink-950/70">
                {selectedLanguage === 'hi' ? 'केवल सरकारी गजट व नियमों से प्रमाणित जानकारी' :
                 selectedLanguage === 'pa' ? 'ਸਿਰਫ਼ ਸਰਕਾਰੀ ਗਜ਼ਟ ਅਤੇ ਨਿਯਮਾਂ ਤੋਂ ਪ੍ਰਮਾਣਿਤ ਜਾਣਕਾਰੀ' :
                 selectedLanguage === 'hinglish' ? 'Sirf sarkari gazette aur rules se verified answer' :
                 'Strictly grounded in official gazettes and statutory rules'}
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-full text-ink-950/60 hover:text-ink-950 hover:bg-white/60 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Language Selection Bar (Prominent Upfront Option) */}
        <div className="px-5 py-2.5 bg-paper-100/70 border-b border-ink-950/10 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-forest-900">
            <Globe className="w-3.5 h-3.5 text-forest-700" />
            <span>अपनी भाषा चुनें / Choose Language:</span>
          </div>
          <div className="flex items-center gap-1.5">
            {LANGUAGES.map((lang) => {
              const isActive = selectedLanguage === lang.id;
              return (
                <button
                  key={lang.id}
                  type="button"
                  onClick={() => handleLanguageChange(lang.id)}
                  className={`px-2.5 py-1 rounded-subtle text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer ${
                    isActive
                      ? 'bg-forest-800 text-paper-50 shadow-xs ring-1 ring-forest-900'
                      : 'bg-white/70 text-ink-950/80 hover:bg-white hover:text-ink-950 border border-white/60'
                  }`}
                >
                  <span>{lang.flag}</span>
                  <span>{lang.nativeLabel}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-paper-50/40">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[88%] rounded-natural p-3.5 text-xs leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-forest-800 text-paper-50 shadow-xs'
                    : 'bg-white/85 text-ink-950 border border-white/90 shadow-xs backdrop-blur-sm'
                }`}
              >
                <div className="whitespace-pre-line font-sans">{msg.text}</div>

                {/* Regional Bigha Ambiguity Notice Banner */}
                {msg.intakeResponse && msg.intakeResponse.ambiguities.length > 0 && (
                  <div className="mt-2.5 p-2.5 rounded-subtle bg-amber-50/90 border border-amber-200/80 text-[11px] text-amber-950">
                    <div className="flex items-center gap-1.5 font-semibold text-amber-900 mb-1">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                      <span>{selectedLanguage === 'hi' ? 'क्षेत्रीय इकाई स्पष्टीकरण (Regional Unit Notice)' : 'Regional Unit Ambiguity Notice'}</span>
                    </div>
                    <div className="whitespace-pre-line text-ink-950/85">
                      {selectedLanguage === 'hi'
                        ? msg.intakeResponse.ambiguities[0].clarification_prompt_hi
                        : msg.intakeResponse.ambiguities[0].clarification_prompt_en}
                    </div>
                  </div>
                )}

                {/* Follow-up question guidance */}
                {msg.intakeResponse && msg.intakeResponse.follow_up_questions_hi.length > 0 && !msg.intakeResponse.can_proceed_to_evaluation && (
                  <div className="mt-2 text-[11px] text-forest-900 space-y-1">
                    <div className="font-semibold text-forest-800">
                      {selectedLanguage === 'hi' ? 'अनुवर्ती प्रश्न (कृपया उत्तर दें):' : 'Follow-up questions:'}
                    </div>
                    {(selectedLanguage === 'hi' ? msg.intakeResponse.follow_up_questions_hi : msg.intakeResponse.follow_up_questions_en).map((q, qIdx) => (
                      <div key={qIdx} className="p-1.5 rounded bg-forest-50/70 border border-forest-200/60 text-forest-950">
                        {q}
                      </div>
                    ))}
                  </div>
                )}

                {/* Direct one-click eligibility evaluation trigger */}
                {msg.intakeResponse && msg.intakeResponse.structured_profile_candidate && onStartWithProfile && (
                  <div className="mt-3 pt-2.5 border-t border-ink-950/10">
                    <Button
                      type="button"
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        if (msg.intakeResponse?.structured_profile_candidate) {
                          onStartWithProfile(
                            msg.intakeResponse.structured_profile_candidate,
                            msg.intakeResponse.extracted_parameters.stated_needs
                          );
                        }
                      }}
                      rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                      className="w-full justify-center shadow-xs"
                    >
                      {selectedLanguage === 'hi'
                        ? 'इस जानकारी से पात्रता जाँचें (Evaluate Schemes Now)'
                        : 'Evaluate Schemes for this Profile'}
                    </Button>
                  </div>
                )}

                {/* Evidence Footer for Assistant Responses */}
                {msg.sourceTitle && (
                  <div className="mt-2.5 pt-2 border-t border-ink-950/10 text-[10.5px] text-ink-950/75 space-y-0.5">
                    <div className="font-semibold text-forest-900 flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5 text-leaf-600" />
                      <span>{msg.authority}</span>
                    </div>
                    <div>
                      <span className="font-medium text-forest-800">
                        {selectedLanguage === 'hi' ? 'सत्यापित स्रोत: ' :
                         selectedLanguage === 'pa' ? 'ਪ੍ਰਮਾਣਿਤ ਸਰੋਤ: ' :
                         selectedLanguage === 'hinglish' ? 'Verified Source: ' :
                         'Statutory Source: '}
                      </span>
                      {msg.sourceTitle} {msg.section && `(${msg.section})`}
                    </div>
                    {msg.verifiedAt && (
                      <div className="font-mono text-[9.5px] text-ink-950/60">
                        समीक्षा तिथि (Audit Date): {new Date(msg.verifiedAt).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-start">
              <div className="p-3 rounded-natural bg-white/85 border border-white/90 text-xs text-ink-950/80 flex items-center gap-2 backdrop-blur-sm shadow-xs">
                <span className="w-2.5 h-2.5 rounded-full bg-forest-800 animate-pulse" />
                <span>
                  {selectedLanguage === 'hi' ? 'सरकारी गजट व नियमों में सत्यापन जारी है...' :
                   selectedLanguage === 'pa' ? 'ਸਰਕਾਰੀ ਗਜ਼ਟ ਅਤੇ ਨਿਯਮਾਂ ਵਿੱਚ ਪੁਸ਼ਟੀ ਕੀਤੀ ਜਾ ਰਹੀ ਹੈ...' :
                   selectedLanguage === 'hinglish' ? 'Government rules aur gazette me check kiya ja raha hai...' :
                   'Verifying against published government records...'}
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompt Chips */}
        <div className="px-4 py-2 border-t border-ink-950/10 bg-white/40 backdrop-blur-sm overflow-x-auto">
          <div className="flex items-center gap-1.5 text-[10px] text-ink-950/60 mb-1.5 font-medium">
            <Sparkles className="w-3 h-3 text-golden-500" />
            <span>
              {selectedLanguage === 'hi' ? 'सुझाए गए प्रश्न (क्लिक करें):' :
               selectedLanguage === 'pa' ? 'ਸੁਝਾਏ ਗਏ ਸਵਾਲ (ਕਲਿੱਕ ਕਰੋ):' :
               selectedLanguage === 'hinglish' ? 'Suggested Questions (Click to Ask):' :
               'Suggested Questions (Click to ask):'}
            </span>
          </div>
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
            {SUGGESTED_QUERIES[selectedLanguage].slice(0, 4).map((prompt, pIdx) => (
              <button
                key={pIdx}
                type="button"
                onClick={() => handleSend(prompt)}
                disabled={isLoading}
                className="whitespace-nowrap px-2.5 py-1 rounded-subtle bg-white/70 hover:bg-forest-50 hover:text-forest-900 border border-white/80 text-[11px] text-ink-950/80 transition-all text-left shadow-2xs hover:border-forest-300 disabled:opacity-50 cursor-pointer"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="p-3 border-t border-ink-950/10 bg-white/60 backdrop-blur-sm flex gap-2"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={e => setInputQuery(e.target.value)}
            placeholder={PLACEHOLDERS[selectedLanguage]}
            className="flex-1 px-3.5 py-2.5 rounded-subtle border border-white/80 bg-white/90 text-ink-950 placeholder:text-ink-950/45 text-xs backdrop-blur-sm focus:bg-white focus:border-forest-700 focus:outline-none transition-all shadow-xs"
          />
          <Button
            type="submit"
            variant="primary"
            size="sm"
            isLoading={isLoading}
            rightIcon={<Send className="w-3.5 h-3.5" />}
          >
            {selectedLanguage === 'hi' ? 'पूछें' :
             selectedLanguage === 'pa' ? 'ਪੁੱਛੋ' :
             selectedLanguage === 'hinglish' ? 'Poochhein' :
             'Ask'}
          </Button>
        </form>

      </div>
    </div>
  );
};
