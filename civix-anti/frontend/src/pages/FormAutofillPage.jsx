import React, { useState, useEffect } from 'react';
import {
  FileCheck,
  ShieldAlert,
  ArrowLeft,
  Copy,
  Check,
  Send,
  Save,
  Zap,
  CheckCircle2,
  ClipboardList
} from 'lucide-react';
import {
  getCurrentProfile,
  getAutofillPreview,
  getAllSchemes,
  submitDirectApplication
} from '../services/api';

export default function FormAutofillPage({ schemeId, draftApplication, onBack, onApplicationSaved }) {
  const [schemes, setSchemes] = useState([]);
  const [selectedId, setSelectedId] = useState(draftApplication?.scheme_id || schemeId || 'SCH001');
  const [formFields, setFormFields] = useState([]);
  const [directApplyEnabled, setDirectApplyEnabled] = useState(true);
  const [currentProfile, setCurrentProfile] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [userConfirmed, setUserConfirmed] = useState(false);
  const [savedResult, setSavedResult] = useState(null);

  useEffect(() => {
    if (draftApplication?.scheme_id) {
      setSelectedId(draftApplication.scheme_id);
    } else if (schemeId) {
      setSelectedId(schemeId);
    }
  }, [schemeId, draftApplication]);

  useEffect(() => {
    loadData();
  }, [selectedId]);

  const loadData = async () => {
    setLoading(true);
    setSavedResult(null);
    setUserConfirmed(false);
    try {
      const schData = await getAllSchemes();
      setSchemes(schData.schemes || []);

      const profData = await getCurrentProfile();
      setCurrentProfile(profData.profile || {});
      const preview = await getAutofillPreview(selectedId, profData.profile || {});

      setDirectApplyEnabled(Boolean(preview.direct_apply));

      if (draftApplication && draftApplication.scheme_id === selectedId && draftApplication.form_data?.fields) {
        setFormFields(draftApplication.form_data.fields);
      } else {
        setFormFields(preview.form_fields || []);
      }
    } catch (err) {
      console.error('Error loading autofill preview', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = (fieldId, newValue) => {
    setFormFields(prev => prev.map(f => (f.field_id === fieldId ? { ...f, value: newValue } : f)));
  };

  const handleCopySummary = () => {
    const summary = formFields.map(f => `${f.label}: ${f.value}`).join('\n');
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleSaveOrSubmit = async (saveAsDraft) => {
    if (!saveAsDraft && !userConfirmed) {
      alert('Please check the confirmation box confirming you reviewed all pre-filled fields.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await submitDirectApplication({
        scheme_id: selectedId,
        form_fields: formFields,
        profile: currentProfile,
        save_as_draft: saveAsDraft,
        user_confirmed: saveAsDraft ? false : userConfirmed,
        application_id: draftApplication?.id || null
      });
      setSavedResult(res.application);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to save application.');
    } finally {
      setSubmitting(false);
    }
  };

  const currentScheme = schemes.find(s => s.id === selectedId);
  const directSchemesCount = schemes.filter(s => s.direct_apply).length;

  return (
    <div style={{ maxWidth: 880, margin: '0 auto' }}>
      {onBack && (
        <button className="btn btn-secondary" style={{ marginBottom: 16 }} onClick={onBack}>
          <ArrowLeft size={16} /> Back to Scheme Details
        </button>
      )}

      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--gray-900)' }}>
          Direct Application & Form Auto-Fill
        </h1>
        <p style={{ color: 'var(--gray-600)', fontSize: '0.95rem' }}>
          Extracted profile fields pre-populated for your review. {directSchemesCount} schemes support direct in-app saving, submission, and progress tracking.
        </p>
      </div>

      {/* Security & Submission Alert */}
      <div className="alert-box alert-warning">
        <ShieldAlert size={20} color="var(--warning)" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <strong style={{ fontSize: '0.95rem' }}>Mandatory Verification Notice:</strong>
          <div style={{ fontSize: '0.85rem', marginTop: 2 }}>
            Applications are <strong>never automatically submitted</strong>. Review and edit any pre-filled fields below, then confirm before saving or submitting.
          </div>
        </div>
      </div>

      {/* Saved Confirmation Banner */}
      {savedResult && (
        <div className="card" style={{ borderLeft: '4px solid var(--success)', background: 'var(--success-light)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 700, color: 'var(--success)', fontSize: '1rem' }}>
                <CheckCircle2 size={20} />
                {savedResult.status} — Progress: {savedResult.progress_pct}%
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--gray-800)', marginTop: 4 }}>
                Reference ID: <strong>{savedResult.id}</strong> | Scheme: <strong>{savedResult.scheme_name}</strong>
              </div>
            </div>
            <button className="btn btn-primary" onClick={onApplicationSaved}>
              <ClipboardList size={16} /> View Application Progress
            </button>
          </div>
        </div>
      )}

      {/* Scheme Selector */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <label className="input-label" style={{ margin: 0 }}>Select Target Scheme Application Form:</label>
          {directApplyEnabled ? (
            <span className="badge badge-matched"><Zap size={12} /> Direct Apply Supported</span>
          ) : (
            <span className="badge badge-unknown">External Portal Only</span>
          )}
        </div>
        <select
          className="form-select"
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
        >
          {schemes.map(s => (
            <option key={s.id} value={s.id}>
              {s.direct_apply ? '⚡ [Direct Apply] ' : ''}{s.name} ({s.category})
            </option>
          ))}
        </select>
      </div>

      {/* Form Fields Pre-Fill Preview */}
      {loading ? (
        <div style={{ padding: 40, textAlign: 'center' }}>Generating form pre-fill fields...</div>
      ) : (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 className="card-title" style={{ margin: 0 }}>
              <FileCheck size={18} color="var(--primary)" />
              Pre-Filled Application Fields ({formFields.length})
            </h3>
            <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={handleCopySummary}>
              {copied ? <><Check size={14} color="var(--success)" /> Copied!</> : <><Copy size={14} /> Copy Summary</>}
            </button>
          </div>

          <div className="grid-2">
            {formFields.map((field) => (
              <div key={field.field_id} className="input-group">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <label className="input-label" style={{ margin: 0 }}>{field.label}:</label>
                  <span
                    className={`badge ${
                      field.status === 'confirmed' || field.status === 'extracted'
                        ? 'badge-matched'
                        : field.status === 'scheme_specific'
                        ? 'badge-info'
                        : 'badge-unknown'
                    }`}
                    style={{ fontSize: '0.7rem' }}
                  >
                    {field.status === 'scheme_specific' ? 'scheme field' : field.status}
                  </span>
                </div>
                <input
                  type="text"
                  className="form-input"
                  placeholder={field.placeholder || ''}
                  value={field.value}
                  onChange={(e) => handleFieldChange(field.field_id, e.target.value)}
                />
              </div>
            ))}
          </div>

          {directApplyEnabled && (
            <div style={{ marginTop: 16, padding: 14, background: 'var(--gray-50)', borderRadius: 8, border: '1px solid var(--gray-200)' }}>
              <label style={{ display: 'flex', alignItems: 'flex-start', gap: 10, cursor: 'pointer', fontSize: '0.88rem', color: 'var(--gray-800)' }}>
                <input
                  type="checkbox"
                  checked={userConfirmed}
                  onChange={(e) => setUserConfirmed(e.target.checked)}
                  style={{ marginTop: 3 }}
                />
                <span>
                  I confirm that I have reviewed all extracted and entered application details and verify their accuracy before saving/submitting.
                </span>
              </label>

              <div style={{ display: 'flex', gap: 12, marginTop: 14, flexWrap: 'wrap' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => handleSaveOrSubmit(true)}
                  disabled={submitting}
                >
                  <Save size={15} /> Save as Draft
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => handleSaveOrSubmit(false)}
                  disabled={submitting || !userConfirmed}
                >
                  <Send size={15} /> {submitting ? 'Submitting...' : 'Submit Direct Application'}
                </button>
              </div>
            </div>
          )}

          {currentScheme && (
            <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--gray-200)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>
                Official Submission URL: <strong>{currentScheme.source_url}</strong>
              </div>
              <a
                href={currentScheme.source_url}
                target="_blank"
                rel="noreferrer"
                className="btn btn-secondary"
              >
                Visit Official Portal
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
