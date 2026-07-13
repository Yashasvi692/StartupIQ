from backend.teams.base_team import StartupIQTeam


class DiscoveryTeam(StartupIQTeam):
    name = "Discovery Team"

    def __init__(
        self,
        members: list | None = None,
        instructions: list[str] | None = None,
        context: dict | None = None,
        markdown: bool = True,
        show_members_responses: bool = False,
    ) -> None:
        team_instructions = instructions or [
            "Transform founder responses into a structured StartupProfile.",
            "Validate and normalize all user input.",
            "Identify missing fields and request clarification when necessary.",
        ]

        super().__init__(
            members=members,
            instructions=team_instructions,
            context=context,
            markdown=markdown,
            show_members_responses=show_members_responses,
        )
