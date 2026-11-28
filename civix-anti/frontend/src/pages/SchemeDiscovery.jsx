import React, { useState, useEffect } from 'react';
import { Building2, ExternalLink, ArrowRight, Filter, Search, ShieldCheck, Zap } from 'lucide-react';
import { getAllSchemes, matchSchemes, getCurrentProfile } from '../services/api';

export default function SchemeDiscovery({ onSelectScheme, onDirectApply }) {
  const [schemes, setSchemes] = useState([]);
  const [category, setCategory] = useState('');
  const [directOnly, setDirectOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [matchedResults, setMatchedResults] = useState([]);
  const [isEvaluated, setIsEvaluated] = useState(false);

  useEffect(() => {
    fetchSchemes();
  }, [category]);

  const fetchSchemes = async () => {
    setLoading(true);
    try {
      const data = await getAllSchemes(category || null);
      setSchemes(data.schemes || []);
    } catch (err) {
      console.error("Error loading schemes", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunEligibilityCheck = async () => {
    setLoading(true);
    try {
      const profileData = await getCurrentProfile();
      const matchData = await matchSchemes(profileData.profile || {}, '');
      setMatchedResults(matchData.results || []);
      setIsEvaluated(true);
    } catch (err) {
      alert("Error evaluating eligibility: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const categories = ["Education", "Agriculture", "Housing", "Disability", "Business", "Women Welfare"];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--gray-900)' }}>
            Government Scheme Directory
          </h1>
          <p style={{ color: 'var(--gray-600)', fontSize: '0.95rem' }}>
            Browse indexed official government schemes across sectors or evaluate eligibility against your profile.
          </p>
        </div>

        <button className="btn btn-primary" onClick={handleRunEligibilityCheck} disabled={loading}>
          <ShieldCheck size={16} /> {loading ? 'Evaluating...' : 'Evaluate Eligibility Against Profile'}
        </button>
      </div>

      {/* Category Filters */}
      <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 12, marginBottom: 20 }}>
        <button
          className={`btn ${category === '' && !directOnly ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.85rem' }}
          onClick={() => { setCategory(''); setDirectOnly(false); setIsEvaluated(false); }}
        >
          All Categories
        </button>
        <button
          className={`btn ${directOnly ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.85rem' }}
          onClick={() => { setDirectOnly(!directOnly); }}
        >
          <Zap size={13} /> Direct Apply (5)
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            className={`btn ${category === cat ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 14px', fontSize: '0.85rem' }}
            onClick={() => { setCategory(cat); setIsEvaluated(false); }}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Scheme Cards Grid */}
      <div className="grid-2">
        {(isEvaluated && matchedResults.length > 0 ? matchedResults.map(r => ({ ...r.scheme, rule_eval: r.rule_evaluation })) : schemes)
          .filter(s => !directOnly || s.direct_apply)
          .map((s) => {
          const ruleEval = s.rule_eval;
          const isEligible = ruleEval?.overall_status === 'potentially_eligible';

          return (
            <div key={s.id} className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    <span className="badge badge-info">{s.category}</span>
                    {s.direct_apply && (
                      <span className="badge badge-matched"><Zap size={11} /> Direct Apply</span>
                    )}
                  </div>
                  {ruleEval && (
                    isEligible ? (
                      <span className="badge badge-matched">✓ Potentially Eligible</span>
                    ) : (
                      <span className="badge badge-unknown">? Verification Needed</span>
                    )
                  )}
                </div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--gray-900)', marginBottom: 8 }}>
                  {s.name}
                </h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--gray-600)', marginBottom: 12 }}>
                  {s.simplified_description || s.description}
                </p>
              </div>

              <div style={{ borderTop: '1px solid var(--gray-200)', paddingTop: 12, marginTop: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                <a
                  href={s.source_url}
                  target="_blank"
                  rel="noreferrer"
                  style={{ fontSize: '0.8rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 4, textDecoration: 'none', fontWeight: 600 }}
                >
                  Official Source <ExternalLink size={12} />
                </a>

                <div style={{ display: 'flex', gap: 8 }}>
                  {s.direct_apply && onDirectApply && (
                    <button className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '0.85rem' }} onClick={() => onDirectApply(s.id)}>
                      <Zap size={13} /> Apply Directly
                    </button>
                  )}
                  <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }} onClick={() => onSelectScheme(s.id)}>
                    View Details <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
