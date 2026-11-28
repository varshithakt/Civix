import React, { useState, useEffect } from 'react';
import {
  ClipboardList,
  CheckCircle2,
  Clock,
  ArrowRight,
  ExternalLink,
  Trash2,
  FileText,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Edit3
} from 'lucide-react';
import {
  listApplications,
  advanceApplicationProgress,
  deleteApplication
} from '../services/api';

export default function ApplicationsPage({ onResumeApplication, onBrowseSchemes }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);
  const [actionId, setActionId] = useState(null);

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const data = await listApplications();
      setApplications(data.applications || []);
    } catch (err) {
      console.error('Error loading applications', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvance = async (appId) => {
    setActionId(appId);
    try {
      const res = await advanceApplicationProgress(appId);
      setApplications(prev => prev.map(a => (a.id === appId ? res.application : a)));
    } catch (err) {
      alert(err.response?.data?.detail || 'Unable to advance progress.');
    } finally {
      setActionId(null);
    }
  };

  const handleDelete = async (appId) => {
    try {
      await deleteApplication(appId);
      setApplications(prev => prev.filter(a => a.id !== appId));
    } catch (err) {
      alert('Failed to remove application: ' + err.message);
    }
  };

  const totalCount = applications.length;
  const submittedCount = applications.filter(a => a.current_step >= 2).length;
  const readyCount = applications.filter(a => a.current_step === 5).length;
  const draftCount = applications.filter(a => a.current_step === 1).length;

  return (
    <div style={{ maxWidth: 980, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--gray-900)' }}>
            Saved Applications & Progress Tracker
          </h1>
          <p style={{ color: 'var(--gray-600)', fontSize: '0.95rem' }}>
            Track saved drafts and directly submitted scheme applications across verification stages.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={fetchApplications} disabled={loading}>
          <RefreshCw size={15} /> Refresh
        </button>
      </div>

      {/* Summary Metrics */}
      <div className="grid-3" style={{ marginBottom: 20 }}>
        <div className="card" style={{ margin: 0, padding: 16 }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--gray-600)' }}>SAVED APPLICATIONS</div>
          <div style={{ fontSize: '1.7rem', fontWeight: 700, color: 'var(--gray-900)', marginTop: 4 }}>{totalCount}</div>
        </div>
        <div className="card" style={{ margin: 0, padding: 16 }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--gray-600)' }}>SUBMITTED / IN REVIEW</div>
          <div style={{ fontSize: '1.7rem', fontWeight: 700, color: 'var(--primary)', marginTop: 4 }}>{submittedCount}</div>
        </div>
        <div className="card" style={{ margin: 0, padding: 16 }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--gray-600)' }}>DRAFTS / READY TO SYNC</div>
          <div style={{ fontSize: '1.7rem', fontWeight: 700, color: 'var(--success)', marginTop: 4 }}>
            {draftCount} / {readyCount}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          Loading saved applications...
        </div>
      ) : applications.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 44 }}>
          <ClipboardList size={40} color="var(--gray-600)" style={{ marginBottom: 12 }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: 8 }}>No Saved Applications Yet</h3>
          <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', marginBottom: 18 }}>
            Choose any of the 5 Direct Apply schemes in the Scheme Directory or open Form Auto-Fill to review, save, and submit your application.
          </p>
          <button className="btn btn-primary" onClick={onBrowseSchemes}>
            Explore Direct-Apply Schemes <ArrowRight size={15} />
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          {applications.map((app) => {
            const isExpanded = expandedId === app.id;
            const isComplete = app.current_step === 5;
            const isDraft = app.current_step === 1;

            return (
              <div
                key={app.id}
                className="card"
                style={{
                  margin: 0,
                  borderLeft: isComplete
                    ? '4px solid var(--success)'
                    : isDraft
                    ? '4px solid var(--warning)'
                    : '4px solid var(--primary)'
                }}
              >
                {/* Header Row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 6 }}>
                      <span className="badge badge-info">{app.category}</span>
                      <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--gray-600)' }}>
                        Ref: {app.id}
                      </span>
                      <span style={{ fontSize: '0.78rem', color: 'var(--gray-600)' }}>
                        Updated: {app.updated_at}
                      </span>
                    </div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--gray-900)' }}>
                      {app.scheme_name}
                    </h3>
                    <div style={{ fontSize: '0.85rem', color: 'var(--gray-600)', marginTop: 2 }}>
                      Applicant: <strong>{app.applicant_name}</strong>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <span
                      className={`badge ${
                        isComplete ? 'badge-matched' : isDraft ? 'badge-unknown' : 'badge-info'
                      }`}
                      style={{ fontSize: '0.85rem', padding: '6px 12px' }}
                    >
                      {app.status} ({app.progress_pct}%)
                    </span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div style={{ marginTop: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, color: 'var(--gray-600)', marginBottom: 6 }}>
                    <span>Application Progress</span>
                    <span>Step {app.current_step} of 5 ({app.progress_pct}%)</span>
                  </div>
                  <div style={{ width: '100%', height: 10, backgroundColor: 'var(--gray-200)', borderRadius: 999, overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${app.progress_pct}%`,
                        height: '100%',
                        backgroundColor: isComplete ? 'var(--success)' : isDraft ? 'var(--warning)' : 'var(--primary)',
                        transition: 'width 0.3s ease'
                      }}
                    />
                  </div>
                </div>

                {/* 5-Stage Horizontal Stepper */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 8, marginTop: 14 }}>
                  {(app.timeline || []).map((stage) => {
                    const done = stage.status === 'completed';
                    const active = stage.status === 'in_progress';
                    return (
                      <div
                        key={stage.step}
                        style={{
                          padding: '8px 10px',
                          borderRadius: 8,
                          border: done
                            ? '1px solid #bbf7d0'
                            : active
                            ? '1px solid #bfdbfe'
                            : '1px solid var(--gray-200)',
                          backgroundColor: done
                            ? 'var(--success-light)'
                            : active
                            ? 'var(--primary-light)'
                            : 'var(--gray-50)',
                          fontSize: '0.78rem'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontWeight: 700, color: done ? 'var(--success)' : active ? 'var(--primary)' : 'var(--gray-600)' }}>
                          {done ? <CheckCircle2 size={13} /> : <Clock size={13} />}
                          <span>{stage.step}. {stage.label}</span>
                        </div>
                        {stage.timestamp && (
                          <div style={{ fontSize: '0.7rem', color: 'var(--gray-600)', marginTop: 3 }}>
                            {stage.timestamp}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Action Bar */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10, marginTop: 16, paddingTop: 12, borderTop: '1px solid var(--gray-200)' }}>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {isDraft ? (
                      <button
                        className="btn btn-primary"
                        style={{ padding: '6px 12px', fontSize: '0.82rem' }}
                        onClick={() => onResumeApplication(app)}
                      >
                        <Edit3 size={14} /> Review & Submit Draft
                      </button>
                    ) : !isComplete ? (
                      <button
                        className="btn btn-primary"
                        style={{ padding: '6px 12px', fontSize: '0.82rem' }}
                        onClick={() => handleAdvance(app.id)}
                        disabled={actionId === app.id}
                      >
                        <RefreshCw size={14} /> {actionId === app.id ? 'Updating...' : 'Advance Verification Stage'}
                      </button>
                    ) : (
                      <a
                        href={app.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-primary"
                        style={{ padding: '6px 12px', fontSize: '0.82rem', textDecoration: 'none' }}
                      >
                        Sync on Official Portal <ExternalLink size={13} />
                      </a>
                    )}

                    <button
                      className="btn btn-secondary"
                      style={{ padding: '6px 12px', fontSize: '0.82rem' }}
                      onClick={() => setExpandedId(isExpanded ? null : app.id)}
                    >
                      <FileText size={14} />
                      {isExpanded ? 'Hide Saved Details' : 'View Saved Details'}
                      {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  </div>

                  <button
                    className="btn btn-secondary"
                    style={{ padding: '6px 10px', fontSize: '0.8rem', color: 'var(--danger)' }}
                    onClick={() => handleDelete(app.id)}
                  >
                    <Trash2 size={14} /> Withdraw
                  </button>
                </div>

                {/* Expanded Details Drawer */}
                {isExpanded && (
                  <div style={{ marginTop: 14, padding: 14, background: 'var(--gray-50)', borderRadius: 8, border: '1px solid var(--gray-200)' }}>
                    <div className="grid-2">
                      <div>
                        <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: 8 }}>Saved Form Fields</h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: '0.82rem' }}>
                          {(app.form_data?.fields || []).map((f) => (
                            <div key={f.field_id}>
                              <strong>{f.label}:</strong> {f.value || '—'}
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: 8 }}>Stage Timeline Notes & Documents</h4>
                        <ul style={{ paddingLeft: 18, fontSize: '0.8rem', color: 'var(--gray-600)', marginBottom: 10 }}>
                          {(app.timeline || []).map((t) => (
                            <li key={t.step} style={{ marginBottom: 3 }}>
                              <strong>{t.label}:</strong> {t.note}
                            </li>
                          ))}
                        </ul>
                        {app.documents?.missing_documents?.length > 0 && (
                          <div style={{ fontSize: '0.78rem', color: 'var(--warning)', fontWeight: 600 }}>
                            Missing docs at submission: {app.documents.missing_documents.join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
