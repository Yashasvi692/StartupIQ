import './LandingPage.css'

function LandingPage({ onStart }) {
  return (
    <div className="landing">
      <section className="hero-section">
        <h1 className="hero-title">StartupIQ</h1>
        <p className="hero-tagline">AI-powered Startup Validation & Market Intelligence Platform</p>
        <p className="hero-description">
          Transform your startup idea into an evidence-backed validation report.
          StartupIQ uses autonomous AI agents to research markets, analyze competitors,
          and deliver actionable recommendations.
        </p>
        <button className="cta-button" type="button" onClick={onStart}>
          Start Validation
        </button>
      </section>

      <section className="features-section">
        <h2>How It Works</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">1</div>
            <h3>Discover</h3>
            <p>Answer structured questions about your startup idea.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">2</div>
            <h3>Research</h3>
            <p>AI agents research markets, trends, and competitors.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">3</div>
            <h3>Analyze</h3>
            <p>Evidence is transformed into business insights and scores.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">4</div>
            <h3>Report</h3>
            <p>Receive a comprehensive validation report with recommendations.</p>
          </div>
        </div>
      </section>

      <section className="capabilities-section">
        <h2>What You Get</h2>
        <ul className="capabilities-list">
          <li>Market Analysis & Industry Trends</li>
          <li>Competitor Intelligence</li>
          <li>Customer Problem Validation</li>
          <li>Business Model Evaluation</li>
          <li>SWOT Analysis & Risk Assessment</li>
          <li>Validation Scorecard</li>
          <li>Strategic Recommendations</li>
        </ul>
      </section>
    </div>
  )
}

export default LandingPage
