import { useState } from 'react'
import './DiscoveryInterview.css'

const INITIAL_FORM = {
  startup_name: '',
  tagline: '',
  industry: '',
  stage: 'idea',
  problem_statement: '',
  target_customers: '',
  solution: '',
  business_model: '',
  market_knowledge: '',
  technical_information: '',
  founder_assumptions: '',
  validation_objectives: '',
}

function DiscoveryInterview({ onSubmit }) {
  const [form, setForm] = useState(INITIAL_FORM)

  function handleChange(e) {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    onSubmit({ ...form })
  }

  return (
    <div className="interview-page">
      <header className="interview-header">
        <h1>Discovery Interview</h1>
        <p className="interview-subtitle">
          Tell us about your startup idea. This information helps our AI agents
          generate a thorough validation report.
        </p>
      </header>

      <form className="interview-form" onSubmit={handleSubmit}>
        <fieldset className="form-section">
          <legend>Startup Overview</legend>
          <div className="form-group">
            <label htmlFor="startup_name">
              Startup Name <span className="required">*</span>
            </label>
            <input
              id="startup_name"
              name="startup_name"
              value={form.startup_name}
              onChange={handleChange}
              placeholder="e.g. AcmeAI"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="tagline">Tagline</label>
            <input
              id="tagline"
              name="tagline"
              value={form.tagline}
              onChange={handleChange}
              placeholder="A short one-liner describing your startup"
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="industry">Industry</label>
              <input
                id="industry"
                name="industry"
                value={form.industry}
                onChange={handleChange}
                placeholder="e.g. Fintech, Health, Edtech"
              />
            </div>
            <div className="form-group">
              <label htmlFor="stage">Current Stage</label>
              <select
                id="stage"
                name="stage"
                value={form.stage}
                onChange={handleChange}
              >
                <option value="idea">Idea</option>
                <option value="prototype">Prototype</option>
                <option value="mvp">MVP</option>
                <option value="launched">Launched</option>
                <option value="growing">Growing</option>
              </select>
            </div>
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Problem Discovery</legend>
          <div className="form-group">
            <label htmlFor="problem_statement">
              What problem are you solving? <span className="required">*</span>
            </label>
            <textarea
              id="problem_statement"
              name="problem_statement"
              value={form.problem_statement}
              onChange={handleChange}
              placeholder="Describe the problem your target customers face"
              rows={4}
              required
            />
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Customer Discovery</legend>
          <div className="form-group">
            <label htmlFor="target_customers">
              Who are your target customers? <span className="required">*</span>
            </label>
            <textarea
              id="target_customers"
              name="target_customers"
              value={form.target_customers}
              onChange={handleChange}
              placeholder="Describe your target audience, demographics, and user segments"
              rows={4}
              required
            />
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Solution</legend>
          <div className="form-group">
            <label htmlFor="solution">
              What is your solution? <span className="required">*</span>
            </label>
            <textarea
              id="solution"
              name="solution"
              value={form.solution}
              onChange={handleChange}
              placeholder="Describe your product or service and how it solves the problem"
              rows={4}
              required
            />
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Business Model</legend>
          <div className="form-group">
            <label htmlFor="business_model">
              How will you make money? <span className="required">*</span>
            </label>
            <textarea
              id="business_model"
              name="business_model"
              value={form.business_model}
              onChange={handleChange}
              placeholder="Describe your revenue model, pricing strategy, and monetization approach"
              rows={4}
              required
            />
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Market Knowledge</legend>
          <div className="form-group">
            <label htmlFor="market_knowledge">
              What do you know about the market? <span className="required">*</span>
            </label>
            <textarea
              id="market_knowledge"
              name="market_knowledge"
              value={form.market_knowledge}
              onChange={handleChange}
              placeholder="Describe market size, trends, and your understanding of the competitive landscape"
              rows={4}
              required
            />
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Technical Information</legend>
          <div className="form-group">
            <label htmlFor="technical_information">
              Technical details about your product <span className="required">*</span>
            </label>
            <textarea
              id="technical_information"
              name="technical_information"
              value={form.technical_information}
              onChange={handleChange}
              placeholder="Describe the technology stack, technical approach, and any IP considerations"
              rows={4}
              required
            />
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Founder Assumptions</legend>
          <div className="form-group">
            <label htmlFor="founder_assumptions">
              What key assumptions are you making?
            </label>
            <textarea
              id="founder_assumptions"
              name="founder_assumptions"
              value={form.founder_assumptions}
              onChange={handleChange}
              placeholder="List any assumptions you have about your customers, market, or business"
              rows={3}
            />
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Validation Objectives</legend>
          <div className="form-group">
            <label htmlFor="validation_objectives">
              What do you want to validate?
            </label>
            <textarea
              id="validation_objectives"
              name="validation_objectives"
              value={form.validation_objectives}
              onChange={handleChange}
              placeholder="What specific aspects of your idea would you like our agents to focus on?"
              rows={3}
            />
          </div>
        </fieldset>

        <div className="form-actions">
          <button type="submit" className="submit-button">
            Generate Validation Plan
          </button>
        </div>
      </form>
    </div>
  )
}

export default DiscoveryInterview
