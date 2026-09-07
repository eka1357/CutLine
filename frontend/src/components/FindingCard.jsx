import React from 'react'

export default function FindingCard({ finding, onOpenEvidence }) {
  return (
    <div className="finding-item">
      <div className="finding-header">
        <span className="finding-rule-name">{finding.rule_name}</span>
        <span className={`status-badge ${finding.consequence}`} style={{ padding: '3px 8px', fontSize: '10px' }}>
          {finding.consequence}
        </span>
      </div>

      <div className="finding-provenance-chain">
        <span>REQUIREMENT: {finding.requirement_name}</span>
        <span>→</span>
        <span>RULE: {finding.rule_name}</span>
        <span>→</span>
        <span>CONSEQUENCE: {finding.consequence}</span>
      </div>

      <p className="finding-reason">{finding.reason}</p>

      {finding.supporting_evidence?.length > 0 && (
        <div className="evidence-tags">
          {finding.supporting_evidence.map((ev, idx) => (
            <button
              key={idx}
              type="button"
              className="evidence-btn"
              onClick={() => onOpenEvidence(ev)}
              title="Click to view verified source evidence"
            >
              <span>SOURCE:</span>
              <strong>{ev.source_domain || 'web citation'}</strong>
              <span>↗</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
