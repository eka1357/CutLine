import React from 'react'

export default function Header({ health }) {
  const isHealthy = health && health.status === 'healthy'

  return (
    <header className="site-header">
      <div className="brand-group">
        <h1 className="brand-title">
          CUTLINE
          <span className="badge-tag highlight">PARALLEL TRACK</span>
        </h1>
        <p className="brand-tagline">
          Autonomous Production-Planning Agent / Reality-Testing Screenplays via Live Parallel Search & Gemini
        </p>
      </div>

      <div className="system-badges">
        <span className="badge-tag">GOOGLE CLOUD GEMINI 3.6 FLASH</span>
        <span className="badge-tag cyan">PARALLEL SEARCH SDK RUNTIME</span>
        <span className={`badge-tag ${isHealthy ? 'highlight' : ''}`}>
          {isHealthy ? 'SYSTEM ONLINE' : 'CONNECTING...'}
        </span>
      </div>
    </header>
  )
}
