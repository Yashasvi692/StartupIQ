import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createValidationJob, getJobStatus, getJobReport } from './api'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

beforeEach(() => {
  mockFetch.mockReset()
})

describe('createValidationJob', () => {
  it('sends POST request to /validate with profile and mode', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'accepted', job_id: 'job_abc123' }),
    })
    const profile = { startup_name: 'TestCo', problem_statement: 'Problem' }
    const result = await createValidationJob(profile, 'deep')
    expect(mockFetch).toHaveBeenCalledWith('/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: 'deep', startup_profile: profile }),
    })
    expect(result.job_id).toBe('job_abc123')
  })

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 400,
      json: () => Promise.resolve({ detail: { message: 'Invalid input' } }),
    })
    await expect(createValidationJob({}, 'deep')).rejects.toThrow('Invalid input')
  })

  it('throws with status code when no detail message', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve(null),
    })
    await expect(createValidationJob({}, 'deep')).rejects.toThrow('Request failed: 500')
  })
})

describe('getJobStatus', () => {
  it('sends GET request to /jobs/{jobId}', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ job_id: 'job_xyz', status: 'running', progress: 50 }),
    })
    const result = await getJobStatus('job_xyz')
    expect(mockFetch.mock.calls[0][0]).toBe('/jobs/job_xyz')
    expect(result.status).toBe('running')
    expect(result.progress).toBe(50)
  })

  it('throws on 404', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: { message: 'Job not found' } }),
    })
    await expect(getJobStatus('invalid')).rejects.toThrow('Job not found')
  })
})

describe('getJobReport', () => {
  it('sends GET request to /jobs/{jobId}/report', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'completed', report: { overall_score: 85 } }),
    })
    const result = await getJobReport('job_abc')
    expect(mockFetch.mock.calls[0][0]).toBe('/jobs/job_abc/report')
    expect(result.report.overall_score).toBe(85)
  })

  it('throws on 409 conflict', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 409,
      json: () => Promise.resolve({ detail: { message: 'Report not ready yet' } }),
    })
    await expect(getJobReport('job_abc')).rejects.toThrow('Report not ready yet')
  })
})
