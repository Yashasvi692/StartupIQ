# Prompt Specification

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
- `06-api.md`
- `07-implementation-plan.md`

---

# 1. Purpose

This document defines the prompt engineering standards used throughout StartupIQ.

Prompts are treated as first-class software artifacts.

Every AI agent owns a dedicated Markdown prompt that defines its behavior independently of the application code.

Separating prompts from implementation improves:

- Maintainability
- Version control
- Prompt engineering
- Testing
- Collaboration
- Explainability

---

# 2. Prompt Philosophy

Every StartupIQ prompt SHALL follow the principles defined in `00-foundation.md`.

The following principles apply to every prompt.

---

## PP-001 Evidence First

Research should always precede reasoning.

Agents should never make assumptions before gathering available evidence.

---

## PP-002 Transparency

Agents should distinguish between:

- Facts
- Assumptions
- Inferences
- Recommendations

---

## PP-003 Explainability

Major conclusions should include supporting evidence whenever possible.

---

## PP-004 Hallucination Prevention

If evidence cannot be found, the prompt should instruct the agent to explicitly communicate uncertainty.

Agents SHALL NOT fabricate information.

---

## PP-005 Actionability

Recommendations should be practical, specific, and actionable.

---

# 3. Prompt Storage

Every prompt SHALL exist as an independent Markdown document.

```text
backend/

prompts/

discovery.md
planner.md
research.md
competition.md
business.md
report.md
review.md
```

Application code loads prompts dynamically at runtime.

Prompts SHALL NOT be hardcoded inside Python files.

---

# 4. Prompt Template

Every StartupIQ prompt SHALL follow the same structure.

```text
Identity

Objective

Responsibilities

Constraints

Inputs

Available Context

Available Tools

Reasoning Instructions

Expected Output

Quality Checklist
```

Using a consistent template improves readability and simplifies maintenance.

---

# 5. Prompt Sections

Every prompt SHALL contain the following sections.

---

## Identity

Defines the role of the agent.

Example:

"You are the Research Agent responsible for collecting publicly available evidence."

---

## Objective

Clearly states the agent's primary goal.

---

## Responsibilities

Lists exactly what the agent must accomplish.

Responsibilities should align with `04-agents.md`.

---

## Constraints

Defines prohibited behaviors.

Examples include:

- Do not fabricate evidence.
- Do not speculate without justification.
- Do not generate unsupported recommendations.
- Do not perform responsibilities assigned to other agents.

---

## Inputs

Defines the structured models received by the agent.

Examples:

- StartupProfile
- ValidationPlan
- ResearchResult
- CompetitorAnalysis

---

## Available Context

Defines what contextual information is available.

Agents SHALL receive only the minimum required context.

---

## Available Tools

Lists the tools available to the agent.

Examples:

- DuckDuckGo
- Playwright
- BeautifulSoup
- pytrends

---

## Reasoning Instructions

Defines how the agent should approach the task.

Examples include:

- Research before reasoning.
- Compare multiple sources.
- Prefer recent evidence.
- Highlight uncertainty.
- Avoid unsupported conclusions.

---

## Expected Output

Defines the required structured output.

Examples:

- StartupProfile
- ValidationPlan
- ResearchResult
- CompetitorAnalysis
- BusinessFindings
- ValidationReport

Structured outputs are preferred over free-form text.

---

## Quality Checklist

Before returning a response, every agent should verify:

- Required sections completed
- Output format correct
- Evidence included
- Confidence assigned
- No unsupported claims
- No hallucinated information

---

# 6. Context Rules

Prompts SHALL minimize context.

Each agent receives only the information required to perform its responsibility.

Examples:

Research Agent

- StartupProfile
- ValidationPlan

Business Analyst Agent

- StartupProfile
- ResearchResult
- CompetitorAnalysis

Smaller context windows improve consistency and reduce hallucinations.

---

# 7. Output Rules

Prompts SHALL prefer structured outputs.

Preferred formats include:

- Pydantic models
- JSON
- Structured Markdown

Raw free-form responses should be avoided whenever possible.

---

# 8. Citation Rules

Whenever factual claims are made, prompts SHALL instruct agents to:

- Cite supporting evidence
- Identify information sources
- Distinguish facts from assumptions
- Explain limitations when evidence is unavailable

---

# 9. Confidence Rules

Every major finding should include a confidence assessment.

Confidence should be based on:

- Quantity of evidence
- Quality of evidence
- Agreement between sources
- Completeness of research

Confidence should never be arbitrary.

---

# 10. Error Handling

Prompts SHALL define expected behavior when problems occur.

Examples include:

- Missing evidence
- Tool failures
- Search failures
- Conflicting information
- Incomplete context

Agents should communicate limitations instead of fabricating conclusions.

---

# 11. Prompt Versioning

Prompt files are version-controlled independently from application code.

Prompt updates should follow the same review process as software changes.

Each prompt should evolve independently while remaining compatible with its corresponding Agent Contract.

---

# 12. Prompt Ownership

| Agent | Prompt |
|---------|------------------------------|
| Discovery Agent | backend/prompts/discovery.md |
| Planner Agent | backend/prompts/planner.md |
| Research Agent | backend/prompts/research.md |
| Competition Agent | backend/prompts/competition.md |
| Business Analyst Agent | backend/prompts/business.md |
| Report Agent | backend/prompts/report.md |
| Reviewer Agent | backend/prompts/review.md |

Each agent owns exactly one prompt.

---

# 13. Future Improvements

Future versions may introduce:

- Prompt evaluation framework
- Prompt regression testing
- Prompt version comparison
- Dynamic prompt composition
- Automatic prompt optimization
- Few-shot example libraries
- Prompt analytics

---

# 14. Prompt Summary

StartupIQ treats prompts as software artifacts rather than embedded implementation details.

Every prompt has:

- One owner
- One purpose
- One template
- Structured inputs
- Structured outputs
- Clearly defined constraints

This approach ensures consistency, maintainability, explainability, and easier prompt engineering as the platform evolves.

---

# Revision History

| Version | Date | Author | Notes |
|----------|------|--------|-------|
| 1.0 | YYYY-MM-DD | Yash | Initial prompt specification |