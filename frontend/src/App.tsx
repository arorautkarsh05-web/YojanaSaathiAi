import { useState, useEffect } from 'react';
import { Header } from './components/layout/Header';
import { BackgroundVideo } from './components/layout/BackgroundVideo';
import { LandingPage } from './features/landing/LandingPage';
import { FarmerIntakeWizard } from './features/intake/FarmerIntakeWizard';
import { RecommendationResultsView } from './features/recommendations/RecommendationResultsView';
import { ActionPlanView } from './features/action-plan/ActionPlanView';
import { SchemesCatalogueView } from './features/schemes/SchemesCatalogueView';
import { AdminPortalView } from './features/admin/AdminPortalView';
import { GroundedAssistantModal } from './features/assistant/GroundedAssistantModal';
import { AuthModal } from './features/auth/AuthModal';
import { api } from './services/api';
import type { FarmerProfileInput, SchemeEvaluation, ActionPlanData } from './services/api';
import './i18n';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('home');
  const [user, setUser] = useState<any | null>(null);

  // Flow data states
  const [, setStatedNeeds] = useState<string[]>([]);
  const [confirmedProfile, setConfirmedProfile] = useState<FarmerProfileInput | null>(null);
  const [evaluatedSchemes, setEvaluatedSchemes] = useState<SchemeEvaluation[]>([]);
  const [actionPlanData, setActionPlanData] = useState<ActionPlanData | null>(null);

  // Modals
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);

  // Restore authenticated session if token exists
  useEffect(() => {
    api.getMe()
      .then(u => {
        if (u) setUser(u);
      })
      .catch(() => {});
  }, []);

  // Restore cached action plan from localStorage if available (offline reliability)
  useEffect(() => {
    if (!actionPlanData) {
      try {
        const latestNum = localStorage.getItem('yojanasaathi_latest_plan_number');
        if (latestNum) {
          const cachedStr = localStorage.getItem(`yojanasaathi_plan_${latestNum}`);
          if (cachedStr) {
            const parsed = JSON.parse(cachedStr);
            if (parsed && parsed.plan_number) {
              setActionPlanData(parsed);
            }
          }
        }
      } catch (err) {
        console.warn('Failed to recover cached plan:', err);
      }
    }
  }, [actionPlanData, currentTab]);

  const handleSignOut = async () => {
    try {
      await api.logout();
    } catch (e) {
      console.error(e);
    }
    setUser(null);
  };

  const handleIntakeComplete = async (needs: string[], profile: FarmerProfileInput) => {
    setStatedNeeds(needs);
    setConfirmedProfile(profile);

    try {
      const res = await api.getRecommendations(needs, profile);
      setEvaluatedSchemes(res.schemes);
      setCurrentTab('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error('Error calculating recommendations:', err);
      alert('पात्रता मूल्यांकन में त्रुटि हुई। कृपया पुनः प्रयास करें।');
    }
  };

  const handleGeneratePlan = async (selectedSchemeCodes: string[]) => {
    if (!confirmedProfile) return;

    try {
      const plan = await api.createActionPlan(confirmedProfile, selectedSchemeCodes);
      setActionPlanData(plan);
      setCurrentTab('action-plan');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error('Error generating action plan:', err);
      alert('कार्य योजना तैयार करने में त्रुटि हुई।');
    }
  };

  return (
    <div className="min-h-screen relative flex flex-col font-sans selection:bg-field-100 selection:text-forest-800">
      {/* Background Video Layer (Autoplays strictly muted with no audio, respecting reduced motion) */}
      <BackgroundVideo videoSrc="/background.mp4" />

      {/* Main Header Navigation */}
      <Header
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        user={user}
        onOpenAuthModal={() => setIsAuthOpen(true)}
        onSignOut={handleSignOut}
      />

      {/* Main Content Area */}
      <main className="flex-1 relative z-10">
        {currentTab === 'home' && (
          <LandingPage
            onStartWizard={() => setCurrentTab('wizard')}
            onOpenSchemes={() => setCurrentTab('schemes')}
            onOpenAssistant={() => setIsAssistantOpen(true)}
            onOpenActionPlan={() => setCurrentTab('action-plan')}
          />
        )}

        {currentTab === 'wizard' && (
          <FarmerIntakeWizard
            onComplete={handleIntakeComplete}
            onCancel={() => setCurrentTab('home')}
          />
        )}

        {currentTab === 'results' && (
          <RecommendationResultsView
            schemes={evaluatedSchemes}
            onGeneratePlan={handleGeneratePlan}
            onRestart={() => setCurrentTab('wizard')}
          />
        )}

        {currentTab === 'action-plan' && (
          actionPlanData ? (
            <ActionPlanView
              planData={actionPlanData}
              onBack={() => setCurrentTab('results')}
            />
          ) : (
            <div className="max-w-2xl mx-auto py-16 px-4 text-center">
              <div className="bg-white/60 backdrop-blur-md border border-white/60 rounded-panel p-8 shadow-sm">
                <div className="w-12 h-12 rounded-full bg-forest-800/10 text-forest-800 flex items-center justify-center mx-auto mb-4 font-serif font-bold text-xl">
                  📋
                </div>
                <h2 className="font-serif text-xl font-bold text-forest-900 mb-2">
                  कोई सक्रिय या सहेजी गई कार्य योजना नहीं मिली
                </h2>
                <p className="text-sm text-ink-950 mb-6 font-medium">
                  अपनी खेती की जानकारी दर्ज करके सरकारी योजनाओं हेतु कदम-दर-कदम कार्य योजना तैयार करें।
                </p>
                <div className="flex justify-center gap-3">
                  <button
                    type="button"
                    onClick={() => setCurrentTab('wizard')}
                    className="px-5 py-2.5 rounded-natural bg-forest-800 text-white font-medium text-sm shadow-sm hover:bg-forest-900"
                  >
                    पात्रता जाँच शुरू करें
                  </button>
                  <button
                    type="button"
                    onClick={() => setCurrentTab('home')}
                    className="px-5 py-2.5 rounded-natural bg-white/70 text-forest-900 font-medium text-sm border border-white/80 hover:bg-white"
                  >
                    मुख्य पृष्ठ पर जाएँ
                  </button>
                </div>
              </div>
            </div>
          )
        )}

        {currentTab === 'schemes' && (
          <SchemesCatalogueView
            onStartWizard={() => setCurrentTab('wizard')}
            onBack={() => setCurrentTab('home')}
          />
        )}

        {currentTab === 'admin' && (
          <AdminPortalView
            onBack={() => setCurrentTab('home')}
            user={user}
            onOpenAuthModal={() => setIsAuthOpen(true)}
          />
        )}
      </main>

      {/* Grounded Scheme Q&A & Natural Language Intake Modal */}
      <GroundedAssistantModal
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        onStartWithProfile={(profile, needs) => {
          setIsAssistantOpen(false);
          handleIntakeComplete(needs, profile);
        }}
      />

      {/* Account Authentication Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={u => setUser(u)}
      />
    </div>
  );
}

export default App;
