const API_BASE = import.meta.env.VITE_API_BASE || ''

async function request(url, options) {
  const response = await fetch(`${API_BASE}${url}`, options)
  if (!response.ok) {
    const error = await response.json().catch(() => null)
    throw new Error(error?.detail?.message || `Request failed: ${response.status}`)
  }
  return response.json()
}

export async function createValidationJob(startupProfile, mode) {
  return request('/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode, startup_profile: startupProfile }),
  })
}

export async function getJobStatus(jobId) {
  return request(`/jobs/${jobId}`)
}

export async function getJobReport(jobId) {
  return request(`/jobs/${jobId}/report`)
}
