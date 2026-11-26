import React, { useState } from 'react';
import { MessageSquare, Send, Bot, User, Sparkles, HelpCircle } from 'lucide-react';
import { askChatbot, getCurrentProfile } from '../services/api';

export default function SchemeChatbotPage() {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: "Hello! I am your Government Scheme Assistant. Ask me anything about scheme requirements, document lists, eligibility criteria, or policy explanations."
    }
  ]);
  const [inputMsg, setInputMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const QUICK_QUESTIONS = [
    "What documents do I need for post-matric scholarship?",
    "Why did I not match this scheme?",
    "Tell me about PM Kisan scheme for farmers",
    "What schemes help female heads of households in Karnataka?"
  ];

  const handleSend = async (textToSend) => {
    const text = textToSend || inputMsg;
    if (!text.trim()) return;

    // Append user message
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setInputMsg('');
    setLoading(true);

    try {
      const profData = await getCurrentProfile();
      const res = await askChatbot(text, profData.profile || null);

      setMessages(prev => [
        ...prev,
        {
          sender: 'bot',
          text: res.grounded_response,
          intent: res.intent_detected,
          source: res.source_scheme
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { sender: 'bot', text: "Sorry, I encountered an error connecting to the scheme knowledge base." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 880, margin: '0 auto' }}>
      <div style={{ marginBottom: 16 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--gray-900)' }}>
          Conversational Scheme Assistant
        </h1>
        <p style={{ color: 'var(--gray-600)', fontSize: '0.95rem' }}>
          Grounded Question Answering interface. Answers are generated strictly from the official scheme database and user profile facts.
        </p>
      </div>

      {/* Chat Container */}
      <div className="card" style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', height: '540px' }}>
        {/* Chat History Window */}
        <div style={{ flex: 1, padding: 20, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 14, background: 'var(--gray-50)' }}>
          {messages.map((m, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                gap: 10,
                alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '82%'
              }}
            >
              {m.sender === 'bot' && (
                <div style={{ background: 'var(--primary)', color: '#ffffff', padding: 8, borderRadius: '50%', height: 36, width: 36, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Bot size={20} />
                </div>
              )}

              <div
                style={{
                  background: m.sender === 'user' ? 'var(--primary)' : '#ffffff',
                  color: m.sender === 'user' ? '#ffffff' : 'var(--gray-900)',
                  padding: '12px 16px',
                  borderRadius: 12,
                  border: m.sender === 'user' ? 'none' : '1px solid var(--gray-200)',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                  whiteSpace: 'pre-line',
                  fontSize: '0.9rem'
                }}
              >
                {m.text}
                {m.source && (
                  <div style={{ fontSize: '0.75rem', marginTop: 8, pt: 4, color: m.sender === 'user' ? '#dbeafe' : 'var(--gray-600)', fontWeight: 600 }}>
                    Source Grounding: {m.source}
                  </div>
                )}
              </div>

              {m.sender === 'user' && (
                <div style={{ background: 'var(--gray-800)', color: '#ffffff', padding: 8, borderRadius: '50%', height: 36, width: 36, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <User size={20} />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', gap: 10, alignSelf: 'flex-start' }}>
              <div style={{ background: 'var(--primary)', color: '#ffffff', padding: 8, borderRadius: '50%', height: 36, width: 36, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={20} />
              </div>
              <div style={{ background: '#ffffff', padding: '10px 16px', borderRadius: 12, fontSize: '0.85rem', color: 'var(--gray-600)' }}>
                Searching scheme knowledge base...
              </div>
            </div>
          )}
        </div>

        {/* Quick Question Chips */}
        <div style={{ padding: '8px 16px', background: '#ffffff', borderTop: '1px solid var(--gray-200)', display: 'flex', gap: 6, overflowX: 'auto' }}>
          {QUICK_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q)}
              style={{
                background: 'var(--gray-100)',
                border: 'none',
                padding: '4px 10px',
                borderRadius: 16,
                fontSize: '0.75rem',
                color: 'var(--gray-700)',
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div style={{ padding: 12, background: '#ffffff', borderTop: '1px solid var(--gray-200)', display: 'flex', gap: 8 }}>
          <input
            type="text"
            className="form-input"
            placeholder="Ask a question about government scheme eligibility or documents..."
            value={inputMsg}
            onChange={(e) => setInputMsg(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button className="btn btn-primary" onClick={() => handleSend()} disabled={loading}>
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
