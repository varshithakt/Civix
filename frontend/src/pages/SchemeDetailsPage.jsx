import React, { useState, useEffect } from 'react';
import { ExternalLink, ShieldCheck, FileText, CheckCircle2, XCircle, HelpCircle, Sparkles, ArrowLeft, ArrowRight } from 'lucide-react';
import { getSchemeDetail, getCurrentProfile, matchSchemes } from '../services/api';

export default function SchemeDetailsPage({ schemeId, onBack, onAutofill }) {
  const [scheme, setScheme] = useState(null);
  const [simplified, setSimplified] = useState('');
  const [showOriginal, setShowOriginal] = useState(false);
  const [ruleEval, setRuleEval] = useState(null);
  const [docCheck, setDocCheck] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (schemeId) {
      loadDetails();
    }
  }, [schemeId]);

  const loadDetails = async () => {
    setLoading(true);
    try {
      const data = await getSchemeDetail(schemeId);
      setScheme(data.scheme);
      setSimplified(data.simplified_language);

      // Evaluate against current user profile
      const profData = await getCurrentProfile();
      const matchData = await matchSchemes(profData.profile || {}, '');
      const found = matchData.results?.find(r => r.scheme.id === schemeId);

      if (found) {
        setRuleEval(found.rule_evaluation);
        setDocCheck(found.document_check);
      }
    } catch (err) {
      console.error("Error loading scheme details", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !scheme) {
    return <div style={{ padding: 40, textAlign: 'center' }}>Loading scheme intelligence data...</div>;
  }

  const isEligible = ruleEval?.overall_status === 'potentially_eligible';

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      <button className="btn btn-secondary" style={{ marginBottom: 16 }} onClick={onBack}>
        <ArrowLeft size={16} /> Back to Scheme Directory
      </button>

      {/* Main Header */}
      <div className="card" style={{ borderLeft: isEligible ? '5px solid var(--success)' : '5px solid var(--warning)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <span className="badge badge-info" style={{ marginBottom: 8 }}>{scheme.category}</span>
            <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--gray-900)' }}>{scheme.name}</h1>
          </div>
          <div>
            {ruleEval && (
              isEligible ? (
                <span className="badge badge-matched" style={{ fontSize: '0.9rem', padding: '6px 14px' }}>
                  ✓ Potentially Eligible
                </span>
              ) : (
                <span className="badge badge-unknown" style={{ fontSize: '0.9rem', padding: '6px 14px' }}>
                  ? Potential Match (Verification Needed)
                </span>
              )
            )}
          </div>
        </div>

        {/* Disclaimer Warning */}
        <div style={{ background: 'var(--gray-50)', padding: 10, borderRadius: 6, fontSize: '0.8rem', color: 'var(--gray-600)', marginTop: 12 }}>
          <strong>Notice:</strong> Potentially eligible based on the information provided. Official eligibility is determined solely by government authorities.
        </div>

        {/* Official Source Link */}
        <div style={{ marginTop: 16 }}>
          <a
            href={scheme.source_url}
            target="_blank"
            rel="noreferrer"
            className="btn btn-primary"
            style={{ fontSize: '0.85rem' }}
          >
            Visit Official Source Portal ({scheme.source_url}) <ExternalLink size={14} />
          </a>
        </div>
      </div>

      {/* Government Language Simplification Module */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 className="card-title" style={{ margin: 0 }}>
            <Sparkles size={18} color="var(--primary)" />
            Government Language Simplification
          </h3>
          <button
            className="btn btn-secondary"
            style={{ fontSize: '0.8rem', padding: '4px 10px' }}
            onClick={() => setShowOriginal(!showOriginal)}
          >
            {showOriginal ? 'View Simplified Text' : 'View Original Policy Wording'}
          </button>
        </div>

        {showOriginal ? (
          <div style={{ background: 'var(--gray-50)', padding: 14, borderRadius: 8, fontSize: '0.9rem', color: 'var(--gray-800)', borderLeft: '3px solid var(--gray-400)' }}>
            <strong>Original Formal Wording:</strong>
            <p style={{ marginTop: 6 }}>{scheme.description}</p>
          </div>
        ) : (
          <div style={{ background: 'var(--primary-light)', padding: 14, borderRadius: 8, fontSize: '0.95rem', color: '#1e40af', borderLeft: '3px solid var(--primary)' }}>
            <strong>Plain Language Explanation:</strong>
            <p style={{ marginTop: 6, fontWeight: 500 }}>
              {simplified || scheme.simplified_description}
            </p>
          </div>
        )}
      </div>

      {/* Criterion-by-Criterion Eligibility Breakdown */}
      {ruleEval && (
        <div className="card">
          <h3 className="card-title">
            <ShieldCheck size={18} color="var(--primary)" />
            Deterministic Eligibility Criterion Breakdown
          </h3>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ background: 'var(--gray-100)', textAlign: 'left' }}>
                  <th style={{ padding: '10px 14px', borderBottom: '1px solid var(--gray-200)' }}>Criterion</th>
                  <th style={{ padding: '10px 14px', borderBottom: '1px solid var(--gray-200)' }}>Requirement</th>
                  <th style={{ padding: '10px 14px', borderBottom: '1px solid var(--gray-200)' }}>Your Profile Value</th>
                  <th style={{ padding: '10px 14px', borderBottom: '1px solid var(--gray-200)' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(ruleEval.breakdown).map(([field, info]) => {
                  let badgeClass = "badge-unknown";
                  let icon = <HelpCircle size={14} />;
                  if (info.status === 'matched') {
                    badgeClass = "badge-matched";
                    icon = <CheckCircle2 size={14} />;
                  } else if (info.status === 'unmatched') {
                    badgeClass = "badge-unmatched";
                    icon = <XCircle size={14} />;
                  }

                  return (
                    <tr key={field} style={{ borderBottom: '1px solid var(--gray-100)' }}>
                      <td style={{ padding: '10px 14px', fontWeight: 600, textTransform: 'capitalize' }}>{field}</td>
                      <td style={{ padding: '10px 14px' }}>{info.requirement}</td>
                      <td style={{ padding: '10px 14px' }}>
                        {info.user_value !== null && info.user_value !== undefined
                          ? (typeof info.user_value === 'number' && field === 'income' ? `₹${info.user_value.toLocaleString()}` : String(info.user_value))
                          : 'Not Provided (Unknown)'}
                      </td>
                      <td style={{ padding: '10px 14px' }}>
                        <span className={`badge ${badgeClass}`}>
                          {icon} {info.status.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Required Documents & Missing Document Alerts */}
      {docCheck && (
        <div className="card">
          <h3 className="card-title">
            <FileText size={18} color="var(--primary)" />
            Document Requirements & Verification
          </h3>

          <div className="grid-2">
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 8, color: 'var(--success)' }}>
                ✓ Uploaded & Verified Documents ({docCheck.provided_count})
              </h4>
              {docCheck.matched_documents.length === 0 ? (
                <div style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>No matching documents uploaded.</div>
              ) : (
                <ul style={{ paddingLeft: 20, fontSize: '0.85rem' }}>
                  {docCheck.matched_documents.map((d, i) => (
                    <li key={i} style={{ marginBottom: 4 }}>{d.name}</li>
                  ))}
                </ul>
              )}
            </div>

            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 8, color: 'var(--warning)' }}>
                ⚠ Missing / Unverified Certificates ({docCheck.missing_count})
              </h4>
              {docCheck.missing_documents.length === 0 ? (
                <div style={{ fontSize: '0.85rem', color: 'var(--success)', fontWeight: 600 }}>All required documents are present!</div>
              ) : (
                <ul style={{ paddingLeft: 20, fontSize: '0.85rem' }}>
                  {docCheck.missing_documents.map((d, i) => (
                    <li key={i} style={{ color: 'var(--warning)', fontWeight: 600, marginBottom: 4 }}>⚠ {d.name}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Action Footer */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 40 }}>
        <button className="btn btn-primary" style={{ flex: 1, padding: 12 }} onClick={() => onAutofill(scheme.id)}>
          Pre-Fill Scheme Application Form <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}
