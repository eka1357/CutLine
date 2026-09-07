import React, { useEffect, useState } from 'react'

const STAGES = [
  { id: 1, name: 'Stage 1: Screenplay Breakdown', agent: 'Gemini 3.6 Flash (google-genai)', desc: 'Parsing scenes, locations, and shoot implications' },
  { id: 2, name: 'Stage 2: Parallel Web Research', agent: 'Parallel Search API (turbo)', desc: 'Querying permits, curfews, weather, events, & safety regulations' },
  { id: 3, name: 'Stage 3: Evidence Engine', agent: 'Grounding & Provenance Engine', desc: 'Linking requirements to authentic HTTP(S) source evidence' },
  { id: 4, name: 'Stage 4: Production Decision Engine', agent: 'Deterministic Python Rule Engine', desc: 'Evaluating GO / RISK / BLOCKED with unbroken provenance' },
  { id: 5, name: 'Stage 5: Rewrite Strategist', agent: 'Gemini 3.6 Flash (google-genai)', desc: 'Generating actionable production rewrites for flagged scenes' },
]

export default function PipelineProgress({ loading }) {
  const [currentStage, setCurrentStage] = useState(1)

  useEffect(() => {
    if (!loading) {
      setCurrentStage(1)
      return
    }

    // Progression timer to reflect live pipeline execution phases
    const timer1 = setTimeout(() => setCurrentStage(2), 2500)
    const timer2 = setTimeout(() => setCurrentStage(3), 12000)
    const timer3 = setTimeout(() => setCurrentStage(4), 16000)
    const timer4 = setTimeout(() => setCurrentStage(5), 20000)

    return () => {
      clearTimeout(timer1)
      clearTimeout(timer2)
      clearTimeout(timer3)
      clearTimeout(timer4)
    }
  }, [loading])

  if (!loading) return null

  return (
    <div className="pipeline-progress">
      <div className="card-title">
        <span>Autonomous Agent Pipeline Active</span>
        <span className="badge-tag cyan">STAGE {currentStage} OF 5</span>
      </div>

      <div className="stage-list">
        {STAGES.map((s) => {
          const isCompleted = currentStage > s.id
          const isActive = currentStage === s.id

          return (
            <div
              key={s.id}
              className={`stage-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
            >
              <div className="stage-number">{isCompleted ? '✓' : s.id}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>{s.name}</span>
                  {isActive && <span className="pulse-indicator"></span>}
                </div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  {s.agent} — {s.desc}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
