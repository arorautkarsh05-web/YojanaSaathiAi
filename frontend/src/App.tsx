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

        {currentTab === 'action-plan' && actionPlanData && (
          <ActionPlanView
            planData={actionPlanData}
            onBack={() => setCurrentTab('results')}
          />
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

      {/* Grounded Scheme Q&A Modal */}
      <GroundedAssistantModal
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
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
