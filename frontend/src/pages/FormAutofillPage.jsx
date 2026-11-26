import React, { useState, useEffect } from 'react';
import { CheckSquare, AlertCircle, FileCheck, ShieldAlert, ArrowLeft, Copy, Check } from 'lucide-react';
import { getCurrentProfile, getAutofillPreview, getAllSchemes } from '../services/api';

export default function FormAutofillPage({ schemeId, onBack }) {
  const [schemes, setSchemes] = useState([]);
  const [selectedId, setSelectedId] = useState(schemeId || 'SCH001');
  const [formFields, setFormFields] = useState([]);
  const [disclaimer, setDisclaimer] = useState('');
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadData();
  }, [selectedId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const schData = await getAllSchemes();
      setSchemes(schData.schemes || []);

      const profData = await getCurrentProfile();
      const preview = await getAutofillPreview(selectedId, profData.profile || {});

      setFormFields(preview.form_fields || []);
      setDisclaimer(preview.disclaimer || '');
    } catch (err) {
      console.error("Error loading autofill preview", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = (fieldId, newValue) => {
    setFormFields(prev => prev.map(f => f.field_id === fieldId ? { ...f, value: newValue } : f));
  };

  const handleCopySummary = () => {
    const summary = formFields.map(f => `${f.label}: ${f.value}`).join('\n');
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const currentScheme = schemes.find(s => s.id === selectedId);

  return (
    <div style={{ maxWidth: 880, margin: '0 auto' }}>
      {onBack && (
        <button className="btn btn-secondary" style={{ marginBottom: 16 }} onClick={onBack}>
          <ArrowLeft size={16} /> Back to Scheme Details
        </button>
      )}

      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--gray-900)' }}>
          Application Form Auto-Fill Preview
        </h1>
        <p style={{ color: 'var(--gray-600)', fontSize: '0.95rem' }}>
          Extracted profile fields pre-populated for your review. You can modify any value before copying or completing official submission.
        </p>
      </div>

      {/* Security & Submission Alert */}
      <div className="alert-box alert-warning">
        <ShieldAlert size={20} color="var(--warning)" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <strong style={{ fontSize: '0.95rem' }}>Mandatory Verification Notice:</strong>
          <div style={{ fontSize: '0.85rem', marginTop: 2 }}>
            Applications are <strong>never automatically submitted</strong>. Please thoroughly review all pre-filled fields below for accuracy before using them on official government portals.
          </div>
        </div>
      </div>

      {/* Scheme Selector */}
      <div className="card">
        <div className="input-group" style={{ margin: 0 }}>
          <label className="input-label">Select Target Scheme Application Form:</label>
          <select
            className="form-select"
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
          >
            {schemes.map(s => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.category})
              </option>
            ))}
          </select>
        </div>
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
                  <span className={`badge ${field.status === 'confirmed' || field.status === 'extracted' ? 'badge-matched' : 'badge-unknown'}`} style={{ fontSize: '0.7rem' }}>
                    {field.status}
                  </span>
                </div>
                <input
                  type="text"
                  className="form-input"
                  value={field.value}
                  onChange={(e) => handleFieldChange(field.field_id, e.target.value)}
                />
              </div>
            ))}
          </div>

          {currentScheme && (
            <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--gray-200)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>
                Official Submission URL: <strong>{currentScheme.source_url}</strong>
              </div>
              <a
                href={currentScheme.source_url}
                target="_blank"
                rel="noreferrer"
                className="btn btn-primary"
              >
                Proceed to Official Portal
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
