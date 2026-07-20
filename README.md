# 🚀 StartupIQ

> **An AI-powered Startup Idea Validation Platform built using Spec-Driven Development and Agno Multi-Agent Systems.**

StartupIQ helps founders validate startup ideas before investing time and money.

Instead of relying on intuition, StartupIQ performs evidence-backed research, analyzes competitors, evaluates market opportunities, identifies risks, and generates actionable recommendations through a coordinated team of AI agents.

---

# ✨ Features

- 🧠 Multi-Agent AI architecture using Agno Teams
- 📊 Evidence-backed startup validation
- 🔍 Market and trend research
- 🏆 Competitor intelligence
- 📈 SWOT analysis
- ⚠️ Risk assessment
- 💡 Actionable business recommendations
- 📑 Investor-style validation report
- 📚 Confidence scores with citations
- ⚡ Quick & Deep validation modes
- 🆓 Built entirely with open-source software

---

# 🎯 Why StartupIQ?

Most founders ask questions like:

- Is my startup idea worth pursuing?
- Is there a real market?
- Who are my competitors?
- Is the market already saturated?
- What risks should I know?
- How can I improve my idea?

StartupIQ answers these questions automatically using coordinated AI agents instead of a single LLM conversation.

---

# 🏗 Architecture

StartupIQ follows a layered architecture.

```text
React Frontend
        │
        ▼
FastAPI Backend
        │
        ▼
Validation Pipeline
        │
        ▼
Agno Teams
        │
        ▼
Specialized AI Agents
        │
        ▼
External Research Tools
```

The application separates:

- Application orchestration
- AI collaboration
- Agent reasoning
- External research

making the system modular and easy to extend.

---

# 🤖 AI Architecture

StartupIQ Version 1 contains two Agno Teams.

## Discovery Team

Responsible for:

- Startup discovery
- Founder interview processing
- StartupProfile generation

---

## Validation Team

Responsible for:

- Validation planning
- Market research
- Competitor analysis
- Business analysis
- Report generation
- Quality review

---

### Validation Team Agents

- Planner Agent
- Research Agent
- Competition Agent
- Business Analyst Agent
- Report Agent
- Reviewer Agent

Each agent performs exactly one responsibility.

---

# 📋 Validation Workflow

```text
Founder

↓

Discovery Interview

↓

StartupProfile

↓

Validation Pipeline

↓

Discovery Team

↓

Validation Team

↓

Validation Report
```

---

# 📂 Repository Structure

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

---

# 📑 Specifications

StartupIQ follows **Spec-Driven Development**.

All implementation begins with specifications.

| Document | Purpose |
|----------|----------|
| 00 Foundation | Project philosophy |
| 01 PRD | Product requirements |
| 02 Architecture | System architecture |
| 03 Workflows | System execution |
| 04 Agents | AI agent contracts |
| 05 Prompts | Prompt engineering |
| 06 API | REST API |
| 07 Implementation Plan | Development roadmap |

---

# ⚙ Technology Stack

## Backend

- Python
- FastAPI
- Agno
- Pydantic

---

## Frontend

- React
- Vite

---

## AI

- Agno Teams
- Google AI Studio (Gemini API)
- Ollama (Future Support)

---

## Research Tools

- DuckDuckGo Search
- Playwright
- BeautifulSoup
- pytrends

---

## Development

- Ruff
- Black
- Pytest
- Docker

---

# 🚀 Getting Started

## Clone the repository

```bash
git clone https://github.com/<username>/startup-iq.git

cd startup-iq
```

---

## Backend

```bash
python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the backend

```bash
uvicorn backend.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 🔑 Environment Variables

Create a `.env` file.

Example

```env
GOOGLE_API_KEY=

MODEL=gemini-2.5-flash

LOG_LEVEL=INFO
```

---

# 🧪 Running Tests

```bash
pytest
```

Lint

```bash
ruff check .
```

Format

```bash
black .
```

---

# 📈 Development Workflow

StartupIQ follows Spec-Driven Development.

```text
Specifications

↓

AGENTS.md

↓

TASKS.md

↓

Implementation

↓

Testing

↓

Review
```

Developers should implement one task at a time.

---

# 📍 Current Roadmap

## Version 1

- Startup Discovery
- Market Research
- Competitor Analysis
- Validation Report
- REST API
- React Frontend

---

## Version 2

- Authentication
- Database
- Job History
- Streaming Progress
- Background Workers

---

## Version 3

- Pitch Deck Analysis
- Financial Modeling
- Investor Matching
- Continuous Startup Monitoring

---

# 🤝 Contributing

StartupIQ follows Spec-Driven Development.

Before contributing:

1. Read the relevant specifications.
2. Read `AGENTS.md`.
3. Pick a task from `TASKS.md`.
4. Implement only one task.
5. Run tests.
6. Submit your changes.

---

# 📄 License

This project is licensed under the MIT License.

---

# 🙏 Acknowledgements

StartupIQ is built entirely using open-source software.

Major technologies include:

- Agno
- FastAPI
- React
- Pydantic
- DuckDuckGo
- Playwright
- BeautifulSoup

Special thanks to the open-source community for making this project possible.

---

# ⭐ Project Status

🚧 **StartupIQ is currently under active development.**

The project follows a specification-first engineering process where every feature is designed before implementation.

Contributions, feedback, and ideas are welcome.