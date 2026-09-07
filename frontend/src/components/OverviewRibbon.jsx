import React from 'react'

export default function OverviewRibbon({ plan }) {
  if (!plan) return null

  const { project_title, location, shoot_window, budget, production_type, crew_size, overall_decision, decision_counts } = plan

  return (
    <div className="overview-ribbon">
      <div className="overview-meta">
        <h2 className="overview-title">{project_title || 'PRODUCTION PLAN'}</h2>
        <div className="overview-details">
          <span>{location}</span>
          <span>•</span>
          <span>{shoot_window}</span>
          <span>•</span>
          <span>BUDGET: ${budget ? budget.toLocaleString() : 'N/A'}</span>
          {production_type && (
            <>
              <span>•</span>
              <span>SCALE: {production_type}</span>
            </>
          )}
          {crew_size && (
            <>
              <span>•</span>
              <span>CREW: {crew_size.split(' ')[0]}</span>
            </>
          )}
        </div>
      </div>

      <div className="status-counts">
        <div className={`status-badge ${overall_decision}`}>
          OVERALL: {overall_decision}
        </div>
        {decision_counts && (
          <>
            <span className="badge-tag highlight">GO: {decision_counts.GO || 0}</span>
            <span className="badge-tag" style={{ borderColor: 'var(--status-risk-border)', color: 'var(--status-risk)' }}>
              RISK: {decision_counts.RISK || 0}
            </span>
            <span className="badge-tag" style={{ borderColor: 'var(--status-blocked-border)', color: 'var(--status-blocked)' }}>
              BLOCKED: {decision_counts.BLOCKED || 0}
            </span>
          </>
        )}
      </div>
    </div>
  )
}
