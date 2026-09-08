import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import ProductionForm from './components/ProductionForm'
import PipelineProgress from './components/PipelineProgress'
import OverviewRibbon from './components/OverviewRibbon'
import SceneTimeline from './components/SceneTimeline'
import EvidenceDrawer from './components/EvidenceDrawer'
import { PRESETS } from './presets'
import { fetchHealth, streamProductionPipeline } from './api'

export default function App() {
  const [health, setHealth] = useState(null)
  const [activePreset, setActivePreset] = useState('neon_driftwood')
  const [formData, setFormData] = useState({
    screenplay: PRESETS.neon_driftwood.screenplay,
    location: PRESETS.neon_driftwood.location,
    shoot_start_date: PRESETS.neon_driftwood.shoot_start_date,
    shoot_end_date: PRESETS.neon_driftwood.shoot_end_date,
    budget: PRESETS.neon_driftwood.budget,
    production_type: PRESETS.neon_driftwood.production_type || 'Independent Feature',
    crew_size: PRESETS.neon_driftwood.crew_size || 'Medium (11-30 crew)',
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [plan, setPlan] = useState(null)
  const [selectedEvidence, setSelectedEvidence] = useState(null)
  const [liveSteps, setLiveSteps] = useState([])

  useEffect(() => {
    fetchHealth().then(setHealth)
  }, [])

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    setPlan(null)
    setLiveSteps([])
    try {
      const result = await streamProductionPipeline(formData, (step) => {
        setLiveSteps((prev) => [...prev, step])
      })
      setPlan(result)
    } catch (err) {
      console.error("Execution error:", err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <Header health={health} />

      <div className="main-grid">
        {/* Left Column: Configuration Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <ProductionForm
            activePreset={activePreset}
            setActivePreset={setActivePreset}
            formData={formData}
            setFormData={setFormData}
            onSubmit={handleSubmit}
            loading={loading}
          />

          <PipelineProgress loading={loading} completed={!!plan} liveSteps={liveSteps} />
        </div>

        {/* Right Column: Interactive Command Center Timeline */}
        <div>
          {error && (
            <div className="control-card" style={{ borderColor: 'var(--status-blocked-border)', background: 'var(--status-blocked-bg)', marginBottom: '20px' }}>
              <div style={{ color: 'var(--status-blocked)', fontWeight: '700' }}>
                PIPELINE EXECUTION ERROR
              </div>
              <p style={{ color: 'var(--text-primary)', fontSize: '13px' }}>{error}</p>
            </div>
          )}

          {plan ? (
            <>
              <OverviewRibbon plan={plan} />
              <SceneTimeline
                scenes={plan.scenes}
                onOpenEvidence={setSelectedEvidence}
              />
            </>
          ) : (
            <EmptyState />
          )}
        </div>
      </div>

      {selectedEvidence && (
        <EvidenceDrawer
          evidence={selectedEvidence}
          onClose={() => setSelectedEvidence(null)}
        />
      )}
    </div>
  )
}


/**
 * Pre-execution empty state showing the 5-stage pipeline architecture.
 * Gives judges an immediate understanding of the system without requiring execution.
 */
function EmptyState() {
  const stages = [
    { id: 1, label: 'Screenplay Breakdown', engine: 'Gemini (google-genai)', icon: 'S1' },
    { id: 2, label: 'Parallel Web Research', engine: 'Parallel Search SDK', icon: 'S2' },
    { id: 3, label: 'Evidence Engine', engine: 'Requirement Mapping', icon: 'S3' },
    { id: 4, label: 'Decision Engine', engine: 'Deterministic Rules', icon: 'S4' },
    { id: 5, label: 'Rewrite Strategist', engine: 'Gemini (google-genai)', icon: 'S5' },
  ]

  return (
    <div className="control-card empty-state-container">
      <div className="card-title">
        <span>Pipeline Architecture</span>
        <span className="badge-tag">5-STAGE DETERMINISTIC</span>
      </div>

      <div className="empty-state-pipeline">
        {stages.map((s, idx) => (
          <React.Fragment key={s.id}>
            <div className="empty-stage-node">
              <div className="empty-stage-icon">{s.icon}</div>
              <div className="empty-stage-info">
                <span className="empty-stage-label">{s.label}</span>
                <span className="empty-stage-engine">{s.engine}</span>
              </div>
            </div>
            {idx < stages.length - 1 && (
              <div className="empty-stage-connector">
                <svg width="24" height="16" viewBox="0 0 24 16" fill="none">
                  <path d="M0 8H20M20 8L14 2M20 8L14 14" stroke="var(--border-strong)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      <div className="empty-state-categories">
        <span className="section-label">5 Research Categories Queried via Parallel Search</span>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
          {['Filming Permits', 'Location Restrictions', 'Weather & Climate', 'Public Events', 'Regional Regulations'].map((cat) => (
            <span key={cat} className="badge-tag">{cat}</span>
          ))}
        </div>
      </div>

      <div className="empty-state-output">
        <span className="section-label">Output Per Scene</span>
        <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
          <span className="status-badge GO" style={{ padding: '4px 12px', fontSize: '11px' }}>GO</span>
          <span className="status-badge RISK" style={{ padding: '4px 12px', fontSize: '11px' }}>RISK</span>
          <span className="status-badge BLOCKED" style={{ padding: '4px 12px', fontSize: '11px' }}>BLOCKED</span>
        </div>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '10px', lineHeight: '1.5' }}>
          Each scene receives a deterministic verdict backed by verified web evidence and source URLs.
          RISK and BLOCKED scenes receive 2-3 concrete production alternatives preserving cinematic intent.
        </p>
      </div>
    </div>
  )
}
