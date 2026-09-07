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
      })
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <div className="control-card">
      <div className="card-title">
        <span>Production Parameters</span>
        <div className="preset-switcher">
          <button
            type="button"
            className={`preset-btn ${activePreset === 'neon_driftwood' ? 'active' : ''}`}
            onClick={() => handlePresetSelect('neon_driftwood')}
          >
            Santa Monica (Neon Driftwood)
          </button>
          <button
            type="button"
            className={`preset-btn ${activePreset === 'lakefront_cipher' ? 'active' : ''}`}
            onClick={() => handlePresetSelect('lakefront_cipher')}
          >
            Chicago (Lakefront Cipher)
          </button>
        </div>
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
