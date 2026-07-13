from typing import Any

from agno.team import Team

from backend.utils.logger import get_logger


class StartupIQTeam:
    name: str = ""

    def __init__(
        self,
        members: list[Any] | None = None,
        instructions: list[str] | None = None,
        context: dict | None = None,
        markdown: bool = True,
        show_members_responses: bool = False,
    ) -> None:
        if not self.name:
            raise ValueError("StartupIQTeam subclasses must set name")

        self.logger = get_logger(f"team.{self.name}")

        agent_list = []
        if members:
            for m in members:
                agent = m.agent if hasattr(m, "agent") else m
                agent_list.append(agent)

        self.team = Team(
            name=self.name,
            members=agent_list,
            instructions=instructions or [],
            additional_context=context,
            markdown=markdown,
            show_members_responses=show_members_responses,
        )
