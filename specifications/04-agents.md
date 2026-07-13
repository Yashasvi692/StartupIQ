# Workflow Specification

**Project:** StartupIQ

**Version:** 1.0

**Status:** Draft

**Methodology:** Spec-Driven Development

---

# Related Documents

- `00-foundation.md`
- `01-prd.md`
- `02-architecture.md`
- `04-agents.md`
- `05-prompts.md`
- `06-api.md`
- `07-implementation-plan.md`

---

# 1. Purpose

This document defines how StartupIQ executes a startup validation request.

It specifies:

- Validation Pipeline execution
- Agno Team orchestration
- Pipeline stages
- Agent collaboration
- Context management
- Execution rules
- Failure handling

This document defines **how work flows through the system**.

It does **not** define the internal behavior of individual agents.

---

# 2. Workflow Philosophy

StartupIQ follows a **Pipeline → Team → Agent** execution model.

Responsibilities are divided as follows:

| Component | Responsibility |
|-----------|----------------|
| Validation Pipeline | Application orchestration |
| Agno Teams | AI collaboration |
| Agents | Specialized reasoning |
| Tools | Information retrieval |

Each layer has exactly one responsibility.

---

# 3. Validation Pipeline Overview

Every startup validation follows the same lifecycle.

```text
User
    │
    ▼
Discovery Team
    │
    ▼
Startup Profile
    │
    ▼
Validation Team
    │
    ▼
Validation Report
    │
    ▼
Completed Job
```

The Validation Pipeline coordinates this entire lifecycle.

---

# 4. Pipeline Stages

Every Validation Job progresses through seven stages.

| Stage | Purpose |
|---------|----------|
| Discovery | Validate startup information |
| Planning | Build validation strategy |
| Research | Collect public evidence |
| Competition | Analyze competitors |
| Analysis | Generate business insights |
| Reporting | Create validation report |
| Review | Validate report quality |

Progress is reported after each completed stage.

---

# 5. Discovery Team Workflow

## Goal

Transform founder responses into a structured Startup Profile.

### Input

Founder responses collected during the Discovery Interview.

### Responsibilities

- Validate responses
- Normalize information
- Identify missing fields
- Request clarification when necessary
- Produce a Startup Profile

### Output

StartupProfile

The Discovery Team completes before validation begins.

---

# 6. Validation Team Workflow

The Validation Team transforms a Startup Profile into a complete validation report.

Execution order:

```text
Planner Agent
       │
       ▼
┌───────────────┬───────────────┐
│               │               │
▼               ▼               ▼
Research     Competition     (Future Agents)
       │               │
       └───────┬───────┘
               ▼
Business Analyst
               ▼
Report Agent
               ▼
Reviewer Agent
               ▼
Validation Report
```

The Validation Team owns AI collaboration.

The Validation Pipeline owns execution.

---

# 7. Planning Stage

The Planner Agent determines how validation should proceed.

## Inputs

- StartupProfile
- Validation Mode

## Outputs

ValidationPlan

The Validation Plan includes:

- Research depth
- Required agents
- Execution strategy
- Estimated completion time

The Planner Agent never performs research.

---

# 8. Research Stage

The Research Stage gathers publicly available evidence.

The Research Agent may investigate:

- Market size
- Industry trends
- Customer pain points
- Technology landscape

Outputs are collected into a structured ResearchResult.

Whenever possible, research should include supporting citations.

---

# 9. Competition Stage

The Competition Agent analyzes competing solutions.

Responsibilities include:

- Identifying competitors
- Comparing products
- Comparing pricing
- Identifying differentiators
- Identifying market gaps

Output:

CompetitorAnalysis

This stage may execute in parallel with the Research Stage.

---

# 10. Analysis Stage

The Business Analyst Agent converts collected evidence into business insights.

Responsibilities include:

- SWOT Analysis
- Risk Assessment
- Opportunity Analysis
- Business Model Evaluation
- Strategic Recommendations

Output:

BusinessFindings

The Analysis Stage performs reasoning only.

It does not gather external information.

---

# 11. Reporting Stage

The Report Agent transforms structured findings into the StartupIQ Validation Report.

The report includes:

- Executive Summary
- Startup Snapshot
- Market Analysis
- Competitor Analysis
- SWOT
- Validation Score
- Recommendations
- References
- Confidence Scores

Output:

ValidationReport

---

# 12. Review Stage

The Reviewer Agent performs a final quality review.

Checks include:

- Missing sections
- Unsupported recommendations
- Missing citations
- Formatting consistency
- Confidence completeness

If major issues are found, the Team may regenerate affected sections.

---

# 13. Context Management

Every agent receives only the context required for its task.

Examples:

Research Agent

- StartupProfile
- ValidationPlan

Competition Agent

- StartupProfile
- ResearchResult

Business Analyst Agent

- StartupProfile
- ResearchResult
- CompetitorAnalysis

This minimizes hallucinations and improves reasoning quality.

---

# 14. Prompt Execution

Every agent owns a dedicated Markdown prompt stored in:

```text
backend/prompts/
```

Prompts are:

- Version controlled
- Independent from implementation
- Loaded dynamically at runtime

Prompt design is specified in `05-prompts.md`.

---

# 15. Execution Rules

The following responsibilities are strictly enforced.

| Component | Responsibility |
|-----------|----------------|
| Validation Pipeline | Application orchestration |
| Agno Teams | Agent collaboration |
| Planner Agent | Validation planning |
| Research Agent | Public research |
| Competition Agent | Competitor analysis |
| Business Analyst Agent | Business reasoning |
| Report Agent | Report generation |
| Reviewer Agent | Report validation |

Responsibilities must never overlap.

---

# 16. Failure Handling

Failures are isolated whenever possible.

Examples:

- Research source unavailable
- Search timeout
- Missing public information

If a stage cannot complete successfully:

- Remaining stages continue when possible.
- The report records the missing information.
- Confidence scores are adjusted accordingly.

The system must never fabricate missing evidence.

---

# 17. Workflow Outputs

Every pipeline stage produces a structured output.

| Stage | Output |
|---------|---------|
| Discovery | StartupProfile |
| Planning | ValidationPlan |
| Research | ResearchResult |
| Competition | CompetitorAnalysis |
| Analysis | BusinessFindings |
| Reporting | ValidationReport |

Structured outputs are preferred over free-form text.

---

# 18. Workflow Summary

StartupIQ follows a layered execution model.

Validation Pipeline

↓

Agno Teams

↓

Specialized Agents

↓

Structured Outputs

↓

Validation Report

This architecture separates application orchestration from AI collaboration, resulting in a workflow that is modular, explainable, maintainable, and easy to extend.

---

# Revision History

| Version | Date | Author | Notes |
|----------|------|--------|-------|
| 1.0 | YYYY-MM-DD | Yash | Initial workflow specification |