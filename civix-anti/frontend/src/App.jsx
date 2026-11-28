import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import DocumentUpload from './pages/DocumentUpload';
import UserProfilePage from './pages/UserProfilePage';
import SchemeDiscovery from './pages/SchemeDiscovery';
import SchemeDetailsPage from './pages/SchemeDetailsPage';
import FormAutofillPage from './pages/FormAutofillPage';
import ApplicationsPage from './pages/ApplicationsPage';
import SchemeChatbotPage from './pages/SchemeChatbotPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedSchemeId, setSelectedSchemeId] = useState(null);
  const [draftApplication, setDraftApplication] = useState(null);

  const handleSelectScheme = (schemeId) => {
    setSelectedSchemeId(schemeId);
    setActiveTab('detail');
  };

  const handleAutofill = (schemeId) => {
    setDraftApplication(null);
    setSelectedSchemeId(schemeId);
    setActiveTab('autofill');
  };

  const handleResumeApplication = (app) => {
    setDraftApplication(app);
    setSelectedSchemeId(app.scheme_id);
    setActiveTab('autofill');
  };

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {activeTab === 'home' && (
          <Home
            onSelectScheme={handleSelectScheme}
            onNavigateToProfile={() => setActiveTab('profile')}
            onNavigateToUpload={() => setActiveTab('upload')}
          />
        )}

        {activeTab === 'upload' && (
          <DocumentUpload onNavigateToProfile={() => setActiveTab('profile')} />
        )}

        {activeTab === 'profile' && (
          <UserProfilePage onNavigateToSchemes={() => setActiveTab('schemes')} />
        )}

        {activeTab === 'schemes' && (
          <SchemeDiscovery onSelectScheme={handleSelectScheme} onDirectApply={handleAutofill} />
        )}

        {activeTab === 'detail' && (
          <SchemeDetailsPage
            schemeId={selectedSchemeId}
            onBack={() => setActiveTab('schemes')}
            onAutofill={handleAutofill}
          />
        )}

        {activeTab === 'autofill' && (
          <FormAutofillPage
            schemeId={selectedSchemeId}
            draftApplication={draftApplication}
            onBack={() => setActiveTab('detail')}
            onApplicationSaved={() => setActiveTab('applications')}
          />
        )}

        {activeTab === 'applications' && (
          <ApplicationsPage
            onResumeApplication={handleResumeApplication}
            onBrowseSchemes={() => setActiveTab('schemes')}
          />
        )}

        {activeTab === 'chat' && (
          <SchemeChatbotPage />
        )}
      </main>

      <footer className="footer">
        Civix Government Scheme Eligibility & Application Assistant © 2026. Built with Python FastAPI & React.
        <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', marginTop: 4 }}>
          Disclaimer: Potentially eligible based on available criteria. Official eligibility must be verified on official government portals.
        </div>
      </footer>
    </div>
  );
}
