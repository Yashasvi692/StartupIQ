# Agent Specification

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
- `05-prompts.md`
- `06-api.md`
- `07-implementation-plan.md`

---

# 1. Purpose

This document defines the responsibilities, interfaces, and expected behavior of every AI agent used within StartupIQ.

Agents are treated as independent software components.

Each agent has a clearly defined contract consisting of:

- Purpose
- Team ownership
- Inputs
- Outputs
- Prompt
- Tools
- Responsibilities
- Failure conditions
- Success criteria

This document does not define implementation details.

Implementation is governed by the architecture and implementation specifications.

---

# 2. Agent Design Principles

Every StartupIQ agent SHALL follow these principles.

---

## AD-001 Single Responsibility

Each agent performs one clearly defined responsibility.

Responsibilities shall never overlap.

---

## AD-002 Team Collaboration

Agents collaborate exclusively through Agno Teams.

Agents SHALL NOT invoke one another directly.

---

## AD-003 Structured Communication

Agents SHALL exchange structured models whenever possible.

Examples include:

- StartupProfile
- ValidationPlan
- ResearchResult
- CompetitorAnalysis
- BusinessFindings
- ValidationReport

---

## AD-004 Prompt Separation

Every agent owns exactly one prompt.

Prompts are stored separately from application code.

---

## AD-005 Explainability

Whenever reasoning is performed, agents should provide evidence and confidence scores whenever applicable.

---

## AD-006 Replaceability

Every agent should be replaceable without affecting the remaining architecture.

---

# 3. Agent Contract

Every StartupIQ agent SHALL define the following attributes.

| Attribute | Description |
|------------|-------------|
| Purpose | Primary responsibility |
| Team | Owning Agno Team |
| Inputs | Required structured models |
| Outputs | Produced structured models |
| Prompt | Markdown prompt file |
| Tools | External tools available |
| Responsibilities | Required behavior |
| Failure Conditions | Expected failure scenarios |
| Success Criteria | Definition of successful execution |

---

# 4. Agent Overview

| Agent | Team | Primary Responsibility |
|---------|----------------|----------------------------|
| Discovery Agent | Discovery Team | Create Startup Profile |
| Planner Agent | Validation Team | Generate Validation Plan |
| Research Agent | Validation Team | Collect public evidence |
| Competition Agent | Validation Team | Analyze competitors |
| Business Analyst Agent | Validation Team | Generate business insights |
| Report Agent | Validation Team | Produce validation report |
| Reviewer Agent | Validation Team | Validate report quality |

StartupIQ Version 1 intentionally uses a small number of highly specialized agents.

---

# 5. Discovery Agent

## Purpose

Transform founder responses into a structured Startup Profile.

---

## Team

Discovery Team

---

## Inputs

- Discovery Interview Responses

---

## Outputs

- StartupProfile

---

## Prompt

```text
backend/prompts/discovery.md
```

---

## Tools

None

---

## Responsibilities

- Validate user responses
- Normalize startup information
- Detect missing fields
- Identify inconsistent information
- Generate a StartupProfile
- Request clarification when required

---

## Failure Conditions

- Required information missing
- Invalid user responses
- Ambiguous startup description

---

## Success Criteria

Produces a valid StartupProfile that satisfies the requirements defined in the PRD.

---

# 6. Planner Agent

## Purpose

Generate a Validation Plan for the Validation Team.

---

## Team

Validation Team

---

## Inputs

- StartupProfile
- Validation Mode

---

## Outputs

- ValidationPlan

---

## Prompt

```text
backend/prompts/planner.md
```

---

## Tools

None

---

## Responsibilities

- Determine validation strategy
- Select research depth
- Estimate execution time
- Determine execution order
- Configure validation intensity
- Produce ValidationPlan

The Planner Agent performs planning only.

It never performs research.

---

## Failure Conditions

- Invalid StartupProfile
- Unsupported validation mode

---

## Success Criteria

Produces a complete ValidationPlan for every valid StartupProfile.

---

# 7. Research Agent

## Purpose

Collect publicly available evidence relevant to the startup.

---

## Team

Validation Team

---

## Inputs

- StartupProfile
- ValidationPlan

---

## Outputs

- ResearchResult

---

## Prompt

```text
backend/prompts/research.md
```

---

## Tools

The Research Agent may use:

- DuckDuckGo
- Playwright
- BeautifulSoup
- GitHub
- pytrends

---

## Responsibilities

Collect evidence regarding:

- Market size
- Industry trends
- Customer pain points
- Existing technologies
- Market maturity
- Industry developments

Every finding should include supporting evidence whenever available.

---

## Failure Conditions

- Search failures
- Network failures
- Missing public information
- Tool execution failures

The agent must never fabricate missing evidence.

---

## Success Criteria

Produces a structured ResearchResult containing evidence-backed findings and appropriate citations.

---

# 8. Competition Agent

## Purpose

Analyze the competitive landscape surrounding the proposed startup.

---

## Team

Validation Team

---

## Inputs

- StartupProfile
- ResearchResult

---

## Outputs

- CompetitorAnalysis

---

## Prompt

```text
backend/prompts/competition.md
```

---

## Tools

The Competition Agent may use:

- DuckDuckGo
- Playwright
- BeautifulSoup

---

## Responsibilities

The Competition Agent SHALL:

- Identify direct competitors
- Identify indirect competitors
- Compare products and services
- Compare pricing models
- Identify differentiators
- Identify market gaps
- Evaluate competitive intensity

Every comparison should be supported by publicly available evidence whenever possible.

---

## Failure Conditions

- Competitors cannot be identified
- Public competitor information unavailable
- Search failures
- Tool execution failures

The agent must never invent competitor information.

---

## Success Criteria

Produces a structured CompetitorAnalysis supported by verifiable evidence.

---

# 9. Business Analyst Agent

## Purpose

Transform collected evidence into actionable business insights.

---

## Team

Validation Team

---

## Inputs

- StartupProfile
- ResearchResult
- CompetitorAnalysis

---

## Outputs

- BusinessFindings

---

## Prompt

```text
backend/prompts/business.md
```

---

## Tools

None

The Business Analyst Agent performs reasoning only.

---

## Responsibilities

Generate:

- SWOT Analysis
- Risk Assessment
- Opportunity Analysis
- Business Model Evaluation
- Go-To-Market observations
- Strategic Recommendations
- Validation Score

Every conclusion should be supported by available evidence.

---

## Failure Conditions

- Insufficient supporting evidence
- Missing research inputs
- Conflicting findings

When uncertainty exists, the agent must explicitly communicate it.

---

## Success Criteria

Produces structured BusinessFindings with evidence-backed recommendations and confidence scores.

---

# 10. Report Agent

## Purpose

Generate the final StartupIQ Validation Report.

---

## Team

Validation Team

---

## Inputs

- StartupProfile
- ResearchResult
- CompetitorAnalysis
- BusinessFindings

---

## Outputs

- ValidationReport

---

## Prompt

```text
backend/prompts/report.md
```

---

## Tools

Markdown formatting utilities

---

## Responsibilities

Generate a report containing:

- Executive Summary
- Startup Snapshot
- Market Analysis
- Industry Trends
- Competitor Analysis
- SWOT Analysis
- Risk Assessment
- Validation Score
- Strategic Recommendations
- Next Steps
- References
- Confidence Scores

The Report Agent SHALL organize information.

It SHALL NOT generate new business insights.

---

## Failure Conditions

- Missing required inputs
- Invalid report structure
- Formatting failures

---

## Success Criteria

Produces a complete ValidationReport matching the specification defined in the PRD.

---

# 11. Reviewer Agent

## Purpose

Perform the final quality review before the report is returned to the user.

---

## Team

Validation Team

---

## Inputs

- ValidationReport

---

## Outputs

- ReviewedReport
- QualityReview

---

## Prompt

```text
backend/prompts/review.md
```

---

## Tools

None

---

## Responsibilities

Verify:

- Report completeness
- Internal consistency
- Evidence availability
- Citation quality
- Confidence scores
- Formatting
- Missing sections
- Unsupported recommendations

The Reviewer Agent may request regeneration of affected sections when major issues are detected.

---

## Failure Conditions

- Missing report sections
- Missing citations
- Unsupported conclusions
- Invalid report format

---

## Success Criteria

Approves the ValidationReport or returns a structured QualityReview describing required improvements.

---

# 12. Agent Communication Rules

StartupIQ follows strict communication rules.

---

## AC-001 Team Ownership

Every agent belongs to exactly one Agno Team.

---

## AC-002 No Direct Agent Communication

Agents SHALL NOT invoke or communicate directly with other agents.

All collaboration is managed by Agno Teams.

---

## AC-003 Structured Inputs

Agents receive structured models only.

Examples include:

- StartupProfile
- ValidationPlan
- ResearchResult
- CompetitorAnalysis
- BusinessFindings
- ValidationReport

---

## AC-004 Structured Outputs

Agents SHALL return structured models whenever possible.

Free-form responses should be avoided.

---

## AC-005 Limited Context

Agents receive only the context required to perform their responsibilities.

Unnecessary information should not be provided.

---

# 13. Agno Team Collaboration

StartupIQ Version 1 contains two Agno Teams.

---

## Discovery Team

Responsible for:

- Startup discovery
- Input validation
- StartupProfile generation

Members:

- Discovery Agent

---

## Validation Team

Responsible for:

- Validation planning
- Research
- Competition analysis
- Business analysis
- Report generation
- Report review

Members:

- Planner Agent
- Research Agent
- Competition Agent
- Business Analyst Agent
- Report Agent
- Reviewer Agent

The Validation Team coordinates AI collaboration while the Validation Pipeline coordinates application execution.

---

# 14. Prompt Ownership

Every StartupIQ agent owns one dedicated Markdown prompt.

| Agent | Prompt |
|---------|------------------------------|
| Discovery Agent | backend/prompts/discovery.md |
| Planner Agent | backend/prompts/planner.md |
| Research Agent | backend/prompts/research.md |
| Competition Agent | backend/prompts/competition.md |
| Business Analyst Agent | backend/prompts/business.md |
| Report Agent | backend/prompts/report.md |
| Reviewer Agent | backend/prompts/review.md |

Prompt engineering is specified separately in `05-prompts.md`.

---

# 15. Agent Summary

StartupIQ Version 1 uses seven specialized AI agents organized into two Agno Teams.

The architecture intentionally favors a small number of highly capable agents rather than many narrowly focused agents.

Each agent has:

- One responsibility
- One prompt
- One owning Team
- Structured inputs
- Structured outputs
- Clearly defined success criteria

This design improves modularity, maintainability, explainability, and future extensibility.

---

# Revision History

| Version | Date | Author | Notes |
|----------|------|--------|-------|
| 1.0 | YYYY-MM-DD | Yash | Initial agent specification |