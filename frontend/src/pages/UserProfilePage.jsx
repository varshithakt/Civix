import React, { useState, useEffect } from 'react';
import { User, Save, RefreshCw, CheckCircle2, HelpCircle } from 'lucide-react';
import { getCurrentProfile, updateProfile } from '../services/api';

export default function UserProfilePage({ onNavigateToSchemes }) {
  const [profile, setProfile] = useState({
    name: 'Rahul Kumar',
    age: 20,
    annual_income: 180000,
    income_type: 'family',
    education: 'engineering',
    state: 'Karnataka',
    district: 'Bengaluru',
    occupation: 'student',
    category: 'General',
    gender: 'Male',
    disability_pct: 'unknown'
  });

  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await getCurrentProfile();
      if (data.profile) {
        setProfile(prev => ({ ...prev, ...data.profile }));
      }
    } catch (err) {
      console.error("Error fetching profile", err);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await updateProfile(profile);
      setMsg('Profile updated successfully!');
      setTimeout(() => setMsg(''), 3000);
    } catch (err) {
      alert("Error saving profile: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--gray-900)' }}>
          Structured User Profile
        </h1>
        <p style={{ color: 'var(--gray-600)', fontSize: '0.95rem' }}>
          Normalized profile parameters extracted by NLP from natural language queries and document OCR. You can manually edit or confirm any value before scheme eligibility execution.
        </p>
      </div>

      {msg && (
        <div className="alert-box alert-info">
          <CheckCircle2 size={18} color="var(--primary)" />
          <div>{msg}</div>
        </div>
      )}

      <form onSubmit={handleSave} className="card">
        <h3 className="card-title">
          <User size={18} color="var(--primary)" />
          Personal & Eligibility Attributes
        </h3>

        <div className="grid-2">
          {/* Full Name */}
          <div className="input-group">
            <label className="input-label">Applicant Name:</label>
            <input
              type="text"
              className="form-input"
              value={profile.name}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
            />
          </div>

          {/* Age */}
          <div className="input-group">
            <label className="input-label">Age (Years):</label>
            <input
              type="text"
              className="form-input"
              value={profile.age}
              onChange={(e) => setProfile({ ...profile, age: e.target.value })}
            />
          </div>

          {/* Annual Household Income */}
          <div className="input-group">
            <label className="input-label">Annual Family Income (₹):</label>
            <input
              type="text"
              className="form-input"
              value={profile.annual_income}
              onChange={(e) => setProfile({ ...profile, annual_income: e.target.value })}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--gray-600)' }}>
              Normalized from monthly or lakh expressions (e.g. ₹1.8L → 180,000)
            </span>
          </div>

          {/* Education */}
          <div className="input-group">
            <label className="input-label">Education Level:</label>
            <select
              className="form-select"
              value={profile.education}
              onChange={(e) => setProfile({ ...profile, education: e.target.value })}
            >
              <option value="school">School (Class 1-12)</option>
              <option value="higher secondary">Higher Secondary (11th/12th/PUC)</option>
              <option value="undergraduate">Undergraduate (General Degree)</option>
              <option value="engineering">Engineering / B.Tech / BE</option>
              <option value="diploma">Diploma / Polytechnic</option>
              <option value="postgraduate">Postgraduate (Master Degree)</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>

          {/* State */}
          <div className="input-group">
            <label className="input-label">State Domicile:</label>
            <input
              type="text"
              className="form-input"
              value={profile.state}
              onChange={(e) => setProfile({ ...profile, state: e.target.value })}
            />
          </div>

          {/* District */}
          <div className="input-group">
            <label className="input-label">District:</label>
            <input
              type="text"
              className="form-input"
              value={profile.district}
              onChange={(e) => setProfile({ ...profile, district: e.target.value })}
            />
          </div>

          {/* Category */}
          <div className="input-group">
            <label className="input-label">Caste / Social Category:</label>
            <select
              className="form-select"
              value={profile.category}
              onChange={(e) => setProfile({ ...profile, category: e.target.value })}
            >
              <option value="General">General / Unreserved</option>
              <option value="OBC">OBC (Other Backward Classes)</option>
              <option value="SC">SC (Scheduled Caste)</option>
              <option value="ST">ST (Scheduled Tribe)</option>
              <option value="EWS">EWS (Economically Weaker Section)</option>
              <option value="Minority">Minority</option>
            </select>
          </div>

          {/* Occupation */}
          <div className="input-group">
            <label className="input-label">Occupation:</label>
            <select
              className="form-select"
              value={profile.occupation}
              onChange={(e) => setProfile({ ...profile, occupation: e.target.value })}
            >
              <option value="student">Student</option>
              <option value="farmer">Farmer / Agriculture</option>
              <option value="entrepreneur">Entrepreneur / Small Business</option>
              <option value="self-employed">Self-Employed</option>
              <option value="unemployed">Unemployed</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>

          {/* Gender */}
          <div className="input-group">
            <label className="input-label">Gender:</label>
            <select
              className="form-select"
              value={profile.gender}
              onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
            >
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>

          {/* Disability % */}
          <div className="input-group">
            <label className="input-label">Disability Percentage (%):</label>
            <input
              type="text"
              className="form-input"
              value={profile.disability_pct}
              onChange={(e) => setProfile({ ...profile, disability_pct: e.target.value })}
              placeholder="e.g. 40 or unknown"
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            <Save size={16} /> Save Confirmed Profile
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onNavigateToSchemes}
          >
            Run Scheme Eligibility Match →
          </button>
        </div>
      </form>
    </div>
  );
}
