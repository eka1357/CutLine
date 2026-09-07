import React from 'react'

export default function EvidenceDrawer({ evidence, onClose }) {
  if (!evidence) return null

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <h3 className="drawer-title">Verified Web Evidence</h3>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              PARALLEL SEARCH RUNTIME CITATION
            </span>
          </div>
          <button type="button" className="btn-close" onClick={onClose}>
            CLOSE ✕
          </button>
        </div>

        <div className="evidence-fact-card">
          <div className="fact-category">
            CATEGORY: {evidence.category ? evidence.category.replace('_', ' ') : 'RESEARCH FACT'}
          </div>

          <div className="fact-claim">
            "{evidence.claim}"
          </div>

          {evidence.evidence_text && (
            <div>
              <span className="alt-meta-label" style={{ display: 'block', marginBottom: '4px' }}>
                Verbatim Excerpt from Parallel Search:
              </span>
              <div className="fact-excerpt">
                {evidence.evidence_text}
              </div>
            </div>
          )}

          <div>
            <span className="alt-meta-label" style={{ display: 'block', marginBottom: '4px' }}>
              Authentic Source URL:
            </span>
            <a
              href={evidence.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="fact-link"
            >
              {evidence.source_url}
            </a>
          </div>

          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Domain: <strong>{evidence.source_domain}</strong> | Source: {evidence.source_title || 'Official Portal'}
          </div>
        </div>
      </div>
    </div>
  )
}
