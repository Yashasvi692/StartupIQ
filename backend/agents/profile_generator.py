from typing import Any

from backend.agents.discovery_agent import DiscoveryAgent
from backend.models.startup_profile import StartupProfile
from backend.utils.logger import get_logger

logger = get_logger(__name__)

REQUIRED_PROFILE_FIELDS: list[str] = [
    "startup_name",
    "problem_statement",
    "target_customers",
    "solution",
    "business_model",
    "market_knowledge",
    "technical_information",
]


def _build_prompt_from_input(data: dict[str, Any]) -> str:
    sections: list[str] = []

    fields_to_prompt = {
        "Startup Name": "startup_name",
        "Tagline": "tagline",
        "Problem Statement": "problem_statement",
        "Target Customers": "target_customers",
        "Solution Description": "solution",
        "Business Model": "business_model",
        "Market Knowledge": "market_knowledge",
        "Technical Information": "technical_information",
        "Founder Assumptions": "founder_assumptions",
        "Validation Objectives": "validation_objectives",
        "Industry": "industry",
        "Stage": "stage",
    }

    for heading, key in fields_to_prompt.items():
        value = data.get(key, "")
        if value:
            sections.append(f"## {heading}\n{value}")

    sections.append(
        "---\n"
        "Please analyze the founder responses above and produce a complete "
        "StartupProfile. Include confidence assessments for each populated field."
    )

    return "\n\n".join(sections)


async def generate_startup_profile(
    founder_input: dict[str, Any],
    agent: DiscoveryAgent | None = None,
) -> StartupProfile:
    if agent is None:
        agent = DiscoveryAgent()

    message = _build_prompt_from_input(founder_input)

    result = await agent.run_structured(message)

    if not isinstance(result, StartupProfile):
        raise TypeError(f"Expected StartupProfile, got {type(result).__name__}")

    _log_missing_fields(result)

    return result


def _log_missing_fields(profile: StartupProfile) -> None:
    missing = []
    for field in REQUIRED_PROFILE_FIELDS:
        value = getattr(profile, field, "")
        if not value or not value.strip():
            missing.append(field)
    if missing:
        logger.warning(
            f"StartupProfile generated with missing required fields: {', '.join(missing)}"
        )
