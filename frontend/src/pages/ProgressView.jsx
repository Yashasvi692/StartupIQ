import { useState, useEffect, useRef } from 'react'
import { getJobStatus } from '../services/api'
import './ProgressView.css'

const ERROR_MESSAGES = {
  failed: 'The validation process encountered an error and could not complete. This may be due to a temporary issue. Please try again.',
  cancelled: 'The validation was cancelled.',
}

const MAX_POLL_ERRORS = 5

function ProgressView({ jobId, onComplete, onRetry }) {
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const intervalRef = useRef(null)
  const errorCountRef = useRef(0)

  useEffect(() => {
    errorCountRef.current = 0

    async function poll() {
      try {
        const data = await getJobStatus(jobId)
        setStatus(data)
        setError(null)
        errorCountRef.current = 0

        if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
          clearInterval(intervalRef.current)
          if (data.status === 'completed') {
            onComplete()
          }
        }
      } catch {
        errorCountRef.current += 1
        if (errorCountRef.current >= MAX_POLL_ERRORS) {
          clearInterval(intervalRef.current)
        }
        setError('Unable to reach the server. Please check your connection and try again.')
      }
    }

    poll()
    intervalRef.current = setInterval(poll, 2000)

    return () => clearInterval(intervalRef.current)
  }, [jobId, onComplete])

  const terminalStatus = status && (status.status === 'failed' || status.status === 'cancelled')

  return (
    <div className="progress-page">
      {terminalStatus ? (
        <div className="progress-terminal">
          <h1 className="terminal-title">Validation {status.status}</h1>
          <p className="terminal-message">{ERROR_MESSAGES[status.status]}</p>
          {onRetry && (
            <button type="button" className="retry-button" onClick={onRetry}>
              Try Again
            </button>
          )}
        </div>
      ) : (
        <>
          <header className="progress-header">
            <h1>Validating Your Idea</h1>
            <p className="progress-subtitle">
              Our AI agents are analyzing your startup. This may take a few minutes.
            </p>
          </header>

          {error && <p className="progress-error">{error}</p>}

          {status ? (
            <div className="progress-body">
              <div className="progress-bar-container">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${status.progress}%` }}
                />
              </div>
              <p className="progress-percent">{status.progress}%</p>

              <div className="progress-details">
                <div className="progress-row">
                  <span className="progress-label">Status</span>
                  <span className={`progress-value status-${status.status}`}>
                    {status.status}
                  </span>
                </div>
                <div className="progress-row">
                  <span className="progress-label">Current Stage</span>
                  <span className="progress-value">{status.current_stage || 'Starting...'}</span>
                </div>
              </div>

              <div className="progress-stages">
                <div className="stages-column">
                  <h3>Completed</h3>
                  {status.completed_stages.length === 0 && (
                    <p className="stages-empty">None yet</p>
                  )}
                  {status.completed_stages.map((stage) => (
                    <span key={stage} className="stage-tag stage-completed">
                      {stage}
                    </span>
                  ))}
                </div>
                <div className="stages-column">
                  <h3>Remaining</h3>
                  {status.remaining_stages.length === 0 && (
                    <p className="stages-empty">Finalizing...</p>
                  )}
                  {status.remaining_stages.map((stage) => (
                    <span key={stage} className="stage-tag stage-remaining">
                      {stage}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="loading-state">
              <div className="spinner" />
              <p>Starting validation...</p>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default ProgressView
