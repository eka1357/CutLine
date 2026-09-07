import React, { useState } from 'react'

export default function RewritePanel({ alternatives }) {
  if (!alternatives?.length) return null

  const [activeTab, setActiveTab] = useState(0)
  const currentAlt = alternatives[activeTab] || alternatives[0]

  const formatStrategyType = (type) => {
    switch (type) {
      case 'timing_shift':
        return 'Timing / Schedule Shift'
      case 'technical_rewrite':
        return 'Technical / Mechanics Rewrite'
      case 'location_swap':
        return 'Location Swap'
      case 'procedural_mitigation':
        return 'Procedural Mitigation'
      default:
        return type ? type.replace(/_/g, ' ') : ''
    }
  }

  return (
    <div className="alternatives-container">
      <div className="card-title">
        <span>Stage 5: Actionable Production Alternatives</span>
        <span className="badge-tag cyan">{alternatives.length} STRATEGIES PROPOSED</span>
      </div>

      <div className="alt-tabs">
        {alternatives.map((alt, idx) => (
          <button
            key={alt.alternative_id || idx}
            type="button"
            className={`alt-tab-btn ${activeTab === idx ? 'active' : ''}`}
            onClick={() => setActiveTab(idx)}
          >
            {alt.title || `Strategy ${idx + 1}`} ({formatStrategyType(alt.strategy_type)})
          </button>
        ))}
      </div>

      {currentAlt && (
        <div className="alt-details">
          <div className="alt-meta-grid">
            <div className="alt-meta-item">
              <span className="alt-meta-label">Constraint Removed</span>
              <span className="alt-meta-value">{currentAlt.constraint_removed}</span>
            </div>
            <div className="alt-meta-item">
              <span className="alt-meta-label">Production Mechanism Change</span>
              <span className="alt-meta-value">{currentAlt.production_mechanism_change}</span>
            </div>
            <div className="alt-meta-item">
              <span className="alt-meta-label">Cinematic Intent Preserved</span>
              <span className="alt-meta-value">{currentAlt.cinematic_intent_preserved}</span>
            </div>
            <div className="alt-meta-item">
              <span className="alt-meta-label">Operational Trade-off & Impact</span>
              <span className="alt-meta-value">{currentAlt.estimated_impact}</span>
            </div>
          </div>

          {currentAlt.rewritten_scene_excerpt && (
            <div style={{ marginTop: '8px' }}>
              <span className="alt-meta-label" style={{ display: 'block', marginBottom: '6px' }}>
                Screenplay Draft Excerpt (Director-Ready)
              </span>
              <div className="script-excerpt-box">
                {currentAlt.rewritten_scene_excerpt}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
