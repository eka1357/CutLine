import React from 'react'

const STAGES = [
  { id: 1, name: 'Screenplay Breakdown', agent: 'Gemini 3.6 Flash (google-genai)', desc: 'Parsing scenes, locations, and shoot implications' },
  { id: 2, name: 'Parallel Web Research', agent: 'Parallel Search API (turbo)', desc: 'Querying permits, curfews, weather, events, & safety regulations' },
  { id: 3, name: 'Evidence Engine', agent: 'Grounding & Provenance Engine', desc: 'Linking requirements to authentic HTTP(S) source evidence' },
  { id: 4, name: 'Production Decision Engine', agent: 'Deterministic Python Rule Engine', desc: 'Evaluating GO / RISK / BLOCKED with unbroken provenance' },
  { id: 5, name: 'Rewrite Strategist', agent: 'Gemini 3.6 Flash (google-genai)', desc: 'Generating actionable production rewrites for flagged scenes' },
]

/**
 * Derives the current active stage number and latest detail message
 * from the live SSE step messages array.
 */
function deriveProgress(liveSteps) {
  if (!liveSteps || liveSteps.length === 0) return { currentStage: 1, stageDetails: {} }

  let currentStage = 1
  const stageDetails = {}

  for (const step of liveSteps) {
    const stage = step.stage || 0
    if (stage >= 1 && stage <= 5) {
      currentStage = stage
      stageDetails[stage] = step.message
    }
  }

  return { currentStage, stageDetails }
}

export default function PipelineProgress({ loading, completed, liveSteps }) {
  if (!loading && !completed) return null

  const isAllComplete = !loading && completed
  const { currentStage, stageDetails } = isAllComplete
    ? { currentStage: 6, stageDetails: {} }
    : deriveProgress(liveSteps)

  return (
    <div className="pipeline-progress">
      <div className="card-title">
        <span>{isAllComplete ? 'Autonomous Agent Pipeline Complete' : 'Autonomous Agent Pipeline Active'}</span>
        {isAllComplete ? (
          <span className="badge-tag highlight">ALL 5 STAGES VERIFIED</span>
        ) : (
          <span className="badge-tag cyan">STAGE {Math.min(currentStage, 5)} OF 5</span>
        )}
      </div>

      <div className="stage-list">
        {STAGES.map((s) => {
          const isCompleted = currentStage > s.id
          const isActive = currentStage === s.id && !isAllComplete
          const detail = stageDetails[s.id] || null

          return (
            <div
              key={s.id}
              className={`stage-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
            >
              <div className="stage-number">{isCompleted ? '✓' : s.id}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>Stage {s.id}: {s.name}</span>
                  {isActive && <span className="pulse-indicator"></span>}
                </div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  {s.agent}
                </span>
                {/* Live detail message from SSE */}
                {(isActive || isCompleted) && detail && (
                  <span className="stage-live-detail">
                    {formatDetailMessage(detail)}
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

/**
 * Cleans up raw pipeline log messages into user-facing progress text.
 */
function formatDetailMessage(msg) {
  if (!msg) return ''
  // Remove "STAGE N:" prefix noise
  let cleaned = msg.replace(/^STAGE \d:\s*/i, '')
  // Truncate very long messages
  if (cleaned.length > 120) {
    cleaned = cleaned.slice(0, 117) + '...'
  }
  return cleaned
}
