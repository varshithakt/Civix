import React from 'react';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

export default function ContradictionAlerts({ alerts }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div style={{ marginBottom: 20 }}>
      {alerts.map((alert, idx) => (
        <div key={idx} className="alert-box alert-warning">
          <AlertTriangle size={20} color="var(--warning)" style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: 2 }}>
              {alert.title}
            </div>
            <div style={{ fontSize: '0.85rem' }}>
              {alert.description}
            </div>
            {alert.conflicting_documents && (
              <div style={{ fontSize: '0.75rem', marginTop: 6, fontWeight: 600, color: '#b45309' }}>
                Conflicting documents: {alert.conflicting_documents.join(' ↔ ')}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
