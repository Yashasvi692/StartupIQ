import './ValidationMode.css'

const MODES = [
  {
    id: 'quick',
    title: 'Quick Validation',
    description: 'Rapid idea screening with essential research and an executive summary.',
    estimate: '2-3 minutes',
    features: [
      'Simplified analysis',
      'Essential market research',
      'Executive summary report',
      'Key risk identification',
    ],
  },
  {
    id: 'deep',
    title: 'Deep Validation',
    description: 'Comprehensive investor-grade analysis with multi-agent research.',
    estimate: '10-20 minutes',
    features: [
      'Complete market intelligence',
      'Multi-agent AI research',
      'Detailed investor-style report',
      'SWOT & Risk Assessment',
      'Validation Scorecard',
      'Strategic recommendations',
    ],
  },
]

function ValidationMode({ onSelect, error, loading }) {
  return (
    <div className="mode-page">
      <header className="mode-header">
        <h1>Choose Validation Mode</h1>
        <p className="mode-subtitle">
          Select how deeply you want our AI agents to analyze your startup idea.
        </p>
        {error && <p className="mode-error">{error}</p>}
        {loading && (
          <div className="loading-state">
            <div className="spinner" />
            <p>Creating validation job...</p>
          </div>
        )}
      </header>

      <div className={`mode-cards${loading ? ' mode-cards-loading' : ''}`}>
        {MODES.map((mode) => (
          <button
            key={mode.id}
            type="button"
            className="mode-card"
            onClick={() => onSelect(mode.id)}
          >
            <h2 className="mode-card-title">{mode.title}</h2>
            <p className="mode-card-description">{mode.description}</p>
            <span className="mode-estimate">~{mode.estimate}</span>
            <ul className="mode-features">
              {mode.features.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
          </button>
        ))}
      </div>
    </div>
  )
}

export default ValidationMode
