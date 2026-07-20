import { useState } from 'react'
import LandingPage from './pages/LandingPage'
import DiscoveryInterview from './pages/DiscoveryInterview'
import ValidationMode from './pages/ValidationMode'
import ProgressView from './pages/ProgressView'
import ValidationReport from './pages/ValidationReport'
import { createValidationJob } from './services/api'

function App() {
  const [page, setPage] = useState('landing')
  const [profile, setProfile] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [error, setError] = useState(null)
  const [isCreating, setIsCreating] = useState(false)

  function handleStartValidation() {
    setPage('interview')
  }

  function handleInterviewSubmit(data) {
    setProfile(data)
    setPage('mode')
  }

  async function handleModeSelect(mode) {
    try {
      setIsCreating(true)
      setError(null)
      const result = await createValidationJob(profile, mode)
      setJobId(result.job_id)
      setPage('progress')
    } catch (err) {
      setError(
        err.message.includes('Failed to fetch')
          ? 'Unable to reach the server. Please make sure the backend is running and try again.'
          : err.message,
      )
    } finally {
      setIsCreating(false)
    }
  }

  function handleJobComplete() {
    setPage('report')
  }

  function handleRetry() {
    setPage('mode')
  }

  if (page === 'interview') {
    return <DiscoveryInterview onSubmit={handleInterviewSubmit} />
  }

  if (page === 'mode') {
    return <ValidationMode onSelect={handleModeSelect} error={error} loading={isCreating} />
  }

  if (page === 'progress') {
    return (
      <ProgressView
        jobId={jobId}
        onComplete={handleJobComplete}
        onRetry={handleRetry}
      />
    )
  }

  if (page === 'report') {
    return <ValidationReport jobId={jobId} />
  }

  return <LandingPage onStart={handleStartValidation} />
}

export default App
