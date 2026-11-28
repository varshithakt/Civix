import React from 'react';
import { Cpu, ArrowRight, CheckCircle2, Zap } from 'lucide-react';

export default function NLPPipelineVisualizer({ nlpResult, profile }) {
  if (!nlpResult && !profile) return null;

  const intent = nlpResult?.intent?.intent || 'FIND_SCHOLARSHIP';
  const confidence = nlpResult?.intent?.confidence || 0.95;

  return (
    <div className="card" style={{ borderLeft: '4px solid var(--primary)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h3 className="card-title" style={{ margin: 0 }}>
          <Cpu size={20} color="var(--primary)" />
          NLP Intelligence Pipeline Breakdown
        </h3>
        <span className="badge badge-info">
          <Zap size={12} /> Hybrid NLP Active
        </span>
      </div>

      <div className="pipeline-container">
        {/* Step 1: Query Input */}
        <div className="pipeline-step active">
          <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>STEP 1</div>
          <div style={{ fontWeight: 600, fontSize: '0.85rem', margin: '4px 0' }}>Raw Text / OCR</div>
          <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>Text Ingestion</span>
        </div>

        <ArrowRight size={16} color="var(--gray-300)" />

        {/* Step 2: Intent Classification */}
        <div className="pipeline-step active">
          <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>STEP 2</div>
          <div style={{ fontWeight: 600, fontSize: '0.85rem', margin: '4px 0' }}>Intent ML</div>
          <span className="badge badge-matched" style={{ fontSize: '0.7rem' }}>
            {intent} ({(confidence * 100).toFixed(0)}%)
          </span>
        </div>

        <ArrowRight size={16} color="var(--gray-300)" />

        {/* Step 3: Entity Extraction */}
        <div className="pipeline-step active">
          <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>STEP 3</div>
          <div style={{ fontWeight: 600, fontSize: '0.85rem', margin: '4px 0' }}>NER Parsing</div>
          <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>Age, State, Edu</span>
        </div>

        <ArrowRight size={16} color="var(--gray-300)" />

        {/* Step 4: Normalization */}
        <div className="pipeline-step active">
          <div style={{ fontSize: '0.75rem', color: 'var(--gray-600)', fontWeight: 600 }}>STEP 4</div>
          <div style={{ fontWeight: 600, fontSize: '0.85rem', margin: '4px 0' }}>Normalization</div>
          <span className="badge badge-matched" style={{ fontSize: '0.7rem' }}>
            {profile?.annual_income && profile.annual_income !== 'unknown' 
              ? `₹${Number(profile.annual_income).toLocaleString()}/yr` 
              : 'Income Standardized'}
          </span>
        </div>
      </div>
    </div>
  );
}
