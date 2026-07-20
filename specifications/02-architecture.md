# System Architecture Specification

**Project:** StartupIQ

**Version:** 1.0

**Status:** Draft

**Methodology:** Spec-Driven Development

---

# Related Documents

- `00-foundation.md`
- `01-prd.md`
- `03-workflows.md`
- `04-agents.md`
- `05-prompts.md`
- `06-api.md`
- `07-implementation-plan.md`

---

# 1. Purpose

This document defines the high-level system architecture for StartupIQ.

Its purpose is to describe how the platform is organized, how information flows through the system, and how responsibilities are distributed across the various architectural layers.

Unlike the Product Requirements Document, this specification focuses on **how the system is structured**, not what features it provides.

This document intentionally avoids implementation details such as programming logic or framework-specific code. Those details belong in the implementation phase.

The architecture described here serves as the blueprint for all future development.

---

# 2. Architecture Goals

The StartupIQ architecture is designed around the following goals.

---

## AG-001 Simplicity

The architecture should remain easy to understand, implement, and maintain.

Version 1 should be achievable by a single developer without introducing unnecessary complexity.

---

## AG-002 Modularity

Each component should have a single responsibility.

Individual modules should be independently replaceable without requiring significant architectural changes.

---

## AG-003 Extensibility

Future capabilities such as additional agents, validation modes, integrations, databases, authentication, and streaming should be accommodated without redesigning the architecture.

---

## AG-004 Explainability

Every recommendation produced by StartupIQ should be traceable back to supporting evidence.

The architecture should preserve transparency throughout the validation pipeline.

---

## AG-005 Open Architecture

StartupIQ Version 1 shall be built entirely using open-source software and freely available services.

No paid APIs or proprietary infrastructure should be required.

---

## AG-006 AI-Native Design

Artificial Intelligence is a core component of StartupIQ.

The architecture should treat AI as a first-class subsystem rather than an external utility.

---

# 3. High-Level Architecture

StartupIQ follows a layered architecture.

Each layer has a clearly defined responsibility.

```text
┌──────────────────────────────────────┐
│            React Frontend            │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│             FastAPI API              │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        Validation Pipeline           │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│            Agno Teams                │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│      StartupIQ Agent Wrappers        │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│      Shared LLM Configuration        │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│         External AI Provider         │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        External Tools & APIs         │
└──────────────────────────────────────┘
```

The architecture intentionally separates application orchestration from AI orchestration.

The **Validation Pipeline** controls application flow.

The **Agno Teams** coordinate AI collaboration.

Individual agents remain focused on solving one problem well.

---

# 4. Architectural Principles

StartupIQ follows the product philosophy defined in **00-foundation.md**.

Additionally, the architecture follows these engineering principles.

---

## AP-001 Single Responsibility

Every architectural component should perform one clearly defined responsibility.

Examples:

- API receives requests.
- Validation Pipeline coordinates execution.
- Teams coordinate agents.
- Agents perform AI tasks.
- Tools retrieve external information.

Responsibilities should never overlap.

---

## AP-002 Separation of Concerns

Application logic, AI logic, presentation, orchestration, and integrations should remain isolated from one another.

This allows individual layers to evolve independently.

---

## AP-003 Loose Coupling

Components should communicate through structured interfaces rather than implementation details.

No architectural layer should depend directly on the internal implementation of another layer.

---

## AP-004 Pipeline-Driven Execution

StartupIQ follows a Validation Pipeline architecture.

The Validation Pipeline controls the lifecycle of every validation request.

The Pipeline is responsible for:

- Creating validation jobs
- Invoking Agno Teams
- Tracking progress
- Aggregating results
- Returning the final report

The Pipeline does not perform AI reasoning.

---

## AP-005 Team-Based AI Collaboration

AI collaboration is delegated to Agno Teams.

Teams coordinate specialized agents while keeping individual agent responsibilities isolated.

Agents never invoke other agents directly.

---

## AP-006 Structured Communication

Whenever possible, communication between architectural layers should use structured models instead of free-form text.

Examples include:

- StartupProfile
- ValidationPlan
- ResearchResult
- CompetitorAnalysis
- BusinessFindings
- ValidationReport

Structured communication improves reliability, testing, and maintainability.

---

## AP-007 Stateless Processing

Version 1 processes each validation request independently.

Persistent storage is optional.

Future versions may introduce databases without requiring architectural redesign.

---

# 5. Major Components

StartupIQ is composed of six major architectural components.

---

## 5.1 React Frontend

The frontend provides the user interface for StartupIQ.

Responsibilities include:

- Startup Discovery Interview
- Validation Mode selection
- Progress visualization
- Report visualization
- Report export

The frontend never communicates directly with AI agents.

All communication occurs through the FastAPI backend.

---

## 5.2 FastAPI API

The API serves as the public interface to the platform.

Responsibilities include:

- Request validation
- Validation Job creation
- Starting the Validation Pipeline
- Returning responses
- Exposing health endpoints

The API contains no business logic and performs no AI reasoning.

---

## 5.3 Validation Pipeline

The Validation Pipeline is the application-level orchestrator.

Responsibilities include:

- Managing Validation Jobs
- Invoking Agno Teams
- Tracking execution progress
- Coordinating pipeline stages
- Aggregating outputs
- Returning the final Validation Report

The Validation Pipeline does not contain prompts or agent reasoning.

---

## 5.4 Agno Team Layer

Agno Teams coordinate collaboration between specialized AI agents.

The Team layer is responsible for:

- Delegating work
- Managing context
- Coordinating specialized agents
- Combining intermediate outputs

StartupIQ Version 1 uses two Agno Teams.

---

## 5.5 Agent Layer

The Agent Layer contains specialized AI agents.

Each agent performs exactly one responsibility.

Agents never communicate directly with one another.

All collaboration occurs through Agno Teams.

## 5.5.1 Shared AI Layer

StartupIQ introduces a shared AI infrastructure layer between the business agents and the underlying LLM provider.

Responsibilities include:

- Loading model configuration
- Managing retry policy
- Managing temperature settings
- Creating configured LLM instances
- Isolating provider-specific code

Business agents never instantiate language models directly.

All model creation SHALL occur through the shared LLM Factory.

This abstraction allows StartupIQ to switch providers without modifying agent implementations.
---

## 5.6 Tool Layer

The Tool Layer provides access to external information.

Examples include:

- DuckDuckGo Search
- Playwright
- GitHub
- pytrends
- BeautifulSoup

Tools contain no business logic and perform no AI reasoning.

Their only responsibility is collecting publicly available information.

---

# 6. Agno Team Architecture

StartupIQ Version 1 contains two Agno Teams.

Each Team represents a major phase of the validation process.

---

## 6.1 Discovery Team

### Purpose

Transform user responses into a structured Startup Profile.

### Responsibilities

- Validate user input
- Normalize responses
- Identify missing information
- Create the Startup Profile
- Ensure interview completeness

### Output

- StartupProfile

The Discovery Team completes before any validation begins.

---

## 6.2 Validation Team

### Purpose

Perform the complete startup validation workflow.

### Responsibilities

- Plan validation strategy
- Coordinate research
- Analyze competitors
- Generate business insights
- Produce the validation report
- Review report quality

### Output

- ValidationReport

The Validation Team is responsible for transforming a Startup Profile into a complete investor-grade validation report.

It operates entirely within the Validation Pipeline.

---

# 7. Validation Pipeline

The Validation Pipeline is the central application orchestrator.

It is responsible for coordinating the complete lifecycle of every startup validation request.

Unlike the Agno Teams, which coordinate AI collaboration, the Validation Pipeline manages the overall application flow.

## Responsibilities

The Validation Pipeline SHALL:

- Create Validation Jobs
- Invoke the Discovery Team
- Invoke the Validation Team
- Track execution progress
- Handle failures
- Aggregate outputs
- Return the final Validation Report

The Validation Pipeline SHALL NOT perform AI reasoning.

---

## Validation Pipeline Execution

Every validation request follows the same execution flow.

```text
User
    │
    ▼
POST /validate
    │
    ▼
Validation Job Created
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
Job Completed
```

The Pipeline owns the lifecycle of the Validation Job from creation until completion.

---

## Pipeline Stages

Every Validation Job progresses through the following stages.

| Stage | Description |
|---------|-------------|
| Discovery | Collect and validate startup information |
| Planning | Determine validation strategy |
| Research | Gather external evidence |
| Competition | Analyze competitors |
| Analysis | Generate business insights |
| Reporting | Produce the validation report |
| Review | Validate report quality |
| Complete | Return final report |

The Validation Pipeline tracks the current stage and reports progress through the API.

---

# 8. Backend Architecture

The backend is organized around business responsibilities rather than implementation frameworks.

```text
backend/

├── api/
├── pipeline/
├── teams/
├── agents/
├── llm/
├── prompts/
├── tools/
├── models/
├── utils/
└── main.py
```

This organization reflects the architecture rather than the underlying libraries.

---

## api/

Contains FastAPI endpoints.

Responsibilities:

- Request validation
- HTTP responses
- API documentation
- Health endpoints

Business logic SHALL NOT exist in this layer.

---

## pipeline/

Contains the Validation Pipeline.

Responsibilities:

- Validation Job lifecycle
- Team orchestration
- Progress tracking
- Error handling
- Result aggregation

The Pipeline is the application orchestrator.

---

## teams/

Contains Agno Team definitions.

Version 1 contains:

- Discovery Team
- Validation Team

Each Team coordinates a group of specialized agents.

---

## agents/

Contains all specialized Agno agents.

Each agent has exactly one responsibility.

Examples include:

- Discovery Agent
- Planner Agent
- Research Agent
- Competition Agent
- Business Analyst Agent
- Report Agent
- Reviewer Agent

Agents never invoke one another directly.

---
## llm/

Contains the shared AI configuration layer.

Responsibilities:

- Provider abstraction
- LLM factory
- Model configuration
- Retry configuration
- Temperature configuration
- Token limits

Business agents SHALL never instantiate providers directly.

Every agent receives its configured LLM instance through this layer.

---

## prompts/

Contains all Markdown prompt files.

Examples:

```text
prompts/

discovery.md
planner.md
research.md
competition.md
business.md
report.md
review.md
```

Prompt files are version-controlled independently from the application code.

---

## tools/

Contains integrations with external services.

Examples:

- DuckDuckGo
- Playwright
- pytrends
- GitHub
- BeautifulSoup

Tools retrieve information but never perform AI reasoning.

---

## models/

Contains shared application models.

Examples:

- StartupProfile
- ValidationPlan
- ResearchResult
- CompetitorAnalysis
- BusinessFindings
- ValidationReport
- ValidationJob

Structured models are used for communication between layers.

---

## utils/

Contains shared helper functionality.

Examples:

- Configuration
- Logging
- Formatting
- Utility functions

---

# 9. Frontend Architecture

The frontend is responsible solely for presentation and user interaction.

Major application views include:

- Landing Page
- Startup Discovery Interview
- Validation Progress
- Validation Report
- Report Export

The frontend communicates exclusively through the REST API.

No frontend component communicates directly with Agno Teams or AI agents.

---

# 10. Data Flow

StartupIQ follows a strictly layered data flow.

```text
User
    │
    ▼
React Frontend
    │
    ▼
FastAPI API
    │
    ▼
Validation Pipeline
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
React Frontend
```

Every architectural layer has a single responsibility.

No component bypasses another architectural layer.

---

# 11. Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | React + Vite |
| Backend | FastAPI |
| AI Framework | Agno |
| AI Collaboration | Agno Teams |
| Language | Python |
| Validation Models | Pydantic |
| Search | DuckDuckGo |
| Web Automation | Playwright |
| HTML Parsing | BeautifulSoup |
| Trend Analysis | pytrends |
| Report Format | Markdown |
| Containerization | Docker |

Only open-source software and freely available services are used.

---

# 12. Design Decisions

## DD-001 Validation Pipeline

The Validation Pipeline is responsible for application orchestration.

It owns Validation Jobs, execution order, progress tracking, and result aggregation.

---

## DD-002 Agno Teams

AI collaboration is delegated to Agno Teams.

Teams coordinate agents while preserving clear responsibility boundaries.

---

## DD-003 Specialized Agents

Each agent performs one well-defined responsibility.

No agent should perform unrelated tasks.

---

## DD-004 Prompt Separation

Prompts are stored separately from application code.

This improves maintainability and allows prompt engineering without modifying Python code.

---

## DD-005 Structured Communication

Architectural layers communicate through structured models rather than free-form text whenever possible.

---

## DD-006 Business-Oriented Organization

Project folders are organized around business responsibilities instead of implementation frameworks.

---

## DD-007 Open-Source Stack

StartupIQ Version 1 shall rely exclusively on open-source software and freely available services.

---
## DD-008 Shared LLM Abstraction

StartupIQ isolates language model providers behind a shared LLM configuration layer.

Business agents remain provider-independent.

This architecture allows StartupIQ to switch between Google AI Studio, Hugging Face, Ollama, or future providers without modifying agent implementations.

---

# 13. Scalability Considerations

Version 1 intentionally prioritizes simplicity.

Future versions may introduce:

- Persistent database storage
- Background workers
- Streaming responses
- Authentication
- Job history
- Team collaboration
- Continuous monitoring
- Additional AI agents

These enhancements should integrate into the existing architecture without major redesign.

---

# 14. Security Considerations

Although StartupIQ Version 1 does not process highly sensitive information, the system SHALL follow basic security practices.

These include:

- Input validation
- Output sanitization
- Environment variables for secrets
- Secure API configuration
- No hardcoded credentials
- Graceful handling of malformed requests

Future versions may introduce authentication and authorization mechanisms.

---

# 15. Architecture Summary

StartupIQ follows a layered architecture centered around a Validation Pipeline and Agno Teams.

The FastAPI backend manages Validation Jobs and delegates execution to the Validation Pipeline.

The Validation Pipeline orchestrates the application lifecycle while Agno Teams coordinate specialized AI agents.

Each agent performs a single responsibility and uses external tools to gather evidence before generating structured business insights.

This separation of concerns results in an architecture that is:

- Modular
- Explainable
- Extensible
- Maintainable
- AI-native

while remaining simple enough for a single developer to implement and evolve.

---

# Revision History

| Version | Date | Author | Notes |
|----------|------|--------|-------|
| 1.0 | YYYY-MM-DD | Yash | Initial architecture specification |