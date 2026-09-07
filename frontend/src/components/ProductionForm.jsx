import React from 'react'
import { PRESETS } from '../presets'

export default function ProductionForm({
  activePreset,
  setActivePreset,
  formData,
  setFormData,
  onSubmit,
  loading,
}) {
  const handlePresetSelect = (presetKey) => {
    setActivePreset(presetKey)
    if (presetKey === 'custom') return

    const preset = PRESETS[presetKey]
    if (preset) {
      setFormData({
        screenplay: preset.screenplay,
        location: preset.location,
        shoot_start_date: preset.shoot_start_date,
        shoot_end_date: preset.shoot_end_date,
        budget: preset.budget,
        production_type: preset.production_type || 'Independent Feature',
        crew_size: preset.crew_size || 'Medium (11-30 crew)',
      })
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <div className="control-card">
      {/* Dedicated Screenplay Preset Scenarios Section */}
      <div className="presets-block">
        <div className="section-header-row">
          <span className="section-label">Demo Screenplay Presets</span>
          <span className="badge-tag cyan">3 JURISDICTIONS</span>
        </div>
        <p className="presets-subtitle">
          Select an original scenario or customize parameters and script below:
        </p>
        <div className="preset-cards-grid">
          <button
            type="button"
            className={`preset-card-btn ${activePreset === 'neon_driftwood' ? 'active' : ''}`}
            onClick={() => handlePresetSelect('neon_driftwood')}
          >
            <div className="preset-card-header">
              <span className="preset-city">SANTA MONICA</span>
              <span className="badge-tag highlight">COASTAL</span>
            </div>
            <div className="preset-title-text">Neon Driftwood</div>
            <div className="preset-desc-text">Pier chase, drone, blank gunfire, tide hazard</div>
          </button>

          <button
            type="button"
            className={`preset-card-btn ${activePreset === 'lakefront_cipher' ? 'active' : ''}`}
            onClick={() => handlePresetSelect('lakefront_cipher')}
          >
            <div className="preset-card-header">
              <span className="preset-city">CHICAGO</span>
              <span className="badge-tag cyan">RIVERWALK</span>
            </div>
            <div className="preset-title-text">The Lakefront Cipher</div>
            <div className="preset-desc-text">River promenade pursuit, drone sweep, freezing fog</div>
          </button>

          <button
            type="button"
            className={`preset-card-btn ${activePreset === 'empire_lockdown' ? 'active' : ''}`}
            onClick={() => handlePresetSelect('empire_lockdown')}
          >
            <div className="preset-card-header">
              <span className="preset-city">NEW YORK</span>
              <span className="badge-tag" style={{ color: 'var(--status-risk)', borderColor: 'var(--status-risk-border)' }}>MANHATTAN</span>
            </div>
            <div className="preset-title-text">Empire Lockdown</div>
            <div className="preset-desc-text">Brooklyn Bridge walkway, blank rounds, UN security</div>
          </button>
        </div>
      </div>

      <div className="divider-line" />

      {/* Production Parameters Section */}
      <div className="card-title">
        <span>Production Parameters</span>
        <span className="badge-tag">FEASIBILITY INPUTS</span>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="location">Shoot Location (City, Region)</label>
        <input
          id="location"
          type="text"
          name="location"
          className="form-input"
          value={formData.location}
          onChange={handleChange}
          placeholder="e.g. Santa Monica, CA"
          required
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label" htmlFor="shoot_start_date">Window Start</label>
          <input
            id="shoot_start_date"
            type="date"
            name="shoot_start_date"
            className="form-input"
            value={formData.shoot_start_date}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="shoot_end_date">Window End</label>
          <input
            id="shoot_end_date"
            type="date"
            name="shoot_end_date"
            className="form-input"
            value={formData.shoot_end_date}
            onChange={handleChange}
            required
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label" htmlFor="budget">Production Budget ($ USD)</label>
          <input
            id="budget"
            type="number"
            name="budget"
            className="form-input"
            value={formData.budget}
            onChange={handleChange}
            step="5000"
            required
          />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="production_type">Production Scale</label>
          <select
            id="production_type"
            name="production_type"
            className="form-select"
            value={formData.production_type || 'Independent Feature'}
            onChange={handleChange}
          >
            <option value="Independent Feature">Independent Feature</option>
            <option value="Commercial / Brand">Commercial / Brand</option>
            <option value="Student / Micro-Budget">Student / Micro-Budget</option>
            <option value="Documentary / Run-and-Gun">Documentary / Run-and-Gun</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="crew_size">Estimated Crew Footprint</label>
        <select
          id="crew_size"
          name="crew_size"
          className="form-select"
          value={formData.crew_size || 'Medium (11-30 crew)'}
          onChange={handleChange}
        >
          <option value="Small (1-10 crew)">Small (1-10 crew — minimal equipment impact)</option>
          <option value="Medium (11-30 crew)">Medium (11-30 crew — standard indie package)</option>
          <option value="Standard (31-60 crew)">Standard (31-60 crew — commercial/trucks)</option>
          <option value="Large (60+ crew)">Large (60+ crew — full street closure footprint)</option>
        </select>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="screenplay">Screenplay Draft (Fountain / Standard Script Text)</label>
        <textarea
          id="screenplay"
          name="screenplay"
          className="form-textarea"
          value={formData.screenplay}
          onChange={handleChange}
          rows={12}
          placeholder="PASTE SCREENPLAY HERE..."
          required
        />
      </div>

      <button
        type="button"
        className="btn-primary"
        onClick={onSubmit}
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="pulse-indicator"></span>
            INVESTIGATING PRODUCTION CONSTRAINTS...
          </>
        ) : (
          'EXECUTE PRODUCTION PLANNING AGENT'
        )}
      </button>
    </div>
  )
}
