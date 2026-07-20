import { useState, useEffect } from 'react'
import { getJobReport } from '../services/api'
import './ValidationReport.css'

function Section({ title, children }) {
  if (!children) return null
  return (
    <section className="report-section">
      <h2 className="report-section-title">{title}</h2>
      <div className="report-section-body">{children}</div>
    </section>
  )
}

function toMarkdown(report) {
  const lines = []

  function heading(text) {
    lines.push('', `## ${text}`, '')
  }

  function body(text) {
    if (text) lines.push(text, '')
  }

  function list(items) {
    if (items?.length) {
      items.forEach((item) => lines.push(`- ${item}`))
      lines.push('')
    }
  }

  lines.push('# Validation Report', '')
  lines.push(`**Overall Score: ${Math.round(report.overall_score)}/100**`, '')

  heading('Executive Summary'); body(report.executive_summary)
  heading('Startup Snapshot'); body(report.startup_snapshot)
  heading('Problem Analysis'); body(report.problem_analysis)
  heading('Market Analysis'); body(report.market_analysis)
  heading('Industry Trends'); body(report.industry_trends)
  heading('Competitor Landscape'); body(report.competitor_landscape)
  heading('Customer Validation'); body(report.customer_validation)
  heading('Business Model Evaluation'); body(report.business_model_evaluation)
  heading('Technical Feasibility'); body(report.technical_feasibility)
  heading('SWOT Analysis'); body(report.swot_analysis)
  heading('Risk Assessment'); body(report.risk_assessment)

  if (report.validation_scorecard && Object.keys(report.validation_scorecard).length > 0) {
    heading('Validation Scorecard')
    Object.entries(report.validation_scorecard).forEach(([key, dim]) => {
      lines.push(`### ${key}`)
      lines.push(`- Score: ${Math.round(dim.score)}/100`)
      lines.push(`- Confidence: ${Math.round(dim.confidence * 100)}%`)
      if (dim.explanation) lines.push(`- ${dim.explanation}`)
      if (dim.evidence) lines.push(`  > ${dim.evidence}`)
      lines.push('')
    })
  }

  heading('Strategic Recommendations'); list(report.strategic_recommendations)
  heading('Suggested Next Steps'); list(report.suggested_next_steps)
  heading('References'); list(report.references)

  return lines.join('\n')
}

function downloadMarkdown(report) {
  const markdown = toMarkdown(report)
  const blob = new Blob([markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'startupiq-validation-report.md'
  a.click()
  URL.revokeObjectURL(url)
}

function ValidationReport({ jobId }) {
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const data = await getJobReport(jobId)
        setReport(data.report)
      } catch (err) {
        setError(err.message)
      }
    }
    load()
  }, [jobId])

  if (error) {
    return (
      <div className="report-page">
        <p className="report-error">
          Unable to load the validation report. Please try again later.
        </p>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="report-page">
        <div className="loading-state">
          <div className="spinner" />
          <p>Loading report...</p>
        </div>
      </div>
    )
  }

  const score = report.overall_score
  const scoreColor = score >= 70 ? '#22c55e' : score >= 40 ? '#f59e0b' : '#ef4444'

  return (
    <div className="report-page">
      <header className="report-header">
        <h1>Validation Report</h1>
        <div className="export-buttons">
          <button type="button" className="export-btn" onClick={() => downloadMarkdown(report)}>
            Export Markdown
          </button>
          <button type="button" className="export-btn export-btn-disabled" disabled title="Coming in a future version">
            Export PDF
          </button>
        </div>
        <div className="overall-score" style={{ borderColor: scoreColor }}>
          <span className="overall-score-value" style={{ color: scoreColor }}>
            {Math.round(score)}
          </span>
          <span className="overall-score-label">Overall Score</span>
        </div>
      </header>

      <Section title="Executive Summary">{report.executive_summary}</Section>
      <Section title="Startup Snapshot">{report.startup_snapshot}</Section>
      <Section title="Problem Analysis">{report.problem_analysis}</Section>
      <Section title="Market Analysis">{report.market_analysis}</Section>
      <Section title="Industry Trends">{report.industry_trends}</Section>
      <Section title="Competitor Landscape">{report.competitor_landscape}</Section>
      <Section title="Customer Validation">{report.customer_validation}</Section>
      <Section title="Business Model Evaluation">{report.business_model_evaluation}</Section>
      <Section title="Technical Feasibility">{report.technical_feasibility}</Section>
      <Section title="SWOT Analysis">{report.swot_analysis}</Section>
      <Section title="Risk Assessment">{report.risk_assessment}</Section>

      {report.validation_scorecard &&
        Object.keys(report.validation_scorecard).length > 0 && (
          <section className="report-section">
            <h2 className="report-section-title">Validation Scorecard</h2>
            <div className="scorecard-grid">
              {Object.entries(report.validation_scorecard).map(([key, dim]) => (
                <div key={key} className="scorecard-item">
                  <div className="scorecard-header">
                    <span className="scorecard-name">{key}</span>
                    <span className="scorecard-score">{Math.round(dim.score)}</span>
                  </div>
                  <p className="scorecard-explanation">{dim.explanation}</p>
                  {dim.evidence && (
                    <p className="scorecard-evidence">{dim.evidence}</p>
                  )}
                  <span className="scorecard-confidence">
                    Confidence: {Math.round(dim.confidence * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </section>
        )}

      <Section title="Strategic Recommendations">
        {report.strategic_recommendations?.length > 0 ? (
          <ul className="report-list">
            {report.strategic_recommendations.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        ) : null}
      </Section>

      <Section title="Suggested Next Steps">
        {report.suggested_next_steps?.length > 0 ? (
          <ul className="report-list">
            {report.suggested_next_steps.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        ) : null}
      </Section>

      <Section title="References">
        {report.references?.length > 0 ? (
          <ul className="report-list">
            {report.references.map((ref, i) => (
              <li key={i}>{ref}</li>
            ))}
          </ul>
        ) : null}
      </Section>
    </div>
  )
}

export default ValidationReport
