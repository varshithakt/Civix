import React, { useState } from 'react';
import { Search, Sparkles, ArrowRight, ShieldCheck, FileCheck, Layers } from 'lucide-react';
import NLPPipelineVisualizer from '../components/NLPPipelineVisualizer';
import { processNLPQuery, matchSchemes, updateProfile } from '../services/api';

export default function Home({ onSelectScheme, onNavigateToProfile, onNavigateToUpload }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [nlpResult, setNlpResult] = useState(null);
  const [matchedResults, setMatchedResults] = useState([]);

  const SAMPLE_QUERIES = [
    "I'm a 20-year-old engineering student from Karnataka and my family income is around 1.8 lakh per year. What government scholarships may be relevant to me?",
    "I am a farmer from Karnataka with 2 acres land. What schemes can help with irrigation?",
    "What government housing schemes are available for household income under 3 lakh?",
    "Disability support and assistive aid schemes for 40% benchmark disability"
  ];

  const handleSearch = async (textToSearch) => {
    const searchText = textToSearch || query;
    if (!searchText.trim()) return;

    setLoading(true);
    try {
      // 1. Process Natural Language Query with NLP
      const nlpData = await processNLPQuery(searchText);
      setNlpResult(nlpData);

      // 2. Update active profile state with extracted entities
      if (nlpData.extracted_profile) {
        await updateProfile(nlpData.extracted_profile);
      }

      // 3. Match schemes against extracted profile
      const matchData = await matchSchemes(nlpData.extracted_profile, searchText);
      setMatchedResults(matchData.results || []);
    } catch (err) {
      console.error("Error processing query:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Hero Header */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)', color: '#ffffff', padding: '36px 28px' }}>
        <div style={{ maxWidth: 800 }}>
          <span className="badge badge-info" style={{ marginBottom: 12 }}>
            <Sparkles size={12} /> AI & NLP Government Eligibility Assistant
          </span>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 700, lineHeight: 1.2, marginBottom: 12 }}>
            Discover Government Schemes You May Be Eligible For
          </h1>
          <p style={{ color: 'var(--gray-300)', fontSize: '1.05rem', marginBottom: 24 }}>
            Describe your situation in plain natural language or upload documents. Our NLP pipeline extracts your profile, checks deterministic eligibility criteria, and explains results in simple language.
          </p>

          {/* Quick Query Input Box */}
          <div style={{ display: 'flex', gap: 10, background: '#ffffff', padding: 6, borderRadius: 10, boxShadow: '0 4px 20px rgba(0,0,0,0.15)' }}>
            <input
              type="text"
              className="form-input"
              style={{ border: 'none', color: 'var(--gray-900)', fontSize: '0.95rem' }}
              placeholder="e.g., I'm a 20 year old student from Karnataka family income 1.8 lakh..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button className="btn btn-primary" onClick={() => handleSearch()} disabled={loading}>
              {loading ? 'Analyzing...' : <><Search size={16} /> Analyze Query</>}
            </button>
          </div>

          {/* Sample Prompts */}
          <div style={{ marginTop: 16 }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--gray-300)', marginBottom: 8, fontWeight: 500 }}>
              Try sample natural language queries:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {SAMPLE_QUERIES.map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => { setQuery(sample); handleSearch(sample); }}
                  style={{
                    background: 'rgba(255,255,255,0.1)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    color: '#ffffff',
                    padding: '6px 12px',
                    borderRadius: 6,
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    textAlign: 'left'
                  }}
                >
                  "{sample.substring(0, 50)}..."
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Method B Shortcut banner */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
        <div className="card" style={{ flex: 1, margin: 0, display: 'flex', alignItems: 'center', gap: 16, cursor: 'pointer' }} onClick={onNavigateToUpload}>
          <div style={{ background: 'var(--primary-light)', color: 'var(--primary)', padding: 14, borderRadius: 10 }}>
            <FileCheck size={24} />
          </div>
          <div>
            <h4 style={{ fontWeight: 600, fontSize: '1rem', margin: 0 }}>Method B: Document Upload & OCR</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--gray-600)', margin: 0 }}>
              Upload Income cert, College ID, or Aadhaar to automatically classify and extract profile data.
            </p>
          </div>
        </div>
      </div>

      {/* NLP Pipeline Visualizer */}
      {nlpResult && (
        <NLPPipelineVisualizer nlpResult={nlpResult} profile={nlpResult.extracted_profile} />
      )}

      {/* Extracted Profile Quick Confirmation */}
      {nlpResult && nlpResult.extracted_profile && (
        <div className="card" style={{ backgroundColor: '#ffffff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <h3 className="card-title" style={{ margin: 0 }}>
              <ShieldCheck size={20} color="var(--success)" />
              Extracted Profile Entities
            </h3>
            <button className="btn btn-secondary" style={{ fontSize: '0.8rem', padding: '4px 10px' }} onClick={onNavigateToProfile}>
              Edit Extracted Profile
            </button>
          </div>

          <div className="grid-3">
            <div style={{ background: 'var(--gray-50)', padding: 12, borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>AGE</div>
              <div style={{ fontWeight: 700, fontSize: '1rem' }}>{nlpResult.extracted_profile.age} years</div>
            </div>
            <div style={{ background: 'var(--gray-50)', padding: 12, borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>ANNUAL HOUSEHOLD INCOME</div>
              <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--primary)' }}>
                {nlpResult.extracted_profile.annual_income !== 'unknown'
                  ? `₹${Number(nlpResult.extracted_profile.annual_income).toLocaleString()}`
                  : 'Unknown'}
              </div>
            </div>
            <div style={{ background: 'var(--gray-50)', padding: 12, borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>EDUCATION</div>
              <div style={{ fontWeight: 700, fontSize: '1rem', textTransform: 'capitalize' }}>
                {nlpResult.extracted_profile.education}
              </div>
            </div>
            <div style={{ background: 'var(--gray-50)', padding: 12, borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>STATE DOMICILE</div>
              <div style={{ fontWeight: 700, fontSize: '1rem' }}>{nlpResult.extracted_profile.state}</div>
            </div>
            <div style={{ background: 'var(--gray-50)', padding: 12, borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>CATEGORY</div>
              <div style={{ fontWeight: 700, fontSize: '1rem' }}>{nlpResult.extracted_profile.category}</div>
            </div>
            <div style={{ background: 'var(--gray-50)', padding: 12, borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>OCCUPATION</div>
              <div style={{ fontWeight: 700, fontSize: '1rem', textTransform: 'capitalize' }}>
                {nlpResult.extracted_profile.occupation}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Matched Scheme Results */}
      {matchedResults.length > 0 && (
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Layers size={22} color="var(--primary)" />
            Potentially Applicable Schemes ({matchedResults.length})
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {matchedResults.map((item, idx) => {
              const s = item.scheme;
              const rule = item.rule_evaluation;
              const isEligible = rule.overall_status === 'potentially_eligible';

              return (
                <div key={idx} className="card" style={{ margin: 0, borderLeft: isEligible ? '4px solid var(--success)' : '4px solid var(--warning)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 10 }}>
                    <div>
                      <span className="badge badge-info" style={{ marginBottom: 6 }}>{s.category}</span>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--gray-900)' }}>{s.name}</h3>
                    </div>
                    <div>
                      {isEligible ? (
                        <span className="badge badge-matched" style={{ fontSize: '0.85rem' }}>
                          ✓ Potentially Eligible
                        </span>
                      ) : (
                        <span className="badge badge-unknown" style={{ fontSize: '0.85rem' }}>
                          ? Potential Match (Verification Needed)
                        </span>
                      )}
                    </div>
                  </div>

                  <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', margin: '10px 0' }}>
                    {s.simplified_description || s.description}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--gray-200)' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--gray-600)' }}>
                      Semantic Similarity Match: <strong>{(item.semantic_similarity * 100).toFixed(0)}%</strong>
                    </div>
                    <button className="btn btn-secondary" onClick={() => onSelectScheme(s.id)}>
                      View Detailed Eligibility Breakdown <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
