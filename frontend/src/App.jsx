import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import ProductionForm from './components/ProductionForm'
import PipelineProgress from './components/PipelineProgress'
import OverviewRibbon from './components/OverviewRibbon'
import SceneTimeline from './components/SceneTimeline'
import EvidenceDrawer from './components/EvidenceDrawer'
import { PRESETS } from './presets'
import { fetchHealth, runProductionPipeline } from './api'

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

  useEffect(() => {
    fetchHealth().then(setHealth)
  }, [])

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await runProductionPipeline(formData)
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

          <PipelineProgress loading={loading} completed={!!plan} />
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
            <div className="control-card" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
              <h3 style={{ fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '8px', textTransform: 'uppercase' }}>
                Production Timeline Awaiting Execution
              </h3>
              <p style={{ fontSize: '13px', maxWidth: '440px', margin: '0 auto' }}>
                Select a screenplay preset or paste your own script, configure the proposed shoot location and window, and execute CutLine to investigate real-world constraints via live Parallel Search and Gemini.
              </p>
            </div>
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
