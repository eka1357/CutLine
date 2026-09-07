import React from 'react'

export default function OverviewRibbon({ plan }) {
  if (!plan) return null

  const { project_title, location, shoot_window, budget, overall_decision, decision_counts } = plan

  return (
    <div className="overview-ribbon">
      <div className="overview-meta">
        <h2 className="overview-title">{project_title || 'PRODUCTION PLAN'}</h2>
        <div className="overview-details">
          {location} | {shoot_window} | BUDGET: ${budget ? budget.toLocaleString() : 'N/A'}
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
