import React from 'react'
import FindingCard from './FindingCard'
import RewritePanel from './RewritePanel'

export default function SceneTimeline({ scenes, onOpenEvidence }) {
  if (!scenes?.length) return null

  return (
    <div className="scenes-container">
      {scenes.map((scene) => (
        <div key={scene.scene_id} className="scene-card">
          <div className="scene-header">
            <div>
              <h3 className="scene-heading-text">{scene.heading}</h3>
              <div className="scene-meta-row">
                <span>{scene.interior_exterior}</span>
                <span>•</span>
                <span>{scene.time_of_day}</span>
                <span>•</span>
                <span>SETTING: {scene.setting}</span>
              </div>
            </div>
            <div className={`status-badge ${scene.decision}`}>
              {scene.decision}
            </div>
          </div>

          <div className="scene-summary-box">
            <strong>Verdict Assessment:</strong> {scene.decision_summary}
          </div>

          {scene.requirements?.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <span className="section-label">Screenplay Production Requirements:</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {scene.requirements.map((req, idx) => (
                  <span key={idx} className="badge-tag">
                    {req}
                  </span>
                ))}
              </div>
            </div>
          )}

          {scene.findings?.length > 0 && (
            <div className="findings-section">
              <span className="section-label">Deterministic Rule Findings ({scene.findings.length}):</span>
              {scene.findings.map((f) => (
                <FindingCard
                  key={f.finding_id}
                  finding={f}
                  onOpenEvidence={onOpenEvidence}
                />
              ))}
            </div>
          )}

          {scene.alternatives?.length > 0 && (
            <RewritePanel alternatives={scene.alternatives} />
          )}
        </div>
      ))}
    </div>
  )
}
