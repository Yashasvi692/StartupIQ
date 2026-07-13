from typing import Any

from backend.agents.discovery_agent import DiscoveryAgent
from backend.agents.profile_generator import generate_startup_profile
from backend.models.startup_profile import StartupProfile
from backend.teams.base_team import StartupIQTeam
from backend.utils.exceptions import ValidationError
from backend.utils.logger import get_logger
from backend.validation.founder_input import (
    is_input_valid,
    normalize_founder_input,
    validate_founder_input,
)

logger = get_logger(__name__)


class DiscoveryTeam(StartupIQTeam):
    name = "Discovery Team"

    def __init__(
        self,
        discovery_agent: DiscoveryAgent | None = None,
        instructions: list[str] | None = None,
        context: dict | None = None,
        markdown: bool = True,
        show_members_responses: bool = False,
    ) -> None:
        if discovery_agent is None:
            discovery_agent = DiscoveryAgent()

        self._discovery_agent = discovery_agent

        team_instructions = instructions or [
            "Transform founder responses into a structured StartupProfile.",
            "Validate and normalize all user input.",
            "Identify missing fields and request clarification when necessary.",
        ]

        super().__init__(
            members=[discovery_agent],
            instructions=team_instructions,
            context=context,
            markdown=markdown,
            show_members_responses=show_members_responses,
        )

    async def run_discovery(self, founder_input: dict[str, Any]) -> StartupProfile:
        errors = validate_founder_input(founder_input)
        if not is_input_valid(errors):
            missing = errors.get("missing", [])
            invalid = errors.get("invalid", [])
            parts = []
            if missing:
                parts.append(f"Missing fields: {', '.join(missing)}")
            if invalid:
                parts.append(f"Invalid values: {'; '.join(invalid)}")
            raise ValidationError(". ".join(parts))

        normalized = normalize_founder_input(founder_input)

        logger.info(
            f"Running discovery with {len(normalized)} fields "
            f"for startup: {normalized.get('startup_name', 'unknown')}"
        )

        profile = await generate_startup_profile(normalized, agent=self._discovery_agent)

        return profile
