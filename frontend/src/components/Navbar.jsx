import React from 'react';
import { 
  Building2, 
  Search, 
  FileText, 
  User, 
  CheckSquare, 
  MessageSquare, 
  Upload 
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'home', label: 'Query & Discover', icon: Search },
    { id: 'upload', label: 'Upload Documents', icon: Upload },
    { id: 'profile', label: 'User Profile', icon: User },
    { id: 'schemes', label: 'Scheme Directory', icon: Building2 },
    { id: 'autofill', label: 'Form Auto-Fill', icon: CheckSquare },
    { id: 'chat', label: 'Scheme Assistant', icon: MessageSquare },
  ];

  return (
    <header className="navbar">
      <div className="nav-inner">
        <div className="logo">
          <span>🏛️ Civix Scheme Intelligence</span>
          <span className="logo-badge">NLP Powered</span>
        </div>
        <nav className="nav-tabs">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={`nav-btn ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
