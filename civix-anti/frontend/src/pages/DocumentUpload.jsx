import React, { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle2, AlertTriangle, Trash2, Eye, Cpu } from 'lucide-react';
import ContradictionAlerts from '../components/ContradictionAlerts';
import { uploadDocument, getUploadedDocuments, clearUploadedDocuments, updateProfile } from '../services/api';

export default function DocumentUpload({ onNavigateToProfile }) {
  const [documents, setDocuments] = useState([]);
  const [contradictions, setContradictions] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [selectedDocText, setSelectedDocText] = useState(null);
  const [textInputDoc, setTextInputDoc] = useState('');
  const [sampleDocType, setSampleDocType] = useState('Income Certificate');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const data = await getUploadedDocuments();
      setDocuments(data.documents || []);
      setContradictions(data.contradiction_alerts || []);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const res = await uploadDocument(file);
      setDocuments(prev => [...prev, res.document]);
      setContradictions(res.contradiction_alerts || []);
      
      // Merge newly extracted document entities into global user profile
      if (res.document?.extracted_profile) {
        await updateProfile(res.document.extracted_profile, true);
      }
    } catch (err) {
      alert("Error uploading document: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleSimulateTextUpload = async () => {
    if (!textInputDoc.trim()) return;
    
    // Create text file blob
    const blob = new Blob([textInputDoc], { type: 'text/plain' });
    const file = new File([blob], `${sampleDocType.replace(/\s+/g, '_')}_Scan.txt`, { type: 'text/plain' });

    setUploading(true);
    try {
      const res = await uploadDocument(file);
      setDocuments(prev => [...prev, res.document]);
      setContradictions(res.contradiction_alerts || []);
      
      if (res.document?.extracted_profile) {
        await updateProfile(res.document.extracted_profile, true);
      }
      setTextInputDoc('');
    } catch (err) {
      alert("Error processing simulated document: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleClear = async () => {
    await clearUploadedDocuments();
    setDocuments([]);
    setContradictions([]);
    setSelectedDocText(null);
  };

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--gray-900)' }}>
          Document Upload & OCR Processing
        </h1>
        <p style={{ color: 'var(--gray-600)', fontSize: '0.95rem' }}>
          Upload PDF or image certificates (Income, Domicile, College ID, Marks Card, Caste, Aadhaar). The pipeline executes OCR, document classification with confidence scores, NLP entity extraction, and contradiction checks across files.
        </p>
      </div>

      {/* Contradiction Alert Box */}
      <ContradictionAlerts alerts={contradictions} />

      <div className="grid-2">
        {/* File Upload Box */}
        <div className="card">
          <h3 className="card-title">
            <Upload size={18} color="var(--primary)" />
            Upload Certificate / Document File
          </h3>

          <div style={{
            border: '2px dashed var(--gray-300)',
            borderRadius: 12,
            padding: 24,
            textAlign: 'center',
            backgroundColor: 'var(--gray-50)',
            cursor: 'pointer',
            marginBottom: 16
          }}>
            <Upload size={36} color="var(--gray-600)" style={{ marginBottom: 12 }} />
            <p style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--gray-800)', margin: 0 }}>
              Drag & drop files or browse
            </p>
            <p style={{ fontSize: '0.8rem', color: 'var(--gray-600)', marginTop: 4 }}>
              Supports PDF, PNG, JPG, JPEG, TXT (Max 10MB)
            </p>
            <input
              type="file"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              id="file-input"
              accept=".pdf,.png,.jpg,.jpeg,.txt"
            />
            <label htmlFor="file-input" className="btn btn-primary" style={{ marginTop: 14 }}>
              {uploading ? 'Processing OCR...' : 'Select File'}
            </label>
          </div>

          <div style={{ borderTop: '1px solid var(--gray-200)', paddingTop: 16, marginTop: 16 }}>
            <h4 style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 8 }}>
              Or Paste Sample Document Text (Instant OCR Test):
            </h4>
            <div className="input-group">
              <label className="input-label">Document Type Hint:</label>
              <select className="form-select" value={sampleDocType} onChange={(e) => setSampleDocType(e.target.value)}>
                <option value="Income Certificate">Income Certificate</option>
                <option value="Residence Certificate">Residence Certificate</option>
                <option value="College ID">College ID</option>
                <option value="Marks Card">Marks Card</option>
                <option value="Caste Certificate">Caste Certificate</option>
                <option value="Disability Certificate">Disability Certificate</option>
              </select>
            </div>
            <textarea
              className="form-textarea"
              rows={3}
              placeholder="e.g. Government of Karnataka Income Certificate. This is to certify that annual family income of Rahul Kumar residing at Bengaluru is Rs. 1,80,000."
              value={textInputDoc}
              onChange={(e) => setTextInputDoc(e.target.value)}
            />
            <button className="btn btn-secondary" style={{ width: '100%', marginTop: 8 }} onClick={handleSimulateTextUpload} disabled={uploading}>
              Run OCR & NLP Extraction
            </button>
          </div>
        </div>

        {/* Uploaded Documents List & OCR Inspection */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 className="card-title" style={{ margin: 0 }}>
              <FileText size={18} color="var(--primary)" />
              Uploaded Documents ({documents.length})
            </h3>
            {documents.length > 0 && (
              <button className="btn btn-secondary" style={{ fontSize: '0.8rem', color: 'var(--danger)' }} onClick={handleClear}>
                <Trash2 size={14} /> Clear All
              </button>
            )}
          </div>

          {documents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 10px', color: 'var(--gray-600)' }}>
              No documents uploaded yet. Upload a certificate to view OCR results and detected entities.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {documents.map((doc, idx) => (
                <div key={idx} style={{ background: 'var(--gray-50)', padding: 14, borderRadius: 8, border: '1px solid var(--gray-200)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--gray-900)' }}>
                        {doc.file_name}
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center', marginTop: 4 }}>
                        <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                          Detected: {doc.document_type}
                        </span>
                        <span className={`badge ${doc.confidence >= 50 ? 'badge-matched' : 'badge-unknown'}`} style={{ fontSize: '0.75rem' }}>
                          Confidence: {doc.confidence}%
                        </span>
                        {doc.ocr_method && (
                          <span className="badge" style={{ fontSize: '0.7rem', background: 'var(--gray-200)', color: 'var(--gray-700)' }}>
                            OCR: {doc.ocr_method}
                          </span>
                        )}
                      </div>
                      {doc.secondary_types && doc.secondary_types.length > 0 && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', marginTop: 4 }}>
                          Also matched: {doc.secondary_types.join(', ')}
                        </div>
                      )}
                    </div>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                      onClick={() => setSelectedDocText(doc)}
                    >
                      <Eye size={12} /> Inspect Text
                    </button>
                  </div>

                  {/* Extracted Profile Snippet */}
                  {doc.extracted_profile && (
                    <div style={{ marginTop: 10, fontSize: '0.8rem', color: 'var(--gray-600)', background: '#ffffff', padding: 8, borderRadius: 6 }}>
                      Extracted: Income = {doc.extracted_profile.annual_income !== 'unknown' ? `₹${Number(doc.extracted_profile.annual_income).toLocaleString()}` : 'N/A'} | State = {doc.extracted_profile.state} | Edu = {doc.extracted_profile.education} | Category = {doc.extracted_profile.category}
                    </div>
                  )}
                  {doc.ocr_error && !doc.raw_text && (
                    <div style={{ marginTop: 6, fontSize: '0.75rem', color: 'var(--danger)' }}>
                      OCR note: {doc.ocr_error}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Raw OCR Text Modal / Drawer */}
      {selectedDocText && (
        <div className="card" style={{ marginTop: 20, borderTop: '4px solid var(--primary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <h3 className="card-title" style={{ margin: 0 }}>
              <Cpu size={18} color="var(--primary)" />
              Extracted Raw OCR Text - {selectedDocText.file_name}
            </h3>
            <button className="btn btn-secondary" style={{ padding: '4px 8px' }} onClick={() => setSelectedDocText(null)}>
              Close
            </button>
          </div>
          <pre style={{
            background: 'var(--gray-900)',
            color: '#38bdf8',
            padding: 16,
            borderRadius: 8,
            fontSize: '0.85rem',
            overflowX: 'auto',
            maxHeight: 300
          }}>
            {selectedDocText.raw_text || "No text extracted."}
          </pre>
        </div>
      )}
    </div>
  );
}
