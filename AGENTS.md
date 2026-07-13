# AGENTS.md

**Project:** StartupIQ

**Version:** 1.0

**Status:** Active

**Audience:** OpenCode, Contributors, Maintainers

---

# 1. Mission

StartupIQ is an AI-powered startup validation platform built using **Spec-Driven Development**.

The objective of the project is to help founders evaluate startup ideas through evidence-backed research, structured reasoning, and actionable recommendations.

Every implementation decision SHALL support this objective.

The purpose of this document is to define the engineering rules that govern the repository.

Specifications define **what** should be built.

This document defines **how contributors should build it.**

---

# 2. Project Philosophy

StartupIQ follows six engineering principles.

---

## GP-001 Specification First

Specifications are the single source of truth.

Implementation SHALL follow the specifications.

Code SHALL NOT redefine requirements.

---

## GP-002 Simplicity

Version 1 favors simplicity over cleverness.

Avoid unnecessary abstractions.

Prefer readable code over highly optimized code.

---

## GP-003 Modularity

Every module should have one clearly defined responsibility.

Large files should be split into focused modules.

---

## GP-004 Explainability

Every important business recommendation should be traceable to supporting evidence.

The system should communicate uncertainty instead of inventing facts.

---

## GP-005 Open Source

StartupIQ Version 1 SHALL use only open-source software and freely available services.

No paid APIs shall be required.

---

## GP-006 Maintainability

Future contributors should be able to understand every architectural decision.

Code readability is more important than minimizing the number of files.

---

# 3. Spec-Driven Development Rules

StartupIQ follows Spec-Driven Development.

Implementation SHALL always follow the specifications.

---

## SDR-001

Read the relevant specification before implementing any feature.

---

## SDR-002

If implementation conflicts with a specification, the specification takes precedence.

---

## SDR-003

Do not invent new architecture during implementation.

Architecture changes require specification updates.

---

## SDR-004

Every implementation task should map back to at least one specification.

---

## SDR-005

Specifications SHALL remain synchronized with implementation.

If implementation changes intentionally, update the specifications.

---

## SDR-006

Never implement features outside the documented project scope.

Future ideas belong in roadmap documents rather than Version 1.

---

# 4. Repository Structure

The repository SHALL follow the approved architecture.

```text
startup-iq/

specifications/

backend/

frontend/

tests/

AGENTS.md

TASKS.md

README.md
```

Each top-level directory has one responsibility.

---

## specifications/

Contains project specifications.

These documents define:

- Foundation
- PRD
- Architecture
- Workflows
- Agents
- Prompts
- API
- Implementation Plan

Specifications SHALL NOT contain implementation code.

---

## backend/

Contains the backend implementation.

The backend SHALL remain independent from the frontend.

---

## frontend/

Contains the React application.

Business logic SHALL NOT exist in the frontend.

---

## tests/

Contains automated tests.

Tests should mirror the backend structure whenever possible.

---

# 5. Architecture Rules

StartupIQ follows the architecture defined in `02-architecture.md`.

Implementation SHALL preserve the architectural boundaries.

---

## AR-001 Layered Architecture

StartupIQ uses the following layers.

```text
Frontend

↓

FastAPI

↓

Validation Pipeline

↓

Agno Teams

↓

Agents

↓

Tools
```

Layers SHALL NOT be bypassed.

---

## AR-002 Validation Pipeline

The Validation Pipeline owns application orchestration.

Responsibilities include:

- Validation Job lifecycle
- Progress tracking
- Team execution
- Error handling
- Result aggregation

The Validation Pipeline SHALL NOT perform AI reasoning.

---

## AR-003 Agno Teams

Agno Teams coordinate AI collaboration.

Teams SHALL NOT contain business logic.

Teams SHALL coordinate specialized agents.

---

## AR-004 Agents

Agents perform specialized reasoning.

Each agent SHALL have exactly one responsibility.

Agents SHALL NOT invoke other agents directly.

---

## AR-005 Tools

Tools retrieve external information.

Tools SHALL NOT contain business logic.

Tools SHALL NOT perform reasoning.

---

## AR-006 Models

Communication between architectural layers SHALL use structured models.

Preferred model types:

- Pydantic models
- Dataclasses (only where appropriate)

Raw dictionaries should be avoided.

---

## AR-007 Prompt Separation

Prompts SHALL NEVER be embedded inside Python code.

Every prompt belongs in:

```text
backend/prompts/
```

Application code loads prompts dynamically.

---

## AR-008 Configuration

Configuration values SHALL NOT be hardcoded.

Configuration should be loaded from environment variables or configuration files.

---

## AR-009 Dependency Direction

Dependencies SHALL always point downward.

```text
API

↓

Pipeline

↓

Teams

↓

Agents

↓

Tools
```

Lower layers SHALL NEVER depend on higher layers.

---

## AR-010 Single Responsibility

Each module should solve one problem.

Examples:

✓ Research Agent

✓ Report Agent

✗ ResearchAndReportAgent

Responsibilities should never overlap.

---

# 6. Backend Directory Rules

The backend SHALL follow the approved structure.

```text
backend/

api/

pipeline/

teams/

agents/

prompts/

tools/

models/

utils/
```

Each directory has one responsibility.

---

## api/

Contains only FastAPI endpoints.

The API SHALL NOT contain:

- Prompt logic
- AI reasoning
- Search logic

---

## pipeline/

Contains application orchestration.

Only the Validation Pipeline belongs here.

---

## teams/

Contains Agno Team definitions.

Version 1 contains:

- Discovery Team
- Validation Team

---

## agents/

Contains specialized AI agents.

Each agent should exist in its own module.

---

## prompts/

Contains Markdown prompt files.

One prompt per agent.

---

## tools/

Contains external integrations.

Examples:

- DuckDuckGo
- Playwright
- pytrends

---

## models/

Contains shared structured models.

All communication between layers should use these models.

---

## utils/

Contains shared utilities.

Examples include:

- Logging
- Configuration
- Formatting
- Helpers

Utility modules SHALL remain framework independent.

---

# 7. AI System Rules

StartupIQ uses Agno as its AI framework.

The AI system SHALL follow the rules below.

---

## AI-001 Team Ownership

Every AI agent SHALL belong to exactly one Agno Team.

Version 1 contains:

- Discovery Team
- Validation Team

---

## AI-002 Agent Responsibility

Each agent SHALL have exactly one primary responsibility.

Responsibilities are defined in `04-agents.md`.

Agents SHALL NOT perform responsibilities assigned to other agents.

---

## AI-003 Agent Communication

Agents SHALL NOT invoke one another directly.

All collaboration SHALL occur through Agno Teams.

---

## AI-004 Structured Communication

Agents SHALL exchange structured models whenever possible.

Examples include:

- StartupProfile
- ValidationPlan
- ResearchResult
- CompetitorAnalysis
- BusinessFindings
- ValidationReport

---

## AI-005 Stateless Agents

Agents SHALL NOT maintain internal state between executions.

All required context SHALL be provided as inputs.

---

## AI-006 Deterministic Responsibilities

Agent responsibilities SHALL remain stable.

Changes to an agent's responsibilities require updating:

- 04-agents.md
- Prompt files
- Relevant implementation

---

## AI-007 Tool Usage

Agents SHALL use tools only when necessary.

Reasoning SHALL NOT depend on unnecessary external tool calls.

---

## AI-008 Confidence

Agents SHOULD include confidence assessments whenever conclusions are generated.

Confidence SHALL reflect evidence quality rather than arbitrary values.

---

## AI-009 Failure Handling

Agents SHALL gracefully handle:

- Missing inputs
- Search failures
- Empty search results
- Tool failures

Agents SHALL communicate limitations rather than fabricate information.

---

# 8. Prompt Rules

Prompts are first-class software artifacts.

Prompt behavior is specified in `05-prompts.md`.

---

## PR-001 Prompt Location

Every prompt SHALL exist inside:

```text
backend/prompts/
```

---

## PR-002 One Prompt Per Agent

Every agent owns exactly one prompt.

Example:

```text
Research Agent

↓

backend/prompts/research.md
```

---

## PR-003 No Embedded Prompts

Prompt text SHALL NEVER be embedded inside Python code.

Python code loads prompts dynamically.

---

## PR-004 Prompt Structure

Every prompt SHALL contain:

- Identity
- Objective
- Responsibilities
- Constraints
- Inputs
- Available Context
- Available Tools
- Reasoning Instructions
- Expected Output
- Quality Checklist

---

## PR-005 Prompt Updates

Prompt modifications SHALL NOT require changes to business logic.

Prompt engineering should remain independent from implementation.

---

## PR-006 Prompt Scope

Prompts SHALL describe agent behavior only.

Implementation details belong in Python code.

---

# 9. API Rules

The REST API SHALL follow `06-api.md`.

---

## API-001 Business-Oriented Endpoints

Endpoints represent user actions.

Avoid CRUD-style APIs unless required.

---

## API-002 Validation Jobs

Every validation request creates a Validation Job.

The API SHALL treat Validation Jobs as primary resources.

---

## API-003 Response Models

Every endpoint SHALL return structured response models.

Avoid returning raw dictionaries.

---

## API-004 Status Codes

HTTP status codes SHALL follow the API specification.

Examples:

- 200 OK
- 202 Accepted
- 400 Bad Request
- 404 Not Found
- 409 Conflict
- 500 Internal Server Error

---

## API-005 Validation

Every request SHALL be validated using Pydantic models.

Manual validation should be avoided.

---

## API-006 Error Responses

Errors SHALL follow a consistent format.

Example:

```json
{
  "status": "error",
  "code": "...",
  "message": "...",
  "details": {}
}
```

---

# 10. Coding Standards

The codebase SHALL follow modern Python best practices.

---

## CS-001 Type Hints

All public functions SHALL use type hints.

---

## CS-002 Formatting

Formatting SHALL follow Black.

---

## CS-003 Linting

Linting SHALL follow Ruff.

---

## CS-004 Naming

Use descriptive names.

Examples:

✓ ValidationPipeline

✓ CompetitionAgent

✗ Pipeline2

✗ HelperClass

---

## CS-005 Async

Use asynchronous functions whenever external I/O occurs.

Examples:

- Web search
- Playwright
- API calls
- File loading

---

## CS-006 Small Functions

Functions SHOULD perform one responsibility.

Large functions should be split into reusable helpers.

---

## CS-007 Dependency Injection

Prefer dependency injection over hardcoded implementations.

This improves testing and future extensibility.

---

## CS-008 Configuration

Configuration SHALL be loaded from:

- .env
- configuration modules

Never hardcode:

- API keys
- model names
- paths

---

## CS-009 Logging

Use structured logging.

Avoid print statements outside debugging.

---

## CS-010 Exceptions

Raise meaningful exceptions.

Do not silently ignore failures.

---

## CS-011 Documentation

Public classes and functions SHOULD contain concise docstrings.

Docstrings should explain intent rather than implementation.

---

## CS-012 Imports

Imports SHOULD be grouped as:

- Standard library
- Third-party
- Local modules

Unused imports SHALL be removed.

---

## CS-013 Constants

Magic numbers and repeated strings SHOULD be replaced with named constants.

---

## CS-014 Code Duplication

Business logic SHALL exist in only one location.

Duplicate implementations should be refactored into shared modules.

---

## CS-015 Comments

Comments SHOULD explain **why** something exists.

Avoid comments that simply repeat the code.

Example:

✓ Explain architectural decisions.

✗ `# increment i`

---

# 11. Naming Conventions

Use consistent naming across the repository.

Classes

```text
ResearchAgent
ValidationPipeline
DiscoveryTeam
```

Files

```text
research_agent.py
validation_pipeline.py
startup_profile.py
```

Functions

```text
run_validation()
generate_report()
perform_research()
```

Variables

```text
startup_profile
validation_plan
research_result
```

Constants

```text
DEFAULT_MODEL

MAX_RETRIES
```

Prompt Files

```text
research.md

planner.md

review.md
```

Maintain consistency throughout the repository.

# 12. Testing Standards

Testing is part of implementation, not a separate activity.

Every significant feature SHALL be testable.

---

## TS-001 Unit Tests

Each major component SHOULD include unit tests.

Examples:

- Validation Pipeline
- Agent logic
- Prompt loader
- API endpoints
- Utility functions

---

## TS-002 Integration Tests

Integration tests SHALL verify communication between components.

Examples:

- API → Pipeline
- Pipeline → Teams
- Teams → Agents
- Agent → Tools

---

## TS-003 Mock External Services

External services SHOULD be mocked whenever possible.

Examples:

- DuckDuckGo
- Playwright
- pytrends

Tests should not depend on internet availability.

---

## TS-004 Prompt Testing

Prompt changes SHOULD be validated using representative startup ideas.

Major prompt changes should be reviewed before merging.

---

## TS-005 Regression Testing

Previously working functionality SHALL continue working after new features are added.

---

## TS-006 Test Organization

Tests SHOULD mirror the backend structure.

Example

```text
tests/

api/

pipeline/

teams/

agents/

tools/

utils/
```

---

# 13. Implementation Workflow

Development SHALL follow the approved implementation workflow.

```text
Read Specifications
        │
        ▼
Read AGENTS.md
        │
        ▼
Read TASKS.md
        │
        ▼
Implement One Task
        │
        ▼
Run Tests
        │
        ▼
Run Ruff
        │
        ▼
Run Black
        │
        ▼
Update Documentation (if required)
        │
        ▼
Commit Changes
```

OpenCode SHOULD complete one task at a time.

Avoid implementing multiple unrelated features simultaneously.

---

## IW-001 Small Tasks

Every implementation should correspond to one task in `TASKS.md`.

---

## IW-002 Specification Verification

Before marking a task complete, verify that the implementation satisfies the relevant specification.

---

## IW-003 Incremental Development

Every completed task should leave the repository in a working state.

---

## IW-004 Documentation

Whenever architecture or behavior changes intentionally, update the relevant specification before continuing development.

---

# 14. Definition of Done

A task is considered complete only when all of the following conditions are satisfied.

- Implementation completed
- Code compiles
- Ruff passes
- Black passes
- Type hints complete
- Tests pass
- Documentation updated
- Specifications satisfied
- No critical TODOs remain

Completion is determined by quality rather than code quantity.

---

# 15. Things Never To Do

The following practices are prohibited within StartupIQ.

---

## NTD-001

Do NOT hardcode prompts inside Python files.

---

## NTD-002

Do NOT bypass the Validation Pipeline.

---

## NTD-003

Do NOT allow agents to invoke other agents directly.

---

## NTD-004

Do NOT duplicate business logic.

---

## NTD-005

Do NOT place business logic inside API routes.

---

## NTD-006

Do NOT perform AI reasoning inside the Validation Pipeline.

---

## NTD-007

Do NOT perform AI reasoning inside tools.

---

## NTD-008

Do NOT modify specifications without intentional review.

---

## NTD-009

Do NOT introduce paid services into Version 1.

The project must remain fully functional using open-source software and freely available services.

---

## NTD-010

Do NOT ignore uncertainty.

If evidence cannot be obtained, communicate the limitation instead of inventing information.

---

# 16. OpenCode Working Agreement

OpenCode is expected to function as a software engineer working within an existing engineering team.

Before implementing any task, OpenCode SHALL:

1. Read the relevant specification documents.
2. Review the corresponding section in `AGENTS.md`.
3. Locate the implementation task in `TASKS.md`.
4. Implement only the requested task.
5. Preserve the approved architecture.
6. Keep changes focused and minimal.
7. Run formatting and linting tools.
8. Ensure tests continue to pass.
9. Avoid unrelated refactoring.
10. Stop and request clarification rather than inventing architecture.

OpenCode SHALL prioritize:

- Correctness over speed
- Simplicity over cleverness
- Modularity over convenience
- Evidence over assumptions
- Maintainability over short-term optimization

The objective is not merely to generate working code.

The objective is to produce a maintainable, explainable, and extensible codebase that faithfully implements the approved specifications.

---

# 17. Document Summary

`AGENTS.md` defines the engineering standards governing StartupIQ.

Together with the specification documents and implementation backlog, it ensures that every contribution follows the same architectural principles, coding standards, and development workflow.

This document serves as the operational guide for all AI-assisted and human contributors.

---

# Revision History

| Version | Date | Author | Notes |
|----------|------|--------|-------|
| 1.0 | YYYY-MM-DD | Yash | Initial engineering guide for StartupIQ |