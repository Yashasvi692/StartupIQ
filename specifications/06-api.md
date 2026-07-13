# API Specification

**Project:** StartupIQ

**Version:** 1.0

**Status:** Draft

**Methodology:** Spec-Driven Development

---

# Related Documents

- `00-foundation.md`
- `01-prd.md`
- `02-architecture.md`
- `03-workflows.md`
- `04-agents.md`
- `05-prompts.md`
- `07-implementation-plan.md`

---

# 1. Purpose

This document defines the public REST API exposed by StartupIQ.

The API provides a stable contract between the frontend and backend while remaining independent of the internal AI implementation.

StartupIQ follows a **job-based asynchronous API model**.

Every validation request creates a Validation Job that progresses independently through the Validation Pipeline.

---

# 2. API Design Principles

StartupIQ APIs follow the principles below.

---

## API-001 Business-Oriented

Endpoints represent business actions rather than database operations.

Example:

✓ POST /validate

Instead of:

✗ POST /startup

---

## API-002 Job-Based

Every validation request creates a Validation Job.

Clients interact with that Job until it completes.

---

## API-003 Stateless

Every request contains all required information.

The backend manages Validation Job state.

---

## API-004 Structured Responses

Every endpoint returns predictable JSON responses.

---

## API-005 Future Compatibility

The API should support future additions such as:

- Streaming
- Authentication
- Background execution
- Persistent storage

without breaking existing clients.

---

# 3. API Overview

| Method | Endpoint | Purpose |
|---------|-------------------------------|--------------------------------|
| POST | /validate | Create Validation Job |
| GET | /jobs/{job_id} | Get Job Status |
| GET | /jobs/{job_id}/report | Retrieve Validation Report |
| GET | /health | Health Check |
| GET | /version | Version Information |
| DELETE | /jobs/{job_id} | Cancel Validation Job (Optional V1) |

---

# 4. Validation Job Lifecycle

Every validation request follows the same lifecycle.

```text
Client
    │
    ▼
POST /validate
    │
    ▼
Validation Job Created
    │
    ▼
Validation Pipeline
    │
    ▼
Agno Teams
    │
    ▼
Validation Report
    │
    ▼
GET /jobs/{job_id}/report
```

---

# 5. POST /validate

Creates a new Validation Job.

## Request

```json
{
  "mode": "deep",
  "startup_profile": {
    "...": "..."
  }
}
```

---

### Parameters

**mode**

Allowed values:

- quick
- deep

**startup_profile**

Structured StartupProfile produced by the Discovery Team.

---

## Success Response

HTTP 202 Accepted

```json
{
  "status": "accepted",
  "job_id": "job_9e7b3c",
  "message": "Validation started.",
  "estimated_duration_seconds": 480
}
```

---

## Error Response

HTTP 400 Bad Request

```json
{
  "status": "error",
  "code": "INVALID_INPUT",
  "message": "Startup Profile is incomplete.",
  "details": {}
}
```

---

# 6. GET /jobs/{job_id}

Returns the current Validation Job status.

Example

```json
{
  "job_id": "job_9e7b3c",
  "status": "running",
  "progress": 62,
  "current_stage": "Competition",
  "completed_stages": [
    "Discovery",
    "Planning",
    "Research"
  ],
  "remaining_stages": [
    "Analysis",
    "Reporting",
    "Review"
  ]
}
```

---

## Job Status Values

Possible values:

- queued
- running
- completed
- failed
- cancelled

---

# 7. GET /jobs/{job_id}/report

Returns the completed Validation Report.

If the Validation Job has not completed:

HTTP 409 Conflict

Example

```json
{
  "status": "completed",
  "report": {
    "...": "..."
  }
}
```

---

# 8. DELETE /jobs/{job_id}

(Optional for Version 1)

Cancels an active Validation Job.

Example

```json
{
  "status": "cancelled"
}
```

---

# 9. GET /health

Returns backend health.

```json
{
  "status": "healthy"
}
```

---

# 10. GET /version

Returns project version.

```json
{
  "project": "StartupIQ",
  "version": "1.0.0"
}
```

---

# 11. ValidationJob Model

Every Validation Job contains:

```text
ValidationJob

job_id

status

mode

startup_profile

progress

current_stage

completed_stages

report

created_at

completed_at
```

Version 1 may keep Validation Jobs in memory.

Future versions may persist Jobs in a database.

---

# 12. StartupProfile Model

The StartupProfile is the primary input to the Validation Pipeline.

It includes:

- Startup Overview
- Problem Statement
- Target Customers
- Solution
- Business Model
- Market Knowledge
- Technical Information
- Founder Assumptions
- Validation Objectives

---

# 13. ValidationReport Model

Every Validation Report contains:

- Executive Summary
- Startup Snapshot
- Market Analysis
- Industry Trends
- Competitor Analysis
- Customer Validation
- Business Model Evaluation
- Technical Feasibility
- SWOT Analysis
- Risk Assessment
- Validation Score
- Strategic Recommendations
- Suggested Next Steps
- References
- Confidence Scores

---

# 14. Progress Model

Progress is updated after every Validation Pipeline stage.

| Stage | Progress |
|---------|----------|
| Discovery | 10% |
| Planning | 20% |
| Research | 50% |
| Competition | 65% |
| Analysis | 80% |
| Reporting | 95% |
| Review | 100% |

---

# 15. Standard Response Format

Successful responses

```json
{
  "status": "success",
  "data": {}
}
```

Error responses

```json
{
  "status": "error",
  "code": "...",
  "message": "...",
  "details": {}
}
```

---

# 16. HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 202 | Accepted |
| 400 | Bad Request |
| 404 | Job Not Found |
| 409 | Report Not Ready |
| 422 | Validation Failed |
| 500 | Internal Server Error |

---

# 17. Security

Version 1 does not require authentication.

Future versions may introduce:

- JWT Authentication
- API Keys
- User Accounts
- Rate Limiting

without changing endpoint semantics.

---

# 18. Future Endpoints

Potential future additions include:

| Method | Endpoint |
|---------|----------------------------|
| GET | /jobs/{job_id}/events |
| POST | /discover |
| POST | /compare |
| POST | /monitor |
| POST | /export |
| GET | /history |
| POST | /pitch-analysis |

---

# 19. API Summary

StartupIQ exposes a small, business-oriented REST API centered around Validation Jobs.

The API intentionally separates job creation, job monitoring, and report retrieval.

This design supports long-running AI workflows while remaining simple enough for Version 1 and extensible for future capabilities such as streaming, persistent storage, and multi-user collaboration.

---

# Revision History

| Version | Date | Author | Notes |
|----------|------|--------|-------|
| 1.0 | YYYY-MM-DD | Yash | Initial API specification |